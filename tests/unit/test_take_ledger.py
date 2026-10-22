"""take_ledger: every take enriched, statuses from the plan and the manifest, a new take landing in the cut."""

from __future__ import annotations

import json
import types

from common.runners import shot_matrix as sm
from common.runners import take_ledger as tl

BODY = "Shot [0-4s] - wide, eye level, 24 mm, slow crane up over the lawn. The family laughs."


def _project(tmp_path, ledger, items, shots):
    (tmp_path / "shots").mkdir()
    for take in ledger:
        (tmp_path / take["file"]).write_bytes(b"")
    (tmp_path / "takes.json").write_text(json.dumps(ledger), encoding="utf-8")
    (tmp_path / "manifest.json").write_text(json.dumps({"items": items}), encoding="utf-8")
    return {"output_dir": str(tmp_path), "shots": shots}


def _take(label, stamp, **extra):
    return {"label": label, "file": f"shots/20261019-{stamp}-{label}.mp4", "route": "r", "how": "",
            "cost_usd": 0.5, "duration": 4.0, **extra}


def test_created_reads_the_file_name():
    assert tl.created("shots/20261019-133222-t30.mp4") == "2026-10-19 13:32:22"
    assert tl.created("shots/fin2-lettered.mp4") is None


def test_camera_reads_size_and_move():
    assert tl.camera(BODY) == {"size": "wide", "move": "slow crane up over the lawn", "moves": True}


def test_backfill_statuses_prompts_and_usable(tmp_path):
    old, cur, hand = _take("a", "100000"), _take("a", "110000"), _take("b", "120000", verdict="rejected")
    items = [{"label": "a", "status": "succeeded", "output_path": f"{tmp_path}/{cur['file']}", "prompt": BODY}]
    plan = _project(tmp_path, [old, cur, hand], items,
                    [{"label": "a", "body": "Shot [0-4s] - close, 85 mm, push-in."},
                     {"label": "c", "clip": "shots/fin2-lettered.mp4"}])
    (tmp_path / "shots" / "fin2-lettered.mp4").write_bytes(b"")
    ledger = {t["file"]: t for t in tl.backfill(plan, json.loads((tmp_path / "takes.json").read_text()))}
    assert ledger[cur["file"]]["status"] == "in cut" and ledger[cur["file"]]["prompt_source"] == "manifest"
    assert ledger[old["file"]]["status"] == "alternate"
    assert ledger[old["file"]]["prompt_source"] == "body: current plan, may differ"
    assert ledger[old["file"]]["size"] == "close"
    assert ledger[hand["file"]]["status"] == "rejected"
    assert ledger["shots/fin2-lettered.mp4"]["status"] == "in cut" and ledger["shots/fin2-lettered.mp4"]["untracked"]
    assert ledger[cur["file"]]["usable"] == [[0.2, 4.0]]


def test_history_body_takes_the_first_plan_saved_after_the_take():
    take = _take("a", "100000")
    late = ("late.json", {"shots": [{"label": "a", "body": "late"}]}, 2e9)
    early = ("early.json", {"shots": [{"label": "a", "body": "too early"}]}, 1.0)
    first = ("first.json", {"shots": [{"label": "a", "body": "first"}]}, 1.9e9)
    assert tl.history_body(take, [late, early, first]) == ("first", "first.json body, may differ")


def test_hand_fields_survive_and_rejected_sets_the_verdict():
    take = _take("a", "100000")
    tl.set_fields(take, ["status=rejected", 'reason="cake upside down"'])
    assert (take["status"], take["verdict"], take["reason"]) == ("rejected", "rejected", "cake upside down")
    tl.set_fields(take, ["status=alternate"])
    assert "verdict" not in take
    assert tl.windows("1.0-3.4, 5-6") == [[1.0, 3.4], [5.0, 6.0]]


def test_record_takes_lands_a_new_take_and_demotes_the_old(tmp_path):
    plan = _project(tmp_path, [_take("a", "100000", status="in cut"), _take("a", "090000", status="rejected")],
                    [], [])
    new = tmp_path / "shots" / "20261022-100000-a.mp4"
    new.write_bytes(b"")
    item = types.SimpleNamespace(status="succeeded", output_path=str(new), label="a", kwargs={}, prompt=BODY)
    sm.record_takes(plan, [item], lambda _: 1.0)
    ledger = json.loads((tmp_path / "takes.json").read_text())
    assert [t["status"] for t in ledger] == ["alternate", "rejected", "in cut"]
    assert ledger[0]["reason"] == "superseded by 20261022-100000-a.mp4"
    assert (ledger[2]["size"], ledger[2]["moves"], ledger[2]["created"]) == ("wide", True, "2026-10-22 10:00:00")


def test_insert_entry_anchors_on_the_shot_that_replaced_it():
    take = _take("t30", "133222", usable=[[1.0, 3.4]])
    entry = tl.insert_entry(take, ["t29", "t30r"])
    assert entry == {"insert_after": "t30r", "shot": {"label": "t30_1332", "clip": take["file"],
                                                      "trim_start": 1.0, "trim_seconds": 2.4}}
