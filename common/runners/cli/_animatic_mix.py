"""The animatic's sound against the cut — hits snapped to the action, punchlines landed, places and vocals added.

Split out of reel_animatic; the names are re-exported there.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

from ._animatic_clips import speech

_MUSIC = ("caper_groove", "caper_bigbeat", "score_main")


def snap_to_action(sound: dict[str, Any], sources: dict[str, Path]) -> None:
    """Every designed hit that asked to be snapped moves onto the loudest onset of the shots' own sound near it."""
    from .. import soundtrack as st
    from . import _trailer_sound as ts

    stems = [(sources[p["source"]], float(p["at"]), float(p["at"]) + float(p["length"]))
             for p in sound["placements"] if p["source"].startswith("prod_")]
    for p in sound["placements"]:
        if p.get("snap"):
            # only the shot the hit sits in: a title card's impact stays on the card
            own = [(wav, a) for wav, a, b in stems if a <= float(p["at"]) < b]
            at = st.snap_time(float(p["at"]), ts.transients(own), window=0.8, floor=10.0) if own else p["at"]
            if at != p["at"]:
                print(f"  {p['source']}: {p['at']:.2f}s → {at:.2f}s, on the shot's own sound", file=sys.stderr)
            p["at"] = at


def _stop_score(kept: list[dict[str, Any]], at: float, line: float,
                resume_at: Callable[[float], float | None] | None) -> None:
    """The score stops ON the scratch: cut when it runs past it, carried up to it when it died just before."""
    for m in kept:
        a = float(m["at"])
        end = a + float(m.get("length") or 1e9)
        if not (m["source"] in _MUSIC and a < at and at - 1.5 <= end):
            continue
        m["length"] = round(at + 0.25 - a, 3)
        m["fade_out"] = 0.02
        back = resume_at(line) if resume_at else None
        if back is not None and back < end - 0.3:
            # the score comes back on the cut after the punchline, where it would have been (rule 104)
            kept.append({**m, "at": round(back, 3), "offset": round(float(m.get("offset") or 0) + back - a, 3),
                         "length": round(end - back, 3), "fade_in": 0.01, "fade_out": 0.02})


def land_punchlines(sound: dict[str, Any], lines_at: list[float], beat: float = 0.577,
                    resume_at: Any = None) -> None:
    """Rule 104 against the cut as it now stands: every record scratch sits half a beat before the first word
    of the line it introduces, the score stops dead on it, and a second scratch for the same line is dropped.

    The sound was designed against the animatic's clock; fitting the lines and recutting moved the words, so
    a scratch left where it was lands mid-sentence and the music runs on under the punchline."""
    kept, done = [], set()
    for p in sorted(sound["placements"], key=lambda x: float(x["at"])):
        if p["source"] != "record_scratch":
            kept.append(p)
            continue
        line = next((t for t in lines_at if float(p["at"]) - 0.3 <= t <= float(p["at"]) + 6.0), None)
        if line in done:
            continue  # a second scratch for the same line
        if line is None:
            kept.append(p)
            continue
        done.add(line)
        at = round(line - beat / 2 - 0.25, 3)  # the scratch's tail ends half a beat before the word
        kept.append({**p, "at": at})
        _stop_score(kept, at, line, resume_at)
    sound["placements"] = kept


def with_places(plan: dict[str, Any], bible: dict[str, Any], used: list) -> dict[str, Any]:
    """The plan's sound plus each place's bed and each rendered shot's own sound (its voice cut out).
    Files already on disk ride along under "_files" (source id → path)."""
    from . import _trailer_sound as ts

    sound = json.loads(json.dumps(plan["sound"]))
    sources, placements = ts.beds(plan, bible)
    sound["sources"] += sources
    sound["placements"] += placements
    # a sound already on disk (a riser made for an earlier cut) rides along by its path, nothing generated
    files = {src["id"]: Path(src["path"]) for src in sound["sources"] if src.get("kind") == "file" and src.get("path")}
    stems = Path(plan["output_dir"]) / "sound" / "production"
    stems.mkdir(parents=True, exist_ok=True)
    mouths = Path(plan["output_dir"]) / "shots" / "mouths.json"
    for shot, clip, start in used:
        sid = f"prod_{shot['label']}"
        span = speech(clip, mouths)  # every shot: generated words nobody wrote are noise in the mix
        files[sid] = ts.production(shot, clip, start, span, stems / f"{shot['label']}.wav")
        sound["sources"].append({"id": sid, "kind": "file"})
        sound["placements"].append(ts.production_placement(sid, shot))
    sound["_files"] = files
    return with_vocals(sound, plan, bible)


def with_vocals(sound: dict[str, Any], plan: dict[str, Any], bible: dict[str, Any]) -> dict[str, Any]:
    """The human sound of a drama pass — breaths, efforts, laughs, a crowd — in the cast's own voices, added to the
    mix of the animatic as of the cut: a comedy is judged on its giggles before any video exists."""
    if not plan.get("vocals"):
        return sound
    from . import _animatic_voice as av
    from . import _drama_pass as dp

    files = sound.setdefault("_files", {})
    voices = av.voices_for(bible, {v["who"] for v in plan["vocals"]} - {"crowd"}, [], lambda rest, lib: {})
    voiced = dp.voice(plan["vocals"], voices, Path(plan["output_dir"]))
    for n, path in voiced.items():
        files[f"vocal_{n}"] = path
        sound["sources"].append({"id": f"vocal_{n}", "kind": "file"})
    sound["placements"] += dp.placements(plan, voiced, bible)
    return sound
