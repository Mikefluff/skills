"""ffmpeg wrappers — concat shots, mix audio, burn captions.

Pure subprocess. No pip dep. Skill degrades gracefully if ffmpeg is missing:
detect_ffmpeg() returns None and the caller prints the assembled command for
the user to run manually.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FfmpegProbe:
    found: bool
    binary: str | None = None
    version: str | None = None


def detect_ffmpeg() -> FfmpegProbe:
    binary = shutil.which("ffmpeg")
    if not binary:
        return FfmpegProbe(found=False)
    try:
        out = subprocess.run(
            [binary, "-version"], check=True, capture_output=True, text=True, timeout=10
        )
        version_line = out.stdout.splitlines()[0] if out.stdout else ""
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        version_line = ""
    return FfmpegProbe(found=True, binary=binary, version=version_line)


def _quote(path: str) -> str:
    return "'" + path.replace("'", "'\\''") + "'"


def concat_videos(
    shot_paths: list[Path], output: Path, *, ffmpeg_bin: str = "ffmpeg"
) -> list[str]:
    """Concat 2+ shots into a single mp4 using the concat demuxer (no re-encode if codecs match).

    Returns the command run as a list (for logging). Raises CalledProcessError on failure.
    If ffmpeg is not on PATH, callers should print the command and skip.
    """
    if len(shot_paths) < 2:
        raise ValueError("concat_videos needs at least 2 shots")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Write concat list to a sibling temp file
    list_file = output.with_suffix(".concat.txt")
    list_file.write_text(
        "\n".join(f"file {_quote(str(p.resolve()))}" for p in shot_paths) + "\n",
        encoding="utf-8",
    )
    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cmd


def mix_audio_over_video(
    video: Path,
    audio: Path,
    output: Path,
    *,
    audio_volume: float = 0.8,
    fade_out: float = 0.5,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Replace (or overlay) the audio track of a video with a music file.

    The video's existing audio is REPLACED — we use -map 0:v + -map 1:a. For
    overlay/duck behaviour (keeping diegetic sound), use mix_audio_with_duck().
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    af = f"volume={audio_volume},afade=out:st=0:d=0:enable='lt(t,0)'"
    # Add a tail fade-out matching the video length minus fade_out
    # (we ignore complex sync — for v1 keep it simple).
    af_filter = f"volume={audio_volume},afade=t=out:st=0:d={fade_out}"
    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-af", af_filter,
        "-shortest",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cmd


def burn_captions(
    video: Path,
    captions: list[tuple[float, float, str]],
    output: Path,
    *,
    ffmpeg_bin: str = "ffmpeg",
    font_size: int = 48,
    font_color: str = "white",
    box_color: str = "black@0.6",
) -> list[str]:
    """Burn timed captions onto a video via drawtext filter.

    captions: list of (start_seconds, end_seconds, text) tuples.
    """
    if not captions:
        # No captions — just copy
        cmd = [
            ffmpeg_bin, "-y", "-loglevel", "error",
            "-i", str(video),
            "-c", "copy",
            str(output),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return cmd

    output.parent.mkdir(parents=True, exist_ok=True)
    parts: list[str] = []
    for start, end, text in captions:
        escaped = (
            text.replace("\\", "\\\\")
                .replace("'", "’")
                .replace(":", "\\:")
                .replace(",", "\\,")
        )
        parts.append(
            f"drawtext=text='{escaped}':"
            f"fontcolor={font_color}:fontsize={font_size}:"
            f"box=1:boxcolor={box_color}:boxborderw=20:"
            f"x=(w-text_w)/2:y=h-(text_h*2.5):"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )
    vf = ",".join(parts)
    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(video),
        "-vf", vf,
        "-c:a", "copy",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cmd


def get_duration(path: Path, *, ffmpeg_bin: str = "ffmpeg") -> float | None:
    """Return media duration in seconds via ffprobe-style probe with ffmpeg."""
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True, capture_output=True, text=True, timeout=20,
        )
        return float(out.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, OSError):
        return None
