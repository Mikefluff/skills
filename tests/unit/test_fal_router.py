"""The fal router returns whole asset sets, not the first file of seventeen.

`fal-image` is a passthrough: `--fal-model <id>` sends you to whatever ByteDance,
Recraft or anyone else has hosted there. Most of those return one image, which is
what `GenerationResult.content` has always carried.

Some do not. `bytedance/seedream/v5/pro/layerize` decomposes a poster into 2-17
transparent PNGs — background, subject, each text block — and bills $0.03375 for
every one it produces. Taking `images[0]` and returning normally would charge for
all of them, hand back one, and print nothing to say the rest existed: an output
wrong in a way the output itself cannot reveal.

So a set comes back whole, ordered by z-index, with each layer's name attached.
The `companions` field is empty for every other provider, which is the point of
adding a field rather than changing `content`.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.errors import ProviderError  # noqa: E402
from common.runners.providers import fal  # noqa: E402
from common.runners.providers.base import JobHandle  # noqa: E402


def handle(model_id="bytedance/seedream/v5/pro/layerize"):
    return JobHandle(
        provider="fal-image",
        job_id="req-1",
        started_at=0.0,
        poll_url="https://queue.fal.run/status",
        extra={"model_id": model_id, "response_url": "https://queue.fal.run/result"},
    )


def poll_with(payload, model_id="bytedance/seedream/v5/pro/layerize"):
    """Run poll() against a canned completed response; content is the url's tail."""
    provider = fal.FalImageProvider()

    class Resp:
        status_code = 200

        def json(self):
            return payload

    with mock.patch.dict("os.environ", {"FAL_KEY": "k"}), \
            mock.patch.object(fal, "poll_until", lambda *a, **k: None), \
            mock.patch.object(fal._http, "get", lambda *a, **k: Resp()), \
            mock.patch.object(fal._http, "download", lambda _n, url, **k: url.encode()):
        return provider.poll(handle(model_id))


def layer(name, z, url=None):
    return {"url": url or f"https://cdn/{name}.png", "name": name, "z_index": z}


class TestAssetSets(unittest.TestCase):
    def test_every_layer_comes_back(self):
        payload = {"layers": [layer("subject", 1), layer("background", 0), layer("title", 2)]}
        result = poll_with(payload)
        self.assertEqual(2, len(result.companions))
        self.assertEqual(3, result.extra["asset_count"])

    def test_the_set_is_ordered_by_z_index(self):
        payload = {"layers": [layer("title", 2), layer("background", 0), layer("subject", 1)]}
        result = poll_with(payload)
        self.assertEqual(b"https://cdn/background.png", result.content)
        self.assertEqual(["subject", "title"], [c.name for c in result.companions])

    def test_layer_names_and_geometry_survive(self):
        payload = {"layers": [
            layer("background", 0),
            {"url": "https://cdn/t.png", "name": "title", "z_index": 1, "bbox": [0, 0, 10, 4]},
        ]}
        companion = poll_with(payload).companions[0]
        self.assertEqual("title", companion.name)
        self.assertEqual([0, 0, 10, 4], companion.meta["bbox"])

    def test_outputs_and_files_are_set_shaped_too(self):
        for key in ("outputs", "files"):
            with self.subTest(key=key):
                result = poll_with({key: [layer("a", 0), layer("b", 1)]})
                self.assertEqual(1, len(result.companions))

    def test_an_asset_without_a_url_is_an_error_not_a_silent_gap(self):
        with self.assertRaises(ProviderError):
            poll_with({"layers": [layer("background", 0), {"name": "broken", "z_index": 1}]})


class TestEstimate(unittest.TestCase):
    """A set-returning model bills per asset, and the count is unknown up front."""

    def estimate(self, **kw):
        return fal.FalImageProvider().estimate_cost(**kw)

    def test_an_ordinary_model_is_quoted_per_image(self):
        self.assertEqual("0.05", str(self.estimate(variants=1)))
        self.assertEqual("0.20", str(self.estimate(variants=4)))

    def test_layerize_is_quoted_at_the_ceiling_not_at_one_image(self):
        # 17 layers is the documented maximum. Quoting $0.05 for a call that can
        # bill $0.57 is wrong in the direction cost.py forbids; the receipt is
        # allowed to come in lower than the estimate, never higher.
        quoted = self.estimate(fal_model="bytedance/seedream/v5/pro/layerize")
        self.assertGreater(quoted, self.estimate(variants=1) * 10)

    def test_the_other_spelling_of_the_same_model_counts_too(self):
        self.assertEqual(
            self.estimate(fal_model="bytedance/seedream/v5/pro/layerize"),
            self.estimate(fal_model="bytedance/seedream-v5.0-pro/layer-decomposition"),
        )


class TestOrdinaryModels(unittest.TestCase):
    def test_a_single_image_has_no_companions(self):
        result = poll_with({"images": [{"url": "https://cdn/one.png"}]}, "fal-ai/flux/pro/v1.1")
        self.assertEqual(b"https://cdn/one.png", result.content)
        self.assertEqual((), result.companions)

    def test_a_one_element_list_is_not_a_set(self):
        # A model that happens to return `layers: [x]` produced one asset. The
        # ordinary path handles that; treating it as a set would only rename it.
        result = poll_with({"layers": [layer("only", 0)], "images": [{"url": "https://cdn/one.png"}]})
        self.assertEqual(b"https://cdn/one.png", result.content)
        self.assertEqual((), result.companions)

    def test_a_completed_job_with_nothing_in_it_still_fails(self):
        with self.assertRaises(ProviderError):
            poll_with({"images": []}, "fal-ai/flux/pro/v1.1")


if __name__ == "__main__":
    unittest.main()
