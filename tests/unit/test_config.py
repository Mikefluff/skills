"""Unit tests for common/runners/config.py — the provider registry.

Every skill with `--execute` resolves its provider through here. The registry is
also what decides whether a provider counts as "available", which is what keeps a
run from starting and failing halfway with a missing key.
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import config  # noqa: E402


class TestResolveEnv(unittest.TestCase):
    def setUp(self):
        self._names = ("T_CFG_A", "T_CFG_B", "T_CFG_MISSING")
        self._saved = {k: os.environ.get(k) for k in self._names}
        for k in self._names:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_returns_only_names_that_are_set(self):
        os.environ["T_CFG_A"] = "value-a"
        got = config.resolve_env("T_CFG_A", "T_CFG_MISSING")
        self.assertEqual(got, {"T_CFG_A": "value-a"})

    def test_missing_names_are_absent_not_empty_strings(self):
        # An empty string would read as "configured" downstream and produce a
        # confusing 401 instead of a clear "key not set".
        got = config.resolve_env("T_CFG_MISSING")
        self.assertNotIn("T_CFG_MISSING", got)

    def test_empty_value_is_treated_as_unset(self):
        os.environ["T_CFG_B"] = ""
        self.assertNotIn("T_CFG_B", config.resolve_env("T_CFG_B"))

    def test_no_names_returns_empty_mapping(self):
        self.assertEqual(config.resolve_env(), {})


class TestRegistry(unittest.TestCase):
    """Exercises the real registry after loading every shipped provider."""

    @classmethod
    def setUpClass(cls):
        config.load_all_providers()

    def test_loading_is_idempotent(self):
        before = len(config.all_providers())
        config.load_all_providers()
        self.assertEqual(len(config.all_providers()), before,
                         "load_all_providers() double-registered on a second call")

    def test_providers_are_registered(self):
        self.assertGreater(len(config.all_providers()), 0)

    def test_unknown_provider_raises_rather_than_returning_none(self):
        with self.assertRaises(Exception):
            config.get_provider("definitely-not-a-provider")

    def test_every_provider_is_retrievable_by_its_own_name(self):
        for p in config.all_providers():
            self.assertIs(config.get_provider(p.name), p)

    def test_provider_names_are_unique(self):
        names = [p.name for p in config.all_providers()]
        self.assertEqual(len(names), len(set(names)), f"duplicate provider names in {names}")

    def test_modality_filter_returns_only_that_modality(self):
        modalities = {p.modality for p in config.all_providers()}
        for m in modalities:
            for p in config.all_providers(m):
                self.assertEqual(p.modality, m)

    def test_available_is_a_subset_of_all(self):
        # available_providers() filters by key presence; it must never invent one.
        all_names = {p.name for p in config.all_providers()}
        avail_names = {p.name for p in config.available_providers()}
        self.assertTrue(avail_names <= all_names)


if __name__ == "__main__":
    unittest.main()
