"""reel_spot: a shot's cues replace its one-shot effects; beds, music and vocals stay; new prompts become sources."""

from __future__ import annotations

from common.runners.cli import reel_spot as rs


def _plan():
    return {"shots": [{"label": "a", "clock_at": 10.0, "trim_seconds": 4}, {"label": "b", "clock_at": 14.0, "trim_seconds": 4}],
            "sound": {"sources": [{"id": "boing"}, {"id": "kitchen_bed", "loop": True}],
                      "placements": [{"source": "boing", "at": 11.0}, {"source": "kitchen_bed", "at": 0, "length": 60},
                                     {"source": "vocal_3", "at": 12.0}, {"source": "boing", "at": 15.0}]}}


def test_cues_replace_only_the_named_shot_s_one_shots():
    plan = _plan()
    cues = [{"label": "a", "at": 0.5, "layer": "accent", "source": "boing", "gain_db": -3},
            {"label": "a", "at": 2.0, "layer": "foley", "source": None, "prompt": "felt slippers on wood", "duration": 1}]
    out = rs.spot(plan, cues)
    ats = sorted((p["source"], p["at"]) for p in plan["sound"]["placements"])
    assert ("boing", 11.0) not in ats and ("boing", 10.5) in ats and ("boing", 15.0) in ats
    assert ("kitchen_bed", 0) in ats and ("vocal_3", 12.0) in ats
    assert out["new_sources"] == 1 and out["credits"] == 40
    assert any(s["id"] == rs.source_id("felt slippers on wood") for s in plan["sound"]["sources"])
