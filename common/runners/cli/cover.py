"""Cover batch execution CLI — same shape as flyer.py / avatar.py.

Plan schema: skills.cover.plan.v1

  {
    "schema": "skills.cover.plan.v1",
    "slug": "lunar-vault-album",
    "title": "Lunar Vault",
    "subtitle": null | "<text>",
    "creator": "Alex Reyes",
    "medium": "album|book|podcast|magazine|report|deck-cover|linkedin-doc",
    "lang": "en",
    "style_id": "neon-cyberpunk",
    "style_anchor": "<text>",
    "model": "flux-2-pro",
    "photo": "./artwork.jpg" | null,
    "output_dir": "./generated/cover/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "album-v1", "prompt": "<full>",
       "kwargs": {"size": "3000x3000", "image_url": "<photo>"}},
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
from .. import cover_imprints
from .. import typography as type_mod
from ..errors import CostConfirmationDeclined


def _print_progress(item: batch_mod.BatchItem) -> None:
    if item.status == "succeeded":
        print(f"  ✓ {item.label:<24s}  {item.output_path or '?'}", file=sys.stderr)
    else:
        print(f"  ✗ {item.label:<24s}  {item.error or 'unknown'}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.cover")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--cost-only", action="store_true")
    args = parser.parse_args()

    # `--plan-file -` reads from stdin (no intermediate file needed).
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
    if plan.get("schema") != "skills.cover.plan.v1":
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

    output_dir = Path(plan.get("output_dir") or f"./generated/cover/{plan.get('slug') or 'batch'}")
    manifest_path = output_dir / "manifest.json"
    extra_meta = {
        "skill": "cover-maker",
        "slug": plan.get("slug"),
        "title": plan.get("title"),
        "subtitle": plan.get("subtitle"),
        "creator": plan.get("creator"),
        "medium": plan.get("medium"),
        "lang": plan.get("lang"),
        "style_id": plan.get("style_id"),
        "model": model,
        "photo": plan.get("photo"),
        "estimated_total_cost_usd": str(estimated) if estimated is not None else None,
    }
    parallelism = int(plan.get("parallelism") or 2)

    print(
        f"Cover: {len(items)} variant(s) via {model} "
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

    # ── two-pass typography composition ──
    # If the plan specifies an imprint OR genre AND typeset=="overlay" (default
    # for book medium), composite real typography on top of each succeeded variant.
    imprint_name = plan.get("imprint")
    genre = plan.get("genre")
    typeset = plan.get("typeset")
    medium = plan.get("medium")
    if typeset is None:
        typeset = "overlay" if medium == "book" and (imprint_name or genre) else "ai"

    if typeset == "overlay" and result.succeeded:
        preset = cover_imprints.resolve_imprint(imprint_name, genre)
        if preset is None:
            print(
                "  · typeset=overlay requested but no --imprint or --genre to resolve. "
                "Skipping composition.",
                file=sys.stderr,
            )
        else:
            print(
                f"\nTypography pass: composing via imprint '{preset.name}' "
                f"({preset.display_name}) ...",
                file=sys.stderr,
            )
            title = plan.get("title") or ""
            author = plan.get("creator") or ""
            subtitle = plan.get("subtitle") or None
            for item in result.succeeded:
                src_path = Path(item.output_path) if item.output_path else None
                if src_path is None or not src_path.is_file():
                    continue
                # Build fresh layout per item (avoid shared-state across iterations)
                preset_fresh = cover_imprints.get_imprint(preset.name)
                layout = cover_imprints.apply_text(preset_fresh.layout, title, author, subtitle)
                try:
                    out_bytes = type_mod.compose_book_cover(src_path.read_bytes(), layout)
                except Exception as exc:  # noqa: BLE001
                    print(f"  ✗ typography compose failed for {src_path.name}: {exc}",
                          file=sys.stderr)
                    continue
                # Save composite alongside source as <stem>-typeset.png
                dest = src_path.with_name(f"{src_path.stem}-typeset.png")
                dest.write_bytes(out_bytes)
                print(f"  ✓ {dest.name}", file=sys.stderr)

    succeeded = len(result.succeeded)
    failed = len(result.failed)
    print(f"\nCover: {output_dir}  ({succeeded}/{len(items)} variant(s) succeeded)", file=sys.stderr)
    print(str(output_dir))
    if failed:
        print(f"  {failed} variant(s) failed. Re-run with --resume to retry.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
