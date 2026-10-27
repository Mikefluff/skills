"""place_beds: beds relaid on the cut's place runs, chosen by location, leading their picture."""

from __future__ import annotations

from common.runners import place_beds as pb


def _shot(label, at, seconds, location):
    return {"label": label, "clock_at": at, "trim_seconds": seconds, "location": location}


def _sound(*placements):
    return {"sources": [{"id": "court", "loop": True}, {"id": "kitchen", "loop": True}, {"id": "hit"}],
            "placements": list(placements)}


def test_beds_follow_a_cut_that_moved_under_them():
    plan = {"shots": [_shot("a", 0, 10, "court_day"), _shot("b", 10, 20, "kitchen_day")]}
    # written for a cut where the court ran to 14 s: the kitchen bed came in 4 s late
    sound = _sound({"source": "court", "at": 0, "length": 14, "gain_db": -22},
                   {"source": "kitchen", "at": 14, "length": 16, "gain_db": -20},
                   {"source": "hit", "at": 3})
    laid = pb.follow_cut(sound, plan)["placements"]
    kitchen = next(p for p in laid if p["source"] == "kitchen")
    assert kitchen["at"] == 10 - pb.PRELAP and kitchen["level"] == pb.BED_LUFS
    assert next(p for p in laid if p["source"] == "court")["at"] == 0
    assert {"source": "hit", "at": 3} in laid


def test_a_short_run_takes_its_location_s_bed_not_the_one_slid_over_it():
    plan = {"shots": [_shot("a", 0, 20, "court_day"), _shot("b", 20, 20, "kitchen_day"),
                      _shot("c", 40, 3, "court_day")]}
    sound = _sound({"source": "court", "at": 0, "length": 20, "gain_db": -22},
                   {"source": "kitchen", "at": 20, "length": 23, "gain_db": -22})
    laid = sorted(pb.follow_cut(sound, plan)["placements"], key=lambda p: p["at"])
    assert [p["source"] for p in laid] == ["court", "kitchen", "court"]


def test_a_burst_of_a_bed_without_a_length_stays_where_it_is():
    plan = {"shots": [_shot("a", 0, 10, "court_day")]}
    burst = {"source": "court", "at": 4.0, "gain_db": -16}
    sound = _sound({"source": "court", "at": 0, "length": 10, "gain_db": -22}, burst)
    assert burst in pb.follow_cut(sound, plan)["placements"]


def test_a_run_longer_than_the_bed_is_laid_as_overlapping_takes():
    plan = {"shots": [_shot("a", 0, 70, "court_day")]}
    sound = _sound({"source": "court", "at": 0, "length": 70, "gain_db": -22})
    sound["sources"][0]["duration_seconds"] = 30
    takes = sorted((p for p in pb.follow_cut(sound, plan)["placements"]), key=lambda p: p["at"])
    assert all(p["length"] <= 30 for p in takes)
    ends = [p["at"] + p["length"] for p in takes]
    assert all(nxt["at"] < end for end, nxt in zip(ends, takes[1:]))  # no gap between takes
    assert ends[-1] >= 70
