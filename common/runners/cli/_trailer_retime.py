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
    live = [s for s in plan["shots"] if not s.get("cut")]
    # the cut's order once it has a clock: a restructure moves shots without renumbering them
    key = (lambda s: float(s["clock_at"])) if all("clock_at" in s for s in live) else (lambda s: int(s["index"]))
    order = [s["label"] for s in sorted(live, key=key)]
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
            # a section's own tempo ("112 bpm" in its local styles) beats the cue's
            local = re.search(r"(\d{2,3})\s*bpm", " ".join(sec.get("positive_local_styles") or []))
            if local or found:
                out[sec["section_name"]] = float((local or found).group(1))
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
    for shot in sorted(plan["shots"], key=lambda s: float(s.get("clock_at") or 0)):
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


# ── the build: a peak whose cuts get shorter, ending on a strobe of the one face ─────────────────────────────


def _busiest(clip: Any, seconds: float, speed: float = 1.0) -> float:
    """Where in `clip` the `seconds` of cut (played at `speed`) see the most change from frame to frame."""
    import subprocess

    res = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-an", "-vf",
                          "scale=160:-2,select='gte(scene,0)',metadata=print:file=-", "-f", "null", "-"],
                         capture_output=True, text=True)
    times, scores = [], []
    for row in res.stdout.splitlines():
        if "pts_time:" in row:
            times.append(float(row.split("pts_time:")[1].split()[0]))
        elif "scene_score=" in row:
            scores.append(float(row.split("=")[1]))
    span = seconds * speed
    if not times or times[-1] <= span:
        return 0.0
    best, at = -1.0, 0.0
    for i, t in enumerate(times):
        if t + span > times[-1]:
            break
        total = sum(sc for tt, sc in zip(times[i:], scores[i:]) if tt < t + span)
        if total > best:
            best, at = total, t
    return round(at, 3)


def _half_beats(n: int, left: int) -> list[int]:
    """Half-beat counts for n shots falling from 8 (four beats) to 2 (one beat), summing to `left`."""
    raw = [8 - 6 * i / max(1, n - 1) for i in range(n)]
    want = [max(2, round(r * left / sum(raw))) for r in raw]
    i = 0
    while sum(want) != left:
        j = i % n
        if sum(want) > left and want[j] > 2:
            want[j] -= 1
        elif sum(want) < left:
            want[j] += 1
        i += 1
        if i > 1000:
            break
    return want


def _build_shots(plan: dict[str, Any], act: str, until: float) -> list[dict[str, Any]]:
    """The act's shots before `until` in clock order; earlier strobes (shots and sounds) cleared."""
    acts = _act_of(plan)
    live = sorted((s for s in plan["shots"] if not s.get("cut") and not s.get("strobe")),
                  key=lambda s: float(s["clock_at"]))
    shots = [s for s in live if acts.get(s["label"]) == act and float(s["clock_at"]) < until - 1e-3]
    plan["shots"] = [s for s in plan["shots"] if not s.get("strobe")]
    if plan.get("sound"):
        plan["sound"]["placements"] = [p for p in plan["sound"]["placements"] if not p.get("strobe")]
    return shots


def _recut(build: dict[str, Any], shots: list[dict[str, Any]], want: list[int], at: float) -> float:
    """Shots laid back to back at their new lengths, each shortened one on its busiest window; returns the end."""
    beat, clips, speed = build["beat"], build["clips"], build["speed"]
    for shot, h in zip(shots, sorted(want, reverse=True)):
        seconds = round(h * beat / 2, 3)
        clip = clips.get(shot["label"])
        if clip and seconds < float(shot["trim_seconds"]) - 0.05 and not shot.get("dialogue"):
            shot["trim_start"] = _busiest(clip, seconds, speed(shot, build["plan"]) if speed else 1.0)
        shot["clock_at"], shot["trim_seconds"] = round(at, 3), seconds
        at += seconds
    return at


def _carry_sounds(plan: dict[str, Any], shots: list[dict[str, Any]],
                  old: dict[str, tuple[float, float]]) -> None:
    """A sound laid on a recut shot keeps its place in it."""
    for p in (plan.get("sound") or {}).get("placements") or []:
        a = float(p["at"])
        for label, (o, length) in old.items():
            if o <= a < o + length:
                new = next(s for s in shots if s["label"] == label)
                p["at"] = round(float(new["clock_at"]) + min(a - o, float(new["trim_seconds"]) - 0.1), 3)
                break


def _strobe(build: dict[str, Any], flashes: list[dict[str, Any]], at: float) -> list[str]:
    """Half-beat flashes of faces from `at`, a scanner beep on each when the plan has one; returns their labels."""
    plan, beat, clips = build["plan"], build["beat"], build["clips"]
    by = {s["label"]: s for s in plan["shots"]}
    nxt = max(int(s["index"]) for s in plan["shots"]) + 1
    beep = any(src.get("id") == "scan_beep" for src in (plan.get("sound") or {}).get("sources") or [])
    added = []
    for k, f in enumerate(flashes):
        src = by[f["from"]]
        label = f"s{k + 1:02d}"
        clip = clips.get(f["from"])
        plan["shots"].append({"index": nxt + k, "label": label, "strobe": True, "location": src.get("location"),
                              "cast": src.get("cast", []), "dialogue": [], "body": "Shot - close. The face.",
                              "clip": str(clip.relative_to(plan["output_dir"])) if clip else src.get("clip"),
                              "trim_start": float(f["at"]), "trim_seconds": round(beat / 2, 3),
                              "clock_at": round(at, 3)})
        if beep:
            # every face in the strobe is matched: the scanner's beep on each flash, the build's clock
            plan["sound"]["placements"].append({"source": "scan_beep", "at": round(at, 3), "strobe": True,
                                                "gain_db": -6.0 + 1.0 * k, "fade_in": 0.0, "fade_out": 0.02})
        at += beat / 2
        added.append(label)
    return added


def accelerate(plan: dict[str, Any], act: str, until: float, strobe: list[dict[str, Any]],
               *media: Any) -> list[str]:
    """The act's shots before `until` recut so each is shorter than the last, then a strobe of faces into it.

    The SAME peak alternated 1.6 s and 1.07 s cuts for thirteen seconds: an even pulse, no build. Here the act's
    span stays (the score was composed to it), shot lengths fall from four beats to one in half beats, and the
    last beats are a strobe: half-beat flashes of `strobe` ({"from": label, "at": seconds into its clip}), the
    face every character shares, back to back. `media` is optionally (clips, speed): label → rendered clip, and
    speed(shot, plan). Each shortened shot plays its clip's busiest window; the sounds laid on a shot keep their
    place in it. Returns the labels of the strobe shots added."""
    clips, speed = (tuple(media) + (None, None))[:2]
    build = {"plan": plan, "beat": 60.0 / act_bpm(plan).get(act, 104.0), "clips": clips or {}, "speed": speed}
    shots = _build_shots(plan, act, until)
    if not shots:
        return []
    start = float(shots[0]["clock_at"])
    halves = round((until - start) / (build["beat"] / 2))
    flashes = min(len(strobe), max(0, halves - 2 * len(shots)))
    old = {s["label"]: (float(s["clock_at"]), float(s["trim_seconds"])) for s in shots}
    at = _recut(build, shots, _half_beats(len(shots), halves - flashes), start)
    _carry_sounds(plan, shots, old)
    added = _strobe(build, strobe[:flashes], at)
    last = max((s for s in plan["shots"] if not s.get("cut") and float(s["clock_at"]) < until),
               key=lambda s: float(s["clock_at"]))
    last["trim_seconds"] = round(until - float(last["clock_at"]), 3)  # the beat grid's rounding, closed
    return added


def shift(plan: dict[str, Any], point: float, delta: float) -> None:
    """Everything at or after `point` on the clock moves by `delta` (shots, cards, sound), the music's own
    sections untouched: a shot put in or taken out moves the film, it does not recompose the score."""
    shifts = [(point, delta, "")]
    moved = lambda t: _moved(t, shifts)  # noqa: E731
    for shot in plan["shots"]:
        shot["clock_at"] = round(moved(float(shot["clock_at"])), 3)
    for card in (plan.get("trailer") or {}).get("title_cards") or []:
        card["clock_at"] = round(moved(float(card["clock_at"])), 3)
    sound = plan.get("sound") or {}
    for pl in sound.get("placements") or []:
        start = float(pl["at"])
        if pl.get("length") is not None and start < point < start + float(pl["length"]):
            pl["length"] = round(float(pl["length"]) + delta, 3)  # a bed or a cue running across grows with it
        pl["at"] = round(moved(start), 3)
    if sound.get("total_seconds"):
        sound["total_seconds"] = round(float(sound["total_seconds"]) + delta, 3)


def insert(plan: dict[str, Any], shot: dict[str, Any], at: float) -> None:
    """Put a shot into the cut at clock `at`, everything from there on moving later by its length."""
    # storyboard frames name their shot by index: carry each to its shot's new number
    frames = (plan.get("board") or {}).get("frames") or []
    owner = {int(s["index"]): s["label"] for s in plan["shots"] if "index" in s}
    by_frame = [(f, owner.get(int(f.get("shot", 0)))) for f in frames]
    shift(plan, at, float(shot["trim_seconds"]))
    shot["clock_at"] = round(at, 3)
    plan["shots"].append(shot)
    plan["shots"].sort(key=lambda s: float(s["clock_at"]))
    for n, s in enumerate(plan["shots"], 1):
        s["index"] = n
    index = {s["label"]: s["index"] for s in plan["shots"]}
    for f, label in by_frame:
        if label in index:
            f["shot"] = index[label]

