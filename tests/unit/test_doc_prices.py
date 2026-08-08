"""Every price a skill quotes has to be derivable from the table that bills it.

`common/references/model-pricing.md` is generated, so it cannot drift. The
skills quote prices somewhere else entirely — in decision tables, in worked
examples, in the sentence that tells you whether a batch will trip the budget —
and 153 such claims were written by hand. Thirteen had gone stale by the time
this test was added: `nano-banana-pro` advertised at $0.05 an image against a
$0.134 charge, a nine-image thumbnail batch quoted at $0.45 that bills $1.21,
`veo-3-1` priced per clip against a per-second table.

The suite already refuses to let a model id rot silently (`test_model_registry`).
This is the same guarantee one layer out: the number the user reads before
deciding to spend money.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# scripts/ names its files with hyphens, so the checker is loaded by path rather
# than imported. Keeping it a script keeps it next to gen-pricing.py, which is
# the thing it enforces.
_spec = importlib.util.spec_from_file_location("check_prices", ROOT / "scripts" / "check-prices.py")
check_prices = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_prices)


class TestQuotedPrices(unittest.TestCase):
    def test_no_doc_contradicts_the_price_table(self):
        failures, checked = check_prices.audit()
        self.assertGreater(checked, 100, "the scan found almost nothing — it is broken, not clean")
        self.assertEqual(
            [],
            failures,
            "\n\n" + "\n".join(failures) + "\n\nRun: make check-prices",
        )


class TestExplains(unittest.TestCase):
    """The arithmetic the checker allows, pinned so it stays deliberate."""

    UNITS = {"per_image": 0.134}

    def test_unit_price_matches(self):
        self.assertIsNotNone(check_prices._explains(0.134, self.UNITS, {1}))

    def test_declared_batch_matches_with_rounding(self):
        # 8 x 0.134 is 1.072, and every doc writes $1.07.
        self.assertIsNotNone(check_prices._explains(1.07, self.UNITS, {1, 8}))

    def test_undeclared_batch_is_rejected(self):
        # The whole point: a batch total only passes where the file says so.
        self.assertIsNone(check_prices._explains(1.07, self.UNITS, {1}))

    def test_fractional_batch_covers_sub_unit_billing(self):
        # lyria-3-clip bills per minute and every skill quotes the 30-second clip.
        self.assertIsNotNone(check_prices._explains(0.05, {"per_minute": 0.10}, {1, 0.5}))

    def test_a_wrong_number_stays_wrong_at_any_batch(self):
        self.assertIsNone(check_prices._explains(0.05, self.UNITS, None))


class TestScope(unittest.TestCase):
    """What counts as a directive, and what counts as a claim."""

    def _claims(self, text: str):
        path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "doc.md"
        path.write_text(text, encoding="utf-8")
        return list(check_prices._claims(path))

    def test_a_quoted_directive_declares_nothing(self):
        # The roadmap documents the syntax. Parsing that as a declaration made
        # the checker fail on its own instructions.
        claims = self._claims(
            "Declare it with `<!-- prices: batch=N -->`.\n| nano-banana-pro | $1.07 |\n"
        )
        self.assertEqual([2], [c.lineno for c in claims], "the prose line declares nothing")
        # $1.07 is 8 x $0.134, and no batch of 8 was declared — so it must fail.
        self.assertIsNone(check_prices._derivation(claims[0]))

    def test_a_backticked_slug_is_still_a_claim(self):
        # Slugs are normally written in code spans, so ignoring them wholesale
        # would have quietly dropped two thirds of the coverage.
        claims = self._claims("| `nano-banana-pro` | $0.99 |\n")
        self.assertEqual(1, len(claims))
        self.assertIsNone(check_prices._derivation(claims[0]))

    def test_prices_inside_a_fence_are_still_checked(self):
        claims = self._claims("```\nCalling veo-3-1-fast (est cost $9.9900)...\n```\n")
        self.assertEqual(1, len(claims))
        self.assertIsNone(check_prices._derivation(claims[0]))


class TestDirectives(unittest.TestCase):
    def test_batch_list(self):
        mode, batches = check_prices._parse_directive("batch=3,9")
        self.assertEqual("batch", mode)
        self.assertEqual({1, 3, 9}, batches)

    def test_any_is_unbounded(self):
        self.assertEqual(("batch", None), check_prices._parse_directive("batch=any"))

    def test_ignore_may_carry_its_reason(self):
        mode, _ = check_prices._parse_directive("ignore — a pipeline total, not one model's rate")
        self.assertEqual("ignore", mode)

    def test_a_typo_is_an_error_not_a_silent_pass(self):
        with self.assertRaises(ValueError):
            check_prices._parse_directive("batsh=3")


if __name__ == "__main__":
    unittest.main()
