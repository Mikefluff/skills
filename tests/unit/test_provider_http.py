"""Unit tests for providers/_http.py — the shared vendor-HTTP layer.

Eight provider adapters now route their calls through this module, so its error
mapping is the error mapping. The distinctions it draws are the ones the CLI
branches on: a 429 is a QuotaError the user can act on by waiting or topping up,
anything else 4xx/5xx is a ProviderError, and a transport failure is neither a
crash nor a silent None.

Nothing here opens a socket — requests.request and requests.get are patched.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.errors import ProviderError, QuotaError  # noqa: E402
from common.runners.providers import _http  # noqa: E402


def fake_response(status=200, text="", content=b""):
    resp = mock.Mock(spec=requests.Response)
    resp.status_code = status
    resp.text = text
    resp.content = content
    return resp


class StatusMapping(unittest.TestCase):
    def test_2xx_passes_through(self):
        _http.raise_for_status("p", fake_response(200))
        _http.raise_for_status("p", fake_response(204))

    def test_429_is_a_quota_error(self):
        with self.assertRaises(QuotaError) as caught:
            _http.raise_for_status("p", fake_response(429, "slow down"))
        self.assertEqual(caught.exception.status, 429)

    def test_quota_error_is_catchable_as_provider_error(self):
        # Callers that only care "the vendor said no" catch the base class.
        with self.assertRaises(ProviderError):
            _http.raise_for_status("p", fake_response(429, "slow down"))

    def test_other_4xx_and_5xx_are_provider_errors(self):
        for status in (400, 401, 404, 500, 503):
            with self.subTest(status=status), self.assertRaises(ProviderError) as caught:
                _http.raise_for_status("p", fake_response(status, "boom"))
            self.assertNotIsInstance(caught.exception, QuotaError)
            self.assertEqual(caught.exception.status, status)

    def test_body_is_truncated(self):
        # Vendors answer 500s with whole HTML pages; a stack trace is not
        # improved by having one pasted into it.
        with self.assertRaises(ProviderError) as caught:
            _http.raise_for_status("p", fake_response(500, "x" * 5000))
        self.assertEqual(len(caught.exception.message), 500)


class Send(unittest.TestCase):
    def test_transport_failure_becomes_a_provider_error(self):
        with mock.patch.object(requests, "request", side_effect=requests.ConnectionError("no route")):
            with self.assertRaises(ProviderError) as caught:
                _http.post("p", "https://example.invalid/v1/go")
        self.assertIn("network error", str(caught.exception))
        self.assertIn("no route", str(caught.exception))
        self.assertIsNone(caught.exception.status)

    def test_transport_failure_keeps_the_original_as_cause(self):
        original = requests.Timeout("too slow")
        with mock.patch.object(requests, "request", side_effect=original):
            with self.assertRaises(ProviderError) as caught:
                _http.post("p", "https://example.invalid/v1/go")
        self.assertIs(caught.exception.__cause__, original)

    def test_poll_failures_say_they_happened_during_a_poll(self):
        # A poll can fail after a job was accepted and paid for, which is a
        # different situation from a submission that never landed.
        with mock.patch.object(requests, "request", side_effect=requests.ConnectionError("x")):
            with self.assertRaises(ProviderError) as caught:
                _http.poll_get("p", "https://example.invalid/v1/jobs/1")
        self.assertIn("network error during poll", str(caught.exception))

    def test_successful_response_is_returned(self):
        ok = fake_response(200, "{}")
        with mock.patch.object(requests, "request", return_value=ok) as sent:
            self.assertIs(_http.post("p", "https://x/y", json={"a": 1}), ok)
        sent.assert_called_once()
        self.assertEqual(sent.call_args.args, ("POST", "https://x/y"))
        self.assertEqual(sent.call_args.kwargs["json"], {"a": 1})


class Timeouts(unittest.TestCase):
    """Every call must carry one — a hung vendor otherwise hangs the batch."""

    def test_defaults_per_phase(self):
        cases = (
            (_http.post, _http.SUBMIT_TIMEOUT),
            (_http.get, _http.SUBMIT_TIMEOUT),
            (_http.poll_get, _http.POLL_TIMEOUT),
        )
        for fn, expected in cases:
            with self.subTest(fn.__name__):
                with mock.patch.object(requests, "request", return_value=fake_response()) as sent:
                    fn("p", "https://x/y")
                self.assertEqual(sent.call_args.kwargs["timeout"], expected)

    def test_caller_can_override(self):
        with mock.patch.object(requests, "request", return_value=fake_response()) as sent:
            _http.post("p", "https://x/y", timeout=300)
        self.assertEqual(sent.call_args.kwargs["timeout"], 300)

    def test_download_default(self):
        with mock.patch.object(requests, "get", return_value=fake_response(content=b"x")) as sent:
            _http.download("p", "https://x/asset.mp4")
        self.assertEqual(sent.call_args.kwargs["timeout"], _http.DOWNLOAD_TIMEOUT)


class Download(unittest.TestCase):
    def test_returns_bytes(self):
        with mock.patch.object(requests, "get", return_value=fake_response(content=b"\x00mp4")):
            self.assertEqual(_http.download("p", "https://x/a.mp4"), b"\x00mp4")

    def test_transport_failure_is_reported_as_a_download(self):
        with mock.patch.object(requests, "get", side_effect=requests.ConnectionError("reset")):
            with self.assertRaises(ProviderError) as caught:
                _http.download("p", "https://x/a.mp4")
        self.assertIn("download failed", str(caught.exception))

    def test_error_status_is_reported(self):
        with mock.patch.object(requests, "get", return_value=fake_response(404)):
            with self.assertRaises(ProviderError) as caught:
                _http.download("p", "https://x/a.mp4")
        self.assertEqual(caught.exception.status, 404)

    def test_429_on_an_asset_url_is_not_a_quota_error(self):
        # A signed asset URL answering 429 means the link is being fetched too
        # fast. QuotaError reads as "the account is out of credit", which would
        # send the user to the billing page over a transient fetch limit.
        with mock.patch.object(requests, "get", return_value=fake_response(429)):
            with self.assertRaises(ProviderError) as caught:
                _http.download("p", "https://x/a.mp4")
        self.assertNotIsInstance(caught.exception, QuotaError)


if __name__ == "__main__":
    unittest.main()
