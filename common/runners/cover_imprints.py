"""Book-cover imprint presets.

Each preset encodes BOTH:
  1. A `TypeLayout` for the typography composer (typography.py)
  2. A `prompt_fragment` to inject into the image-gen prompt so the
     generated visual harmonizes with the typographic system

Pulled from research on real publisher design systems — NYRB Classics,
Penguin Marber Grid, MIT Essential Knowledge, Picador Modern, Faber, etc.

Each imprint also declares a recommended `genre` set so we can auto-pick
imprint when only `--genre` is provided.
"""

from __future__ import annotations

from dataclasses import dataclass

from .typography import Decoration, TextBlock, TypeLayout


@dataclass(frozen=True)
class ImprintPreset:
    """One imprint's full design system."""

    name: str                      # slug, e.g. "nyrb-classics"
    display_name: str              # human label
    description: str               # one-line aesthetic summary
    layout: TypeLayout             # typography spec (title-text gets injected at compose time)
    prompt_fragment: str           # image-gen anchor — what kind of art the model should produce
    genres: tuple[str, ...]        # genres this imprint fits naturally


def _build_layout(
    title_font: str, title_weight: int, title_size: float, title_color: str,
    title_anchor: str, title_case: str, title_tracking: float,
    title_align: str, title_margin_top: float, title_max_lines: int,
    author_font: str, author_weight: int, author_size: float, author_color: str,
    author_anchor: str, author_tracking: float,
    decorations: list[Decoration] | None = None,
    title_band: dict | None = None,
    title_margin_x: float = 0.10,
    author_margin_bottom: float = 0.08,
) -> TypeLayout:
    """Helper to keep the imprint dict below readable."""
    return TypeLayout(
        title=TextBlock(
            text="",
            font=title_font,
            weight=title_weight,
            size_fraction=title_size,
            color=title_color,
            case=title_case,
            anchor=title_anchor,
            tracking=title_tracking,
            align=title_align,
            margin_top_fraction=title_margin_top,
            margin_x_fraction=title_margin_x,
            max_lines=title_max_lines,
            line_height=1.05,
        ),
        author=TextBlock(
            text="",
            font=author_font,
            weight=author_weight,
            size_fraction=author_size,
            color=author_color,
            case="preserve",
            anchor=author_anchor,
            tracking=author_tracking,
            align="center",
            margin_bottom_fraction=author_margin_bottom,
            max_lines=1,
        ),
        decorations=decorations or [],
        title_band=title_band,
    )


# ─── IMPRINT PRESETS ───────────────────────────────────────────────────────────


IMPRINTS: dict[str, ImprintPreset] = {

    # ── NYRB Classics ──
    # Painting/photo background, centered colored title-box ~1/3 from top,
    # FF Meta caps proxy (we substitute Inter Bold). Highly recognizable.
    "nyrb-classics": ImprintPreset(
        name="nyrb-classics",
        display_name="NYRB Classics",
        description="Painting / photograph background, centered title plate, modernist sans caps — New York Review Books Classics aesthetic.",
        layout=TypeLayout(
            title=TextBlock(
                text="",
                font="Inter", weight=700, size_fraction=0.052, color="#FFFFFF",
                case="upper", tracking=0.06, align="center", anchor="top-center",
                margin_top_fraction=0.20, margin_x_fraction=0.15, max_lines=4,
                line_height=1.10,
            ),
            # Author sits INSIDE the colored band, below the title.
            # Use anchor="top-center" + explicit margin_top to position inside band.
            author=TextBlock(
                text="",
                font="Inter", weight=500, size_fraction=0.020, color="#FFFFFF",
                case="preserve", tracking=0.14, align="center", anchor="top-center",
                margin_top_fraction=0.43, margin_x_fraction=0.15, max_lines=1,
            ),
            title_band={"y_start": 0.15, "y_end": 0.50, "color": "#8B2C28", "opacity": 0.92},
        ),
        prompt_fragment=(
            "Painterly background art — atmospheric oil-painting or grainy mid-century photograph, "
            "muted earthy palette (deep umber, faded ochre, dusty blue), evocative of mid-20th-century "
            "European literary fiction. SUBTLE TEXTURE: visible canvas weave or paper grain. "
            "NEGATIVE SPACE: leave the upper third area as a calmer / less detailed region "
            "(the title plate will be composited over it). "
            "NO embedded text, no lettering, no typography, no title — pure background art."
        ),
        genres=("literary-fiction", "classics", "translated-fiction", "essay"),
    ),

    # ── Penguin Marber Grid ──
    # The 1963 Marber tri-band: title 27% top / image 50% middle / author 23% bottom.
    "penguin-marber-grid": ImprintPreset(
        name="penguin-marber-grid",
        display_name="Penguin Marber Grid",
        description="1963 Romek Marber tri-band: title band top, image band middle, author/imprint band bottom. Helvetica + single accent color.",
        layout=_build_layout(
            title_font="Inter", title_weight=600, title_size=0.060, title_color="#1A1A1A",
            title_anchor="top-center", title_case="preserve", title_tracking=0.02,
            title_align="center", title_margin_top=0.05, title_max_lines=3,
            title_margin_x=0.08,
            author_font="Inter", author_weight=500, author_size=0.025, author_color="#1A1A1A",
            author_anchor="bottom-center", author_tracking=0.05,
            author_margin_bottom=0.06,
            title_band={"y_start": 0.0, "y_end": 0.27, "color": "#F5F0E8", "opacity": 1.0},
            decorations=[
                Decoration(kind="hline", color="#1A1A1A", thickness_fraction=0.002,
                           length_fraction=1.0, position_y_fraction=0.27),
                Decoration(kind="hline", color="#1A1A1A", thickness_fraction=0.002,
                           length_fraction=1.0, position_y_fraction=0.77),
            ],
        ),
        prompt_fragment=(
            "Single bold conceptual symbol or geometric illustration, FLAT VECTOR aesthetic, "
            "2-3 color palette (warm cream off-white background #F5F0E8 + deep ink + one accent: "
            "vermillion red OR avocado green OR ochre yellow). 1960s European design vocabulary, "
            "Marber Grid era. The illustration sits ENTIRELY in the middle 50% of the frame — "
            "leave the top 27% and bottom 23% as PURE solid cream background (those zones are "
            "reserved for typography). Anti-photo: cue 'illustration' not 'photograph'. "
            "NO text, no letters, no title, no author name."
        ),
        genres=("classic-fiction", "crime", "thriller", "non-fiction"),
    ),

    # ── MIT Press Essential Knowledge ──
    # Clean typographic top half, abstract visual lower half, sans-serif modern.
    "mit-essential-knowledge": ImprintPreset(
        name="mit-essential-knowledge",
        display_name="MIT Press Essential Knowledge",
        description="Top half typographic (title dominant), bottom half abstract diagrammatic visual, modern sans-serif. Pocketable academic primer.",
        layout=_build_layout(
            title_font="Inter", title_weight=700, title_size=0.090, title_color="#1A1A1A",
            title_anchor="top-left", title_case="preserve", title_tracking=-0.01,
            title_align="left", title_margin_top=0.10, title_max_lines=4,
            title_margin_x=0.07,
            author_font="Inter", author_weight=500, author_size=0.025, author_color="#1A1A1A",
            author_anchor="bottom-left", author_tracking=0.04,
            author_margin_bottom=0.05,
            title_band={"y_start": 0.0, "y_end": 0.55, "color": "#FFFFFF", "opacity": 1.0},
        ),
        prompt_fragment=(
            "Abstract diagrammatic visual occupying the bottom 45% of the frame ONLY. "
            "Flat geometric shapes, limited palette (white background + single accent color: "
            "process-cyan OR cadmium-red OR chartreuse-yellow), academic-textbook aesthetic. "
            "Think: schematic diagrams from a 1970s science primer. "
            "The TOP 55% of the frame is PURE WHITE with no detail at all "
            "(it's reserved for title typography). "
            "NO embedded text, no labels, no annotations, no lettering. Just shapes."
        ),
        genres=("academic", "non-fiction", "essay", "technology", "science", "popular-science"),
    ),

    # ── Picador Modern Classics ──
    # Typographic top + flat-color minimal visual, refined.
    "picador-modern": ImprintPreset(
        name="picador-modern",
        display_name="Picador Modern Classics",
        description="Refined typographic top with bold display serif, minimal flat-color visual accent below, generous negative space.",
        layout=_build_layout(
            title_font="Playfair Display", title_weight=700, title_size=0.080, title_color="#1A1A1A",
            title_anchor="top-center", title_case="preserve", title_tracking=0.00,
            title_align="center", title_margin_top=0.12, title_max_lines=4,
            title_margin_x=0.10,
            author_font="EB Garamond", author_weight=400, author_size=0.028, author_color="#1A1A1A",
            author_anchor="bottom-center", author_tracking=0.10,
            author_margin_bottom=0.06,
            decorations=[
                Decoration(kind="hline", color="#1A1A1A", thickness_fraction=0.0015,
                           length_fraction=0.10, position_y_fraction=0.90),
            ],
        ),
        prompt_fragment=(
            "Single small flat-color symbolic illustration or geometric form, positioned in the "
            "middle-lower portion of the frame (around 55-70% vertical), occupying a SMALL footprint "
            "(about 25% of frame width). Restrained color palette: warm cream background (#F4ECD8) "
            "with a single muted accent (dusty rose OR soft terracotta OR muted teal). "
            "Lots of negative space — most of the cover is the cream background. "
            "Editorial / Picador-modern aesthetic. NO text, no letters, no title."
        ),
        genres=("literary-fiction", "memoir", "essay", "essays"),
    ),

    # ── Faber Poetry / Faber Modernist ──
    # Large typographic statement, bold flat color background, no image (or extremely minimal).
    "faber-modernist": ImprintPreset(
        name="faber-modernist",
        display_name="Faber Modernist",
        description="Typography-as-image — Faber & Faber poetry / criticism style. Large display lettering, bold flat color, no photo.",
        layout=_build_layout(
            title_font="Cinzel", title_weight=700, title_size=0.110, title_color="#F5F0E8",
            title_anchor="center", title_case="upper", title_tracking=0.04,
            title_align="center", title_margin_top=0.30, title_max_lines=3,
            title_margin_x=0.10,
            author_font="EB Garamond", author_weight=400, author_size=0.030, author_color="#F5F0E8",
            author_anchor="bottom-center", author_tracking=0.18,
            author_margin_bottom=0.08,
            decorations=[
                Decoration(kind="hline", color="#F5F0E8", thickness_fraction=0.0015,
                           length_fraction=0.15, position_y_fraction=0.85),
            ],
        ),
        prompt_fragment=(
            "Solid bold flat color background — choose ONE rich saturated color: "
            "deep cobalt blue (#1E3A8A) OR oxblood red (#722F37) OR olive green (#556B2F) "
            "OR aubergine purple (#4A1E50). NO illustration. NO image. NO photograph. "
            "Just a SOLID FIELD of one color with subtle paper grain texture suggesting "
            "letterpress printing. Faber & Faber poetry aesthetic. "
            "NO text, no letters, no title — only the color field."
        ),
        genres=("poetry", "essay", "criticism", "manifesto", "non-fiction"),
    ),
}


# ─── genre → imprint default mapping ───────────────────────────────────────────


GENRE_DEFAULT_IMPRINT: dict[str, str] = {
    "literary-fiction": "nyrb-classics",
    "classics": "nyrb-classics",
    "translated-fiction": "nyrb-classics",
    "thriller": "penguin-marber-grid",
    "crime": "penguin-marber-grid",
    "non-fiction": "mit-essential-knowledge",
    "academic": "mit-essential-knowledge",
    "popular-science": "mit-essential-knowledge",
    "science": "mit-essential-knowledge",
    "technology": "mit-essential-knowledge",
    "memoir": "picador-modern",
    "essay": "picador-modern",
    "essays": "picador-modern",
    "poetry": "faber-modernist",
    "criticism": "faber-modernist",
    "manifesto": "faber-modernist",
}


def get_imprint(name: str) -> ImprintPreset:
    """Resolve imprint by name. Raises KeyError if unknown."""
    if name not in IMPRINTS:
        raise KeyError(
            f"unknown imprint '{name}'. Known: {sorted(IMPRINTS)}"
        )
    return IMPRINTS[name]


def resolve_imprint(imprint: str | None, genre: str | None) -> ImprintPreset | None:
    """Pick an imprint:
      1. Explicit --imprint wins
      2. Otherwise --genre maps to a default
      3. Else None (no two-pass typography)
    """
    if imprint:
        return get_imprint(imprint)
    if genre and genre in GENRE_DEFAULT_IMPRINT:
        return IMPRINTS[GENRE_DEFAULT_IMPRINT[genre]]
    return None


def apply_text(layout: TypeLayout, title: str, author: str | None,
               subtitle: str | None = None) -> TypeLayout:
    """Inject runtime text into a preset's layout (which ships with empty text fields)."""
    layout.title.text = title
    if layout.author is not None and author:
        layout.author.text = author
    if subtitle and layout.subtitle is not None:
        layout.subtitle.text = subtitle
    return layout
