"""Cuts in a voiced film land in pauses, and every segment fits one generation.

The seams of the last voiced film broke mid-word: segments were cut at fixed
lengths, so one segment's lip-sync reference ended inside a syllable and the
next began inside it again. These tests hold the two properties that prevent
that — a cut is always inside a pause, and no segment exceeds what the model
can render — plus the one that makes the result watchable: no runt segment at
the end because the planner cut greedily.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import voice_timing as vt  # noqa: E402


def alignment(text, per_char=0.06, pauses=None):
    """Synthetic ElevenLabs alignment. `pauses` maps a char index to extra silence before it."""
    pauses = pauses or {}
    chars, starts, ends = [], [], []
    t = 0.0
    for i, ch in enumerate(text):
        t += pauses.get(i, 0.0)
        chars.append(ch)
        starts.append(round(t, 3))
        t += per_char
        ends.append(round(t, 3))
    return {
        "characters": chars,
        "character_start_times_seconds": starts,
        "character_end_times_seconds": ends,
    }


def words(spec):
    """[(text, start, end)] shorthand."""
    return [vt.Word(t, s, e) for t, s, e in spec]


class WordsFromAlignment(unittest.TestCase):
    def test_words_span_their_characters(self):
        out = vt.words_from_alignment(alignment("Нажми PLAY."))
        self.assertEqual([w.text for w in out], ["Нажми", "PLAY."])
        self.assertAlmostEqual(out[0].start, 0.0)
        self.assertAlmostEqual(out[1].start, 0.36)

    def test_audio_tags_are_not_words(self):
        out = vt.words_from_alignment(alignment("Свет [pause] дым"))
        self.assertEqual([w.text for w in out], ["Свет", "дым"])

    def test_multi_word_v4_tags_are_not_words(self):
        out = vt.words_from_alignment(alignment("[dry, sarcastic] Очень живо. [long pause] Даже я."))
        self.assertEqual([w.text for w in out], ["Очень", "живо.", "Даже", "я."])

    def test_strip_tags_leaves_the_spoken_text(self):
        self.assertEqual(vt.strip_tags("[calm, low voice] Шоу [pause] живое."), "Шоу живое.")

    def test_mismatched_lists_are_rejected(self):
        bad = alignment("abc")
        bad["character_end_times_seconds"].pop()
        with self.assertRaises(ValueError):
            vt.words_from_alignment(bad)


class PlanCuts(unittest.TestCase):
    def test_short_film_is_one_segment(self):
        segs = vt.segments(words([("a", 0, 1), ("b", 2, 3)]), total=12.0)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].request_seconds, 12)

    def test_cuts_land_inside_pauses_only(self):
        spec = [(f"w{i}", i * 1.0, i * 1.0 + 0.95) for i in range(27)]
        # One real pause at 13.95-14.6, after a sentence end.
        spec[13] = ("end.", 13.0, 13.95)
        spec = [(t, s + (0.6 if i > 13 else 0), e + (0.6 if i > 13 else 0)) for i, (t, s, e) in enumerate(spec)]
        cuts = vt.plan_cuts(words(spec), total=28.0)
        self.assertEqual(len(cuts), 1)
        self.assertTrue(13.95 < cuts[0] < 14.6)

    def test_no_segment_exceeds_the_model_limit(self):
        spec = []
        t = 0.0
        for i in range(60):
            spec.append((f"w{i}.", t, t + 0.4))
            t += 0.7
        segs = vt.segments(words(spec), total=t, rules=vt.CutRules(max_seconds=10))
        self.assertTrue(all(s.span <= 10 for s in segs))
        self.assertTrue(all(s.request_seconds >= s.span for s in segs))

    def test_no_runt_segment_at_the_end(self):
        # 32 s, pauses every second: greedy-at-15 gives 15 + 15 + 2.
        spec = [(f"w{i}.", float(i), i + 0.7) for i in range(32)]
        segs = vt.segments(words(spec), total=32.0)
        self.assertEqual(len(segs), 3)
        self.assertTrue(all(s.span >= 4 for s in segs))

    def test_unbroken_speech_is_an_error_not_a_mid_word_cut(self):
        spec = [(f"w{i}", i * 0.5, i * 0.5 + 0.49) for i in range(60)]
        with self.assertRaises(ValueError):
            vt.plan_cuts(words(spec), total=30.0)

    def test_segment_words_are_on_the_segment_clock(self):
        spec = [(f"w{i}.", float(i), i + 0.7) for i in range(20)]
        segs = vt.segments(words(spec), total=20.0, rules=vt.CutRules(max_seconds=12))
        second = segs[1].to_json()
        self.assertGreaterEqual(second["words"][0]["start"], 0.0)
        self.assertLess(second["words"][0]["start"], 1.0)


if __name__ == "__main__":
    unittest.main()


class Conform(unittest.TestCase):
    def _w(self, *spec):
        return [vt.Word(t, s, s + 0.4) for t, s in spec]

    def test_a_phrase_goes_where_the_picture_says_it(self):
        master = self._w(("Шоу", 1.0), ("выглядит", 1.5), ("живым.", 2.0), ("Артист", 4.0), ("нажимает", 4.5))
        heard = self._w(("Шоу", 1.5), ("выглядит", 2.0), ("живым", 2.5), ("Артист", 3.6), ("нажимает", 4.1))
        moves = vt.conform(master, heard)
        self.assertAlmostEqual(vt.warp(moves, 1.0), 1.5, places=2)
        self.assertAlmostEqual(vt.warp(moves, 4.0), 3.6, places=2)

    def test_a_line_moved_into_another_shot_stays_put(self):
        master = self._w(("Свет.", 4.5), ("Визуал.", 5.3))
        heard = self._w(("Свет", 7.7), ("Визуал", 8.1))
        self.assertEqual([m.dst_start for m in vt.conform(master, heard)], [m.src_start for m in vt.conform(master, [])])

    def test_moves_never_overlap_and_the_film_starts_at_zero(self):
        master = self._w(("один", 1.0), ("два.", 1.5), ("три", 2.2), ("четыре.", 2.7))
        heard = self._w(("один", 1.0), ("два", 1.5), ("три", 1.2), ("четыре", 1.7))
        moves = vt.conform(master, heard)
        for a, b in zip(moves, moves[1:]):
            self.assertGreaterEqual(b.dst_start, a.dst_end)
        self.assertEqual(vt.warp(moves, 0.0), 0.0)


class ConformSeparateShots(unittest.TestCase):
    def test_a_voice_over_phrase_does_not_inherit_a_lip_shot_shift(self):
        master = [vt.Word("Очень", 1.0, 1.4), vt.Word("живо.", 1.5, 1.9), vt.Word("Система", 4.0, 4.5)]
        heard = [vt.Word("Очень", 1.6, 2.0), vt.Word("живо", 2.1, 2.5)]
        moves = vt.conform(master, heard, carry=False)
        self.assertAlmostEqual(moves[0].dst_start - moves[0].src_start, 0.6, places=2)
        self.assertEqual(moves[1].dst_start, moves[1].src_start)
