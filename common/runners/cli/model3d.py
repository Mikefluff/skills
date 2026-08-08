"""3D model execution CLI — text or image in, a mesh file out.

Named `model3d` rather than `model` because `--model` is already the flag every
other CLI here uses for a provider slug, and a module called `model` next to it
reads as that flag's implementation.

Thin declaration over cli/_shared.py, like image / video / music / audio. The
shared dispatcher was already modality-agnostic, so the only thing 3D needed was
the modality itself and four passthrough flags.
"""

from __future__ import annotations

import sys

from ._shared import build_parser as _build, dispatch

MODELS_HINT = ["tripo-v3"]


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build("model", MODELS_HINT)


def main() -> int:
    return dispatch("model", MODELS_HINT)


if __name__ == "__main__":
    sys.exit(main())
