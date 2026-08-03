"""The imprint presets, and the rule that composing a cover must not consume them.

IMPRINTS is module-level shared state: one ImprintPreset per imprint, each
holding one TypeLayout with empty text fields waiting to be filled. Filling
them in place works exactly once per process, which is why a CLI that runs
once per invocation never noticed.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import cover_imprints  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
