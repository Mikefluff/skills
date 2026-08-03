"""CLI entry: video generation."""

from __future__ import annotations

import sys

from ._shared import dispatch

MODELS_HINT = [
    "veo-3-1",
    "veo-3-1-fast",
    "veo-3-1-lite",
    "kling-3",
    "gen-4",
    "gen-4-turbo",
    "gen-4-5",
    "aleph",
    "fal-video",
    "replicate-video",
    # Retired from the OpenAI API on 2026-09-24. Listed last, on purpose.
    "sora-2",
    "sora-2-pro",
]


def main() -> int:
    return dispatch("video", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
