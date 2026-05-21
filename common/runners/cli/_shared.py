"""Shared CLI plumbing — argparse skeleton, validation, dispatch, output."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .. import cost as cost_mod
from .. import output as output_mod
from .. import config
from ..errors import (
    CostConfirmationDeclined,
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)
from ..providers.base import JobHandle, Modality


def build_parser(modality: Modality, models_hint: list[str] | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"common.runners.cli.{modality}",
        description=f"Optional execution layer for {modality} generation.",
    )
    parser.add_argument("--model", "--provider", dest="model", help="provider slug")
    parser.add_argument("--prompt", help="prompt text")
    parser.add_argument("--prompt-file", type=Path, help="read prompt from file")
    parser.add_argument("--output", type=Path, help=f"output dir (default: ./generated/{modality}/)")
    parser.add_argument("--variants", type=int, default=1)
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument("--check", action="store_true", help="dry-run availability check, no generation")
    parser.add_argument("--list-providers", action="store_true", help="list providers available given current env")
    parser.add_argument("--cost-only", action="store_true", help="print estimated cost without generating")
    parser.add_argument("--timeout", type=float, default=600.0, help="poll timeout seconds (async vendors)")
    # passthrough free-form kwargs
    parser.add_argument("--duration", type=float, help="seconds (video) or minutes (music)")
    parser.add_argument("--lyrics", help="lyrics text (music)")
    parser.add_argument("--lyrics-file", type=Path, help="lyrics from file (music)")
    parser.add_argument("--instrumental", action="store_true", help="instrumental music (no lyrics)")
    parser.add_argument("--image-url", help="reference image URL (i2v / edit)")
    parser.add_argument("--video-url", help="reference video URL (v2v)")
    parser.add_argument("--size", help='image size like "1024x1024"')
    parser.add_argument("--quality", help='image quality: low/medium/high')
    parser.add_argument("--voice", help="voice id (TTS)")
    parser.add_argument("--fal-model", help="override fal.ai hosted model id")
    parser.add_argument("--replicate-model", help="override Replicate model id")
    if models_hint:
        parser.epilog = "Common models: " + ", ".join(models_hint)
    return parser


def list_providers(modality: Modality) -> int:
    config.load_all_providers()
    all_for_mod = config.all_providers(modality)
    if not all_for_mod:
        print(f"No {modality} providers registered.", file=sys.stderr)
        return 1
    print(f"{modality.title()} providers:")
    for p in all_for_mod:
        mark = "available" if p.available() else "missing env"
        missing = "" if p.available() else f"  set: {', '.join(p.requires_env)}"
        print(f"  - {p.name:30s} {mark}{missing}")
    return 0


def check_provider(model: str, modality: Modality) -> int:
    config.load_all_providers()
    try:
        provider = config.get_provider(model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if provider.modality != modality:
        print(
            f"provider '{model}' is {provider.modality}, not {modality}. "
            f"Use 'python3 -m common.runners.cli.{provider.modality} --check --model {model}'.",
            file=sys.stderr,
        )
        return 2
    if not provider.available():
        missing = [k for k in provider.requires_env if not __import__("os").environ.get(k)]
        print(f"missing env: {', '.join(missing)}", file=sys.stderr)
        return 2
    print(f"OK: {model} configured (env set). Run without --check to generate.")
    return 0


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return args.prompt_file.read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("No prompt. Pass --prompt '...' or --prompt-file <path> or pipe via stdin.")


def gather_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Pack passthrough kwargs into a dict the provider's generate() accepts."""
    kwargs: dict[str, Any] = {"variants": args.variants}
    if args.duration is not None:
        kwargs["duration_seconds"] = args.duration
        kwargs["duration_minutes"] = args.duration
    if args.lyrics is not None:
        kwargs["lyrics"] = args.lyrics
    if args.lyrics_file and not args.lyrics:
        kwargs["lyrics"] = args.lyrics_file.read_text(encoding="utf-8")
    if args.instrumental:
        kwargs["instrumental"] = True
    if args.image_url:
        kwargs["image_url"] = args.image_url
    if args.video_url:
        kwargs["video_url"] = args.video_url
    if args.size:
        kwargs["size"] = args.size
    if args.quality:
        kwargs["quality"] = args.quality
    if args.voice:
        kwargs["voice"] = args.voice
    if args.fal_model:
        kwargs["fal_model"] = args.fal_model
    if args.replicate_model:
        kwargs["replicate_model"] = args.replicate_model
    return kwargs


def dispatch(modality: Modality, models_hint: list[str] | None = None) -> int:
    parser = build_parser(modality, models_hint)
    args = parser.parse_args()

    if args.list_providers:
        return list_providers(modality)

    if not args.model:
        parser.error("missing --model. Use --list-providers to see options.")

    if args.check:
        return check_provider(args.model, modality)

    config.load_all_providers()
    try:
        provider = config.get_provider(args.model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if provider.modality != modality:
        print(
            f"provider '{args.model}' is {provider.modality}, not {modality}.",
            file=sys.stderr,
        )
        return 2

    prompt = read_prompt(args)
    kwargs = gather_kwargs(args)

    estimated = provider.estimate_cost(**kwargs)
    if args.cost_only:
        print(f"estimated cost: {cost_mod.format_cost(estimated)}")
        return 0

    try:
        cost_mod.confirm(estimated, yes=args.yes)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    try:
        provider.ensure_available()
    except KeyMissingError as exc:
        # fall back to prompt-only
        saved = output_mod.save_prompt_only(
            prompt, modality, slug=args.model, output_dir=args.output, reason=str(exc)
        )
        print(saved.display())
        return 4

    print(f"Calling {args.model} (est cost {cost_mod.format_cost(estimated)})...", file=sys.stderr)

    try:
        result = provider.generate(prompt, **kwargs)
        if isinstance(result, JobHandle):
            print(f"  job {result.job_id} queued, polling", file=sys.stderr, end="")
            sys.stderr.flush()
            result = provider.poll(result, timeout=args.timeout)
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        saved = output_mod.save_prompt_only(
            prompt, modality, slug=args.model, output_dir=args.output, reason=str(exc)
        )
        print(f"FAILED: {exc}", file=sys.stderr)
        print(saved.display())
        return 5

    saved = output_mod.save(
        result.content,
        modality,
        result.extension,
        slug=args.model,
        output_dir=args.output,
        mime=result.mime,
    )
    print(saved.display())
    return 0
