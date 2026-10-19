"""Splice new shots into a film's plan — the cut, its storyboard, previs, vocals and continuity in one go.

  python3 -m common.runners.cli.reel_insert --plan-file <dir>/plan.json --from <inserts.json> [--dry-run]

<inserts.json> is {"shots": [...], "continuity": [...], "note": "..."}. Each entry places one shot by
"insert_after": <label> (at that shot's end), "insert_before": <label> (at its start) or "replace": <label>
(that shot taken out, the new one at its place). It carries "shot" (the plan's shot: label, scene, cast,
location, dialogue, body, trim_start, trim_seconds, kwargs; or a hand-cut piece of an existing take,
{"label", "clip", "trim_start", "trim_seconds"}) and optionally "frame" (a storyboard frame), "previs"
(that shot's previs) and "vocals". Everything from the insertion point on moves by the new shot's length:
shots, title cards, sound placements, the total; shots are numbered again and frames follow their shots.

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
from ._trailer_retime import insert, remove

_PLACES = ("insert_after", "insert_before", "replace")


def _by_label(plan: dict[str, Any], label: str) -> dict[str, Any]:
    found = next((s for s in plan["shots"] if s["label"] == label), None)
    if found is None:
        raise ValueError(f"anchor {label!r} is not a shot in the plan")
    return found


def _place(entry: dict[str, Any]) -> tuple[str, str]:
    places = [(k, entry[k]) for k in _PLACES if entry.get(k)]
    if len(places) != 1:
        raise ValueError(f"{entry.get('shot', {}).get('label')}: give exactly one of {', '.join(_PLACES)}")
    return places[0]


def _drop_shot_data(plan: dict[str, Any], label: str) -> None:
    """A replaced shot's previs and vocals go with it."""
    (plan.get("previs") or {}).get("shots", {}).pop(label, None)
    plan["vocals"] = [v for v in plan.get("vocals") or [] if v.get("shot") != label]


def _check_new(plan: dict[str, Any], entry: dict[str, Any], replaced: str | None) -> None:
    shot = entry["shot"]
    if not shot.get("label") or shot.get("trim_seconds") is None:
        raise ValueError(f"every shot needs a label and trim_seconds: {shot.get('label')!r}")
    if shot["label"] != replaced and any(s["label"] == shot["label"] for s in plan["shots"]):
        raise ValueError(f"label {shot['label']!r} is already a shot in the plan")
    frame = entry.get("frame")
    frames = (plan.get("board") or {}).get("frames") or []
    if frame and any(f.get("id") == frame.get("id") for f in frames):
        raise ValueError(f"frame id {frame.get('id')!r} is already on the board")


def apply_entry(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """Splice one entry into `plan` in place; returns the shot as it now sits in the cut."""
    kind, anchor = _place(entry)
    old = _by_label(plan, anchor)
    _check_new(plan, entry, anchor if kind == "replace" else None)
    shot = copy.deepcopy(entry["shot"])
    at = float(old["clock_at"])
    if kind == "insert_after":
        at += float(old["trim_seconds"])
    elif kind == "replace":
        remove(plan, anchor)
        _drop_shot_data(plan, anchor)
    insert(plan, shot, at)
    if entry.get("frame"):
        plan.setdefault("board", {}).setdefault("frames", []).append({**entry["frame"], "shot": shot["index"]})
    if entry.get("previs"):
        plan.setdefault("previs", {}).setdefault("shots", {})[shot["label"]] = entry["previs"]
    plan.setdefault("vocals", []).extend(entry.get("vocals") or [])
    return shot


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


def splice(plan: dict[str, Any], inserts: dict[str, Any]) -> list[dict[str, Any]]:
    """Every entry of `inserts` spliced into `plan` in order, then its continuity; returns the new shots."""
    added = [apply_entry(plan, entry) for entry in inserts.get("shots") or []]
    plan.setdefault("continuity", []).extend(inserts.get("continuity") or [])
    return added


def _clock(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def summary(plan: dict[str, Any], added: list[dict[str, Any]], inserts: dict[str, Any], plan_file: Path) -> str:
    rows = [f"  {s['label']:<8} #{s['index']:<3} at {_clock(float(s['clock_at']))}  {float(s['trim_seconds']):.2f}s"
            + ("  (clip)" if s.get("clip") else "") for s in added]
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
                        help="JSON with the shots to splice in (insert_after / insert_before / replace)")
    parser.add_argument("--dry-run", action="store_true", help="print what would change, write nothing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    inserts = json.loads(args.inserts.read_text(encoding="utf-8"))
    before = set(problems(plan, args.plan_file))
    try:
        added = splice(plan, inserts)
    except (ValueError, KeyError) as exc:
        print(f"reel_insert: {exc}", file=sys.stderr)
        return 1
    found = [p for p in problems(plan, args.plan_file) if p not in before]
    if found:
        print("reel_insert: the plan would not validate:\n  " + "\n  ".join(found), file=sys.stderr)
        return 1
    print(summary(plan, added, inserts, args.plan_file))
    if args.dry_run:
        print("\n(dry run: nothing written)")
        return 0
    shutil.copyfile(args.plan_file, args.plan_file.with_name(args.plan_file.name + ".bak"))
    write_text(args.plan_file, json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {args.plan_file} (previous: {args.plan_file.name}.bak)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
