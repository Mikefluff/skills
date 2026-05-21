"""Avatar batch execution CLI — same shape as flyer.py.

Plan schema: skills.avatar.plan.v1

  {
    "schema": "skills.avatar.plan.v1",
    "slug": "alex-headshot",
    "photo": "./alex-selfie.jpg",
    "style_id": "kinfolk-minimal",
    "style_anchor": "<text>",
    "model": "nano-banana-pro",
    "output_dir": "./generated/avatar/<slug>",
    "parallelism": 3,
    "items": [
      {"index": 1, "label": "square-v1", "aspect": "square",
       "prompt": "<full>", "kwargs": {"size": "1080x1080", "image_url": "<photo>"}},
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
        print(f"  ✓ {item.label:<24s}  {item.output_path or '?'}", file=sys.stderr)
    else:
        print(f"  ✗ {item.label:<24s}  {item.error or 'unknown'}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.avatar")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--cost-only", action="store_true")
    args = parser.parse_args()

    if not args.plan_file.is_file():
        print(f"plan-file not found: {args.plan_file}", file=sys.stderr)
        return 2

    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if plan.get("schema") != "skills.avatar.plan.v1":
        print(f"unexpected plan schema '{plan.get('schema')}'", file=sys.stderr)
        return 2

    model = plan.get("model")
    raw_items = plan.get("items") or []
    if not model or not raw_items:
        print("plan missing model or items", file=sys.stderr)
        return 2

    items = [
        batch_mod.BatchItem(
            index=int(e["index"]),
            label=str(e.get("label") or f"variant-{int(e['index']):02d}"),
            prompt=str(e["prompt"]),
            kwargs=dict(e.get("kwargs") or {}),
        )
        for e in raw_items
    ]

    config.load_all_providers()
    try:
        provider = config.get_provider(model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if provider.modality != "image":
        print(f"'{model}' is {provider.modality}, not image", file=sys.stderr)
        return 2

    estimated = batch_mod.estimate_batch_cost(provider, items)
    if args.cost_only:
        print(f"items: {len(items)}")
        print(f"estimated total: {cost_mod.format_cost(estimated)}")
        return 0

    try:
        cost_mod.confirm_batch(estimated, n_items=len(items), modality="carousel", yes=args.yes)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    output_dir = Path(plan.get("output_dir") or f"./generated/avatar/{plan.get('slug') or 'batch'}")
    manifest_path = output_dir / "manifest.json"
    extra_meta = {
        "skill": "avatar-maker",
        "slug": plan.get("slug"),
        "photo": plan.get("photo"),
        "style_id": plan.get("style_id"),
        "model": model,
        "estimated_total_cost_usd": str(estimated) if estimated is not None else None,
    }
    parallelism = int(plan.get("parallelism") or 3)

    print(
        f"Avatar: {len(items)} variant(s) via {model} "
        f"(estimated {cost_mod.format_cost(estimated)}). Parallelism: {parallelism}.",
        file=sys.stderr,
    )

    result = batch_mod.run_batch(
        provider, items,
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
    print(f"\nAvatar: {output_dir}  ({succeeded}/{len(items)} variant(s) succeeded)", file=sys.stderr)
    print(str(output_dir))
    if failed:
        print(f"  {failed} variant(s) failed. Re-run with --resume to retry.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
