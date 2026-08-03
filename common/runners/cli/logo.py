"""Logo batch execution CLI — thin declaration over cli/_maker.py.

Plan schema: skills.logo.plan.v1

  {
    "schema": "skills.logo.plan.v1",
    "slug": "lunar-vault",
    "brand": "Lunar Vault",
    "tagline": null | "<text>",
    "style": "wordmark|minimal|illustrated|typographic|geometric|emblem",
    "palette_hint": "two tones, deep teal + warm cream",
    "lang": "en",
    "model": "ideogram-3-quality",
    "output_dir": "./generated/logo/<slug>",
    "parallelism": 2,
    "items": [
      {"index": 1, "label": "logo-v1", "prompt": "<full>",
       "kwargs": {"size": "1024x1024"}},
      ...
    ]
  }

Logos are single-image (no aspect multiplexing). Variants differ only in stochastic interpretation.
Transparent BG via a downstream bg-remover pass; this skill outputs PNG on solid BG (or hints
"isolated on white" via the prompt).
"""

from __future__ import annotations

import sys

from ._maker import MakerSpec, run

SPEC = MakerSpec(
    module="logo",
    schema="skills.logo.plan.v1",
    skill="logo-maker",
    title="Logo",
    noun="variant(s)",
    meta_keys=("slug", "brand", "tagline", "style", "palette_hint", "lang"),
)


def main() -> int:
    return run(SPEC)


if __name__ == "__main__":
    sys.exit(main())
