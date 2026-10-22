"""The shot matrix — one row per shot saying what it is built from, and why, before anything is paid for.

A trailer mixes routes: a close-up that must be the cast's face goes to a
first-frame model (Wan), a shot carried by its camera and its action goes to
Seedance with a clay previs, a composite cut by hand is a clip. Deciding that
shot by shot in conversation drifted (every silent shot went to one route,
every face to another). The matrix makes the decision explicit and the same
every time:

  what      size, faces seen, the line, the camera move named in the body
  route     clip | wan | seedance, with the rule that chose it ("why")
  inputs    what the route is sent: first frame, blurred frame, location, previs
  voice     wan-mouth (the cast's take laid on the clip's mouth), none
  into      the transition into the shot from the one before (see TRANSITIONS); "out" is the
            matching move on the outgoing shot's tail
  status    done, todo, failed, redo (made on another route), no-previs (made before its previs)
  takes     every paid render of the shot (<out>/takes.json, appended by reel): how many, what they cost,
            and which one the cut uses; a take marked "rejected" is never the answer
  next      keep | render, with its estimate — nothing is rendered that this column does not name

`plan["matrix"][label]["route"]` set by hand wins over the rules and is kept
("pinned"). `apply` writes each shot's `video_provider` from the matrix, so
reel_cast and reel act on it and nothing else.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROUTES = {"wan": "openrouter-wan-3-0", "seedance": "openrouter-seedance-2-5", "atlas": "atlas-seedance-2-5"}

# Read off the body's "Shot [0-4s] - <size, angle, lens>, <move>." sentence.
_FACE_SIZES = ("extreme close", "close-wide", "close-up", "medium close", "close,", "close ")
_DEVICE = re.compile(r"cctv|kiosk camera|dash ?cam|body ?cam|locked-off, cctv|security camera", re.I)
_COMPLEX = re.compile(r"whip|crash[- ]zoom|track(s|ing)?|orbit|arc|crane|rush|drop|top-down|through the|"
                      r"speed[- ]ramp|slow motion|fly|swoop", re.I)
_ACTION = re.compile(r"\b(slam|punch|lunge|chase|run|fall|crash|smash|grab|swing|scatter|ram|stumbl|sprint|"
                     r"leap|vault|tackle|shove|burst)\w*", re.I)


def shot_line(shot: dict[str, Any]) -> str:
    """The body's camera sentence: size, angle, lens, move."""
    m = re.search(r"Shot \[[^\]]*\]\s*-\s*(.*?)(?:\.\s|$)", shot.get("body") or "")
    return (m.group(1) if m else "").strip()


def size(shot: dict[str, Any]) -> str:
    line = shot_line(shot).lower()
    for name in ("extreme close", "close-wide", "medium close", "close-up", "close insert", "insert", "close",
                 "medium-wide", "medium", "wide"):
        if line.startswith(name) or f" {name}" in line[:30]:
            return name
    return "?"


def opening(shot: dict[str, Any]) -> str:
    body = (shot.get("body") or "").lower()
    return "crash" if re.search(r"crash[- ]zoom", body) else "whip" if "whip" in body else "cut"


# Action shots in the fast acts play faster than they were rendered: a generation's fight comes back at a
# careful, even pace, and Ritchie undercranks. The slow motion of rule 109 is the generation's own (the body asks
# for it); the edit does not slow a shot again (pinned "ramp" cuts excepted, interpolated, never duplicated).
ACTION_SPEED = 1.3


def _live(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """The shots in the cut, in clock order."""
    return sorted((s for s in plan["shots"] if not s.get("cut")), key=lambda s: float(s["clock_at"]))


def _acts(plan: dict[str, Any], shots: list[dict[str, Any]]) -> dict[str, str]:
    """label → the name of the act it sits in."""
    acts = {}
    labels = [s["label"] for s in shots]
    for act in (plan.get("trailer") or {}).get("acts") or []:
        if act.get("from") in labels and act.get("to") in labels:
            for lab in labels[labels.index(act["from"]): labels.index(act["to"]) + 1]:
                acts[lab] = act.get("name")
    return acts


def _is_action(shot: dict[str, Any], plan: dict[str, Any]) -> bool:
    """Action without a line, a clip or a narrated line (a narrated shot is held for its line, never rushed)."""
    told = any(n.get("shot") == shot["label"] for n in plan.get("narration") or [])
    return (bool(_ACTION.search(shot.get("body") or "")) and not shot.get("dialogue") and not shot.get("clip")
            and not told)


def speed(shot: dict[str, Any], plan: dict[str, Any]) -> float:
    """How fast the cut plays the shot: action without a line in the escalation or the montage, faster."""
    fast = _acts(plan, _live(plan)).get(shot["label"]) in ("escalation", "montage", "drop", "peak")
    return ACTION_SPEED if fast and _is_action(shot, plan) and not _DEVICE.search(shot_line(shot)) else 1.0


# Cut → (into the next shot, out of this one). Built in the edit (reel_animatic) on both sides of the cut.
TRANSITIONS = {
    "cut": "plain cut",
    "whip": "whip-through: the tail smears and slides out, the next shot slides in from the same side",
    "crash": "crash into the cut: the tail snaps in, the next shot lands close and settles",
    "ramp": "speed ramp: the tail's action drops to slow motion for half a second, then a hard cut",
    "wipe": "foreground wipe: a dark shape crosses the lens out of one shot and off the next",
    "flash": "flash frame: two white frames on the impact",
    "dip": "dip to black: out of one place or time and up into the next",
    "iris": "iris: a circle closes on the shot and opens on the next — a cartoon's full stop",
}


_CRASH_SIZES = ("close", "close-wide", "close-up", "insert", "close insert", "extreme close")


def _fixed_into(shot: dict[str, Any], old: dict[str, Any]) -> str | None:
    """A transition decided before the rules: the film's own edit, a pinned row, a strobe."""
    label = shot["label"]
    if shot.get("into") in TRANSITIONS:
        return shot["into"]  # the film's own edit (its chain decided the cut), above the defaults
    if (old.get(label) or {}).get("into_pinned"):
        return old[label]["into"]
    if shot.get("strobe"):
        return "cut"  # a strobe is hard cuts, frame against frame
    return None


def _rule_into(prev: dict[str, Any] | None, shot: dict[str, Any], cards: list[float], act: str | None) -> str:
    """The director's rules for the cut from `prev` into `shot`."""
    move = opening(shot)
    if prev is None:
        return "cut"
    if move in ("whip", "crash"):
        return move  # rule 108 first: a scene change on a whip or a crash zoom
    at = float(shot["clock_at"])
    if any(abs(c - at) < 2.5 and c < at for c in cards):
        return "flash"  # coming back from a title card on the groove's hit
    moved = shot.get("location") != prev.get("location")
    if act in ("montage", "peak") and moved:
        return "wipe"
    if moved:
        # rule 108: a scene changes on a whip or a crash zoom, never a plain cut. A crash lands on a face or a
        # screen (a close or insert), a whip carries everything else.
        return "crash" if size(shot) in _CRASH_SIZES else "whip"
    return "cut"


def transitions(plan: dict[str, Any]) -> dict[str, str]:
    """label → the transition INTO that shot, by the director's rules (108 whip/crash, 109 ramp, 111 montage)
    and the clock: a shot before a title card goes out on a flash; a pinned "into" in the matrix wins."""
    old = plan.get("matrix") or {}
    cards = [float(c["clock_at"]) for c in (plan.get("trailer") or {}).get("title_cards") or []]
    shots = _live(plan)
    acts = _acts(plan, shots)
    out = {}
    for prev, shot in zip([None, *shots], shots):
        fixed = _fixed_into(shot, old)
        out[shot["label"]] = fixed if fixed is not None else _rule_into(prev, shot, cards, acts.get(shot["label"]))
    return out


def decide(shot: dict[str, Any]) -> tuple[str, str]:
    """(route, why) by the rules; a hand-cut clip is always a clip."""
    if shot.get("clip"):
        return "clip", "cut by hand (composite)"
    line, body = shot_line(shot), shot.get("body") or ""
    # "opens on the tail of a whip pan" is the edit's move into the shot, made in the cut, not the camera's
    line = re.sub(r";?\s*the shot opens on the tail of a [^;]*", "", line)
    face = size(shot) in ("extreme close", "close-wide", "medium close", "close-up", "close") \
        and bool(shot.get("cast"))
    complex_cam = bool(_COMPLEX.search(line))
    if shot.get("dialogue"):
        return "wan", "speaks: the cast's face and a mouth for the take" + (
            "; its move is simplified (Wan takes no previs)" if complex_cam else "")
    if _DEVICE.search(line):
        return "seedance", "a device's view: locked-off framing, faces small"
    if face and not complex_cam:
        return "wan", "carried by a recognisable face, simple move"
    if complex_cam or _ACTION.search(body):
        return "seedance", "carried by the camera or the action: previs as Video 1"
    return "seedance", "wide or medium without a face to hold"


def inputs(route: str, shot: dict[str, Any], previs: bool) -> list[str]:
    if route == "clip":
        return [shot.get("clip", "")]
    if route == "wan":
        return ["board frame as first frame", "motion prompt"]
    return [*(["previs (Video 1)"] if previs else []), "location plate", "board frame, heads blurred",
            "people in words"]


def _status(item: dict[str, Any], route: str, plan: dict[str, Any]) -> str:
    """done | todo | failed | redo (rendered on another route than its row now names) |
    no-previs (a Seedance shot rendered before its previs existed)."""
    if item.get("status") != "succeeded":
        return "failed" if item.get("status") == "failed" else "todo"
    kwargs = item.get("kwargs") or {}
    made_on = kwargs.get("_route") or plan.get("video_provider")
    if made_on != ROUTES[route]:
        return "redo"
    has_previs = item["label"] in ((plan.get("previs") or {}).get("shots") or {})
    return "no-previs" if route == "seedance" and has_previs and not kwargs.get("reference_videos") else "done"


def takes(plan: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(plan.get("output_dir") or ".") / "takes.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []


def _take_file(item: Any, out: Path) -> str:
    """The render's path relative to the output folder when it sits inside it."""
    path = Path(item.output_path).resolve()
    return str(path.relative_to(out.resolve())) if path.is_relative_to(out.resolve()) else item.output_path


def _take(item: Any, file: str, plan: dict[str, Any], estimate) -> dict[str, Any]:
    kw = item.kwargs or {}
    how = ", ".join(k for k in ("first_frame", "reference_videos", "reference_images") if kw.get(k))
    return {"label": item.label, "file": file, "route": kw.get("_route") or plan.get("video_provider"),
            "how": how, "cost_usd": round(float(estimate(item) or 0), 2)}


def record_takes(plan: dict[str, Any], items: list[Any], estimate) -> None:
    """Add every newly succeeded render to the take ledger (`estimate(item)` → dollars) as the take in the cut,
    with its time, length, prompt, size and move; the label's take in the cut before it becomes an alternate."""
    from . import take_ledger

    out = Path(plan.get("output_dir") or ".")
    ledger = takes(plan)
    known = {t["file"] for t in ledger if not t.get("untracked")}
    for item in items:
        if item.status != "succeeded" or not item.output_path:
            continue
        file = _take_file(item, out)
        if file in known:
            continue
        take = _take(item, file, plan, estimate)
        take.update(created=take_ledger.created(file), duration=take_ledger.duration(out / file),
                    prompt=getattr(item, "prompt", "") or "", prompt_source="manifest", status="in cut", reason="")
        take.update(take_ledger.camera(take["prompt"]))
        if take["duration"]:
            take["usable"] = [[take_ledger.HEAD, take["duration"]]]
        take_ledger.land(ledger, take)
    (out / "takes.json").write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _manifest(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """label → the manifest item of its last render."""
    manifest = Path(plan.get("output_dir") or ".") / "manifest.json"
    if not manifest.is_file():
        return {}
    return {item["label"]: item for item in json.loads(manifest.read_text(encoding="utf-8")).get("items") or []}


def _voice(shot: dict[str, Any], route: str) -> str:
    if not shot.get("dialogue"):
        return "none"
    return "wan-mouth" if route == "wan" else "seedance-own (needs conform)"


def _row(shot: dict[str, Any], plan: dict[str, Any], item: dict[str, Any], into: str) -> dict[str, Any]:
    """One shot's row before its takes: what it is, its route and why, and where it stands."""
    label, old = shot["label"], (plan.get("matrix") or {}).get(shot["label"]) or {}
    previs = (plan.get("previs") or {}).get("shots") or {}
    pinned = old.get("pinned")
    route, why = (old["route"], old.get("why", "pinned by hand")) if pinned else decide(shot)
    return {
        "clock": round(float(shot["clock_at"]), 2), "seconds": round(float(shot["trim_seconds"]), 2),
        "size": size(shot), "cast": shot.get("cast") or [],
        "line": (shot.get("dialogue") or [{}])[0].get("line", ""),
        "camera": previs.get(label, {}).get("move_id") or shot_line(shot)[:80],
        "route": route, "why": why, "pinned": bool(pinned),
        "inputs": inputs(route, shot, label in previs),
        "voice": _voice(shot, route),
        "speed": speed(shot, plan), "into": into, "into_pinned": bool(old.get("into_pinned")),
        "status": "clip" if route == "clip" else _status(item, route, plan),
        "file": shot.get("clip") or item.get("output_path"),
    }


def _takes_cols(row: dict[str, Any], mine: list[dict[str, Any]]) -> dict[str, Any]:
    """The take columns: how many, what they cost, what to do next, and the note on the take in the cut."""
    current = row["file"] or ""
    used = next((t for t in mine if current.endswith(t["file"])), None)
    rejected = bool(used and (used.get("verdict") == "rejected" or used.get("status") == "rejected"))
    return {"takes": len(mine), "spent": round(sum(t["cost_usd"] for t in mine), 2),
            "next": "render" if rejected or row["status"] in ("todo", "failed") else "keep",
            "note": (used or {}).get("note", "")}


def build(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The matrix for every shot; rows pinned by hand keep their route."""
    done = _manifest(plan)
    into = transitions(plan)
    ledger = takes(plan)
    rows = {}
    for shot in _live(plan):
        label = shot["label"]
        row = _row(shot, plan, done.get(label) or {}, into[label])
        row.update(_takes_cols(row, [t for t in ledger if t["label"] == label]))
        rows[label] = row
    return rows


def apply(plan: dict[str, Any], rows: dict[str, dict[str, Any]]) -> list[str]:
    """Each shot's video_provider from its row; returns the labels whose route changed."""
    changed = []
    for shot in plan["shots"]:
        route = rows[shot["label"]]["route"]
        if route == "clip":
            continue
        slug = ROUTES[route]
        if (shot.get("video_provider") or plan.get("video_provider")) != slug:
            changed.append(shot["label"])
        shot["video_provider"] = slug
    plan["matrix"] = rows
    return changed


def table(rows: dict[str, dict[str, Any]]) -> str:
    """The matrix as a markdown table."""
    head = ("| shot | s | size | line | camera | route | into | takes | spent | in the cut | next |\n|"
            + "---|" * 11)
    out = [head]
    for label, r in rows.items():
        line = (r["line"][:24] + "…") if len(r["line"]) > 24 else r["line"]
        cut = "clip" if r["status"] == "clip" else (r["note"] or r["status"])
        out.append(f"| {label}{' 📌' if r['pinned'] else ''} | {r['seconds']} | {r['size']} | {line} | "
                   f"{r['camera'][:32]} | {r['route']} | {r['into']} | {r['takes']} | ${r['spent']:.2f} | {cut} | "
                   f"{r['next']} |")
    spent = sum(r["spent"] for r in rows.values())
    todo = [k for k, r in rows.items() if r["next"] == "render"]
    out.append(f"\nSpent on takes: ${spent:.2f}. To render ({len(todo)}): {', '.join(todo) or 'nothing'}")
    return "\n".join(out)
