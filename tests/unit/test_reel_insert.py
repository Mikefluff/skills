"""reel_insert splices shots into a plan: the clock, the frames, the sound and the total move with them."""

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.runners.cli import reel_insert  # noqa: E402


def _shot(label, at, length, **extra):
    return {"label": label, "cast": ["ann"], "location": "room", "dialogue": [], "body": "Shot.",
            "trim_start": 0.3, "trim_seconds": length, "kwargs": {"duration_seconds": 6},
            "clock_at": at, **extra}


_PREVIS = {"set": "room", "camera": [{"t": 0, "pos": [0, -3, 1.5], "look": [0, 0, 1]},
                                    {"t": 4, "pos": [0, -2, 1.5], "look": [0, 0, 1]}]}


def _plan():
    shots = [_shot("a", 0.0, 4.0), _shot("b", 4.0, 3.0), _shot("c", 7.0, 5.0)]
    for n, s in enumerate(shots, 1):
        s["index"] = n
    return {"bible": "bible.json", "shots": shots,
            "board": {"frames": [{"id": "fa", "shot": 1}, {"id": "fb", "shot": 2}, {"id": "fc", "shot": 3}]},
            "trailer": {"title_cards": [{"clock_at": 12.0, "text": "end"}]},
            "sound": {"total_seconds": 12.0, "placements": [
                {"source": "bed", "at": 0.0, "length": 12.0}, {"source": "door", "at": 7.5}]},
            "previs": {"sets": {"room": []}, "shots": {"b": _PREVIS}},
            "vocals": [{"shot": "b", "who": "ann", "at": 1.0, "text": "Oh"}], "continuity": []}


_BIBLE = {"language": "en", "cast": [{"id": "ann", "name": "Ann", "identity": "x"}],
          "locations": [{"id": "room", "description": "a room"}]}


class TestReelInsert(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.dir / "bible.json").write_text(json.dumps(_BIBLE))
        self.plan_file = self.dir / "plan.json"
        self.plan_file.write_text(json.dumps(_plan()))

    def _run(self, inserts, *flags):
        src = self.dir / "inserts.json"
        src.write_text(json.dumps(inserts))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = reel_insert.main(["--plan-file", str(self.plan_file), "--from", str(src), *flags])
        return rc, out.getvalue() + err.getvalue()

    def _saved(self):
        plan = json.loads(self.plan_file.read_text())
        return plan, {s["label"]: s for s in plan["shots"]}

    def test_insert_after_moves_later_shots_sound_and_frames(self):
        rc, out = self._run({"shots": [{"insert_after": "a", "shot": _shot("a2", 0, 2.0),
                                        "frame": {"id": "fa2"}, "previs": _PREVIS,
                                        "vocals": [{"shot": "a2", "who": "ann", "at": 0.5, "text": "Hm"}]}],
                             "continuity": [{"what": "cup", "state": "full", "from": "a2"}]})
        self.assertEqual(0, rc, out)
        plan, by = self._saved()
        self.assertEqual((4.0, 2), (by["a2"]["clock_at"], by["a2"]["index"]))
        self.assertEqual((6.0, 3), (by["b"]["clock_at"], by["b"]["index"]))
        self.assertEqual(9.0, by["c"]["clock_at"])
        self.assertEqual({"fa": 1, "fa2": 2, "fb": 3, "fc": 4}, {f["id"]: f["shot"] for f in plan["board"]["frames"]})
        self.assertEqual(14.0, plan["sound"]["total_seconds"])
        self.assertEqual([0.0, 9.5], [p["at"] for p in plan["sound"]["placements"]])
        self.assertEqual(14.0, plan["sound"]["placements"][0]["length"])
        self.assertEqual(14.0, plan["trailer"]["title_cards"][0]["clock_at"])
        self.assertIn("a2", plan["previs"]["shots"])
        self.assertEqual(2, len(plan["vocals"]))
        self.assertEqual(1, len(plan["continuity"]))
        self.assertTrue((self.dir / "plan.json.bak").is_file())
        self.assertIn("reel_previs", out)

    def test_insert_before(self):
        self.assertEqual(0, self._run({"shots": [{"insert_before": "c", "shot": _shot("c0", 0, 1.0)}]})[0])
        _, by = self._saved()
        self.assertEqual((7.0, 8.0), (by["c0"]["clock_at"], by["c"]["clock_at"]))

    def test_replace_keeps_the_total_consistent(self):
        rc, out = self._run({"shots": [{"replace": "b", "shot": _shot("b2", 0, 5.0), "frame": {"id": "fb2"}}]})
        self.assertEqual(0, rc, out)
        plan, by = self._saved()
        self.assertNotIn("b", by)
        self.assertEqual((4.0, 2), (by["b2"]["clock_at"], by["b2"]["index"]))
        self.assertEqual(9.0, by["c"]["clock_at"])
        self.assertEqual(14.0, plan["sound"]["total_seconds"])  # 12 - 3 + 5
        self.assertEqual({"fa": 1, "fb2": 2, "fc": 3}, {f["id"]: f["shot"] for f in plan["board"]["frames"]})
        self.assertNotIn("b", plan["previs"]["shots"])
        self.assertEqual([], plan["vocals"])

    def test_a_clip_only_shot_needs_no_frame_or_body(self):
        clip = {"label": "b9", "clip": "shots/x.mp4", "trim_start": 3.4, "trim_seconds": 0.9}
        rc, out = self._run({"shots": [{"insert_after": "b", "shot": clip}]})
        self.assertEqual(0, rc, out)
        plan, by = self._saved()
        self.assertEqual(7.0, by["b9"]["clock_at"])
        self.assertAlmostEqual(7.9, by["c"]["clock_at"])
        self.assertEqual(3, len(plan["board"]["frames"]))
        self.assertIn("(clip)", out)
        self.assertNotIn("reel --plan-file", out)

    def test_dry_run_writes_nothing(self):
        before = self.plan_file.read_text()
        rc, out = self._run({"shots": [{"insert_after": "a", "shot": _shot("a2", 0, 2.0)}]}, "--dry-run")
        self.assertEqual(0, rc, out)
        self.assertEqual(before, self.plan_file.read_text())
        self.assertFalse((self.dir / "plan.json.bak").exists())

    def test_rejections(self):
        before = self.plan_file.read_text()
        cases = [{"insert_after": "a", "shot": _shot("b", 0, 1.0)},  # duplicate label
                 {"insert_after": "zz", "shot": _shot("n", 0, 1.0)},  # missing anchor
                 {"insert_after": "a", "shot": _shot("n", 0, 1.0), "frame": {"id": "fb"}},  # duplicate frame
                 {"insert_after": "a", "shot": _shot("n", 0, 1.0, cast=["bob"])}]  # not in the bible
        for entry in cases:
            with self.subTest(entry=entry):
                self.assertEqual(1, self._run({"shots": [entry]})[0])
        self.assertEqual(before, self.plan_file.read_text())


if __name__ == "__main__":
    unittest.main()
