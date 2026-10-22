"""The joins of a cut: what the viewer is carried across at every cut, and where nothing carries them.

A cut feels abrupt when the picture jumps place, time or scale with nothing to hold on to: no flight, no fade,
no shared sound, no matching shape. `join_problems(plan, transitions)` walks the cut in clock order and
reports, for each pair of neighbouring shots, a sentence per problem:

- a jump to another place on a plain cut or a whip (a new location, inside a scene or across one), with no
  bridge, no dip or iris and no moving establishing shot to land on; a new scene in the same room is no jump;
- a jump in the time of day (night to morning) on anything but a bridge, a dip or an iris;
- a bridge played in part: a first-and-last-frame flight only joins its two shots when the cut plays all of it,
  from its first frame to its last (faster if it must be short), never a window out of its middle;
- a jump cut: the same people, the same size and no camera move on both sides of a cut in one scene.

The picture itself (how far the last frame of one shot is from the first of the next in light and colour)
is measured by cli/reel_joins on the kept parts; this module reads only the plan.
"""

from __future__ import annotations

import re
import sys
from typing import Any, TextIO

from .shot_coverage import read_shot

JOINERS = ("dip", "iris")  # transitions that carry a jump in place or time on their own
_TIMES = (("night", r"\bnight\b|\bstars?\b|moonlit"), ("dusk", r"\bdusk\b|\bevening\b|sunset|twilight"),
          ("dawn", r"\bdawn\b|sunrise"), ("day", r"\bby day\b|\bmorning\b|\bdaylight\b|\bmidday\b|\bnoon\b|sun\b"))
_BRIDGE_SLACK = 0.5  # seconds of a bridge's render the cut may leave off its two ends together


def time_of_day(shot: dict[str, Any]) -> str | None:
    """night | dusk | dawn | day, read off the body's light; None when it does not say."""
    body = (shot.get("body") or shot.get("prompt") or "").split("[Overall style]")[0]
    for name, pattern in _TIMES:
        if re.search(pattern, body, re.I):
            return name
    return None


def live(plan: dict[str, Any]) -> list[dict[str, Any]]:
    shots = [s for s in plan.get("shots") or [] if not s.get("cut")]
    if all(s.get("clock_at") is not None for s in shots):
        shots.sort(key=lambda s: float(s["clock_at"]))
    return shots


def bridge_played(shot: dict[str, Any], speed: float = 1.0) -> tuple[float, float]:
    """(seconds of the render left off its head, seconds left off its tail) as the cut plays the bridge."""
    render = float((shot.get("kwargs") or {}).get("duration_seconds") or 0)
    head = float(shot.get("trim_start") or 0)
    used = float(shot.get("trim_seconds") or render) * speed
    return head, max(0.0, render - head - used)


def _bridge_problem(shot: dict[str, Any], speed: float) -> str | None:
    if not shot.get("bridge") or shot.get("clip") or shot.get("speed"):
        return None  # a bridge given its own speed was cut short on purpose (it lands early, before a morph)
    head, tail = bridge_played(shot, speed)
    if head + tail <= _BRIDGE_SLACK:
        return None
    return (f"{shot['label']}: bridge played in part ({head:.1f} s off its head, {tail:.1f} s off its tail): it "
            "neither leaves the last shot's frame nor lands on the next one's; play the whole flight, faster")


def _place(shot: dict[str, Any]) -> Any:
    return shot.get("location") or shot.get("scene")


def _place_problem(prev: dict[str, Any], shot: dict[str, Any], into: str, sizes: dict[str, Any]) -> str | None:
    if prev.get("bridge") or shot.get("bridge") or into in JOINERS:
        return None
    if not prev.get("location") and not shot.get("location") or _place(prev) == _place(shot):
        return None
    if not prev.get("location") or not shot.get("location"):
        return None  # a hand-cut clip names no place: nothing to compare
    landing = sizes.get(shot["label"]) or {}
    if landing.get("moves") and landing.get("size") == "wide":
        return None  # the new place opens on a moving establishing shot: it lands the viewer on its own
    return (f"{prev['label']} → {shot['label']}: {prev['location']} → {shot['location']} on a {into}, "
            "nothing carries the viewer across (no bridge, dip or moving wide)")


def _time_problem(prev: dict[str, Any], shot: dict[str, Any], into: str) -> str | None:
    if prev.get("bridge") or shot.get("bridge") or into in JOINERS:
        return None
    then, now = time_of_day(prev), time_of_day(shot)
    if not then or not now or then == now:
        return None
    return f"{prev['label']} → {shot['label']}: {then} → {now} on a {into}; a jump in time wants a bridge or a dip"


def _jump_problem(prev: dict[str, Any], shot: dict[str, Any], sizes: dict[str, Any]) -> str | None:
    a, b = sizes.get(prev["label"]), sizes.get(shot["label"])
    if not a or not b or prev.get("scene") != shot.get("scene") or a["moves"] or b["moves"]:
        return None
    if a["size"] != b["size"] or sorted(prev.get("cast") or []) != sorted(shot.get("cast") or []):
        return None
    if not prev.get("cast"):
        return None
    return f"{prev['label']} → {shot['label']}: jump cut, the same people at the same size with no move"


def join_problems(plan: dict[str, Any], transitions: dict[str, str],
                  speeds: dict[str, float] | None = None) -> list[str]:
    """Join warnings for the cut, as sentences, in clock order. `transitions` is label → the cut into it
    (shot_matrix.transitions); `speeds` label → how fast the cut plays the shot (1.0 when absent)."""
    shots, speeds = live(plan), speeds or {}
    sizes = {s["label"]: read_shot(s) for s in shots}
    problems: list[str] = []
    for prev, shot in zip([None, *shots], shots):
        found = [_bridge_problem(shot, speeds.get(shot["label"], 1.0))]
        if prev is not None:
            into = transitions.get(shot["label"]) or "cut"
            found += [_place_problem(prev, shot, into, sizes), _time_problem(prev, shot, into),
                      _jump_problem(prev, shot, sizes)]
        problems += [p for p in found if p]
    return problems


def warn(plan: dict[str, Any], stream: TextIO = sys.stderr) -> list[str]:
    """Print the join warnings before the board is drawn; drawing goes on regardless."""
    from . import shot_matrix

    speeds = {s["label"]: shot_matrix.speed(s, plan) for s in live(plan)}
    problems = join_problems(plan, shot_matrix.transitions(plan), speeds)
    for problem in problems:
        print(f"  join: {problem}", file=stream)
    return problems
