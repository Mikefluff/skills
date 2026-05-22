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
from .. import carousel_prompt_builder as cpb
from .. import config
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined
from ..providers.base import Modality


# ─── structured content → builder bridge ──────────────────────────────────────


_CONTENT_FACTORIES = {
    "hook": lambda c: cpb.HookContent(**c),
    "point": lambda c: cpb.PointContent(**c),
    "framework": lambda c: cpb.FrameworkContent(
        framework_name=c["framework_name"],
        boxes=[cpb.Box(**b) for b in c["boxes"]],
        box_layout=c.get("box_layout", "grid"),
    ),
    "data": lambda c: cpb.DataContent(
        data_points=[cpb.DataPoint(**d) for d in c["data_points"]],
        source=c.get("source"),
    ),
    "steps": lambda c: cpb.StepsContent(
        process_name=c["process_name"],
        steps=[cpb.Step(**s) for s in c["steps"]],
        direction=c.get("direction", "horizontal"),
    ),
    "comparison": lambda c: cpb.ComparisonContent(
        comparison_title=c["comparison_title"],
        left=cpb.ComparisonSide(**c["left"]),
        right=cpb.ComparisonSide(**c["right"]),
        divider_style=c.get("divider_style", "vertical-rule"),
    ),
    "quote": lambda c: cpb.QuoteContent(
        quote=c["quote"],
        attribution=cpb.QuoteAttribution(**c["attribution"]),
    ),
    "myth-vs-truth": lambda c: cpb.MythTruthContent(**c),
    "cta": lambda c: cpb.CtaContent(**c),
}


def _build_prompt_from_structured(
    entry: dict,
    plan: dict,
    slide_number: int,
    total: int,
) -> str:
    """When a plan item has `role` + `content` instead of `prompt`, run the figma-rigor builder."""
    role = entry["role"]
    if role not in _CONTENT_FACTORIES:
        raise ValueError(f"unknown role '{role}'. Valid: {sorted(_CONTENT_FACTORIES)}")
    style_anchor = entry.get("style_anchor") or plan.get("style_anchor")
    if not style_anchor:
        raise ValueError("structured item requires 'style_anchor' on the item or plan root")
    content_obj = _CONTENT_FACTORIES[role](entry["content"])
    return cpb.build_slide_prompt(
        style_anchor=style_anchor,
        role=role,
        slide_number=slide_number,
        total_slides=total,
        content=content_obj,
        lang=entry.get("lang") or plan.get("lang", "en"),
        is_last=bool(entry.get("is_last", slide_number == total)),
        slide_marker_style=entry.get("slide_marker_style")
            or plan.get("slide_marker_style", "arabic"),
    )


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

    # Support `--plan-file -` for stdin (no intermediate file needed):
    #   cat <<EOF | carousel-builder --plan-file - --yes
    #     {...}
    #   EOF
    if str(args.plan_file) == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            print("plan-file '-' (stdin) is empty", file=sys.stderr)
            return 2
        plan = json.loads(raw)
    else:
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

    total = len(raw_items)
    items: list[batch_mod.BatchItem] = []
    for entry in raw_items:
        idx = int(entry["index"])
        if "prompt" in entry:
            # Legacy: prompt assembled by caller
            prompt = str(entry["prompt"])
        elif "role" in entry and "content" in entry:
            # Structured: builder assembles figma-rigor prompt at execution time
            prompt = _build_prompt_from_structured(entry, plan, idx, total)
        else:
            print(
                f"item {idx} has neither 'prompt' nor 'role'+'content' — skipping",
                file=sys.stderr,
            )
            continue
        items.append(
            batch_mod.BatchItem(
                index=idx,
                label=str(entry.get("label") or f"slide-{idx:02d}"),
                prompt=prompt,
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
