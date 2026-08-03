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

from . import _tool

DEFAULT_REPLICATE_MODEL = "nightmareai/real-esrgan"
DEFAULT_SCALE = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.upscale")
    _tool.add_common_arguments(parser, "./generated/upscaled/<stem>-<scale>x.png")
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
    return parser


def main() -> int:
    args = build_parser().parse_args()

    provider = _tool.resolve_provider("replicate-image")
    if provider is None:
        return 2

    early = _tool.preflight(
        provider, args,
        ready_line="OK: replicate-image configured. Run without --check to upscale.",
        cost_line=(
            f"estimated cost: ~$0.005-0.02 per image at {args.scale}× (Replicate upscalers)"
        ),
    )
    if early is not None:
        return early

    # Not fatal: an unusual factor may still be valid for a specific model.
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
    output = _tool.ToolOutput(
        directory=Path("./generated/upscaled"),
        suffix=f"-{args.scale}x",
        verb="Upscaled",
    )
    return _tool.run(provider, "", kwargs, args, output)


if __name__ == "__main__":
    sys.exit(main())
