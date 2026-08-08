"""Ideogram v3 and v4 send to different endpoints under different field names.

The two APIs are otherwise near-identical, which is the danger: pointing a v4
slug at the v3 path returns a perfectly valid image, billed at the v3 rate, from
the model the caller did not ask for. Nothing in the response says so.

`prompt` versus `text_prompt` fails louder — v4 rejects the request — but only
once someone runs it with a key. Both are pinned here instead.

Verified against developer.ideogram.ai on 2026-08-08.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import cost  # noqa: E402
from common.runners.providers import ideogram  # noqa: E402

V3 = "https://api.ideogram.ai/v1/ideogram-v3/generate"
V4 = "https://api.ideogram.ai/v1/ideogram-v4/generate"


class _Response:
    status_code = 200

    def json(self):
        return {"data": [{"url": "https://img.example/x.png"}]}


def sent(provider):
    """Return (url, body) the provider would post, without posting it."""
    captured = {}

    def fake_post(name, url, *, json, headers, timeout):
        captured["url"] = url
        captured["body"] = json
        return _Response()

    with mock.patch.dict("os.environ", {"IDEOGRAM_API_KEY": "k"}), \
            mock.patch.object(ideogram._http, "post", fake_post), \
            mock.patch.object(ideogram._http, "download", lambda *a, **k: b"PNG"):
        provider.generate("a poster")
    return captured["url"], captured["body"]


class TestEndpoints(unittest.TestCase):
    def test_v3_tiers_post_to_the_v3_path(self):
        for provider in (
            ideogram.IdeogramFlashProvider(),
            ideogram.IdeogramTurboProvider(),
            ideogram.IdeogramDefaultProvider(),
            ideogram.IdeogramQualityProvider(),
        ):
            with self.subTest(model=provider.name):
                self.assertEqual(V3, sent(provider)[0])

    def test_v4_tiers_post_to_the_v4_path(self):
        for provider in (
            ideogram.Ideogram4TurboProvider(),
            ideogram.Ideogram4DefaultProvider(),
            ideogram.Ideogram4QualityProvider(),
        ):
            with self.subTest(model=provider.name):
                self.assertEqual(V4, sent(provider)[0])


class TestPromptField(unittest.TestCase):
    def test_v3_sends_prompt(self):
        body = sent(ideogram.IdeogramQualityProvider())[1]
        self.assertEqual("a poster", body["prompt"])
        self.assertNotIn("text_prompt", body)

    def test_v4_sends_text_prompt(self):
        body = sent(ideogram.Ideogram4QualityProvider())[1]
        self.assertEqual("a poster", body["text_prompt"])
        self.assertNotIn("prompt", body)


class TestRenderingSpeed(unittest.TestCase):
    def test_each_tier_asks_for_its_own_speed(self):
        expected = {
            "ideogram-3-flash": "FLASH",
            "ideogram-3-turbo": "TURBO",
            "ideogram-3": "DEFAULT",
            "ideogram-3-quality": "QUALITY",
            "ideogram-4-turbo": "TURBO",
            "ideogram-4": "DEFAULT",
            "ideogram-4-quality": "QUALITY",
        }
        for provider in (
            ideogram.IdeogramFlashProvider(), ideogram.IdeogramTurboProvider(),
            ideogram.IdeogramDefaultProvider(), ideogram.IdeogramQualityProvider(),
            ideogram.Ideogram4TurboProvider(), ideogram.Ideogram4DefaultProvider(),
            ideogram.Ideogram4QualityProvider(),
        ):
            with self.subTest(model=provider.name):
                self.assertEqual(expected[provider.name], sent(provider)[1]["rendering_speed"])

    def test_v4_never_asks_for_flash(self):
        # Documented as "coming soon"; the API returns 400 for it today. The
        # flash tier stays on v3 until that changes.
        for provider in (
            ideogram.Ideogram4TurboProvider(),
            ideogram.Ideogram4DefaultProvider(),
            ideogram.Ideogram4QualityProvider(),
        ):
            self.assertNotEqual("FLASH", sent(provider)[1]["rendering_speed"])


class TestPricing(unittest.TestCase):
    # ideogram.ai/api-pricing, read 2026-08-08. These had been carrying the v2-era
    # figures — under what the vendor charges, which is the one direction the
    # estimator is not allowed to be wrong in.
    VENDOR = {
        "ideogram-4-turbo": "0.03", "ideogram-4": "0.06", "ideogram-4-quality": "0.10",
        "ideogram-3-turbo": "0.03", "ideogram-3": "0.06", "ideogram-3-quality": "0.09",
    }

    def test_every_tier_prices_at_the_published_rate(self):
        for slug, price in self.VENDOR.items():
            with self.subTest(model=slug):
                self.assertEqual(price, str(cost.estimate(slug, variants=1)))

    def test_flash_is_never_billed_above_turbo(self):
        self.assertLessEqual(
            cost.estimate("ideogram-3-flash", variants=1),
            cost.estimate("ideogram-3-turbo", variants=1),
        )


if __name__ == "__main__":
    unittest.main()
