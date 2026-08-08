"""Quote-card batch execution CLI — thin declaration over cli/_maker.py.

Plan schema: skills.quote.plan.v1

  {
    "schema": "skills.quote.plan.v1",
    "slug": "kierkegaard-anxiety",
    "quote": "Anxiety is the dizziness of freedom.",
    "attribution": "— Søren Kierkegaard",
    "style_id": "swiss-grid-poster",
    "style_anchor": "<text>",
    "lang": "en",
    "model": "ideogram-3-quality",
    "output_dir": "./generated/quote/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "square-v1", "aspect": "square",
       "prompt": "<full>", "kwargs": {"size": "1080x1080"}},
      {"index": 2, "label": "portrait-v1", "aspect": "portrait",
       "prompt": "<full>", "kwargs": {"size": "1080x1350"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, build_parser as _build, run

SPEC = MakerSpec(
    module="quote",
    schema="skills.quote.plan.v1",
    skill="quote-card-maker",
    title="Quote",
    noun="card(s)",
    meta_keys=("slug", "quote", "attribution", "style_id", "lang"),
)


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build(SPEC)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
