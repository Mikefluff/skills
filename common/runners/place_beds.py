"""Ambience beds that follow the cut: each place's room tone laid over the run of shots in that place.

A film's sound plan places its beds on the clock it was written for. Every shot inserted, trimmed or moved
since then slides the picture under them, and a bed left where it was plays the last room over the next
place (in the Tanya short, by 2 to 6 seconds after a few bridges went in). `follow_cut(sound, plan)` lays
the beds again from the cut as it is: one placement per run of shots in one location, the bed being the
loop source the plan had playing over most of that location's runs across the whole film (a short run,
slid under the wrong room by the edits, would vote for the wrong one), at the gain it had there. Each bed
after the first starts `PRELAP` seconds before its picture and fades in under the outgoing room: the next
place is heard a beat before it is seen, a J-cut, and the two rooms cross instead of switching on the frame.

Only beds with a length are relaid; a short burst of a bed (no length) is a cue of its own and stays.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

PRELAP = 0.5  # seconds the next place's bed leads its picture
TAIL = 0.4  # seconds a bed rings on past its run, under the next one's fade-in
_SAME_RUN = 2.0  # a gap shorter than this (a title card) keeps one run


def runs(plan: dict[str, Any]) -> list[tuple[str, float, float]]:
    """(location, from, to) for every run of consecutive shots in one place, on the cut's clock."""
    out: list[list[Any]] = []
    for shot in sorted((s for s in plan["shots"] if not s.get("cut")), key=lambda s: float(s["clock_at"])):
        start, end = float(shot["clock_at"]), float(shot["clock_at"]) + float(shot["trim_seconds"])
        place = shot.get("location")
        if not place:
            continue
        if out and out[-1][0] == place and start - out[-1][2] < _SAME_RUN:
            out[-1][2] = end
        else:
            out.append([place, start, end])
    return [(p, a, b) for p, a, b in out]


def _overlap(p: dict[str, Any], a: float, b: float) -> float:
    at = float(p["at"])
    return max(0.0, min(b, at + float(p["length"])) - max(a, at))


def _beds_by_place(beds: list[dict[str, Any]], cut: list[tuple[str, float, float]]) -> dict[str, tuple[str, float]]:
    """location → (source, gain) of the bed the plan played over most of that location's runs in the film."""
    heard: dict[str, Counter] = {}
    gains: dict[str, Counter] = {}
    for place, a, b in cut:
        for p in beds:
            if (o := _overlap(p, a, b)) > 0:
                heard.setdefault(place, Counter())[p["source"]] += o
                gains.setdefault(p["source"], Counter())[float(p.get("gain_db") or 0)] += o
    chosen = {place: votes.most_common(1)[0][0] for place, votes in heard.items()}
    return {place: (src, gains[src].most_common(1)[0][0]) for place, src in chosen.items()}


def _beds(sound: dict[str, Any], placements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The placements of a loop source that run for a length: the beds to lay again."""
    loops = {s["id"] for s in sound.get("sources") or [] if s.get("loop")}
    return [p for p in placements if p.get("source") in loops and p.get("length")]


def _lay(bed: tuple[str, float], a: float, b: float, first: bool) -> dict[str, Any]:
    """One bed over a..b: leading its picture by PRELAP (the film's first starts on its picture), ringing on TAIL."""
    at = a if first else max(0.0, a - PRELAP)
    return {"source": bed[0], "at": round(at, 3), "length": round(b + TAIL - at, 3), "gain_db": bed[1],
            "duck": False, "fade_in": 0.6 if first else PRELAP, "fade_out": TAIL}


def follow_cut(sound: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """`sound` with its beds laid again over the cut's place runs (see the module doc); changed in place."""
    placements = sound.get("placements") or []
    beds = _beds(sound, placements)
    if not beds:
        return sound
    cut = runs(plan)
    by_place = _beds_by_place(beds, cut)
    laid = [_lay(by_place[place], a, b, first=n == 0) for n, (place, a, b) in enumerate(cut) if place in by_place]
    sound["placements"] = [p for p in placements if p not in beds] + laid
    return sound
