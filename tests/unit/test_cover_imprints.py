"""The imprint presets, and what compose_book_cover draws from them.

Two things live here.

IMPRINTS is module-level shared state: one ImprintPreset per imprint, each
holding one TypeLayout with empty text fields waiting to be filled. Filling
them in place works exactly once per process, which is why a CLI that runs
once per invocation never noticed.

And the composition itself. The paydown proved a typography.py refactor
byte-identical with a throwaway script — compose all five imprints, sha256 the
result. That harness was sound and is committed here, with one change: the
pixel hashes are recorded per Pillow major version rather than pinned flat.
Rasterisation is FreeType's, not ours, and CI installs a different Pillow than
a laptop does (requirements.txt says >=10.4,<12). A hash that fails for
somebody else's font renderer is a hash that gets deleted.

So the invariants that hold everywhere are asserted everywhere, and the exact
pixels are checked only where they mean something. See PIXEL_SHA for how to
record a version.
"""

import hashlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import cover_imprints  # noqa: E402

try:
    import PIL
    from PIL import Image

    from common.runners import typography as type_mod

    PILLOW_MAJOR = int(PIL.__version__.split(".")[0])
    HAVE_PILLOW = type_mod.DEFAULT_FONTS_DIR.is_dir()
except ImportError:  # pragma: no cover — Pillow is an optional dependency
    HAVE_PILLOW = False
    PILLOW_MAJOR = 0


class ApplyText(unittest.TestCase):
    def preset(self, name="nyrb-classics"):
        return cover_imprints.get_imprint(name)

    def test_the_shared_preset_is_not_written_into(self):
        layout = cover_imprints.apply_text(self.preset().layout, "Первая книга", "Автор")
        self.assertEqual(layout.title.text, "Первая книга")
        # The preset must still be the blank template it ships as.
        self.assertEqual(self.preset().layout.title.text, "")

    def test_a_second_cover_does_not_inherit_the_first(self):
        first = cover_imprints.apply_text(self.preset().layout, "Первая", "Автор А")
        second = cover_imprints.apply_text(self.preset().layout, "Вторая", "Автор Б")
        self.assertEqual(first.title.text, "Первая")
        self.assertEqual(second.title.text, "Вторая")
        self.assertEqual(first.author.text, "Автор А")
        self.assertEqual(second.author.text, "Автор Б")

    def test_an_absent_author_does_not_leave_the_previous_one_standing(self):
        # `if layout.author is not None and author:` skips the write when the
        # author is empty. Combined with the in-place mutation, the second
        # cover kept the first cover's author.
        cover_imprints.apply_text(self.preset().layout, "Первая", "Автор А")
        second = cover_imprints.apply_text(self.preset().layout, "Вторая", "")
        self.assertEqual(second.author.text, "")

    def test_subtitle_behaves_the_same(self):
        named = [n for n, p in cover_imprints.IMPRINTS.items() if p.layout.subtitle is not None]
        if not named:
            self.skipTest("no imprint ships a subtitle block")
        first = cover_imprints.apply_text(self.preset(named[0]).layout, "Т", "А", "Подзаголовок")
        second = cover_imprints.apply_text(self.preset(named[0]).layout, "Т", "А", None)
        self.assertEqual(first.subtitle.text, "Подзаголовок")
        self.assertEqual(second.subtitle.text, "")

    def test_every_imprint_ships_blank_and_stays_blank(self):
        for name in cover_imprints.IMPRINTS:
            with self.subTest(imprint=name):
                self.assertEqual(cover_imprints.get_imprint(name).layout.title.text, "")
                cover_imprints.apply_text(cover_imprints.get_imprint(name).layout, "X", "Y")
                self.assertEqual(cover_imprints.get_imprint(name).layout.title.text, "")

    def test_decorations_are_copied_not_shared(self):
        # A shallow copy would hand every cover the same decoration list.
        named = [n for n, p in cover_imprints.IMPRINTS.items() if p.layout.decorations]
        if not named:
            self.skipTest("no imprint ships decorations")
        layout = cover_imprints.apply_text(self.preset(named[0]).layout, "Т", "А")
        self.assertIsNot(layout.decorations, cover_imprints.IMPRINTS[named[0]].layout.decorations)


# ── the composition proof ──────────────────────────────────────────────────

TITLE = "Тихий Дон"
AUTHOR = "Михаил Шолохов"

# sha256 of the composed RGB pixel data (not the PNG container — zlib settings
# are Pillow's business, not this repo's), keyed by Pillow major version.
#
# To record a version, run from the repo root:
#
#   python3 -c "import tests.unit.test_cover_imprints as t; t.print_hashes()"
#
# and paste the block. A version that is not listed skips rather than fails:
# an unrecorded Pillow proves nothing about typography.py.
PIXEL_SHA: dict[int, dict[str, str]] = {
    12: {
        "nyrb-classics": "494af5bbd73c2e2e2dbeeb1d227a6f3bcf56fa89afcb81d2e3b7290c5ed58824",
        "penguin-marber-grid": "b392db07924919e90ed420a940150905201e0cdfd5bd16006ae2d028da8551c2",
        "mit-essential-knowledge": "7164343cb21550d228f02386ea9e67019f5122373b641c693250f9d34b12b29f",
        "picador-modern": "998492711d0423e57b28b144f50b685b8271e91f356a2a56b2a1889f14a53102",
        "faber-modernist": "1da272d8cefe3e05f438142962b793320e105a666686d50fd71a2f48636858d1",
    },
}


def _source_png(width: int = 1024, height: int = 1536) -> bytes:
    """A deterministic checkerboard — flat colour would hide a misplaced band."""
    img = Image.new("RGB", (width, height), (27, 59, 42))
    for y in range(0, height, 64):
        for x in range(0, width, 64):
            if (x // 64 + y // 64) % 2 == 0:
                img.paste((60, 90, 70), (x, y, min(x + 64, width), min(y + 64, height)))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _compose(imprint: str, source: bytes, title: str = TITLE, author: str = AUTHOR) -> bytes:
    layout = cover_imprints.apply_text(cover_imprints.get_imprint(imprint).layout, title, author)
    return type_mod.compose_book_cover(source, layout)


def _pixels(png: bytes) -> bytes:
    return Image.open(io.BytesIO(png)).tobytes()


def print_hashes() -> None:  # pragma: no cover — developer helper, see PIXEL_SHA
    source = _source_png()
    print(f"    {PILLOW_MAJOR}: {{")
    for name in cover_imprints.IMPRINTS:
        digest = hashlib.sha256(_pixels(_compose(name, source))).hexdigest()
        print(f'        "{name}": "{digest}",')
    print("    },")


@unittest.skipUnless(HAVE_PILLOW, "Pillow and the bundled fonts are needed to compose")
class ComposeBookCover(unittest.TestCase):
    """What a typography.py refactor must not change.

    The properties below hold on any Pillow. The pixel pin is the sharper
    instrument but only speaks for a recorded version.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = _source_png()

    def test_every_imprint_composes(self):
        for name in cover_imprints.IMPRINTS:
            with self.subTest(imprint=name):
                out = _compose(name, self.source)
                self.assertTrue(out.startswith(b"\x89PNG\r\n\x1a\n"), "not a PNG")
                img = Image.open(io.BytesIO(out))
                self.assertEqual(img.size, (1024, 1536))
                self.assertEqual(img.mode, "RGB")

    def test_composition_is_deterministic(self):
        # Same input twice, same pixels. This is the property that a refactor
        # reaching for a dict or a set can quietly break.
        for name in cover_imprints.IMPRINTS:
            with self.subTest(imprint=name):
                self.assertEqual(
                    _pixels(_compose(name, self.source)),
                    _pixels(_compose(name, self.source)),
                )

    def test_text_is_actually_drawn(self):
        # A composer that silently drew nothing would satisfy every structural
        # assertion above and return the source unchanged.
        untouched = Image.open(io.BytesIO(self.source)).convert("RGB").tobytes()
        for name in cover_imprints.IMPRINTS:
            with self.subTest(imprint=name):
                self.assertNotEqual(_pixels(_compose(name, self.source)), untouched)

    def test_the_five_imprints_are_five_different_designs(self):
        seen = {}
        for name in cover_imprints.IMPRINTS:
            digest = hashlib.sha256(_pixels(_compose(name, self.source))).hexdigest()
            self.assertNotIn(digest, seen, f"{name} composes identically to {seen.get(digest)}")
            seen[digest] = name

    def test_a_different_title_produces_a_different_cover(self):
        for name in cover_imprints.IMPRINTS:
            with self.subTest(imprint=name):
                self.assertNotEqual(
                    _pixels(_compose(name, self.source, title="Тихий Дон")),
                    _pixels(_compose(name, self.source, title="Поднятая целина")),
                )

    def test_pixels_match_the_recorded_hashes(self):
        expected = PIXEL_SHA.get(PILLOW_MAJOR)
        if expected is None:
            self.skipTest(
                f"no pixel hashes recorded for Pillow {PILLOW_MAJOR} — "
                f"recorded: {sorted(PIXEL_SHA)}. See PIXEL_SHA to add one."
            )
        self.assertEqual(sorted(expected), sorted(cover_imprints.IMPRINTS), "imprint set changed")
        for name in cover_imprints.IMPRINTS:
            with self.subTest(imprint=name):
                digest = hashlib.sha256(_pixels(_compose(name, self.source))).hexdigest()
                self.assertEqual(digest, expected[name], f"{name} composes differently than recorded")


if __name__ == "__main__":
    unittest.main()
