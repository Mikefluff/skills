"""cut_joins: jumps in place or time with nothing to carry them, bridges played in part, jump cuts."""

from __future__ import annotations

from common.runners import cut_joins as cj
from common.runners import shot_matrix


def _shot(label, at, location, phrase="medium, eye level, 35 mm, slow push-in", **extra):
    return {"label": label, "clock_at": at, "location": location, "scene": extra.pop("scene", 1),
            "body": f"Shot [0-4s] - {phrase}. Action by day.", **extra}


def _bridge(label, at, render=4.0, start=0.3, window=1.6):
    return {"label": label, "clock_at": at, "bridge": {"from": "a", "to": "b"}, "trim_start": start,
            "trim_seconds": window, "kwargs": {"duration_seconds": render}, "body": "Start exactly on the image."}


def test_a_new_place_on_a_plain_cut_is_reported():
    plan = {"shots": [_shot("a", 0, "court"), _shot("b", 4, "kitchen", scene=2)]}
    assert any("a → b: court → kitchen" in p for p in cj.join_problems(plan, {}))


def test_a_new_scene_in_the_same_room_is_no_jump():
    plan = {"shots": [_shot("a", 0, "kitchen"), _shot("b", 4, "kitchen", scene=2, cast=["x"])]}
    assert cj.join_problems(plan, {}) == []


def test_a_bridge_a_dip_or_a_moving_wide_carries_the_jump():
    moving_wide = "wide, high angle, 20 mm, a drone sweeps over the roof"
    plans = [
        ({"shots": [_shot("a", 0, "court"), _bridge("br", 4, window=3.6), _shot("b", 8, "kitchen")]}, {}),
        ({"shots": [_shot("a", 0, "court"), _shot("b", 4, "kitchen")]}, {"b": "dip"}),
        ({"shots": [_shot("a", 0, "court"), _shot("b", 4, "kitchen", moving_wide)]}, {}),
    ]
    for plan, into in plans:
        assert not [p for p in cj.join_problems(plan, into) if "→" in p.split(":")[0]]


def test_a_bridge_played_from_its_middle_is_reported_and_its_speed_plays_it_whole():
    bridge = _bridge("br", 0)
    assert cj.join_problems({"shots": [bridge]}, {})
    speed = shot_matrix.speed(bridge, {"shots": [bridge]})
    assert speed > 2 and cj.join_problems({"shots": [bridge]}, {}, {"br": speed}) == []
    assert shot_matrix.speed({**bridge, "speed": 1.2}, {"shots": [bridge]}) == 1.2


def test_a_jump_in_time_of_day_wants_a_joiner():
    night = {**_shot("a", 0, "lawn"), "body": "Shot [0-4s] - wide, eye level, 24 mm, static. Stars at night."}
    plan = {"shots": [night, _shot("b", 4, "lawn")]}
    assert any("night → day" in p for p in cj.join_problems(plan, {}))
    assert not any("night → day" in p for p in cj.join_problems(plan, {"b": "dip"}))


def test_the_same_people_at_the_same_size_unmoving_is_a_jump_cut():
    plan = {"shots": [_shot("a", 0, "pit", cast=["x"]), _shot("b", 4, "pit", cast=["x"])]}
    assert any("jump cut" in p for p in cj.join_problems(plan, {}))
    plan["shots"][1]["cast"] = ["y"]
    assert cj.join_problems(plan, {}) == []
