"""Clay-render previs for a voiced film — the spec, its checks, and its camera moves.

Seedance 2.5 follows a reference video's camera far more faithfully than any
sentence: told "slow push-in" over a still, it breathes; given a grey 3D
blocking clip as @Video1, it flies the same path, at the same speed, with the
same changes of shot size, and fires the lights when the blocks light up. So
the camera of a film is designed here, as data, and rendered by Blender
(`blender/previs_scene.py`) before any video is paid for.

The spec lives in the plan:

  "previs": {
    "sets": {"arena": [ {"kind": "box", "at": [0, 11, -0.05], "size": [14, 30, 0.1], "tone": "dark"},
                        {"kind": "truss", "y": [3, 24], "step": 5, "width": 9, "height": 6},
                        {"kind": "crowd", "at": [0, 31], "size": [13, 7]},
                        {"kind": "box", "id": "mh1", "at": [-2.5, 5, 0.35], "size": [0.5, 0.5, 0.7]} ]},
    "shots": {"s03": {"set": "arena", "lens": 18, "shake": 0.02,
                      "camera": [{"t": 0, "pos": [0.4, -1.5, 1.8], "look": [0, 6, 1.3]},
                                 {"move": "orbit", "t": [1, 3], "center": [0, 0, 1.6], "radius": 2.5,
                                  "deg": [200, 320], "height": 1.6},
                                 {"t": 5, "pos": [0, 22, 15], "look": [0, 25.5, 0], "lens": 24}],
                      "hero": [{"t": 0, "pos": [0, -0.15], "facing": 0}, {"t": 4, "pos": [0, 3], "facing": 180}],
                      "fire": [{"t": 0.3, "id": "mh1"}]}}
  }

Coordinates are metres: x to the hero's right, y forward from his decks toward
the crowd, z up. Times are seconds on the shot's own clip clock (0 to its
generation length). A shot may add its own "extra" props — the foreground that
passes the lens in that shot only. Camera keys may carry "roll" (degrees, a
dutch angle or a spin) and "ease": ease, linear or snap (hold, then jump).
Tones: light, dark, hero. `kind` is box, cylinder, truss
(gates of towers and a span along y) or crowd (a grid of standing figures).
The hero figure — body, head, hat brim — appears in a shot that has "hero"
keys and nowhere else; a block with an `id` can be fired (lit) at a time.
"""

from __future__ import annotations

import math
from typing import Any

KINDS = {"box", "cylinder", "truss", "crowd"}
TONES = {"light", "dark", "hero"}


class PrevisError(ValueError):
    pass


def orbit(move: dict[str, Any]) -> list[dict[str, Any]]:
    """An orbit move — {center, radius, deg, height, t[, steps]} — as camera keys
    looking at its center. 0° is behind the subject (−y)."""
    center, radius, height, steps = move["center"], move["radius"], move["height"], move.get("steps", 6)
    (t0, t1), (d0, d1) = move["t"], move["deg"]
    keys = []
    for n in range(steps + 1):
        f = n / steps
        a = math.radians(d0 + (d1 - d0) * f - 90)
        keys.append({
            "t": round(t0 + (t1 - t0) * f, 3),
            "pos": [round(center[0] + radius * math.cos(a), 3), round(center[1] + radius * math.sin(a), 3), height],
            "look": list(center),
        })
    return keys


def camera_keys(shot: dict[str, Any]) -> list[dict[str, Any]]:
    """The shot's camera as plain keys {t, pos, look[, lens, roll, ease]}, moves expanded, in time order."""
    keys: list[dict[str, Any]] = []
    for key in shot.get("camera") or []:
        if key.get("move") == "orbit":
            keys += orbit(key)
        else:
            keys.append({k: key[k] for k in ("t", "pos", "look", "lens", "roll", "ease") if k in key})
    return sorted(keys, key=lambda k: k["t"])


def _prop_problems(sets: dict[str, list[dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    for name, props in sets.items():
        for n, prop in enumerate(props):
            if prop.get("kind") not in KINDS:
                problems.append(f"set {name} prop {n}: kind must be one of {sorted(KINDS)}")
            if prop.get("tone", "light") not in TONES:
                problems.append(f"set {name} prop {n}: tone must be one of {sorted(TONES)}")
    return problems


def _shot_problems(label: str, shot: dict[str, Any], sets: dict[str, list[dict[str, Any]]],
                   duration: float) -> list[str]:
    problems: list[str] = []
    if shot.get("set") not in sets:
        problems.append(f"{label}: unknown set {shot.get('set')!r}")
    keys = camera_keys(shot)
    if len(keys) < 2:
        problems.append(f"{label}: the camera needs at least two keys")
    extra = shot.get("extra") or []
    problems += [f"{label}: {problem}" for problem in _prop_problems({"extra": extra})]
    ids = {p.get("id") for p in [*sets.get(shot.get("set"), []), *extra] if p.get("id")}
    return problems + _timed_problems(label, shot, keys, ids, duration)


def _timed_problems(label: str, shot: dict[str, Any], keys: list[dict[str, Any]], ids: set[Any],
                    duration: float) -> list[str]:
    """Keys outside the generation, and cues that fire nothing."""
    timed = [*keys, *(shot.get("hero") or []), *(shot.get("fire") or [])]
    late = [f"{label}: time {item.get('t')} is outside 0-{duration:g}s"
            for item in timed if not 0 <= float(item.get("t", 0)) <= duration + 1e-6]
    unknown = [f"{label}: fire refers to unknown id {cue.get('id')!r}"
               for cue in shot.get("fire") or [] if cue.get("id") not in ids]
    return late + unknown


def validate(previs: dict[str, Any], durations: dict[str, float]) -> list[str]:
    """Problems with the spec, as sentences; empty when it can be rendered.

    `durations` maps shot label → generation length; a key outside it would be
    rendered into frames the shot never has.
    """
    sets = previs.get("sets") or {}
    problems = _prop_problems(sets)
    for label, shot in (previs.get("shots") or {}).items():
        if label not in durations:
            problems.append(f"previs shot {label} is not a shot in the plan")
            continue
        problems += _shot_problems(label, shot, sets, durations[label])
    return problems
