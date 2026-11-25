"""Unit tests for the reel-recut edit decisions — timeline, captions, framing, plan.

None of this raises when it is wrong. A trim that lands inside a word, a caption
that orphans a preposition or a reframe in mid-sentence all render without
complaint, and the mistake is only seen by whoever watches the reel. These are
the decisions that can be checked without rendering one.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import recut_framing as framing  # noqa: E402
from common.runners import recut_plan  # noqa: E402
from common.runners import recut_scene as scene_mod  # noqa: E402
from common.runners import recut_timeline as tl  # noqa: E402


def word(text, start, end):
    return {"word": text, "start": start, "end": end}


class Silences(unittest.TestCase):
    def test_pairs_are_read_from_ffmpeg_output(self):
        log = "[silencedetect @ 0x1] silence_start: 1.5\n[silencedetect @ 0x1] silence_end: 2.25 | silence_duration: 0.75\n"
        self.assertEqual(tl.parse_silences(log), [(1.5, 2.25)])


class TimelineCase(unittest.TestCase):
    def test_nothing_to_trim_keeps_the_clip_to_just_after_the_last_word(self):
        line = tl.plan_timeline(10.0, 8.0, [])
        self.assertEqual(line.keep, ((0.0, 8.5),))

    def test_an_opener_trim_snaps_into_the_pause_beside_it(self):
        # Asked to start at 2.1, in the middle of a pause that ends at 2.4: the
        # cut lands just before speech resumes, not where it was typed.
        line = tl.plan_timeline(10.0, 8.0, [(1.8, 2.4)], start=2.1)
        self.assertAlmostEqual(line.keep[0][0], 2.4 - 0.14 - 0.03, places=1)

    def test_a_long_pause_is_shortened_but_keeps_air(self):
        line = tl.plan_timeline(10.0, 8.0, [(3.0, 4.2)])
        removed = [span for span in line.removed if 3.0 < span[0] < 4.2]
        self.assertEqual(len(removed), 1)
        self.assertGreater(removed[0][0], 3.0 + 0.2)
        self.assertLess(removed[0][1], 4.2 - 0.1)

    def test_a_breath_is_left_alone(self):
        line = tl.plan_timeline(10.0, 8.0, [(3.0, 3.5)])
        self.assertEqual(len(line.keep), 1)

    def test_times_after_a_cut_move_earlier_by_its_length(self):
        line = tl.plan_timeline(10.0, 8.0, [], cuts=((2.0, 4.0),))
        self.assertAlmostEqual(line.at(5.0), 3.0, places=2)
        self.assertAlmostEqual(line.at(3.0), 2.0, places=2)  # inside the cut: its start
        self.assertEqual(line.cuts, [2.0])

    def test_total_is_what_is_kept(self):
        line = tl.plan_timeline(10.0, 8.0, [], cuts=((2.0, 4.0),))
        self.assertAlmostEqual(line.total, 6.5, places=2)


class Words(unittest.TestCase):
    def setUp(self):
        self.line = tl.plan_timeline(10.0, 8.0, [], cuts=((2.0, 4.0),))

    def test_words_inside_a_cut_are_dropped(self):
        words = [word("one", 0.5, 0.9), word("gone", 2.5, 3.0), word("two", 4.5, 5.0)]
        self.assertEqual([w["text"] for w in tl.remap_words(words, self.line)], ["one", "two"])

    def test_a_fix_replaces_the_word_at_its_time(self):
        words = [word("ЦПФ", 0.5, 0.9)]
        self.assertEqual(tl.remap_words(words, self.line, ((0.5, "CPF"),))[0]["text"], "CPF")

    def test_an_empty_fix_drops_the_word(self):
        words = [word("э", 0.5, 0.6), word("да", 0.7, 0.9)]
        self.assertEqual([w["text"] for w in tl.remap_words(words, self.line, ((0.5, ""),))], ["да"])

    def test_a_lone_dash_is_not_a_word(self):
        self.assertEqual(tl.remap_words([word("—", 0.5, 0.6)], self.line), [])


class Captions(unittest.TestCase):
    def spoken(self, *texts, step=0.3):
        return [{"t": i * step, "e": i * step + 0.25, "text": text} for i, text in enumerate(texts)]

    def test_no_caption_is_longer_than_three_words(self):
        groups = tl.caption_groups(self.spoken("раз", "два", "три", "четыре", "пять", "шесть", "семь"))
        self.assertTrue(all(len(g["words"]) <= 3 for g in groups))

    def test_a_pause_starts_a_new_caption(self):
        words = self.spoken("раз", "два")
        words.append({"t": 2.0, "e": 2.3, "text": "три"})
        self.assertEqual([len(g["words"]) for g in tl.caption_groups(words)], [2, 1])

    def test_a_trailing_preposition_opens_the_next_caption(self):
        groups = tl.caption_groups(self.spoken("документы", "подаём", "в", "полицию", "сегодня"))
        self.assertEqual([w["text"] for w in groups[0]["words"]], ["документы", "подаём"])
        self.assertEqual(groups[1]["words"][0]["text"], "в")

    def test_captions_do_not_overlap(self):
        groups = tl.caption_groups(self.spoken("раз", "два", "три", "четыре", "пять", "шесть"))
        for a, b in zip(groups, groups[1:]):
            self.assertLessEqual(a["t1"], b["t0"] + 1e-6)


class Takes(unittest.TestCase):
    def test_a_fragment_finds_its_full_take(self):
        full = "привет это серия про легализацию в бразилии без иллюзий разберём реальные истории и цены"
        texts = {"a": full, "b": "привет это серия про легализацию в бразилии", "c": "совсем другой ролик про налоги и карты"}
        self.assertEqual(tl.duplicate_takes(texts), [["a", "b"]])

    def test_different_clips_are_not_grouped(self):
        self.assertEqual(tl.duplicate_takes({"a": "один два три четыре", "b": "пять шесть семь восемь"}), [])

    def test_a_restart_is_reported_with_both_times(self):
        words = [word(t, i * 0.4, i * 0.4 + 0.3) for i, t in enumerate(
            "итак давайте разберём главное давайте разберём главное первое".split())]
        found = tl.repeated_lines(words)
        self.assertEqual(len(found), 1)
        self.assertAlmostEqual(found[0][0], 0.4)
        self.assertAlmostEqual(found[0][1], 1.6)

    def test_a_phrase_that_returns_much_later_is_not_a_restart(self):
        words = [word("вид", 0, 0.2), word("на", 0.3, 0.4), word("жительство", 0.5, 0.9),
                 word("вид", 20, 20.2), word("на", 20.3, 20.4), word("жительство", 20.5, 20.9)]
        self.assertEqual(tl.repeated_lines(words), [])


class Framing(unittest.TestCase):
    def test_segments_cover_the_speech_without_gaps(self):
        segments = framing.framing_segments(20.0, [], [3.0, 6.0, 9.5, 13.0, 16.0], [])
        self.assertEqual(segments[0][0], 0.0)
        self.assertEqual(segments[-1][1], 20.0)
        for a, b in zip(segments, segments[1:]):
            self.assertEqual(a[1], b[0])

    def test_framing_alternates(self):
        modes = [s[2] for s in framing.framing_segments(20.0, [], [3.0, 6.0, 9.5, 13.0, 16.0], [])]
        self.assertTrue(all(a != b for a, b in zip(modes, modes[1:])))

    def test_a_panel_is_always_stacked(self):
        segments = framing.framing_segments(20.0, [(8.0, 14.0)], [3.0, 6.0, 16.0], [])
        self.assertIn((8.0, 14.0, "stack"), segments)

    def test_the_opening_framing_is_held_for_the_hook(self):
        segments = framing.framing_segments(20.0, [], [1.0, 2.0, 3.5, 8.0], [])
        self.assertGreaterEqual(segments[0][1], framing.FIRST_HOLD)

    def test_nothing_is_held_longer_than_the_limit_when_there_is_no_pause(self):
        segments = framing.framing_segments(30.0, [], [], [])
        self.assertTrue(all(b - a <= framing.LONGEST for a, b, _ in segments))

    def test_expressions_name_every_segment(self):
        segments = [(0.0, 3.0, "wide"), (3.0, 6.0, "close")]
        expr = framing.zoom_expr(segments, recut_plan.DEFAULT_FRAMING)
        self.assertEqual(expr.count("gte(t,"), 2)
        self.assertIn("1.35", expr)


class PlanCase(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        for name in ("a.mp4", "a.json", "cut.png"):
            (self.dir / name).write_bytes(b"x")

    def plan(self, **episode):
        ep = {"n": 1, "src": "a.mp4", "words": "a.json", "slug": "01-a", "face": [0.5, 0.4], "hook": ["A", "b"]}
        ep.update(episode)
        path = self.dir / "plan.json"
        path.write_text(json.dumps({"series": "S", "episodes": [ep]}), encoding="utf-8")
        return recut_plan.load(path)

    def test_a_minimal_plan_has_no_problems(self):
        self.assertEqual(recut_plan.problems(self.plan()), [])

    def test_a_missing_cutaway_is_named(self):
        plan = self.plan(items=[{"kind": "broll", "at": [1, 3], "asset": "nope.mp4"}])
        self.assertIn("nope.mp4", " ".join(recut_plan.problems(plan)))

    def test_a_reversed_span_is_a_problem(self):
        plan = self.plan(items=[{"kind": "chip", "at": [3, 1], "text": "x", "style": "ok"}])
        self.assertTrue(any("start < end" in p for p in recut_plan.problems(plan)))

    def test_an_unknown_style_is_a_problem(self):
        plan = self.plan(items=[{"kind": "chip", "at": [1, 3], "text": "x", "style": "shiny"}])
        self.assertTrue(any("shiny" in p for p in recut_plan.problems(plan)))

    def test_an_episode_framing_overrides_only_what_it_names(self):
        path = self.dir / "plan.json"
        path.write_text(json.dumps({"framing": {"desk": {"close": [1.2, 700]}},
                                    "episodes": [{"n": 1, "framing": "desk"}]}), encoding="utf-8")
        plan = recut_plan.load(path)
        presets = plan.presets(plan.episode(1))
        self.assertEqual(presets["close"], (1.2, 700))
        self.assertEqual(presets["wide"], recut_plan.DEFAULT_FRAMING["wide"])


class SceneCase(unittest.TestCase):
    def setUp(self):
        font = Path("/nonexistent/font.ttf")
        brand = recut_plan.Brand(("site", ".io"), "#f00", "#0f0", "#000", font, font)
        self.scene = scene_mod.Scene(brand, lambda t: t - 1.0, 30.0)

    def test_item_times_are_moved_onto_the_new_clock(self):
        cue = scene_mod.item_cues(self.scene, [{"kind": "chip", "at": [5.0, 8.0], "text": "x", "style": "ok"}])[0]
        self.assertEqual((cue.t0, cue.t1), (4.0, 7.0))

    def test_text_is_escaped(self):
        cue = scene_mod.item_cues(self.scene, [{"kind": "chip", "at": [5, 8], "text": "<b>&", "style": "ok"}])[0]
        self.assertIn("&lt;b&gt;&amp;", cue.html)

    def test_a_number_and_its_caption_arrive_separately(self):
        cues = scene_mod.item_cues(self.scene, [{"kind": "big", "at": [5, 8], "text": "$3 000", "sub": "за документы"}])
        self.assertEqual(len(cues), 2)
        self.assertLess(cues[0].t0, cues[1].t0)

    def test_each_panel_row_is_its_own_cue_and_leaves_with_the_panel(self):
        items = [{"kind": "panel", "at": [10, 20], "title": "T", "rows": [[11, "a"], [14, "b"]], "style": "num"}]
        panels = scene_mod.panels_of(self.scene, items, None)
        cues = scene_mod.panel_cues(self.scene, panels)
        self.assertEqual(len(cues), 3)
        self.assertTrue(all(c.t1 == panels[0].t1 for c in cues))

    def test_a_tail_panel_starts_where_the_speech_ends(self):
        tail = {"seconds": 5, "title": "T", "rows": [[0.4, "a"]], "style": "check"}
        panel = scene_mod.panels_of(self.scene, [], tail)[0]
        self.assertEqual((panel.t0, panel.t1), (30.0, 35.0))
        self.assertAlmostEqual(panel.rows[0][0], 30.4)

    def test_every_end_card_button_gets_a_cue(self):
        end = {"tagline": ["a"], "buttons": [{"text": "one"}, {"text": "two", "icon": "tg"}]}
        self.assertEqual(len(scene_mod.end_cues(self.scene, end, 30.0)), 5)


if __name__ == "__main__":
    unittest.main()
