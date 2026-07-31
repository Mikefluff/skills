"""Unit tests for common/runners/cost.py — the module that guards user money.

Every provider call routes through estimate() and confirm(). A wrong multiplier
here does not fail loudly; it silently bills the user more than they agreed to.
That makes this the highest-value module in the runner layer to pin down.
"""

import io
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import cost  # noqa: E402
from common.runners.errors import CostConfirmationDeclined  # noqa: E402


class TestEstimate(unittest.TestCase):
    def test_unknown_provider_returns_none_not_zero(self):
        # None means "unknown", which callers must not confuse with "free".
        self.assertIsNone(cost.estimate("no-such-model"))

    def test_per_image_scales_with_variants(self):
        self.assertEqual(cost.estimate("nano-banana-pro"), Decimal("0.05"))
        self.assertEqual(cost.estimate("nano-banana-pro", variants=4), Decimal("0.20"))

    def test_variants_zero_or_none_treated_as_one(self):
        # `int(kwargs.get("variants", 1) or 1)` — a falsy variants must not zero the bill.
        self.assertEqual(cost.estimate("imagen-4", variants=0), Decimal("0.04"))
        self.assertEqual(cost.estimate("imagen-4", variants=None), Decimal("0.04"))

    def test_per_second_uses_duration_and_defaults_to_eight(self):
        self.assertEqual(cost.estimate("veo-3-1", duration_seconds=10), Decimal("4.0"))
        # Default duration is 8s — a caller that forgets the kwarg still gets a real number.
        self.assertEqual(cost.estimate("veo-3-1-fast"), Decimal("1.20"))

    def test_per_minute_uses_duration_minutes(self):
        self.assertEqual(cost.estimate("whisper-1", duration_minutes=10), Decimal("0.060"))

    def test_per_1k_chars_is_fractional_not_rounded_up(self):
        # 500 chars must cost half of 1k, not a full unit.
        self.assertEqual(cost.estimate("eleven-tts", char_count=500), Decimal("0.075"))

    def test_quality_tier_selection(self):
        self.assertEqual(cost.estimate("gpt-image-2", quality="low"), Decimal("0.02"))
        self.assertEqual(cost.estimate("gpt-image-2", quality="high"), Decimal("0.10"))
        # Unspecified quality falls back to medium, never to the cheapest tier.
        self.assertEqual(cost.estimate("gpt-image-2"), Decimal("0.05"))

    def test_unknown_quality_returns_none_rather_than_guessing(self):
        self.assertIsNone(cost.estimate("gpt-image-2", quality="ultra"))

    def test_price_table_has_no_zero_or_negative_prices(self):
        for model, entry in cost.PRICE_TABLE.items():
            for unit, price in entry.items():
                self.assertGreater(price, Decimal("0"), f"{model}.{unit} is not positive")


class _StdIO:
    """Swap stdin/stderr around a confirmation prompt."""

    def __init__(self, answer: str):
        self.answer = answer
        self.err = io.StringIO()

    def __enter__(self):
        self._stdin, self._stderr = sys.stdin, sys.stderr
        sys.stdin, sys.stderr = io.StringIO(self.answer), self.err
        return self

    def __exit__(self, *exc):
        sys.stdin, sys.stderr = self._stdin, self._stderr
        return False


class TestConfirm(unittest.TestCase):
    def test_below_threshold_never_prompts(self):
        with _StdIO("") as io_:
            cost.confirm(Decimal("0.05"))
        self.assertEqual(io_.err.getvalue(), "")

    def test_unknown_cost_never_prompts(self):
        with _StdIO("") as io_:
            cost.confirm(None)
        self.assertEqual(io_.err.getvalue(), "")

    def test_yes_flag_skips_prompt_even_when_expensive(self):
        with _StdIO("") as io_:
            cost.confirm(Decimal("99.00"), yes=True)
        self.assertEqual(io_.err.getvalue(), "")

    def test_accepts_y_and_yes(self):
        for answer in ("y\n", "yes\n", "Y\n", "YES\n"):
            with _StdIO(answer):
                cost.confirm(Decimal("5.00"))  # must not raise

    def test_declines_on_anything_else(self):
        for answer in ("n\n", "no\n", "maybe\n", "\n"):
            with _StdIO(answer):
                with self.assertRaises(CostConfirmationDeclined):
                    cost.confirm(Decimal("5.00"))

    def test_empty_stdin_declines(self):
        # Non-interactive context (CI, piped input): readline() returns "".
        # Failing closed is the correct default — never bill without an answer.
        with _StdIO(""):
            with self.assertRaises(CostConfirmationDeclined):
                cost.confirm(Decimal("5.00"))

    def test_exactly_at_threshold_prompts(self):
        # Guard against the boundary silently flipping from `<` to `<=`.
        with _StdIO("n\n"):
            with self.assertRaises(CostConfirmationDeclined):
                cost.confirm(cost.CONFIRMATION_THRESHOLD)


class TestBatchBudget(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in cost._BUDGET_ENV_OVERRIDE.values()}
        for k in self._saved:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_defaults(self):
        self.assertEqual(cost.batch_budget("carousel"), Decimal("1.50"))
        self.assertEqual(cost.batch_budget("reel"), Decimal("4.00"))

    def test_unknown_modality_returns_none(self):
        self.assertIsNone(cost.batch_budget("nope"))

    def test_env_override_wins(self):
        os.environ["SKILLS_CAROUSEL_BUDGET"] = "9.99"
        self.assertEqual(cost.batch_budget("carousel"), Decimal("9.99"))

    def test_malformed_env_override_falls_back_to_default(self):
        # A typo in the env var must not remove the guard rail entirely.
        os.environ["SKILLS_REEL_BUDGET"] = "not-a-number"
        self.assertEqual(cost.batch_budget("reel"), Decimal("4.00"))


class TestConfirmBatch(unittest.TestCase):
    def test_under_threshold_is_silent(self):
        with _StdIO("") as io_:
            cost.confirm_batch(Decimal("0.01"), n_items=3, modality="carousel")
        self.assertEqual(io_.err.getvalue(), "")

    def test_yes_flag_skips(self):
        with _StdIO("") as io_:
            cost.confirm_batch(Decimal("50.00"), n_items=9, modality="reel", yes=True)
        self.assertEqual(io_.err.getvalue(), "")

    def test_declines_raise(self):
        with _StdIO("n\n"):
            with self.assertRaises(CostConfirmationDeclined):
                cost.confirm_batch(Decimal("2.00"), n_items=8, modality="carousel")

    def test_over_budget_warns_and_names_the_override(self):
        with _StdIO("y\n") as io_:
            cost.confirm_batch(Decimal("3.00"), n_items=8, modality="carousel")
        err = io_.err.getvalue()
        self.assertIn("WARNING", err)
        self.assertIn("SKILLS_CAROUSEL_BUDGET", err)

    def test_within_budget_does_not_warn(self):
        with _StdIO("y\n") as io_:
            cost.confirm_batch(Decimal("1.00"), n_items=5, modality="carousel")
        self.assertNotIn("WARNING", io_.err.getvalue())

    def test_item_count_is_reported(self):
        with _StdIO("y\n") as io_:
            cost.confirm_batch(Decimal("1.00"), n_items=7, modality="carousel")
        self.assertIn("7 carousel items", io_.err.getvalue())


if __name__ == "__main__":
    unittest.main()
