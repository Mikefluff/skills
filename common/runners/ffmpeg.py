"""ffmpeg wrappers — concat shots, mix audio, burn captions.

Pure subprocess. No pip dep. Skill degrades gracefully if ffmpeg is missing:
detect_ffmpeg() returns None and the caller prints the assembled command for
the user to run manually.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass
class FfmpegProbe:
    found: bool
    binary: str | None = None
    version: str | None = None


# ── option objects ───────────────────────────────────────────────────────
# These signatures had grown into bags of six to nine keyword arguments, which
# is how "audio_volume" and "duck_amount" end up passed positionally by a
# caller in a hurry. Frozen, so they are safe as default arguments.


@dataclass(frozen=True)
class MixOptions:
    """How a music track sits against a video's existing audio.

    mode:
      replace — drop the original audio, music becomes the only track
      overlay — mix music on top of the original, both audible
      duck    — overlay, but sidechain-compressed so music drops under speech

    duck_amount attenuates the music while ducking: 0.0 mutes it, 1.0 is no
    ducking at all.
    """

    mode: str = "replace"
    audio_volume: float = 0.8
    fade_in: float = 0.0
    fade_out: float = 0.5
    duck_amount: float = 0.6

    def music_filter(self) -> str:
        """The -af chain applied to the music input before mixing."""
        parts = [f"volume={self.audio_volume}"]
        if self.fade_in > 0:
            parts.append(f"afade=t=in:st=0:d={self.fade_in}")
        if self.fade_out > 0:
            parts.append(f"afade=t=out:st=0:d={self.fade_out}")
        return ",".join(parts)


@dataclass(frozen=True)
class CaptionStyle:
    font_size: int = 48
    font_color: str = "white"
    box_color: str = "black@0.6"


@dataclass(frozen=True)
class GifOptions:
    """fps 12-15 reads well; 24+ inflates the file for no visible gain.

    width scales the output in px, keeping aspect; None keeps the source width.
    start / duration trim in seconds. loop: 0 is infinite, -1 never repeats,
    N plays N+1 times.
    """

    fps: int = 12
    width: int | None = None
    start: float = 0.0
    duration: float | None = None
    loop: int = 0

    def scale_filter(self) -> str:
        chain = f"fps={self.fps}"
        if self.width is not None and self.width > 0:
            chain += f",scale={int(self.width)}:-1:flags=lanczos"
        return chain

    def trim_args(self) -> list[str]:
        args: list[str] = []
        if self.start and self.start > 0:
            args += ["-ss", f"{self.start:.3f}"]
        if self.duration and self.duration > 0:
            args += ["-t", f"{self.duration:.3f}"]
        return args


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
    opts: MixOptions = MixOptions(),
    *,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Replace the audio track of a video with a music file.

    The video's existing audio is REPLACED — -map 0:v plus -map 1:a. To keep
    diegetic sound, use mix_audio_with_modes() with overlay or duck.
    """
    return mix_audio_with_modes(
        video, audio, output,
        replace(opts, mode="replace"),
        ffmpeg_bin=ffmpeg_bin,
    )


def _replace_cmd(video: Path, audio: Path, output: Path, opts: MixOptions, ffmpeg_bin: str) -> list[str]:
    return [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-af", opts.music_filter(),
        "-shortest",
        str(output),
    ]


def _mixed_cmd(video: Path, audio: Path, output: Path, graph: str, ffmpeg_bin: str) -> list[str]:
    """Shared tail for the two modes that keep the original audio."""
    return [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(video),
        "-i", str(audio),
        "-filter_complex", graph,
        "-map", "0:v",
        "-map", "[mix]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output),
    ]


def mix_audio_with_modes(
    video: Path,
    audio: Path,
    output: Path,
    opts: MixOptions = MixOptions(),
    *,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Mix a music track onto a video. See MixOptions for the three modes."""
    if opts.mode not in ("replace", "overlay", "duck"):
        raise ValueError(f"mode must be replace/overlay/duck, got {opts.mode}")
    output.parent.mkdir(parents=True, exist_ok=True)

    music = opts.music_filter()
    if opts.mode == "replace":
        cmd = _replace_cmd(video, audio, output, opts, ffmpeg_bin)
    elif opts.mode == "overlay":
        graph = (
            f"[1:a]{music}[music];"
            f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[mix]"
        )
        cmd = _mixed_cmd(video, audio, output, graph, ffmpeg_bin)
    else:
        # Sidechain compressor: the original audio (0:a) ducks the music (1:a).
        graph = (
            f"[1:a]{music}[music];"
            f"[music][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300:makeup=1[ducked];"
            f"[0:a][ducked]amix=inputs=2:duration=first:weights={1.0} {opts.duck_amount}[mix]"
        )
        cmd = _mixed_cmd(video, audio, output, graph, ffmpeg_bin)

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cmd


def _drawtext_chain(captions: list[tuple[float, float, str]], style: CaptionStyle) -> str:
    """One drawtext filter per cue, each gated to its own time window."""
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
            f"fontcolor={style.font_color}:fontsize={style.font_size}:"
            f"box=1:boxcolor={style.box_color}:boxborderw=20:"
            f"x=(w-text_w)/2:y=h-(text_h*2.5):"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )
    return ",".join(parts)


def burn_captions(
    video: Path,
    captions: list[tuple[float, float, str]],
    output: Path,
    style: CaptionStyle = CaptionStyle(),
    *,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Burn timed (start_seconds, end_seconds, text) captions onto a video."""
    if not captions:
        # Nothing to draw — stream-copy so the caller still gets an output file.
        cmd = [
            ffmpeg_bin, "-y", "-loglevel", "error",
            "-i", str(video),
            "-c", "copy",
            str(output),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return cmd

    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(video),
        "-vf", _drawtext_chain(captions, style),
        "-c:a", "copy",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cmd


def mp4_to_gif(
    video: Path,
    output: Path,
    opts: GifOptions = GifOptions(),
    *,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Convert an MP4 to a looping GIF via 2-pass palettegen / paletteuse.

    A GIF is limited to 256 colours, so the palette is generated from the
    actual frames first and applied second — one pass produces visible banding.

    Returns the second-pass command (the visible one). Raises
    CalledProcessError on failure.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    palette = output.with_suffix(".palette.png")
    scale = opts.scale_filter()
    trim = opts.trim_args()

    pass1 = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        *trim,
        "-i", str(video),
        "-vf", f"{scale},palettegen=max_colors=256:stats_mode=diff",
        str(palette),
    ]
    subprocess.run(pass1, check=True, capture_output=True, text=True)

    pass2 = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        *trim,
        "-i", str(video),
        "-i", str(palette),
        "-filter_complex",
        f"[0:v]{scale}[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=5",
        "-loop", str(opts.loop),
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
