"""A short film's controls: a shot that opens on its own board frame, a line's own loudness, a line re-voiced
when its words change."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.runners import drama  # noqa: E402
from common.runners.cli import _animatic_voice as av  # noqa: E402
from common.runners.cli import _drama_pass as dp  # noqa: E402
from common.runners.cli import reel_cast, reel_previs  # noqa: E402
from common.runners.errors import RunnerError  # noqa: E402

BIBLE = {"_dir": "/series", "language": "ru", "look": "felted 3D",
         "cast": [{"id": "ann", "name": "Ann", "identity": "woman"}],
         "locations": [{"id": "room", "description": "a room"}]}


def _shot(**kw):
    return {"index": 1, "label": "t01", "cast": ["ann"], "location": "room", "dialogue": [],
            "body": "Start exactly on the image. Ann ducks.",
            "kwargs": {"duration_seconds": 5, "resolution": "480p", "aspect_ratio": "16:9", "generate_audio": False,
                       "reference_images": ["x.png"], "reference_videos": ["p.mp4"], "media_host": "litterbox",
                       "reference_audio": ["a.mp3"]}, **kw}


class OpenOnFrame(unittest.TestCase):
    def setUp(self):
        self.out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.out / "board").mkdir()
        (self.out / "board" / "f01.jpg").write_bytes(b"jpg")
        (self.out / "board" / "f01.png").write_bytes(b"png")

    def _plan(self, **kw):
        return {"output_dir": str(self.out), "board": {"frames": [{"id": "f01", "shot": 1}]},
                "previs": {"shots": {"t01": {}}}, "shots": [_shot(open_on_frame=True, **kw)]}

    def test_the_board_png_opens_the_shot_and_nothing_else_is_sent(self):
        plan = self._plan()
        reel_cast.cast_scenes(plan, BIBLE)
        shot = plan["shots"][0]
        self.assertEqual({"duration_seconds": 5, "resolution": "480p", "aspect_ratio": "16:9",
                          "generate_audio": False, "first_frame": str(self.out / "board" / "f01.png")}, shot["kwargs"])
        self.assertEqual("Start exactly on the image. Ann ducks.\n[Overall style]: felted 3D", shot["prompt"])

    def test_it_matches_the_bridge_from_image_it_replaces(self):
        png = str(self.out / "board" / "f01.png")
        flagged, bridged = self._plan(), self._plan()
        del bridged["shots"][0]["open_on_frame"]
        bridged["shots"][0]["bridge"] = {"from_image": png}
        reel_cast.cast_scenes(flagged, BIBLE)
        reel_cast.cast_scenes(bridged, BIBLE)
        self.assertEqual(bridged["shots"][0]["kwargs"], flagged["shots"][0]["kwargs"])
        self.assertEqual(bridged["shots"][0]["prompt"], flagged["shots"][0]["prompt"])

    def test_no_board_frame_is_refused(self):
        plan = self._plan()
        plan["board"]["frames"] = []
        with self.assertRaisesRegex(RunnerError, "run reel_board first"):
            reel_cast.cast_scenes(plan, BIBLE)

    def test_validate_wants_a_frame_for_the_shot(self):
        plan = self._plan()
        self.assertEqual([], drama.validate(plan, BIBLE))
        plan["board"]["frames"] = [{"id": "f02", "shot": 2}]
        self.assertEqual(["t01: open_on_frame but no storyboard frame for shot 1"], drama.validate(plan, BIBLE))

    def test_preflight_and_previs_leave_it_alone(self):
        plan = self._plan()
        plan["previs"] = {"sets": {"room": []}, "shots": {"t01": {"set": "room", "camera": [
            {"t": 0, "pos": [0, -3, 1.5], "look": [0, 0, 1]}, {"t": 4, "pos": [0, -3, 1.5], "look": [0, 0, 1]}]}}}
        self.assertEqual([], drama.preflight(plan, BIBLE), "a locked-off previs is not noted for it")
        self.assertEqual([], reel_previs.job(plan, self.out, None)["shots"])
        (self.out / "t01.mp4").write_bytes(b"mp4")
        self.assertEqual([], reel_previs._hand_clips(plan, self.out))


class LineGain(unittest.TestCase):
    def test_gain_is_clamped(self):
        self.assertEqual([0.0, 3.0, 12.0, -12.0], [av.gain_db(x) for x in
                                                   ({}, {"gain_db": 3}, {"gain_db": 30}, {"gain_db": -40})])

    def test_mix_lifts_a_line_by_its_gain_on_top_of_the_short_line_lift(self):
        placed = [(Path("long.wav"), 1.0, 1.0), (Path("short.wav"), 3.0, 1.0), (Path("plain.wav"), 5.0, 1.0)]
        with mock.patch.object(av, "_seconds", side_effect=lambda p: 0.5 if p.name == "short.wav" else 2.0), \
                mock.patch.object(av.subprocess, "run") as run:
            av.mix(placed, 10.0, Path("out.wav"), [4.0, -2.0, 0.0])
        graph = run.call_args[0][0][run.call_args[0][0].index("-filter_complex") + 1].split(";")
        self.assertIn("volume=4dB,alimiter", graph[0])
        self.assertIn("volume=3dB,alimiter", graph[1])  # 5 dB short-line lift, 2 dB down
        self.assertNotIn("volume", graph[2])

    def test_a_vocal_placement_carries_its_gain(self):
        plan = {"shots": [{"label": "t01", "clock_at": 2.0}],
                "vocals": [{"shot": "t01", "who": "ann", "at": 0.5, "text": "Ой", "gain_db": 4},
                           {"shot": "t01", "who": "crowd", "at": 1.0, "text": "[cheer]"}]}
        out = dp.placements(plan, {0: Path("a.mp3"), 1: Path("b.mp3")})
        self.assertEqual([5, -3], [p["gain_db"] for p in out])


class Revoice(unittest.TestCase):
    def test_an_edited_line_is_read_in_its_new_words(self):
        line = {"line": "Растёт!", "performance": "[panicked gasp] Он растёт!"}
        self.assertEqual("[panicked gasp] Растёт!", av._text(line))
        self.assertEqual("[panicked gasp] Он растёт!", av._text({**line, "line": "Он растет"}))

    def test_the_take_cache_key_follows_the_words(self):
        keys = []
        group = [{"who": "ann", "line": "Он растёт!", "performance": "[gasp] Он растёт!", "location": "room"}]
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(av, "_clean_take", return_value=(b"mp3", [])) as take, \
                mock.patch.object(av, "_split", side_effect=lambda t, s, n, stem: keys.append(stem.name) or []):
            av.read_exchange(group, {"ann": "v1"}, Path(tmp), "ru")
            av.read_exchange([{**group[0], "line": "Растёт!"}], {"ann": "v1"}, Path(tmp), "ru")
            av.read_exchange(group, {"ann": "v1"}, Path(tmp), "ru")
        self.assertNotEqual(keys[0], keys[1])
        self.assertEqual(keys[0], keys[2])
        self.assertEqual(2, take.call_count, "the unchanged line comes from the cache")


if __name__ == "__main__":
    unittest.main()


def test_a_russian_take_is_checked_word_for_word():
    from common.runners.cli import _animatic_voice as av
    assert av._words("[hurried] Ещё раз! У нас сорок минут…") == ["еще", "раз", "у", "нас", "сорок", "минут"]
    assert av._errors(av._words("Он растёт!"), av._words("Он растёт, растёт!")) == 1
    assert av._words("ninety-eight point seven, it's me") == ["ninety", "eight", "point", "seven", "it's", "me"]
