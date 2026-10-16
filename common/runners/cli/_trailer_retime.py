"""Conform a cut to its lines — a speaking shot is as long as its line, rounded to the beat.

An edit planned on the beat grid before anyone spoke gives each line a guess of
a shot; once the lines exist (the animatic's takes), most of the guesses are
wrong, and a line that outruns its shot lands on the next speaker. Here every
speaking shot is lengthened to line_at + the line + a breath, rounded up to a
whole number of beats of its act's tempo; everything after it moves later by
the difference: shots, title cards, sound placements, and the length of every
music section of an act that grew (the cue is generated again at its new length).
A speaking shot is cut shorter too when its line is shorter than the guess, down
to two beats at least, so the trailer is as long as its lines and no longer.
"""

from __future__ import annotations

import math
import re
from typing import Any

_BREATH = 0.3


def _act_of(plan: dict[str, Any]) -> dict[str, str]:
    """shot label → act name, from the acts' from/to labels."""
    order = [s["label"] for s in sorted(plan["shots"], key=lambda s: int(s["index"]))]
    out = {}
    for act in (plan.get("trailer") or {}).get("acts") or []:
        if act.get("from") in order and act.get("to") in order:
            for label in order[order.index(act["from"]): order.index(act["to"]) + 1]:
                out.setdefault(label, act["name"])  # a shot shared by two acts belongs to the first
    return out


def act_bpm(plan: dict[str, Any]) -> dict[str, float]:
    """act name → tempo, read from the music cue whose section carries the act's name ("104 bpm" in its styles)."""
    out = {}
    for src in (plan.get("sound") or {}).get("sources") or []:
        cp = src.get("composition_plan") or {}
        styles = " ".join(cp.get("positive_global_styles") or [])
        found = re.search(r"(\d{2,3})\s*bpm", styles)
        for sec in cp.get("sections") or []:
            if found:
                out[sec["section_name"]] = float(found.group(1))
    return out


def new_lengths(plan: dict[str, Any], line_seconds: dict[str, float]) -> dict[str, float]:
    """shot label → its conformed length (only the shots whose length changes)."""
    acts, bpm = _act_of(plan), act_bpm(plan)
    out = {}
    for shot in plan["shots"]:
        said = line_seconds.get(shot["label"])
        if said is None:
            continue
        beat = 60.0 / bpm.get(acts.get(shot["label"], ""), 104.0)
        need = float(shot.get("line_at") or 0.3) + said + _BREATH
        beats = max(2, math.ceil(need / beat - 1e-6))
        length = round(beats * beat, 2)
        if abs(length - float(shot["trim_seconds"])) > 0.01:
            out[shot["label"]] = length
    return out


def _moved(t: float, shifts: list[tuple[float, float, str]]) -> float:
    """A time after a changed shot moves by its change; a time inside a cut-off tail lands on the new end."""
    out = t
    for point, d, _ in shifts:
        if t >= point - 1e-6:
            out += d
        elif d < 0 and t > point + d:
            out += point + d - t
    return out


def retime(plan: dict[str, Any], lengths: dict[str, float]) -> list[tuple[float, float, str]]:
    """Apply new shot lengths in place; returns (clock point, added seconds, shot label) per change, in order."""
    shifts = []
    for shot in sorted(plan["shots"], key=lambda s: int(s["index"])):
        if shot["label"] in lengths:
            delta = lengths[shot["label"]] - float(shot["trim_seconds"])
            end = float(shot["clock_at"]) + float(shot["trim_seconds"])
            shifts.append((end, round(delta, 3), shot["label"]))
            shot["trim_seconds"] = lengths[shot["label"]]
            kwargs = shot.setdefault("kwargs", {})
            need = float(shot.get("trim_start") or 0) + shot["trim_seconds"] + 0.5
            kwargs["duration_seconds"] = max(int(kwargs.get("duration_seconds") or 4), math.ceil(need))
    moved = lambda t: _moved(t, shifts)  # noqa: E731
    for shot in plan["shots"]:
        shot["clock_at"] = round(moved(float(shot["clock_at"])), 3)
    for card in (plan.get("trailer") or {}).get("title_cards") or []:
        card["clock_at"] = round(moved(float(card["clock_at"])), 3)
    _sound(plan, shifts, moved)
    return shifts


def _sound(plan: dict[str, Any], shifts: list[tuple[float, float]], moved) -> None:
    sound = plan.get("sound")
    if not sound:
        return
    for pl in sound.get("placements") or []:
        start = float(pl["at"])
        if pl.get("length") is not None:
            end = moved(start + float(pl["length"]) - 1e-6)
            pl["length"] = round(end - moved(start) + 1e-6, 3)
        pl["at"] = round(moved(start), 3)
    sound["total_seconds"] = round(moved(float(sound["total_seconds"]) - 1e-6) + 1e-6, 2)
    _sections(plan, shifts)


def _sections(plan: dict[str, Any], shifts: list[tuple[float, float, str]]) -> None:
    """Every music section named after an act grows by what that act's shots grew."""
    acts, grew = _act_of(plan), {}
    for _, delta, label in shifts:
        grew[acts.get(label, "")] = grew.get(acts.get(label, ""), 0.0) + delta
    for src in plan["sound"].get("sources") or []:
        for sec in (src.get("composition_plan") or {}).get("sections") or []:
            if grew.get(sec["section_name"]):
                sec["duration_ms"] = int(round(sec["duration_ms"] + grew[sec["section_name"]] * 1000))
