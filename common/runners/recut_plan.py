"""The edit decision file for reel-recut: one plan.json, many episodes.

A recut starts from footage that already exists — a person talking to camera —
and the plan says what is laid over it and when. Every time in the plan is a
second on the ORIGINAL clip. The builder trims the opener and tightens pauses
afterwards and moves each time onto the new clock itself, so an editor reads the
times off the transcript and never recomputes them when a cut changes.

Paths in the plan are relative to the plan file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

W, H, FPS = 1080, 1920, 30

# The screen splits here while a list panel is up: speaker above, list below.
STACK_Y = 900
CAPTION_Y, CAPTION_Y_STACK = 1245, 792

ITEM_KINDS = ("chip", "big", "vs", "tags", "url", "broll", "panel")
CHIP_STYLES = ("plain", "warn", "ok", "loc", "save", "comment", "quote", "ask")
PANEL_STYLES = ("num", "check", "cross", "flag")

# (zoom, where the face sits on the canvas in px; None keeps the source framing)
DEFAULT_FRAMING = {"wide": (1.0, None), "close": (1.35, 680), "stack": (1.45, 440)}

_FONT_DIRS = (
    Path(__file__).resolve().parents[2] / "skills" / "cover-maker" / "fonts",
    Path(__file__).resolve().parents[2] / "cover-maker" / "fonts",
)


@dataclass(frozen=True)
class Brand:
    wordmark: tuple[str, str]
    accent: str
    second: str
    ink: str
    display_font: Path
    text_font: Path
    caption_weight: int = 850


@dataclass(frozen=True)
class Plan:
    root: Path
    series: str
    out: Path
    work: Path
    brand: Brand
    end: dict
    music: dict | None
    framing: dict
    episodes: list[dict] = field(default_factory=list)

    def episode(self, number: int) -> dict:
        for ep in self.episodes:
            if ep["n"] == number:
                return ep
        raise KeyError(f"no episode {number} in the plan")

    def path(self, relative: str) -> Path:
        return (self.root / relative).resolve()

    def presets(self, ep: dict) -> dict:
        """The framing preset an episode names, laid over the defaults."""
        chosen = self.framing.get(ep.get("framing", "default"), {})
        return {mode: tuple(chosen.get(mode, default)) for mode, default in DEFAULT_FRAMING.items()}


def _bundled_font() -> Path:
    for folder in _FONT_DIRS:
        font = folder / "Inter-VF.ttf"
        if font.is_file():
            return font
    return _FONT_DIRS[0] / "Inter-VF.ttf"


def _brand(raw: dict, root: Path) -> Brand:
    colors = raw.get("colors", {})
    fonts = raw.get("fonts", {})
    fallback = _bundled_font()
    mark = raw.get("wordmark") or ["", ""]
    return Brand(
        wordmark=(mark[0], mark[1] if len(mark) > 1 else ""),
        accent=colors.get("accent", "#ff6544"),
        second=colors.get("second", "#19c2b8"),
        ink=colors.get("ink", "#0a1413"),
        display_font=(root / fonts["display"]).resolve() if fonts.get("display") else fallback,
        text_font=(root / fonts["text"]).resolve() if fonts.get("text") else fallback,
        caption_weight=int(raw.get("caption_weight", 850)),
    )


def load(plan_file: Path) -> Plan:
    raw = json.loads(plan_file.read_text(encoding="utf-8"))
    root = plan_file.resolve().parent
    return Plan(
        root=root,
        series=raw.get("series", ""),
        out=(root / raw.get("out", "final")).resolve(),
        work=(root / raw.get("work", "work")).resolve(),
        brand=_brand(raw.get("brand", {}), root),
        end=raw.get("end", {}),
        music=raw.get("music"),
        framing=raw.get("framing", {}),
        episodes=raw.get("episodes", []),
    )


def _span_problem(item: dict) -> str | None:
    at = item.get("at")
    if not (isinstance(at, list) and len(at) == 2 and at[0] < at[1]):
        return f"'at' must be [start, end] with start < end, got {at!r}"
    return None


def _style_problem(item: dict) -> str | None:
    kind, style = item.get("kind"), item.get("style")
    if kind == "panel" and style not in PANEL_STYLES:
        return f"panel style {style!r} is not one of {', '.join(PANEL_STYLES)}"
    if kind == "chip" and style not in CHIP_STYLES:
        return f"chip style {style!r} is not one of {', '.join(CHIP_STYLES)}"
    return None


def _item_problems(plan: Plan, item: dict) -> list[str]:
    kind = item.get("kind")
    if kind not in ITEM_KINDS:
        return [f"unknown item kind {kind!r}"]
    found = [p for p in (_span_problem(item), _style_problem(item)) if p]
    if kind == "broll" and not plan.path(item.get("asset", "?")).is_file():
        found.append(f"b-roll asset not found: {item.get('asset')}")
    return found


def _episode_problems(plan: Plan, ep: dict) -> list[str]:
    found = []
    for key in ("n", "src", "words", "slug", "face", "hook"):
        if key not in ep:
            found.append(f"missing '{key}'")
    for key in ("src", "words"):
        if key in ep and not plan.path(ep[key]).is_file():
            found.append(f"{key} not found: {ep[key]}")
    for item in ep.get("items", []):
        found.extend(_item_problems(plan, item))
    tail = ep.get("tail")
    if tail and tail.get("asset") and not plan.path(tail["asset"]).is_file():
        found.append(f"tail asset not found: {tail['asset']}")
    return found


def problems(plan: Plan) -> list[str]:
    """Everything that would stop a build, named by episode — read before rendering."""
    found = []
    if not plan.episodes:
        found.append("the plan has no episodes")
    for font in (plan.brand.display_font, plan.brand.text_font):
        if not font.is_file():
            found.append(f"font not found: {font}")
    if plan.music and not plan.path(plan.music.get("file", "?")).is_file():
        found.append(f"music not found: {plan.music.get('file')}")
    for ep in plan.episodes:
        label = f"episode {ep.get('n', '?')}"
        found.extend(f"{label}: {p}" for p in _episode_problems(plan, ep))
    return found
