"""CLI entry: audio (TTS) generation.

Routes through the shared dispatch — same shape as image/video/music CLIs.
Common providers under this modality: gpt-4o-mini-tts (OpenAI), eleven-tts
(ElevenLabs).
"""

from __future__ import annotations

import sys

from ._shared import dispatch

MODELS_HINT = [
    "gpt-4o-mini-tts",
    "eleven-tts",
]


def main() -> int:
    return dispatch("audio", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
