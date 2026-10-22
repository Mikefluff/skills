"""Nothing the cut's sound already has is bought, priced or rendered again: the score across a retime, the
exchanges' takes, their split lines, the shots' own sound, and the plan file itself."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.runners.cli import _animatic_mix as amix  # noqa: E402
from common.runners.cli import _animatic_voice as av  # noqa: E402
from common.runners.cli import _reel_sound as rs  # noqa: E402
from common.runners.cli import _trailer_sound as ts  # noqa: E402
from common.runners.cli import _stage_cache as sc  # noqa: E402


def _score(setup_ms=4000, chase_ms=2000, style="104 bpm caper"):
    return {"id": "caper_score", "kind": "music", "composition_plan": {
        "positive_global_styles": [style],
        "sections": [{"section_name": "setup", "duration_ms": setup_ms}, {"section_name": "chase", "duration_ms": chase_ms}]}}


class Score(unittest.TestCase):
    def setUp(self):
        self.dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.take = self.dir / "caper.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=220:d=6", str(self.take)],
                       check=True)

    def test_a_take_kept_before_the_score_key_is_adopted_and_survives_a_retime(self):
        index = {"caper_score": {"path": str(self.take), "hash": rs._spec_hash(_score())}}
        self.assertIn("caper_score", rs._cached({"caper_score": _score()}, index))
        self.assertEqual(index["caper_score"]["made_ms"], [4000, 2000])
        self.assertIn("caper_score", rs._cached({"caper_score": _score(setup_ms=5000)}, index))

    def test_a_score_whose_music_changed_is_made_again(self):
        index = {"caper_score": rs._entry(_score(), str(self.take))}
        self.assertNotIn("caper_score", rs._cached({"caper_score": _score(style="90 bpm tango")}, index))
        self.assertNotIn("caper_score", rs._cached({"caper_score": {**_score(), "take": 2}}, index))

    def test_a_grown_act_stretches_its_section_of_the_take(self):
        entry = rs._entry(_score(), str(self.take))
        self.assertEqual(rs._fitted(_score(), entry, self.take, self.dir), self.take)  # same lengths: as made
        fitted = rs._fitted(_score(setup_ms=5000), entry, self.take, self.dir)
        self.assertNotEqual(fitted, self.take)
        self.assertAlmostEqual(av._probe(fitted), 7.0, delta=0.1)
        with mock.patch.object(rs.subprocess, "run") as run:
            self.assertEqual(rs._fitted(_score(setup_ms=5000), entry, self.take, self.dir), fitted)
        run.assert_not_called()

    def test_only_sources_not_kept_are_priced(self):
        sfx = {"id": "pop", "kind": "sfx", "prompt": "a pop", "duration_seconds": 1}
        sound = {"sources": [_score(), sfx], "placements": []}
        (self.dir / "sound").mkdir()
        (self.dir / "sound" / "sources.json").write_text(json.dumps({
            "caper_score": rs._entry(_score(), str(self.take)),
            "pop": {"path": str(self.take), "hash": rs._spec_hash(sfx)}}))
        with mock.patch.object(rs.batch_mod, "estimate_batch_cost", return_value=Decimal("1")) as est:
            self.assertEqual(rs.estimate(sound, self.dir), Decimal("0"))
        est.assert_not_called()


class Takes(unittest.TestCase):
    def setUp(self):
        self.cache = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.group = [{"who": "ann", "line": "Привет", "label": "t01", "location": None}]

    def test_the_language_is_in_the_key_and_an_older_take_is_moved_not_bought(self):
        voices = {"ann": "v1"}
        (new, new_marks), (old, old_marks) = av._take_paths(self.group, voices, self.cache, "ru", None)
        self.assertNotEqual(new, old)
        self.assertFalse(av.take_kept(self.group, voices, self.cache, "ru"))
        old.write_bytes(b"mp3")
        old_marks.write_text("[]")
        self.assertTrue(av.take_kept(self.group, voices, self.cache, "ru"))
        self.assertEqual(av.take_files(self.group, voices, self.cache, "ru"), (new, new_marks))
        self.assertTrue(new.is_file() and not old.is_file())

    def test_lines_cut_from_a_take_are_kept(self):
        take = self.cache / "abc.mp3"
        take.write_bytes(b"mp3")
        segments = [{"dialogue_input_index": 0, "start_time_seconds": 0.0, "end_time_seconds": 1.0}]
        with mock.patch.object(av, "_cut", side_effect=lambda t, clip, *_: clip.write_bytes(b"wav")) as cut:
            av._split(take, segments, 1, self.cache / "abc")
            av._split(take, segments, 1, self.cache / "abc")
        self.assertEqual(cut.call_count, 1)

    def test_the_lines_lengths_go_through_the_kept_probe(self):
        with mock.patch.object(sc, "probed", return_value=1.5) as kept:
            self.assertEqual(av._seconds(self.cache / "a.wav"), 1.5)
        self.assertIs(kept.call_args[0][1], av._probe)


class NothingToBuy(unittest.TestCase):
    def test_a_cut_with_everything_kept_costs_nothing(self):
        out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        plan = {"output_dir": str(out), "sound": {"sources": [], "placements": []},
                "shots": [{"label": "t01", "clock_at": 0, "trim_seconds": 2, "scene": 1,
                           "dialogue": [{"who": "ann", "line": "Hi"}]}],
                "vocals": [{"shot": "t01", "who": "ann", "text": "[laughs]"}]}
        voices = {"ann": "v1"}
        group = av.exchanges(plan)[0]
        take, marks = av.take_files(group, voices, out / "animatic-lines", "ru")
        take.parent.mkdir(parents=True)
        take.write_bytes(b"mp3")
        marks.write_text("[]")
        from common.runners.cli import _drama_pass as dp

        vocal = dp.vocal_file(plan["vocals"][0], out, "v1")
        vocal.parent.mkdir(parents=True)
        vocal.write_bytes(b"mp3")
        total, what = amix.to_buy(plan, {"language": "ru"}, voices)
        self.assertEqual((total, what), (Decimal("0"), []))
        vocal.unlink()
        with mock.patch.object(amix, "_spoken", return_value=Decimal("0.01")):
            self.assertEqual(amix.to_buy(plan, {"language": "ru"}, voices)[1], ["1 vocal(s) to voice"])


class ShotSound(unittest.TestCase):
    def test_a_shots_own_sound_is_rendered_once_for_the_same_window(self):
        out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clip = out / "t01.mp4"
        clip.write_bytes(b"clip")
        shot = {"label": "t01", "trim_seconds": 2.0, "clock_at": 0}
        with mock.patch.object(ts, "_production", side_effect=lambda *a: a[-1].write_bytes(b"wav")) as made:
            ts.production(shot, clip, 0.5, None, out / "t01.wav")
            ts.production(shot, clip, 0.5, None, out / "t01.wav")
            ts.production(shot, clip, 0.7, None, out / "t01.wav")
        self.assertEqual(made.call_count, 2)


class Mix(unittest.TestCase):
    def test_a_mix_of_the_same_inputs_is_not_run_again(self):
        out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        src, mixed = out / "a.wav", out / "mix.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=d=0.5", str(src)], check=True)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", "volume=0.5", str(mixed)]
        self.assertTrue(sc.run_once(cmd, mixed))
        self.assertFalse(sc.run_once(cmd, mixed))
        os.utime(src, ns=(1, 1))  # an input made again
        self.assertTrue(sc.run_once(cmd, mixed))
        self.assertTrue(sc.run_once([*cmd[:-2], "volume=0.4", str(mixed)], mixed))


CALLS = []


def _measure(path):
    CALLS.append(path)
    return 2.5


class Probes(unittest.TestCase):
    def test_a_files_length_is_kept_across_runs_until_the_file_changes(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clip = tmp / "a.mp4"
        clip.write_bytes(b"x")
        with mock.patch.object(sc, "_PROBE_FILE", tmp / "probed.json"), mock.patch.dict(sc._PROBED, clear=True):
            self.assertEqual(sc.probed(clip, _measure), 2.5)
            sc._save_probes()
            sc._PROBED.clear()  # a new run
            self.assertEqual(sc.probed(clip, _measure), 2.5)
            os.utime(clip, ns=(1, 1))
            sc.probed(clip, _measure)
            sc._NEW.clear()
        self.assertEqual(len(CALLS), 2)


class PlanFile(unittest.TestCase):
    def test_an_unchanged_plan_is_not_written(self):
        path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "plan.json"
        self.assertTrue(sc.save_json(path, {"a": 1}))
        self.assertFalse(sc.save_json(path, {"a": 1}))


if __name__ == "__main__":
    unittest.main()
