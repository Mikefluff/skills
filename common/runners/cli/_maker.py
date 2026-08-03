"""Shared skeleton for the plan-driven maker CLIs.

Nine skills — carousel, cover, flyer, banner, thumbnail, meme, quote, logo,
avatar — do the same seven things in the same order: read a plan.json, check its
schema, turn its items into BatchItems, resolve the provider, estimate, confirm,
run the batch and print where the files landed. They differ only in nouns,
manifest keys and two genuine behaviours (carousel numbers its progress lines by
slide; cover runs a typography pass afterwards).

So the shape lives here once and each module declares its differences as a
`MakerSpec`. A tenth maker is a fifteen-line module, not another copy of this.

Exit codes are the contract callers branch on, and they are pinned by
tests/unit/test_cli_makers.py:

    0  everything generated (or --cost-only printed and stopped)
    1  the batch ran, some items failed — the directory is still on stdout
    2  the plan is unusable: absent, wrong schema, no model, no items,
       unknown provider slug, or a provider of the wrong modality
    3  the cost confirmation was declined

stdout carries only machine-readable output — the output directory, or the
--cost-only estimate. Everything a human reads goes to stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from .. import batch as batch_mod
from .. import config
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined
from ..providers.base import Provider


@dataclass(frozen=True)
class MakerSpec:
    """Everything one maker CLI declares about itself.

    `module` doubles as the argparse prog name and the ./generated/<module>/
    namespace, so it must match the module's own filename.
    """

    module: str
    schema: str
    skill: str                       # skill directory name, recorded in the manifest
    title: str                       # leading word of every human-facing line
    noun: str                        # what one item is called: "slide(s)", "card(s)"
    slug_key: str = "slug"           # plan key naming the default output subdirectory
    label_prefix: str = "variant"    # default item label: "<prefix>-01"
    parallelism: int = 2
    meta_keys: tuple[str, ...] = ()  # plan keys copied verbatim into the manifest
    progress_by_index: bool = False  # number progress lines instead of labelling them
    list_files: bool = False         # print the filenames after a successful batch
    item_hint: str | None = None     # extra sentence on the missing-prompt error
    after_batch: Callable[[dict[str, Any], batch_mod.BatchResult], None] | None = None


@dataclass(frozen=True)
class _Job:
    """A validated plan, ready to run. Built only once every check has passed."""

    spec: MakerSpec
    plan: dict[str, Any]
    provider: Provider
    items: list[batch_mod.BatchItem] = field(default_factory=list)
    estimated: Decimal | None = None
    resume: bool = False


def _parse_args(spec: MakerSpec) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=f"common.runners.cli.{spec.module}")
    parser.add_argument(
        "--plan-file", type=Path, required=True,
        help="path to plan.json, or '-' to read it from stdin",
    )
    parser.add_argument("--resume", action="store_true", help="reuse succeeded items from the manifest")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument(
        "--cost-only", action="store_true",
        help="print the estimated total; do not generate",
    )
    return parser.parse_args()


def _load_plan(plan_file: Path, schema: str) -> dict[str, Any] | None:
    """Read and schema-check a plan. None means the caller exits 2.

    `--plan-file -` reads stdin so a skill can pipe a heredoc straight in
    without leaving a plan.json behind.
    """
    if str(plan_file) == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            print("plan-file '-' (stdin) is empty", file=sys.stderr)
            return None
        plan = json.loads(raw)
    else:
        if not plan_file.is_file():
            print(f"plan-file not found: {plan_file}", file=sys.stderr)
            return None
        plan = json.loads(plan_file.read_text(encoding="utf-8"))

    if plan.get("schema") != schema:
        print(
            f"unexpected plan schema '{plan.get('schema')}'. Expected '{schema}'.",
            file=sys.stderr,
        )
        return None
    return plan


def _build_items(plan: dict[str, Any], spec: MakerSpec) -> list[batch_mod.BatchItem] | None:
    """Turn plan items into BatchItems. None means the caller exits 2."""
    items: list[batch_mod.BatchItem] = []
    for entry in plan.get("items") or []:
        index = int(entry["index"])
        if "prompt" not in entry:
            hint = f" {spec.item_hint}" if spec.item_hint else ""
            print(
                f"item {index} missing 'prompt' — write prompts via the image-prompt "
                f"skill, then assemble plan items as "
                f"{{index, label, prompt, kwargs}}.{hint}",
                file=sys.stderr,
            )
            return None
        items.append(
            batch_mod.BatchItem(
                index=index,
                label=str(entry.get("label") or f"{spec.label_prefix}-{index:02d}"),
                prompt=str(entry["prompt"]),
                kwargs=dict(entry.get("kwargs") or {}),
            )
        )
    return items


def _resolve_provider(model: str, spec: MakerSpec) -> Provider | None:
    """Look up the provider slug and check it can make images. None → exit 2."""
    config.load_all_providers()
    try:
        provider = config.get_provider(model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return None
    if provider.modality != "image":
        print(
            f"{spec.module} CLI expects an image provider; "
            f"'{model}' is {provider.modality}.",
            file=sys.stderr,
        )
        return None
    return provider


def _progress_printer(spec: MakerSpec) -> Callable[[batch_mod.BatchItem], None]:
    """One stderr line per finished item, as the batch completes them."""

    def report(item: batch_mod.BatchItem) -> None:
        if item.status == "succeeded":
            mark, detail = "✓", item.output_path or "?"
        else:
            mark, detail = "✗", item.error or "unknown"
        # Carousel slides are an ordered sequence, so the number is what a
        # reader wants; everywhere else the label is more informative.
        if spec.progress_by_index:
            print(f"  {mark} slide {item.index:>2}: {detail}", file=sys.stderr)
        else:
            print(f"  {mark} {item.label:<24s}  {detail}", file=sys.stderr)

    return report


def _manifest_meta(job: _Job) -> dict[str, Any]:
    """The `meta` block of the batch manifest — provenance for a finished run."""
    meta: dict[str, Any] = {"skill": job.spec.skill}
    for key in job.spec.meta_keys:
        meta[key] = job.plan.get(key)
    meta["model"] = job.plan.get("model")
    meta["estimated_total_cost_usd"] = str(job.estimated) if job.estimated is not None else None
    return meta


def _execute(job: _Job) -> int:
    """Run the batch and report. Returns the process exit code."""
    spec, plan = job.spec, job.plan
    total = len(job.items)
    output_dir = Path(
        plan.get("output_dir")
        or f"./generated/{spec.module}/{plan.get(spec.slug_key) or 'batch'}"
    )
    parallelism = int(plan.get("parallelism") or spec.parallelism)

    print(
        f"{spec.title}: {total} {spec.noun} via {plan.get('model')} "
        f"(estimated {cost_mod.format_cost(job.estimated)}). Parallelism: {parallelism}.",
        file=sys.stderr,
    )

    result = batch_mod.run_batch(
        job.provider,
        job.items,
        batch_mod.BatchSpec(
            modality="image",
            output_dir=output_dir,
            manifest_path=output_dir / "manifest.json",
            parallelism=parallelism,
            resume=job.resume,
            extension_hint="png",
            extra_meta=_manifest_meta(job),
        ),
        on_progress=_progress_printer(spec),
    )
    if spec.after_batch is not None:
        spec.after_batch(plan, result)

    print(
        f"\n{spec.title}: {output_dir}  "
        f"({len(result.succeeded)}/{total} {spec.noun} succeeded)",
        file=sys.stderr,
    )
    if spec.list_files and result.succeeded:
        names = " · ".join(Path(i.output_path).name for i in result.succeeded if i.output_path)
        print(f"Files: {names}", file=sys.stderr)

    print(str(output_dir))
    if result.failed:
        print(
            f"  {len(result.failed)} {spec.noun} failed. Re-run with --resume to retry.",
            file=sys.stderr,
        )
        return 1
    return 0


def run(spec: MakerSpec) -> int:
    """Entry point every maker's main() delegates to."""
    args = _parse_args(spec)

    plan = _load_plan(args.plan_file, spec.schema)
    if plan is None:
        return 2

    model = plan.get("model")
    if not model:
        print("plan missing 'model'", file=sys.stderr)
        return 2
    if not plan.get("items"):
        print("plan has no items", file=sys.stderr)
        return 2

    items = _build_items(plan, spec)
    if items is None:
        return 2

    provider = _resolve_provider(model, spec)
    if provider is None:
        return 2

    estimated = batch_mod.estimate_batch_cost(provider, items)
    if args.cost_only:
        print(f"items: {len(items)}")
        print(f"estimated total: {cost_mod.format_cost(estimated)}")
        return 0

    try:
        # Flyers, covers and the rest share image-gen economics with carousels,
        # so they share the carousel budget cap rather than each inventing one.
        cost_mod.confirm_batch(estimated, n_items=len(items), modality="carousel", yes=args.yes)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    return _execute(
        _Job(
            spec=spec,
            plan=plan,
            provider=provider,
            items=items,
            estimated=estimated,
            resume=args.resume,
        )
    )
