"""Carousel batch execution CLI — thin declaration over cli/_maker.py.

The carousel-builder skill assembles the plan (slide split + per-slide prompts +
style anchor + model pick) and writes a plan.json. Per-slide prompts are written
by the skill side via the chained `image-prompt` skill — natural-language,
designer-grade, ~80-150 words each. This CLI is a thin runner.

Plan format (schema = "skills.carousel.plan.v1"):

  {
    "schema": "skills.carousel.plan.v1",
    "topic": "...",
    "platform": "instagram|linkedin|tiktok",
    "aspect": "portrait|square|story",
    "style_id": "...",
    "model": "nano-banana-pro",
    "text_mode": "embedded|overlay|none",
    "output_dir": "./generated/carousel/<slug>",
    "parallelism": 3,
    "items": [
      {"index": 1, "label": "slide-01-hook", "prompt": "<full text>", "kwargs": {"size": "1080x1350"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, build_parser as _build, run

SPEC = MakerSpec(
    module="carousel",
    schema="skills.carousel.plan.v1",
    skill="carousel-builder",
    title="Carousel",
    noun="slide(s)",
    slug_key="topic_slug",
    label_prefix="slide",
    parallelism=3,
    # Slides are read in order, so a progress line is more useful numbered than
    # labelled — "slide 3 failed" is the thing the user needs to know.
    progress_by_index=True,
    item_hint="Structured role+content items were removed in v2.13.0.",
    meta_keys=("topic", "platform", "aspect", "style_id", "text_mode", "research_brief"),
)


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build(SPEC)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
