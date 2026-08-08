"""render_html across every language, theme and brand shape it supports.

The paydown split render.py from its stylesheet and proved the split
byte-identical with a throwaway script: render the same offer across the whole
matrix, sha256 each document, compare before and after. The script was deleted;
the proof is here.

Unlike the cover composition next door, this one can be pinned flat. The output
is text this repo generates from its own fixtures — no font renderer, no image
encoder, nothing outside the tree that can move under it.

The matrix is 2 languages x 3 themes x 6 brands = 36 documents. The brands are
not decorative: each one drops a key the renderer actually reads (logo,
tagline, google fonts), plus a name-only brand and no brand at all.

Regenerate after an intentional change:

    python3 -c "import tests.unit.test_proposal_render as t; t.print_hashes()"

and read the diff of one document before believing the new numbers.
"""

import copy
import hashlib
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.proposal import render as render_mod  # noqa: E402
from common.runners.proposal.parse import parse  # noqa: E402

OFFER = """\
Client: Acme Events
Phone: +66 812 345 678
Date: 12.09.2026
Event: Wedding
Manager: Dasha

Order:
1. Stage truss 6x4 m — 45 000 THB
2. LED screen 3x2 m - 78,500 THB
3. Sound system x2 — 120 000 ฿
4. Logistics — 5 000 000 THB

Total: 5 243 500 THB

Catalogue: https://shop.example.com/catalogue/lighting
сайт: www.example.com
"""

LANGS = ("en", "ru")
THEMES = ("editorial", "dark", "invoice")

# Each brand turns on a different branch of the renderer — and only the keys
# the renderer actually reads count. It reads name, tagline, logo_url,
# google_fonts_url, and url (as a footer fallback). It does NOT read palette,
# which belongs to the stylesheet and the brief, and it reads is_dark only
# through pick_theme when the template is "auto". Building this matrix out of
# palette variations produced six brands and four distinct documents; the test
# below now refuses to let that happen quietly again.
_BASE = {
    "name": "Acme Staging",
    "tagline": "Мы строим сцены",
    "url": "https://acme.example.com",
    "logo_url": "https://acme.example.com/logo.png",
    "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter",
}

BRANDS: dict[str, dict] = {
    "full": dict(_BASE),
    "no_logo": {k: v for k, v in _BASE.items() if k != "logo_url"},
    "no_tagline": {k: v for k, v in _BASE.items() if k != "tagline"},
    "no_fonts": {k: v for k, v in _BASE.items() if k != "google_fonts_url"},
    "name_only": {"name": "Acme Staging"},
    "empty": {},
}

# sha256 of the rendered document, keyed "<brand>/<lang>/<theme>".
DOC_SHA: dict[str, str] = {
    "full/en/editorial": "0425907d003d53801c801ffa11af7f3241376cdb654d33138641e8a7363cdd10",
    "full/en/dark": "11aa644d8760b20538cae2e4cecc8c13045cfe10913a59fc949841e6c1d2c440",
    "full/en/invoice": "6c47767e46fdb12db3af8cb1c19a7850251a0e902465a63c8ec7d546f9826f5d",
    "full/ru/editorial": "87a0eda65d4589ddb797888c93af791da6c864dbc57e87b6aee5d00ef2ba24dc",
    "full/ru/dark": "e5cef5ca7175d565b14a6f9691a657b7ad167adbd8d816bd0524d6232d53042a",
    "full/ru/invoice": "009e46ea07003866bbf394da88eac72cbee15b258b72462e51ceb1c051771a8b",
    "no_logo/en/editorial": "5ec0b6e4fb56eecfe737a083645b9b7e9959d88fad1ed25cf6ad21c471323906",
    "no_logo/en/dark": "f110a9e43d3a3d9848b9ece4ee2160e0d60886df6d98d70ab27aecbf26d74f64",
    "no_logo/en/invoice": "670902dd2d69afd6f3d6dabbf6ee4782a4855d04b54ff0cabdb1d5b139012632",
    "no_logo/ru/editorial": "09b73b2c6e3cfcf207181477911df10937bcb17eee6de2c9ae6874d6b6ca8252",
    "no_logo/ru/dark": "39f1ab7ce92684da32a89d04fcba4c63f30d8182402730c4ae9a0e9a7168b241",
    "no_logo/ru/invoice": "be116b0cc231ebb7ab9563b2fd99a144e7dbe774ae613cdeeae32f19bd897db8",
    "no_tagline/en/editorial": "d8a1e73d3d23355cd07b4dcf0f484132b50264aff140485605dd693e45503f20",
    "no_tagline/en/dark": "56af9e6b559ee9edd7f0ccccb823b76258437e75d8bfc9397e4401344fb0afb1",
    "no_tagline/en/invoice": "6c47767e46fdb12db3af8cb1c19a7850251a0e902465a63c8ec7d546f9826f5d",
    "no_tagline/ru/editorial": "e086272a4c4f957ab2017a9d8876225937f0b4cbe530b5fac073de09f572b404",
    "no_tagline/ru/dark": "4c3a0ef2573e11380cb5ee1d26edd26f474084f6c46457d370d895308419ca31",
    "no_tagline/ru/invoice": "009e46ea07003866bbf394da88eac72cbee15b258b72462e51ceb1c051771a8b",
    "no_fonts/en/editorial": "891cbdb2f6f8221110e83f5ed727bcf03a32595b8c8d2e09ce9676088dcd334c",
    "no_fonts/en/dark": "74365c09a117a6038620627ca657ef45ea08d28f6f48e2b14a7cdbe3017d0d16",
    "no_fonts/en/invoice": "787bae058ab13b742b98aa82c7ca8496f9cbef303a305d559a705b535c1c9f9e",
    "no_fonts/ru/editorial": "b894b8ccfb40f4cd6d72f4eb237540edc55bf347ed1e35146b58a13ed7dc0f23",
    "no_fonts/ru/dark": "7501a817c96afe9c0592ef982c2a17a02b124c744cffa98c3377ca3cd296142a",
    "no_fonts/ru/invoice": "6d2c6f98f821d734c88d5d494bbf2307e5cf92531b5e7247b00698be42b4a191",
    "name_only/en/editorial": "341e2d4025d40d6c4468b10a237a8360dc80f63fa5a7abecebf967c91e334ada",
    "name_only/en/dark": "0ef5fb0dd3b254e3fbace1797caabce54f35ea348ce7a7103475f60e3cee413a",
    "name_only/en/invoice": "d7341c4e3102c4e6158452843ed02232bc1f71bbdc2d3ef5b6800dd7636bf6b2",
    "name_only/ru/editorial": "0285e0b948ad80f66458642a6068ef8ba1b09327e0bb038d8576879ea629207a",
    "name_only/ru/dark": "e6ca886d2ed09afa0b43e70e12612dd84a641fa736a4c152ad4b04a524289c7c",
    "name_only/ru/invoice": "07d66b6061b88705d7545780e7cd8d4b9bde7b5a0e3ed3930951323b601a60d3",
    "empty/en/editorial": "808170396fc25b0cb151d316a6b16dbbf601bede1dc302a06ab3beb998fde643",
    "empty/en/dark": "7ac73d3d06e4354d463fa691c6d06b36703af9698b71e2319cf80c7de5c15c42",
    "empty/en/invoice": "5d0beec88d44ef14e26ba52f6e864bf27ada75fb968f69b2c7e43cca5fc2ad57",
    "empty/ru/editorial": "452b41f1b7d48545a62f3716c2b6b46da38fe592d25d2fc41d443642f25f6af1",
    "empty/ru/dark": "13867577c634a8099bce3cdf4399067bcc6e5ebb572e4796b29f09cd70107b7b",
    "empty/ru/invoice": "a9548becaeb3e64334d51e5e75e52e3250ca3e4413dda84b778146efc29ba9bb",
}


def _plan() -> dict:
    return parse(OFFER)


# The colophon stamps time.strftime("%d.%m.%Y"). Left alone, every hash below
# would be correct for exactly one day. Freezing the clock is what makes this a
# test of the renderer rather than of the calendar.
FROZEN_DATE = "03.08.2026"


def _frozen_strftime(fmt: str, *args) -> str:
    return FROZEN_DATE if fmt == "%d.%m.%Y" else time.strftime(fmt, *args)


def _render(brand_key: str, lang: str, theme: str) -> str:
    # Deep-copied because render_html mutates what it is handed (it rewrites
    # brand["logo_url"] in place when embedding), and a shared fixture would
    # make the matrix order-dependent.
    with mock.patch.object(render_mod.time, "strftime", _frozen_strftime):
        return render_mod.render_html(
            _plan(), copy.deepcopy(BRANDS[brand_key]), lang=lang, template=theme
        )


def _render_brand(brand: dict, lang: str, theme: str) -> str:
    """Same freeze, for the one-off brands the matrix does not carry."""
    with mock.patch.object(render_mod.time, "strftime", _frozen_strftime):
        return render_mod.render_html(_plan(), copy.deepcopy(brand), lang=lang, template=theme)


def _key(brand: str, lang: str, theme: str) -> str:
    return f"{brand}/{lang}/{theme}"


def _matrix():
    for brand in BRANDS:
        for lang in LANGS:
            for theme in THEMES:
                yield brand, lang, theme


def print_hashes() -> None:  # pragma: no cover — developer helper
    print("DOC_SHA: dict[str, str] = {")
    for brand, lang, theme in _matrix():
        digest = hashlib.sha256(_render(brand, lang, theme).encode("utf-8")).hexdigest()
        print(f'    "{_key(brand, lang, theme)}": "{digest}",')
    print("}")


class RenderMatrix(unittest.TestCase):
    def test_the_matrix_is_the_size_it_claims(self):
        self.assertEqual(len(list(_matrix())), 36)

    def test_every_combination_renders_a_document(self):
        for brand, lang, theme in _matrix():
            with self.subTest(brand=brand, lang=lang, theme=theme):
                html = _render(brand, lang, theme)
                self.assertIn("<!doctype html>", html)
                self.assertIn("</html>", html)
                self.assertIn("Acme Events", html, "client name missing")

    def test_rendering_is_deterministic(self):
        for brand, lang, theme in _matrix():
            with self.subTest(brand=brand, lang=lang, theme=theme):
                self.assertEqual(_render(brand, lang, theme), _render(brand, lang, theme))

    def test_language_actually_changes_the_labels(self):
        en = _render("full", "en", "editorial")
        ru = _render("full", "ru", "editorial")
        self.assertNotEqual(en, ru)
        self.assertIn("Коммерческое предложение", ru)
        self.assertNotIn("Коммерческое предложение", en)

    def test_theme_actually_changes_the_document(self):
        seen = {}
        for theme in THEMES:
            html = _render("full", "en", theme)
            self.assertNotIn(html, seen, f"{theme} renders identically to {seen.get(html)}")
            seen[html] = theme

    def test_an_unknown_template_falls_back_rather_than_rendering_unstyled(self):
        fallback = _render_brand(BRANDS["full"], "en", "no-such-theme")
        self.assertEqual(fallback, _render("full", "en", "editorial"))
        self.assertIn("<style", fallback)

    def test_an_empty_brand_still_renders(self):
        # The renderer must not require a brand it could not scrape.
        for lang in LANGS:
            for theme in THEMES:
                with self.subTest(lang=lang, theme=theme):
                    self.assertIn("</html>", _render("empty", lang, theme))

    def test_every_brand_in_the_matrix_is_a_distinct_input(self):
        # A brand axis whose members render alike is not an axis. The first
        # draft of this file varied `palette`, which render_html never reads,
        # and three of six brands produced byte-identical documents.
        seen = {}
        for brand in BRANDS:
            html = _render(brand, "en", "editorial")
            self.assertNotIn(html, seen, f"{brand} renders identically to {seen.get(html)}")
            seen[html] = brand

    def test_palette_is_not_a_render_input(self):
        # Pinned so that a future reader does not add it to this matrix again.
        # The palette drives the stylesheet and the authoring brief, not this.
        with_palette = dict(_BASE, palette=["#101820", "#F2AA4C"])
        self.assertEqual(
            _render_brand(with_palette, "en", "editorial"),
            _render("full", "en", "editorial"),
        )

    def test_is_dark_picks_the_theme_only_when_the_template_is_auto(self):
        auto_dark = _render_brand(dict(_BASE, is_dark=True), "en", "auto")
        self.assertEqual(auto_dark, _render("full", "en", "dark"))
        auto_light = _render_brand(dict(_BASE, is_dark=False), "en", "auto")
        self.assertEqual(auto_light, _render("full", "en", "editorial"))

    def test_the_clock_is_actually_frozen(self):
        # If the freeze stops working — a rename, a different clock source —
        # every hash below drifts once a day and the failure looks like a
        # renderer regression. Assert the freeze itself, separately.
        self.assertIn(f"Generated {FROZEN_DATE}", _render("full", "en", "editorial"))

    def test_documents_match_the_recorded_hashes(self):
        actual = {
            _key(b, la, t): hashlib.sha256(_render(b, la, t).encode("utf-8")).hexdigest()
            for b, la, t in _matrix()
        }
        self.assertEqual(actual, DOC_SHA)


if __name__ == "__main__":
    unittest.main()
