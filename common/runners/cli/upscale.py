"""Upscaler CLI — calls the Replicate router with an upscaling model.

Single image in, upscaled image out. Default: Real-ESRGAN (4×).

Defaults:
  Replicate model: nightmareai/real-esrgan (popular general upscaler)
  Scale: 4× (most providers support 2 / 4 / 8)

Alternatives (--replicate-model <slug>):
  - nightmareai/real-esrgan        — general; default
  - tencentarc/gfpgan              — face-focused (best for portraits)
  - jingyunliang/swinir            — alt general
  - philz1337x/clarity-upscaler    — high-fidelity preservation

For face-focused upscale: --face-enhance flag wires GFPGAN-style face restoration if the model supports it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import config
from .. import output as output_mod
from ..errors import (
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)
from ..providers.base import JobHandle


DEFAULT_REPLICATE_MODEL = "nightmareai/real-esrgan"
DEFAULT_SCALE = 4


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.upscale")
    parser.add_argument("--image", required=True, help="path or URL to the input image")
    parser.add_argument("--output", help="output path (default ./generated/upscaled/<stem>-<scale>x.png)")
    parser.add_argument(
        "--scale", type=int, default=DEFAULT_SCALE,
        help=f"upscaling factor (2/4/8; default {DEFAULT_SCALE}); model must support it",
    )
    parser.add_argument(
        "--replicate-model",
        default=DEFAULT_REPLICATE_MODEL,
        help=f"Replicate model id (default: {DEFAULT_REPLICATE_MODEL})",
    )
    parser.add_argument(
        "--face-enhance", action="store_true",
        help="enable face restoration (Real-ESRGAN / GFPGAN supports this)",
    )
    parser.add_argument("--check", action="store_true", help="verify env + connectivity, no upscale")
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
        print("OK: replicate-image configured. Run without --check to upscale.")
        return 0

    if args.cost_only:
        print(f"estimated cost: ~$0.005-0.02 per image at {args.scale}× (Replicate upscalers)")
        return 0

    if not provider.available():
        missing = ", ".join(provider.requires_env)
        print(f"missing env: {missing}", file=sys.stderr)
        return 2

    if args.scale not in (2, 4, 8):
        print(f"  ⚠ scale={args.scale} unusual; common values are 2 / 4 / 8", file=sys.stderr)

    kwargs = {
        "replicate_model": args.replicate_model,
        "image_url": args.image,
        "variants": 1,
        "scale": args.scale,
    }
    if args.face_enhance:
        kwargs["face_enhance"] = True

    print(
        f"Upscaling {args.scale}× via Replicate model '{args.replicate_model}'"
        f"{' (face-enhance ON)' if args.face_enhance else ''} ...",
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
        print(f"  ✓ Upscaled → {output_path}", file=sys.stderr)
        print(str(output_path))
    else:
        input_path = Path(args.image)
        stem = input_path.stem if input_path.suffix else "image"
        if "/" in stem or stem.startswith("http"):
            stem = "image"
        saved = output_mod.save(
            result.content,
            "image",
            "png",
            output_mod.SaveOptions(
                slug=f"{stem}-{args.scale}x",
                output_dir=Path("./generated/upscaled"),
                mime="image/png",
            ),
        )
        print(f"  ✓ Upscaled → {saved.local_path}", file=sys.stderr)
        print(saved.display())

    return 0


if __name__ == "__main__":
    sys.exit(main())
