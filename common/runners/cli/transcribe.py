"""Transcribe CLI — audio/video → SRT / VTT / JSON / plain text via OpenAI Whisper.

Closes the loop with subtitle-burner: produce subtitles → feed them in.

Supports MP3 / MP4 / MOV / WAV / WebM. Whisper API limit: 25 MB.
For larger files: split with ffmpeg or compress audio first.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import config
from .. import ffmpeg as ff_mod
from ..errors import (
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.transcribe")
    parser.add_argument("--input", required=True, type=Path, help="audio or video file path")
    parser.add_argument(
        "--output", type=Path,
        help="output path (default: <input-stem>.<format>)",
    )
    parser.add_argument(
        "--format", choices=["srt", "vtt", "json", "text", "verbose_json"], default="srt",
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
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"  ✗ input file not found: {args.input}", file=sys.stderr)
        return 2

    config.load_all_providers()
    try:
        provider = config.get_provider("whisper-1")
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check:
        if not provider.available():
            missing = ", ".join(provider.requires_env)
            print(f"missing env: {missing}", file=sys.stderr)
            return 2
        print("OK: whisper-1 (OpenAI Whisper) configured. Run without --check to transcribe.")
        return 0

    # Estimate cost: $0.006/min. Probe duration via ffprobe.
    duration_seconds = ff_mod.get_duration(args.input)
    duration_minutes = (duration_seconds or 0) / 60.0 if duration_seconds else None

    if args.cost_only:
        if duration_minutes is not None:
            est = duration_minutes * 0.006
            print(f"duration: {duration_seconds:.1f}s ({duration_minutes:.2f}min)")
            print(f"estimated cost: ${est:.4f} (Whisper @ $0.006/min)")
        else:
            print("estimated cost: ~$0.006/min (duration not detectable; install ffprobe to estimate)")
        return 0

    if not provider.available():
        missing = ", ".join(provider.requires_env)
        print(f"missing env: {missing}", file=sys.stderr)
        return 2

    kwargs = {
        "file_path": str(args.input),
        "response_format": args.format,
        "temperature": float(args.temperature),
    }
    if args.lang:
        kwargs["language"] = args.lang
    if duration_minutes is not None:
        kwargs["duration_minutes"] = duration_minutes

    duration_label = f"{duration_seconds:.1f}s" if duration_seconds else "?"
    print(
        f"Transcribing {args.input.name} ({duration_label}) via Whisper → {args.format} ...",
        file=sys.stderr,
    )

    try:
        result = provider.generate("", **kwargs)
    except KeyMissingError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 5

    ext_map = {"srt": "srt", "vtt": "vtt", "json": "json", "text": "txt", "verbose_json": "json"}
    extension = ext_map.get(args.format, args.format)
    output = args.output or args.input.with_suffix(f".{extension}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result.content)

    print(f"  ✓ Transcribed → {output}", file=sys.stderr)
    print(str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
