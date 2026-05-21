"""Carousel batch execution CLI — reads a plan.json, runs N image generations.

The carousel-builder skill assembles the plan (slide split + per-slide prompts +
style anchor + model pick) and writes a plan.json. This CLI reads that file,
runs the batch through common.runners.batch, and writes outputs + manifest.

Plan format (schema = "skills.carousel.plan.v1"):

  {
    "schema": "skills.carousel.plan.v1",
    "topic": "...",
    "platform": "instagram|linkedin|tiktok",
    "aspect": "portrait|square|story",
    "style_id": "...",
    "style_anchor": "<text>",
    "model": "flux-2-pro",
    "text_mode": "embedded|overlay|none",
    "output_dir": "./generated/carousel/<slug>",
    "parallelism": 3,
    "items": [
      {"index": 1, "label": "slide-01-hook", "prompt": "<full text>", "kwargs": {"size": "1080x1350"}},
      ...
    ]
  }
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from .. import batch as batch_mod
from .. import config
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined
from ..providers.base import Modality


def _print_progress(item: batch_mod.BatchItem) -> None:
    """stdout progress as each slide finishes."""
    if item.status == "succeeded":
        out = item.output_path or "?"
        print(f"  ✓ slide {item.index:>2}: {out}", file=sys.stderr)
    else:
        err = item.error or "unknown"
        print(f"  ✗ slide {item.index:>2}: {err}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.carousel")
    parser.add_argument("--plan-file", type=Path, required=True, help="path to plan.json")
    parser.add_argument("--resume", action="store_true", help="re-use succeeded items from manifest")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument(
        "--cost-only", action="store_true",
        help="print estimated total + per-slide; do not generate",
    )
    args = parser.parse_args()

    if not args.plan_file.is_file():
        print(f"plan-file not found: {args.plan_file}", file=sys.stderr)
        return 2

    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if plan.get("schema") != "skills.carousel.plan.v1":
        print(
            f"unexpected plan schema '{plan.get('schema')}'. Expected 'skills.carousel.plan.v1'.",
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
                label=str(entry.get("label") or f"slide-{int(entry['index']):02d}"),
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
        print(f"carousel CLI expects image provider; '{model}' is {provider.modality}.", file=sys.stderr)
        return 2

    estimated = batch_mod.estimate_batch_cost(provider, items)
    if args.cost_only:
        print(f"items: {len(items)}")
        print(f"estimated total: {cost_mod.format_cost(estimated)}")
        return 0

    try:
        cost_mod.confirm_batch(
            estimated, n_items=len(items), modality="carousel", yes=args.yes,
        )
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    output_dir = Path(plan.get("output_dir") or f"./generated/carousel/{plan.get('topic_slug') or 'batch'}")
    manifest_path = output_dir / "manifest.json"
    extra_meta = {
        "skill": "carousel-builder",
        "topic": plan.get("topic"),
        "platform": plan.get("platform"),
        "aspect": plan.get("aspect"),
        "style_id": plan.get("style_id"),
        "model": model,
        "text_mode": plan.get("text_mode"),
        "research_brief": plan.get("research_brief"),
        "estimated_total_cost_usd": str(estimated) if estimated is not None else None,
    }
    parallelism = int(plan.get("parallelism") or 3)

    print(
        f"Batch: {len(items)} slides via {model} "
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
        f"\nCarousel: {output_dir}  ({succeeded}/{len(items)} slides succeeded)",
        file=sys.stderr,
    )
    print(str(output_dir))
    if failed:
        print(
            f"  {failed} slide(s) failed. Re-run with --resume to retry.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
