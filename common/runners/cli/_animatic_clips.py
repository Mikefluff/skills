"""The rendered shots of a cut — which clip plays each shot, where its mouth opens, and how long it runs.

Split out of reel_animatic; the names are re-exported there.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _manifest_clips(out: Path) -> dict[str, Path]:
    """label → the reel manifest's succeeded output that is on disk."""
    clips = {}
    manifest = out / "manifest.json"
    if manifest.is_file():
        for item in json.loads(manifest.read_text(encoding="utf-8")).get("items") or []:
            path = Path(item.get("output_path") or "")
            if item.get("status") == "succeeded" and path.is_file():
                clips[item["label"]] = path
    return clips


def _past_rejections(plan: dict[str, Any], out: Path, clips: dict[str, Path]) -> None:
    """The take ledger knows every render: a shot whose current take was rejected falls back to its latest take
    that was not (e.g. the first Wan pass), never to a still."""
    from .. import shot_matrix

    ledger = shot_matrix.takes(plan)
    rejected = {t["file"] for t in ledger if t.get("verdict") == "rejected" or t.get("status") == "rejected"}
    for label in {t["label"] for t in ledger} | set(clips):
        path = clips.get(label)
        if path is not None and not any(str(path).endswith(f) for f in rejected):
            continue
        good = _latest_good(ledger, label, out)
        if good:
            clips[label] = good
        else:
            clips.pop(label, None)


def _latest_good(ledger: list[dict[str, Any]], label: str, out: Path) -> Path | None:
    good = [t for t in ledger if t["label"] == label and "rejected" not in (t.get("verdict"), t.get("status"))
            and (out / t["file"]).is_file()]
    return out / good[-1]["file"] if good else None


def _hd_copies(clips: dict[str, Path]) -> dict[str, Path]:
    return {k: (v.parent / "hd" / v.name if (v.parent / "hd" / v.name).is_file() else v) for k, v in clips.items()}


def rendered(plan: dict[str, Any], hd: bool | None = None) -> dict[str, Path]:
    """label → the shot's clip: its own "clip" (a composite), else the reel manifest's succeeded output; with
    "hd" in the plan, its upscaled copy (reel_upscale) wherever one exists."""
    out = Path(plan["output_dir"])
    clips = _manifest_clips(out)
    _past_rejections(plan, out, clips)
    for shot in plan["shots"]:
        if shot.get("clip"):
            clips[shot["label"]] = out / shot["clip"]
    if plan.get("hd") if hd is None else hd:
        clips = _hd_copies(clips)
    return clips


def speech(clip: Path, cache: Path) -> list[float] | None:
    """[start, end] of the clip's own voice (Scribe's first and last word), cached by file; None when silent."""
    from ..providers.elevenlabs import transcribe

    from . import _trailer_sound as ts

    seen = json.loads(cache.read_text(encoding="utf-8")) if cache.is_file() else {}
    if clip.name not in seen and not ts.has_audio(clip):
        return None  # rendered without sound (a vendor's audio filter, a bridge): no mouth to find
    if clip.name not in seen:
        wav = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(clip), "-vn", "-ac", "1", "-ar", "16000",
                              "-f", "wav", "-"], capture_output=True, check=True).stdout
        words = [w for w in transcribe(wav) if w.get("type", "word") == "word"]
        seen[clip.name] = [round(float(words[0]["start"]), 3), round(float(words[-1]["end"]), 3)] if words else None
        cache.write_text(json.dumps(seen, indent=2) + "\n", encoding="utf-8")
    return seen[clip.name]


def mouth_at(clip: Path, cache: Path) -> float | None:
    """When the clip's own voice starts its line."""
    span = speech(clip, cache)
    return span[0] if span else None


def mouth_marks(plan: dict[str, Any], clips: dict[str, Path]) -> dict[str, tuple[float, float, float]]:
    """label → (where the used window starts in the clip, where its mouth opens on the clock, how long it talks)
    for every speaking shot that is rendered. The window keeps the plan's lead-in before the mouth when the clip
    has room; the cast's line then moves to the mouth, not the mouth to the line."""
    cache = Path(plan["output_dir"]) / "shots" / "mouths.json"
    marks = {}
    for shot in plan["shots"]:
        clip = clips.get(shot["label"])
        span = speech(clip, cache) if clip and shot.get("dialogue") else None
        if not span:
            continue
        room = max(0.0, _length(clip) - float(shot["trim_seconds"]))
        start = round(min(max(0.0, span[0] - float(shot.get("line_at") or 0.3)), room), 3)
        marks[shot["label"]] = (start, round(float(shot["clock_at"]) + span[0] - start, 3), span[1] - span[0])
    return marks


def clip_start(shot: dict[str, Any], clip: Path, onset: float | None, cache: Path) -> float:
    """Where the used window starts in the clip: the plan's trim, or for a speaking shot, the moment that puts the
    clip's mouth on the cast's line (which plays `onset - clock_at` into the window)."""
    start = float(shot.get("trim_start") or 0.0)
    if onset is not None:
        mouth = mouth_at(clip, cache)
        if mouth is not None:
            start = mouth - (onset - float(shot["clock_at"]))
    room = _length(clip) - float(shot["trim_seconds"])
    return round(min(max(0.0, start), max(0.0, room)), 3)


def _length(path: Path) -> float:
    """The clip's length, probed once per version of the file."""
    from ._stage_cache import probed

    return probed(path, _probe_length)


def _probe_length(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout.strip() or 0)


def tighten(plan: dict[str, Any], ends: dict[str, float], clips: dict[str, Path] | None = None) -> dict[str, float]:
    """Speaking shots cut one beat after their last word, rounded up to whole beats; the cut after moves.
    A line that runs past its shot lengthens it, as far as its clip lasts. Returns the shots that changed."""
    from . import _trailer_retime as rt

    bpm = rt.act_bpm(plan)
    acts = rt._act_of(plan)
    lengths = {}
    for shot in plan["shots"]:
        end = ends.get(shot["label"])
        if end is None or not shot.get("dialogue"):
            continue
        beat = 60.0 / bpm.get(acts.get(shot["label"], ""), 104.0)
        need = (end - float(shot["clock_at"])) + beat
        beats = max(2, -(-need // beat))
        new = round(beats * beat, 3)
        clip = (clips or {}).get(shot["label"])
        if new > float(shot["trim_seconds"]) + 0.05 and clip:
            longest = _length(clip) - float(shot.get("trim_start") or 0) - 0.1
            new = round(min(new, (longest // beat) * beat), 3)
        if abs(new - float(shot["trim_seconds"])) > 0.05:
            lengths[shot["label"]] = new
    if lengths:
        rt.retime(plan, lengths)
        print("Tightened: " + ", ".join(f"{k} {v:.2f}s" for k, v in lengths.items()), file=sys.stderr)
    return lengths
