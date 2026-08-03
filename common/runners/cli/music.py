"""CLI entry: music generation."""

from __future__ import annotations

import sys

from ._shared import dispatch

MODELS_HINT = [
    "suno-v5-5",
    "lyria-3-pro",
    "lyria-3-clip",
    "eleven-music",
    "fal-music",
    "replicate-music",
]


def main() -> int:
    return dispatch("music", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
