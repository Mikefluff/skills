"""Subtitle burner CLI — burn captions onto an existing MP4 via ffmpeg.

Subcommands:

  burn <video> <subtitle-source> [--output <path>] [--font-size N]
       [--font-color white] [--box-color "black@0.6"] [--style modern|minimal|bold]

  preview <video> <subtitle-source>    # parse + print cue list, don't burn

Subtitle sources:
  *.srt / *.vtt → standard parsers
  *.txt        → evenly-distributed plain text (requires --video-duration via ffprobe auto-detect)
  --inline "text"  → one-cue burn-on-whole-video

ffmpeg required. If absent: prints install instructions + the manual command.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .. import ffmpeg as ff_mod
from .. import subtitles as subs_mod


STYLE_PRESETS: dict[str, dict[str, str | int]] = {
    "modern": {"font_size": 48, "font_color": "white", "box_color": "black@0.6"},
    "minimal": {"font_size": 42, "font_color": "white", "box_color": "black@0"},
    "bold": {"font_size": 56, "font_color": "yellow", "box_color": "black@0.85"},
}


def _cues_from_file(subtitle: Path, video: Path) -> list[subs_mod.Cue] | None:
    """Parse a subtitle file. None means the caller should exit 2."""
    if not subtitle.is_file():
        print(f"  ✗ subtitle file not found: {subtitle}", file=sys.stderr)
        return None

    if subtitle.suffix.lower() != ".txt":
        return subs_mod.parse_file(subtitle)

    # Plain text carries no timings, so they are distributed across the video's
    # duration. Without a duration there is nothing to distribute over, and
    # guessing one would desync every cue.
    duration = ff_mod.get_duration(video)
    if duration is None:
        print(
            "  ✗ couldn't probe video duration (ffprobe missing?). "
            "Use --inline or .srt / .vtt instead.",
            file=sys.stderr,
        )
        return None
    return subs_mod.parse_plain_text(
        subtitle.read_text(encoding="utf-8"), video_duration=duration, gap_seconds=0.2
    )


def _resolve_cues(args: argparse.Namespace) -> list[subs_mod.Cue] | None:
    """--inline or --subtitle into cues. None means the caller should exit 2."""
    if args.inline:
        # One caption spanning the whole video. 9999s is the fallback when the
        # real duration cannot be probed — ffmpeg clamps it to the video anyway.
        duration = ff_mod.get_duration(args.video) or 9999.0
        return [subs_mod.Cue(start=0.0, end=duration, text=args.inline)]
    return _cues_from_file(args.subtitle, args.video)


def _caption_style(args: argparse.Namespace) -> ff_mod.CaptionStyle:
    """A preset, with any explicit flag overriding its fields."""
    preset = STYLE_PRESETS.get(args.style, STYLE_PRESETS["modern"])
    return ff_mod.CaptionStyle(
        font_size=int(args.font_size or preset["font_size"]),
        font_color=str(args.font_color or preset["font_color"]),
        box_color=str(args.box_color or preset["box_color"]),
    )


def _cmd_burn(args: argparse.Namespace) -> int:
    video = args.video
    if not video.is_file():
        print(f"  ✗ video file not found: {video}", file=sys.stderr)
        return 2

    cues = _resolve_cues(args)
    if cues is None:
        return 2
    if not cues:
        print("  ✗ no cues parsed from subtitle source", file=sys.stderr)
        return 2

    probe = ff_mod.detect_ffmpeg()
    if not probe.found:
        print("  ✗ ffmpeg not found in PATH.", file=sys.stderr)
        print("    Install: 'brew install ffmpeg' (Mac) / 'apt-get install -y ffmpeg' (Debian).", file=sys.stderr)
        return 2

    output = args.output or video.with_name(f"{video.stem}-subtitled{video.suffix}")
    style = _caption_style(args)

    print(f"  Burning {len(cues)} cue(s) into {video}", file=sys.stderr)
    print(f"  Output: {output}", file=sys.stderr)
    print(
        f"  Style: {args.style} "
        f"(font_size={style.font_size}, color={style.font_color})",
        file=sys.stderr,
    )

    try:
        ff_mod.burn_captions(
            video,
            subs_mod.cues_to_tuples(cues),
            output,
            style,
            ffmpeg_bin=probe.binary or "ffmpeg",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  ✗ ffmpeg burn failed: {exc}", file=sys.stderr)
        return 1

    print(f"\nBurned: {output}", file=sys.stderr)
    print(str(output))
    return 0


def _cmd_preview(args: argparse.Namespace) -> int:
    if args.inline:
        print(f"  cue 1:  0.00s → ?  →  {args.inline}")
        return 0
    if not args.subtitle or not args.subtitle.is_file():
        print(f"  ✗ subtitle file not found: {args.subtitle}", file=sys.stderr)
        return 2

    if args.subtitle.suffix.lower() == ".txt":
        if not args.video or not args.video.is_file():
            print(f"  ✗ for plain .txt, pass the --video too (to compute timing)", file=sys.stderr)
            return 2
        duration = ff_mod.get_duration(args.video)
        if duration is None:
            print(f"  ✗ couldn't probe duration; install ffprobe or use .srt/.vtt", file=sys.stderr)
            return 2
        text = args.subtitle.read_text(encoding="utf-8")
        cues = subs_mod.parse_plain_text(text, video_duration=duration, gap_seconds=0.2)
    else:
        cues = subs_mod.parse_file(args.subtitle)

    if not cues:
        print("  (no cues parsed)", file=sys.stderr)
        return 1
    print(f"# {len(cues)} cue(s) parsed from {args.subtitle}")
    print()
    for i, cue in enumerate(cues, 1):
        print(f"  {i:>3}. {cue.start:>7.2f}s → {cue.end:>7.2f}s  ({cue.end - cue.start:>5.2f}s)  {cue.text}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="common.runners.cli.subtitle",
        description="Burn captions onto an existing MP4 via ffmpeg.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_burn = sub.add_parser("burn", help="burn captions onto video")
    p_burn.add_argument("video", type=Path)
    group = p_burn.add_mutually_exclusive_group(required=True)
    group.add_argument("--subtitle", type=Path, help="SRT / VTT / TXT subtitle file")
    group.add_argument("--inline", help="single caption text for the entire video")
    p_burn.add_argument("--output", type=Path, help="output path (default: <video>-subtitled<ext>)")
    p_burn.add_argument("--style", choices=list(STYLE_PRESETS), default="modern", help="visual style preset")
    p_burn.add_argument("--font-size", type=int)
    p_burn.add_argument("--font-color")
    p_burn.add_argument("--box-color")
    p_burn.set_defaults(func=_cmd_burn)

    p_preview = sub.add_parser("preview", help="parse subtitle source + print cues")
    group2 = p_preview.add_mutually_exclusive_group(required=True)
    group2.add_argument("--subtitle", type=Path)
    group2.add_argument("--inline")
    p_preview.add_argument("--video", type=Path, help="needed only when subtitle is a .txt file (for timing)")
    p_preview.set_defaults(func=_cmd_preview)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
