"""CLI entry: image generation."""

from __future__ import annotations

import sys

from ._shared import build_parser as _build, dispatch

MODELS_HINT = [
    "gpt-image-2",
    "nano-banana-pro",
    "nano-banana-2",
    "nano-banana-2-lite",
    "flux-1-1-pro",
    "flux-2-pro",
    "flux-kontext",
    "flux-schnell",
    "ideogram-3",
    "ideogram-3-quality",
    "fal-image",
    "replicate-image",
]


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build("image", MODELS_HINT)


def main() -> int:
    return dispatch("image", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
