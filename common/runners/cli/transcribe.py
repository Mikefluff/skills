"""Transcribe CLI — audio/video → SRT / VTT / JSON / plain text via OpenAI Whisper.

Closes the loop with subtitle-burner: produce subtitles → feed them in.

Supports MP3 / MP4 / MOV / WAV / WebM. Whisper API limit: 25 MB.
For larger files: split with ffmpeg or compress audio first.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import ffmpeg as ff_mod
from . import _tool
from ..errors import (
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)


RATE_PER_MINUTE = 0.006  # Whisper, USD

# Whisper's response_format names are not all file extensions.
EXTENSION_BY_FORMAT = {
    "srt": "srt", "vtt": "vtt", "json": "json", "text": "txt", "verbose_json": "json",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.transcribe")
    parser.add_argument("--input", required=True, type=Path, help="audio or video file path")
    parser.add_argument(
        "--output", type=Path,
        help="output path (default: <input-stem>.<format>)",
    )
    parser.add_argument(
        "--format", choices=list(EXTENSION_BY_FORMAT), default="srt",
        help="output format (default srt)",
    )
    parser.add_argument(
        "--lang", help="language hint (ISO-639-1 like 'en' / 'ru'); auto-detect if omitted",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.0,
        help="Whisper sampling temperature (0-1); default 0 for deterministic",
    )
    parser.add_argument("--check", action="store_true", help="verify OPENAI_API_KEY + connectivity")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument("--cost-only", action="store_true", help="print estimated cost + exit")
    return parser


def _estimate_line(duration_seconds: float | None) -> str:
    """Whisper bills by the minute, so the estimate needs the file's duration."""
    if duration_seconds is None:
        return (
            f"estimated cost: ~${RATE_PER_MINUTE}/min "
            f"(duration not detectable; install ffprobe to estimate)"
        )
    minutes = duration_seconds / 60.0
    return (
        f"duration: {duration_seconds:.1f}s ({minutes:.2f}min)\n"
        f"estimated cost: ${minutes * RATE_PER_MINUTE:.4f} (Whisper @ ${RATE_PER_MINUTE}/min)"
    )


def _write_transcript(args: argparse.Namespace, content: bytes) -> int:
    extension = EXTENSION_BY_FORMAT.get(args.format, args.format)
    output = args.output or args.input.with_suffix(f".{extension}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    print(f"  ✓ Transcribed → {output}", file=sys.stderr)
    print(str(output))
    return 0


def _transcribe_kwargs(args: argparse.Namespace, duration_minutes: float | None) -> dict:
    kwargs = {
        "file_path": str(args.input),
        "response_format": args.format,
        "temperature": float(args.temperature),
    }
    if args.lang:
        kwargs["language"] = args.lang
    if duration_minutes is not None:
        kwargs["duration_minutes"] = duration_minutes
    return kwargs


def main() -> int:
    args = build_parser().parse_args()

    if not args.input.is_file():
        print(f"  ✗ input file not found: {args.input}", file=sys.stderr)
        return 2

    provider = _tool.resolve_provider("whisper-1")
    if provider is None:
        return 2

    # Probed before the key check so --cost-only can answer without a key.
    duration_seconds = ff_mod.get_duration(args.input) or None

    early = _tool.preflight(
        provider, args,
        ready_line="OK: whisper-1 (OpenAI Whisper) configured. Run without --check to transcribe.",
        cost_line=_estimate_line(duration_seconds),
    )
    if early is not None:
        return early

    duration_label = f"{duration_seconds:.1f}s" if duration_seconds else "?"
    print(
        f"Transcribing {args.input.name} ({duration_label}) via Whisper → {args.format} ...",
        file=sys.stderr,
    )

    minutes = duration_seconds / 60.0 if duration_seconds else None
    try:
        result = provider.generate("", **_transcribe_kwargs(args, minutes))
    except KeyMissingError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 5

    return _write_transcript(args, result.content)


if __name__ == "__main__":
    sys.exit(main())
