"""GIF-maker CLI — produce a looping GIF either from an existing MP4
or by generating a short clip via a video provider and converting.

Two modes:

  Mode A — convert existing MP4:
    gif --input clip.mp4 [--output out.gif] [--fps 12] [--width 720]
        [--start 0] [--duration 3.0] [--aspect 1:1|9:16|16:9|2:1]

  Mode B — generate then convert:
    gif --prompt "<text>" --model veo-3-1-fast [--duration 3.0]
        [--aspect 1:1|9:16|16:9|2:1] [--fps 12] [--width 720]
        [--yes] [--output out.gif]

Aspect crop is post-process: source video is center-cropped to the requested
aspect ratio, then scaled to --width (defaults: 720px for landscape, 540 for portrait/square).

ffmpeg required. If absent: prints the manual command + install instructions.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from .. import config
from .. import ffmpeg as ff_mod
from .. import output as output_mod
from ..errors import (
    CostConfirmationDeclined,
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)
from ..providers.base import JobHandle


ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "1:1": (1, 1),
    "9:16": (9, 16),
    "16:9": (16, 9),
    "4:5": (4, 5),
    "2:1": (2, 1),
    "1:2": (1, 2),
}

DEFAULT_WIDTH_BY_ASPECT: dict[str, int] = {
    "1:1": 720,
    "9:16": 540,
    "16:9": 960,
    "4:5": 600,
    "2:1": 1080,
    "1:2": 540,
}


def _crop_filter(aspect: str | None) -> str | None:
    if not aspect:
        return None
    if aspect not in ASPECT_RATIOS:
        return None
    w, h = ASPECT_RATIOS[aspect]
    # ffmpeg expression: center-crop to the requested ratio
    return f"crop='if(gt(iw/ih,{w}/{h}),ih*{w}/{h},iw)':'if(gt(iw/ih,{w}/{h}),ih,iw*{h}/{w})'"


def _convert(video: Path, output: Path, args: argparse.Namespace) -> int:
    probe = ff_mod.detect_ffmpeg()
    if not probe.found:
        print("  ✗ ffmpeg not found in PATH.", file=sys.stderr)
        print("    Install: 'brew install ffmpeg' (Mac) / 'apt-get install -y ffmpeg' (Debian).", file=sys.stderr)
        return 2

    aspect = args.aspect
    width = args.width
    if width is None and aspect:
        width = DEFAULT_WIDTH_BY_ASPECT.get(aspect, 720)
    elif width is None:
        width = 720

    # If aspect crop is requested, we need to crop before scale. ff_mod.mp4_to_gif
    # only supports fps + width via vf chain; we apply crop as a pre-pass when needed.
    crop_vf = _crop_filter(aspect) if aspect else None

    try:
        if crop_vf:
            tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            tmp.close()
            tmp_path = Path(tmp.name)
            trim_in: list[str] = []
            if args.start and args.start > 0:
                trim_in += ["-ss", f"{args.start:.3f}"]
            if args.duration and args.duration > 0:
                trim_in += ["-t", f"{args.duration:.3f}"]
            crop_cmd = [
                probe.binary or "ffmpeg", "-y", "-loglevel", "error",
                *trim_in,
                "-i", str(video),
                "-vf", crop_vf,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-an",
                str(tmp_path),
            ]
            subprocess.run(crop_cmd, check=True, capture_output=True, text=True)
            ff_mod.mp4_to_gif(
                tmp_path, output,
                fps=int(args.fps), width=width,
                ffmpeg_bin=probe.binary or "ffmpeg",
            )
            try:
                tmp_path.unlink()
            except OSError:
                pass
        else:
            ff_mod.mp4_to_gif(
                video, output,
                fps=int(args.fps), width=width,
                start=float(args.start or 0.0),
                duration=float(args.duration) if args.duration else None,
                ffmpeg_bin=probe.binary or "ffmpeg",
            )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        print(f"  ✗ ffmpeg failed: {stderr[:400] or exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"  ✗ conversion failed: {exc}", file=sys.stderr)
        return 1

    print(f"  ✓ GIF → {output}", file=sys.stderr)
    print(str(output))
    return 0


def _generate(args: argparse.Namespace) -> tuple[int, Path | None]:
    if not args.model:
        print("  ✗ --model required when generating (e.g., veo-3-1-fast, fal-video).", file=sys.stderr)
        return 2, None
    if not args.prompt:
        print("  ✗ --prompt required when generating", file=sys.stderr)
        return 2, None

    config.load_all_providers()
    try:
        provider = config.get_provider(args.model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2, None
    if provider.modality != "video":
        print(f"'{args.model}' is {provider.modality}, not video", file=sys.stderr)
        return 2, None
    if not provider.available():
        missing = ", ".join(provider.requires_env)
        print(f"missing env: {missing}", file=sys.stderr)
        return 2, None

    kwargs: dict = {}
    if args.duration:
        kwargs["duration"] = float(args.duration)
    if args.aspect and args.aspect in ASPECT_RATIOS:
        # provider may or may not honor; we still center-crop post-hoc
        kwargs["aspect"] = args.aspect

    print(
        f"Generating short clip via {args.model} (duration ~{args.duration or '?'}s) ...",
        file=sys.stderr,
    )
    try:
        result = provider.generate(args.prompt, **kwargs)
        if isinstance(result, JobHandle):
            print("  job queued, polling", end="", file=sys.stderr, flush=True)
            result = provider.poll(result, timeout=args.timeout)
            print("", file=sys.stderr)
    except KeyMissingError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2, None
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 5, None

    # Save intermediate MP4
    saved = output_mod.save(
        result.content,
        "video",
        "mp4",
        slug="gif-source",
        output_dir=Path("./generated/gif/_source"),
        mime="video/mp4",
    )
    print(f"  ✓ source MP4 → {saved.local_path}", file=sys.stderr)
    return 0, Path(saved.local_path)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.gif")
    parser.add_argument("--input", type=Path, help="path to existing MP4 (Mode A)")
    parser.add_argument("--prompt", help="prompt text for video generation (Mode B)")
    parser.add_argument("--prompt-file", type=Path, help="read prompt from file (Mode B)")
    parser.add_argument("--model", help="video provider slug (Mode B; e.g., veo-3-1-fast)")
    parser.add_argument("--output", type=Path, help="output GIF path (default: ./generated/gif/<stem>.gif)")
    parser.add_argument(
        "--aspect",
        choices=list(ASPECT_RATIOS),
        help="center-crop to this aspect ratio (default: keep source)",
    )
    parser.add_argument("--fps", type=int, default=12, help="GIF frame rate (default 12)")
    parser.add_argument("--width", type=int, help="GIF output width in px (default by aspect)")
    parser.add_argument("--start", type=float, default=0.0, help="trim start seconds")
    parser.add_argument(
        "--duration", type=float,
        help="trim length seconds (Mode A) OR target generation duration seconds (Mode B)",
    )
    parser.add_argument("--timeout", type=float, default=600.0, help="poll timeout (Mode B)")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation (Mode B)")
    args = parser.parse_args()

    if args.prompt_file and not args.prompt:
        if not args.prompt_file.is_file():
            print(f"  ✗ prompt-file not found: {args.prompt_file}", file=sys.stderr)
            return 2
        args.prompt = args.prompt_file.read_text(encoding="utf-8").strip()

    if not args.input and not args.prompt:
        print(
            "  ✗ provide either --input <mp4> (Mode A) or --prompt + --model (Mode B)",
            file=sys.stderr,
        )
        return 2

    if args.input and args.prompt:
        print(
            "  ✗ pass either --input OR --prompt+--model, not both",
            file=sys.stderr,
        )
        return 2

    source: Path
    if args.input:
        if not args.input.is_file():
            print(f"  ✗ input MP4 not found: {args.input}", file=sys.stderr)
            return 2
        source = args.input
    else:
        rc, source = _generate(args)
        if rc != 0 or source is None:
            return rc

    if args.output:
        output = args.output
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        stem = source.stem or "loop"
        out_dir = Path("./generated/gif")
        out_dir.mkdir(parents=True, exist_ok=True)
        output = out_dir / f"{stem}.gif"

    return _convert(source, output, args)


if __name__ == "__main__":
    sys.exit(main())
