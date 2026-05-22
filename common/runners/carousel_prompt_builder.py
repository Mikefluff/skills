"""Carousel prompt builder — assembles figma-rigor image prompts per slide.

Combines:
  1. Style anchor (text-in-image mode block from the chosen carousel style)
  2. Role composition template (per slide role: hook / point / framework / etc.)
  3. Content slots (filled in by the caller — title, body, list items, data points)
  4. Static carousel elements (page indicator + swipe arrow OR end marker + slide marker)
  5. Anti-AI-tells closing modifiers

Result: a single dense paragraph (~800-1500 chars) ready to send to gpt-image-2 /
ideogram-3 / nano-banana-pro / flux-2-pro for one carousel slide.

The builder enforces the rules documented in:
  - common/style-library/carousel/_universal-rules.md  (universal carousel conventions)
  - carousel-builder/references/slide-roles.md         (per-role composition + density)

Public API:
    build_slide_prompt(
        style_anchor: str,         # the text-in-image mode block from the style file
        role: SlideRole,           # one of 9 roles
        slide_number: int,
        total_slides: int,
        content: SlideContent,     # role-specific dataclass
        lang: str = "en",          # "en" | "ru" — chooses page-indicator vocabulary
        is_last: bool = False,     # True → end marker, False → swipe arrow
    ) -> str
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union


SlideRole = Literal[
    "hook", "point", "framework", "data", "steps",
    "comparison", "quote", "myth-vs-truth", "cta",
]

# ─── content dataclasses per role ──────────────────────────────────────────────


@dataclass
class HookContent:
    title: str                          # ≤7 words — the provocation
    subtitle: str | None = None         # ≤10 words — deepening
    visual_hint: str | None = None      # ≤20 words — scene/object dominating frame


@dataclass
class PointContent:
    title: str                          # ≤7 words
    body: str                           # ≤40 words — the development
    attribution: str | None = None      # if quoting


@dataclass
class Box:
    header: str
    body: str


@dataclass
class FrameworkContent:
    framework_name: str                 # ≤6 words
    boxes: list[Box]                    # 2-9 entries
    box_layout: Literal["grid", "2x2", "horizontal", "vertical", "circular"] = "grid"


@dataclass
class DataPoint:
    value: str                          # e.g. "78%", "$2M", "3×"
    caption: str                        # ≤8 words


@dataclass
class DataContent:
    data_points: list[DataPoint]        # 1-4 entries
    source: str | None = None           # ≤10 words attribution


@dataclass
class Step:
    number: int
    header: str
    body: str


@dataclass
class StepsContent:
    process_name: str                   # ≤6 words
    steps: list[Step]                   # 3-7 entries
    direction: Literal["horizontal", "vertical", "circular"] = "horizontal"


@dataclass
class ComparisonSide:
    label: str                          # e.g. "BEFORE", "MYTH"
    body: str                           # ≤25 words


@dataclass
class ComparisonContent:
    comparison_title: str               # ≤6 words
    left: ComparisonSide
    right: ComparisonSide
    divider_style: Literal["vertical-rule", "arrow", "vs-glyph"] = "vertical-rule"


@dataclass
class QuoteAttribution:
    name: str
    context: str = ""


@dataclass
class QuoteContent:
    quote: str                          # ≤25 words
    attribution: QuoteAttribution


@dataclass
class MythTruthContent:
    myth: str                           # ≤20 words
    truth: str                          # ≤20 words
    myth_label: str = "MYTH"
    truth_label: str = "REALITY"


@dataclass
class CtaContent:
    cta_text: str                       # ≤8 words — the action
    context: str | None = None          # ≤15 words — reasoning
    attribution: str | None = None      # brand / author


SlideContent = Union[
    HookContent, PointContent, FrameworkContent, DataContent, StepsContent,
    ComparisonContent, QuoteContent, MythTruthContent, CtaContent,
]


# ─── universal blocks ─────────────────────────────────────────────────────────


_ANTI_AI_TELLS = (
    "Sharp text rendering, every letter fully formed and legible, no melted glyphs, "
    "no gradient text effects, no drop shadows on type unless explicitly described, "
    "no AI-tell face artifacts, no double pupils, no extra fingers, no warped geometry. "
    "All visible text in the image is exactly the text in double quotes — nothing else, "
    "no additional labels, no watermarks, no logos other than what is named, no QR codes, "
    "no website URLs, no email addresses."
)


# ─── per-role scene policy ────────────────────────────────────────────────────
#
# Overrides scene-y style anchors so the same anchor doesn't render an identical
# literal scene on every slide. Style anchor describes VOCABULARY + TREATMENT +
# PALETTE + TYPOGRAPHY — never a fixed setting. The scene per slide is chosen
# per role: hook = literal establishing shot OK; framework/data/steps/comparison/
# myth-vs-truth/point = clean styled background, content dominates; quote/cta =
# minimal single decorative element OK.

_SCENE_POLICY: dict[str, str] = {
    "hook": (
        "BACKGROUND POLICY for this slide: this is the establishing shot of the deck — "
        "a literal scene per the visual hint is OK and welcome. Use the full style "
        "vocabulary as a scene."
    ),
    "point": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field "
        "(palette + paper / leather / fabric / gradient / paint grain — whichever fits "
        "the style). NO literal recurring scene from earlier slides. Apply the style as "
        "PALETTE + TYPOGRAPHY + TREATMENT vocabulary, not as a fixed setting. The text "
        "block dominates."
    ),
    "framework": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field "
        "(palette + texture only). NO literal scene, no recurring environment from "
        "earlier slides. The framework cards / boxes ARE the slide — they fill the "
        "composition. Decorative scene elements would compete with the content."
    ),
    "data": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field. "
        "NO literal scene. The data badges / numbers dominate the composition. "
        "Decorative scene elements would compete with the numbers."
    ),
    "steps": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field. "
        "NO literal scene. The numbered step sequence dominates the composition."
    ),
    "comparison": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field. "
        "NO literal scene. The two-column contrast IS the slide."
    ),
    "quote": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field "
        "with AT MOST ONE small decorative element from the style vocabulary (e.g., a "
        "single inkwell silhouette, a corner ornament, a thin rule, a single ivy leaf). "
        "NO full recurring scene. The quote text dominates."
    ),
    "myth-vs-truth": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field. "
        "NO literal scene. The myth/reality contrast IS the slide."
    ),
    "cta": (
        "BACKGROUND POLICY for this slide: a clean style-appropriate textured field "
        "with AT MOST ONE small decorative element from the style vocabulary "
        "(e.g., a corner ornament, a thin gold rule, a single object silhouette). "
        "NO full recurring scene. The CTA plate dominates."
    ),
}


def _page_indicator(slide_number: int, total: int, lang: str) -> str:
    """Bottom-center page indicator phrasing."""
    if lang == "ru":
        return f'bottom-center small subtle text in italic: "{slide_number} из {total}"'
    return f'bottom-center small subtle text in italic: "{slide_number} of {total}"'


def _navigation_glyph(is_last: bool, lang: str) -> str:
    """Bottom-right swipe arrow (non-last) or end marker (last)."""
    if is_last:
        marker = "конец" if lang == "ru" else "end"
        return f'bottom-right corner small italic: "{marker}" (no swipe arrow — this is the final slide)'
    swipe = "листай →" if lang == "ru" else "swipe →"
    return f'bottom-right corner small italic with a thin arrow glyph: "{swipe}"'


def _slide_marker(slide_number: int, style: Literal["arabic", "roman", "bracketed"]) -> str:
    if style == "roman":
        roman = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                 "XI", "XII", "XIII", "XIV", "XV"][slide_number] if slide_number < 16 else str(slide_number)
        return f'lower-LEFT corner small subdued: "{roman}"'
    if style == "bracketed":
        return f'top-right corner tabular monospace: "[{slide_number:03d}]"'
    return f'top-right corner tabular figures small: "{slide_number}"'


# ─── role-specific composition templates ──────────────────────────────────────


def _hook_layout(content: HookContent) -> str:
    parts: list[str] = []
    parts.append(
        f'COMPOSITION: large headline upper-center on a style-appropriate underlay/plate, '
        f'main headline: "{content.title}".'
    )
    if content.subtitle:
        parts.append(
            f'Immediately beneath the headline, smaller subtitle on the same plate or area: '
            f'"{content.subtitle}".'
        )
    if content.visual_hint:
        parts.append(f'Visual context: {content.visual_hint}')
    parts.append(
        "Generous negative space; this slide must read as a HOOK — sparse, sharp, "
        "earning the swipe to the next slide. No list, no bullets, no body paragraph."
    )
    return " ".join(parts)


def _point_layout(content: PointContent) -> str:
    parts: list[str] = []
    parts.append(
        f'COMPOSITION: headline upper-center: "{content.title}".'
    )
    parts.append(
        f'Body paragraph centered on a style-appropriate plate, 1-2 sentences: "{content.body}".'
    )
    if content.attribution:
        parts.append(f'Small attribution beneath the body in italic: "{content.attribution}".')
    return " ".join(parts)


def _framework_layout(content: FrameworkContent) -> str:
    parts: list[str] = []
    parts.append(
        f'COMPOSITION: small title at top: "{content.framework_name}".'
    )
    layout_desc = {
        "grid": f"{len(content.boxes)}-box grid layout centered on the frame",
        "2x2": "2x2 quadrant matrix centered on the frame",
        "horizontal": f"{len(content.boxes)} boxes arranged in a horizontal row",
        "vertical": f"{len(content.boxes)} boxes stacked vertically",
        "circular": f"{len(content.boxes)} boxes arranged around a central circle",
    }
    parts.append(f'Layout: {layout_desc[content.box_layout]}.')
    for i, box in enumerate(content.boxes, 1):
        parts.append(f'Box {i}: header "{box.header}", body "{box.body}".')
    parts.append("Each box has a thin border or background tint in style-appropriate color. Visual rhythm — the framework IS the slide.")
    return " ".join(parts)


def _data_layout(content: DataContent) -> str:
    parts: list[str] = []
    if len(content.data_points) == 1:
        dp = content.data_points[0]
        parts.append(
            f'COMPOSITION: one massive number dominating the frame in a circle / pill / badge: "{dp.value}". '
            f'Caption beneath: "{dp.caption}".'
        )
    else:
        layout = "horizontal row" if len(content.data_points) <= 3 else "2x2 grid"
        parts.append(
            f'COMPOSITION: {len(content.data_points)} data badges arranged in a {layout} centered on the frame.'
        )
        for i, dp in enumerate(content.data_points, 1):
            parts.append(f'Badge {i}: large number "{dp.value}" + caption beneath "{dp.caption}".')
    if content.source:
        parts.append(f'Tiny attribution near the bottom: "{content.source}".')
    return " ".join(parts)


def _steps_layout(content: StepsContent) -> str:
    parts: list[str] = []
    parts.append(f'COMPOSITION: small title at top: "{content.process_name}".')
    dir_desc = {
        "horizontal": f"horizontal sequence of {len(content.steps)} numbered steps with arrows between them",
        "vertical": f"vertical stack of {len(content.steps)} numbered steps with arrows downward",
        "circular": f"{len(content.steps)} numbered steps arranged in a circle with arrows showing the loop",
    }
    parts.append(f'Layout: {dir_desc[content.direction]}.')
    for step in content.steps:
        parts.append(f'Step {step.number}: number "{step.number:02d}" + header "{step.header}" + body "{step.body}".')
    return " ".join(parts)


def _comparison_layout(content: ComparisonContent) -> str:
    parts: list[str] = []
    parts.append(f'COMPOSITION: title at top: "{content.comparison_title}".')
    divider_desc = {
        "vertical-rule": "thin vertical line of accent color separating the two halves",
        "arrow": "connecting arrow from left to right indicating direction of change",
        "vs-glyph": "large 'VS' glyph in the center between the two halves",
    }
    parts.append(
        f'Two-column layout: left column header "{content.left.label}", left body "{content.left.body}". '
        f'Right column header "{content.right.label}", right body "{content.right.body}". '
        f'Divider: {divider_desc[content.divider_style]}.'
    )
    return " ".join(parts)


def _quote_layout(content: QuoteContent) -> str:
    parts: list[str] = []
    parts.append('COMPOSITION: large decorative open-quote glyph upper-left of the quote area.')
    parts.append(
        f'Quote body centered, taking 60-70% of frame, in italic or display-serif: "{content.quote}".'
    )
    attr = content.attribution
    if attr.context:
        parts.append(f'Attribution beneath the quote in smaller weight: "— {attr.name}, {attr.context}".')
    else:
        parts.append(f'Attribution beneath the quote in smaller weight: "— {attr.name}".')
    parts.append("Generous negative space around the quote.")
    return " ".join(parts)


def _myth_truth_layout(content: MythTruthContent) -> str:
    parts: list[str] = []
    parts.append('COMPOSITION: vertical split — top half MYTH zone, bottom half REALITY zone, divided by a thick horizontal accent line.')
    parts.append(f'Top half: label in accent color "{content.myth_label}". Body sentence: "{content.myth}".')
    parts.append(f'Bottom half: label in contrasting accent color "{content.truth_label}". Body sentence: "{content.truth}".')
    parts.append("The divider line color should be the strongest accent in the style palette.")
    return " ".join(parts)


def _cta_layout(content: CtaContent) -> str:
    parts: list[str] = []
    parts.append(
        f'COMPOSITION: primary CTA text on a prominent plate / button / underlay, centered or upper-center: "{content.cta_text}".'
    )
    if content.context:
        parts.append(f'Secondary context line beneath the CTA, smaller: "{content.context}".')
    if content.attribution:
        parts.append(f'Attribution somewhere in frame, small: "{content.attribution}".')
    return " ".join(parts)


_LAYOUT_BUILDERS = {
    "hook": _hook_layout,
    "point": _point_layout,
    "framework": _framework_layout,
    "data": _data_layout,
    "steps": _steps_layout,
    "comparison": _comparison_layout,
    "quote": _quote_layout,
    "myth-vs-truth": _myth_truth_layout,
    "cta": _cta_layout,
}


# ─── main public API ──────────────────────────────────────────────────────────


def build_slide_prompt(
    style_anchor: str,
    role: SlideRole,
    slide_number: int,
    total_slides: int,
    content: SlideContent,
    lang: str = "en",
    is_last: bool = False,
    slide_marker_style: Literal["arabic", "roman", "bracketed"] = "arabic",
) -> str:
    """Assemble a figma-rigor image prompt for one carousel slide.

    Args:
        style_anchor: Verbatim text from the style file's "Style anchor (text-in-image mode)" block.
        role: One of the 9 supported slide roles.
        slide_number: 1-indexed position of this slide.
        total_slides: Total slides in the carousel.
        content: Role-specific dataclass (HookContent, PointContent, etc.).
        lang: "en" | "ru" — controls page indicator / swipe vocabulary.
        is_last: True for the final slide (uses end marker instead of swipe arrow).
        slide_marker_style: "arabic" / "roman" / "bracketed" — style of the slide-number marker.

    Returns:
        A single-paragraph image prompt, ~800-1500 chars, ready to send to the image provider.
    """
    if role not in _LAYOUT_BUILDERS:
        raise ValueError(f"unknown role '{role}'. Valid: {list(_LAYOUT_BUILDERS)}")

    layout_block = _LAYOUT_BUILDERS[role](content)

    parts: list[str] = []
    # 1. Style anchor (vocabulary + treatment + palette + typography)
    parts.append(style_anchor.strip())
    # 2. Per-role scene policy — overrides scene-y style anchors so non-hook slides
    #    do not repeat the same literal setting from the anchor
    parts.append(_SCENE_POLICY[role])
    # 3. Role-specific composition
    parts.append(layout_block)
    # 4. Static carousel elements
    parts.append(_page_indicator(slide_number, total_slides, lang) + ".")
    parts.append(_navigation_glyph(is_last, lang) + ".")
    parts.append(_slide_marker(slide_number, slide_marker_style) + ".")
    # 5. Anti-AI-tells
    parts.append(_ANTI_AI_TELLS)

    return " ".join(parts)


# ─── self-test ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    style = (
        "Dark academia photograph, single warm light source from upper-left, deep chiaroscuro. "
        "Headline set in old-style serif (Garamond, Caslon, Tiempos), parchment-cream ink "
        "on aged parchment underlay floated in the lit zone of the frame. A small italic caption "
        "beneath in deep sepia. Roman numeral slide indicator in the lower-outer corner. "
        "Leather, brass, and manuscript detail in the photographic subject beneath."
    )

    hook = build_slide_prompt(
        style_anchor=style,
        role="hook",
        slide_number=1,
        total_slides=5,
        content=HookContent(
            title="Software, slowly.",
            subtitle="A manifesto.",
            visual_hint="Library reading room at dusk, brass lamp glowing, leather books, dust motes.",
        ),
        lang="ru",
        is_last=False,
        slide_marker_style="roman",
    )
    print("─── HOOK ───")
    print(hook)
    print()

    framework = build_slide_prompt(
        style_anchor=style,
        role="framework",
        slide_number=2,
        total_slides=5,
        content=FrameworkContent(
            framework_name="Four laws of slow software",
            boxes=[
                Box(header="01 PATIENCE", body="Wait for the right shape to emerge."),
                Box(header="02 CRAFT", body="Build with the hand, not the deadline."),
                Box(header="03 LEGIBILITY", body="Make the code readable to your replacement."),
                Box(header="04 REPAIR", body="Maintain is more honest than ship."),
            ],
            box_layout="2x2",
        ),
        lang="ru",
        slide_marker_style="roman",
    )
    print("─── FRAMEWORK ───")
    print(framework)
    print()

    cta = build_slide_prompt(
        style_anchor=style,
        role="cta",
        slide_number=5,
        total_slides=5,
        content=CtaContent(
            cta_text="Out now — link in bio",
            context="The Slow Software Manifesto",
            attribution="Mikhail Savchenko",
        ),
        lang="ru",
        is_last=True,
        slide_marker_style="roman",
    )
    print("─── CTA ───")
    print(cta)
