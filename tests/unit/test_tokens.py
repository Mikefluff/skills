"""Unit tests for common/runners/tokens.py — the OAuth token store.

This module decides whether a stored credential is still good enough to post
with. Getting that wrong is expensive in both directions: too eager and every
publish dies on a 401 the user cannot explain; too lax and we hand an expired
token to a platform mid-upload. It also writes secrets to disk, so the same
permission and atomicity concerns as keysfile apply.
"""

import stat
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import tokens  # noqa: E402
from common.runners.errors import TokenError  # noqa: E402


class TokensCase(unittest.TestCase):
    """Redirects TOKENS_FILE at a temp path so no test can touch real tokens."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._saved = tokens.TOKENS_FILE
        tokens.TOKENS_FILE = Path(self._tmp.name) / ".skills-tokens.json"
        self._saved_refreshers = dict(tokens._REFRESHERS)
        tokens._REFRESHERS.clear()

    def tearDown(self):
        tokens.TOKENS_FILE = self._saved
        tokens._REFRESHERS.clear()
        tokens._REFRESHERS.update(self._saved_refreshers)
        self._tmp.cleanup()

    def entry(self, platform="threads", **kw):
        base = dict(
            platform=platform,
            access_token="tok-ABCDEFGHIJKLMNOP",
            refresh_token="ref-1",
            expires_at=time.time() + 86400,
        )
        base.update(kw)
        return tokens.TokenEntry(**base)


class TestExpiry(TokensCase):
    def test_none_expiry_never_expires(self):
        self.assertFalse(self.entry(expires_at=None).expired())

    def test_past_expiry_is_expired(self):
        self.assertTrue(self.entry(expires_at=time.time() - 1).expired())

    def test_skew_window_expires_early(self):
        # Still nominally valid, but inside the skew window — we must refresh
        # BEFORE the request rather than discover the 401 halfway through an
        # upload that already pushed 200 MB.
        soon = time.time() + (tokens.REFRESH_SKEW / 2)
        self.assertTrue(self.entry(expires_at=soon).expired())

    def test_outside_skew_window_is_fine(self):
        later = time.time() + (tokens.REFRESH_SKEW * 3)
        self.assertFalse(self.entry(expires_at=later).expired())

    def test_human_readable_expiry(self):
        self.assertEqual(self.entry(expires_at=None).expires_in_human(), "no expiry")
        self.assertEqual(self.entry(expires_at=time.time() - 10).expires_in_human(), "expired")
        self.assertIn("min", self.entry(expires_at=time.time() + 600).expires_in_human())
        self.assertIn("h", self.entry(expires_at=time.time() + 7200).expires_in_human())
        self.assertIn("days", self.entry(expires_at=time.time() + 300000).expires_in_human())


class TestRoundTrip(TokensCase):
    def test_save_then_read(self):
        tokens.save(self.entry(account_label="@mikefluff"))
        got = tokens.read("threads")
        self.assertIsNotNone(got)
        self.assertEqual(got.access_token, "tok-ABCDEFGHIJKLMNOP")
        self.assertEqual(got.account_label, "@mikefluff")

    def test_read_missing_platform_is_none(self):
        self.assertIsNone(tokens.read("tiktok"))

    def test_save_stamps_obtained_at(self):
        tokens.save(self.entry())
        self.assertGreater(tokens.read("threads").obtained_at, 0)

    def test_save_is_per_platform_not_wholesale(self):
        tokens.save(self.entry("threads"))
        tokens.save(self.entry("telegram", access_token="tg-XXXXXXXXXXXX"))
        self.assertEqual(len(tokens.all_entries()), 2)
        self.assertEqual(tokens.read("threads").access_token, "tok-ABCDEFGHIJKLMNOP")

    def test_remove(self):
        tokens.save(self.entry())
        self.assertTrue(tokens.remove("threads"))
        self.assertIsNone(tokens.read("threads"))
        self.assertFalse(tokens.remove("threads"))

    def test_unknown_fields_in_file_are_ignored(self):
        # A token file written by a future version must not crash this one.
        tokens.TOKENS_FILE.write_text(
            '{"version": 99, "platforms": {"threads": '
            '{"platform": "threads", "access_token": "t", "quantum_field": 1}}}',
            encoding="utf-8",
        )
        self.assertEqual(tokens.read("threads").access_token, "t")


class TestFileSafety(TokensCase):
    def test_file_is_owner_only(self):
        tokens.save(self.entry())
        mode = stat.S_IMODE(tokens.TOKENS_FILE.stat().st_mode)
        self.assertEqual(mode, 0o600, f"token file is {oct(mode)}, expected 0o600")

    def test_corrupt_file_does_not_raise(self):
        tokens.TOKENS_FILE.write_text("{not json at all", encoding="utf-8")
        self.assertEqual(tokens.all_entries(), [])
        self.assertIsNone(tokens.read("threads"))

    def test_corrupt_file_can_be_overwritten(self):
        tokens.TOKENS_FILE.write_text("garbage", encoding="utf-8")
        tokens.save(self.entry())
        self.assertEqual(tokens.read("threads").access_token, "tok-ABCDEFGHIJKLMNOP")

    def test_token_is_never_shown_in_full(self):
        self.assertEqual(self.entry().masked(), "tok-…MNOP")

    def test_status_lines_never_leak_a_token(self):
        tokens.save(self.entry(account_label="@mikefluff"))
        joined = "\n".join(tokens.status_lines())
        self.assertNotIn("tok-ABCDEFGHIJKLMNOP", joined)
        self.assertIn("@mikefluff", joined)

    def test_status_lines_when_empty_tell_you_what_to_run(self):
        self.assertIn("cli.auth", tokens.status_lines()[0])


class TestGetValid(TokensCase):
    def test_missing_token_raises_actionable_error(self):
        with self.assertRaises(TokenError) as ctx:
            tokens.get_valid("threads")
        self.assertIn("cli.auth --platform threads", str(ctx.exception))

    def test_live_token_returned_untouched(self):
        tokens.save(self.entry())
        self.assertEqual(tokens.get_valid("threads"), "tok-ABCDEFGHIJKLMNOP")

    def test_expired_without_refresher_raises(self):
        tokens.save(self.entry(expires_at=time.time() - 10))
        with self.assertRaises(TokenError):
            tokens.get_valid("threads")

    def test_expired_with_refresher_is_renewed_and_persisted(self):
        tokens.save(self.entry(expires_at=time.time() - 10))
        calls = []

        def refresher(old):
            calls.append(old.refresh_token)
            return tokens.TokenEntry(
                platform="threads",
                access_token="tok-NEWNEWNEWNEWNEW",
                refresh_token="ref-2",
                expires_at=time.time() + 86400,
            )

        tokens.register_refresher("threads", refresher)
        self.assertEqual(tokens.get_valid("threads"), "tok-NEWNEWNEWNEWNEW")
        self.assertEqual(calls, ["ref-1"])
        # Persisted, so the next process does not refresh again.
        self.assertEqual(tokens.read("threads").access_token, "tok-NEWNEWNEWNEWNEW")

    def test_refresher_failure_becomes_typed_error(self):
        tokens.save(self.entry(expires_at=time.time() - 10))

        def boom(_old):
            raise RuntimeError("upstream 500")

        tokens.register_refresher("threads", boom)
        with self.assertRaises(TokenError) as ctx:
            tokens.get_valid("threads")
        self.assertIn("upstream 500", str(ctx.exception))

    def test_missing_refresh_token_is_the_refreshers_call_not_this_modules(self):
        # Whether a refresh token is needed is a property of the platform's
        # flow. A guard here previously hardcoded "instagram" as the exception
        # and so made Threads — which refreshes identically — unrefreshable.
        tokens.save(self.entry(expires_at=time.time() - 10, refresh_token=None))
        tokens.register_refresher(
            "threads",
            lambda old: tokens.TokenEntry(
                platform="threads", access_token="th-RENEWEDRENEWED", expires_at=time.time() + 5_000_000
            ),
        )
        self.assertEqual(tokens.get_valid("threads"), "th-RENEWEDRENEWED")

    def test_a_refresher_that_demands_a_refresh_token_still_reports_it(self):
        tokens.save(self.entry(expires_at=time.time() - 10, refresh_token=None))

        def needs_one(old):
            if not old.refresh_token:
                raise RuntimeError("no refresh token stored")
            return old

        tokens.register_refresher("threads", needs_one)
        with self.assertRaises(TokenError) as ctx:
            tokens.get_valid("threads")
        self.assertIn("no refresh token stored", str(ctx.exception))


class TestHasUsable(TokensCase):
    def test_absent(self):
        self.assertFalse(tokens.has_usable("threads"))

    def test_live(self):
        tokens.save(self.entry())
        self.assertTrue(tokens.has_usable("threads"))

    def test_expired_but_refreshable_counts_as_usable(self):
        tokens.save(self.entry(expires_at=time.time() - 10))
        tokens.register_refresher("threads", lambda old: old)
        self.assertTrue(tokens.has_usable("threads"))

    def test_expired_without_refresher_is_not_usable(self):
        tokens.save(self.entry(expires_at=time.time() - 10))
        self.assertFalse(tokens.has_usable("threads"))

    def test_empty_access_token_is_not_usable(self):
        tokens.save(self.entry(access_token=""))
        self.assertFalse(tokens.has_usable("threads"))


if __name__ == "__main__":
    unittest.main()
