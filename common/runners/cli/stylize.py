"""Style-transfer CLI — apply an artistic style to an existing image.

Default provider: BFL Flux Kontext (best for natural-language style transfer).

Style presets (--style):
  watercolor, oil-painting, sketch, line-art, ink-wash, cyberpunk,
  studio-ghibli, pixar-3d, manga, art-deco, low-poly, vaporwave,
  custom (use --prompt-mod for arbitrary)

Outputs PNG to ./generated/stylized/<stem>-<style>.png (or --output).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from typing import Any

from . import _tool


STYLE_PROMPTS: dict[str, str] = {
    "watercolor": "transform into a watercolor painting, soft washes of color, visible brush strokes, bleeding edges, paper texture visible",
    "oil-painting": "transform into a thick oil painting, visible brush strokes, impasto texture, rich pigments, classical painting feel",
    "sketch": "transform into a pencil sketch, graphite shading, cross-hatching, white paper background, no color",
    "line-art": "transform into clean black line art, no shading, no color, just outlines on white background",
    "ink-wash": "transform into Chinese ink-wash painting style, sumi-e aesthetic, brush stroke economy, monochromatic ink tones, soft gradient washes",
    "cyberpunk": "transform into cyberpunk neon aesthetic, neon glow, holographic accents, dark background with vibrant pink/cyan/yellow neons, retrofuturistic feel",
    "studio-ghibli": "transform into Studio Ghibli animation style, hand-painted aesthetic, soft watercolor backgrounds, expressive characters, Miyazaki-inspired",
    "pixar-3d": "transform into Pixar 3D animation style, smooth surfaces, expressive features, cinematic lighting, vibrant colors",
    "manga": "transform into Japanese manga style, black and white, screentone patterns, expressive line art, action lines",
    "art-deco": "transform into Art Deco poster style, geometric shapes, gold + black palette, 1920s aesthetic, symmetric composition",
    "low-poly": "transform into low-poly 3D aesthetic, flat triangular facets, limited palette, geometric simplification",
    "vaporwave": "transform into vaporwave aesthetic, pastel pink/purple/cyan palette, retro 80s neon grid, glitch effects, dreamlike",
}

DEFAULT_MODEL = "flux-kontext"


def _style_prompt(args: argparse.Namespace) -> str | None:
    """Resolve --style into prompt text. None means the caller should exit 2."""
    if args.style == "custom":
        if not args.prompt_mod:
            print("  ✗ --style custom requires --prompt-mod '<description>'", file=sys.stderr)
            return None
        return args.prompt_mod

    if args.style not in STYLE_PROMPTS:
        print(
            f"  ✗ unknown --style '{args.style}'. "
            f"Available: {', '.join(STYLE_PROMPTS)} or 'custom'.",
            file=sys.stderr,
        )
        return None

    preset = STYLE_PROMPTS[args.style]
    return f"{preset}, {args.prompt_mod}" if args.prompt_mod else preset


def _image_kwargs(args: argparse.Namespace) -> dict[str, Any] | None:
    """Route the image reference under the kwarg name each provider expects.

    flux-kontext and nano-banana-pro both accept `image_url` or `input_image`
    (bfl.py and google_image.py normalise); replicate-image passes kwargs
    straight to the hosted model, which for style transfer usually reads
    `image`. None means the caller should exit 2.
    """
    if args.model == "gpt-image-2":
        print(
            "  ✗ gpt-image-2 image-to-image edits not wired in this skill yet "
            "(needs /v1/images/edits endpoint). Use --model flux-kontext or nano-banana-pro.",
            file=sys.stderr,
        )
        return None

    by_model = {
        "flux-kontext": ("input_image",),
        "nano-banana-pro": ("image_url",),
        "replicate-image": ("image",),
    }
    # Unknown or future provider — send both aliases and hope one lands.
    keys = by_model.get(args.model, ("image_url", "input_image"))
    kwargs: dict[str, Any] = {"variants": 1}
    for key in keys:
        kwargs[key] = args.image
    return kwargs


def build_parser() -> argparse.ArgumentParser:
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    parser = argparse.ArgumentParser(prog="common.runners.cli.stylize")
    _tool.add_common_arguments(parser, "./generated/stylized/<stem>-<style>.png")
    parser.add_argument(
        "--style",
        default="watercolor",
        help=f"style preset (one of: {', '.join(STYLE_PROMPTS)}, or 'custom' with --prompt-mod)",
    )
    parser.add_argument(
        "--prompt-mod",
        help="custom style description (used when --style custom, or appended to preset)",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"provider slug (default {DEFAULT_MODEL}); other options: nano-banana-pro, replicate-image",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    provider = _tool.resolve_provider(args.model)
    if provider is None:
        return 2

    early = _tool.preflight(
        provider, args,
        ready_line=f"OK: {args.model} configured. Run without --check to stylize.",
        cost_line=f"estimated cost: ~$0.05 per image via {args.model}",
    )
    if early is not None:
        return early

    style_prompt = _style_prompt(args)
    if style_prompt is None:
        return 2

    kwargs = _image_kwargs(args)
    if kwargs is None:
        return 2

    print(f"Stylizing via {args.model} → {args.style} ...", file=sys.stderr)
    output = _tool.ToolOutput(
        directory=Path("./generated/stylized"),
        suffix=f"-{args.style}",
        verb="Stylized",
    )
    return _tool.run(provider, style_prompt, kwargs, args, output)


if __name__ == "__main__":
    sys.exit(main())
