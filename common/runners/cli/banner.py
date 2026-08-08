"""Banner batch execution CLI — thin declaration over cli/_maker.py.

Plan schema: skills.banner.plan.v1

  {
    "schema": "skills.banner.plan.v1",
    "slug": "saas-launch-q3",
    "headline": "Ship 10× faster",
    "subhead": null | "<text>",
    "cta": "Start free trial",
    "brand": "Acme Cloud",
    "lang": "en",
    "style_id": "swiss-grid-poster",
    "style_anchor": "<text>",
    "model": "ideogram-3-quality",
    "logo": "./logo.png" | null,
    "output_dir": "./generated/banner/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "og-image", "preset": "og",
       "prompt": "<full>", "kwargs": {"size": "1200x630"}},
      {"index": 2, "label": "linkedin-ad", "preset": "linkedin-ad",
       "prompt": "<full>", "kwargs": {"size": "1200x627"}},
      {"index": 3, "label": "leaderboard", "preset": "leaderboard",
       "prompt": "<full>", "kwargs": {"size": "1456x180"}},
      ...
    ]
  }
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, build_parser as _build, run

SPEC = MakerSpec(
    module="banner",
    schema="skills.banner.plan.v1",
    skill="banner-maker",
    title="Banner",
    noun="preset(s)",
    label_prefix="banner",
    meta_keys=("slug", "headline", "subhead", "cta", "brand", "lang", "style_id", "logo"),
)


def build_parser():
    """The flags this module accepts — read by scripts/check-cli-docs.py."""
    return _build(SPEC)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
