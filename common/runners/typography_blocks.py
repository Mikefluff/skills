"""Typesetting one text block — the spec vocabulary and the block renderer.

Split out of typography.py, which had grown past the module-size gate. This half
answers "what is a text block and how is one drawn"; typography.py answers "how
is a whole cover composed". The spec dataclasses live here because the renderer
needs them and nothing here needs the composer — the dependency runs one way.

TextBlock, Decoration and TypeLayout are re-exported from typography, so
`from .typography import TextBlock` keeps working.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from PIL import ImageDraw, ImageFont


# ─── default fonts directory (overridable) ─────────────────────────────────────

DEFAULT_FONTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "cover-maker" / "fonts"


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


@dataclass(frozen=True)
class _Pen:
    """The drawing context for one text run — measuring and rendering agree."""

    draw: ImageDraw.ImageDraw
    font: ImageFont.FreeTypeFont
    tracking_px: int = 0
    fill: str = "#000000"


def _draw_tracked_text(pen: _Pen, xy: tuple[int, int], text: str, align_offset: int = 0) -> None:
    """Draw text with manual per-glyph spacing for tracking control."""
    if pen.tracking_px == 0:
        pen.draw.text((xy[0] + align_offset, xy[1]), text, font=pen.font, fill=pen.fill)
        return
    x = xy[0] + align_offset
    for ch in text:
        pen.draw.text((x, xy[1]), ch, font=pen.font, fill=pen.fill)
        bbox = pen.draw.textbbox((0, 0), ch, font=pen.font)
        x += (bbox[2] - bbox[0]) + pen.tracking_px


def _measure_tracked(pen: _Pen, text: str) -> int:
    """Width of `text` rendered with the pen's tracking."""
    if pen.tracking_px == 0:
        bbox = pen.draw.textbbox((0, 0), text, font=pen.font)
        return bbox[2] - bbox[0]
    total = 0
    for ch in text:
        bbox = pen.draw.textbbox((0, 0), ch, font=pen.font)
        total += (bbox[2] - bbox[0]) + pen.tracking_px
    return max(0, total - pen.tracking_px)  # no trailing gap


# ─── block positioning ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _Box:
    w: int
    h: int


@dataclass(frozen=True)
class _Margins:
    top: int
    bottom: int
    x: int


def _anchor_origin(anchor: Anchor, block: _Box, cover: _Box, margins: _Margins) -> tuple[int, int]:
    """Top-left (x, y) for a block, given its anchor and the cover dimensions."""
    if anchor.endswith("left"):
        x = margins.x
    elif anchor.endswith("right"):
        x = cover.w - margins.x - block.w
    else:  # center
        x = (cover.w - block.w) // 2

    if anchor.startswith("top"):
        y = margins.top
    elif anchor.startswith("bottom"):
        y = cover.h - margins.bottom - block.h
    else:  # center
        y = (cover.h - block.h) // 2
    return x, y


# ─── render one block ──────────────────────────────────────────────────────────


def _draw_lines(pen: _Pen, lines: list[str], widths: list[int],
                geometry: tuple[int, int, int, int], align: str) -> None:
    """Lay the wrapped lines out, each aligned within the block's own width."""
    x0, y0, block_w, line_h = geometry
    for i, line in enumerate(lines):
        if align == "center":
            line_x = x0 + (block_w - widths[i]) // 2
        elif align == "right":
            line_x = x0 + (block_w - widths[i])
        else:
            line_x = x0
        _draw_tracked_text(pen, (line_x, y0 + i * line_h), line)


def _render_block(draw: ImageDraw.ImageDraw, block: TextBlock, cover: _Box,
                  fonts_dir: Path) -> tuple[int, int, int, int] | None:
    """Render `block`. Returns (x, y, w, h) of the rendered area, None if empty."""
    if not block.text:
        return None

    size_px = max(8, int(cover.h * block.size_fraction))
    pen = _Pen(
        draw=draw,
        font=_load_font(block.font, size_px, block.weight, fonts_dir),
        tracking_px=int(block.tracking * size_px) if block.tracking else 0,
        fill=block.color,
    )

    margin_x = int(cover.w * block.margin_x_fraction)
    # Wrapping measures without tracking. Approximate, but headlines are short
    # enough that the error never costs a line.
    lines = _wrap_text(
        draw, _apply_case(block.text, block.case), pen.font,
        cover.w - 2 * margin_x, block.max_lines,
    )
    if not lines:
        return None

    line_widths = [_measure_tracked(pen, ln) for ln in lines]
    line_h = int(size_px * block.line_height)
    extent = _Box(w=max(line_widths), h=line_h * len(lines))

    margins = _Margins(
        top=int(cover.h * block.margin_top_fraction),
        bottom=int(cover.h * block.margin_bottom_fraction),
        x=margin_x,
    )
    x0, y0 = _anchor_origin(block.anchor, extent, cover, margins)
    x0 += int(cover.w * block.offset_x_fraction)
    y0 += int(cover.h * block.offset_y_fraction)

    _draw_lines(pen, lines, line_widths, (x0, y0, extent.w, line_h), block.align)
    return x0, y0, extent.w, extent.h
