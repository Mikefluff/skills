"""A score's sections that follow the cut: each section as long as the stretch of film it now plays under.

A music source is a composition plan whose sections were sized for the cut it was written for, and its take is
fitted to them in the mix (cli/_reel_sound._fitted stretches each section of the take to its length). The
placement grows with the cut (reel_insert moves and lengthens it) but the sections did not: in the Tanya short
the caper score's two sections still added up to 183 s under a 285 s placement, and the whole catastrophe
(the cake's rise, the court, the fireworks) played with no music at all.

`follow_cut(sound, plan)` sizes the sections again from the placement: a section named after one of the
plan's acts (trailer.acts, "from" and "to" shot labels) ends where the next section's act begins, the first
starts where the placement's take starts (its `at` less its `offset`) and the last ends with the placement.
A score whose sections are not all acts, or whose acts are out of order, is scaled as a whole to its
placement instead. Only lengths change; the take is never bought again for it.
"""

from __future__ import annotations

from typing import Any


def _clock(plan: dict[str, Any]) -> dict[str, float]:
    return {s["label"]: float(s["clock_at"]) for s in plan.get("shots") or [] if not s.get("cut")}


def _act_starts(plan: dict[str, Any], names: list[str]) -> list[float] | None:
    """Where each named act begins on the clock, or None when one is missing."""
    acts = {a["name"]: a for a in (plan.get("trailer") or {}).get("acts") or []}
    clock = _clock(plan)
    starts = [clock.get((acts.get(n) or {}).get("from", "")) for n in names]
    return None if any(s is None for s in starts) else starts


def _lengths(starts: list[float] | None, begin: float, end: float, made: list[float]) -> list[float]:
    """Each section's seconds: from act start to act start, or `made` scaled to begin..end."""
    bounds = [begin, *(starts or [None])[1:], end]
    if starts and all(a < b for a, b in zip(bounds, bounds[1:])):
        return [b - a for a, b in zip(bounds, bounds[1:])]
    total = sum(made) or 1.0
    return [m * (end - begin) / total for m in made]


def _fit(src: dict[str, Any], p: dict[str, Any], plan: dict[str, Any]) -> None:
    """One music source's sections sized to the film under its placement `p`."""
    sections = src["composition_plan"]["sections"]
    begin = float(p["at"]) - float(p.get("offset") or 0)
    end = float(p["at"]) + float(p["length"])
    made = [float(s["duration_ms"]) / 1000 for s in sections]
    lengths = _lengths(_act_starts(plan, [s["section_name"] for s in sections]), begin, end, made)
    for section, seconds in zip(sections, lengths):
        section["duration_ms"] = int(round(seconds * 1000))


def follow_cut(sound: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """`sound` with every music source's sections sized to the film under its placement; changed in place."""
    placed = {p["source"]: p for p in sound.get("placements") or [] if p.get("length")}
    for src in sound.get("sources") or []:
        has_sections = bool((src.get("composition_plan") or {}).get("sections"))
        if src.get("kind") == "music" and has_sections and src["id"] in placed:
            _fit(src, placed[src["id"]], plan)
    return sound
