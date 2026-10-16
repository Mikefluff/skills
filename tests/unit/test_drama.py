"""Drama mode: scenes get their faces from the bible, directors inherit, and a scene that said the wrong words is caught."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import drama  # noqa: E402
from common.runners import ffmpeg_film  # noqa: E402
from common.runners.cli import reel_cast, reel_check  # noqa: E402

BIBLE = {
    "_dir": "/series", "language": "th", "look": "35mm, warm tungsten, heavy grain",
    "cast": [{"id": "malai", "name": "Malai", "identity": "young woman, long black hair, red sash"},
             {"id": "phaya", "name": "Phaya", "identity": "broad man in his forties, scar over the left brow"}],
    "locations": [{"id": "village_storm", "description": "a stilt village on a lake at night, in a storm"}],
}


def scene(**kw):
    return {"index": 1, "label": "sc01", "cast": ["phaya", "malai"], "location": "village_storm",
            "dialogue": [{"who": "malai", "line": "เร็วเข้า"}], "body": "Shot 1 [0-15s] - wide.", **kw}


class Assets(unittest.TestCase):
    def test_images_are_the_cast_in_scene_order_then_the_place(self):
        refs, lines = drama.references(scene(), BIBLE)
        self.assertEqual(refs, ["/series/cast/phaya.png", "/series/cast/malai.png", "/series/locations/village_storm.png"])
        self.assertTrue(lines[0].startswith("Image 1 is Phaya:"))
        self.assertTrue(lines[2].startswith("Image 3 is the location:"))

    def test_the_prompt_is_asset_lines_then_look_then_body(self):
        prompt = drama.compose(scene(), BIBLE).splitlines()
        self.assertEqual(prompt[3], "[Overall style]: 35mm, warm tungsten, heavy grain")
        self.assertEqual(prompt[-1], "Shot 1 [0-15s] - wide.")

    def test_cast_scenes_hands_each_scene_its_refs_and_prompt(self):
        plan = {"shots": [scene(), scene(index=2, label="sc02", cast=[], location=None)]}
        reel_cast.cast_scenes(plan, BIBLE)
        self.assertEqual(len(plan["shots"][0]["kwargs"]["reference_images"]), 3)
        self.assertEqual(plan["shots"][1]["kwargs"]["reference_images"], [])
        self.assertTrue(plan["shots"][0]["kwargs"]["generate_audio"])


class Voices(unittest.TestCase):
    def setUp(self):
        self.bible = {**BIBLE, "cast": [{**BIBLE["cast"][0], "voice_text": "..."}, BIBLE["cast"][1]]}

    def test_each_speaker_with_a_voice_gets_an_audio_bound_to_their_name(self):
        refs, lines = drama.voices(scene(dialogue=[{"who": "malai", "line": "a"}, {"who": "phaya", "line": "b"},
                                                   {"who": "malai", "line": "c"}]), self.bible)
        self.assertEqual(refs, ["/series/cast/malai.mp3"], "phaya has no voice_text, so no audio")
        self.assertTrue(lines[0].startswith("Audio 1 is Malai's voice"))

    def test_cast_scenes_attaches_voices_and_the_plans_media_host(self):
        plan = {"media_host": "litterbox", "shots": [scene(), scene(index=2, label="sc02", dialogue=[])]}
        reel_cast.cast_scenes(plan, self.bible)
        first, second = (s["kwargs"] for s in plan["shots"])
        self.assertEqual(first["reference_audio"], ["/series/cast/malai.mp3"])
        self.assertEqual(first["media_host"], "litterbox")
        self.assertNotIn("reference_audio", second)
        self.assertIn("Audio 1 is Malai's voice", plan["shots"][0]["prompt"])

    def test_three_speakers_in_one_scene_is_a_problem(self):
        bible = {**BIBLE, "cast": BIBLE["cast"] + [{"id": "monk", "name": "Monk", "identity": "x"}]}
        crowded = scene(cast=["malai", "phaya", "monk"],
                        dialogue=[{"who": w, "line": "."} for w in ("malai", "phaya", "monk")])
        self.assertIn("sc01: more than 2 speakers", drama.validate({"shots": [crowded]}, bible))


class Board(unittest.TestCase):
    def test_the_critic_sees_people_and_places_but_not_earlier_frames(self):
        from common.runners.cli import reel_board
        frame = {"_ref_names": ["Minh (thin, blue jacket)", "the location: LAX", "frame f01"]}
        people = reel_board._people(frame, ["minh.png", "lax.png", "f01.png"])
        self.assertEqual([r for r, _ in people], ["minh.png", "lax.png"])
        self.assertEqual(reel_board._refs_note([n for _, n in people]),
                         "Image 1 is Minh (thin, blue jacket). Image 2 is the location: LAX.")

    def test_a_double_is_drawn_after_the_face_it_copies(self):
        bible = {**BIBLE, "cast": [{"id": "jun", "name": "Jun", "identity": "x", "like": "minh", "prompt": "p"},
                                   {"id": "minh", "name": "Minh", "identity": "y", "prompt": "p"}], "locations": []}
        order = [item["id"] for _, item in reel_cast._todo(bible, {}, set())]
        self.assertEqual(order, ["minh", "jun"])


class Validate(unittest.TestCase):
    def test_a_scene_that_matches_its_bible_has_no_problems(self):
        self.assertEqual(drama.validate({"shots": [scene()]}, BIBLE), [])

    def test_unknown_ids_and_a_speaker_outside_the_scene_are_named(self):
        bad = scene(cast=["malai", "ghost"], location="palace",
                    dialogue=[{"who": "phaya", "line": "..."}, {"who": "vo", "line": "..."}])
        problems = " ".join(drama.validate({"shots": [bad]}, BIBLE))
        self.assertIn("unknown cast 'ghost'", problems)
        self.assertIn("unknown location 'palace'", problems)
        self.assertIn("'phaya' speaks but is not in the scene's cast", problems)
        self.assertNotIn("'vo'", problems)


class Directors(unittest.TestCase):
    def test_a_director_replaces_rules_by_number_and_appends_new_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "base.md").write_text("# Base\n\n1. Cut often.\n2. Keep the line.\n", encoding="utf-8")
            Path(tmp, "slow.md").write_text("extends: base\nSlow cinema.\n\n1. Hold 8 s.\n101. No hand-held.\n",
                                            encoding="utf-8")
            rules = drama.director("slow", Path(tmp))
        self.assertIn("1. Hold 8 s.", rules)
        self.assertNotIn("Cut often", rules)
        self.assertLess(rules.index("1. Hold 8 s."), rules.index("2. Keep the line."), "a replaced rule keeps its place")
        self.assertTrue(rules.rstrip().endswith("101. No hand-held."))
        self.assertIn("Slow cinema.", rules)

    def test_the_shipped_base_director_loads(self):
        self.assertIn("1. The first 3 seconds", drama.director("base"))


class Speech(unittest.TestCase):
    def test_thai_said_with_spaces_inserted_by_stt_still_matches(self):
        self.assertEqual(drama.speech_match("พญานาคตื่นแล้ว", "พญานาค ตื่น แล้ว"), 1.0)

    def test_half_the_words_missing_fails_the_default_threshold(self):
        self.assertLess(drama.speech_match("the river took the whole village", "the river"), 0.8)

    def test_a_scene_without_lines_has_nothing_to_check(self):
        self.assertEqual(drama.speech_match("", "rain"), 1.0)

    def test_fails_names_each_reason(self):
        why = reel_check._fails({"speech": 0.5, "identity": 9, "text_on_screen": True}, 0.8, 7)
        self.assertEqual(why, ["speech 0.50", "text on screen"])
        self.assertEqual(reel_check._fails({"speech": None, "identity": 8}, 0.8, 7), [])


class NativeAudio(unittest.TestCase):
    def test_concat_keeps_each_scenes_sound_cut_on_the_same_frames(self):
        with mock.patch.object(ffmpeg_film, "_run", side_effect=lambda cmd: cmd), \
             mock.patch.object(ffmpeg_film, "_size", return_value=(854, 480)):
            cmd = ffmpeg_film.concat_trimmed([(Path("a.mp4"), 15.0), (Path("b.mp4"), 12.0, 0.5)], Path("/tmp/x.mp4"),
                                             audio=True)
        graph = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("[1:a]atrim=0.500:12.500", graph)
        self.assertIn("concat=n=2:v=1:a=1[v][a]", graph)
        self.assertNotIn("-an", cmd)

    def test_film_mode_concat_stays_picture_only(self):
        with mock.patch.object(ffmpeg_film, "_run", side_effect=lambda cmd: cmd), \
             mock.patch.object(ffmpeg_film, "_size", return_value=(480, 854)):
            cmd = ffmpeg_film.concat_trimmed([(Path("a.mp4"), 4.0)], Path("/tmp/x.mp4"))
        self.assertIn("-an", cmd)
        self.assertNotIn("atrim", cmd[cmd.index("-filter_complex") + 1])


class Animatic(unittest.TestCase):
    PLAN = {"shots": [{"index": 1, "label": "t01", "clock_at": 0.0, "trim_seconds": 2.14,
                       "dialogue": [{"who": "minh", "line": "I'm not Christopher Park."}], "line_at": 0.4},
                      {"index": 2, "label": "t02", "clock_at": 4.28, "trim_seconds": 1.43}],
            "trailer": {"title_cards": [{"after": "t01", "text": "SAME", "clock_at": 2.14, "seconds": 2.14}]}}

    def test_cards_sit_between_shots_on_the_clock(self):
        from common.runners.cli import reel_animatic
        self.assertEqual([i["kind"] for i in reel_animatic.timeline(self.PLAN)], ["shot", "card", "shot"])

    def test_a_line_starts_at_its_shot_plus_line_at(self):
        from common.runners.cli import reel_animatic
        self.assertEqual(reel_animatic.lines(self.PLAN)[0]["at"], 0.4)

    def test_stand_ins_match_sex_and_age_and_differ_while_they_can(self):
        from common.runners.cli import reel_animatic
        library = [{"voice_id": "old_f", "labels": {"gender": "female", "age": "old"}},
                   {"voice_id": "young_m", "labels": {"gender": "male", "age": "young"}},
                   {"voice_id": "mid_m", "labels": {"gender": "male", "age": "middle_aged"}}]
        cast = [{"id": "sun_hee", "identity": "Korean woman, 67, small"},
                {"id": "minh", "identity": "Vietnamese man, 31, slim"},
                {"id": "harper", "identity": "white man, 48, stocky"}]
        self.assertEqual(reel_animatic.pick_voices(cast, library),
                         {"sun_hee": "old_f", "minh": "mid_m", "harper": "young_m"})


class Retime(unittest.TestCase):
    def plan(self):
        return {"shots": [{"index": 1, "label": "a", "clock_at": 0, "trim_seconds": 2.0, "line_at": 0.3},
                          {"index": 2, "label": "b", "clock_at": 2.0, "trim_seconds": 1.0}],
                "trailer": {"acts": [{"name": "world", "from": "a", "to": "b"}],
                            "title_cards": [{"after": "b", "clock_at": 3.0, "seconds": 1.0}]},
                "sound": {"total_seconds": 4.0,
                          "sources": [{"id": "m", "kind": "music", "composition_plan": {
                              "positive_global_styles": ["120 bpm"],
                              "sections": [{"section_name": "world", "duration_ms": 3000}]}}],
                          "placements": [{"source": "m", "at": 0, "length": 3.0}, {"source": "m", "at": 3.0}]}}

    def test_a_speaking_shot_takes_its_lines_length_in_whole_beats(self):
        from common.runners.cli import _trailer_retime as rt
        self.assertEqual(rt.new_lengths(self.plan(), {"a": 2.6}), {"a": 3.5})
        self.assertEqual(rt.new_lengths(self.plan(), {"a": 0.2}), {"a": 1.0}, "shorter lines shorten, to 2 beats at least")

    def test_everything_after_the_grown_shot_moves_later_and_the_music_section_grows(self):
        from common.runners.cli import _trailer_retime as rt
        plan = self.plan()
        rt.retime(plan, {"a": 3.5})
        self.assertEqual(plan["shots"][1]["clock_at"], 3.5)
        self.assertEqual(plan["trailer"]["title_cards"][0]["clock_at"], 4.5)
        self.assertEqual(plan["sound"]["placements"], [{"source": "m", "at": 0.0, "length": 4.5},
                                                       {"source": "m", "at": 4.5}])
        self.assertEqual(plan["sound"]["sources"][0]["composition_plan"]["sections"][0]["duration_ms"], 4500)
        self.assertEqual(plan["sound"]["total_seconds"], 5.5)

    def test_lines_of_consecutive_shots_of_one_scene_are_one_exchange(self):
        from common.runners.cli import _animatic_voice as av
        plan = {"shots": [{"index": 1, "label": "t1", "scene": 6, "clock_at": 0, "trim_seconds": 2,
                           "dialogue": [{"who": "voss", "line": "98.7"}]},
                          {"index": 2, "label": "t2", "scene": 6, "clock_at": 2, "trim_seconds": 1,
                           "dialogue": [{"who": "minh", "line": "Percent?"}]},
                          {"index": 3, "label": "t3", "scene": 7, "clock_at": 3, "trim_seconds": 2,
                           "dialogue": [{"who": "jun", "line": "Hi"}]}]}
        self.assertEqual([[l["label"] for l in g] for g in av.exchanges(plan)], [["t1", "t2"], ["t3"]])


if __name__ == "__main__":
    unittest.main()
