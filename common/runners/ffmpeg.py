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


def mp4_to_gif(
    video: Path,
    output: Path,
    *,
    fps: int = 12,
    width: int | None = None,
    start: float = 0.0,
    duration: float | None = None,
    loop: int = 0,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Convert an MP4 to a high-quality looping GIF via 2-pass palettegen/paletteuse.

    width: scaled output width in px (keeps aspect). None = source width.
    fps: target frame rate (12-15 is good for GIFs; 24+ inflates file size).
    start / duration: optional trim window in seconds.
    loop: 0 = infinite (default), -1 = no loop, N = N+1 plays.

    Two passes:
      1. ffmpeg ... palettegen → palette.png
      2. ffmpeg ... -i palette.png paletteuse → output.gif

    Returns the second-pass command run (the visible one). Raises CalledProcessError on failure.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    palette = output.with_suffix(".palette.png")

    scale_part = f"fps={fps}"
    if width is not None and width > 0:
        scale_part += f",scale={int(width)}:-1:flags=lanczos"

    trim_in: list[str] = []
    if start and start > 0:
        trim_in += ["-ss", f"{start:.3f}"]
    if duration and duration > 0:
        trim_in += ["-t", f"{duration:.3f}"]

    # Pass 1 — palette
    pass1 = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        *trim_in,
        "-i", str(video),
        "-vf", f"{scale_part},palettegen=max_colors=256:stats_mode=diff",
        str(palette),
    ]
    subprocess.run(pass1, check=True, capture_output=True, text=True)

    # Pass 2 — apply palette
    pass2 = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        *trim_in,
        "-i", str(video),
        "-i", str(palette),
        "-filter_complex",
        f"[0:v]{scale_part}[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=5",
        "-loop", str(loop),
        str(output),
    ]
    subprocess.run(pass2, check=True, capture_output=True, text=True)

    try:
        palette.unlink()
    except OSError:
        pass

    return pass2


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
