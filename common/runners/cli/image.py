"""CLI entry: image generation."""

from __future__ import annotations

import sys

from ._shared import dispatch

MODELS_HINT = [
    "gpt-image-2",
    "imagen-4",
    "imagen-4-ultra",
    "nano-banana-pro",
    "flux-1-1-pro",
    "flux-2-pro",
    "flux-kontext",
    "flux-schnell",
    "ideogram-3",
    "ideogram-3-quality",
    "fal-image",
    "replicate-image",
]


def main() -> int:
    return dispatch("image", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
