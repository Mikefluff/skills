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

from .. import config
from .. import output as output_mod
from ..errors import (
    KeyMissingError,
    ProviderError,
    RunnerError,
    TimeoutError as RunnerTimeoutError,
)
from ..providers.base import JobHandle


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


def main() -> int:
    parser = argparse.ArgumentParser(prog="common.runners.cli.stylize")
    parser.add_argument("--image", required=True, help="path or URL to the input image")
    parser.add_argument("--output", help="output path (default ./generated/stylized/<stem>-<style>.png)")
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
    parser.add_argument("--check", action="store_true", help="verify env + connectivity, no generation")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument("--cost-only", action="store_true", help="print estimated cost + exit")
    parser.add_argument("--timeout", type=float, default=180.0, help="poll timeout seconds")
    args = parser.parse_args()

    config.load_all_providers()
    try:
        provider = config.get_provider(args.model)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check:
        if not provider.available():
            missing = ", ".join(provider.requires_env)
            print(f"missing env: {missing}", file=sys.stderr)
            return 2
        print(f"OK: {args.model} configured. Run without --check to stylize.")
        return 0

    if args.cost_only:
        print(f"estimated cost: ~$0.05 per image via {args.model}")
        return 0

    if not provider.available():
        missing = ", ".join(provider.requires_env)
        print(f"missing env: {missing}", file=sys.stderr)
        return 2

    # Assemble style prompt
    if args.style == "custom":
        if not args.prompt_mod:
            print("  ✗ --style custom requires --prompt-mod '<description>'", file=sys.stderr)
            return 2
        style_prompt = args.prompt_mod
    elif args.style in STYLE_PROMPTS:
        style_prompt = STYLE_PROMPTS[args.style]
        if args.prompt_mod:
            style_prompt = f"{style_prompt}, {args.prompt_mod}"
    else:
        print(f"  ✗ unknown --style '{args.style}'. Available: {', '.join(STYLE_PROMPTS)} or 'custom'.", file=sys.stderr)
        return 2

    # Route the image reference under the kwarg name each provider expects.
    # flux-kontext + nano-banana-pro both now accept `image_url` or `input_image`
    # (bfl.py and google_image.py normalize); replicate-image passes kwargs through
    # to the hosted model, which typically expects `image` for style-transfer models.
    kwargs: dict[str, Any] = {"variants": 1}
    if args.model == "flux-kontext":
        kwargs["input_image"] = args.image
    elif args.model == "nano-banana-pro":
        kwargs["image_url"] = args.image
    elif args.model == "replicate-image":
        # Most Replicate style-transfer models read `image` (the model's input field).
        kwargs["image"] = args.image
    elif args.model == "gpt-image-2":
        print(
            "  ✗ gpt-image-2 image-to-image edits not wired in this skill yet "
            "(needs /v1/images/edits endpoint). Use --model flux-kontext or nano-banana-pro.",
            file=sys.stderr,
        )
        return 2
    else:
        # Unknown / future provider — pass both aliases and hope for the best.
        kwargs["image_url"] = args.image
        kwargs["input_image"] = args.image

    print(
        f"Stylizing via {args.model} → {args.style} ...",
        file=sys.stderr,
    )

    try:
        result = provider.generate(style_prompt, **kwargs)
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
        print(f"  ✓ Stylized → {output_path}", file=sys.stderr)
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
                slug=f"{stem}-{args.style}",
                output_dir=Path("./generated/stylized"),
                mime="image/png",
            ),
        )
        print(f"  ✓ Stylized → {saved.local_path}", file=sys.stderr)
        print(saved.display())

    return 0


if __name__ == "__main__":
    sys.exit(main())
