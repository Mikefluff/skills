"""Shared steps for the single-call tool CLIs — one provider call, one file out.

bg, upscale and stylize each take an image, hand it to one provider with a
handful of kwargs, and write the result. Around that they all did the same five
things by hand: resolve the provider slug, answer --check, answer --cost-only,
refuse to start without the key, then generate-poll-save with the same two
except clauses.

What is genuinely per-tool — which provider, what the kwargs mean, what to call
the output — stays in each module. Everything else is here.

Exit codes are the contract, pinned by tests/unit/test_cli_tools.py:

    0  done (or --check / --cost-only answered and stopped)
    2  unusable before spending anything: unknown slug, missing key, bad flags
    5  the vendor was called and failed
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import config
from .. import output as output_mod
from ..errors import (
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)
from ..providers.base import GenerationResult, JobHandle, Provider


@dataclass(frozen=True)
class ToolOutput:
    """Where the single output file goes when --output was not given."""

    directory: Path
    suffix: str   # appended to the input stem: "-nobg", "-4x", "-watercolor"
    verb: str     # past-tense report: "Background removed", "Upscaled"


def add_common_arguments(parser: argparse.ArgumentParser, default_output: str) -> None:
    """The flags every tool CLI carries, so they cannot drift apart."""
    parser.add_argument("--image", required=True, help="path or URL to the input image")
    parser.add_argument("--output", help=f"output path (default {default_output})")
    parser.add_argument("--check", action="store_true", help="verify env + connectivity, no generation")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument("--cost-only", action="store_true", help="print estimated cost + exit")
    parser.add_argument("--timeout", type=float, default=180.0, help="poll timeout seconds")


def resolve_provider(slug: str) -> Provider | None:
    """Look up a provider slug. None means the caller should exit 2."""
    config.load_all_providers()
    try:
        return config.get_provider(slug)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return None


def _missing_env(provider: Provider) -> str:
    """The keys this provider needs, or "" when it is ready."""
    return "" if provider.available() else ", ".join(provider.requires_env)


def preflight(provider: Provider, args: argparse.Namespace,
              ready_line: str, cost_line: str) -> int | None:
    """Answer --check / --cost-only and refuse to start without a key.

    Returns an exit code to return immediately, or None to carry on.
    --cost-only is answered before the key check on purpose: asking what
    something would cost should not require being able to pay for it.
    """
    if args.check:
        missing = _missing_env(provider)
        if missing:
            print(f"missing env: {missing}", file=sys.stderr)
            return 2
        print(ready_line)
        return 0

    if args.cost_only:
        print(cost_line)
        return 0

    missing = _missing_env(provider)
    if missing:
        print(f"missing env: {missing}", file=sys.stderr)
        return 2
    return None


def _input_stem(image_ref: str) -> str:
    """Stem for the default output filename. A URL collapses to "image"."""
    path = Path(image_ref)
    stem = path.stem if path.suffix else "image"
    if "/" in stem or stem.startswith("http"):
        stem = "image"
    return stem


def _write(result: GenerationResult, args: argparse.Namespace, out: ToolOutput) -> int:
    """Explicit --output wins; otherwise the tool's own generated/ namespace."""
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result.content)
        print(f"  ✓ {out.verb} → {path}", file=sys.stderr)
        print(str(path))
        return 0

    saved, companions = output_mod.save_result(
        result,
        "image",
        "png",
        output_mod.SaveOptions(
            slug=f"{_input_stem(args.image)}{out.suffix}",
            output_dir=out.directory,
            mime="image/png",
        ),
    )
    print(f"  ✓ {out.verb} → {saved.local_path}", file=sys.stderr)
    print(saved.display())
    for companion in companions:
        print(companion.display())
    return 0


def run(provider: Provider, prompt: str, kwargs: dict[str, Any],
        args: argparse.Namespace, out: ToolOutput) -> int:
    """Generate, poll if the vendor is async, write. Returns the exit code."""
    try:
        result = provider.generate(prompt, **kwargs)
        if isinstance(result, JobHandle):
            print("  job queued, polling", end="", file=sys.stderr, flush=True)
            result = provider.poll(result, timeout=args.timeout)
            print("", file=sys.stderr)
    except KeyMissingError as exc:
        # Nothing was spent — the key was checked but is gone or invalid.
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 5

    return _write(result, args, out)
