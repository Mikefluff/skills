"""The brand pickers — pure functions over HTML, verified by diff and never by test.

extract() decides what a client's proposal will look like from whatever HTML a
site happens to serve. Every choice it makes is a heuristic with a threshold,
and a heuristic with no test is a number nobody can change safely: the accent
picker in particular exists to avoid choosing #ffffff, which every site has
more of than of its own colour.

So the thresholds are exercised from both sides — a colour just inside a bound
and a colour just outside it — rather than only on a happy case.

extract() itself is driven with _get patched. It is documented as never
raising, and the tests hold it to that on input designed to be hostile.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.proposal import brand  # noqa: E402


class CollectColors(unittest.TestCase):
    def test_hex_and_rgb_are_counted_together(self):
        html = "<style>a{color:#FF0000}b{color:rgb(255, 0, 0)}</style>"
        self.assertEqual(brand._collect_colors(html), [("#ff0000", 2)])

    def test_three_digit_hex_expands(self):
        self.assertEqual(brand._collect_colors("#f00"), [("#ff0000", 1)])

    def test_ordering_is_by_frequency(self):
        html = "#111111 #111111 #111111 #222222 #222222 #333333"
        self.assertEqual(
            [h for h, _ in brand._collect_colors(html)],
            ["#111111", "#222222", "#333333"],
        )

    def test_rgb_channels_over_255_are_clamped_not_crashed(self):
        self.assertEqual(brand._collect_colors("rgb(999,0,0)"), [("#ff0000", 1)])

    def test_rgba_is_read_like_rgb(self):
        self.assertEqual(brand._collect_colors("rgba(0,128,255,0.5)"), [("#0080ff", 1)])


class AccentPicker(unittest.TestCase):
    """The reason this module has thresholds at all."""

    def test_white_and_black_never_win_however_common(self):
        colors = [("#ffffff", 900), ("#000000", 800), ("#f2aa4c", 3)]
        accent, _second = brand._accents(colors)
        self.assertEqual(accent, "#f2aa4c")

    def test_a_grey_is_not_an_accent(self):
        # Saturation below the floor — grey is chrome, not brand.
        accent, second = brand._accents([("#808080", 500), ("#7f7f80", 400)])
        self.assertIsNone(accent)
        self.assertIsNone(second)

    def test_frequency_beats_vividness(self):
        # A brand's colour is the one it uses, not the loudest one on the page.
        accent, _ = brand._accents([("#4c6ef2", 50), ("#ff0000", 10)])
        self.assertEqual(accent, "#4c6ef2")

    def test_the_second_accent_is_a_different_colour(self):
        accent, second = brand._accents([("#f2aa4c", 50), ("#f2aa4c", 40), ("#4c6ef2", 30)])
        self.assertEqual(accent, "#f2aa4c")
        self.assertNotEqual(second, accent)

    def test_a_single_saturated_colour_leaves_the_second_empty(self):
        accent, second = brand._accents([("#f2aa4c", 50), ("#ffffff", 900)])
        self.assertEqual(accent, "#f2aa4c")
        self.assertIsNone(second)

    def test_the_saturation_floor_is_exercised_from_both_sides(self):
        floor = brand.MIN_ACCENT_SATURATION
        for hexv, sat_expected in (("#f2aa4c", True), ("#808080", False)):
            with self.subTest(color=hexv):
                sat = brand._saturation(brand._rgb(hexv))
                self.assertEqual(sat >= floor, sat_expected, f"{hexv} saturation {sat:.2f}")

    def test_nothing_saturated_means_no_accent(self):
        self.assertEqual(brand._accents([]), (None, None))


class BackgroundPicker(unittest.TestCase):
    def test_a_light_site_gets_its_light_background(self):
        self.assertEqual(brand._background([("#ffffff", 500), ("#000000", 10)]), "#ffffff")

    def test_a_dark_dominant_site_gets_its_dark_background(self):
        # Dark must beat light by more than half again before it wins.
        self.assertEqual(brand._background([("#0b0b0b", 500), ("#ffffff", 100)]), "#0b0b0b")

    def test_a_dark_site_that_only_narrowly_leads_stays_light(self):
        # 120 is not more than 100 * 1.5, so the light background holds.
        self.assertEqual(brand._background([("#0b0b0b", 120), ("#ffffff", 100)]), "#ffffff")

    def test_no_recognisable_background_falls_back_to_white(self):
        self.assertEqual(brand._background([("#f2aa4c", 10)]), "#ffffff")


class PickPalette(unittest.TestCase):
    def test_a_dark_background_flips_the_text_colour(self):
        pal = brand._pick_palette([("#0b0b0b", 500), ("#ffffff", 10), ("#f2aa4c", 20)])
        self.assertTrue(pal["is_dark"])
        self.assertEqual(pal["text"], "#f5f5f5")

    def test_a_light_background_keeps_dark_text(self):
        pal = brand._pick_palette([("#ffffff", 500), ("#f2aa4c", 20)])
        self.assertFalse(pal["is_dark"])
        self.assertEqual(pal["text"], "#111111")

    def test_no_accent_at_all_falls_back_to_the_default(self):
        pal = brand._pick_palette([("#ffffff", 500), ("#808080", 100)])
        self.assertEqual(pal["accent"], brand.DEFAULT_ACCENT)
        self.assertEqual(pal["accent2"], brand.DEFAULT_ACCENT)

    def test_a_lone_accent_is_reused_as_the_secondary(self):
        pal = brand._pick_palette([("#ffffff", 500), ("#f2aa4c", 20)])
        self.assertEqual(pal["accent"], "#f2aa4c")
        self.assertEqual(pal["accent2"], "#f2aa4c")

    def test_an_empty_page_still_yields_a_usable_palette(self):
        pal = brand._pick_palette([])
        self.assertEqual(pal["accent"], brand.DEFAULT_ACCENT)
        self.assertEqual(pal["bg"], "#ffffff")


class FontPicker(unittest.TestCase):
    def test_a_google_link_outranks_a_css_declaration(self):
        html = (
            '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap">'
            "<style>body{font-family:Georgia, serif}</style>"
        )
        picked = brand._pick_fonts(html)
        self.assertEqual(picked["font_heading"], "Playfair Display")
        self.assertEqual(picked["font_body"], "Georgia")
        self.assertIn("fonts.googleapis.com", picked["google_fonts_url"])

    def test_generic_families_are_not_brand_fonts(self):
        html = "<style>a{font-family:sans-serif}b{font-family:Georgia}</style>"
        self.assertEqual(brand._pick_fonts(html)["font_heading"], "Georgia")

    def test_the_system_stack_is_treated_as_generic_not_as_a_brand_face(self):
        # Helvetica, Arial and Roboto are in _GENERIC_FONTS: a site that
        # declares them has not chosen a typeface, it has declined to. Naming
        # one as the brand font would put a default on a client's proposal and
        # call it branding. (This caught a wrong test, not wrong code — the
        # first draft expected Helvetica to win.)
        for generic in ("Helvetica", "Arial", "Roboto", "Segoe UI", "system-ui"):
            with self.subTest(font=generic):
                html = f"<style>a{{font-family:{generic}, sans-serif}}</style>"
                self.assertIsNone(brand._pick_fonts(html)["font_heading"])

    def test_matching_is_case_insensitive_for_generics(self):
        self.assertIsNone(brand._pick_fonts("<style>a{font-family:ARIAL}</style>")["font_heading"])

    def test_body_falls_back_to_heading_when_only_one_face_exists(self):
        picked = brand._pick_fonts("<style>h1{font-family:Georgia}</style>")
        self.assertEqual(picked["font_heading"], "Georgia")
        self.assertEqual(picked["font_body"], "Georgia")

    def test_no_fonts_at_all_is_none_not_a_crash(self):
        picked = brand._pick_fonts("<p>no styles here</p>")
        self.assertIsNone(picked["font_heading"])
        self.assertIsNone(picked["font_body"])
        self.assertIsNone(picked["google_fonts_url"])

    def test_an_absurdly_long_family_name_is_rejected(self):
        # A minified blob can produce a "family" hundreds of characters long.
        long_name = "A" * (brand.MAX_FONT_NAME_CHARS + 1)
        html = f"<style>a{{font-family:{long_name}}}b{{font-family:Georgia}}</style>"
        self.assertEqual(brand._pick_fonts(html)["font_heading"], "Georgia")

    def test_weight_suffixes_are_stripped_from_google_families(self):
        url = "https://fonts.googleapis.com/css2?family=Inter:wght@400;700"
        self.assertEqual(brand._google_families(url), ["Inter"])

    def test_two_google_families_become_heading_and_body(self):
        html = '<link href="https://fonts.googleapis.com/css2?family=Inter&family=Lora">'
        picked = brand._pick_fonts(html)
        self.assertEqual(picked["font_heading"], "Inter")
        self.assertEqual(picked["font_body"], "Lora")


class GoogleFontsLink(unittest.TestCase):
    def test_spaces_become_plus(self):
        link = brand.google_fonts_link(["Playfair Display"])
        self.assertIn("family=Playfair+Display", link)

    def test_duplicates_collapse(self):
        link = brand.google_fonts_link(["Inter", "Inter"])
        self.assertEqual(link.count("family=Inter"), 1)

    def test_nones_are_dropped_and_an_empty_list_is_none(self):
        self.assertIsNone(brand.google_fonts_link([None, None]))
        self.assertIsNone(brand.google_fonts_link([]))


class LogoPicker(unittest.TestCase):
    BASE = "https://acme.example.com"

    def test_an_img_that_says_logo_beats_a_generic_og_image(self):
        html = (
            '<meta property="og:image" content="https://acme.example.com/hero.jpg">'
            '<img src="/assets/logo.svg" alt="Acme">'
        )
        self.assertEqual(brand._pick_logo(html, self.BASE), f"{self.BASE}/assets/logo.svg")

    def test_a_relative_src_is_made_absolute(self):
        html = '<img class="brand" src="img/mark.png">'
        self.assertEqual(brand._pick_logo(html, self.BASE), f"{self.BASE}/img/mark.png")

    def test_a_data_uri_logo_is_skipped(self):
        html = '<img class="logo" src="data:image/png;base64,AAAA">'
        self.assertIsNone(brand._pick_logo(html, self.BASE))

    def test_og_image_is_the_fallback(self):
        html = '<meta property="og:image" content="https://cdn.example.com/og.png">'
        self.assertEqual(brand._pick_logo(html, self.BASE), "https://cdn.example.com/og.png")

    def test_a_favicon_is_the_last_resort(self):
        html = '<link rel="apple-touch-icon" href="/touch.png">'
        self.assertEqual(brand._pick_logo(html, self.BASE), f"{self.BASE}/touch.png")

    def test_nothing_at_all_is_none(self):
        self.assertIsNone(brand._pick_logo("<p>bare</p>", self.BASE))


class BrandName(unittest.TestCase):
    def test_a_tagline_after_a_separator_is_trimmed(self):
        for sep in (" — ", " - ", " | ", " · ", ": "):
            with self.subTest(sep=sep):
                html = f"<title>Acme Staging{sep}we build stages</title>"
                self.assertEqual(brand._brand_name(html), "Acme Staging")

    def test_og_site_name_wins_over_the_title(self):
        html = '<meta property="og:site_name" content="Acme"><title>Something else</title>'
        self.assertEqual(brand._brand_name(html), "Acme")

    def test_a_title_with_no_separator_survives_whole(self):
        self.assertEqual(brand._brand_name("<title>Acme Staging</title>"), "Acme Staging")

    def test_nothing_to_go_on_is_none(self):
        self.assertIsNone(brand._brand_name("<p>no title</p>"))


PAGE = """\
<html><head>
<title>Acme Staging — we build stages</title>
<meta property="og:site_name" content="Acme Staging">
<meta property="og:description" content="Мы строим сцены">
<meta property="og:image" content="https://acme.example.com/hero.jpg">
<link href="https://fonts.googleapis.com/css2?family=Inter&family=Lora">
<style>
  body{background:#ffffff;color:#111111;font-family:Inter,sans-serif}
  .cta{background:#f2aa4c}.cta:hover{background:#f2aa4c}.badge{color:#f2aa4c}
  .alt{color:#4c6ef2}
</style>
</head><body><img class="logo" src="/logo.svg"></body></html>
"""


class Extract(unittest.TestCase):
    """The public entry point. Documented as never raising."""

    def extract(self, page, url="https://acme.example.com"):
        with mock.patch.object(brand, "_get", return_value=page):
            return brand.extract(url)

    def test_a_normal_page_yields_every_token(self):
        out = self.extract(PAGE)
        self.assertTrue(out["ok"])
        self.assertEqual(out["url"], "https://acme.example.com")
        self.assertEqual(out["name"], "Acme Staging")
        self.assertEqual(out["tagline"], "Мы строим сцены")
        self.assertEqual(out["accent"], "#f2aa4c")
        self.assertEqual(out["font_heading"], "Inter")
        self.assertEqual(out["font_body"], "Lora")
        self.assertEqual(out["logo_url"], "https://acme.example.com/logo.svg")
        self.assertEqual(out["hero_url"], "https://acme.example.com/hero.jpg")
        self.assertFalse(out["is_dark"])

    def test_an_unreachable_site_returns_defaults_with_ok_false(self):
        out = self.extract(None)
        self.assertFalse(out["ok"])
        self.assertEqual(out["accent"], "#1f6feb")
        self.assertEqual(out["bg"], "#ffffff")
        self.assertIsNone(out["name"])

    def test_a_bare_domain_is_given_a_scheme(self):
        out = self.extract(PAGE, url="acme.example.com")
        self.assertEqual(out["url"], "https://acme.example.com")

    def test_the_url_is_reduced_to_its_origin(self):
        out = self.extract(PAGE, url="https://acme.example.com/deep/page?x=1")
        self.assertEqual(out["url"], "https://acme.example.com")

    def test_a_google_link_is_synthesised_when_only_css_names_the_font(self):
        page = "<style>h1{font-family:Georgia}</style>"
        out = self.extract(page)
        self.assertEqual(out["font_heading"], "Georgia")
        self.assertIn("family=Georgia", out["google_fonts_url"])

    def test_hostile_input_does_not_raise(self):
        # The contract is "always returns a dict (never raises)".
        for page in ("", "<", "\x00\x01\x02", "#" * 5000, "rgb(,,)", "<img src=", "<title>"):
            with self.subTest(page=page[:12]):
                out = self.extract(page)
                self.assertIsInstance(out, dict)
                self.assertIn("accent", out)

    def test_every_documented_key_is_present_on_both_paths(self):
        keys = set(self.extract(None))
        self.assertEqual(keys, set(self.extract(PAGE)), "ok and not-ok return different shapes")


if __name__ == "__main__":
    unittest.main()
