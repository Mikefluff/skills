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

An ensemble film gives a shot "actors" instead: each
  {"id": "tanya", "height": 1.2, "color": [0.95, 0.35, 0.65], "hair": "big", "hair_color": [...],
   "keys": [{"t": 0, "pos": [x, y(, z)], "facing": 0, "pose": "stand"}]}
is a troll-proportioned figure (big head, ears, nose, eyes on the side it faces) in its own colour, so who
is where reads in the clay. Poses: POSES below. Any prop may move on "anim" keys
{"t", "at": [x, y, z], "scale": [sx, sy, sz], "rot": [deg x, y, z]} — a cake that rises, a rocket that flies.
"""

from __future__ import annotations

import math
import re
from typing import Any

KINDS = {"box", "cylinder", "truss", "crowd"}
POSES = {"stand", "arms_up", "arms_out", "point", "wave", "crouch", "jump", "fall", "lean", "hug", "sit"}
HAIR = {"big", "bun", "ponytail", "short", "long", "turban", "hood", "none"}
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


def _timed(shot: dict[str, Any], keys: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every timed thing in a shot: camera keys, hero and fire cues, moving props, actor keys."""
    moving = [k for prop in shot.get("extra") or [] for k in prop.get("anim") or []]
    acting = [k for a in shot.get("actors") or [] for k in a.get("keys") or []]
    return [*keys, *(shot.get("hero") or []), *(shot.get("fire") or []), *moving, *acting]


def _timed_problems(label: str, shot: dict[str, Any], keys: list[dict[str, Any]], ids: set[Any],
                    duration: float) -> list[str]:
    """Keys outside the generation, and cues that fire nothing."""
    late = [f"{label}: time {item.get('t')} is outside 0-{duration:g}s"
            for item in _timed(shot, keys) if not 0 <= float(item.get("t", 0)) <= duration + 1e-6]
    unknown = [f"{label}: fire refers to unknown id {cue.get('id')!r}"
               for cue in shot.get("fire") or [] if cue.get("id") not in ids]
    return late + unknown + _actor_problems(label, shot.get("actors") or [])


def _actor_problems(label: str, actors: list[dict[str, Any]]) -> list[str]:
    problems = []
    for actor in actors:
        name = actor.get("id", "?")
        if not actor.get("keys"):
            problems.append(f"{label}: actor {name} has no keys")
        if actor.get("hair", "short") not in HAIR:
            problems.append(f"{label}: actor {name} hair must be one of {sorted(HAIR)}")
        problems += [f"{label}: actor {name} pose {k.get('pose')!r} is not one of {sorted(POSES)}"
                     for k in actor.get("keys") or [] if k.get("pose", "stand") not in POSES]
    return problems


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


# ── Framing: where each cast head lands in the frame ──────────────────────────
# Figure proportions as blender/previs_scene.py builds them; that script runs inside Blender and cannot
# import this, so these are duplicated there (HEAD_RATIO, POSES) and tests/unit/test_previs.py keeps the
# two copies equal. HEAD_RATIO: (height below which a figure is a baby, its head radius / height, an
# adult's). POSE_BODY: each pose's body squash, lift (m) and forward tilt (degrees about x).
HEAD_RATIO = (0.8, 0.22, 0.17)
POSE_BODY = {"crouch": (0.72, 0, 0), "jump": (1.12, 0.35, 0), "fall": (1, 0, -75), "lean": (1, 0, 15),
             "sit": (0.6, 0, 0)}
SENSOR_MM = 36.0  # Blender's default, fitted to the frame's longer side
# Smallest head diameter, as a fraction of the frame height, by the first size word the shot names; a
# "medium" that shows a whole baby with room to spare is a wide shot, and Seedance would play it as one.
SIZE_MIN = (("medium wide", 0.04), ("close", 0.15), ("medium", 0.2))
OTHER_MIN = 0.04


def _around(keys: list[dict[str, Any]], t: float) -> tuple[dict[str, Any], dict[str, Any]]:
    """The last key at or before t and the first at or after it (the end keys outside the range)."""
    before = [k for k in keys if k["t"] <= t] or keys[:1]
    after = [k for k in keys if k["t"] >= t] or keys[-1:]
    return before[-1], after[0]


def _lerp(keys: list[dict[str, Any]], t: float, field: str) -> Any:
    """A key field at time t: linear between the keys around t, held before the first and after the last."""
    have = [k for k in keys if field in k]
    if not have:
        return None
    a, b = _around(have, t)
    f = 0.0 if b["t"] == a["t"] else (t - a["t"]) / (b["t"] - a["t"])
    va, vb = a[field], b[field]
    if isinstance(va, (int, float)):
        return va + (vb - va) * f
    return [x + (y - x) * f for x, y in zip(va, vb)]


def _body(pose: str) -> tuple[float, float, float]:
    return POSE_BODY.get(pose, (1, 0, 0))


def head_at(actor: dict[str, Any], t: float) -> tuple[list[float], float]:
    """World centre and radius of an actor's head at time t, as previs_scene.py places it."""
    h = float(actor.get("height", 1.2))
    small, baby, adult = HEAD_RATIO
    r = h * (baby if h < small else adult)
    keys = sorted(actor.get("keys") or [], key=lambda k: k["t"])
    pos = [*(_lerp(keys, t, "pos") or [0, 0]), 0][:3]
    facing = math.radians(_lerp(keys, t, "facing") or 0)
    bodies = [{"t": k["t"], "b": list(_body(k.get("pose", "stand")))} for k in keys]
    squash, lift, tilt = _lerp(bodies, t, "b") or (1, 0, 0)
    up = (h - r) * squash  # head centre above the feet, before tilt
    y = -up * math.sin(math.radians(tilt))
    z = up * math.cos(math.radians(tilt))
    centre = [pos[0] - y * math.sin(facing), pos[1] + y * math.cos(facing), pos[2] + lift + z]
    return centre, r


def _basis(pos: list[float], look: list[float]) -> tuple[list[float], list[float], list[float]]:
    """Forward, right and up of a camera aimed at `look` with world z up (Track To, up Y)."""
    def norm(v: list[float]) -> list[float]:
        n = math.sqrt(sum(c * c for c in v)) or 1.0
        return [c / n for c in v]
    fwd = norm([b - a for a, b in zip(pos, look)])
    right = norm([fwd[1], -fwd[0], 0.0]) if abs(fwd[2]) < 0.999 else [1.0, 0.0, 0.0]
    up = [right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2],
          right[0] * fwd[1] - right[1] * fwd[0]]
    return fwd, right, up


def project(point: list[float], radius: float, camera: dict[str, Any], aspect: float) -> dict[str, float] | None:
    """A sphere seen by a pinhole camera {pos, look, lens}: centre (u, v from the top-left, 0-1 of the frame)
    and diameter as a fraction of the frame height; None when it is behind the lens. aspect = width / height."""
    fwd, right, up = _basis(camera["pos"], camera["look"])
    d = [p - c for p, c in zip(point, camera["pos"])]
    depth = sum(a * b for a, b in zip(d, fwd))
    if depth <= radius * 0.5:
        return None
    width_mm = SENSOR_MM if aspect >= 1 else SENSOR_MM * aspect
    height_mm = width_mm / aspect
    scale = float(camera["lens"]) / depth
    return {"u": 0.5 + scale * sum(a * b for a, b in zip(d, right)) / width_mm,
            "v": 0.5 - scale * sum(a * b for a, b in zip(d, up)) / height_mm,
            "size": 2 * radius * scale / height_mm, "rx": radius * scale / width_mm}


def _camera_at(shot: dict[str, Any], t: float) -> dict[str, Any]:
    keys = camera_keys(shot)
    return {"pos": _lerp(keys, t, "pos"), "look": _lerp(keys, t, "look"),
            "lens": _lerp(keys, t, "lens") or shot.get("lens", 24)}


_EDGE = ("out of frame", "cut by")


def shot_size(body: str) -> str:
    """The shot-size phrase of a body ("Shot [0-4s] - close-up, ..." gives "close-up"); else the whole body."""
    found = re.search(r"shot \[[^\]]*\]\s*-\s*([^,.]+)", body, re.IGNORECASE)
    return (found.group(1) if found else body).lower()


def _least(size: str) -> float:
    return next((least for word, least in SIZE_MIN if word in size), OTHER_MIN)


def _head_problem(seen: dict[str, float] | None, size: str) -> str | None:
    """What is wrong with one projected head, or None. A close shot also loses a head whose centre sits
    within half its radius of an edge — the face is cut, not just the hair."""
    if seen is None:
        return "behind the camera"
    u, v, tall, rx = seen["u"], seen["v"], seen["size"], seen["rx"]
    if not (0 <= u <= 1 and 0 <= v <= 1):
        return f"out of frame (centre at {u:.2f}, {v:.2f})"
    least = _least(size)
    if tall < least:
        return f"too small ({tall:.0%} of the frame height, a {size.strip()} wants {least:.0%})"
    if "close" in size and min(u / rx, (1 - u) / rx, v / (tall / 2), (1 - v) / (tall / 2)) < 0.5:
        return f"cut by the frame edge (centre at {u:.2f}, {v:.2f})"
    return None


def framing_problems(shot: dict[str, Any], cast: list[str], seconds: float, body: str,
                     aspect: float) -> list[str]:
    """Cast heads the previs camera loses, cuts or shrinks, at the start, middle and end of the shot.
    A group of three or more may lose or cut a third of its heads at an edge — a crowded frame does that."""
    size = shot_size(body)
    actors = [a for a in shot.get("actors") or [] if a.get("id") in cast]
    problems = []
    for t in (0.0, seconds / 2, seconds):
        problems += [f"{who} at {t:g}s: head {why}" for who, why in _lost_at(shot, actors, t, size, aspect)]
    return problems


def _lost_at(shot: dict[str, Any], actors: list[dict[str, Any]], t: float, size: str,
             aspect: float) -> list[tuple[str, str]]:
    """[(actor, problem)] at one moment, a group's spare third of edge losses forgiven."""
    camera = _camera_at(shot, t)
    lost = [(a["id"], _head_problem(project(*head_at(a, t), camera, aspect), size)) for a in actors]
    lost = [(who, why) for who, why in lost if why]
    if sum(why.startswith(_EDGE) for _, why in lost) <= len(actors) // 3:
        lost = [(who, why) for who, why in lost if not why.startswith(_EDGE)]
    return lost


def _aspect(plan: dict[str, Any]) -> float:
    """Width / height of the previs render: the first shot's ratio, as reel_previs sizes it (9:16 if unknown)."""
    ratio = str(((plan.get("shots") or [{}])[0].get("kwargs") or {}).get("aspect_ratio", "9:16"))
    w, _, h = ratio.partition(":")
    try:
        return float(w) / float(h)
    except ValueError:
        return 9 / 16


def framing(plan: dict[str, Any]) -> dict[str, list[str]]:
    """{label: problems} for every previs'd shot whose cast heads are lost or tiny; clean shots left out."""
    shots = (plan.get("previs") or {}).get("shots") or {}
    aspect = _aspect(plan)
    report = {}
    for entry in plan.get("shots") or []:
        shot = shots.get(entry["label"])
        if not shot:
            continue
        seconds = float((entry.get("kwargs") or {}).get("duration_seconds") or 5)
        problems = framing_problems(shot, entry.get("cast") or [], seconds,
                                    entry.get("body") or entry.get("prompt") or "", aspect)
        if problems:
            report[entry["label"]] = problems
    return report
