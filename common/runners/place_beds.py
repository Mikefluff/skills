"""Ambience beds that follow the cut: each place's room tone laid over the run of shots in that place.

A film's sound plan places its beds on the clock it was written for. Every shot inserted, trimmed or moved
since then slides the picture under them, and a bed left where it was plays the last room over the next
place (in the Tanya short, by 2 to 6 seconds after a few bridges went in). `follow_cut(sound, plan)` lays
the beds again from the cut as it is: one placement per run of shots in one location, the bed being the
loop source the plan had playing over most of that location's runs across the whole film (a short run,
slid under the wrong room by the edits, would vote for the wrong one), at the gain it had there. Each bed
after the first starts `PRELAP` seconds before its picture and fades in under the outgoing room: the next
place is heard a beat before it is seen, a J-cut, and the two rooms cross instead of switching on the frame.

A bed's file is as long as it was made (30 s) and the mixer does not loop it, so a run longer than that is
laid as consecutive takes of the bed that overlap by `OVERLAP` and cross-fade: one 59 s placement went silent
after 30 s, and wherever the score paused the film fell to digital silence.

Only beds with a length are relaid; a short burst of a bed (no length) is a cue of its own and stays.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

PRELAP = 0.5  # seconds the next place's bed leads its picture
TAIL = 0.4  # seconds a bed rings on past its run, under the next one's fade-in
OVERLAP = 1.0  # seconds consecutive takes of one bed overlap and cross-fade
_BED_SECONDS = 30.0  # a bed's length when its source does not say
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


def _lay(bed: tuple[str, float], a: float, b: float, first: bool, seconds: float) -> list[dict[str, Any]]:
    """One bed over a..b: leading its picture by PRELAP (the film's first starts on its picture), ringing on TAIL,
    as takes of at most `seconds` (the bed's file) overlapping by OVERLAP."""
    at, end, laid = (a if first else max(0.0, a - PRELAP)), b + TAIL, []
    while at < end - 0.05:
        length = min(seconds, end - at)
        fade_in = (0.6 if first else PRELAP) if not laid else OVERLAP
        laid.append({"source": bed[0], "at": round(at, 3), "length": round(length, 3), "gain_db": bed[1],
                     "duck": False, "fade_in": fade_in, "fade_out": OVERLAP if at + length < end - 0.05 else TAIL})
        at += length - OVERLAP if at + length < end - 0.05 else length
    return laid


def follow_cut(sound: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """`sound` with its beds laid again over the cut's place runs (see the module doc); changed in place."""
    placements = sound.get("placements") or []
    beds = _beds(sound, placements)
    if not beds:
        return sound
    cut = runs(plan)
    by_place = _beds_by_place(beds, cut)
    seconds = {src["id"]: float(src.get("duration_seconds") or _BED_SECONDS) for src in sound.get("sources") or []}
    laid = [take for n, (place, a, b) in enumerate(cut) if place in by_place
            for take in _lay(by_place[place], a, b, n == 0, seconds.get(by_place[place][0], _BED_SECONDS))]
    sound["placements"] = [p for p in placements if p not in beds] + laid
    return sound
