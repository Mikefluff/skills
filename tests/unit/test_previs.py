"""Previs spec: camera moves expand into keys, and a spec that cannot render says why."""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import previs as pv  # noqa: E402


def spec(**shot):
    return {"sets": {"arena": [{"kind": "box", "id": "mh1", "at": [0, 5, 0.3], "size": [0.5, 0.5, 0.7]}]},
            "shots": {"s01": {"set": "arena", **shot}}}


class Orbit(unittest.TestCase):
    def test_an_orbit_circles_its_centre_at_its_radius_and_looks_at_it(self):
        keys = pv.orbit({"center": [0, 0, 1.6], "radius": 2.0, "deg": [0, 180], "height": 1.5, "t": [1, 3], "steps": 4})
        self.assertEqual([k["t"] for k in keys], [1.0, 1.5, 2.0, 2.5, 3.0])
        for k in keys:
            self.assertAlmostEqual((k["pos"][0] ** 2 + k["pos"][1] ** 2) ** 0.5, 2.0, places=2)
            self.assertEqual(k["look"], [0, 0, 1.6])
        self.assertAlmostEqual(keys[0]["pos"][1], -2.0, places=2, msg="0° is behind the subject")

    def test_moves_and_plain_keys_come_out_in_time_order(self):
        keys = pv.camera_keys({"camera": [{"t": 4, "pos": [0, 9, 1], "look": [0, 20, 1]},
                                          {"move": "orbit", "t": [0, 2], "center": [0, 0, 1], "radius": 1,
                                           "deg": [0, 90], "height": 1, "steps": 2}]})
        self.assertEqual([k["t"] for k in keys], [0.0, 1.0, 2.0, 4])


class Ensemble(unittest.TestCase):
    CAMERA = [{"t": 0, "pos": [0, -2, 1], "look": [0, 1, 1]}, {"t": 3, "pos": [0, -1, 1], "look": [0, 1, 1]}]

    def test_actors_and_moving_props_are_checked_like_every_other_timed_key(self):
        good = spec(camera=self.CAMERA,
                    actors=[{"id": "tanya", "height": 1.2, "hair": "big",
                             "keys": [{"t": 0, "pos": [0, 1], "pose": "stand"}, {"t": 2, "pos": [0, 1], "pose": "jump"}]}],
                    extra=[{"kind": "cylinder", "at": [0, 2, 0.3], "anim": [{"t": 0, "at": [0, 2, 0.3]}, {"t": 3, "at": [0, 2, 2]}]}])
        self.assertEqual(pv.validate(good, {"s01": 3}), [])

    def test_an_unknown_pose_a_late_key_and_a_keyless_actor_are_named(self):
        bad = spec(camera=self.CAMERA,
                   actors=[{"id": "tanya", "keys": [{"t": 5, "pos": [0, 1], "pose": "moonwalk"}]}, {"id": "arthur"}],
                   extra=[{"kind": "box", "at": [0, 0, 0], "size": [1, 1, 1], "anim": [{"t": 9, "at": [0, 0, 1]}]}])
        problems = " ".join(pv.validate(bad, {"s01": 3}))
        self.assertIn("pose 'moonwalk'", problems)
        self.assertIn("time 5", problems)
        self.assertIn("time 9", problems)
        self.assertIn("actor arthur has no keys", problems)


class Validate(unittest.TestCase):
    def test_a_good_spec_has_no_problems(self):
        good = spec(camera=[{"t": 0, "pos": [0, -1, 1.7], "look": [0, 5, 1]}, {"t": 4, "pos": [0, 9, 1], "look": [0, 20, 1]}],
                    fire=[{"t": 1, "id": "mh1"}])
        self.assertEqual(pv.validate(good, {"s01": 4}), [])

    def test_times_past_the_generation_unknown_ids_and_one_key_cameras_are_caught(self):
        bad = spec(camera=[{"t": 6, "pos": [0, 0, 1], "look": [0, 1, 1]}], fire=[{"t": 1, "id": "nope"}])
        problems = " ".join(pv.validate(bad, {"s01": 4}))
        self.assertIn("at least two keys", problems)
        self.assertIn("outside 0-4s", problems)
        self.assertIn("unknown id 'nope'", problems)


class Framing(unittest.TestCase):
    """The head projection the previs uses to flag shots that lose or shrink their cast."""

    ADULT = {"id": "arthur", "height": 1.2, "keys": [{"t": 0, "pos": [0, 0], "facing": 180}]}

    def shot(self, pos, look, lens=50, actor=None):
        return {"set": "pit", "lens": lens, "camera": [{"t": 0, "pos": pos, "look": look}, {"t": 4, "pos": pos, "look": look}],
                "actors": [actor or self.ADULT]}

    def test_a_head_the_camera_aims_at_lands_in_the_centre(self):
        centre, r = pv.head_at(self.ADULT, 0)
        self.assertAlmostEqual(centre[2], 1.2 - 1.2 * 0.17)
        seen = pv.project(centre, r, {"pos": [0, -2, centre[2]], "look": centre, "lens": 50}, 16 / 9)
        self.assertAlmostEqual(seen["u"], 0.5)
        self.assertAlmostEqual(seen["v"], 0.5)
        self.assertAlmostEqual(seen["size"], 2 * r * 50 / 2 / (36 * 9 / 16))

    def test_a_centred_close_up_passes(self):
        head = pv.head_at(self.ADULT, 0)[0]
        shot = self.shot([0, -1.2, head[2]], head)
        self.assertEqual(pv.framing_problems(shot, ["arthur"], 4, "Shot [0-4s] - close-up, 50 mm", 16 / 9), [])

    def test_a_head_off_the_frame_or_behind_the_lens_fails(self):
        off = self.shot([3, -2, 1], [3, 5, 1])
        self.assertIn("out of frame", " ".join(pv.framing_problems(off, ["arthur"], 4, "Shot [0-4s] - wide", 16 / 9)))
        behind = self.shot([0, 2, 1], [0, 5, 1])
        self.assertIn("behind the camera", " ".join(pv.framing_problems(behind, ["arthur"], 4, "wide", 16 / 9)))

    def test_a_tiny_head_in_a_close_up_fails_but_passes_in_a_wide(self):
        head = pv.head_at(self.ADULT, 0)[0]
        far = self.shot([0, -9, head[2]], head, lens=24)  # a 5% head
        self.assertIn("too small", " ".join(pv.framing_problems(far, ["arthur"], 4, "Shot [0-4s] - close-up", 16 / 9)))
        self.assertEqual(pv.framing_problems(far, ["arthur"], 4, "Shot [0-4s] - wide", 16 / 9), [])

    def test_a_close_up_framed_on_the_belly_cuts_the_face(self):
        baby = {"id": "baby", "height": 0.52, "keys": [{"t": 0, "pos": [0, 0], "facing": 180}]}
        shot = self.shot([0, -0.6, 0.2], [0, 0, 0.2], lens=35, actor=baby)
        problems = " ".join(pv.framing_problems(shot, ["baby"], 4, "Shot [0-4s] - close-up", 16 / 9))
        self.assertRegex(problems, "cut by the frame edge|out of frame")

    def test_actors_outside_the_cast_are_not_judged(self):
        off = self.shot([3, -2, 1], [3, 5, 1])
        self.assertEqual(pv.framing_problems(off, ["someone_else"], 4, "wide", 16 / 9), [])

    def test_the_blender_script_builds_the_figure_these_numbers_describe(self):
        tree = ast.parse((Path(pv.__file__).parent / "blender" / "previs_scene.py").read_text(encoding="utf-8"))
        found = {t.id: ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                 for t in node.targets if isinstance(t, ast.Name) and t.id in ("HEAD_RATIO", "POSES")}
        self.assertEqual(found["HEAD_RATIO"], pv.HEAD_RATIO)
        body = {name: (p.get("squash", 1), p.get("lift", 0), p.get("tilt", 0)) for name, p in found["POSES"].items()}
        self.assertEqual({k: v for k, v in body.items() if v != (1, 0, 0)}, pv.POSE_BODY)
        self.assertEqual(set(found["POSES"]), pv.POSES)


if __name__ == "__main__":
    unittest.main()
