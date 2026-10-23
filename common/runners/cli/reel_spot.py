"""A spotting pass laid into the film: each shot's sound cues replace the one-shot effects it had.

  python3 -m common.runners.cli.reel_spot --plan-file <dir>/plan.json --cues <cues.json> [...] [--dry-run]

A cue list (one JSON list per file) has, per cue: "label" (the shot), "at" (seconds into the shot on screen),
"layer" (foley | hard | accent | oneoff | none), "source" (an existing sound source id) or "prompt" (a new
one-event sound-effect prompt), "duration", "gain_db", "why". A shot named in the cues loses every one-shot
effect placement that starts inside it — not its beds, music, vocals or the flights under its bridges — and
gets the cues instead, on the film's clock. A new prompt becomes a sound source ("sfx", id from its words)
that the next reel_animatic run makes; the same prompt twice is one source. "none" cues are notes, not sound.
--dry-run prints what would change and what the new sources cost (ElevenLabs bills 40 credits a second).
The previous plan is kept as <plan>.bak.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

CREDITS_PER_SECOND = 40
_KEEP = re.compile(r"bed|score|song|^vocal_|^prod_|^flight_whoosh$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_spot")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--cues", type=Path, nargs="+", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def source_id(prompt: str) -> str:
    """A stable id for a new effect: its first words and a short hash of the whole prompt."""
    words = "_".join(re.findall(r"[a-z]+", prompt.lower())[:3]) or "sfx"
    return f"{words}_{hashlib.sha256(prompt.encode()).hexdigest()[:6]}"


def _new_sources(cues: list[dict[str, Any]], known: set[str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for cue in cues:
        if cue.get("layer") == "none" or (cue.get("source") in known) or not cue.get("prompt"):
            continue
        sid = source_id(cue["prompt"])
        out.setdefault(sid, {"id": sid, "kind": "sfx", "prompt": cue["prompt"],
                             "duration_seconds": max(0.5, min(30.0, float(cue.get("duration") or 1.5)))})
    return out


def _placements(cues: list[dict[str, Any]], clock: dict[str, float], known: set[str]) -> list[dict[str, Any]]:
    laid = []
    for cue in cues:
        if cue.get("layer") == "none" or cue["label"] not in clock:
            continue
        sid = cue["source"] if cue.get("source") in known else source_id(cue.get("prompt") or "")
        laid.append({"source": sid, "at": round(clock[cue["label"]] + float(cue.get("at") or 0), 3),
                     "gain_db": float(cue.get("gain_db") or -6), "fade_in": 0.01, "fade_out": 0.05,
                     "keep": True})  # spotted and layered on purpose: the mix's declutter must not thin it
    return laid


def _replaced(placements: list[dict[str, Any]], spans: list[tuple[float, float]]) -> list[dict[str, Any]]:
    """The one-shot effects that start inside the spans: not beds, music, vocals, production or flights."""
    def one_shot(p: dict[str, Any]) -> bool:
        return not _KEEP.search(p["source"]) and not p.get("length")
    return [p for p in placements if one_shot(p) and any(a <= float(p["at"]) < b for a, b in spans)]


def spot(plan: dict[str, Any], cues: list[dict[str, Any]]) -> dict[str, Any]:
    """The plan with the cues laid in place of the named shots' one-shot effects; returns a summary."""
    sound = plan.setdefault("sound", {})
    sources, placements = sound.setdefault("sources", []), sound.setdefault("placements", [])
    shots = {s["label"]: s for s in plan["shots"] if not s.get("cut")}
    clock = {k: float(s["clock_at"]) for k, s in shots.items()}
    named = {c["label"] for c in cues if c["label"] in shots}
    gone = _replaced(placements, [(clock[k], clock[k] + float(shots[k]["trim_seconds"])) for k in named])
    known = {s["id"] for s in sources}
    new = _new_sources(cues, known)
    sources += list(new.values())
    known |= set(new)
    sound["placements"] = [p for p in placements if p not in gone] + _placements(cues, clock, known)
    seconds = sum(s["duration_seconds"] for s in new.values())
    return {"shots": len(named), "removed": len(gone), "cues": sum(c.get("layer") != "none" for c in cues),
            "new_sources": len(new), "credits": round(seconds * CREDITS_PER_SECOND)}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    cues = [c for path in args.cues for c in json.loads(path.read_text(encoding="utf-8"))]
    summary = spot(plan, cues)
    print(f"Spot: {summary['cues']} cue(s) in {summary['shots']} shot(s), {summary['removed']} old effect(s) "
          f"replaced, {summary['new_sources']} new source(s) ≈ {summary['credits']} ElevenLabs credits")
    if args.dry_run:
        print("(dry run: nothing written)")
        return 0
    shutil.copy2(args.plan_file, args.plan_file.with_suffix(".json.bak"))
    args.plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
