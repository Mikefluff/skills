"""Batch executor — runs N generations through a Provider with manifest + resume.

Used by carousel-builder (8 slides) and reel-builder (3-4 shots). Each item is
a dict with at minimum {"prompt": str}; provider-specific kwargs can be passed
through. Manifest is written after every item so --resume works after crashes.

Cost confirmation happens ONCE for the aggregate batch (not per item) before
the first call — caller passes the estimated total in.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from . import output as output_mod
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
    error: str | None = None
    started_at: float | None = None
    finished_at: float | None = None


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
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_manifest(manifest_path: Path) -> list[BatchItem]:
    """Restore items list from a manifest written by a previous run."""
    if not manifest_path.is_file():
        return []
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    out: list[BatchItem] = []
    for entry in raw.get("items", []):
        out.append(BatchItem(**{k: entry.get(k) for k in BatchItem.__dataclass_fields__}))
    return out


def run_batch(
    provider: Provider,
    items: list[BatchItem],
    *,
    modality: Modality,
    output_dir: Path,
    manifest_path: Path,
    parallelism: int = 3,
    poll_timeout: float = 600.0,
    extension_hint: str = "png",
    resume: bool = False,
    on_progress: Callable[[BatchItem], None] | None = None,
    extra_meta: dict[str, Any] | None = None,
) -> BatchResult:
    """Execute a list of items through the provider.

    Manifest is written after every state change. On --resume, items with
    status='succeeded' are skipped (re-using existing output_path).

    Parallelism uses a thread pool — fine for vendor APIs (I/O bound). Async
    providers (video, music) are polled inside the worker thread.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if resume:
        prior = {item.index: item for item in load_manifest(manifest_path)}
        for current in items:
            previous = prior.get(current.index)
            if previous and previous.status == "succeeded":
                current.status = "succeeded"
                current.output_path = previous.output_path
                current.s3_url = previous.s3_url

    write_manifest(manifest_path, items, extra_meta)

    pending = [i for i in items if i.status != "succeeded"]
    if not pending:
        return BatchResult(items=items, manifest_path=manifest_path, output_dir=output_dir)

    parallelism = max(1, parallelism)

    def _worker(item: BatchItem) -> BatchItem:
        item.started_at = time.time()
        try:
            try:
                provider.ensure_available()
            except KeyMissingError as exc:
                raise RunnerError(str(exc)) from exc

            result = provider.generate(item.prompt, **item.kwargs)
            if isinstance(result, JobHandle):
                result = provider.poll(result, timeout=poll_timeout)

            if not isinstance(result, GenerationResult):
                raise RunnerError(f"provider returned unexpected type: {type(result).__name__}")

            saved = output_mod.save(
                result.content,
                modality if modality in {"image", "video", "music", "audio"} else "image",
                result.extension or extension_hint,
                slug=item.label or f"item-{item.index:02d}",
                output_dir=output_dir,
                mime=result.mime,
            )
            item.output_path = str(saved.local_path)
            item.s3_url = saved.s3_url
            item.status = "succeeded"
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

    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = {pool.submit(_worker, item): item for item in pending}
        for fut in as_completed(futures):
            item = fut.result()
            write_manifest(manifest_path, items, extra_meta)
            if on_progress is not None:
                on_progress(item)

    return BatchResult(items=items, manifest_path=manifest_path, output_dir=output_dir)


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
