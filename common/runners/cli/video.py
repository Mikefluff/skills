"""CLI entry: video generation."""

from __future__ import annotations

import sys

from ._shared import dispatch

MODELS_HINT = [
    "veo-3-1",
    "veo-3-1-fast",
    "sora-2",
    "sora-2-pro",
    "kling-3",
    "gen-4",
    "gen-4-turbo",
    "aleph",
    "fal-video",
    "replicate-video",
]


def main() -> int:
    return dispatch("video", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
