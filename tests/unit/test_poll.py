"""Unit tests for common/runners/poll.py — the async-vendor wait loop.

Every video and music generation blocks here. A backoff that never grows hammers
the vendor's API; a timeout that never fires hangs the user's terminal forever.
Time is stubbed so the suite stays instant and deterministic.
"""

import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import poll  # noqa: E402
from common.runners.errors import TimeoutError as RunnerTimeoutError  # noqa: E402


class FakeClock:
    """Replaces time.monotonic/time.sleep so elapsed time is driven by sleeps."""

    def __init__(self):
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class PollCase(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self._saved = (poll.time.monotonic, poll.time.sleep, sys.stderr)
        poll.time.monotonic = self.clock.monotonic
        poll.time.sleep = self.clock.sleep
        sys.stderr = io.StringIO()

    def tearDown(self):
        poll.time.monotonic, poll.time.sleep, sys.stderr = self._saved


class TestPollUntil(PollCase):
    def test_returns_immediately_when_ready(self):
        result = poll.poll_until(lambda: "done", provider="veo", progress=False)
        self.assertEqual(result, "done")
        self.assertEqual(self.clock.sleeps, [], "slept despite an immediate result")

    def test_polls_until_the_value_appears(self):
        calls = {"n": 0}

        def check():
            calls["n"] += 1
            return "ready" if calls["n"] == 4 else None

        self.assertEqual(poll.poll_until(check, provider="kling", progress=False), "ready")
        self.assertEqual(calls["n"], 4)

    def test_falsy_but_not_none_results_are_accepted(self):
        # `if result is not None` — an empty list or 0 is a legitimate payload
        # and must not be mistaken for "not ready yet".
        self.assertEqual(poll.poll_until(lambda: [], provider="x", progress=False), [])
        self.assertEqual(poll.poll_until(lambda: 0, provider="x", progress=False), 0)

    def test_raises_timeout_with_the_provider_name(self):
        with self.assertRaises(RunnerTimeoutError) as ctx:
            poll.poll_until(
                lambda: None, provider="sora", timeout=30.0,
                backoff=poll.Backoff(initial_interval=3.0), progress=False,
            )
        self.assertIn("sora", str(ctx.exception))

    def test_never_sleeps_past_the_timeout(self):
        with self.assertRaises(RunnerTimeoutError):
            poll.poll_until(
                lambda: None, provider="p", timeout=10.0,
                backoff=poll.Backoff(initial_interval=3.0), progress=False,
            )
        # A final sleep overshooting the deadline would make the call outlive
        # the timeout the caller asked for.
        self.assertLessEqual(sum(self.clock.sleeps), 10.0)

    def test_backoff_grows_but_is_capped(self):
        with self.assertRaises(RunnerTimeoutError):
            poll.poll_until(
                lambda: None, provider="p", timeout=600.0,
                backoff=poll.Backoff(initial_interval=3.0, max_interval=12.0), progress=False,
            )
        self.assertEqual(self.clock.sleeps[0], 3.0, "first wait should be initial_interval")
        self.assertGreater(max(self.clock.sleeps), 3.0, "backoff never grew")
        self.assertLessEqual(max(self.clock.sleeps), 12.0, "backoff exceeded max_interval")

    def test_progress_output_goes_to_stderr_not_stdout(self):
        # stdout carries machine-readable results; a progress dot there corrupts them.
        calls = {"n": 0}

        def check():
            calls["n"] += 1
            return "ok" if calls["n"] == 3 else None

        poll.poll_until(check, provider="p", progress=True)
        self.assertIn(".", sys.stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
