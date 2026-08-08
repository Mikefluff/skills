"""CLI entry: music generation."""

from __future__ import annotations

import sys

from ._shared import build_parser as _build, dispatch

MODELS_HINT = [
    "suno-v5-5",
    "lyria-3-pro",
    "lyria-3-clip",
    "eleven-music",
    "fal-music",
    "replicate-music",
]


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build("music", MODELS_HINT)


def main() -> int:
    return dispatch("music", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
