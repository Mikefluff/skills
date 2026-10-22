"""reel_listen — text normalisation, matching, the windows a plan's lines play in, and no Whisper at all.
Also the `reel` post-render hook that upscales a "hd" film's new clips (_reel_hd)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from common.runners.cli import _reel_hd, reel_listen
from common.runners.errors import RunnerError


def test_normalize_drops_tags_punctuation_and_yo():
    assert reel_listen.normalize("[stern] Больше — ни-ни! Ещё…") == "больше ни ни еще"


def test_has_words_skips_held_sounds():
    assert reel_listen.has_words("[cheering] Ура-а!")
    assert reel_listen.has_words("Ещё!")
    for sound in ("[gasps] А-а-ах!", "Хи-хи!", "Ррр!", "Тсс", "Хып!", "Мм-хм.", "[tag only]"):
        assert not reel_listen.has_words(sound), sound


def test_similarity_exact_misheard_and_neighbour_tail():
    assert reel_listen.similarity("Для Тани — всю!", "Для Тани всю.") == 1.0
    assert reel_listen.similarity("Корт", "Торт") < 0.8
    # the window also catches the next line: the best stretch is what counts
    assert reel_listen.similarity("Теннис твой на час.", "Теннис твой на час. Ровно через час домой") == 1.0
    assert reel_listen.similarity("Ещё!", "") == 0.0


def test_heard_text_drops_whisper_silence_phrases():
    assert reel_listen.heard_text("Субтитры сделал DimaTorzok") == ""
    assert reel_listen.heard_text("Продолжение следует...") == ""
    assert reel_listen.heard_text("АААААААААА") == "ААА"


def _plan():
    return {"output_dir": "out", "shots": [
        {"label": "t01", "clock_at": 10.0, "trim_seconds": 3.0, "line_at": 0.4,
         "dialogue": [{"who": "arthur", "line": "Корт на час!"}]},
        {"label": "t02", "clock_at": 13.0, "trim_seconds": 4.0, "dialogue": []},
        {"label": "t03", "clock_at": 17.0, "trim_seconds": 2.0, "cut": True,
         "dialogue": [{"who": "x", "line": "Вырезано."}]},
    ], "vocals": [
        {"shot": "t02", "who": "baby", "at": 1.0, "text": "[shouts] Ещё!"},
        {"shot": "t02", "who": "baby", "at": 2.0, "text": "[giggles] Хи-хи!"},
        {"shot": "t03", "who": "baby", "at": 0.5, "text": "Ура!"},
    ]}


def test_windows_place_lines_and_vocals_on_the_clock():
    wins = reel_listen.windows(_plan(), pad=0.3)
    assert [(w["label"], w["kind"], w["expected"]) for w in wins] == [
        ("t01", "line", "Корт на час!"), ("t02", "vocal", "еще")]
    line, vocal = wins
    assert (line["start"], line["end"]) == (10.1, 13.7)  # 10 + 0.4 - pad .. 10 + 3 + spill + pad
    assert vocal["start"] == 13.7 and vocal["end"] == 15.8  # 14 - pad .. 14 + 1.5 + pad


def test_windows_only_filters_by_shot_label():
    assert [w["label"] for w in reel_listen.windows(_plan(), {"t02"})] == ["t02"]


def test_flagged_lines_get_a_gain_and_the_path_to_set_it(tmp_path, capsys):
    plan = _plan()
    plan["vocals"][0]["gain_db"] = 10
    film = tmp_path / "film.mp4"
    film.write_bytes(b"x")
    line, vocal = reel_listen.windows(plan)
    assert line["path"] == "shots[t01].dialogue[0].gain_db" and vocal["path"] == "vocals[0].gain_db"
    heard = {reel_listen._key(film, line): "Торт на час", reel_listen._key(film, vocal): ""}
    results = reel_listen.judge(film, [line, vocal], heard, 0.95)
    assert [r["suggest_gain_db"] for r in results] == [3.0, 12.0]  # +3 misheard; +4 unheard, held to +12
    reel_listen.report(results, 0.95)
    err = capsys.readouterr().err
    assert "set shots[t01].dialogue[0].gain_db = 3" in err and "set vocals[0].gain_db = 12" in err


def test_missing_whisper_is_skipped_gracefully(monkeypatch, tmp_path, capsys):
    plan = tmp_path / "plan.json"
    plan.write_text('{"output_dir": "%s", "shots": []}' % tmp_path, encoding="utf-8")
    monkeypatch.delenv("WHISPER", raising=False)
    monkeypatch.setattr(reel_listen.shutil, "which", lambda _: None)
    monkeypatch.setattr(reel_listen, "_FALLBACK", tmp_path / "nope")
    monkeypatch.setattr(sys, "argv", ["reel_listen", "--plan-file", str(plan)])
    assert reel_listen.whisper_binary() is None
    assert reel_listen.main() == 0
    assert "Whisper not found" in capsys.readouterr().err
    assert not (tmp_path / "listen.json").exists()


def test_transcribe_uses_cache(tmp_path):
    film = tmp_path / "film.mp4"
    film.write_bytes(b"x")
    win = {"label": "t01", "start": 1.0, "end": 2.0}
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / f"{reel_listen._key(film, win)}.json").write_text('{"text": " Корт "}', encoding="utf-8")
    with mock.patch.object(reel_listen.subprocess, "run") as run:
        heard = reel_listen.transcribe(film, [win], cache, "whisper")
    run.assert_not_called()
    assert list(heard.values()) == ["Корт"]


# ── reel's post-render hook ─────────────────────────────────────────────────


def _items(tmp_path):
    new = SimpleNamespace(status="succeeded", started_at=1.0, output_path=str(tmp_path / "a.mp4"))
    resumed = SimpleNamespace(status="succeeded", started_at=None, output_path=str(tmp_path / "b.mp4"))
    failed = SimpleNamespace(status="failed", started_at=1.0, output_path=None)
    return [new, resumed, failed]


def test_hook_upscales_only_new_clips_when_hd(tmp_path):
    from common.runners.cli import reel_upscale

    with mock.patch.object(reel_upscale, "binary", return_value="esrgan"), \
            mock.patch.object(reel_upscale, "upscale") as up:
        assert _reel_hd.upscale_new({"hd": True}, _items(tmp_path)) == 1
    up.assert_called_once_with(Path(tmp_path / "a.mp4"), "esrgan")


def test_hook_does_nothing_without_hd(tmp_path):
    from common.runners.cli import reel_upscale

    with mock.patch.object(reel_upscale, "binary") as exe, mock.patch.object(reel_upscale, "upscale") as up:
        assert _reel_hd.upscale_new({}, _items(tmp_path)) == 0
    exe.assert_not_called()
    up.assert_not_called()


def test_hook_skips_without_realesrgan(tmp_path, capsys):
    from common.runners.cli import reel_upscale

    with mock.patch.object(reel_upscale, "binary", side_effect=RunnerError("Real-ESRGAN not found")), \
            mock.patch.object(reel_upscale, "upscale") as up:
        assert _reel_hd.upscale_new({"hd": True}, _items(tmp_path)) == 0
    up.assert_not_called()
    assert "Real-ESRGAN not found" in capsys.readouterr().err


def test_reel_generate_calls_the_hook():
    import inspect

    from common.runners.cli import reel

    assert "upscale_new(job.plan, shots_result.items)" in inspect.getsource(reel._generate)
