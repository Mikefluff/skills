"""Audio-mix CLI — mix a music track onto an existing video via ffmpeg.

Modes:
  - replace (default): drop the video's original audio, use music as sole audio track
  - overlay: mix music ON TOP of original audio (both audible)
  - duck: like overlay but music auto-attenuates when speech is present (sidechain compressor)

ffmpeg required. No API calls — pure ffmpeg.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import ffmpeg as ff_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.mix")
    parser.add_argument("--video", type=Path, required=True, help="input video path")
    parser.add_argument("--audio", type=Path, required=True, help="input music/audio path")
    parser.add_argument(
        "--output", type=Path,
        help="output path (default: <video-stem>-mixed<ext>)",
    )
    parser.add_argument(
        "--mode", choices=["replace", "overlay", "duck"], default="replace",
        help="replace = drop original audio; overlay = mix both; duck = sidechain duck music under speech",
    )
    parser.add_argument(
        "--volume", type=float, default=0.8,
        help="music volume multiplier (0.0-2.0; default 0.8)",
    )
    parser.add_argument(
        "--fade-in", type=float, default=0.0,
        help="fade in duration in seconds (default 0)",
    )
    parser.add_argument(
        "--fade-out", type=float, default=0.5,
        help="fade out duration in seconds (default 0.5)",
    )
    parser.add_argument(
        "--duck-amount", type=float, default=0.6,
        help="duck mode: how much music attenuates when speech present (0.0-1.0; default 0.6)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.video.is_file():
        print(f"  ✗ video not found: {args.video}", file=sys.stderr)
        return 2
    if not args.audio.is_file():
        print(f"  ✗ audio not found: {args.audio}", file=sys.stderr)
        return 2

    probe = ff_mod.detect_ffmpeg()
    if not probe.found:
        print("  ✗ ffmpeg not found in PATH.", file=sys.stderr)
        print("    Install: 'brew install ffmpeg' (Mac) / 'apt-get install -y ffmpeg' (Debian).", file=sys.stderr)
        return 2

    output = args.output or args.video.with_name(f"{args.video.stem}-mixed{args.video.suffix}")

    print(
        f"  Mixing {args.audio.name} onto {args.video.name} (mode={args.mode}, volume={args.volume})",
        file=sys.stderr,
    )
    print(f"  Output: {output}", file=sys.stderr)

    try:
        ff_mod.mix_audio_with_modes(
            args.video, args.audio, output,
            ff_mod.MixOptions(
                mode=args.mode,
                audio_volume=float(args.volume),
                fade_in=float(args.fade_in),
                fade_out=float(args.fade_out),
                duck_amount=float(args.duck_amount),
            ),
            ffmpeg_bin=probe.binary or "ffmpeg",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  ✗ ffmpeg mix failed: {exc}", file=sys.stderr)
        return 1

    print(f"\n  ✓ Mixed: {output}", file=sys.stderr)
    print(str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
