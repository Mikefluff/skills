"""Drama mode: scenes get their faces from the bible, directors inherit, and a scene that said the wrong words is caught."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import drama  # noqa: E402
from common.runners.errors import RunnerError  # noqa: E402
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


class FirstFrameRoute(unittest.TestCase):
    def test_a_first_frame_route_sends_the_board_frame_and_the_motion_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "board").mkdir()
            (Path(tmp) / "board" / "f01.jpg").write_bytes(b"jpg")
            plan = {"video_provider": "openrouter-wan-3-0", "output_dir": tmp,
                    "board": {"frames": [{"id": "f01", "shot": 1}]},
                    "shots": [scene(motion="Handheld camera. Open exactly on this frame.",
                                    kwargs={"duration_seconds": 5, "reference_images": ["x.png"]}),
                              scene(index=2, label="sc02", clip="shots/composite.mp4")]}
            from common.runners import config
            config.load_all_providers()
            reel_cast.cast_scenes(plan, BIBLE)
        first, composite = plan["shots"]
        self.assertEqual(first["prompt"], "Handheld camera. Open exactly on this frame.")
        self.assertEqual(first["kwargs"]["first_frame"], str(Path(tmp) / "board" / "f01.jpg"))
        self.assertNotIn("reference_images", first["kwargs"])
        self.assertEqual(first["kwargs"]["resolution"], "480p")
        self.assertNotIn("prompt", composite, "a hand-cut composite is left alone")

    def test_a_shot_without_motion_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "board").mkdir()
            (Path(tmp) / "board" / "f01.jpg").write_bytes(b"jpg")
            plan = {"video_provider": "openrouter-wan-3-0", "output_dir": tmp,
                    "board": {"frames": [{"id": "f01", "shot": 1}]}, "shots": [scene()]}
            from common.runners import config
            config.load_all_providers()
            with self.assertRaises(RunnerError):
                reel_cast.cast_scenes(plan, BIBLE)


class TrailerCut(unittest.TestCase):
    def test_the_trim_puts_the_clips_mouth_where_the_cast_line_plays(self):
        from common.runners.cli import _animatic_clips, reel_animatic
        shot = {"label": "t09", "clock_at": 28.3, "trim_start": 0.3, "trim_seconds": 2.9}
        with mock.patch.object(_animatic_clips, "mouth_at", return_value=2.75), \
                mock.patch.object(_animatic_clips, "_length", return_value=5.0):
            # the cast's line plays 0.9 s into the window, so the window opens 0.9 s before the mouth
            self.assertEqual(reel_animatic.clip_start(shot, Path("c.mp4"), 29.2, Path("m.json")), 1.85)
            # never past the end of the clip
            self.assertEqual(reel_animatic.clip_start(shot, Path("c.mp4"), 28.3, Path("m.json")), 2.1)

    def test_a_silent_shot_keeps_the_plans_trim(self):
        from common.runners.cli import _animatic_clips, reel_animatic
        shot = {"label": "t03", "clock_at": 5.0, "trim_start": 0.5, "trim_seconds": 2.0}
        with mock.patch.object(_animatic_clips, "_length", return_value=5.0):
            self.assertEqual(reel_animatic.clip_start(shot, Path("c.mp4"), None, Path("m.json")), 0.5)

    def test_a_grade_pins_its_format_before_it_splits_off_the_luma(self):
        from common.runners import film_grade
        # unpinned, ffmpeg negotiates the gray branch's format back up the chain: a mono trailer
        self.assertTrue(all(g.startswith("format=gbrp,split") for g in film_grade.GRADES.values() if "split" in g))

    def test_an_unknown_grade_is_refused(self):
        from common.runners import film_grade
        with self.assertRaises(ValueError):
            film_grade.apply(Path("c.mp4"), "teal-orange", Path("o.mp4"))
        self.assertEqual(film_grade.apply(Path("c.mp4"), None, Path("o.mp4")), Path("c.mp4"))


class TrailerSound(unittest.TestCase):
    PLAN = {"shots": [{"label": "t01", "clock_at": 0.0, "trim_seconds": 20.0, "location": "lab"},
                      {"label": "t02", "clock_at": 20.0, "trim_seconds": 15.0, "location": "lab"},
                      {"label": "t03", "clock_at": 36.5, "trim_seconds": 2.0, "location": "street"},
                      {"label": "t04", "clock_at": 38.5, "trim_seconds": 2.0, "location": None}]}
    BIBLE = {"locations": [{"id": "lab", "description": "A cold lab.", "acoustics": "hall"},
                           {"id": "street", "description": "A wet street at night."}]}

    def test_a_bed_runs_under_every_stretch_in_one_place_and_is_laid_again_past_its_length(self):
        from common.runners.cli import _trailer_sound as ts
        sources, placements = ts.beds(self.PLAN, self.BIBLE)
        self.assertEqual([s["id"] for s in sources], ["bed_lab", "bed_street"])
        self.assertTrue(all(s["loop"] for s in sources))
        self.assertIn("a big hard hall", sources[0]["prompt"])
        lab = [(p["at"], p["length"]) for p in placements if p["source"] == "bed_lab"]
        self.assertEqual(lab, [(0.0, 30.0), (30.0, 5.0)])

    def test_the_clips_own_voice_is_cut_out_of_its_sound(self):
        from common.runners.cli import _trailer_sound as ts
        with mock.patch.object(ts.subprocess, "run") as run:
            ts.production({"trim_seconds": 3.0}, Path("c.mp4"), 1.0, [2.0, 2.5], Path("o.wav"))
        af = run.call_args.args[0][run.call_args.args[0].index("-af") + 1]
        self.assertIn("atrim=start=1.000:end=4.000", af)
        self.assertIn("abs(t-1.290)-0.410", af, "silent from 0.88 s to 1.70 s into the window")


class MixedRoutes(unittest.TestCase):
    def test_each_item_goes_to_the_provider_it_names(self):
        from common.runners.cli import reel
        wan, seed = mock.Mock(name="wan"), mock.Mock(name="seed")
        wan.name, seed.name = "openrouter-wan-3-0", "openrouter-seedance-2-5"
        routed = reel.Routed(wan, {"openrouter-seedance-2-5": seed})
        routed.generate("p", _route="openrouter-seedance-2-5", duration_seconds=5)
        seed.generate.assert_called_once_with("p", duration_seconds=5)
        routed.generate("q", duration_seconds=4)
        wan.generate.assert_called_once_with("q", duration_seconds=4)
        routed.poll(mock.Mock(provider="openrouter-seedance-2-5"))
        seed.poll.assert_called_once()

class ShotMatrix(unittest.TestCase):
    def shot(self, label, line, **kw):
        return {"label": label, "clock_at": 0.0, "trim_seconds": 2.0, "cast": ["minh"],
                "body": f"Minh in a room. Shot [0-4s] - {line}. He moves.", **kw}

    def test_the_rules_pick_a_route_and_say_why(self):
        from common.runners import shot_matrix as sm
        cases = {
            "speaks": (self.shot("a", "close, low angle, 18 mm, slow push-in", dialogue=[{"line": "Hi."}]), "wan"),
            "face": (self.shot("b", "close-wide, horizon tilted 20 degrees, 18 mm, handheld; the shot opens on the "
                                    "tail of a fast whip pan right"), "wan"),
            "camera": (self.shot("c", "medium over his shoulder, 24 mm; at 1 s a fast crash zoom into the monitor"),
                       "seedance"),
            "device": (self.shot("d", "wide, high angle 40 degrees down, 20 mm, locked-off, CCTV framing"), "seedance"),
            "clip": (self.shot("e", "wide", clip="shots/x.mp4"), "clip"),
        }
        for name, (shot, route) in cases.items():
            self.assertEqual(sm.decide(shot)[0], route, name)

    def test_a_pinned_row_keeps_its_route_and_apply_writes_the_provider(self):
        from common.runners import shot_matrix as sm
        plan = {"output_dir": "/nonexistent", "shots": [self.shot("a", "close-wide, 18 mm, slow push-in")],
                "matrix": {"a": {"route": "seedance", "pinned": True}}}
        rows = sm.build(plan)
        self.assertEqual(rows["a"]["route"], "seedance")
        self.assertEqual(sm.apply(plan, rows), ["a"])
        self.assertEqual(plan["shots"][0]["video_provider"], "openrouter-seedance-2-5")

    def test_a_shot_made_on_another_route_or_before_its_previs_is_flagged(self):
        from common.runners import shot_matrix as sm
        plan = {"video_provider": "openrouter-wan-3-0", "previs": {"shots": {"c": {}}}}
        item = {"label": "c", "status": "succeeded", "kwargs": {"_route": "openrouter-seedance-2-5"}}
        self.assertEqual(sm._status(item, "wan", plan), "redo")
        self.assertEqual(sm._status(item, "seedance", plan), "no-previs")


class CutTransitions(unittest.TestCase):
    PLAN = {"trailer": {"title_cards": [{"clock_at": 4.0, "seconds": 2.0, "text": "X"}],
                        "acts": [{"name": "montage", "from": "t05", "to": "t06"}]},
            "shots": [{"label": "t01", "clock_at": 0.0, "trim_seconds": 2.0, "body": "Shot [0-4s] - wide, 14 mm."},
                      {"label": "t02", "clock_at": 2.0, "trim_seconds": 2.0,
                       "body": "Shot [0-4s] - medium; at 1 s a crash zoom into the screen. A slap in slow motion."},
                      {"label": "t03", "clock_at": 6.0, "trim_seconds": 2.0, "body": "Shot [0-4s] - medium."},
                      {"label": "t04", "clock_at": 8.0, "trim_seconds": 2.0,
                       "body": "Shot [0-4s] - wide; the shot opens on the tail of a fast whip pan."},
                      {"label": "t05", "clock_at": 10.0, "trim_seconds": 2.0, "location": "a", "body": "Shot - wide."},
                      {"label": "t06", "clock_at": 12.0, "trim_seconds": 2.0, "location": "b", "body": "Shot - wide."}]}

    def test_each_cut_gets_its_transition_by_the_rules(self):
        from common.runners import shot_matrix as sm
        self.assertEqual(sm.transitions(self.PLAN),
                         {"t01": "cut", "t02": "crash", "t03": "flash", "t04": "whip", "t05": "wipe", "t06": "wipe"})

    def test_a_pinned_transition_wins(self):
        from common.runners import shot_matrix as sm
        plan = {**self.PLAN, "matrix": {"t05": {"into": "ramp", "into_pinned": True}}}
        self.assertEqual(sm.transitions(plan)["t05"], "ramp")

    def test_the_wipe_band_leaves_on_the_head_and_enters_on_the_tail(self):
        from common.runners import cut_transitions as ct
        bands = ct.wipes("wipe", "wipe", 2.0)
        self.assertEqual([on for _, on in bands], ["lt(t,0.25)", "gte(t,1.750)"])

    def test_a_ramp_shows_less_action_on_the_tail(self):
        from common.runners import cut_transitions as ct
        normal, slow, factor = ct.ramp_window(2.0)
        self.assertEqual((normal, round(slow, 2), factor), (1.5, 0.2, 2.5))


class ActionSpeed(unittest.TestCase):
    def test_action_in_the_fast_acts_is_undercranked_and_nothing_else_is(self):
        from common.runners import shot_matrix as sm
        plan = {"trailer": {"acts": [{"name": "montage", "from": "a", "to": "c"}]},
                "shots": [{"label": "a", "clock_at": 0, "body": "Shot - medium. Jun throws a punch."},
                          {"label": "b", "clock_at": 1, "body": "Shot - wide, the frame holds still."},
                          {"label": "c", "clock_at": 2, "body": "Shot - close. He punches.", "dialogue": [{"line": "x"}]},
                          {"label": "d", "clock_at": 3, "body": "Shot - medium. They run."}]}
        self.assertEqual([sm.speed(s, plan) for s in plan["shots"]], [sm.ACTION_SPEED, 1.0, 1.0, 1.0])


class Declutter(unittest.TestCase):
    PLAN = {"trailer": {"acts": [{"name": "peak", "from": "a", "to": "c"}],
                        "title_cards": [{"after": "c", "text": "SAME", "clock_at": 6.0}]},
            "narration": [{"shot": "c", "text": "Still not me."}],
            "shots": [{"label": "c", "index": 1, "clock_at": 4.0, "trim_seconds": 2.0, "location": "tier"},
                      {"label": "a", "index": 2, "clock_at": 0.0, "trim_seconds": 2.0, "location": "tier"},
                      {"label": "b", "index": 3, "clock_at": 2.0, "trim_seconds": 2.0, "location": "tier",
                       "dialogue": [{"line": "x"}]}]}

    def test_a_film_that_ends_on_its_picture_keeps_its_sound_to_the_card(self):
        from common.runners.cli import _trailer_sound as ts
        film = {**self.PLAN, "trailer": {**self.PLAN["trailer"], "acts": [{"name": "finale", "from": "a", "to": "c"}]}}
        self.assertIsNone(ts._breath(film))

    def test_acts_follow_the_cut_not_the_numbering(self):
        from common.runners.cli import _trailer_retime as rt
        self.assertEqual(rt._act_of(self.PLAN), {"a": "peak", "b": "peak", "c": "peak"})

    def test_one_sound_at_a_time_and_a_silence_before_the_title(self):
        from common.runners.cli import _trailer_sound as ts
        sound = {"sources": [{"id": "riser"}], "placements": [
            {"source": "score_main", "at": 0.0, "length": 10.0},
            {"source": "prod_a", "at": 0.0, "length": 2.0},
            {"source": "prod_b", "at": 2.0, "length": 2.0},
            {"source": "bed_tier", "at": 0.0, "length": 1.5},
            {"source": "slap", "at": 1.0},
            {"source": "vocal_1", "at": 1.2},
            {"source": "whip", "at": 1.3, "cut": "b"},
            {"source": "vocal_2", "at": 2.5}, {"source": "vocal_3", "at": 3.5},
            {"source": "rail_slam", "at": 4.5},
            {"source": "title_impact", "at": 5.9}]}
        ts.declutter(sound, self.PLAN)
        got = {p["source"]: p for p in sound["placements"]}
        self.assertNotIn("prod_a", got)  # a silent montage shot loses its own noise
        self.assertIn("prod_b", got)  # a speaking one keeps it
        self.assertNotIn("vocal_1", got)  # stacked on the slap
        self.assertNotIn("whip", got)
        self.assertIn("vocal_2", got)
        self.assertNotIn("vocal_3", got)  # one vocal a montage shot
        self.assertNotIn("rail_slam", got)  # inside the silence
        self.assertEqual(got["score_main"]["length"], 4.0)  # the score stops where the last line's shot starts
        self.assertEqual(got["bed_tier"]["gain_db"], -28.0)  # a low room carries the silence
        self.assertIn("title_impact", got)
        self.assertAlmostEqual(got["riser"]["at"], 4.0 - 0.55 - 3.4)


class PeakBuild(unittest.TestCase):
    def test_the_peak_cuts_get_shorter_and_end_on_a_strobe_that_fills_the_act(self):
        from common.runners.cli import _trailer_retime as rt
        shots = [{"label": f"p{i}", "index": i, "clock_at": i * 1.5, "trim_seconds": 1.5, "body": "Shot - wide."}
                 for i in range(6)]
        plan = {"output_dir": "/x", "trailer": {"acts": [{"name": "peak", "from": "p0", "to": "p5"}]},
                "sound": {"sources": [], "placements": [{"source": "slam", "at": 4.6}]}, "shots": shots}
        added = rt.accelerate(plan, "peak", 9.0, [{"from": "p0", "at": 1.0}, {"from": "p1", "at": 0.5}])
        live = sorted(plan["shots"], key=lambda s: s["clock_at"])
        lengths = [s["trim_seconds"] for s in live if not s.get("strobe")]
        self.assertEqual(added, ["s01", "s02"])
        self.assertEqual(lengths, sorted(lengths, reverse=True))
        self.assertGreater(lengths[0], lengths[-1])
        self.assertAlmostEqual(live[-1]["clock_at"] + live[-1]["trim_seconds"], 9.0, places=3)
        p3 = next(s for s in live if s["label"] == "p3")
        self.assertTrue(p3["clock_at"] <= plan["sound"]["placements"][0]["at"] < p3["clock_at"] + p3["trim_seconds"])


class FreezeFrame(unittest.TestCase):
    def test_the_freeze_holds_its_frame_for_the_seconds_asked(self):
        import subprocess
        from PIL import Image
        from common.runners import title_cards
        with tempfile.TemporaryDirectory() as tmp:
            still, out = Path(tmp) / "f.png", Path(tmp) / "f.mp4"
            Image.new("RGB", (320, 180), (90, 110, 120)).save(still)
            title_cards.freeze(still, 1.0, out, bpm=120, caption="PICK ONE.",
                               boxes=[{"box": [40, 40, 120, 140], "label": "MINH TRAN  98.7%"},
                                      {"box": [180, 40, 260, 140], "label": "MINH TRAN  98.7%", "below": True}])
            frames = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v",
                                     "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(out)],
                                    capture_output=True, text=True).stdout.strip()
            self.assertEqual(int(frames), 24)


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

    def test_a_film_drawn_from_a_picture_sends_it_with_every_portrait_and_offers_it_to_frames(self):
        from common.runners.cli import reel_board
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "bible.json").write_text(json.dumps({**BIBLE, "master": "master.png", "cast": [], "locations": []}))
            bible = drama.load_bible(Path(tmp, "bible.json"))
            bible["_judge"] = False
            provider = mock.Mock()
            provider.generate.return_value = mock.Mock(content=b"png", extra={})
            with mock.patch.object(reel_cast.config, "get_provider", return_value=provider):
                reel_cast._take("cast", {"id": "tanya", "prompt": "p"}, bible, "p", Path(tmp, "t.png"))
            self.assertEqual(provider.generate.call_args.kwargs["reference_images"], [str(Path(tmp, "master.png"))])
            board = {}
            reel_board._bible_assets({"bible": "bible.json"}, board, Path(tmp, "plan.json"))
            self.assertEqual(board["_assets"]["master"], str(Path(tmp, "master.png").resolve()))

    def test_a_frame_renumbered_by_an_inserted_shot_is_not_drawn_again(self):
        from common.runners.cli import reel_board
        frame = {"id": "f04", "shot": 5, "prompt": "p", "refs": ["engineer"]}
        self.assertEqual(reel_board._spec_hash(frame, "i"), reel_board._spec_hash({**frame, "shot": 6}, "i"))
        self.assertNotEqual(reel_board._spec_hash(frame, "i"), reel_board._spec_hash({**frame, "prompt": "q"}, "i"))


class Bridge(unittest.TestCase):
    def test_a_bridge_opens_on_the_last_used_frame_of_one_shot_and_ends_on_the_first_of_the_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("a.mp4", "b.mp4"):
                Path(tmp, name).write_bytes(b"x")
            plan = {"output_dir": tmp, "shots": [
                {"label": "a", "trim_start": 0.5, "trim_seconds": 2.0},
                {"label": "x", "bridge": {"from": "a", "to": "b"}, "body": "The camera flies over the pines.",
                 "kwargs": {"duration_seconds": 4, "reference_images": ["p.png"]}},
                {"label": "b", "trim_start": 0.3, "trim_seconds": 2.0}]}
            seen = []
            with mock.patch.object(reel_cast.subprocess, "run", side_effect=lambda cmd, **_: seen.append(cmd)):
                reel_cast._bridge_scene(plan, plan["shots"][1], {"a": Path(tmp, "a.mp4"), "b": Path(tmp, "b.mp4")},
                                        {"look": "3D animated"})
        kwargs = plan["shots"][1]["kwargs"]
        self.assertTrue(kwargs["first_frame"].endswith("x.first.jpg"))
        self.assertTrue(kwargs["last_frame"].endswith("x.last.jpg"))
        self.assertNotIn("reference_images", kwargs)
        self.assertEqual([c[c.index("-ss") + 1] for c in seen], ["2.450", "0.300"])
        self.assertIn("3D animated", plan["shots"][1]["prompt"])

    def test_atlas_sends_a_pinned_shot_to_image_to_video(self):
        from common.runners.providers.atlas_seedance import AtlasSeedance25Provider
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image
            for name in ("f.jpg", "l.jpg"):
                Image.new("RGB", (8, 8)).save(Path(tmp, name))
            body = AtlasSeedance25Provider().build_body("fly", {"first_frame": str(Path(tmp, "f.jpg")),
                                                                "last_frame": str(Path(tmp, "l.jpg")), "duration_seconds": 4})
        self.assertEqual(body["model"], "bytedance/seedance-2.5/image-to-video")
        self.assertEqual(body["ratio"], "adaptive")
        self.assertTrue(body["image"].startswith("data:image/jpeg"))
        self.assertIn("last_image", body)


class Insert(unittest.TestCase):
    def test_a_shot_put_in_moves_everything_after_it_and_stretches_what_runs_across(self):
        from common.runners.cli import _trailer_retime as rt
        plan = {"shots": [{"label": "a", "clock_at": 0.0, "trim_seconds": 2.0},
                          {"label": "b", "clock_at": 2.0, "trim_seconds": 2.0}],
                "trailer": {"title_cards": [{"clock_at": 4.0, "seconds": 1.0}]},
                "sound": {"total_seconds": 5.0, "placements": [{"source": "bed", "at": 0.0, "length": 5.0},
                                                               {"source": "hit", "at": 2.5}]}}
        rt.insert(plan, {"label": "x", "trim_seconds": 1.5}, 2.0)
        self.assertEqual([s["label"] for s in plan["shots"]], ["a", "x", "b"])
        self.assertEqual(plan["shots"][2]["clock_at"], 3.5)
        self.assertEqual(plan["trailer"]["title_cards"][0]["clock_at"], 5.5)
        self.assertEqual(plan["sound"]["placements"][0]["length"], 6.5)
        self.assertEqual(plan["sound"]["placements"][1]["at"], 4.0)
        self.assertEqual(plan["sound"]["total_seconds"], 6.5)


class Picture(unittest.TestCase):
    def test_parts_are_whole_frames_of_the_film_clock_so_the_picture_never_drifts(self):
        from common.runners.cli import reel_animatic as ra
        items = [{"at": i * 2.03, "seconds": 2.03} for i in range(83)]
        frames = sum(round(it["seconds"] * 24) for it in ra.frame_aligned(items))
        self.assertEqual(frames, round(83 * 2.03 * 24))


class ProductionSound(unittest.TestCase):
    def test_a_film_with_its_own_beds_gets_no_second_room_from_the_cut(self):
        from common.runners.cli import _trailer_sound as ts
        plan = {"sound": {"sources": [{"id": "pit_bed", "kind": "sfx", "loop": True}]}, "shots": []}
        self.assertEqual(ts.beds(plan, {"locations": [{"id": "pit"}]}), ([], []))

    def test_without_a_separator_the_voice_is_ducked_in_time_instead(self):
        from common.runners.cli import _trailer_sound as ts
        with mock.patch.dict("os.environ", {}, clear=False), mock.patch.object(ts.shutil, "which", return_value=None):
            os_env = __import__("os").environ
            os_env.pop("AUDIO_SEPARATOR", None)
            self.assertIsNone(ts.without_voice(Path("clip.mp4"), Path("cache")))


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


KIDS = {**BIBLE, "cast": [*BIBLE["cast"],
                          {"id": "bo", "name": "Bo", "identity": "troll toddler, purple hoodie", "voice": "Toddler boy, about 3"},
                          {"id": "lin", "name": "Lin", "identity": "small girl", "age": 30, "voice": "warm alto"}]}
STILL = {"camera": [{"t": 0, "pos": [0, -2, 1], "look": [0, 0, 1]}, {"t": 4, "pos": [0, -2, 1], "look": [0, 0, 1]}]}
MOVING = {"camera": [{"t": 0, "pos": [0, -2, 1], "look": [0, 0, 1]}, {"t": 4, "pos": [0, -1, 1], "look": [0, 0, 1]}]}


class Preflight(unittest.TestCase):
    def test_a_childs_voice_or_singing_turns_the_generations_audio_off(self):
        plan = {"shots": [scene(label="a", cast=["bo"], dialogue=[{"who": "bo", "line": "Ещё!"}]),
                          scene(label="b", cast=["malai"], dialogue=[]),
                          scene(label="c", dialogue=[], body="Malai sings to the cake. [Strictly exclude]: singing"),
                          scene(label="d", dialogue=[], body="Shot 1 [0-4s]. No singing."),
                          scene(label="e", cast=["lin"], dialogue=[{"who": "lin", "line": "Hi"}])],
                "vocals": [{"shot": "b", "who": "bo", "text": "[giggles]"}]}
        notes = drama.preflight(plan, KIDS)
        audio = {s["label"]: (s.get("kwargs") or {}).get("generate_audio") for s in plan["shots"]}
        self.assertEqual(audio, {"a": False, "b": False, "c": False, "d": None, "e": None}, "an age beats the words")
        self.assertIn("a: generate_audio off, a child speaks (Bo)", notes)

    def test_a_locked_off_previs_is_noted_not_dropped_and_explicit_keys_stay(self):
        plan = {"previs": {"shots": {"a": STILL, "b": MOVING, "c": STILL}},
                "shots": [scene(label="a", cast=["bo"], dialogue=[{"who": "bo", "line": "Ой"}],
                                kwargs={"generate_audio": True, "reference_videos": ["previs/a.mp4"]}),
                          scene(label="b"), scene(label="c", no_previs=False)]}
        notes = drama.preflight(plan, KIDS)
        self.assertEqual([s.get("no_previs") for s in plan["shots"]], [None, None, False])
        self.assertEqual(plan["shots"][0]["kwargs"], {"generate_audio": True, "reference_videos": ["previs/a.mp4"]},
                         "audio set by hand stays on, the previs stays sent")
        self.assertTrue(any(n.startswith("a: the previs camera is locked off") for n in notes))

    def test_cast_scenes_runs_the_preflight_first(self):
        plan = {"shots": [scene(cast=["bo"], dialogue=[{"who": "bo", "line": "Ой"}])]}
        reel_cast.cast_scenes(plan, KIDS)
        self.assertFalse(plan["shots"][0]["kwargs"]["generate_audio"])


class StoryCheck(unittest.TestCase):
    def test_the_screenplay_is_action_and_lines_in_order_without_the_boilerplate(self):
        plan = {"trailer": {"title_cards": [{"after": "t00", "text": "Birthday"}, {"after": "t2", "text": ""}]},
                "shots": [scene(label="t1", scene=1, dialogue=[{"who": "malai", "line": "เร็วเข้า"}],
                                body="Malai runs. Dialogue language: Thai. <rain> No music. [Strictly exclude]: text"),
                          scene(label="t2", scene=1, dialogue=[], body="Malai says: {ok}"),
                          scene(label="x", clip="shots/x.mp4", body="", dialogue=[])]}
        self.assertEqual(drama.screenplay_text(plan, BIBLE),
                         "[title card: Birthday]\n\nt1 (scene 1)\nMalai runs. <rain>\n  Malai: เร็วเข้า\n\n"
                         "t2 (scene 1)\nMalai says: {ok}")

    def test_coverage_names_a_wide_that_carries_no_line(self):
        plan = {"shots": [scene(label="w", coverage="w", dialogue=[]), scene(label="c1", coverage="w"),
                          scene(label="c2", coverage="nope"), scene(label="w2", coverage="w2")]}
        self.assertEqual(drama.validate(plan, BIBLE), ["c2: coverage 'nope' is not a wide that names itself",
                                                       "w2: a coverage wide carries no line; the close-ups do"])


if __name__ == "__main__":
    unittest.main()
