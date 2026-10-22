"""A line read once is never bought again when a silent shot splits or joins the exchange it was read in."""

from __future__ import annotations

import json

from common.runners.cli import _animatic_voice as av


def _group(*lines):
    return [{"who": who, "line": text, "label": f"s{n}", "at": n, "room": 3, "shot_start": n, "shot_end": n + 3}
            for n, (who, text) in enumerate(lines)]


def test_a_regrouped_exchange_is_put_together_from_its_first_readings(tmp_path, monkeypatch):
    voices = {"a": "VA", "b": "VB"}
    bought = []

    def dialogue(inputs, language=None, effects=None):
        bought.append([i["text"] for i in inputs])
        return b"take", [{"dialogue_input_index": n, "start_time_seconds": n, "end_time_seconds": n + 0.9}
                         for n in range(len(inputs))]

    monkeypatch.setattr(av, "_clean_take", lambda d, inputs, lang, fx: dialogue(inputs))
    monkeypatch.setattr(av, "_cut", lambda take, clip, start, end: clip.write_bytes(f"{start}".encode()))
    first = av.read_exchange(_group(("a", "Привет!"), ("b", "Пока!")), voices, tmp_path, "ru")
    # a silent shot now stands between the two lines: two exchanges of one line each
    again = av.read_exchange(_group(("a", "Привет!")), voices, tmp_path, "ru")
    again += av.read_exchange(_group(("b", "Пока!")), voices, tmp_path, "ru")
    assert len(bought) == 1 and again == first
    assert av.take_kept(_group(("b", "Пока!")), voices, tmp_path, "ru")
    assert len(json.loads((tmp_path / "lines.json").read_text())) == 2
