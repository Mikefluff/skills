"""Meme batch execution CLI — thin declaration over cli/_maker.py.

Plan schema: skills.meme.plan.v1

  {
    "schema": "skills.meme.plan.v1",
    "slug": "drake-prefers-ssr",
    "top_text": "USING CLIENT-SIDE RENDERING",
    "bottom_text": "ACTUALLY SHIPPING THE SITE",
    "template": "drake|distracted-boyfriend|expanding-brain|two-buttons|custom",
    "base_photo": "./photo.jpg" | null,
    "lang": "en",
    "style_id": "meme-classic-impact",
    "model": "gpt-image-2",
    "output_dir": "./generated/meme/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "meme-v1",
       "prompt": "<full>", "kwargs": {"size": "1024x1024", "image_url": "<base_photo>"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, build_parser as _build, run

SPEC = MakerSpec(
    module="meme",
    schema="skills.meme.plan.v1",
    skill="meme-card-maker",
    title="Meme",
    noun="variant(s)",
    label_prefix="meme",
    meta_keys=("slug", "top_text", "bottom_text", "template", "base_photo", "lang", "style_id"),
)


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build(SPEC)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
