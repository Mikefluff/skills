"""Cut transitions: each kind gives both halves of the cut, and a film's own choice beats the defaults."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import cut_transitions as ct  # noqa: E402
from common.runners import shot_matrix  # noqa: E402


class Halves(unittest.TestCase):
    def test_a_dip_fades_the_tail_out_and_the_head_up_from_black(self):
        self.assertIn("fade=t=out:st=2.650", ct.out("dip", 3.0, 640, 360))
        self.assertIn("fade=t=in:st=0", ct.into("dip", 640, 360))

    def test_an_iris_closes_on_the_tail_and_opens_on_the_head(self):
        tail, head = ct.out("iris", 3.0, 640, 360), ct.into("iris", 640, 360)
        self.assertIn("geq=", tail)
        self.assertIn("2.500", tail, "the circle starts closing half a second before the cut")
        self.assertIn("min(T/0.5", head)

    def test_every_listed_transition_has_a_name(self):
        for kind in ("dip", "iris"):
            self.assertIn(kind, shot_matrix.TRANSITIONS)


class FilmsChoice(unittest.TestCase):
    def test_a_shot_that_names_its_transition_gets_it(self):
        plan = {"shots": [{"label": "a", "clock_at": 0, "body": ""},
                          {"label": "b", "clock_at": 3, "body": "", "into": "iris"}]}
        self.assertEqual(shot_matrix.transitions(plan)["b"], "iris")


if __name__ == "__main__":
    unittest.main()
