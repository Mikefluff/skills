"""ffmpeg for voiced films — the local half of reel-builder's film mode.

A voiced film is cut against one continuous voice take. These helpers pad the
take to the film's length, slice it per segment for lip-sync references, trim
each generated segment to the exact cut, pull the frame the next segment
continues from, and lay the take back over the finished picture. The voice the
viewer hears is never the per-segment copy, so a seam in the picture is never
a seam in the speech.

Split from `ffmpeg.py`, which is about reels that have no voice to keep in sync.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .ffmpeg import MixOptions

def _run(cmd: list[str]) -> list[str]:
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cmd


def pad_audio(src: Path, output: Path, *, lead: float, total: float, ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """Silence before (`lead`) and after, to exactly `total` seconds. WAV, so slicing is sample-exact."""
    output.parent.mkdir(parents=True, exist_ok=True)
    delay_ms = int(round(lead * 1000))
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(src),
        "-af", f"adelay={delay_ms}:all=1,apad=whole_dur={total:.3f}",
        "-t", f"{total:.3f}",
        "-ar", "44100", "-ac", "1",
        str(output),
    ])


def retime(src: Path, output: Path, tempo: float, *, ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """Speed speech up or down without changing its pitch. 0.96-1.06 is inaudible as an effect."""
    output.parent.mkdir(parents=True, exist_ok=True)
    return _run([ffmpeg_bin, "-y", "-loglevel", "error", "-i", str(src), "-af", f"atempo={tempo}", str(output)])


def slice_audio(
    src: Path, output: Path, window: tuple[float, float], length: float, *, ffmpeg_bin: str = "ffmpeg"
) -> list[str]:
    """`window` = [start, end) of `src`, padded with silence to `length` — one segment's lip-sync reference."""
    start, end = window
    output.parent.mkdir(parents=True, exist_ok=True)
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
        "-i", str(src),
        "-af", f"apad=whole_dur={length:.3f}",
        "-t", f"{length:.3f}",
        str(output),
    ])


def assemble(
    src: Path, output: Path, moves: list[tuple[float, float, float, float]], length: float,
    *, ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Pieces of `src` — (start, end, place_at, tempo) — laid on silence `length` long."""
    output.parent.mkdir(parents=True, exist_ok=True)
    chains, labels = [], []
    for n, (start, end, at, tempo) in enumerate(moves):
        ms = int(round(at * 1000))
        chains.append(
            f"[0:a]atrim={start:.3f}:{end:.3f},asetpts=PTS-STARTPTS,atempo={tempo:.3f},"
            f"afade=t=in:d=0.01,areverse,afade=t=in:d=0.02,areverse,adelay={ms}:all=1[p{n}]"
        )
        labels.append(f"[p{n}]")
    graph = ";".join(chains) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad=whole_dur={length:.3f}[out]"
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error", "-i", str(src),
        "-filter_complex", graph, "-map", "[out]", "-t", f"{length:.3f}", "-ar", "44100", "-ac", "1", str(output),
    ])


def _size(video: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(video)],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        w, h = (int(x) for x in out.split(",")[:2])
    except ValueError:
        return 1080, 1920
    return w - w % 2, h - h % 2


def window_audio(src: Path, output: Path, start: float, length: float, *, ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """`length` seconds of `src` from `start`, which may be negative (silence first) — one shot's lip-sync slice."""
    output.parent.mkdir(parents=True, exist_ok=True)
    lead = max(0.0, -start)
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-ss", f"{max(0.0, start):.3f}", "-i", str(src),
        "-af", f"adelay={int(round(lead * 1000))}:all=1,apad=whole_dur={length:.3f}",
        "-t", f"{length:.3f}", "-ar", "44100", "-ac", "1",
        str(output),
    ])


def extract_frame(video: Path, output: Path, *, at: float, ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """The frame shown at `at` seconds. One frame early, so a cut at `at` never lands past the end."""
    output.parent.mkdir(parents=True, exist_ok=True)
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-ss", f"{max(0.0, at - 0.042):.3f}",
        "-i", str(video),
        "-frames:v", "1",
        str(output),
    ])


def concat_trimmed(
    shots: list[tuple[Path, float] | tuple[Path, float, float]], output: Path, *, fps: int = 24,
    ffmpeg_bin: str = "ffmpeg", audio: bool = False,
) -> list[str]:
    """Each (path, seconds[, start]) cut to [start, start + seconds), joined; picture only unless `audio`.

    `start` is the head handle of a shot generated longer than it is used: the
    first half-second of a generation is the model settling into its frame,
    and an editor cuts in after it. Re-encodes: a stream copy can only cut on
    keyframes, and a cut that drifts by half a second is a lip-sync error for
    the rest of the film. `audio` keeps each clip's own sound, cut on the same
    frames — a drama scene's dialogue is Seedance's, there is no master take.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg_bin, "-y", "-loglevel", "error"]
    chains, labels = [], []
    # Shots opened on a first frame come back at that frame's size (478x856
    # beside 480x854), and concat refuses mixed sizes: every shot is filled to
    # the first one's frame.
    w, h = _size(shots[0][0])
    fit = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    for i, (path, seconds, *rest) in enumerate(shots):
        start = rest[0] if rest else 0.0
        cmd += ["-i", str(path)]
        chains.append(
            f"[{i}:v]trim={start:.3f}:{start + seconds:.3f},setpts=PTS-STARTPTS,{fit},fps={fps},setsar=1[v{i}]"
        )
        labels.append(f"[v{i}]")
        if audio:
            chains.append(f"[{i}:a]atrim={start:.3f}:{start + seconds:.3f},asetpts=PTS-STARTPTS,"
                          f"aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
            labels.append(f"[a{i}]")
    graph = ";".join(chains) + f";{''.join(labels)}concat=n={len(shots)}:v=1:a={int(audio)}[v]" + ("[a]" if audio else "")
    maps = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k"] if audio else ["-map", "[v]", "-an"]
    cmd += [
        "-filter_complex", graph, *maps,
        "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
        str(output),
    ]
    return _run(cmd)


@dataclass(frozen=True)
class MusicBed:
    """A music track to sit under the voice, and how loud and how it ends."""

    path: Path
    opts: MixOptions = field(default_factory=lambda: MixOptions(audio_volume=0.35))


def mix_voice(
    video: Path,
    voice: Path,
    output: Path,
    music: MusicBed | None = None,
    *,
    ffmpeg_bin: str = "ffmpeg",
) -> list[str]:
    """Picture from `video`, speech from `voice`, music ducked under the speech.

    The video's own audio is dropped: Seedance re-voices the reference it was
    given, slightly differently per segment, and mixing that copy under the
    master doubles every word.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg_bin, "-y", "-loglevel", "error", "-i", str(video), "-i", str(voice)]
    if music is None:
        graph = "[1:a]anull[a]"
    else:
        cmd += ["-i", str(music.path)]
        graph = (
            "[1:a]asplit=2[key][speech];"
            f"[2:a]{music.opts.music_filter()}[m];"
            "[m][key]sidechaincompress=threshold=0.03:ratio=10:attack=15:release=350[duck];"
            "[speech][duck]amix=inputs=2:duration=first:normalize=0[a]"
        )
    cmd += [
        "-filter_complex", graph,
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output),
    ]
    return _run(cmd)


def render_mix(inputs: list[str], graph: str, output: Path, *, ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """Run a soundtrack graph from `soundtrack.build_graph` into a 48 kHz WAV."""
    output.parent.mkdir(parents=True, exist_ok=True)
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error", *inputs,
        "-filter_complex", graph, "-map", "[out]",
        "-ar", "48000", "-c:a", "pcm_s16le",
        str(output),
    ])


def extract_audio(video: Path, output: Path, *, start: float = 0.0, length: float | None = None,
                  ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """A clip's sound, 48 kHz, WAV or MP3 by the output's suffix, optionally only [start, start + length)."""
    output.parent.mkdir(parents=True, exist_ok=True)
    window = ["-ss", f"{start:.3f}"] + (["-t", f"{length:.3f}"] if length else [])
    codec = ["-c:a", "libmp3lame", "-b:a", "128k"] if output.suffix == ".mp3" else ["-c:a", "pcm_s16le"]
    return _run([ffmpeg_bin, "-y", "-loglevel", "error", *window, "-i", str(video),
                 "-vn", "-ar", "48000", *codec, str(output)])


def mux(picture: Path, audio: Path, output: Path, *, ffmpeg_bin: str = "ffmpeg") -> list[str]:
    """Picture from one file, sound from another; nothing re-encoded but the audio."""
    output.parent.mkdir(parents=True, exist_ok=True)
    return _run([
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(picture), "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-shortest",
        str(output),
    ])


def luma_series(video: Path) -> list[tuple[float, float]]:
    """(time, mean luma 0-255) per frame — where the flashes and ignitions actually are."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-f", "lavfi",
            "-i", f"movie={_lavfi_path(video)},signalstats",
            "-show_entries", "frame=pts_time:frame_tags=lavfi.signalstats.YAVG",
            "-of", "csv=p=0",
        ],
        check=True, capture_output=True, text=True,
    ).stdout
    series = []
    for line in out.splitlines():
        parts = line.split(",")
        if len(parts) >= 2 and parts[0] and parts[1]:
            series.append((float(parts[0]), float(parts[1])))
    return series


def _lavfi_path(path: Path) -> str:
    # movie= takes a filter argument, where ':' ',' and '\' are syntax.
    return str(path.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace(",", "\\,").replace("'", "\\'")
