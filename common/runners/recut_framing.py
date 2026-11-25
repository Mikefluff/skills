"""Punch-ins: when the speaker is shown wide, close, or above a list panel.

A talking head held in one framing for thirty seconds is the reason the footage
looked unfinished. The picture alternates between the source framing and a
closer one, and it changes only where the speaker pauses or where the edit
already cut — a reframe in the middle of a word reads as a glitch, a reframe on
a cut hides the cut.

Everything here returns ffmpeg expressions in `t`, evaluated per frame by
`scale` and `overlay`, so the whole plan is one filter graph and one encode.
"""

from __future__ import annotations

from .recut_plan import H, STACK_Y

Segment = tuple[float, float, str]

FIRST_HOLD, HOLD, LONGEST = 2.9, 2.2, 6.5
# Slow push inside every segment, so a held framing is never a frozen one.
DRIFT, DRIFT_STACK = 0.03, 0.02


def _next_change(t: float, window: tuple[float, float], pauses: list[float], cuts: list[float]) -> float:
    """Where the framing started at `t` should end."""
    a, b = window
    earliest = t + (FIRST_HOLD if t == a == 0 else HOLD)
    forced = [c for c in cuts if t + 0.5 < c < min(earliest, b - 0.3)]
    if forced:
        return forced[0]
    candidates = [p for p in pauses if earliest <= p <= b - 1.4]
    nxt = candidates[0] if candidates else b
    if nxt - t > LONGEST:
        return b if b - t <= LONGEST else t + 4.0
    return nxt


def _alternate(window: tuple[float, float], pauses: list[float], cuts: list[float], mode: str) -> tuple[list[Segment], str]:
    segments, t = [], window[0]
    while t < window[1] - 0.05:
        nxt = _next_change(t, window, pauses, cuts)
        segments.append((t, nxt, mode))
        mode = "close" if mode == "wide" else "wide"
        t = nxt
    return segments, mode


def framing_segments(speech: float, panels: list[tuple[float, float]],
                     pauses: list[float], cuts: list[float]) -> list[Segment]:
    """Wide/close alternation over the speech, with `stack` wherever a panel is up."""
    def in_panel(t: float) -> bool:
        return any(a - 1e-3 <= t < b for a, b in panels)

    edges = sorted({0.0, speech} | {x for span in panels for x in span if x < speech})
    segments: list[Segment] = []
    mode = "wide"
    for a, b in zip(edges, edges[1:]):
        if in_panel(a + 0.01):
            segments.append((a, b, "stack"))
            continue
        run, mode = _alternate((a, b), pauses, cuts, mode)
        segments.extend(run)
    return segments


def _piecewise(segments: list[Segment], value) -> str:
    return "+".join(f"gte(t,{a:.3f})*lt(t,{b:.3f})*({value(a, b, mode)})" for a, b, mode in segments)


def zoom_expr(segments: list[Segment], presets: dict) -> str:
    def zoom(a: float, b: float, mode: str) -> str:
        drift = DRIFT_STACK if mode == "stack" else DRIFT
        return f"{presets[mode][0]}*(1+{drift}*(t-{a:.3f})/{max(b - a, 0.1):.3f})"
    return _piecewise(segments, zoom)


def face_y_expr(segments: list[Segment], presets: dict, face_y: float) -> str:
    """Canvas y the face is held at; the source position when a preset leaves it None."""
    def y(_a: float, _b: float, mode: str) -> str:
        target = presets[mode][1]
        return f"{target if target is not None else face_y * H:.0f}"
    return _piecewise(segments, y)


def floor_expr(segments: list[Segment]) -> str:
    """The lowest canvas row the speaker may cover: the panel's top edge while stacked."""
    def floor(_a: float, _b: float, mode: str) -> str:
        return str(STACK_Y + 60 if mode == "stack" else H)
    return _piecewise(segments, floor)
