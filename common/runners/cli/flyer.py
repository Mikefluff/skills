"""Flyer batch execution CLI — thin declaration over cli/_maker.py.

Each item is a per-aspect render with composition zones already encoded in the
prompt by the skill's prompt assembly.

Plan format (schema = "skills.flyer.plan.v1"):

  {
    "schema": "skills.flyer.plan.v1",
    "event_slug": "workshop-slow-software",
    "title": "...",
    "subtitle": "...",
    "date": "...",
    "location": "...",
    "cta": "...",
    "lang": "en",
    "style_id": "kinfolk-minimal",
    "style_anchor": "<text>",
    "model": "nano-banana-pro",
    "photo": "./alex-headshot.jpg" | null,
    "output_dir": "./generated/flyer/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "portrait", "aspect": "portrait",
       "prompt": "<full per-aspect prompt>",
       "kwargs": {"size": "1080x1350", "image_url": "./alex-headshot.jpg"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, run

SPEC = MakerSpec(
    module="flyer",
    schema="skills.flyer.plan.v1",
    skill="flyer-maker",
    title="Flyer",
    noun="aspect(s)",
    slug_key="event_slug",
    label_prefix="aspect",
    # A flyer set is printed and handed around, so the filenames are what the
    # user asks for next — list them rather than making them go and look.
    list_files=True,
    meta_keys=("title", "subtitle", "date", "location", "cta", "lang", "style_id", "photo"),
)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
