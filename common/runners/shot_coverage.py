"""Coverage of a cut: shot sizes and camera moves read off each shot's body.

A film of close-ups and slow push-ins reads as no cutting and no camera at all.
`coverage_problems(plan)` reads the "Shot [0-4s] - <size>, <angle>, <lens>, <move>."
phrase every planned shot body opens with (or, for a body that starts on its own
frame, the sentences that say what the camera does) and reports, as sentences:

- a scene with no wide, aerial or overhead shot;
- three or more close-ups in a row, in clock order;
- three or more shots in a row with no real camera move;
- real moves under a third of the shots.

A real move is a crane, dolly, track, orbit, FPV, drone, whip, sweep or arc; a
push-in of any speed, a pan, a tilt, a zoom or a locked-off frame is not.
Clip-only shots and cut shots are skipped; a bridge is a flight between scenes,
so it counts as a moving shot of no scene. These are warnings, not failures.
"""

from __future__ import annotations

import re
import sys
from typing import Any, TextIO

RUN = 3  # this many close-ups, or static shots, in a row is a problem
MOVE_SHARE = 1 / 3

_PHRASE = re.compile(r"Shot \[[^\]]*\]\s*[-–—]\s*([^.]*)")
_REAL = re.compile(r"crane|dolly|track|orbit|fpv|drone|whip|sweep|\barc\b|circl|pull\w* back|chase|swoop|"
                   r"\bfl(y|ies|ying)\b|camera \w*\s?(rises|sinks|dives|climbs)", re.I)
_PUSH = re.compile(r"push-?in|dolly in|locked-off|static", re.I)
_FLIGHT = re.compile(r"crane|orbit|fpv|drone|track", re.I)
_CAMERA =re.compile(r"[^.:]*\b(camera|drone|crane|fpv|dolly)\b[^.]*", re.I)
_REVEAL = re.compile(r"drone|aerial|high above|straight down|overhead|reveal", re.I)
_CLOSE = re.compile(r"^(extreme |medium )?close|^insert|^macro")
_WIDE = re.compile(r"^(extreme |very )?wide|aerial|overhead|straight down|top-down|bird")


def _size(field: str) -> str:
    field = field.strip().lower()
    if _CLOSE.search(field):
        return "close"
    return "wide" if _WIDE.search(field) else "medium"


def _move(text: str) -> bool:
    """A real move names one; "dolly in" is a push-in under another name unless a flight goes with it."""
    if not _REAL.search(text):
        return False
    return not _PUSH.search(text) or bool(_FLIGHT.search(text))


def read_shot(shot: dict[str, Any]) -> dict[str, Any] | None:
    """{label, scene, size: close|medium|wide|None, moves}; None for a shot the cut takes as it is."""
    body = (shot.get("body") or shot.get("prompt") or "").strip()
    if shot.get("cut") or not body:
        return None
    label, scene = shot.get("label") or str(shot.get("index")), shot.get("scene")
    if shot.get("bridge") and not scene:
        return {"label": label, "scene": None, "size": None, "moves": True}
    phrase = _PHRASE.search(body)
    if phrase:
        fields = phrase.group(1).split(",")
        return {"label": label, "scene": scene, "size": _size(fields[0]), "moves": _move(fields[-1])}
    camera = " ".join(m.group(0) for m in _CAMERA.finditer(body))
    size = "wide" if _REVEAL.search(camera) else ("close" if "close-up" in camera.lower() else None)
    return {"label": label, "scene": scene, "size": size, "moves": _move(camera)}


def move_phrase(body: str) -> str:
    """What the camera does, as written: the shot phrase's last field, else the body's camera sentences."""
    phrase = _PHRASE.search(body or "")
    if phrase:
        return phrase.group(1).split(",")[-1].strip()
    return " ".join(m.group(0).strip() for m in _CAMERA.finditer(body or ""))[:120]


def _in_order(plan: dict[str, Any]) -> list[dict[str, Any]]:
    shots = list(plan.get("shots") or [])
    if all(s.get("clock_at") is not None for s in shots):
        shots.sort(key=lambda s: float(s["clock_at"]))
    return [r for r in map(read_shot, shots) if r]


def _runs(read: list[dict[str, Any]], hit, what: str) -> list[str]:
    problems, run = [], []
    for shot in [*read, None]:
        if shot is not None and hit(shot):
            run.append(shot["label"])
            continue
        if len(run) >= RUN:
            problems.append(f"{len(run)} {what} in a row: {run[0]}..{run[-1]}")
        run = []
    return problems


def _sceneless_wides(read: list[dict[str, Any]]) -> list[str]:
    scenes: dict[Any, list[dict[str, Any]]] = {}
    for shot in read:
        if shot["scene"] is not None:
            scenes.setdefault(shot["scene"], []).append(shot)
    return [f"scene {scene}: no wide, aerial or overhead shot ({shots[0]['label']}..{shots[-1]['label']})"
            for scene, shots in scenes.items() if not any(s["size"] == "wide" for s in shots)]


def coverage_problems(plan: dict[str, Any]) -> list[str]:
    """Coverage warnings for a planned cut, as sentences; empty when the cut has wides and a moving camera."""
    read = _in_order(plan)
    if not read:
        return []
    problems = _sceneless_wides(read)
    problems += _runs(read, lambda s: s["size"] == "close", "close-ups")
    problems += _runs(read, lambda s: not s["moves"], "shots without a real camera move")
    moving = sum(s["moves"] for s in read)
    if moving < MOVE_SHARE * len(read):
        problems.append(f"real camera moves in {moving} of {len(read)} shots, under a third "
                        "(a push-in, pan, tilt or zoom is not a move)")
    return problems


def warn(plan: dict[str, Any], stream: TextIO = sys.stderr) -> list[str]:
    """Print the coverage warnings before the board is drawn; drawing goes on regardless."""
    problems = coverage_problems(plan)
    for problem in problems:
        print(f"  coverage: {problem}", file=stream)
    if problems:
        print(f"Coverage: {len(problems)} warning(s); fix the plan before drawing frames for it.", file=stream)
    return problems
