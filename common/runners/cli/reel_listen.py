"""Listen to a finished film — every line transcribed where it plays, and the ones the ear would miss flagged.

  python3 -m common.runners.cli.reel_listen --plan-file <dir>/plan.json [--film <mp4>] [--only t03a,t08b]
                                            [--threshold 0.6]

Every dialogue line (a shot's dialogue[*].line, placed at its clock_at + line_at) and every vocal with words in
it (plan.vocals, [bracket tags] stripped; "А-а-ах!" and "Хи-хи" are not words) is cut out of the film with a
little padding and transcribed by a local Whisper (mlx_whisper, nothing is paid). The heard text is compared
with the line after normalisation (lowercase, ё→е, no punctuation); a line whose best match scores under the
threshold is reported as expected vs heard, with a suggested "gain_db" (+4 when nothing was heard, +3 when
the words came out wrong) and the JSON path to set it on (vocals[57].gain_db, shots[t03a].dialogue[0].gain_db).
Short lines under music ("Корт" heard as «Торт», «Ещё!») are what this catches. Children's high voices transcribe poorly, so a flagged baby line means "listen", not "broken".

The film defaults to <output_dir>/trailer.mp4 (what `reel_animatic --clips` writes). Transcripts are cached in
<output_dir>/listen-cache/, keyed by the sound itself — the window's samples, the Whisper model and the
language — so a re-cut that leaves a line's stretch of sound as it was (a picture-only change, a re-mux, every
line before the first change) hears it from the cache instead of from Whisper again. The film's sound is pulled
out once per film file; the report goes to <output_dir>/listen.json.

Whisper is found through $WHISPER, then `mlx_whisper` on PATH, then the video-dub venv; the model through
$WHISPER_MODEL (default mlx-community/whisper-large-v3-turbo).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

from . import _stage_cache as sc

_FALLBACK = Path.home() / "Documents" / "video-dub" / ".venv" / "bin" / "mlx_whisper"
_MODEL = "mlx-community/whisper-large-v3-turbo"
_PAD = 0.3
_SPILL = 0.4  # a line may run this far past its cut (as in _animatic_voice)
_LINE_AT = 0.3
_THRESHOLD = 0.6


# ── text ────────────────────────────────────────────────────────────────────


def normalize(text: str) -> str:
    """Lowercase, ё→е, [tags] and punctuation gone, single spaces."""
    text = re.sub(r"\[[^\]]*\]", " ", text or "").lower().replace("ё", "е")
    return " ".join(re.sub(r"[\W_]+", " ", text).split())


# sounds that pass for words by their letters: the vocals a voice-performance chain writes most
_SOUNDS = frozenset({"хып", "хэх", "апчх", "ням", "фью", "рау", "хмф", "ахх", "охх", "уфф", "пфф", "кхм"})
_VOWELS = frozenset("аеиоуыэюя")
# what Whisper writes when it hears no speech (it was trained on subtitled video)
_SILENCE = ("субтитры", "продолжение следует", "редактор субтитров", "спасибо за просмотр", "dimatorzok")


def has_words(text: str) -> bool:
    """A vocal says something when one of its pieces (split on spaces and hyphens) is a word: 3+ letters, a
    vowel, not one letter held, not a known sound. "Ура!", "Ещё!" do; "А-а-ах!", "Тсс", "Хып!", "Ррр!" do not."""
    pieces = normalize(text.replace("-", " ")).split()
    return any(len(p) >= 3 and len(set(p)) >= 2 and _VOWELS & set(p) and p not in _SOUNDS for p in pieces)


def heard_text(raw: str) -> str:
    """Whisper's text with its no-speech phrases dropped and a held letter ("АААА…") cut to three."""
    if any(mark in raw.lower() for mark in _SILENCE):
        return ""
    return re.sub(r"(\w)\1{3,}", r"\1\1\1", re.sub(r"((\w)-)\1{3,}", r"\1\1\1", raw)).strip()


def similarity(expected: str, heard: str) -> float:
    """0..1: the expected line against the heard text, or against its best stretch of as many words (a window
    also catches the neighbouring line's tail, which must not count against this one)."""
    want, got = normalize(expected), normalize(heard)
    if not want or not got:
        return 0.0
    best = difflib.SequenceMatcher(None, want, got).ratio()
    words, n = got.split(), len(want.split())
    for size in {max(1, n - 1), n, n + 1}:
        for i in range(max(1, len(words) - size + 1)):
            chunk = " ".join(words[i:i + size])
            best = max(best, difflib.SequenceMatcher(None, want, chunk).ratio())
    return round(best, 3)


# ── where the lines are ────────────────────────────────────────────────────


def _shot_end(shot: dict[str, Any]) -> float:
    return float(shot["clock_at"]) + float(shot["trim_seconds"]) + _SPILL


def _dialogue(shot: dict[str, Any], pad: float) -> list[dict[str, Any]]:
    at = float(shot["clock_at"]) + float(shot.get("line_at") or _LINE_AT)
    return [{"label": shot["label"], "kind": "line", "who": line.get("who"), "expected": line["line"],
             "start": round(max(0.0, at - pad), 3), "end": round(_shot_end(shot) + pad, 3),
             "path": f"shots[{shot['label']}].dialogue[{i}].gain_db", "gain_db": line.get("gain_db")}
            for i, line in enumerate(shot.get("dialogue") or []) if normalize(line.get("line", ""))]


def _vocal(n: int, vocal: dict[str, Any], shot: dict[str, Any], pad: float) -> dict[str, Any]:
    at = float(shot["clock_at"]) + float(vocal.get("at") or 0)
    # a vocal is a breath or a word or two: about half a second a word, never past the shot's spill
    end = min(_shot_end(shot), at + max(1.5, 0.5 * len(normalize(vocal["text"]).split()) + 0.8))
    return {"label": shot["label"], "kind": "vocal", "who": vocal.get("who"), "expected": normalize(vocal["text"]),
            "start": round(max(0.0, at - pad), 3), "end": round(end + pad, 3),
            "path": f"vocals[{n}].gain_db", "gain_db": vocal.get("gain_db")}


def _said(plan: dict[str, Any], shots: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    """The vocals in shots the cut keeps that say a word, with their place in plan.vocals."""
    return [(n, v) for n, v in enumerate(plan.get("vocals") or [])
            if v.get("shot") in shots and has_words(v.get("text", ""))]


def windows(plan: dict[str, Any], only: set[str] | None = None, pad: float = _PAD) -> list[dict[str, Any]]:
    """Every line with words, with the stretch of the film it plays in, in clock order."""
    shots = {s["label"]: s for s in plan["shots"] if not s.get("cut") and "clock_at" in s}
    out = [w for s in shots.values() for w in _dialogue(s, pad)]
    out += [_vocal(n, v, shots[v["shot"]], pad) for n, v in _said(plan, shots)]
    return sorted((w for w in out if not only or w["label"] in only), key=lambda w: w["start"])


# ── Whisper ─────────────────────────────────────────────────────────────────


def whisper_binary() -> str | None:
    found = os.environ.get("WHISPER") or shutil.which("mlx_whisper")
    if found:
        return found
    return str(_FALLBACK) if _FALLBACK.is_file() else None


def _key(film: Path, window: dict[str, Any]) -> str:
    """The window on this film file (its path and mtime): what `transcribe` returns the heard text under, and the
    name of a transcript cached before transcripts were keyed by their sound."""
    raw = f"{film.resolve()}|{film.stat().st_mtime_ns}|{window['start']:.3f}|{window['end']:.3f}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


_RATE = 16000


def _model() -> str:
    return os.environ.get("WHISPER_MODEL") or _MODEL


def _film_audio(film: Path, cache: Path) -> Path:
    """The film's sound as one 16 kHz mono wav, pulled out once per film file (path, size, mtime)."""
    wav = cache / f"film-{sc.key(sc.file_sig(film))}.wav"
    if not wav.is_file():
        for old in cache.glob("film-*.wav"):
            old.unlink()
        part = cache / "film.part.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(film), "-vn", "-ac", "1", "-ar", str(_RATE),
                        "-c:a", "pcm_s16le", str(part)], check=True, capture_output=True)
        part.replace(wav)
    return wav


def _samples(audio: Path, wins: list[dict[str, Any]]) -> list[bytes]:
    """Each window's stretch of the film's sound, as raw 16-bit samples."""
    out = []
    with wave.open(str(audio), "rb") as f:
        for w in wins:
            f.setpos(min(int(w["start"] * _RATE), f.getnframes()))
            out.append(f.readframes(int(round((w["end"] - w["start"]) * _RATE))))
    return out


def sound_key(samples: bytes) -> str:
    """A transcript's cache key: the sound it was heard from, the model and the language."""
    return hashlib.sha1(samples + f"|{_model()}|ru".encode()).hexdigest()[:16]


def _write_wav(path: Path, samples: bytes) -> None:
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(_RATE)
        f.writeframes(samples)


def _whisper(exe: str, wav: Path, cache: Path) -> None:
    # one file per call: mlx_whisper's CLI names every output after the first input when given several
    subprocess.run([exe, str(wav), "--model", _model(), "--language", "ru",
                    "--output-format", "json", "--output-dir", str(cache), "--verbose", "False",
                    "--condition-on-previous-text", "False"], check=True, capture_output=True)


def _lookup(cache: Path, keys: dict[str, str]) -> list[str]:
    """Window ids with no transcript yet. One cached under the older film-and-mtime name is still this sound
    (same file, same window), so it is copied to its sound key, not heard again."""
    todo = []
    for wid, k in keys.items():
        legacy = cache / f"{wid}.json"
        if not (cache / f"{k}.json").is_file() and legacy.is_file():
            (cache / f"{k}.json").write_bytes(legacy.read_bytes())
        if not (cache / f"{k}.json").is_file():
            todo.append(wid)
    return todo


def transcribe(film: Path, wins: list[dict[str, Any]], cache: Path, exe: str) -> dict[str, str]:
    """window id (`_key`) → heard text. Each window's sound is keyed by its samples; one not heard before goes to
    Whisper as a 16 kHz wav, and its json output, named by the sound key, is the cache."""
    cache.mkdir(parents=True, exist_ok=True)
    by_id = {_key(film, w): w for w in wins}
    audio = _film_audio(film, cache)
    sound = dict(zip(by_id, _samples(audio, list(by_id.values()))))
    keys = {wid: sound_key(samples) for wid, samples in sound.items()}
    todo = _lookup(cache, keys)
    if len(keys) > len(todo):
        print(f"Listen: {len(keys) - len(todo)} of {len(keys)} line(s) sound as before, heard from the cache",
              file=sys.stderr)
    for n, wid in enumerate(todo, 1):
        wav = cache / f"{keys[wid]}.wav"
        _write_wav(wav, sound[wid])
        try:
            _whisper(exe, wav, cache)
        finally:
            wav.unlink(missing_ok=True)
        print(f"  {n}/{len(todo)} {by_id[wid]['label']}", file=sys.stderr)
    return {wid: json.loads((cache / f"{k}.json").read_text(encoding="utf-8")).get("text", "").strip()
            for wid, k in keys.items()}


# ── report ──────────────────────────────────────────────────────────────────


def judge(film: Path, wins: list[dict[str, Any]], heard: dict[str, str], threshold: float) -> list[dict[str, Any]]:
    out = []
    for w in wins:
        text = heard_text(heard.get(_key(film, w), ""))
        score = similarity(w["expected"], text)
        out.append({**w, "heard": text, "score": score, "flagged": score < threshold})
        if score < threshold:
            out[-1]["suggest_gain_db"] = suggested_gain(out[-1])
    return out


def suggested_gain(result: dict[str, Any]) -> float:
    """A flagged line a step louder in the voice mix: +4 dB when nothing was heard, +3 when the words were wrong,
    on top of the gain it already has, held to the mix's +12."""
    return min(12.0, float(result.get("gain_db") or 0) + (3.0 if result.get("heard") else 4.0))


def report(results: list[dict[str, Any]], threshold: float) -> None:
    flagged = [r for r in results if r["flagged"]]
    print(f"Listened to {len(results)} line(s); {len(flagged)} under {threshold}. Children's high voices and "
          "one-word vocals transcribe poorly — a flag means listen to it, not that it is wrong.", file=sys.stderr)
    for r in flagged:
        print(f"  {r['label']:<6} {r['who'] or '?':<12} {r['score']:.2f}  {r['start']:7.2f}s  "
              f"expected «{r['expected']}»  heard «{r['heard'] or '(nothing)'}»", file=sys.stderr)
        print(f"         louder: set {r['path']} = {r['suggest_gain_db']:g}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_listen")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--film", type=Path, help="the finished film (default: <output_dir>/trailer.mp4)")
    parser.add_argument("--only", help="comma-separated shot labels (default: every line)")
    parser.add_argument("--threshold", type=float, default=_THRESHOLD, help=f"flag below this (default {_THRESHOLD})")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    out = Path(plan["output_dir"])
    film = args.film or out / "trailer.mp4"
    exe = whisper_binary()
    if exe is None:
        print("Whisper not found: set $WHISPER or install mlx_whisper — nothing listened to", file=sys.stderr)
        return 0
    if not film.is_file():
        print(f"No film at {film}: cut it with reel_animatic --clips, or pass --film", file=sys.stderr)
        return 1
    wins = windows(plan, set((args.only or "").split(",")) - {""})
    try:
        heard = transcribe(film, wins, out / "listen-cache", exe)
    except subprocess.CalledProcessError as exc:
        print(f"{exc.cmd[0]} failed: {(exc.stderr or b'').decode(errors='replace')[-400:]}", file=sys.stderr)
        return 1
    results = judge(film, wins, heard, args.threshold)
    report(results, args.threshold)
    (out / "listen.json").write_text(json.dumps({"film": str(film), "threshold": args.threshold,
                                                 "only": args.only, "lines": results}, ensure_ascii=False,
                                                indent=2) + "\n", encoding="utf-8")
    print(f"Report: {out / 'listen.json'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
