"""Guards against model drift — the failure mode that cost this repo twelve releases.

Google shut the Imagen 4 endpoints down on 2026-06-30. Three providers went on
pointing at them, priced, documented, and listed in `--help`, because nothing in
the suite knew the difference between a model that works and a string that used
to. Every test here exists to make one class of that mistake loud.

The checks are deliberately offline. Calling vendor APIs from CI would need keys,
cost money, and fail for reasons that have nothing to do with the commit.
"""

import datetime as dt
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import config, cost  # noqa: E402

# Aggregators bill per hosted model, so they price against a shared median key
# rather than their own slug. Anything else missing from PRICE_TABLE is a bug.
AGGREGATE_PRICED = {
    "fal-image": "fal/any",
    "fal-video": "fal/any",
    "fal-music": "fal/any",
    "replicate-image": "replicate/any",
    "replicate-video": "replicate/any",
    "replicate-music": "replicate/any",
}

# Vendor model id strings, pinned. These are the values that silently rot: the
# slug on the left stays valid forever while the string on the right stops
# resolving. Updating this table should be a deliberate line in a diff, verified
# against the vendor's own model list — never a drive-by edit.
#
# Last verified against vendor docs: 2026-08-03.
PINNED_MODEL_IDS = {
    "nano-banana-pro": "gemini-3-pro-image",
    "nano-banana-2": "gemini-3.1-flash-image",
    "nano-banana-2-lite": "gemini-3.1-flash-lite-image",
    "veo-3-1": "veo-3.1-generate-preview",
    "veo-3-1-fast": "veo-3.1-fast-generate-preview",
    "veo-3-1-lite": "veo-3.1-lite-generate-preview",
    "gen-4": "gen4",
    "gen-4-turbo": "gen4_turbo",
    "gen-4-5": "gen4.5",
    "aleph": "aleph",
    "sora-2": "sora-2",
    "sora-2-pro": "sora-2-pro",
    "whisper-1": "whisper-1",
    "gpt-4o-transcribe": "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe": "gpt-4o-mini-transcribe",
    "lyria-3-pro": "lyria-3-pro-preview",
    "lyria-3-clip": "lyria-3-clip-preview",
}

# How long a snapshot of vendor model ids is allowed to go unverified. Vendors
# give roughly six months' notice on a shutdown, so a review cadence inside that
# window catches the announcement while there is still time to act.
REVIEW_INTERVAL_DAYS = 120
LAST_REVIEWED = dt.date(2026, 8, 3)


def _model_id(provider) -> str | None:
    for attr in ("model_id", "_model_id"):
        value = getattr(provider, attr, None)
        if isinstance(value, str) and value:
            return value
    return None


class TestRegistryPricingParity(unittest.TestCase):
    """Every provider has a price, and every price has a provider."""

    @classmethod
    def setUpClass(cls):
        config.load_all_providers()
        cls.providers = {p.name: p for p in config.all_providers()}

    def test_every_provider_can_be_priced(self):
        for name in self.providers:
            key = AGGREGATE_PRICED.get(name, name)
            self.assertIn(
                key, cost.PRICE_TABLE,
                f"provider '{name}' is registered but unpriced — a call would estimate "
                f"as None, which never prompts for confirmation",
            )

    def test_every_priced_model_is_reachable(self):
        aggregate_keys = set(AGGREGATE_PRICED.values())
        for name in cost.PRICE_TABLE:
            if name in aggregate_keys:
                continue
            self.assertIn(
                name, self.providers,
                f"'{name}' is priced but no provider registers it — either the "
                f"provider was dropped or the price entry is aspirational",
            )


class TestDeprecationAliases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config.load_all_providers()
        cls.providers = {p.name for p in config.all_providers()}

    def test_aliases_resolve_to_a_live_provider(self):
        for old, (new, _reason) in config.deprecations().items():
            self.assertIn(
                new, self.providers,
                f"'{old}' is aliased to '{new}', which is not registered",
            )

    def test_aliases_do_not_shadow_live_providers(self):
        for old in config.deprecations():
            self.assertNotIn(
                old, self.providers,
                f"'{old}' is both registered and deprecated — the alias is dead code",
            )

    def test_retired_slug_still_resolves_with_a_warning(self):
        import io

        stderr, sys.stderr = sys.stderr, io.StringIO()
        try:
            provider = config.get_provider("imagen-4")
            warning = sys.stderr.getvalue()
        finally:
            sys.stderr = stderr
        self.assertEqual(provider.name, "nano-banana-2")
        self.assertIn("retired", warning)


class TestPinnedModelIds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config.load_all_providers()
        cls.providers = {p.name: p for p in config.all_providers()}

    def test_pinned_ids_match_the_providers(self):
        for slug, expected in PINNED_MODEL_IDS.items():
            provider = self.providers.get(slug)
            self.assertIsNotNone(provider, f"pinned slug '{slug}' is no longer registered")
            self.assertEqual(
                _model_id(provider), expected,
                f"'{slug}' now sends model id '{_model_id(provider)}' instead of "
                f"'{expected}'. If the change is intentional, update PINNED_MODEL_IDS "
                f"and re-verify against the vendor's model list.",
            )

    def test_every_provider_with_a_model_id_is_pinned(self):
        unpinned = [
            name for name, p in self.providers.items()
            if _model_id(p) and name not in PINNED_MODEL_IDS
        ]
        self.assertEqual(
            unpinned, [],
            f"these providers send a vendor model id that nothing pins: {unpinned}",
        )


class TestSnapshotFreshness(unittest.TestCase):
    def test_model_ids_have_been_verified_recently(self):
        if os.environ.get("SKILLS_SKIP_STALENESS") == "1":
            self.skipTest("staleness tripwire disabled via SKILLS_SKIP_STALENESS=1")
        age = (dt.date.today() - LAST_REVIEWED).days
        self.assertLessEqual(
            age, REVIEW_INTERVAL_DAYS,
            f"model ids were last verified {age} days ago (limit {REVIEW_INTERVAL_DAYS}). "
            f"Re-check PINNED_MODEL_IDS and PRICE_TABLE against the vendor docs, then "
            f"move LAST_REVIEWED. Set SKILLS_SKIP_STALENESS=1 to bypass for one run.",
        )


if __name__ == "__main__":
    unittest.main()
