"""Flyer batch execution CLI — reads a plan.json, runs N single-image generations.

Each item is a per-aspect render with composition zones already encoded in the
prompt by the skill's prompt assembly. We reuse common.runners.batch for
parallel execution + manifest + --resume.

Plan format (schema = "skills.flyer.plan.v1"):

  {
    "schema": "skills.flyer.plan.v1",
    "event_slug": "workshop-slow-software",
    "title": "...",
    "subtitle": "...",
    "date": "...",
    "location": "...",
    "cta": "...",
    "lang": "en",
    "style_id": "kinfolk-minimal",
    "style_anchor": "<text>",
    "model": "nano-banana-pro",
    "photo": "./alex-headshot.jpg" | null,
    "output_dir": "./generated/flyer/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "portrait", "aspect": "portrait",
       "prompt": "<full per-aspect prompt>",
       "kwargs": {"size": "1080x1350", "image_url": "./alex-headshot.jpg"}},
      ...
    ]
  }
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .. import batch as batch_mod
from .. import config
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined


def _print_progress(item: batch_mod.BatchItem) -> None:
    if item.status == "succeeded":
        out = item.output_path or "?"
        print(f"  ✓ {item.label:<24s}  {out}", file=sys.stderr)
    else:
        err = item.error or "unknown"
        print(f"  ✗ {item.label:<24s}  {err}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.flyer")
    parser.add_argument("--plan-file", type=Path, required=True, help="path to plan.json")
    parser.add_argument("--resume", action="store_true", help="reuse succeeded items from manifest")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument(
        "--cost-only", action="store_true",
        help="print estimated total + per-aspect; do not generate",
    )
    args = parser.parse_args()

    if not args.plan_file.is_file():
        print(f"plan-file not found: {args.plan_file}", file=sys.stderr)
        return 2

    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if plan.get("schema") != "skills.flyer.plan.v1":
        print(
            f"unexpected plan schema '{plan.get('schema')}'. Expected 'skills.flyer.plan.v1'.",
            file=sys.stderr,
        )
        return 2

    model = plan.get("model")
    if not model:
        print("plan missing 'model'", file=sys.stderr)
        return 2

    raw_items = plan.get("items") or []
    if not raw_items:
        print("plan has no items", file=sys.stderr)
        return 2

    items: list[batch_mod.BatchItem] = []
    for entry in raw_items:
        items.append(
            batch_mod.BatchItem(
                index=int(entry["index"]),
                label=str(entry.get("label") or f"aspect-{int(entry['index']):02d}"),
                prompt=str(entry["prompt"]),
                kwargs=dict(entry.get("kwargs") or {}),
            )
        )

    config.load_all_providers()
    try:
        provider = config.get_provider(model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if provider.modality != "image":
        print(f"flyer CLI expects image provider; '{model}' is {provider.modality}.", file=sys.stderr)
        return 2

    estimated = batch_mod.estimate_batch_cost(provider, items)
    if args.cost_only:
        print(f"items: {len(items)}")
        print(f"estimated total: {cost_mod.format_cost(estimated)}")
        return 0

    try:
        # Use the carousel budget — flyers and carousels share image-gen modality
        # economics and the same default cap fits both.
        cost_mod.confirm_batch(
            estimated, n_items=len(items), modality="carousel", yes=args.yes,
        )
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    output_dir = Path(plan.get("output_dir") or f"./generated/flyer/{plan.get('event_slug') or 'batch'}")
    manifest_path = output_dir / "manifest.json"
    extra_meta = {
        "skill": "flyer-maker",
        "title": plan.get("title"),
        "subtitle": plan.get("subtitle"),
        "date": plan.get("date"),
        "location": plan.get("location"),
        "cta": plan.get("cta"),
        "lang": plan.get("lang"),
        "style_id": plan.get("style_id"),
        "model": model,
        "photo": plan.get("photo"),
        "estimated_total_cost_usd": str(estimated) if estimated is not None else None,
    }
    parallelism = int(plan.get("parallelism") or 2)

    print(
        f"Flyer: {len(items)} aspect(s) via {model} "
        f"(estimated {cost_mod.format_cost(estimated)}). Parallelism: {parallelism}.",
        file=sys.stderr,
    )

    result = batch_mod.run_batch(
        provider,
        items,
        modality="image",
        output_dir=output_dir,
        manifest_path=manifest_path,
        parallelism=parallelism,
        resume=args.resume,
        extension_hint="png",
        on_progress=_print_progress,
        extra_meta=extra_meta,
    )

    succeeded = len(result.succeeded)
    failed = len(result.failed)
    print(
        f"\nFlyer: {output_dir}  ({succeeded}/{len(items)} aspect(s) succeeded)",
        file=sys.stderr,
    )
    if result.succeeded:
        names = " · ".join(Path(i.output_path).name for i in result.succeeded if i.output_path)
        print(f"Files: {names}", file=sys.stderr)
    print(str(output_dir))
    if failed:
        print(
            f"  {failed} aspect(s) failed. Re-run with --resume to retry.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
