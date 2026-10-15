"""A film's soundtrack is placements on the film clock, and hits land on the picture.

Two things here go wrong silently. A placement that names the wrong source or a
made-up treatment would reach ffmpeg as a string and fail there, or worse, run;
so the spec is validated and `fx` is a closed set. And a sound effect timed to
the prompt instead of to the frame plays before or after its flash — audible as
cheapness without anyone being able to say why — so snapping is pinned too.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import soundtrack as st  # noqa: E402

SOURCES = [{"id": "show", "kind": "music"}, {"id": "hit", "kind": "sfx", "prompt": "boom"}]


class Validate(unittest.TestCase):
    def test_unknown_source_is_rejected(self):
        with self.assertRaises(ValueError):
            st.validate({"sources": SOURCES, "placements": [{"source": "nope", "at": 1}]})

    def test_unknown_fx_is_rejected(self):
        with self.assertRaises(ValueError):
            st.validate({"sources": SOURCES, "placements": [{"source": "hit", "at": 1, "fx": "reverb;rm -rf"}]})

    def test_one_source_can_be_placed_twice(self):
        out = st.validate({"sources": SOURCES, "placements": [
            {"source": "show", "at": 3.0, "length": 7.1},
            {"source": "show", "at": 12.0, "offset": 9.0, "fx": "distant"},
        ]})
        self.assertEqual([p.offset for p in out], [0.0, 9.0])


class Graph(unittest.TestCase):
    def graph(self, placements):
        paths = {"show": Path("/s/show.mp3"), "hit": Path("/s/hit.mp3")}
        return st.build_graph(st.validate({"sources": SOURCES, "placements": placements}),
                              paths, Path("/s/voice.wav"), 28.47)

    def test_voice_is_input_zero_and_the_duck_key(self):
        inputs, graph = self.graph([{"source": "show", "at": 2.98, "duck": True}])
        self.assertEqual(inputs[:2], ["-i", "/s/voice.wav"])
        self.assertIn("[bed][key]sidechaincompress", graph)

    def test_placement_is_trimmed_treated_and_delayed(self):
        _, graph = self.graph([{"source": "show", "at": 11.95, "offset": 9.5, "length": 13.3,
                                "fx": "distant", "gain_db": -12, "duck": True}])
        self.assertIn("atrim=start=9.500:end=22.800", graph)
        self.assertIn(st.FX["distant"], graph)
        self.assertIn("volume=-12.0dB", graph)
        self.assertIn("adelay=11950:all=1", graph)

    def test_effects_are_not_ducked(self):
        _, graph = self.graph([{"source": "hit", "at": 5.44}])
        self.assertNotIn("sidechaincompress", graph)
        self.assertIn("[key]anullsink", graph)

    def test_master_is_cut_to_the_film_and_normalised(self):
        _, graph = self.graph([{"source": "hit", "at": 5.44}])
        self.assertIn("atrim=end=28.470,apad=whole_dur=28.470", graph)
        self.assertIn("loudnorm=I=-14.0:TP=-1.0", graph)


class Snap(unittest.TestCase):
    HITS = [(5.0, 2.0), (5.71, 40.0), (6.3, 90.0), (8.0, 120.0)]

    def test_moves_to_the_strongest_flash_in_the_window(self):
        self.assertEqual(st.snap_time(5.44, self.HITS), 5.71)

    def test_stays_put_when_nothing_flashes_nearby(self):
        self.assertEqual(st.snap_time(3.0, self.HITS), 3.0)

    def test_brightness_jumps_are_frame_to_frame(self):
        jumps = st.brightness_jumps([(0.0, 10.0), (0.04, 10.5), (0.08, 80.0)])
        self.assertEqual(jumps, [(0.04, 0.5), (0.08, 69.5)])


if __name__ == "__main__":
    unittest.main()
