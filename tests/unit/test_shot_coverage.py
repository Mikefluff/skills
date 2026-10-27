"""shot_coverage: wides per scene, close-up runs, static runs and the share of real moves."""

from __future__ import annotations

import io

from common.runners import shot_coverage as sc


def _shot(label, scene, phrase, at, **extra):
    return {"label": label, "scene": scene, "clock_at": at, "body": f"Shot [0-4s] - {phrase}. Action.", **extra}


def _plan(*shots):
    return {"shots": list(shots)}


def test_reads_size_and_move_from_the_shot_phrase():
    read = sc.read_shot(_shot("a", 1, "medium close, eye level, 50 mm, slow push-in", 0))
    assert (read["size"], read["moves"]) == ("close", False)
    read = sc.read_shot(_shot("b", 1, "wide, high angle, 24 mm, an orbit at 12 m radius sweeping an arc", 0))
    assert (read["size"], read["moves"]) == ("wide", True)
    assert sc.read_shot(_shot("c", 1, "medium wide, low angle, 24 mm, tracking left to right", 0))["size"] == "medium"
    assert sc.read_shot(_shot("d", 1, "medium, eye level, 35 mm, dolly in", 0))["moves"] is False
    assert sc.read_shot(_shot("e", 1, "wide, eye level, 24 mm, slow pan left to right", 0))["moves"] is False


def test_prose_body_reads_its_camera_sentences():
    read = sc.read_shot({"label": "p", "scene": 2, "body": "Start exactly on the image. A drone pulls back over the lawn."})
    assert (read["size"], read["moves"]) == ("wide", True)
    read = sc.read_shot({"label": "q", "scene": 2, "body": "Start exactly on the image. She flies across the room."})
    assert (read["size"], read["moves"]) == (None, False)


def test_clips_and_cut_shots_are_skipped_and_bridges_move():
    assert sc.read_shot({"label": "c", "scene": 1, "body": "", "clip": "x.mp4"}) is None
    assert sc.read_shot(_shot("x", 1, "wide, 24 mm, crane up", 0, cut=True)) is None
    bridge = sc.read_shot({"label": "b", "bridge": {"from": "a", "to": "b"}, "body": "Start on the first image."})
    assert bridge == {"label": "b", "scene": None, "size": None, "moves": True}


def test_good_coverage_has_no_problems():
    plan = _plan(_shot("a", 1, "wide, high, 20 mm, drone descends", 0),
                 _shot("b", 1, "close-up, eye level, 50 mm, slow push-in", 4),
                 _shot("c", 1, "medium, eye level, 35 mm, slow dolly right", 8),
                 _shot("d", 2, "aerial, top-down, 14 mm, crane down", 12),
                 _shot("e", 2, "close-up, 50 mm, locked-off", 16))
    assert sc.coverage_problems(plan) == []


def test_reports_scene_without_wide_close_run_static_run_and_share():
    plan = _plan(_shot("a", 1, "wide, 20 mm, crane up", 0),
                 _shot("b", 2, "close-up, 50 mm, slow push-in", 3),
                 _shot("c", 2, "medium close-up, 50 mm, locked-off", 1),  # clock order puts it before b
                 _shot("d", 2, "insert, 85 mm, static", 4),
                 {"label": "k", "scene": 2, "body": "", "clip": "k.mp4", "clock_at": 5},
                 _shot("e", 2, "medium, 35 mm, slow tilt up", 6))
    problems = sc.coverage_problems(plan)
    assert "scene 2: no wide, aerial or overhead shot (c..e)" in problems
    assert "3 close-ups in a row: c..d" in problems
    assert "4 shots without a real camera move in a row: c..e" in problems
    assert any(p.startswith("real camera moves in 1 of 5 shots") for p in problems)


def test_warn_prints_and_returns():
    out = io.StringIO()
    plan = _plan(_shot("a", 1, "close-up, 50 mm, slow push-in", 0))
    assert sc.warn(plan, out) == sc.coverage_problems(plan)
    assert "coverage: scene 1" in out.getvalue()
    assert sc.warn({"shots": []}, io.StringIO()) == []


def test_an_open_on_frame_shot_takes_its_size_from_the_storyboard_frame():
    from common.runners import shot_coverage as sc
    shot = {"label": "w", "scene": 3, "index": 4, "open_on_frame": True,
            "body": "Start exactly on the image. The camera cranes up over the family."}
    plan = {"shots": [shot], "board": {"frames": [{"shot": 4, "shot_spec": "Wide, high corner, 20 mm: everyone"}]}}
    read = sc._in_order(plan)[0]
    assert read["size"] == "wide" and read["moves"]
