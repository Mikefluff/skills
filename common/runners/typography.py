"""Typography composer — overlay title/author/subtitle on a generated cover image.

Two-pass workflow (per BeYourCover / Inkfluence pro pattern):
  1. AI model generates text-free background art ("no embedded text" prompt)
  2. This module composes designer-grade typography on top with real OFL fonts

Why: AI image models squeeze text awkwardly, ignore baseline grids, and produce
"image with floating title" rather than a designed book cover. Composing typography
externally with real fonts + proper ratios fixes that.

Public API:
    compose_book_cover(image_bytes, layout: TypeLayout, fonts_dir: Path) -> bytes

The TypeLayout dataclass describes which font, size fraction, position fraction,
case, palette, and tracking to apply per text block (title / subtitle / author /
publisher / series).

Layout fractions are interpreted relative to cover height (so they scale to any
output size). Title at `size=0.10` means title cap-height = 10% of cover height.

Font weight: variable fonts auto-pick by `weight` int (100-900). Static fonts ignore
the parameter.

Imprint presets (see cover-maker/references/imprints.md) compose into TypeLayout
instances and pass through unchanged — the composer doesn't know about imprints,
only about layout dicts.
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw

# Anchor, CaseMode, Decoration, TextBlock and TypeLayout are re-exported: the
# vocabulary lives next to the block renderer, but callers have always imported
# it from here and there is no reason to make them learn otherwise.
from .typography_blocks import (  # noqa: F401
    DEFAULT_FONTS_DIR,
    Anchor,
    CaseMode,
    Decoration,
    TextBlock,
    TypeLayout,
    _Box,
    _render_block,
)


# ─── render a band (legibility plate behind text) ──────────────────────────────


def _render_band(canvas: Image.Image, band: dict, cover_w: int, cover_h: int) -> None:
    y_start = int(cover_h * float(band["y_start"]))
    y_end = int(cover_h * float(band["y_end"]))
    color = band.get("color", "#000000")
    opacity = float(band.get("opacity", 0.4))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Parse hex
    h = color.lstrip("#")
    r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(255 * opacity)
    od.rectangle([0, y_start, cover_w, y_end], fill=(r, g, b, a))
    canvas.alpha_composite(overlay)


# ─── decoration rendering ──────────────────────────────────────────────────────


def _render_decoration(canvas: Image.Image, draw: ImageDraw.ImageDraw,
                       deco: Decoration, cover_w: int, cover_h: int) -> None:
    thick = max(1, int(min(cover_w, cover_h) * deco.thickness_fraction))
    cx = int(cover_w * deco.position_x_fraction)
    cy = int(cover_h * deco.position_y_fraction)
    length = int(cover_w * deco.length_fraction)

    if deco.kind == "hline":
        x0 = cx - length // 2
        x1 = cx + length // 2
        draw.rectangle([x0, cy - thick // 2, x1, cy + thick // 2], fill=deco.color)
    elif deco.kind == "vline":
        v = int(cover_h * deco.length_fraction)
        y0 = cy - v // 2
        y1 = cy + v // 2
        draw.rectangle([cx - thick // 2, y0, cx + thick // 2, y1], fill=deco.color)
    elif deco.kind == "dot":
        r = int(cover_h * deco.thickness_fraction * 8)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=deco.color)
    elif deco.kind == "circle":
        r = int(cover_h * deco.length_fraction * 0.5)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=deco.color, width=thick)


# ─── main composer ─────────────────────────────────────────────────────────────


def compose_book_cover(
    image_bytes: bytes,
    layout: TypeLayout,
    fonts_dir: Path | None = None,
) -> bytes:
    """Compose typography over a generated cover image.

    Pipeline:
      1. Load image, convert to RGBA
      2. Apply optional legibility bands (top / bottom)
      3. Apply optional decorations (rule, dot, etc.)
      4. Render text blocks in z-order: subtitle, title, author, publisher, series
      5. Flatten to RGB, return PNG bytes
    """
    fonts_dir = fonts_dir or DEFAULT_FONTS_DIR
    if not fonts_dir.is_dir():
        raise FileNotFoundError(f"fonts dir not found: {fonts_dir}")

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    cover_w, cover_h = img.size

    # Legibility bands first (so text sits on top)
    if layout.title_band:
        _render_band(img, layout.title_band, cover_w, cover_h)
    if layout.author_band:
        _render_band(img, layout.author_band, cover_w, cover_h)

    draw = ImageDraw.Draw(img)

    # Decorations
    for deco in layout.decorations:
        _render_decoration(img, draw, deco, cover_w, cover_h)

    # Text blocks
    cover = _Box(w=cover_w, h=cover_h)
    for block in (layout.series, layout.subtitle, layout.title, layout.author, layout.publisher):
        if block is None:
            continue
        _render_block(draw, block, cover, fonts_dir)

    # Flatten to RGB
    final = Image.new("RGB", img.size, (255, 255, 255))
    final.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)

    out = io.BytesIO()
    final.save(out, format="PNG", optimize=True)
    return out.getvalue()


# ─── self-test (run as a script) ───────────────────────────────────────────────


if __name__ == "__main__":
    # Generate a solid background as smoke test
    bg = Image.new("RGB", (1024, 1536), (27, 59, 42))  # forest green
    buf = io.BytesIO()
    bg.save(buf, format="PNG")

    layout = TypeLayout(
        title=TextBlock(
            text="The Slow Software Manifesto",
            font="EB Garamond",
            weight=500,
            size_fraction=0.075,
            color="#E8DCC4",
            case="preserve",
            max_lines=3,
            margin_top_fraction=0.20,
            margin_x_fraction=0.12,
            anchor="top-center",
            tracking=0.01,
        ),
        author=TextBlock(
            text="Mikhail Savchenko",
            font="EB Garamond",
            weight=400,
            size_fraction=0.025,
            color="#E8DCC4",
            case="preserve",
            tracking=0.10,
            anchor="bottom-center",
            margin_bottom_fraction=0.08,
        ),
        decorations=[
            Decoration(
                kind="hline", color="#B8860B",
                length_fraction=0.10, position_y_fraction=0.90,
            ),
        ],
    )
    output_bytes = compose_book_cover(buf.getvalue(), layout)
    out_path = Path("/tmp/typography-self-test.png")
    out_path.write_bytes(output_bytes)
    print(f"Self-test composed → {out_path} ({len(output_bytes):,} bytes)")
