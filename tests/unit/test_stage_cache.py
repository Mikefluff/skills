"""What the film pipeline keeps between runs: a rerun that changed nothing redoes nothing, and a change redoes
only what it touches — previs clips, board jpgs and contact sheet, cast's plan and bridge frames, preflight
notes, hd copies, vocals per voice, temporary-host URLs, and kept takes rendered from an older prompt."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from common.runners import batch as batch_mod
from common.runners.cli import _cast_scenes, _drama_pass, _reel_spend, _stage_cache as sc
from common.runners.cli import reel_board, reel_previs, reel_upscale
from common.runners.providers import openrouter_video


def _touch(path: Path, data: bytes = b"x", mtime: float | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


# ── the helper ──────────────────────────────────────────────────────────────


def test_save_json_leaves_an_unchanged_file_alone(tmp_path):
    plan = tmp_path / "plan.json"
    assert sc.save_json(plan, {"a": 1})
    os.utime(plan, (1, 1))
    assert not sc.save_json(plan, {"a": 1})
    assert plan.stat().st_mtime == 1
    assert sc.save_json(plan, {"a": 2})


def test_stamps_need_the_file_and_the_same_key(tmp_path):
    stamps, out = sc.Stamps(tmp_path / "cache.json"), tmp_path / "out.jpg"
    stamps.set("out.jpg", "k1")
    assert not stamps.fresh("out.jpg", "k1", out)  # no file
    _touch(out)
    assert stamps.fresh("out.jpg", "k1", out) and not stamps.fresh("out.jpg", "k2", out)
    stamps.save()
    assert sc.Stamps(tmp_path / "cache.json").fresh("out.jpg", "k1", out)


# ── previs ──────────────────────────────────────────────────────────────────


def _previs_spec(tmp_path: Path) -> dict:
    shot = lambda label, lens: {"label": label, "seconds": 5.0, "frames": str(tmp_path / f"{label}-frames"),  # noqa: E731
                                "props": [], "camera": [], "lens": lens, "shake": 0, "hero": [], "actors": [],
                                "fire": [], "extra": []}
    return {"size": (480, 854), "fps": 24, "shots": [shot("t01", 24), shot("t02", 35)]}


def test_previs_sends_blender_only_the_shots_whose_spec_changed(tmp_path, capsys):
    spec, stamps = _previs_spec(tmp_path), sc.Stamps(tmp_path / "cache.json")
    for shot in spec["shots"]:
        _touch(tmp_path / f"{shot['label']}.mp4")
        stamps.set(shot["label"], reel_previs._shot_key(shot, spec))
    with mock.patch.object(reel_previs.subprocess, "run") as run:
        reel_previs._blender(spec, tmp_path, stamps)
    run.assert_not_called()  # nothing changed: Blender is not even started
    assert "2 clip(s) unchanged" in capsys.readouterr().err

    spec["shots"][1]["lens"] = 50
    seen = []
    done = SimpleNamespace(returncode=0, stdout="", stderr="")
    with mock.patch.object(reel_previs.subprocess, "run", return_value=done), \
            mock.patch.object(reel_previs, "_encode"), mock.patch.object(reel_previs, "blender_binary", return_value="b"):
        reel_previs._blender(spec, tmp_path, stamps)
        seen = json.loads((tmp_path / "job.json").read_text())["shots"]
    assert [s["label"] for s in seen] == ["t02"]
    assert stamps.fresh("t02", reel_previs._shot_key(spec["shots"][1], spec), tmp_path / "t02.mp4")


def test_previs_key_ignores_where_the_frames_go(tmp_path):
    spec = _previs_spec(tmp_path)
    moved = {**spec["shots"][0], "frames": "/elsewhere"}
    assert reel_previs._shot_key(moved, spec) == reel_previs._shot_key(spec["shots"][0], spec)


def test_previs_contact_and_cut_are_made_again_only_when_a_trim_or_clip_moved(tmp_path):
    clip = _touch(tmp_path / "t01.mp4")
    plan = {"shots": [{"index": 1, "label": "t01", "trim_seconds": 4}], "previs": {"shots": {"t01": {}}}}
    stamps = sc.Stamps(tmp_path / "cache.json")

    def make(*_a, **_k):
        _touch(tmp_path / "contact.jpg"), _touch(tmp_path / "animatic.mp4")
        return True

    with mock.patch.object(reel_previs, "_contact", side_effect=make) as contact, \
            mock.patch.object(reel_previs, "_animatic", side_effect=make) as cut:
        reel_previs._derived(plan, tmp_path, [(clip, 120)], stamps)
        reel_previs._derived(plan, tmp_path, [(clip, 120)], stamps)
        assert (contact.call_count, cut.call_count) == (1, 1)
        plan["shots"][0]["trim_seconds"] = 3
        reel_previs._derived(plan, tmp_path, [(clip, 120)], stamps)
        assert (contact.call_count, cut.call_count) == (1, 2)


# ── board ───────────────────────────────────────────────────────────────────


def test_board_jpg_is_encoded_again_only_after_its_png_is_redrawn(tmp_path):
    png = _touch(tmp_path / "f01.png", mtime=100)
    _touch(tmp_path / "f01.jpg", mtime=200)
    with mock.patch.object(reel_board.subprocess, "run") as run:
        reel_board._jpeg(png)
        run.assert_not_called()
        os.utime(png, (300, 300))
        reel_board._jpeg(png)
        run.assert_called_once()


def test_board_contact_sheet_is_kept_while_its_frames_are(tmp_path, capsys):
    jpgs = [_touch(tmp_path / "f01.jpg"), _touch(tmp_path / "f02.jpg")]

    def sheet(frames, out, wide=False):
        _touch(out)

    with mock.patch.object(reel_board, "_contact", side_effect=sheet) as contact:
        reel_board._sheet(jpgs, tmp_path, wide=False)
        reel_board._sheet(jpgs, tmp_path, wide=False)
        assert contact.call_count == 1
        assert "contact sheet unchanged" in capsys.readouterr().err
        reel_board._sheet(list(reversed(jpgs)), tmp_path, wide=False)  # the order is part of the sheet
        assert contact.call_count == 2


# ── cast ────────────────────────────────────────────────────────────────────


def test_bridge_frames_are_grabbed_again_only_when_their_clip_or_second_moved(tmp_path):
    clip_a, clip_b = _touch(tmp_path / "a.mp4"), _touch(tmp_path / "b.mp4")
    plan = {"output_dir": str(tmp_path), "shots": [
        {"label": "t01", "trim_seconds": 3.0}, {"label": "t02", "trim_seconds": 2.0},
        {"label": "b01", "body": "fly", "bridge": {"from": "t01", "to": "t02"}}]}
    scene, clips = plan["shots"][2], {"t01": clip_a, "t02": clip_b}

    def grab(clip, at, frame):
        _touch(frame)

    with mock.patch.object(_cast_scenes, "_grab_frame", side_effect=grab) as grabbed:
        _cast_scenes._bridge_scene(plan, scene, clips, {})
        _cast_scenes._bridge_scene(plan, scene, clips, {})
        assert grabbed.call_count == 2  # first and last frame, once
        plan["shots"][0]["trim_seconds"] = 2.5
        _cast_scenes._bridge_scene(plan, scene, clips, {})
        assert grabbed.call_count == 3  # only the end that moved
    assert scene["kwargs"]["first_frame"].endswith("b01.first.jpg")


def test_preflight_notes_print_in_full_only_when_new(tmp_path, capsys):
    plan = {"output_dir": str(tmp_path)}
    assert _cast_scenes._preflight_notes(plan, ["t01: a", "t02: b"]) == ["t01: a", "t02: b"]
    capsys.readouterr()
    assert _cast_scenes._preflight_notes(plan, ["t01: a", "t02: b", "t03: c"]) == ["t03: c"]
    err = capsys.readouterr().err
    assert "preflight t03: c" in err and "t01: a" not in err and "2 note(s) unchanged" in err


# ── upscale ─────────────────────────────────────────────────────────────────


def test_upscale_redoes_a_copy_older_than_its_clip(tmp_path):
    clip = _touch(tmp_path / "shots" / "t01.mp4", mtime=100)
    _touch(tmp_path / "shots" / "hd" / "t01.mp4", mtime=200)
    assert reel_upscale.current(clip)
    os.utime(clip, (300, 300))  # the clip was replaced under the same name
    assert not reel_upscale.current(clip)


# ── vocals ──────────────────────────────────────────────────────────────────


def test_vocal_is_read_again_when_its_speaker_gets_a_new_voice(tmp_path):
    vocal = {"who": "tanya", "text": "Ура!"}
    old_voice, new_voice = _drama_pass.vocal_file(vocal, tmp_path, "v1"), _drama_pass.vocal_file(vocal, tmp_path, "v2")
    assert old_voice != new_voice
    _touch(old_voice)
    read = SimpleNamespace(content=b"new")
    with mock.patch.object(_drama_pass, "_clean_vocal", return_value=read) as tts:
        assert _drama_pass.voice([vocal], {"tanya": "v1"}, tmp_path) == {0: old_voice}
        tts.assert_not_called()
        assert _drama_pass.voice([vocal], {"tanya": "v2"}, tmp_path) == {0: new_voice}
        tts.assert_called_once()


def test_a_vocal_kept_under_the_older_name_is_adopted_not_bought(tmp_path):
    vocal = {"who": "tanya", "text": "Ура!"}
    legacy = _touch(_drama_pass.vocal_file(vocal, tmp_path), b"take")
    with mock.patch.object(_drama_pass, "_clean_vocal") as tts:
        files = _drama_pass.voice([vocal], {"tanya": "v1"}, tmp_path)
    tts.assert_not_called()
    assert files[0] == _drama_pass.vocal_file(vocal, tmp_path, "v1") and files[0].read_bytes() == b"take"
    assert not legacy.exists()


# ── temporary host ──────────────────────────────────────────────────────────


def test_a_file_goes_up_once_while_its_url_lives(tmp_path, monkeypatch):
    sample = _touch(tmp_path / "voice.mp3")
    monkeypatch.setattr(openrouter_video, "_HOSTED", {})
    put = mock.Mock(side_effect=["https://h/1", "https://h/2"])
    assert openrouter_video._hosted(sample, "litterbox", put) == "https://h/1"
    assert openrouter_video._hosted(sample, "litterbox", put) == "https://h/1"
    assert put.call_count == 1
    _touch(sample, b"changed", mtime=5)
    assert openrouter_video._hosted(sample, "litterbox", put) == "https://h/2"


# ── reel: kept takes rendered from an older prompt ──────────────────────────


def test_reel_names_kept_takes_whose_shot_was_edited_since(tmp_path):
    manifest = tmp_path / "manifest.json"
    a = batch_mod.BatchItem(index=1, label="t01", prompt="old", kwargs={}, status="succeeded", output_path="a.mp4")
    b = batch_mod.BatchItem(index=2, label="t02", prompt="same", kwargs={}, status="succeeded", output_path="b.mp4")
    legacy = batch_mod.BatchItem(index=3, label="t03", prompt="x", kwargs={}, status="succeeded", output_path="c.mp4")
    a.spec_hash, b.spec_hash = batch_mod.spec_hash(a), batch_mod.spec_hash(b)
    batch_mod.write_manifest(manifest, [a, b, legacy])
    now = [batch_mod.BatchItem(index=1, label="t01", prompt="new"),
           batch_mod.BatchItem(index=2, label="t02", prompt="same", kwargs={"media_host": "uguu"}),
           batch_mod.BatchItem(index=3, label="t03", prompt="y")]
    assert batch_mod.changed_since_output(now, manifest) == ["t01"]  # a host is not the shot; no hash, no claim
    job = SimpleNamespace(shot_items=now, manifest_path=manifest)
    warning = _reel_spend._changed(job, [])
    assert warning and "t01" in warning[0] and "t02" not in warning[0]
    assert _reel_spend._changed(job, [("t01", None, "asked")]) == []  # being rendered again: nothing to say


def test_resume_carries_the_hash_of_what_the_take_was_made_from(tmp_path):
    manifest = tmp_path / "manifest.json"
    done = batch_mod.BatchItem(index=1, label="t01", prompt="p", status="succeeded", output_path="a.mp4",
                               spec_hash="abc")
    batch_mod.write_manifest(manifest, [done])
    item = batch_mod.BatchItem(index=1, label="t01", prompt="edited")
    batch_mod._restore_succeeded([item], manifest)
    assert item.spec_hash == "abc"
