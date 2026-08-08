"""Unit tests for the amount parser in common/runners/proposal/parse.py.

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

from common.runners.proposal.parse import _norm_currency, _parse_amount, parse  # noqa: E402


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


OFFER = """\
\U0001f4cb Client: Acme Events
Phone: +66 812 345 678
Date: 12.09.2026
Event: Wedding
Manager: Dasha

\U0001f9fe Order:
1. Stage truss 6x4 m — 45 000 THB
2. LED screen 3x2 m - 78,500 THB
3. Sound system x2 — 120 000 ฿
4. Logistics — 5 000 000 THB

Total: 5 243 500 THB

Catalogue: https://shop.example.com/catalogue/lighting
сайт: www.example.com
"""


class TestParse(unittest.TestCase):
    """The whole-offer path: sections, footer, currency vote, outlier flagging."""

    def setUp(self):
        self.plan = parse(OFFER)

    def test_known_header_fields_land_in_client(self):
        self.assertEqual(self.plan["client"]["name"], "Acme Events")
        self.assertEqual(self.plan["client"]["phone"], "+66 812 345 678")
        self.assertEqual(self.plan["client"]["event"], "Wedding")

    def test_unrecognised_header_fields_are_kept_not_dropped(self):
        # An unknown label is still information the proposal may want.
        self.assertEqual(self.plan["extra_fields"].get("manager"), "Dasha")

    def test_every_order_line_becomes_an_item(self):
        self.assertEqual(len(self.plan["items"]), 4)

    def test_leading_emoji_does_not_hide_the_order_header(self):
        # Offers are pasted from Telegram, where every section starts with one.
        self.assertTrue(self.plan["items"], "order section was never entered")

    def test_thin_and_grouped_separators_parse_to_the_same_number(self):
        prices = [i["price"] for i in self.plan["items"]]
        self.assertEqual(prices, [45000.0, 78500.0, 120000.0, 5000000.0])

    def test_currency_is_a_majority_vote_across_items(self):
        # One line used ฿ rather than THB; the vote still resolves to THB and
        # backfills it onto any item that named none.
        self.assertEqual(self.plan["currency"], "THB")
        self.assertTrue(all(i["currency"] == "THB" for i in self.plan["items"]))

    def test_subtotal_is_computed_not_trusted(self):
        self.assertEqual(self.plan["subtotal_computed"], 5243500.0)
        self.assertEqual(self.plan["total_stated"], 5243500.0)
        self.assertFalse(self.plan["total_mismatch"])

    def test_stated_total_that_disagrees_is_flagged(self):
        plan = parse(OFFER.replace("Total: 5 243 500 THB", "Total: 9 000 000 THB"))
        self.assertTrue(plan["total_mismatch"])
        # Flagged, never silently corrected.
        self.assertEqual(plan["subtotal_computed"], 5243500.0)

    def test_dominant_line_is_flagged_as_an_outlier(self):
        outliers = self.plan["price_outliers"]
        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers[0]["index"], 3)
        self.assertGreater(outliers[0]["share"], 0.9)

    def test_short_orders_are_not_outlier_checked(self):
        # With three lines a 60% share is ordinary, not a typo.
        short = "Order:\n1. A — 10 THB\n2. B — 1000 THB\n"
        self.assertEqual(parse(short)["price_outliers"], [])

    def test_footer_urls(self):
        self.assertEqual(
            self.plan["footer"]["catalog_url"],
            "https://shop.example.com/catalogue/lighting",
        )
        self.assertEqual(self.plan["footer"]["site_url"], "https://www.example.com")

    def test_site_url_falls_back_to_the_catalogue_origin(self):
        plan = parse(OFFER.replace("сайт: www.example.com", ""))
        self.assertEqual(plan["footer"]["site_url"], "https://shop.example.com")

    def test_empty_offer_does_not_raise(self):
        plan = parse("")
        self.assertEqual(plan["items"], [])
        self.assertEqual(plan["subtotal_computed"], 0)
        self.assertIsNone(plan["total_stated"])
        self.assertFalse(plan["total_mismatch"])

    def test_schema_is_stamped(self):
        self.assertEqual(self.plan["schema"], "skills.proposal.plan.v1")


if __name__ == "__main__":
    unittest.main()
