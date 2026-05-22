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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont


# ─── default fonts directory (overridable) ─────────────────────────────────────

DEFAULT_FONTS_DIR = Path(__file__).resolve().parents[2] / "cover-maker" / "fonts"


# ─── known font mapping ────────────────────────────────────────────────────────
# Logical name → bundled filename. The composer accepts logical names so imprint
# presets don't have to know about file paths.

FONT_FILES: dict[str, str] = {
    # serif text
    "EB Garamond": "EBGaramond-VF.ttf",
    "Cormorant": "Cormorant-VF.ttf",
    "Cormorant Garamond": "Cormorant-VF.ttf",
    "Playfair Display": "PlayfairDisplay-VF.ttf",
    # sans
    "Inter": "Inter-VF.ttf",
    # display
    "Bebas Neue": "BebasNeue-Regular.ttf",
    "Cinzel": "Cinzel-VF.ttf",
}


# ─── text-block spec ───────────────────────────────────────────────────────────


CaseMode = Literal["sentence", "title", "upper", "lower", "preserve"]
Anchor = Literal["top-left", "top-center", "top-right",
                 "center-left", "center", "center-right",
                 "bottom-left", "bottom-center", "bottom-right"]


@dataclass
class TextBlock:
    """One typeset block (title / subtitle / author / publisher)."""

    text: str
    font: str = "EB Garamond"
    weight: int = 600                    # 100-900; ignored for static fonts
    size_fraction: float = 0.10          # of cover height
    color: str = "#1A1A1A"               # CSS hex
    case: CaseMode = "preserve"
    tracking: float = 0.0                # extra letter-spacing in ems (0 = normal; 0.05 = +50 thousandths)
    line_height: float = 1.1             # multiplier of size
    max_lines: int = 3                   # wrap if longer
    align: Literal["left", "center", "right"] = "center"

    # position: anchor + offset
    anchor: Anchor = "top-center"
    offset_x_fraction: float = 0.0       # horizontal nudge from anchor (of width)
    offset_y_fraction: float = 0.0       # vertical nudge from anchor (of height)

    # margins: how far from the cover edge the block sits (used by anchor)
    margin_top_fraction: float = 0.08
    margin_bottom_fraction: float = 0.08
    margin_x_fraction: float = 0.10      # both sides; constrains wrap width


@dataclass
class Decoration:
    """Optional minimal decorative element (thin rule, dot, brand mark)."""

    kind: Literal["hline", "vline", "dot", "circle"] = "hline"
    color: str = "#1A1A1A"
    thickness_fraction: float = 0.0015   # of min(width, height)
    length_fraction: float = 0.15        # of width
    position_y_fraction: float = 0.5     # of height (for hline / dot / circle)
    position_x_fraction: float = 0.5     # of width


@dataclass
class TypeLayout:
    """Full layout spec — all blocks + decorations + global background tinting."""

    title: TextBlock
    author: TextBlock | None = None
    subtitle: TextBlock | None = None
    publisher: TextBlock | None = None
    series: TextBlock | None = None
    decorations: list[Decoration] = field(default_factory=list)

    # Optional vignette / band to improve text legibility over busy art
    title_band: dict | None = None       # {"y_start": 0.0, "y_end": 0.35, "color": "#000000", "opacity": 0.4}
    author_band: dict | None = None


# ─── apply case mode ───────────────────────────────────────────────────────────


def _apply_case(text: str, mode: CaseMode) -> str:
    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "title":
        return text.title()
    return text  # preserve | sentence (caller's responsibility)


# ─── font loading ──────────────────────────────────────────────────────────────


def _load_font(font_name: str, size: int, weight: int, fonts_dir: Path) -> ImageFont.FreeTypeFont:
    filename = FONT_FILES.get(font_name)
    if filename is None:
        raise ValueError(f"unknown font '{font_name}'. Known: {sorted(FONT_FILES)}")
    path = fonts_dir / filename
    if not path.is_file():
        raise FileNotFoundError(f"font file missing: {path}. Re-run install.sh to fetch bundled fonts.")

    font = ImageFont.truetype(str(path), size=size)
    # If variable font, set weight axis
    try:
        font.set_variation_by_axes([float(weight)])
    except (OSError, AttributeError, Exception):  # noqa: BLE001 — static font or no axes
        pass
    return font


# ─── word-wrap helper ──────────────────────────────────────────────────────────


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
               max_width: int, max_lines: int) -> list[str]:
    """Greedy word-wrap to fit max_width pixels. Hard-truncate to max_lines."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
    if len(lines) < max_lines and current:
        lines.append(current)
    return lines[:max_lines]


# ─── tracking (letter-spacing) ─────────────────────────────────────────────────


def _draw_tracked_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int],
                       text: str, font: ImageFont.FreeTypeFont, fill: str,
                       tracking_px: int, align_offset: int = 0) -> None:
    """Draw text with manual per-glyph spacing for tracking control."""
    if tracking_px == 0:
        draw.text((xy[0] + align_offset, xy[1]), text, font=font, fill=fill)
        return
    x = xy[0] + align_offset
    for ch in text:
        draw.text((x, xy[1]), ch, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), ch, font=font)
        x += (bbox[2] - bbox[0]) + tracking_px


def _measure_tracked(draw: ImageDraw.ImageDraw, text: str,
                     font: ImageFont.FreeTypeFont, tracking_px: int) -> int:
    """Width of `text` rendered with `tracking_px` extra between glyphs."""
    if tracking_px == 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    total = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        total += (bbox[2] - bbox[0]) + tracking_px
    return max(0, total - tracking_px)  # no trailing gap


# ─── block positioning ─────────────────────────────────────────────────────────


def _anchor_origin(anchor: Anchor, block_w: int, block_h: int,
                   cover_w: int, cover_h: int,
                   margin_top: int, margin_bottom: int,
                   margin_x: int) -> tuple[int, int]:
    """Compute top-left (x, y) for a block given its anchor + cover dims."""
    # x
    if anchor.endswith("left"):
        x = margin_x
    elif anchor.endswith("right"):
        x = cover_w - margin_x - block_w
    else:  # center
        x = (cover_w - block_w) // 2
    # y
    if anchor.startswith("top"):
        y = margin_top
    elif anchor.startswith("bottom"):
        y = cover_h - margin_bottom - block_h
    else:  # center
        y = (cover_h - block_h) // 2
    return x, y


# ─── render one block ──────────────────────────────────────────────────────────


def _render_block(canvas: Image.Image, draw: ImageDraw.ImageDraw,
                  block: TextBlock, cover_w: int, cover_h: int,
                  fonts_dir: Path) -> tuple[int, int, int, int] | None:
    """Render `block` onto canvas. Returns (x, y, w, h) of the rendered area, or None if empty."""
    if not block.text:
        return None

    text = _apply_case(block.text, block.case)

    # Font + size
    size_px = max(8, int(cover_h * block.size_fraction))
    font = _load_font(block.font, size_px, block.weight, fonts_dir)

    # Tracking in pixels (em-relative)
    tracking_px = int(block.tracking * size_px) if block.tracking else 0

    # Max line width (after horizontal margins)
    margin_x = int(cover_w * block.margin_x_fraction)
    max_line_w = cover_w - 2 * margin_x

    # Wrap (tracking-aware measurement is approximate — use plain measurement for wrapping, OK for headlines)
    lines = _wrap_text(draw, text, font, max_line_w, block.max_lines)
    if not lines:
        return None

    # Measure lines with tracking
    line_widths = [_measure_tracked(draw, ln, font, tracking_px) for ln in lines]
    line_h = int(size_px * block.line_height)
    block_w = max(line_widths)
    block_h = line_h * len(lines)

    # Position
    margin_top = int(cover_h * block.margin_top_fraction)
    margin_bottom = int(cover_h * block.margin_bottom_fraction)
    x0, y0 = _anchor_origin(
        block.anchor, block_w, block_h, cover_w, cover_h,
        margin_top, margin_bottom, margin_x,
    )
    # Nudge
    x0 += int(cover_w * block.offset_x_fraction)
    y0 += int(cover_h * block.offset_y_fraction)

    # Render each line with its own alignment
    for i, line in enumerate(lines):
        lw = line_widths[i]
        if block.align == "center":
            line_x = x0 + (block_w - lw) // 2
        elif block.align == "right":
            line_x = x0 + (block_w - lw)
        else:
            line_x = x0
        line_y = y0 + i * line_h
        _draw_tracked_text(draw, (line_x, line_y), line, font, block.color, tracking_px)

    return x0, y0, block_w, block_h


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
    for block in (layout.series, layout.subtitle, layout.title, layout.author, layout.publisher):
        if block is None:
            continue
        _render_block(img, draw, block, cover_w, cover_h, fonts_dir)

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
