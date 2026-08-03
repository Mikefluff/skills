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

import copy
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


# Every preset below builds its TypeLayout directly. A _build_layout() helper
# used to flatten the two TextBlocks into one call, which meant twenty
# positional-ish parameters named title_*/author_* — a signature nobody could
# read and the worst one in the repo. Four of the five imprints went through it
# and one did not, so the file had two shapes for the same thing anyway.


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
        layout=TypeLayout(
            title=TextBlock(
                text="",
                font="Inter", weight=600, size_fraction=0.060, color="#1A1A1A",
                case="preserve", tracking=0.02, align="center", anchor="top-center",
                margin_top_fraction=0.05, margin_x_fraction=0.08, max_lines=3,
                line_height=1.05,
            ),
            author=TextBlock(
                text="",
                font="Inter", weight=500, size_fraction=0.025, color="#1A1A1A",
                case="preserve", tracking=0.05, align="center", anchor="bottom-center",
                margin_bottom_fraction=0.06, max_lines=1,
            ),
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
        layout=TypeLayout(
            title=TextBlock(
                text="",
                font="Inter", weight=700, size_fraction=0.090, color="#1A1A1A",
                case="preserve", tracking=-0.01, align="left", anchor="top-left",
                margin_top_fraction=0.10, margin_x_fraction=0.07, max_lines=4,
                line_height=1.05,
            ),
            # Author is bottom-left to match the title's rag, but the text itself
            # is centre-aligned within its own single line — which is a no-op.
            author=TextBlock(
                text="",
                font="Inter", weight=500, size_fraction=0.025, color="#1A1A1A",
                case="preserve", tracking=0.04, align="center", anchor="bottom-left",
                margin_bottom_fraction=0.05, max_lines=1,
            ),
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
        layout=TypeLayout(
            title=TextBlock(
                text="",
                font="Playfair Display", weight=700, size_fraction=0.080, color="#1A1A1A",
                case="preserve", tracking=0.00, align="center", anchor="top-center",
                margin_top_fraction=0.12, margin_x_fraction=0.10, max_lines=4,
                line_height=1.05,
            ),
            author=TextBlock(
                text="",
                font="EB Garamond", weight=400, size_fraction=0.028, color="#1A1A1A",
                case="preserve", tracking=0.10, align="center", anchor="bottom-center",
                margin_bottom_fraction=0.06, max_lines=1,
            ),
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
        layout=TypeLayout(
            title=TextBlock(
                text="",
                font="Cinzel", weight=700, size_fraction=0.110, color="#F5F0E8",
                case="upper", tracking=0.04, align="center", anchor="center",
                margin_top_fraction=0.30, margin_x_fraction=0.10, max_lines=3,
                line_height=1.05,
            ),
            author=TextBlock(
                text="",
                font="EB Garamond", weight=400, size_fraction=0.030, color="#F5F0E8",
                case="preserve", tracking=0.18, align="center", anchor="bottom-center",
                margin_bottom_fraction=0.08, max_lines=1,
            ),
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
    """A copy of `layout` with the runtime text filled in.

    Copied, not written into. The presets in IMPRINTS are module-level shared
    state that ships with empty text fields, and this used to fill them in
    place: a second cover in the same process started from the first cover's
    text, and since an empty author skipped the write entirely, book two was
    published under book one's author. One process per CLI invocation hid it.
    """
    layout = copy.deepcopy(layout)
    layout.title.text = title
    if layout.author is not None:
        layout.author.text = author or ""
    if layout.subtitle is not None:
        layout.subtitle.text = subtitle or ""
    return layout
