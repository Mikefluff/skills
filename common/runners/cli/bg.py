"""Background removal CLI — calls the Replicate router with a bg-removal model.

Single image in, transparent PNG out. No batch (use a shell loop for batch).

Default model: 851-labs/background-remover (popular Replicate model).
Override via --replicate-model <user>/<model>.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .. import config
from .. import output as output_mod
from ..errors import (
    CostConfirmationDeclined,
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)
from ..providers.base import JobHandle


DEFAULT_REPLICATE_MODEL = "851-labs/background-remover"


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.bg")
    parser.add_argument("--image", required=True, help="path or URL to the input image")
    parser.add_argument("--output", help="output path (default ./generated/bg-removed/<stem>-nobg.png)")
    parser.add_argument(
        "--replicate-model",
        default=DEFAULT_REPLICATE_MODEL,
        help=f"Replicate model id (default: {DEFAULT_REPLICATE_MODEL})",
    )
    parser.add_argument("--check", action="store_true", help="verify env + connectivity, no generation")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument("--cost-only", action="store_true", help="print estimated cost + exit")
    parser.add_argument("--timeout", type=float, default=180.0, help="poll timeout seconds")
    args = parser.parse_args()

    config.load_all_providers()
    try:
        provider = config.get_provider("replicate-image")
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check:
        if not provider.available():
            missing = ", ".join(provider.requires_env)
            print(f"missing env: {missing}", file=sys.stderr)
            return 2
        print("OK: replicate-image configured. Run without --check to remove background.")
        return 0

    if args.cost_only:
        print("estimated cost: ~$0.001-0.005 per image (Replicate bg-removal models)")
        return 0

    if not provider.available():
        missing = ", ".join(provider.requires_env)
        print(f"missing env: {missing}", file=sys.stderr)
        return 2

    kwargs = {
        "replicate_model": args.replicate_model,
        "image_url": args.image,
        "variants": 1,
    }

    print(
        f"Removing background via Replicate model '{args.replicate_model}' ...",
        file=sys.stderr,
    )

    try:
        result = provider.generate("", **kwargs)
        if isinstance(result, JobHandle):
            print("  job queued, polling", end="", file=sys.stderr, flush=True)
            result = provider.poll(result, timeout=args.timeout)
            print("", file=sys.stderr)
    except KeyMissingError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    except (ProviderError, RunnerTimeoutError, RunnerError) as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 5

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(result.content)
        print(f"  ✓ Background removed → {output_path}", file=sys.stderr)
        print(str(output_path))
    else:
        input_path = Path(args.image)
        stem = input_path.stem if input_path.suffix else "image"
        # Strip URL path components if --image was a URL
        if "/" in stem or stem.startswith("http"):
            stem = "image"
        saved = output_mod.save(
            result.content,
            "image",
            "png",
            slug=f"{stem}-nobg",
            output_dir=Path("./generated/bg-removed"),
            mime="image/png",
        )
        print(f"  ✓ Background removed → {saved.local_path}", file=sys.stderr)
        print(saved.display())

    return 0


if __name__ == "__main__":
    sys.exit(main())
