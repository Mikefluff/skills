"""Splice new shots into a film's plan — the cut, its storyboard, previs, vocals and continuity in one go.

  python3 -m common.runners.cli.reel_insert --plan-file <dir>/plan.json --from <inserts.json> [--dry-run]

<inserts.json> is {"shots": [...], "continuity": [...], "note": "..."}. Each entry places one shot by
"insert_after": <label> (at that shot's end), "insert_before": <label> (at its start) or "replace": <label>
(that shot taken out, the new one at its place). It carries "shot" (the plan's shot: label, scene, cast,
location, dialogue, body, trim_start, trim_seconds, kwargs; or a hand-cut piece of an existing take,
{"label", "clip", "trim_start", "trim_seconds"}) and optionally "frame" (a storyboard frame), "previs"
(that shot's previs) and "vocals". Everything from the insertion point on moves by the new shot's length:
shots, title cards, sound placements, the total; shots are numbered again and frames follow their shots.

Three more kinds of entry rework the cut without anything new: {"remove": <label>} takes a shot out (the rest
moves back; its vocals go, its frames and previs too unless "keep_assets": true parks them); {"move": <label>,
"insert_after"|"insert_before": <anchor>} puts a shot elsewhere with its own frames, previs and vocals;
{"restore": <label>, "from": <plan file>, "insert_after"|"insert_before": <anchor>} brings back a shot removed
earlier, with its frames, previs and vocals, from another plan (a copy of plan.json.bak: the backup is
overwritten each run). Its rendered clip is still in the manifest by label, so nothing is rendered again.
{"trim": <label>, "trim_start"?, "trim_seconds"?} gives a shot a new window in its take, and {"split": <label>,
"cut_from": a, "cut_to": b} drops the stretch a..b (seconds of the take) from a rendered take, the rest playing on
as "<label>_2", a hand-cut piece of the same clip: for a frame the generation got wrong in the middle of a take.
Entries apply in order. An added shot may carry "sounds": [{"source", "at" (seconds into the shot),
"gain_db", ...}] laid as placements on the film's clock (they move with the cut from then on), and the file
may declare new "sources" (an sfx prompt) beside the shots: a silent render is scored in the mix, never
rendered again for its sound.

The plan is checked (its bible, its previs, labels and frame ids unique) before anything is written; the
previous plan is kept as <plan>.bak (one backup, overwritten each run). --dry-run prints what would change.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from .. import drama
from .. import previs as pv
from ..atomicfile import write_text
from ._trailer_retime import _owners, insert, remove, shift

_PLACES = ("insert_after", "insert_before", "replace")
_BESIDE = ("insert_after", "insert_before")


def _by_label(plan: dict[str, Any], label: str) -> dict[str, Any]:
    found = next((s for s in plan["shots"] if s["label"] == label), None)
    if found is None:
        raise ValueError(f"anchor {label!r} is not a shot in the plan")
    return found


def _place(entry: dict[str, Any], places: tuple[str, ...] = _PLACES) -> tuple[str, str]:
    found = [(k, entry[k]) for k in places if entry.get(k)]
    if len(found) != 1:
        name = entry.get("move") or entry.get("restore") or entry.get("shot", {}).get("label")
        raise ValueError(f"{name}: give exactly one of {', '.join(places)}")
    return found[0]


def _at(plan: dict[str, Any], kind: str, anchor: str) -> float:
    """Where on the clock a shot placed `kind` of `anchor` starts."""
    old = _by_label(plan, anchor)
    return float(old["clock_at"]) + (float(old["trim_seconds"]) if kind == "insert_after" else 0.0)


def _frames_of(plan: dict[str, Any], label: str, parked: bool = False) -> list[dict[str, Any]]:
    """The storyboard frames drawn for a shot: those on its index (and, with `parked`, any parked under its label)."""
    return [f for f, owner in _owners(plan) if owner == label or (parked and f.get("parked") == label)]


def _drop_shot_data(plan: dict[str, Any], label: str) -> None:
    """A replaced shot's previs and vocals go with it."""
    (plan.get("previs") or {}).get("shots", {}).pop(label, None)
    plan["vocals"] = [v for v in plan.get("vocals") or [] if v.get("shot") != label]


def _attach(plan: dict[str, Any], shot: dict[str, Any], frames: list[dict[str, Any]], previs: Any,
            vocals: list[dict[str, Any]] | None) -> None:
    """A shot's frames (on its new number), previs and vocals into the plan."""
    if frames:
        board = plan.setdefault("board", {}).setdefault("frames", [])
        board += [{**{k: v for k, v in f.items() if k != "parked"}, "shot": shot["index"]} for f in frames]
    if previs:
        plan.setdefault("previs", {}).setdefault("shots", {})[shot["label"]] = previs
    plan.setdefault("vocals", []).extend(vocals or [])


def _check_new(plan: dict[str, Any], shot: dict[str, Any], frames: list[dict[str, Any]], replaced: str | None) -> None:
    if not shot.get("label") or shot.get("trim_seconds") is None:
        raise ValueError(f"every shot needs a label and trim_seconds: {shot.get('label')!r}")
    if shot["label"] != replaced and any(s["label"] == shot["label"] for s in plan["shots"]):
        raise ValueError(f"label {shot['label']!r} is already a shot in the plan")
    taken = {f.get("id") for f in (plan.get("board") or {}).get("frames") or []}
    for frame in frames:
        if frame.get("id") in taken:
            raise ValueError(f"frame id {frame.get('id')!r} is already on the board")


def _add(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """A new shot spliced in after, before or in place of its anchor."""
    kind, anchor = _place(entry)
    frames = [entry["frame"]] if entry.get("frame") else []
    _check_new(plan, entry["shot"], frames, anchor if kind == "replace" else None)
    shot = copy.deepcopy(entry["shot"])
    at = float(_by_label(plan, anchor)["clock_at"]) if kind == "replace" else _at(plan, kind, anchor)
    if kind == "replace":
        remove(plan, anchor)
        _drop_shot_data(plan, anchor)
    insert(plan, shot, at)
    _attach(plan, shot, frames, entry.get("previs"), entry.get("vocals"))
    _lay_sounds(plan, shot, entry.get("sounds") or [])
    return shot


def _lay_sounds(plan: dict[str, Any], shot: dict[str, Any], sounds: list[dict[str, Any]]) -> None:
    """A shot's own sound design, "at" seconds into the shot, laid on the film's clock as placements: a silent
    render gets its bangs and whooshes from the mix, not from a second paid generation."""
    sound = plan.setdefault("sound", {})
    known = {s["id"] for s in sound.get("sources") or []}
    for cue in sounds:
        if cue["source"] not in known:
            raise ValueError(f"{shot['label']}: sound {cue['source']!r} is not a sound source (add it under \"sources\")")
        at = round(float(shot["clock_at"]) + float(cue.get("at", 0.0)), 3)
        sound.setdefault("placements", []).append({"fade_in": 0.01, "fade_out": 0.05, **cue, "at": at})


def _add_sources(plan: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    """New sound sources (an sfx prompt, a file) declared next to the shots that use them; an id already in the
    film is kept as it is, so a rerun does not pay for it again."""
    if not sources:
        return
    have = plan.setdefault("sound", {}).setdefault("sources", [])
    ids = {s["id"] for s in have}
    have.extend(s for s in sources if s["id"] not in ids)


def _remove(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """A shot out of the cut, its vocals with it; its frames and previs too, unless "keep_assets" parks them
    (frames stay on the board under "parked": <label>, the previs under previs.parked) for a later restore."""
    label = entry["remove"]
    _own_sounds(plan, _by_label(plan, label))  # its bangs go with it, not onto the shot that moves up
    frames = _frames_of(plan, label)
    shot = remove(plan, label)
    if entry.get("keep_assets"):
        plan.setdefault("board", {}).setdefault("frames", []).extend({**f, "shot": 0, "parked": label} for f in frames)
        previs = (plan.get("previs") or {}).get("shots", {}).get(label)
        if previs:
            plan["previs"].setdefault("parked", {})[label] = previs
    _drop_shot_data(plan, label)
    return shot


def _own_sounds(plan: dict[str, Any], shot: dict[str, Any]) -> list[dict[str, Any]]:
    """The one-shot sounds that play inside a shot (taken out of the plan), each at its offset into the shot. A
    bed or cue that runs on past the shot stays: it belongs to the scene, not to this shot."""
    a = float(shot["clock_at"])
    b = a + float(shot["trim_seconds"])
    placements = (plan.get("sound") or {}).get("placements") or []
    own = [p for p in placements if a <= float(p["at"]) < b and float(p.get("length") or 0) <= b - float(p["at"])]
    plan["sound"]["placements"] = [p for p in placements if p not in own] if own else placements
    return [{**p, "at": round(float(p["at"]) - a, 3)} for p in own]


def _move(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """A shot taken out and put back at its anchor, with its own frames, previs, vocals and sounds."""
    label = entry["move"]
    kind, anchor = _place(entry, _BESIDE)
    if anchor == label:
        raise ValueError(f"{label}: a shot cannot move next to itself")
    sounds = _own_sounds(plan, _by_label(plan, label))
    frames = _frames_of(plan, label)
    shot = remove(plan, label)
    insert(plan, shot, _at(plan, kind, anchor))
    _attach(plan, shot, frames, None, None)
    plan["sound"]["placements"] += [{**p, "at": round(float(shot["clock_at"]) + p["at"], 3)} for p in sounds]
    return shot


def _taken_from(old: dict[str, Any], label: str) -> tuple[dict, list[dict], Any, list[dict]]:
    """A shot as another plan has it: the shot, its frames (parked ones too), its previs and its vocals."""
    kept = old.get("previs") or {}
    previs = (kept.get("shots") or {}).get(label) or (kept.get("parked") or {}).get(label)
    vocals = [v for v in old.get("vocals") or [] if v.get("shot") == label]
    return copy.deepcopy((_by_label(old, label), _frames_of(old, label, parked=True), previs, vocals))


def _unpark(plan: dict[str, Any], label: str) -> None:
    """What this plan parked for the shot is the same frame and previs coming back."""
    if plan.get("board"):
        plan["board"]["frames"] = [f for f in plan["board"].get("frames") or [] if f.get("parked") != label]
    ((plan.get("previs") or {}).get("parked") or {}).pop(label, None)


def _restore(plan: dict[str, Any], entry: dict[str, Any], base: Path) -> dict[str, Any]:
    """A shot taken out earlier, back from another plan file (plan.json.bak): the shot, its frames, previs and
    vocals as they were there. Its clip is still in the manifest under its label, so nothing is rendered."""
    kind, anchor = _place(entry, _BESIDE)
    path = base / entry["from"] if (base / entry["from"]).is_file() else Path(entry["from"])
    shot, frames, previs, vocals = _taken_from(json.loads(path.read_text(encoding="utf-8")), entry["restore"])
    _unpark(plan, shot["label"])
    _check_new(plan, shot, frames, None)
    insert(plan, shot, _at(plan, kind, anchor))
    _attach(plan, shot, frames, previs, vocals)
    return shot


def _retrim(plan: dict[str, Any], shot: dict[str, Any], start: float, seconds: float) -> None:
    """A shot's window in its take changed: everything after it moves by the difference."""
    end = float(shot["clock_at"]) + float(shot["trim_seconds"])
    shift(plan, end, round(seconds - float(shot["trim_seconds"]), 3))
    shot["trim_start"], shot["trim_seconds"] = round(start, 3), round(seconds, 3)


def _trim(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """{"trim": <label>, "trim_start"?, "trim_seconds"?}: a new window in the same take, the cut following."""
    shot = _by_label(plan, entry["trim"])
    start = float(entry.get("trim_start", shot.get("trim_start") or 0.0))
    _retrim(plan, shot, start, float(entry.get("trim_seconds", shot["trim_seconds"])))
    return shot


def _split(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """{"split": <label>, "cut_from": a, "cut_to": b} (seconds of the take): the stretch a..b of a rendered take
    goes, the rest plays on as a hand-cut piece "<label>_2" of the same clip. For a frame the take got wrong."""
    shot = _by_label(plan, entry["split"])
    start, cut_from, cut_to = float(shot.get("trim_start") or 0.0), float(entry["cut_from"]), float(entry["cut_to"])
    end = start + float(shot["trim_seconds"])
    if not start < cut_from < cut_to < end:
        raise ValueError(f"{shot['label']}: cut {cut_from}..{cut_to} must lie inside its window {start}..{end}")
    clip = entry.get("clip") or _clip_of(plan, shot["label"])
    _retrim(plan, shot, start, cut_from - start)
    tail = {"label": f"{shot['label']}_2", "scene": shot.get("scene"), "cast": shot.get("cast", []),
            "location": shot.get("location"), "dialogue": [], "clip": clip, "trim_start": round(cut_to, 3),
            "trim_seconds": round(end - cut_to, 3), "kwargs": dict(shot.get("kwargs") or {})}
    insert(plan, tail, float(shot["clock_at"]) + float(shot["trim_seconds"]))
    return tail


def _clip_of(plan: dict[str, Any], label: str) -> str:
    """The rendered take of a shot, relative to the output dir, from the reel manifest."""
    out = Path(plan.get("output_dir") or ".")
    manifest = out / "manifest.json"
    items = json.loads(manifest.read_text(encoding="utf-8")).get("items") or [] if manifest.is_file() else []
    path = next((i["output_path"] for i in items if i.get("label") == label and i.get("status") == "succeeded"), None)
    if not path:
        raise ValueError(f"{label}: no rendered take to split; render it first or give \"clip\"")
    return str(Path(path).relative_to(out)) if Path(path).is_relative_to(out) else path


def apply_entry(plan: dict[str, Any], entry: dict[str, Any], base: Path = Path(".")) -> tuple[str, dict[str, Any]]:
    """Apply one entry to `plan` in place; returns what was done (added, removed, moved, restored, trimmed,
    split) and the shot."""
    kinds = (("remove", "removed", _remove), ("move", "moved", _move), ("trim", "trimmed", _trim),
             ("split", "split", _split))
    for key, verb, fn in kinds:
        if entry.get(key):
            return verb, fn(plan, entry)
    if entry.get("restore"):
        return "restored", _restore(plan, entry, base)
    return "added", _add(plan, entry)


def bible_path(plan: dict[str, Any], plan_file: Path) -> Path | None:
    """plan["bible"] is relative to the plan's directory, or else to where the command runs."""
    if not plan.get("bible"):
        return None
    near = plan_file.parent / plan["bible"]
    return near if near.is_file() else Path(plan["bible"])


def _repeated(name: str, values: list[Any]) -> list[str]:
    return [f"{name} {x!r} appears more than once" for x in sorted({x for x in values if values.count(x) > 1})]


def _bible_problems(plan: dict[str, Any], plan_file: Path) -> list[str]:
    bible = bible_path(plan, plan_file)
    if bible is None:
        return []
    # a hand-cut clip is not rendered, so it needs no body
    cut = {f"{s['label']}: no body" for s in plan["shots"] if s.get("clip")}
    return [p for p in drama.validate(plan, drama.load_bible(bible)) if p not in cut]


def _previs_problems(plan: dict[str, Any]) -> list[str]:
    if not plan.get("previs"):
        return []
    durations = {s["label"]: float((s.get("kwargs") or {}).get("duration_seconds") or 5) for s in plan["shots"]}
    return pv.validate(plan["previs"], durations)


def problems(plan: dict[str, Any], plan_file: Path) -> list[str]:
    frames = (plan.get("board") or {}).get("frames") or []
    return (_repeated("label", [s["label"] for s in plan["shots"]]) + _repeated("frame id", [f.get("id") for f in frames])
            + _bible_problems(plan, plan_file) + _previs_problems(plan))


def splice(plan: dict[str, Any], inserts: dict[str, Any], base: Path = Path(".")) -> list[tuple[str, dict[str, Any]]]:
    """Every entry of `inserts` applied to `plan` in order, then its continuity; returns (what was done, shot)."""
    _add_sources(plan, inserts.get("sources") or [])
    done = [apply_entry(plan, entry, base) for entry in inserts.get("shots") or []]
    plan.setdefault("continuity", []).extend(inserts.get("continuity") or [])
    return done


def _clock(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def _row(verb: str, s: dict[str, Any]) -> str:
    if verb == "removed":
        return f"  {s['label']:<8} removed   {float(s['trim_seconds']):.2f}s"
    return (f"  {s['label']:<8} #{s['index']:<3} at {_clock(float(s['clock_at']))}  {float(s['trim_seconds']):.2f}s"
            + ("  (clip)" if s.get("clip") else "") + ("" if verb == "added" else f"  ({verb})"))


def summary(plan: dict[str, Any], done: list[tuple[str, dict[str, Any]]], inserts: dict[str, Any],
            plan_file: Path) -> str:
    rows = [_row(verb, s) for verb, s in done]
    added = [s for verb, s in done if verb == "added"]
    last = max(plan["shots"], key=lambda s: float(s["clock_at"]))
    end = float(last["clock_at"]) + float(last["trim_seconds"])
    total = (plan.get("sound") or {}).get("total_seconds")
    rows.append(f"  cut ends at {_clock(end)}" + (f", film {_clock(float(total))}" if total else ""))
    return "\n".join(rows + ["", "next:", *next_commands(added, inserts, plan_file)])


def _only(command: str, labels: list[str]) -> str:
    return f"{command} --only {','.join(labels)}" if labels else ""


def next_commands(added: list[dict[str, Any]], inserts: dict[str, Any], plan_file: Path) -> list[str]:
    entries = inserts.get("shots") or []
    cli = f"python3 -m common.runners.cli.{{}} --plan-file {plan_file}"
    lines = [_only(cli.format("reel_board"), [e["frame"]["id"] for e in entries if e.get("frame")]),
             _only(cli.format("reel_previs"), [e["shot"]["label"] for e in entries if e.get("previs")]),
             cli.format("reel_cast"),
             _only(cli.format("reel"), [s["label"] for s in added if not s.get("clip")]),
             _only(cli.format("reel_upscale"), [s["label"] for s in added]),
             cli.format("reel_animatic") + " --clips"]
    return [f"  {line}" for line in lines if line]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_insert")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--from", dest="inserts", type=Path, required=True,
                        help="JSON with the shots to splice in (insert_after / insert_before / replace), "
                                 "or to remove / move / restore")
    parser.add_argument("--dry-run", action="store_true", help="print what would change, write nothing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    inserts = json.loads(args.inserts.read_text(encoding="utf-8"))
    before = set(problems(plan, args.plan_file))
    try:
        done = splice(plan, inserts, args.plan_file.parent)
    except (ValueError, KeyError, OSError) as exc:
        print(f"reel_insert: {exc}", file=sys.stderr)
        return 1
    found = [p for p in problems(plan, args.plan_file) if p not in before]
    if found:
        print("reel_insert: the plan would not validate:\n  " + "\n  ".join(found), file=sys.stderr)
        return 1
    print(summary(plan, done, inserts, args.plan_file))
    if args.dry_run:
        print("\n(dry run: nothing written)")
        return 0
    shutil.copyfile(args.plan_file, args.plan_file.with_name(args.plan_file.name + ".bak"))
    write_text(args.plan_file, json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {args.plan_file} (previous: {args.plan_file.name}.bak)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
