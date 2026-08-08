"""Tripo — the first `model` provider, and the first with an expiring output.

Every other async provider here can hand back a URL and let the caller fetch it
whenever. Tripo cannot: a finished model URL is valid for five minutes, and the
asset is already billed. A provider that returns the link and downloads later
loses paid work on any slow path — a batch queue, a retry, a user reading the
output before acting on it.

So `poll` downloads inside the call that observes success, and that is the
property worth pinning: not that the download happens, but that it happens
before the function returns.

Contract verified against developers.tripo3d.ai/en/docs/quick-start 2026-08-08.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import cost  # noqa: E402
from common.runners.errors import ProviderError  # noqa: E402
from common.runners.providers import tripo  # noqa: E402


class _Resp:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def create(**kwargs):
    """Run generate() and return (url, body) it would have posted."""
    seen = {}

    def fake_post(name, url, *, json, headers, timeout=None):
        seen["url"] = url
        seen["body"] = json
        seen["headers"] = headers
        return _Resp({"data": {"task_id": "task-1"}})

    with mock.patch.dict("os.environ", {"TRIPO_API_KEY": "k"}), \
            mock.patch.object(tripo._http, "post", fake_post):
        handle = tripo.TripoProvider().generate(kwargs.pop("prompt", "a fox"), **kwargs)
    return handle, seen


def finish(status_payload, downloads):
    """Run poll() against a canned task response, recording downloads."""
    provider = tripo.TripoProvider()
    handle = tripo.JobHandle(
        provider=provider.name, job_id="task-1", started_at=0.0,
        poll_url=f"{tripo.BASE}/tasks/task-1", extra={"model_version": tripo.DEFAULT_MODEL},
    )

    def fake_download(name, url, **kw):
        downloads.append(url)
        return b"GLB-BYTES"

    with mock.patch.dict("os.environ", {"TRIPO_API_KEY": "k"}), \
            mock.patch.object(tripo, "poll_until", lambda check, **kw: check()), \
            mock.patch.object(tripo._http, "poll_get", lambda *a, **k: _Resp(status_payload)), \
            mock.patch.object(tripo._http, "download", fake_download):
        return provider.poll(handle)


SUCCESS = {
    "data": {
        "status": "success",
        "consumed_credit": 20,
        "output": {"model_url": "https://cdn.tripo/x.glb?sig=abc"},
    }
}


class TestRequest(unittest.TestCase):
    def test_text_prompt_posts_to_the_text_endpoint(self):
        _, seen = create(prompt="a low-poly fox")
        self.assertEqual(f"{tripo.BASE}/generation/text-to-model", seen["url"])
        self.assertEqual("a low-poly fox", seen["body"]["prompt"])

    def test_an_image_switches_the_endpoint(self):
        _, seen = create(prompt="back is plain", image_url="./ref.jpg")
        self.assertEqual(f"{tripo.BASE}/generation/image-to-model", seen["url"])
        self.assertEqual("./ref.jpg", seen["body"]["image_url"])
        self.assertEqual("back is plain", seen["body"]["prompt"])

    def test_the_model_string_is_pinned_not_floating(self):
        # A silent vendor upgrade would change geometry and price under a caller
        # who asked for neither.
        _, seen = create()
        self.assertEqual(tripo.DEFAULT_MODEL, seen["body"]["model"])

    def test_optional_tuning_is_omitted_unless_asked_for(self):
        _, seen = create()
        for key in ("texture", "pbr", "face_limit", "style"):
            self.assertNotIn(key, seen["body"])

    def test_opting_out_of_texture_is_sent(self):
        _, seen = create(texture=False, face_limit=5000)
        self.assertIs(False, seen["body"]["texture"])
        self.assertEqual(5000, seen["body"]["face_limit"])

    def test_a_response_without_a_task_id_is_an_error(self):
        with mock.patch.dict("os.environ", {"TRIPO_API_KEY": "k"}), \
                mock.patch.object(tripo._http, "post", lambda *a, **k: _Resp({"data": {}})):
            with self.assertRaises(ProviderError):
                tripo.TripoProvider().generate("a fox")


class TestPoll(unittest.TestCase):
    def test_the_model_is_downloaded_before_poll_returns(self):
        # The whole reason this provider does not hand back a URL.
        downloads: list[str] = []
        result = finish(SUCCESS, downloads)
        self.assertEqual(["https://cdn.tripo/x.glb?sig=abc"], downloads)
        self.assertEqual(b"GLB-BYTES", result.content)

    def test_the_extension_follows_the_url(self):
        self.assertEqual("glb", finish(SUCCESS, []).extension)
        usdz = {"data": {"status": "success", "output": {"model_url": "https://cdn/x.usdz"}}}
        self.assertEqual("usdz", finish(usdz, []).extension)

    def test_a_url_with_no_extension_falls_back_to_glb(self):
        bare = {"data": {"status": "success", "output": {"model_url": "https://cdn/download"}}}
        self.assertEqual("glb", finish(bare, []).extension)

    def test_the_credits_actually_consumed_are_reported(self):
        # The estimate is a ceiling; this is what was really spent.
        self.assertEqual(20, finish(SUCCESS, []).extra["consumed_credit"])

    def test_every_terminal_failure_raises(self):
        for status in ("failed", "cancelled", "banned"):
            with self.subTest(status=status):
                with self.assertRaises(ProviderError):
                    finish({"data": {"status": status, "message": "no"}}, [])

    def test_success_without_a_model_url_is_an_error_not_an_empty_file(self):
        with self.assertRaises(ProviderError):
            finish({"data": {"status": "success", "output": {}}}, [])


class TestPricing(unittest.TestCase):
    def test_priced_at_the_ceiling_of_the_credit_table(self):
        # docs.tripo3d.ai: $1 = 100 credits, text-to-model 10-40 credits by tier.
        # The tier is chosen per call, so the estimate quotes the top of the band.
        self.assertEqual("0.40", str(cost.estimate("tripo-v3", variants=1)))
        self.assertEqual("1.60", str(cost.estimate("tripo-v3", variants=4)))

    def test_a_generation_always_trips_the_confirmation_threshold(self):
        self.assertGreater(cost.estimate("tripo-v3", variants=1), cost.CONFIRMATION_THRESHOLD)


if __name__ == "__main__":
    unittest.main()
