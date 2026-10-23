"""score_fit: a score's sections sized to the acts they play under, or scaled to the placement."""

from __future__ import annotations

from common.runners import score_fit as sf


def _plan(**clock):
    return {"shots": [{"label": k, "clock_at": v, "trim_seconds": 2} for k, v in clock.items()],
            "trailer": {"acts": [{"name": "setup", "from": "a", "to": "b"}, {"name": "chaos", "from": "c", "to": "d"}]}}


def _sound(sections, at=0.0, length=200.0, offset=1.0):
    return {"sources": [{"id": "score", "kind": "music", "composition_plan": {"sections": sections}}],
            "placements": [{"source": "score", "at": at, "length": length, "offset": offset}]}


def test_sections_named_after_acts_end_where_the_next_act_begins():
    sound = _sound([{"section_name": "setup", "duration_ms": 90000}, {"section_name": "chaos", "duration_ms": 90000}])
    sf.follow_cut(sound, _plan(a=0, b=50, c=120, d=180))
    got = [s["duration_ms"] for s in sound["sources"][0]["composition_plan"]["sections"]]
    assert got == [121000, 80000]  # from the take's start (at - offset) to c, then to the placement's end


def test_sections_that_are_not_acts_scale_to_the_placement():
    sound = _sound([{"section_name": "verse", "duration_ms": 10000}, {"section_name": "chorus", "duration_ms": 30000}],
                   length=79.0)
    sf.follow_cut(sound, _plan(a=0, b=50, c=120, d=180))
    assert [s["duration_ms"] for s in sound["sources"][0]["composition_plan"]["sections"]] == [20000, 60000]
