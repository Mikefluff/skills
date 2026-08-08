"""The fal router must not quietly deliver one asset out of seventeen.

`fal-image` is a passthrough: `--fal-model <id>` sends you to whatever ByteDance,
Recraft or anyone else has hosted there. Most of those return one image, which is
what `GenerationResult` carries — a single `content: bytes`.

Some do not. `bytedance/seedream/v5/pro/layerize` decomposes a poster into 2-17
transparent PNGs and bills $0.03375 for each layer it produces. Taking the first
element and returning normally would charge for all of them, hand back one, and
print nothing to say the other sixteen existed. That is the same failure this
repo has been finding all week in cheaper forms: an output that is wrong in a way
the output itself cannot reveal.

So the router refuses, and says how many it found. Returning a set of assets is a
real feature — `GenerationResult` would have to grow — and until it exists,
failing costs the user exactly as much as succeeding wrongly, and tells them why.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.errors import ProviderError  # noqa: E402
from common.runners.providers import fal  # noqa: E402
from common.runners.providers.base import JobHandle  # noqa: E402


def handle(model_id="fal-ai/flux/pro/v1.1"):
    return JobHandle(
        provider="fal-image",
        job_id="req-1",
        started_at=0.0,
        poll_url="https://queue.fal.run/status",
        extra={"model_id": model_id, "response_url": "https://queue.fal.run/result"},
    )


def poll_with(payload):
    """Run poll() against a canned completed response."""
    provider = fal.FalImageProvider()

    class Resp:
        status_code = 200

        def json(self):
            return payload

    with mock.patch.dict("os.environ", {"FAL_KEY": "k"}), \
            mock.patch.object(fal, "poll_until", lambda *a, **k: None), \
            mock.patch.object(fal._http, "get", lambda *a, **k: Resp()), \
            mock.patch.object(fal._http, "download", lambda *a, **k: b"PNG"):
        return provider.poll(handle("bytedance/seedream/v5/pro/layerize"))


class TestMultiAssetRefusal(unittest.TestCase):
    def test_a_layer_set_is_refused_rather_than_truncated(self):
        layers = [{"url": f"https://cdn/l{i}.png", "z_index": i} for i in range(17)]
        with self.assertRaises(ProviderError) as caught:
            poll_with({"layers": layers, "images": [layers[0]]})
        message = str(caught.exception)
        self.assertIn("17", message, "the count is the point — say how much was dropped")
        self.assertIn("layerize", message)

    def test_the_other_set_shaped_keys_are_covered_too(self):
        for key in ("outputs", "files"):
            with self.subTest(key=key):
                with self.assertRaises(ProviderError):
                    poll_with({key: [{"url": "a"}, {"url": "b"}], "images": [{"url": "a"}]})

    def test_a_single_asset_still_passes(self):
        result = poll_with({"images": [{"url": "https://cdn/one.png"}]})
        self.assertEqual(b"PNG", result.content)

    def test_a_one_element_set_is_not_a_set(self):
        # A model that happens to return `layers: [x]` produced one asset. The
        # router can carry that, so refusing it would be noise.
        result = poll_with({"layers": [{"url": "a"}], "images": [{"url": "https://cdn/one.png"}]})
        self.assertEqual(b"PNG", result.content)


if __name__ == "__main__":
    unittest.main()
