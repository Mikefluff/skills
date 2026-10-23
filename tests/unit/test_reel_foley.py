"""reel_foley: windows of whole shots broken at scenes, laid as file sources replacing earlier foley."""

from __future__ import annotations

from pathlib import Path

from common.runners.cli import reel_foley as rf


def _shot(label, at, seconds, scene, **extra):
    return {"label": label, "clock_at": at, "trim_seconds": seconds, "scene": scene, **extra}


def test_windows_break_at_scenes_and_at_the_limit():
    plan = {"shots": [_shot("a", 0, 10, 1), _shot("b", 10, 10, 1), _shot("c", 20, 15, 1), _shot("d", 35, 5, 2),
                      _shot("br", 40, 2, None, bridge={"from": "d", "to": "e"}), _shot("e", 42, 4, 3)]}
    got = [[s["label"] for s in w] for w in rf.windows(plan, limit=30)]
    assert got == [["a", "b"], ["c"], ["d", "br"], ["e"]]


def test_lay_replaces_earlier_foley():
    plan = {"sound": {"sources": [{"id": "foley_000", "kind": "file"}, {"id": "boing"}],
                      "placements": [{"source": "foley_000", "at": 0}, {"source": "boing", "at": 1}]}}
    rf.lay(plan, [(Path("/x/a.wav"), 2.0, 9.0)], -10)
    assert [s["id"] for s in plan["sound"]["sources"]] == ["boing", "foley_000"]
    assert plan["sound"]["placements"][-1] == {"source": "foley_000", "at": 2.0, "length": 7.0, "gain_db": -10,
                                               "duck": False, "fade_in": 0.08, "fade_out": 0.08}
