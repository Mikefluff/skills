"""ffmpeg stage of the reel pipeline: concat → music → captions → final.mp4.

Split out of `cli/reel.py` because it is the one part with no API calls in it —
everything here is local ffmpeg work, and separating it keeps the CLI module
about orchestration rather than about video plumbing.

Every step degrades rather than aborts. A failed music mix leaves a silent reel,
a failed caption burn leaves an uncaptioned one; losing the whole render because
the last optional step failed would waste every second of generation that
preceded it.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from .. import ffmpeg as ff_mod
from .. import ffmpeg_film

if TYPE_CHECKING:
    from .reel import ReelJob


# ── stitching ───────────────────────────────────────────────────────────────


def stitch(job: "ReelJob", shots_result, music_path: Path | None) -> int:
    probe = ff_mod.detect_ffmpeg()
    if not probe.found:
        print("\nffmpeg not found — components saved; stitch skipped.", file=sys.stderr)
        print(
            "Install: 'brew install ffmpeg' (mac) or 'apt-get install -y ffmpeg' (debian).",
            file=sys.stderr,
        )
        return 0
    ffmpeg_bin = probe.binary or "ffmpeg"

    final_mp4 = job.output_dir / "final.mp4"
    if _is_film(job):
        return _stitch_film(job, shots_result, music_path, ffmpeg_bin)

    concat_mp4 = job.output_dir / "concat.mp4"
    try:
        _concat(job, shots_result, concat_mp4, ffmpeg_bin)
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg concat failed: {exc}", file=sys.stderr)
        return 1

    stitched = _mix_music(job, concat_mp4, music_path, ffmpeg_bin)
    _apply_captions(job, stitched, final_mp4, ffmpeg_bin)

    print(f"\nReel: {final_mp4}")
    print(f"Components: {job.output_dir}/(shots/, music.mp3, script.md)")
    return 0


def _is_film(job: "ReelJob") -> bool:
    plan = job.plan
    return bool(plan.get("voiceover")) or any(e.get("trim_seconds") for e in plan.get("shots") or [])


def _stitch_film(job: "ReelJob", shots_result, music_path: Path | None, ffmpeg_bin: str) -> int:
    """Trim each segment to its cut, join, lay the master voice over, duck music under it.

    The concat is the one step with no fallback: an untrimmed join would put
    every word after the first seam out of sync, which is worse than no film.
    """
    in_order = sorted(shots_result.succeeded, key=lambda it: it.index)
    cuts = [_cut(job, Path(it.output_path), it.index) for it in in_order if it.output_path]
    picture = job.output_dir / "picture.mp4"
    try:
        ffmpeg_film.concat_trimmed(cuts, picture, ffmpeg_bin=ffmpeg_bin)
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg trim/concat failed: {exc}", file=sys.stderr)
        return 1

    stitched = _film_sound(job, picture, (music_path, sum(c[1] for c in cuts)), ffmpeg_bin)

    final_mp4 = job.output_dir / "final.mp4"
    _apply_captions(job, stitched, final_mp4, ffmpeg_bin)
    print(f"\nFilm: {final_mp4}")
    print(f"Components: {job.output_dir}/(shots/, voice/, timing.json, plan.json)")
    return 0


def _cut(job: "ReelJob", path: Path, index: int) -> tuple:
    """(path, seconds) or, for a shot with a head handle, (path, seconds, trim_start)."""
    entry = next((e for e in job.plan["shots"] if int(e["index"]) == index), {})
    start = float(entry.get("trim_start") or 0)
    return (path, job.cut_seconds(index), start) if start else (path, job.cut_seconds(index))


def _film_sound(job: "ReelJob", picture: Path, music: tuple[Path | None, float], ffmpeg_bin: str) -> Path:
    """The picture with its sound: designed soundtrack, else voice (+ music bed), else silent."""
    voice = Path((job.plan.get("voiceover") or {}).get("path") or "")
    if not voice.is_file():
        if job.plan.get("voiceover"):
            print(f"\nvoiceover not found at '{voice}' — picture only.", file=sys.stderr)
        return picture
    if job.plan.get("sound"):
        return _designed_sound(job, picture, voice, ffmpeg_bin)
    music_path, seconds = music
    with_voice = job.output_dir / "with-voice.mp4"
    try:
        bed = None
        if music_path and music_path.is_file():
            opts = ff_mod.MixOptions(audio_volume=0.35, fade_out=1.0, video_seconds=seconds)
            bed = ffmpeg_film.MusicBed(music_path, opts)
        ffmpeg_film.mix_voice(picture, voice, with_voice, bed, ffmpeg_bin=ffmpeg_bin)
        return with_voice
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg voice mix failed: {exc} — picture only.", file=sys.stderr)
        return picture


def _designed_sound(job: "ReelJob", picture: Path, voice: Path, ffmpeg_bin: str) -> Path:
    """Voice + cues + effects, hits snapped to the picture, mastered, muxed. Falls back to voice only."""
    from . import _reel_sound

    soundtrack = job.output_dir / "soundtrack.wav"
    with_sound = job.output_dir / "with-sound.mp4"
    try:
        _reel_sound.render(job.plan["sound"], job.sound_sources, voice, soundtrack, picture)
        ffmpeg_film.mux(picture, soundtrack, with_sound, ffmpeg_bin=ffmpeg_bin)
        return with_sound
    except Exception as exc:  # noqa: BLE001
        print(f"\nsoundtrack mix failed: {exc} — voice only.", file=sys.stderr)
    fallback = job.output_dir / "with-voice.mp4"
    try:
        ffmpeg_film.mix_voice(picture, voice, fallback, None, ffmpeg_bin=ffmpeg_bin)
        return fallback
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg voice mix failed: {exc} — picture only.", file=sys.stderr)
        return picture


def _concat(job: "ReelJob", shots_result, concat_mp4: Path, ffmpeg_bin: str) -> None:
    # Concat must follow plan order (shot index), NOT file-finish order. Sorting
    # by filename concats by timestamp prefix, which reflects when each shot
    # finished — wrong when shots run in parallel or get retried via --resume.
    in_order = sorted(shots_result.succeeded, key=lambda it: it.index)
    paths = [Path(item.output_path) for item in in_order if item.output_path]
    if len(paths) >= 2:
        ff_mod.concat_videos(paths, concat_mp4, ffmpeg_bin=ffmpeg_bin)
    else:
        shutil.copyfile(paths[0], concat_mp4)


def _mix_music(job: "ReelJob", concat_mp4: Path, music_path: Path | None, ffmpeg_bin: str) -> Path:
    if music_path is None or not music_path.is_file():
        return concat_mp4
    with_music = job.output_dir / "with-music.mp4"
    try:
        ff_mod.mix_audio_over_video(
            concat_mp4, music_path, with_music,
            ff_mod.MixOptions(
                audio_volume=0.8, fade_out=0.5,
                video_seconds=ff_mod.get_duration(concat_mp4, ffmpeg_bin=ffmpeg_bin),
            ),
            ffmpeg_bin=ffmpeg_bin,
        )
        return with_music
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg music mix failed: {exc} — using silent reel.", file=sys.stderr)
        return concat_mp4


def _apply_captions(job: "ReelJob", stitched: Path, final_mp4: Path, ffmpeg_bin: str) -> None:
    captions = job.plan.get("captions") or []
    if not (job.plan.get("captions_enabled") and captions):
        _finalize(stitched, final_mp4)
        return
    try:
        tuples = [(float(c["start"]), float(c["end"]), str(c["text"])) for c in captions]
        ff_mod.burn_captions(stitched, tuples, final_mp4, ffmpeg_bin=ffmpeg_bin)
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg burn-captions failed: {exc} — using uncaptioned reel.", file=sys.stderr)
        _finalize(stitched, final_mp4)


def _finalize(src: Path, final_mp4: Path) -> None:
    # No transformation left between src and final.mp4 — rename instead of copy
    # so the reel dir doesn't carry two identical multi-MB files.
    if src == final_mp4:
        return
    if final_mp4.exists():
        final_mp4.unlink()
    src.replace(final_mp4)
