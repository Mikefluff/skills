"""The cut's parts: a part kept by everything that makes it, the picture's signature, and an --audio-only build
refused on a stale picture."""

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.runners.cli import _animatic_parts as parts  # noqa: E402
from common.runners.cli import reel_animatic as ra  # noqa: E402
from common.runners.cli._animatic_picture import Takes  # noqa: E402
from common.runners.errors import RunnerError  # noqa: E402


def _shot(label, index, at, **kw):
    return {"label": label, "index": index, "clock_at": at, "trim_seconds": 2.0, "trim_start": 0.0,
            "location": "room", "body": "Shot [a] - medium, static. Ann waits.", "dialogue": [], **kw}


class Cut(unittest.TestCase):
    def setUp(self):
        self.out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clips = {}
        for label in ("t01", "t02"):
            self.clips[label] = self.out / f"{label}.mp4"
            self.clips[label].write_bytes(b"clip")
        # where a window starts is the plan's trim here; the real one also probes the clip's length
        self.enterContext(mock.patch.object(parts, "clip_start", lambda shot, *_: float(shot["trim_start"])))

    def _plan(self, **kw):
        return {"output_dir": str(self.out), "grade": "candy", "hd": True,
                "shots": [_shot("t01", 1, 0.0, dialogue=[{"who": "ann", "line": "Hi", "gain_db": 0}]),
                          _shot("t02", 2, 2.0)],
                "vocals": [{"shot": "t01", "who": "ann", "at": 0.5, "text": "[laughs]", "gain_db": 0}], **kw}

    def _keys(self, plan):
        return {p.label: p.key for p in parts.cut_parts(plan, self.out / "board", Takes(clips=self.clips))}


class Signature(Cut):
    def test_a_shots_trim_changes_its_part_and_no_other(self):
        plan = self._plan()
        before = self._keys(plan)
        plan["shots"][0]["trim_start"] = 0.5
        after = self._keys(plan)
        self.assertNotEqual(before["t01"], after["t01"])
        self.assertEqual(before["t02"], after["t02"])

    def test_a_transition_changes_both_sides_of_its_cut(self):
        plan = self._plan()
        before = self._keys(plan)
        plan["shots"][1]["into"] = "dip"  # the tail of t01 now fades out
        after = self._keys(plan)
        self.assertNotEqual(before["t01"], after["t01"])
        self.assertNotEqual(before["t02"], after["t02"])

    def test_sound_only_changes_leave_the_picture_alone(self):
        plan = self._plan()
        before = self._keys(plan)
        plan["shots"][0]["dialogue"][0]["gain_db"] = 6
        plan["vocals"][0]["gain_db"] = -3
        plan["vocals"].append({"shot": "t02", "who": "ann", "at": 2.4, "text": "[sighs]"})
        plan["sound"] = {"placements": [{"source": "score_main", "at": 0, "length": 4}]}
        self.assertEqual(before, self._keys(plan))

    def test_grade_and_size_are_in_every_part(self):
        plan = self._plan()
        before = self._keys(plan)
        self.assertTrue(all(before[k] != v for k, v in self._keys(self._plan(grade=None)).items()))
        self.assertTrue(all(before[k] != v for k, v in self._keys(self._plan(hd=False)).items()))


class PartCache(Cut):
    def test_the_same_inputs_are_the_same_file_and_a_touched_clip_is_not(self):
        plan = self._plan()
        first = parts.cut_parts(plan, self.out, Takes(clips=self.clips))[0]
        again = parts.cut_parts(plan, self.out, Takes(clips=self.clips))[0]
        self.assertEqual(first.path, again.path)
        self.assertEqual(first.path.parent, self.out / "parts")
        self.clips["t01"].write_bytes(b"a new take")
        self.assertNotEqual(first.path, parts.cut_parts(plan, self.out, Takes(clips=self.clips))[0].path)

    def test_a_kept_part_is_reused_not_drawn(self):
        drawn = []
        part = parts.Part("t01", ["clip", 1], lambda out: (drawn.append(out), out.write_bytes(b"v")), self.out)
        self.assertTrue(parts._ensure(part))
        self.assertFalse(parts._ensure(part))
        self.assertEqual(len(drawn), 1)
        self.assertEqual(part.path.read_bytes(), b"v")
        self.assertFalse(list(self.out.glob("*.tmp.mp4")))

    def test_the_drawing_code_is_in_the_file_name_but_not_in_the_signature(self):
        part = parts.Part("t01", ["clip", 1], lambda out: None, self.out)
        with mock.patch.object(parts, "_code", lambda: "other"):
            moved = parts.Part("t01", ["clip", 1], lambda out: None, self.out)
        self.assertEqual(part.key, moved.key)
        self.assertNotEqual(part.path, moved.path)


class AudioOnly(Cut):
    def test_a_stale_picture_is_refused_naming_the_shot(self):
        plan = self._plan()
        cut = self.out / "trailer.mp4"
        cut.write_bytes(b"picture")
        parts.record(cut, parts.cut_parts(plan, self.out, Takes(clips=self.clips)))
        parts.fresh(cut, parts.cut_parts(plan, self.out, Takes(clips=self.clips)))  # unchanged: accepted
        plan["shots"][1]["trim_seconds"] = 2.5
        with self.assertRaises(RunnerError) as err:
            parts.fresh(cut, parts.cut_parts(plan, self.out, Takes(clips=self.clips)))
        self.assertIn("t02 changed", str(err.exception))
        self.assertNotIn("t01", str(err.exception))
        self.assertIn("picture build", str(err.exception))

    def test_a_picture_without_a_signature_is_refused(self):
        (self.out / "trailer.mp4").write_bytes(b"picture")
        with self.assertRaises(RunnerError):
            parts.fresh(self.out / "trailer.mp4", [])

    def test_an_audio_only_run_never_saves_the_plan(self):
        plan_file = self.out / "plan.json"
        plan_file.write_text("{}", encoding="utf-8")
        ra._save(argparse.Namespace(plan_file=plan_file, audio_only=True), {"shots": []})
        self.assertEqual(json.loads(plan_file.read_text(encoding="utf-8")), {})

    def test_fit_lines_with_audio_only_is_refused(self):
        argv = ["reel_animatic", "--plan-file", str(self.out / "plan.json"), "--clips", "--audio-only", "--fit-lines"]
        with mock.patch.object(sys, "argv", argv), mock.patch("sys.stderr"):
            self.assertEqual(ra.main(), 1)


if __name__ == "__main__":
    unittest.main()
