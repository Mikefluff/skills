"""Batch executor — runs N generations through a Provider with manifest + resume.

Used by carousel-builder (8 slides) and reel-builder (3-4 shots). Each item is
a dict with at minimum {"prompt": str}; provider-specific kwargs can be passed
through. Manifest is written after every item so --resume works after crashes.

Cost confirmation happens ONCE for the aggregate batch (not per item) before
the first call — caller passes the estimated total in.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from . import atomicfile
from . import output as output_mod
from . import spend
from .errors import KeyMissingError, ProviderError, RunnerError, TimeoutError as RunnerTimeoutError
from .providers.base import GenerationResult, JobHandle, Modality, Provider


@dataclass
class BatchItem:
    index: int
    label: str                    # human readable, used in filename slug
    prompt: str
    kwargs: dict[str, Any] = field(default_factory=dict)
    # Populated after run:
    status: str = "pending"        # pending | succeeded | failed | skipped
    output_path: str | None = None
    s3_url: str | None = None
    # Extra files the same call produced — Seedream's layer sets, and nothing
    # else so far. Recorded so `--resume` does not regenerate an item whose
    # companions are already on disk, and so the manifest lists what was billed.
    companion_paths: list[str] = field(default_factory=list)
    error: str | None = None
    started_at: float | None = None
    finished_at: float | None = None
    # The prompt and kwargs this output was generated from (`spec_hash`), carried across --resume, so a
    # changed prompt or reference is noticed even though the output is kept. None on older manifests.
    spec_hash: str | None = None
    # A job the vendor accepted but this run never saw finish (a poll that timed out on the network): its
    # handle, so the next run polls it again for the take already billed instead of buying it a second time.
    pending_job: dict[str, Any] | None = None


@dataclass
class BatchResult:
    items: list[BatchItem]
    manifest_path: Path
    output_dir: Path

    @property
    def succeeded(self) -> list[BatchItem]:
        return [i for i in self.items if i.status == "succeeded"]

    @property
    def failed(self) -> list[BatchItem]:
        return [i for i in self.items if i.status == "failed"]

    @property
    def ok(self) -> bool:
        return not self.failed


def write_manifest(manifest_path: Path, items: list[BatchItem], extra: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {
        "schema": "skills.batch.v1",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "items": [asdict(i) for i in items],
    }
    if extra:
        payload["meta"] = extra
    # Atomic: this is rewritten after every item so a crash is survivable, and
    # a crash *during* the write would otherwise leave the half-file that the
    # next --resume chokes on.
    atomicfile.write_text(
        manifest_path, json.dumps(payload, indent=2, ensure_ascii=False)
    )


def load_manifest(manifest_path: Path) -> list[BatchItem]:
    """Restore items list from a manifest written by a previous run."""
    if not manifest_path.is_file():
        return []
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    out: list[BatchItem] = []
    for entry in raw.get("items", []):
        out.append(BatchItem(**{k: entry.get(k) for k in BatchItem.__dataclass_fields__}))
    return out


@dataclass(frozen=True)
class BatchSpec:
    """Everything about a batch run except the provider and the work itself."""

    modality: Modality
    output_dir: Path
    manifest_path: Path
    parallelism: int = 3
    poll_timeout: float = 600.0
    extension_hint: str = "png"
    resume: bool = False
    # With resume: labels to generate again even though they succeeded — a take
    # that rendered but is wrong (a duplicate face, a frozen shot).
    redo: frozenset[str] = frozenset()
    # Labels to generate now; every other item keeps its manifest record and is not touched (empty = all).
    only: frozenset[str] = frozenset()
    extra_meta: dict[str, Any] | None = None
    # Runs in the worker just before an item generates; raising fails the item.
    # A voiced film uses it to hand each segment the frame the previous one was
    # cut on, which only exists once that segment is done — so it pairs with
    # parallelism=1, where the pool runs items in submission order.
    before_item: Callable[[BatchItem], None] | None = None
    # Called the moment a vendor accepts a job, after run_batch has saved the manifest with its handle.
    on_submit: Callable[[BatchItem], None] | None = None

    def save_modality(self) -> Modality:
        """output.save only knows the four asset kinds; anything else is an image."""
        return self.modality if self.modality in {"image", "video", "music", "audio"} else "image"


def _previous(manifest_path: Path) -> Callable[[BatchItem], BatchItem | None]:
    """The manifest record of an item, if a previous run left one."""
    # By label first: a shot inserted into a film renumbers every shot after it, and an index would hand
    # each of them its neighbour's clip. The index is the fallback for unlabelled items.
    loaded = load_manifest(manifest_path)
    by_label = {item.label: item for item in loaded if item.label}
    by_index = {item.index: item for item in loaded}
    return lambda current: by_label.get(current.label) if current.label else by_index.get(current.index)


def spec_hash(item: BatchItem) -> str:
    """What an item is generated from: its prompt and kwargs (the temporary host they go up through aside)."""
    kwargs = {k: v for k, v in item.kwargs.items() if k not in ("media_host", "audio_host")}
    raw = json.dumps([item.prompt, kwargs], sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def changed_since_output(items: list[BatchItem], manifest_path: Path) -> list[str]:
    """Labels of items kept from an earlier run whose prompt or kwargs have changed since that output was made."""
    previous = _previous(manifest_path)
    return [item.label for item in items
            if (prev := previous(item)) is not None and prev.status == "succeeded"
            and prev.spec_hash and prev.spec_hash != spec_hash(item)]


def pending_reasons(items: list[BatchItem], manifest_path: Path, *, resume: bool,
                    redo: frozenset[str] = frozenset(), only: frozenset[str] = frozenset()) -> list[tuple[BatchItem, str]]:
    """The items run_batch would generate with this spec, each with why (a `spend` reason); generates nothing."""
    previous = _previous(manifest_path)
    out = []
    for item in items:
        prev = previous(item)
        done = prev is not None and prev.status == "succeeded"
        if (only and item.label not in only) or (resume and done and item.label not in redo):
            continue
        out.append((item, _reason(item, prev, redo | only)))
    return out


def _reason(item: BatchItem, prev: BatchItem | None, asked: frozenset[str]) -> str:
    if item.label in asked:
        return spend.ASKED
    if prev is None:
        return spend.MISSING
    return {"succeeded": spend.RERUN, "failed": spend.FAILED}.get(prev.status, spend.MISSING)


def _restore_succeeded(items: list[BatchItem], manifest_path: Path, redo: frozenset[str] = frozenset()) -> None:
    """--resume: carry forward items a previous run already paid for, except those asked to be redone."""
    previous_of = _previous(manifest_path)
    for current in items:
        previous = previous_of(current)
        if previous and previous.status == "failed" and previous.pending_job and previous.spec_hash == spec_hash(current):
            current.pending_job = previous.pending_job  # accepted and billed; poll it, do not submit again
        if previous and previous.status == "succeeded" and current.label not in redo:
            current.status = "succeeded"
            current.output_path = previous.output_path
            current.s3_url = previous.s3_url
            current.companion_paths = list(previous.companion_paths)
            current.spec_hash = previous.spec_hash


def _resumed_job(item: BatchItem) -> JobHandle | None:
    """The job a previous run left polling for this same item (same prompt and kwargs), to poll again."""
    job = item.pending_job
    if not job or not job.get("job_id"):
        return None
    print(f"  {item.label}: polling the job already submitted ({job['job_id']}), not buying it again",
          file=sys.stderr)
    return JobHandle(**{k: job[k] for k in ("provider", "job_id", "started_at", "poll_url", "extra") if k in job})


def _generate_one(provider: Provider, item: BatchItem, spec: BatchSpec,
                  submitted: Callable[[BatchItem], None] | None = None) -> None:
    """Generate and save a single item. Raises; the caller records the failure."""
    try:
        provider.ensure_available()
    except KeyMissingError as exc:
        raise RunnerError(str(exc)) from exc

    result = _resumed_job(item) or provider.generate(item.prompt, **item.kwargs)
    if isinstance(result, JobHandle):
        item.pending_job = asdict(result)
        if submitted is not None:
            submitted(item)
        result = provider.poll(result, timeout=spec.poll_timeout)
    if not isinstance(result, GenerationResult):
        raise RunnerError(f"provider returned unexpected type: {type(result).__name__}")

    saved, companions = output_mod.save_result(
        result,
        spec.save_modality(),
        spec.extension_hint,
        output_mod.SaveOptions(
            slug=item.label or f"item-{item.index:02d}",
            output_dir=spec.output_dir,
            mime=result.mime,
        ),
    )
    item.output_path = str(saved.local_path)
    item.s3_url = saved.s3_url
    item.companion_paths = [str(c.local_path) for c in companions]
    item.status = "succeeded"
    item.pending_job = None


def _run_item(provider: Provider, item: BatchItem, spec: BatchSpec,
              submitted: Callable[[BatchItem], None] | None = None) -> BatchItem:
    """Worker body — one item must never be able to end the batch."""
    item.started_at = time.time()
    item.spec_hash = spec_hash(item)  # before a seam hook adds the frame it hands over
    try:
        if spec.before_item is not None:
            spec.before_item(item)
        _generate_one(provider, item, spec, submitted or spec.on_submit)
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        item.status = "failed"
        item.error = str(exc)
    except Exception as exc:  # noqa: BLE001 — protect the batch from one item crashing the whole run
        item.status = "failed"
        item.error = f"{type(exc).__name__}: {exc}"
        traceback.print_exc(file=sys.stderr)
    finally:
        item.finished_at = time.time()
    return item


def run_batch(
    provider: Provider,
    items: list[BatchItem],
    spec: BatchSpec,
    *,
    on_progress: Callable[[BatchItem], None] | None = None,
) -> BatchResult:
    """Execute a list of items through the provider.

    The manifest is written after every state change, so --resume works after a
    crash and a half-finished run is never silently re-paid for.

    Parallelism is a thread pool — right for vendor APIs, which are I/O bound.
    Async providers (video, music) are polled inside the worker thread.
    """
    spec.output_dir.mkdir(parents=True, exist_ok=True)

    if spec.resume:
        _restore_succeeded(items, spec.manifest_path, spec.redo)
    import threading

    lock = threading.Lock()

    def saved(item: BatchItem) -> None:
        with lock:
            write_manifest(spec.manifest_path, items, spec.extra_meta)
        if spec.on_submit is not None:
            spec.on_submit(item)

    write_manifest(spec.manifest_path, items, spec.extra_meta)
    result = BatchResult(
        items=items, manifest_path=spec.manifest_path, output_dir=spec.output_dir
    )

    pending = [i for i in items if i.status != "succeeded" and (not spec.only or i.label in spec.only)]
    if not pending:
        return result

    with ThreadPoolExecutor(max_workers=max(1, spec.parallelism)) as pool:
        futures = [pool.submit(_run_item, provider, item, spec, saved) for item in pending]
        for fut in as_completed(futures):
            item = fut.result()
            write_manifest(spec.manifest_path, items, spec.extra_meta)
            if on_progress is not None:
                on_progress(item)

    return result


def estimate_batch_cost(provider: Provider, items: list[BatchItem]) -> Decimal | None:
    """Sum per-item estimate. Returns None if provider has no pricing entry."""
    total = Decimal("0")
    any_known = False
    for item in items:
        per = provider.estimate_cost(**item.kwargs)
        if per is None:
            continue
        any_known = True
        total += per
    return total if any_known else None
