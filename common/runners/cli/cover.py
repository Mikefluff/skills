"""Cover batch execution CLI — cli/_maker.py plus a typography pass.

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
    "imprint": "penguin-modern" | null,
    "genre": "literary-fiction" | null,
    "typeset": "overlay" | "ai" | null,
    "output_dir": "./generated/cover/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "album-v1", "prompt": "<full>",
       "kwargs": {"size": "3000x3000", "image_url": "<photo>"}},
      ...
    ]
  }

Generators still set type badly at small sizes, so a book cover can ask for real
typography to be composited over the generated art instead — that is the
second pass below, and it writes <stem>-typeset.png next to each variant.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .. import batch as batch_mod
from .. import cover_imprints
from .. import typography as type_mod
from ._maker import MakerSpec, run


def _typeset_mode(plan: dict[str, Any]) -> str:
    """An explicit `typeset` wins; otherwise only a book with a preset overlays."""
    declared = plan.get("typeset")
    if declared is not None:
        return declared
    has_preset = plan.get("imprint") or plan.get("genre")
    return "overlay" if plan.get("medium") == "book" and has_preset else "ai"


def _compose(preset_name: str, plan: dict[str, Any], items: list[batch_mod.BatchItem]) -> None:
    """Draw the cover text over each generated variant."""
    title = plan.get("title") or ""
    author = plan.get("creator") or ""
    subtitle = plan.get("subtitle") or None

    for item in items:
        src_path = Path(item.output_path) if item.output_path else None
        if src_path is None or not src_path.is_file():
            continue
        # apply_text returns a copy, so each variant gets its own layout and
        # the preset stays the blank template it ships as.
        layout = cover_imprints.apply_text(
            cover_imprints.get_imprint(preset_name).layout, title, author, subtitle
        )
        try:
            out_bytes = type_mod.compose_book_cover(src_path.read_bytes(), layout)
        except Exception as exc:  # noqa: BLE001 — one bad variant must not lose the rest
            print(f"  ✗ typography compose failed for {src_path.name}: {exc}", file=sys.stderr)
            continue
        dest = src_path.with_name(f"{src_path.stem}-typeset.png")
        dest.write_bytes(out_bytes)
        print(f"  ✓ {dest.name}", file=sys.stderr)


def _typeset_pass(plan: dict[str, Any], result: batch_mod.BatchResult) -> None:
    """Second pass — real type over the generated art, when the plan asks for it."""
    if _typeset_mode(plan) != "overlay" or not result.succeeded:
        return

    preset = cover_imprints.resolve_imprint(plan.get("imprint"), plan.get("genre"))
    if preset is None:
        print(
            "  · typeset=overlay requested but no --imprint or --genre to resolve. "
            "Skipping composition.",
            file=sys.stderr,
        )
        return

    print(
        f"\nTypography pass: composing via imprint '{preset.name}' "
        f"({preset.display_name}) ...",
        file=sys.stderr,
    )
    _compose(preset.name, plan, result.succeeded)


SPEC = MakerSpec(
    module="cover",
    schema="skills.cover.plan.v1",
    skill="cover-maker",
    title="Cover",
    noun="variant(s)",
    meta_keys=("slug", "title", "subtitle", "creator", "medium", "lang", "style_id", "photo"),
    after_batch=_typeset_pass,
)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
