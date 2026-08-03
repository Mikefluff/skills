"""write_brief across screenshot x logo x language, over a difficult offer.

The third of the paydown's throwaway proofs. proposal_brief.py was split out of
proposal_kit.py and verified byte-identical by rendering the brief across every
combination of the three things BriefContext carries, then hashing. The script
is gone; this is the same harness, committed.

The offer is chosen to be awkward on purpose. The brief's job is to warn the
orchestrator about an offer that does not add up, so an offer that adds up
proves nothing about the half of the code that matters: this one states a total
that disagrees with its own items, and carries an item two orders of magnitude
above the rest.

Pinned flat — the output is markdown built from fixtures in this file, with no
clock, no font renderer and no network in the path.

Regenerate after an intentional change:

    python3 -c "import tests.unit.test_proposal_brief as t; t.print_hashes()"
"""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import proposal_brief as brief_mod  # noqa: E402
from common.runners.proposal_parse import parse  # noqa: E402

# Stated total is 200 000 while the items sum to 5 243 500 — a mismatch the
# brief must surface — and Logistics is the outlier at 5 000 000.
OFFER = """\
Client: Acme Events
Phone: +66 812 345 678
Date: 12.09.2026
Event: Wedding
Manager: Dasha

Order:
1. Stage truss 6x4 m — 45 000 THB
2. LED screen 3x2 m - 78,500 THB
3. Sound system x2 — 120 000 THB
4. Logistics — 5 000 000 THB

Total: 200 000 THB

Catalogue: https://shop.example.com/catalogue/lighting
сайт: www.example.com
"""

BRAND = {
    "name": "Acme Staging",
    "tagline": "Мы строим сцены",
    "url": "https://acme.example.com",
    "logo_url": "https://acme.example.com/logo.png",
    "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter",
    "accent": "#F2AA4C",
    "accent2": "#101820",
    "bg": "#FFFFFF",
    "text": "#16181D",
    "is_dark": False,
    "font_heading": "Inter",
    "font_body": "Inter",
}

SCREENSHOTS = (None, Path("/tmp/brand/shot.png"))
LOGOS = (None, Path("/tmp/brand/logo.svg"))
LANGS = ("en", "ru")

# sha256 of the written brief, keyed "<screenshot>/<logo>/<lang>".
DOC_SHA: dict[str, str] = {
    "noshot/nologo/en": "e6425fa686c5d903e266b9b5e70863d6c38ddcedfad4897b7e54c39b6d9898e1",
    "noshot/nologo/ru": "b0b5a6cd5040dfe907cf6c244dd8d2c26c72c4c496a08a32fa61886b2e99e3ae",
    "noshot/logo/en": "d10418a42a131c8787f12ec647aaabf7a59522782a66ad8d5afc1751e3d4b57b",
    "noshot/logo/ru": "dfaa53dadd74d79baf5e7fa581a9b8c396d5244eae0ef7cddc9521b436d10838",
    "shot/nologo/en": "03df0ddebc400ac2f3cec20a68e8479cfd31c6506f157adbdcd2a0fc1870a802",
    "shot/nologo/ru": "134434581c3a6817477972096856a13a2fbab7767e3efc03a73b7f6e5fbf03f9",
    "shot/logo/en": "e292ab6161f8b37fffbe966a4f3d4281ab8043af54e2c1a2b3387b9454e14d7a",
    "shot/logo/ru": "384db77a5c725c58485790a11654bfb032407816682d0ba21ff97d28ee265264",
}


def _key(shot, logo, lang) -> str:
    return f"{'shot' if shot else 'noshot'}/{'logo' if logo else 'nologo'}/{lang}"


def _matrix():
    for shot in SCREENSHOTS:
        for logo in LOGOS:
            for lang in LANGS:
                yield shot, logo, lang


def _write(shot, logo, lang) -> str:
    """Write the brief to a scratch dir and return it.

    The brief embeds its own parent directory in the authoring steps, so the
    path has to be stable across runs or every hash moves. A fixed name under
    one temporary root gives that without writing into the repo.
    """
    with tempfile.TemporaryDirectory() as tmp:
        # The folder name is interpolated into the document; normalise it so
        # the hash is of the brief, not of mkdtemp's random suffix.
        folder = Path(tmp) / "proposal"
        folder.mkdir()
        path = folder / "BRIEF.md"
        brief_mod.write_brief(
            path,
            parse(OFFER),
            dict(BRAND),
            brief_mod.BriefContext(screenshot=shot, logo_local=logo, lang=lang),
        )
        return path.read_text(encoding="utf-8").replace(str(folder), "<FOLDER>")


def print_hashes() -> None:  # pragma: no cover — developer helper
    print("DOC_SHA: dict[str, str] = {")
    for shot, logo, lang in _matrix():
        digest = hashlib.sha256(_write(shot, logo, lang).encode("utf-8")).hexdigest()
        print(f'    "{_key(shot, logo, lang)}": "{digest}",')
    print("}")


class BriefMatrix(unittest.TestCase):
    def test_the_matrix_is_the_size_it_claims(self):
        self.assertEqual(len(list(_matrix())), 8)

    def test_every_combination_writes_a_brief(self):
        for shot, logo, lang in _matrix():
            with self.subTest(key=_key(shot, logo, lang)):
                text = _write(shot, logo, lang)
                self.assertTrue(text.startswith("# Proposal authoring brief"))
                for heading in ("## 1. Look at the brand", "## 4. Author the proposal"):
                    self.assertIn(heading, text)

    def test_writing_is_deterministic(self):
        for shot, logo, lang in _matrix():
            with self.subTest(key=_key(shot, logo, lang)):
                self.assertEqual(_write(shot, logo, lang), _write(shot, logo, lang))

    def test_a_total_that_disagrees_with_its_items_is_flagged(self):
        # The reason this module exists. If the warning ever stops being
        # emitted, the orchestrator writes a proposal that quietly undercharges
        # by five million baht.
        plan = parse(OFFER)
        # Assert the fixture is actually difficult, so this cannot pass vacuously.
        self.assertTrue(plan.get("total_mismatch"), "fixture no longer mismatches")
        text = _write(None, None, "en")
        self.assertIn("⚠", text)
        self.assertIn(str(plan["total_stated"]), text, "the stated total should be quoted back")

    def test_the_price_outlier_is_named(self):
        plan = parse(OFFER)
        self.assertTrue(plan.get("price_outliers"), "fixture no longer has an outlier")
        self.assertIn("Logistics", _write(None, None, "en"))

    def test_each_axis_changes_the_document(self):
        base = _write(None, None, "en")
        self.assertNotEqual(base, _write(SCREENSHOTS[1], None, "en"), "screenshot ignored")
        self.assertNotEqual(base, _write(None, LOGOS[1], "en"), "logo ignored")
        self.assertNotEqual(base, _write(None, None, "ru"), "lang ignored")

    def test_a_screenshot_is_ordered_to_be_opened(self):
        with_shot = _write(SCREENSHOTS[1], None, "en")
        self.assertIn(str(SCREENSHOTS[1]), with_shot)
        self.assertIn("Read tool", with_shot)

    def test_all_eight_briefs_are_distinct(self):
        seen = {}
        for shot, logo, lang in _matrix():
            key = _key(shot, logo, lang)
            text = _write(shot, logo, lang)
            self.assertNotIn(text, seen, f"{key} is identical to {seen.get(text)}")
            seen[text] = key

    def test_briefs_match_the_recorded_hashes(self):
        actual = {
            _key(s, lo, la): hashlib.sha256(_write(s, lo, la).encode("utf-8")).hexdigest()
            for s, lo, la in _matrix()
        }
        self.assertEqual(actual, DOC_SHA)


if __name__ == "__main__":
    unittest.main()
