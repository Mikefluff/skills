"""Previs spec: camera moves expand into keys, and a spec that cannot render says why."""

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


if __name__ == "__main__":
    unittest.main()
