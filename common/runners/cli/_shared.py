"""Shared CLI plumbing — argparse skeleton, validation, dispatch, output."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
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
from ..providers.base import JobHandle, Modality, Provider


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
    parser.add_argument("--voice", help="voice id / name (TTS) — used by OpenAI TTS (alloy/echo/fable/...) and as fallback for ElevenLabs")
    parser.add_argument("--voice-id", dest="voice_id", help="explicit ElevenLabs voice_id (preferred for Eleven)")
    parser.add_argument("--speed", type=float, help="speech speed multiplier (0.5-2.0, provider-dependent)")
    parser.add_argument("--lang", help="language hint for TTS (provider-dependent; Eleven multilingual auto-detects)")
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


# Flags that pass straight through under their own name, included only when the
# user actually set one. A provider handed size=None forwards a literal null to
# the vendor and gets a 400 back, so absent must stay absent.
_PASSTHROUGH = (
    "image_url", "video_url", "size", "quality",
    "voice", "voice_id", "lang", "fal_model", "replicate_model",
)


def gather_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Pack passthrough kwargs into a dict the provider's generate() accepts."""
    kwargs: dict[str, Any] = {"variants": args.variants}

    # One --duration serves video (seconds) and music (minutes); each provider
    # reads the unit it understands and ignores the other.
    if args.duration is not None:
        kwargs["duration_seconds"] = args.duration
        kwargs["duration_minutes"] = args.duration

    for name in _PASSTHROUGH:
        value = getattr(args, name, None)
        if value:
            kwargs[name] = value

    if args.lyrics is not None:
        kwargs["lyrics"] = args.lyrics
    if args.lyrics_file and not args.lyrics:
        kwargs["lyrics"] = args.lyrics_file.read_text(encoding="utf-8")
    if args.instrumental:
        kwargs["instrumental"] = True
    # Guarded on None, not truthiness: 0.0 is a legal speed.
    if getattr(args, "speed", None) is not None:
        kwargs["speed"] = args.speed
    return kwargs


def resolve_provider(model: str, modality: Modality) -> "Provider | None":
    """Look up the slug and check it makes this modality. None → exit 2."""
    config.load_all_providers()
    try:
        provider = config.get_provider(model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return None

    if provider.modality != modality:
        print(
            f"provider '{model}' is {provider.modality}, not {modality}.",
            file=sys.stderr,
        )
        return None
    return provider


def _keep_prompt(prompt: str, args: argparse.Namespace, modality: Modality, reason: str) -> None:
    """Persist the prompt when a run cannot produce an asset.

    A prompt is the expensive part — it was written by an LLM chain, sometimes
    over several steps. Losing it to a missing key would be the real cost.
    """
    saved = output_mod.save_prompt_only(
        prompt, modality,
        output_mod.SaveOptions(slug=args.model, output_dir=args.output),
        reason=reason,
    )
    print(saved.display())


def _generate(provider: "Provider", args: argparse.Namespace,
              prompt: str, kwargs: dict[str, Any], estimated: Decimal | None) -> int:
    """Everything past the cost gate: call, poll, save. Returns the exit code."""
    modality = provider.modality
    try:
        provider.ensure_available()
    except KeyMissingError as exc:
        _keep_prompt(prompt, args, modality, str(exc))
        return 4

    print(f"Calling {args.model} (est cost {cost_mod.format_cost(estimated)})...", file=sys.stderr)

    try:
        result = provider.generate(prompt, **kwargs)
        if isinstance(result, JobHandle):
            print(f"  job {result.job_id} queued, polling", file=sys.stderr, end="")
            sys.stderr.flush()
            result = provider.poll(result, timeout=args.timeout)
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        _keep_prompt(prompt, args, modality, str(exc))
        return 5

    saved = output_mod.save(
        result.content,
        modality,
        result.extension,
        output_mod.SaveOptions(slug=args.model, output_dir=args.output, mime=result.mime),
    )
    print(saved.display())
    return 0


def dispatch(modality: Modality, models_hint: list[str] | None = None) -> int:
    parser = build_parser(modality, models_hint)
    args = parser.parse_args()

    if args.list_providers:
        return list_providers(modality)
    if not args.model:
        parser.error("missing --model. Use --list-providers to see options.")
    if args.check:
        return check_provider(args.model, modality)

    provider = resolve_provider(args.model, modality)
    if provider is None:
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

    return _generate(provider, args, prompt, kwargs, estimated)
