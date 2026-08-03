"""Avatar batch execution CLI — thin declaration over cli/_maker.py.

Plan schema: skills.avatar.plan.v1

  {
    "schema": "skills.avatar.plan.v1",
    "slug": "alex-headshot",
    "photo": "./alex-selfie.jpg",
    "style_id": "kinfolk-minimal",
    "style_anchor": "<text>",
    "model": "nano-banana-pro",
    "output_dir": "./generated/avatar/<slug>",
    "parallelism": 3,
    "items": [
      {"index": 1, "label": "square-v1", "aspect": "square",
       "prompt": "<full>", "kwargs": {"size": "1080x1080", "image_url": "<photo>"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, run

SPEC = MakerSpec(
    module="avatar",
    schema="skills.avatar.plan.v1",
    skill="avatar-maker",
    title="Avatar",
    noun="variant(s)",
    parallelism=3,
    meta_keys=("slug", "photo", "style_id"),
)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
