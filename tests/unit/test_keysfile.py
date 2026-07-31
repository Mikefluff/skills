"""Unit tests for common/runners/keysfile.py — the API-key store.

This module writes secrets to disk, loads them into the process environment, and
prints them back to a terminal. Each of those is a way to leak a key: wrong file
permissions, a mask that shows too much, a shell-export line that breaks quoting,
or file values silently overriding a deliberate shell export.
"""

import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import keysfile  # noqa: E402


class KeysFileCase(unittest.TestCase):
    """Redirects KEYS_FILE at a temp path so no test can touch a real ~/.skills.env."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._saved = keysfile.KEYS_FILE
        keysfile.KEYS_FILE = Path(self._tmp.name) / ".skills.env"

    def tearDown(self):
        keysfile.KEYS_FILE = self._saved
        self._tmp.cleanup()


class TestMask(unittest.TestCase):
    def test_unset_is_labelled_not_blank(self):
        self.assertEqual(keysfile.mask(None), "(unset)")
        self.assertEqual(keysfile.mask(""), "(unset)")

    def test_short_values_are_fully_hidden(self):
        # A short key would be reconstructable from a 4+4 mask, so it shows nothing.
        self.assertEqual(keysfile.mask("abc"), "***")
        self.assertEqual(keysfile.mask("12345678"), "***")

    def test_long_values_show_only_the_ends(self):
        self.assertEqual(keysfile.mask("sk-proj-ABCDEFGHIJKL"), "sk-p…IJKL")

    def test_mask_never_contains_the_middle(self):
        secret = "sk-live-SUPERSECRETMIDDLE-tail"
        self.assertNotIn("SUPERSECRETMIDDLE", keysfile.mask(secret))


class TestReadWrite(KeysFileCase):
    def test_missing_file_reads_as_empty_not_error(self):
        self.assertEqual(keysfile.read_all(), [])
        self.assertIsNone(keysfile.get("ANYTHING"))

    def test_upsert_then_get_roundtrip(self):
        self.assertTrue(keysfile.upsert("OPENAI_API_KEY", "sk-test-123"))
        self.assertEqual(keysfile.get("OPENAI_API_KEY"), "sk-test-123")

    def test_upsert_returns_false_when_replacing(self):
        keysfile.upsert("FAL_KEY", "one")
        self.assertFalse(keysfile.upsert("FAL_KEY", "two"))
        self.assertEqual(keysfile.get("FAL_KEY"), "two")

    def test_replacing_does_not_duplicate_the_entry(self):
        keysfile.upsert("FAL_KEY", "one")
        keysfile.upsert("FAL_KEY", "two")
        names = [e.name for e in keysfile.read_all()]
        self.assertEqual(names.count("FAL_KEY"), 1)

    def test_rejects_invalid_env_var_names(self):
        for bad in ("lowercase", "9LEADING", "has-dash", "has space", ""):
            with self.assertRaises(ValueError, msg=f"accepted {bad!r}"):
                keysfile.upsert(bad, "x")

    def test_comments_and_blank_lines_are_preserved_on_upsert(self):
        keysfile.KEYS_FILE.write_text("# my keys\n\nA_KEY=1\n", encoding="utf-8")
        keysfile.upsert("B_KEY", "2")
        text = keysfile.KEYS_FILE.read_text(encoding="utf-8")
        self.assertIn("# my keys", text)
        self.assertIn("A_KEY=1", text)
        self.assertIn("B_KEY=2", text)

    def test_quoted_values_are_unquoted_on_read(self):
        keysfile.KEYS_FILE.write_text('A="quoted"\nB=\'single\'\n', encoding="utf-8")
        self.assertEqual(keysfile.get("A"), "quoted")
        self.assertEqual(keysfile.get("B"), "single")

    def test_remove_reports_whether_it_removed(self):
        keysfile.upsert("GONE_KEY", "x")
        self.assertTrue(keysfile.remove("GONE_KEY"))
        self.assertFalse(keysfile.remove("GONE_KEY"))
        self.assertIsNone(keysfile.get("GONE_KEY"))

    def test_remove_on_missing_file_is_false_not_error(self):
        self.assertFalse(keysfile.remove("NOPE"))

    def test_file_is_chmod_600_after_write(self):
        keysfile.upsert("SECRET_KEY", "value")
        mode = stat.S_IMODE(keysfile.KEYS_FILE.stat().st_mode)
        self.assertEqual(mode, 0o600, f"expected 0600, got {oct(mode)}")

    def test_no_temp_file_left_behind(self):
        keysfile.upsert("A_KEY", "1")
        leftovers = list(Path(self._tmp.name).glob(".skills.env.*"))
        self.assertEqual(leftovers, [], f"atomic write leaked {leftovers}")


class TestLoadIntoEnv(KeysFileCase):
    def setUp(self):
        super().setUp()
        self._env_saved = {k: os.environ.get(k) for k in ("T_SHELL_WINS", "T_FROM_FILE")}
        for k in self._env_saved:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._env_saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        super().tearDown()

    def test_shell_export_wins_over_file(self):
        # Documented precedence: explicit shell export > ~/.skills.env.
        os.environ["T_SHELL_WINS"] = "from-shell"
        keysfile.upsert("T_SHELL_WINS", "from-file")
        keysfile.load_into_env()
        self.assertEqual(os.environ["T_SHELL_WINS"], "from-shell")

    def test_override_forces_the_file_value(self):
        os.environ["T_SHELL_WINS"] = "from-shell"
        keysfile.upsert("T_SHELL_WINS", "from-file")
        keysfile.load_into_env(override=True)
        self.assertEqual(os.environ["T_SHELL_WINS"], "from-file")

    def test_returns_count_of_variables_actually_loaded(self):
        keysfile.upsert("T_FROM_FILE", "value")
        self.assertEqual(keysfile.load_into_env(), 1)
        # Second call loads nothing new — the value is already in the environment.
        self.assertEqual(keysfile.load_into_env(), 0)

    def test_empty_values_are_not_loaded(self):
        keysfile.KEYS_FILE.write_text("T_FROM_FILE=\n", encoding="utf-8")
        self.assertEqual(keysfile.load_into_env(), 0)
        self.assertNotIn("T_FROM_FILE", os.environ)


class TestExportLines(KeysFileCase):
    def test_masked_export_does_not_leak_the_secret(self):
        keysfile.upsert("OPENAI_API_KEY", "sk-proj-SUPERSECRETVALUE")
        line = keysfile.export_lines(mask_values=True)[0]
        self.assertNotIn("SUPERSECRETVALUE", line)

    def test_unmasked_export_is_shell_evaluable(self):
        keysfile.upsert("A_KEY", "plain-value")
        self.assertEqual(keysfile.export_lines(), ['export A_KEY="plain-value"'])

    def test_quotes_and_backslashes_are_escaped(self):
        # An unescaped quote would terminate the string and turn the rest into
        # shell words — `eval "$(...)"` would then execute them.
        keysfile.upsert("A_KEY", 'has"quote')
        self.assertEqual(keysfile.export_lines(), ['export A_KEY="has\\"quote"'])
        keysfile.upsert("B_KEY", "has\\backslash")
        line = [l for l in keysfile.export_lines() if l.startswith("export B_KEY")][0]
        self.assertEqual(line, 'export B_KEY="has\\\\backslash"')


if __name__ == "__main__":
    unittest.main()
