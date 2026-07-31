"""Unit tests for the amount parser in common/runners/proposal_parse.py.

proposal-maker's whole promise is "prices stay exact". The offers it reads are
pasted from Telegram, so the same number arrives as `5 154 000`, `5,154,000` or
`1.234,50` depending on who typed it and on which locale. A separator read the
wrong way does not crash — it quietly sends the client a proposal off by three
orders of magnitude.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.proposal_parse import _parse_amount, _norm_currency  # noqa: E402


class TestParseAmount(unittest.TestCase):
    def test_plain_integer(self):
        self.assertEqual(_parse_amount("10000"), 10000.0)

    def test_space_grouped_russian_style(self):
        self.assertEqual(_parse_amount("5 154 000"), 5154000.0)

    def test_non_breaking_and_narrow_spaces(self):
        # Telegram and Word paste U+00A0 / U+202F instead of a plain space.
        self.assertEqual(_parse_amount("5 154 000"), 5154000.0)
        self.assertEqual(_parse_amount("5 154 000"), 5154000.0)

    def test_comma_grouped_english_style(self):
        self.assertEqual(_parse_amount("5,154,000"), 5154000.0)

    def test_comma_as_decimal_when_two_trailing_digits(self):
        self.assertEqual(_parse_amount("1234,50"), 1234.50)

    def test_european_dot_group_comma_decimal(self):
        self.assertEqual(_parse_amount("1.234,50"), 1234.50)

    def test_english_comma_group_dot_decimal(self):
        self.assertEqual(_parse_amount("1,234.50"), 1234.50)

    def test_thousands_comma_is_not_read_as_decimal(self):
        # The dangerous case: 5,154 must be five thousand, not five-point-something.
        self.assertEqual(_parse_amount("5,154"), 5154.0)

    def test_plain_decimal_point(self):
        self.assertEqual(_parse_amount("99.99"), 99.99)

    def test_empty_and_garbage_return_none(self):
        self.assertIsNone(_parse_amount(""))
        self.assertIsNone(_parse_amount("   "))
        self.assertIsNone(_parse_amount("abc"))

    def test_currency_symbols_are_stripped_not_fatal(self):
        self.assertEqual(_parse_amount("10000₽"), 10000.0)
        self.assertEqual(_parse_amount("$1500"), 1500.0)

    def test_zero_is_a_real_value_not_none(self):
        self.assertEqual(_parse_amount("0"), 0.0)


class TestNormCurrency(unittest.TestCase):
    def test_none_and_empty(self):
        self.assertIsNone(_norm_currency(None))
        self.assertIsNone(_norm_currency(""))

    def test_unknown_token_returns_none(self):
        self.assertIsNone(_norm_currency("zzz"))


if __name__ == "__main__":
    unittest.main()
