"""Seams of a voiced film: what each segment is handed from the one before, and
which stretch of the master take each lip-synced shot is handed to mouth.

Split out of `cli/reel.py` for the same reason as `_reel_stitch`: this is media
plumbing (pull a frame, attach it as a reference), not orchestration.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .. import batch as batch_mod
from .. import ffmpeg_film
from ..errors import RunnerError

if TYPE_CHECKING:
    from .reel import ReelJob


def _seam_frame(job: "ReelJob", prev: batch_mod.BatchItem, entry: dict[str, Any]) -> Path:
    """The frame the next segment is handed, taken from `prev`.

    At the cut by default, not at the end of the clip: the clip overshoots to a
    whole second and the overshoot never reaches the film. A designed seam
    (whiteout, black) has nothing usable at the cut, so the plan can point at
    an earlier frame that still shows the layout.
    """
    frame = job.shots_dir / f"seam-{prev.index:02d}.png"
    at = entry.get("seam_frame_at") or job.cut_seconds(prev.index)
    ffmpeg_film.extract_frame(Path(prev.output_path), frame, at=float(at))
    return frame


def _attach(item: batch_mod.BatchItem, frame: Path, mode: str) -> None:
    if mode == "first_frame":
        item.kwargs["first_frame"] = str(frame)
        return
    refs = list(item.kwargs.get("reference_images") or [])
    if str(frame) not in refs:
        # Always last, so the prompt can name it: @Image{len(refs)+1}.
        refs.append(str(frame))
    item.kwargs["reference_images"] = refs


def seam_hook(job: "ReelJob"):
    """Before a chained segment generates, hand it a frame from its predecessor."""
    by_index = {item.index: item for item in job.shot_items}
    entries = {int(e["index"]): e for e in job.plan["shots"]}
    order = sorted(by_index)
    mode = job.plan.get("continuity") or "reference"

    def hook(item: batch_mod.BatchItem) -> None:
        entry = entries[item.index]
        if not entry.get("continue_from_previous"):
            return
        pos = order.index(item.index)
        prev = by_index[order[pos - 1]] if pos else None
        if prev is None or prev.status != "succeeded" or not prev.output_path:
            raise RunnerError(f"{item.label}: previous segment did not succeed; nothing to continue from")
        _attach(item, _seam_frame(job, prev, entry), mode)

    return hook


def _shot_label(entry: dict[str, Any]) -> str:
    return entry.get("label") or f"shot-{int(entry['index']):02d}"


def _slice_voice(voice: Path, entry: dict[str, Any], film_at: float, output_dir: Path) -> None:
    kwargs = entry["kwargs"]
    out = output_dir / "voice" / f"{_shot_label(entry)}.wav"
    length = float(kwargs.get("duration_seconds") or 5)
    ffmpeg_film.window_audio(voice, out, film_at - float(entry.get("trim_start") or 0), length)
    kwargs["reference_audio"] = [str(out)]


def lip_slices(plan: dict[str, Any], output_dir: Path) -> None:
    """Give every `lip_sync` shot the stretch of the master take its picture will carry.

    In a film cut from one generation per shot, shot i starts on the film clock
    at the sum of the earlier cuts, and its clip time 0 sits `trim_start` before
    that. The slice is taken from there for the whole generation, so the words
    the model mouths at clip time t are the words the master has at that moment
    of the cut film. Shots without `lip_sync` get no audio: their lines are
    voice-over and their mouths stay shut.
    """
    voice = Path((plan.get("voiceover") or {}).get("path") or "")
    shots = sorted(plan.get("shots") or [], key=lambda e: int(e["index"]))
    if not voice.is_file() or not any(e.get("lip_sync") for e in shots):
        return
    film_at = 0.0
    for entry in shots:
        kwargs = entry.setdefault("kwargs", {})
        if entry.get("lip_sync"):
            _slice_voice(voice, entry, film_at, output_dir)
        film_at += float(entry.get("trim_seconds") or kwargs.get("duration_seconds") or 5)
