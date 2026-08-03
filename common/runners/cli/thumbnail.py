"""Thumbnail batch execution CLI — thin declaration over cli/_maker.py.

Plan schema: skills.thumbnail.plan.v1

  {
    "schema": "skills.thumbnail.plan.v1",
    "slug": "tutorial-title-slug",
    "title": "...",
    "subtitle": null | "<text>",
    "type": "youtube|blog|podcast-episode",
    "lang": "en",
    "style_id": "gradient-mesh-modern",
    "style_anchor": "<text>",
    "model": "nano-banana-pro",
    "photo": "./me.jpg" | null,
    "output_dir": "./generated/thumbnail/<slug>",
    "parallelism": 3,
    "items": [
      {"index": 1, "label": "thumbnail-left", "placement": "left",
       "prompt": "<full>", "kwargs": {"size": "1920x1080", "image_url": "<photo>"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, run

SPEC = MakerSpec(
    module="thumbnail",
    schema="skills.thumbnail.plan.v1",
    skill="thumbnail-maker",
    title="Thumbnail",
    noun="variant(s)",
    parallelism=3,
    meta_keys=("slug", "title", "subtitle", "type", "lang", "style_id", "photo"),
)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
