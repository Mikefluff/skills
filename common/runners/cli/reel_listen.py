"""Listen to a finished film — every line transcribed where it plays, and the ones the ear would miss flagged.

  python3 -m common.runners.cli.reel_listen --plan-file <dir>/plan.json [--film <mp4>] [--only t03a,t08b]
                                            [--threshold 0.6]

Every dialogue line (a shot's dialogue[*].line, placed at its clock_at + line_at) and every vocal with words in
it (plan.vocals, [bracket tags] stripped; "А-а-ах!" and "Хи-хи" are not words) is cut out of the film with a
little padding and transcribed by a local Whisper (mlx_whisper, nothing is paid). The heard text is compared
with the line after normalisation (lowercase, ё→е, no punctuation); a line whose best match scores under the
threshold is reported as expected vs heard. Short lines under music ("Корт" heard as «Торт», «Ещё!») are what
this catches. Children's high voices transcribe poorly, so a flagged baby line means "listen", not "broken".

The film defaults to <output_dir>/trailer.mp4 (what `reel_animatic --clips` writes). Transcripts are cached in
<output_dir>/listen-cache/, keyed by the window and the film's mtime; the report goes to <output_dir>/listen.json.

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
from pathlib import Path
from typing import Any

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
             "start": round(max(0.0, at - pad), 3), "end": round(_shot_end(shot) + pad, 3)}
            for line in shot.get("dialogue") or [] if normalize(line.get("line", ""))]


def _vocal(vocal: dict[str, Any], shot: dict[str, Any], pad: float) -> dict[str, Any]:
    at = float(shot["clock_at"]) + float(vocal.get("at") or 0)
    # a vocal is a breath or a word or two: about half a second a word, never past the shot's spill
    end = min(_shot_end(shot), at + max(1.5, 0.5 * len(normalize(vocal["text"]).split()) + 0.8))
    return {"label": shot["label"], "kind": "vocal", "who": vocal.get("who"), "expected": normalize(vocal["text"]),
            "start": round(max(0.0, at - pad), 3), "end": round(end + pad, 3)}


def _said(plan: dict[str, Any], shots: dict[str, Any]) -> list[dict[str, Any]]:
    """The vocals in shots the cut keeps that say a word."""
    return [v for v in plan.get("vocals") or [] if v.get("shot") in shots and has_words(v.get("text", ""))]


def windows(plan: dict[str, Any], only: set[str] | None = None, pad: float = _PAD) -> list[dict[str, Any]]:
    """Every line with words, with the stretch of the film it plays in, in clock order."""
    shots = {s["label"]: s for s in plan["shots"] if not s.get("cut") and "clock_at" in s}
    out = [w for s in shots.values() for w in _dialogue(s, pad)]
    out += [_vocal(v, shots[v["shot"]], pad) for v in _said(plan, shots)]
    return sorted((w for w in out if not only or w["label"] in only), key=lambda w: w["start"])


# ── Whisper ─────────────────────────────────────────────────────────────────


def whisper_binary() -> str | None:
    found = os.environ.get("WHISPER") or shutil.which("mlx_whisper")
    if found:
        return found
    return str(_FALLBACK) if _FALLBACK.is_file() else None


def _key(film: Path, window: dict[str, Any]) -> str:
    raw = f"{film.resolve()}|{film.stat().st_mtime_ns}|{window['start']:.3f}|{window['end']:.3f}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def _whisper(exe: str, wav: Path, cache: Path) -> None:
    # one file per call: mlx_whisper's CLI names every output after the first input when given several
    subprocess.run([exe, str(wav), "--model", os.environ.get("WHISPER_MODEL") or _MODEL, "--language", "ru",
                    "--output-format", "json", "--output-dir", str(cache), "--verbose", "False",
                    "--condition-on-previous-text", "False"], check=True, capture_output=True)


def transcribe(film: Path, wins: list[dict[str, Any]], cache: Path, exe: str) -> dict[str, str]:
    """key → heard text. A window not cached yet is cut to a 16 kHz wav and goes to Whisper; its json output,
    named by the key, is the cache."""
    cache.mkdir(parents=True, exist_ok=True)
    keys = {_key(film, w): w for w in wins}
    todo = [k for k in keys if not (cache / f"{k}.json").is_file()]
    for n, k in enumerate(todo, 1):
        w, wav = keys[k], cache / f"{k}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(w["start"]), "-t",
                        str(round(w["end"] - w["start"], 3)), "-i", str(film), "-vn", "-ac", "1", "-ar", "16000",
                        str(wav)], check=True, capture_output=True)
        try:
            _whisper(exe, wav, cache)
        finally:
            wav.unlink(missing_ok=True)
        print(f"  {n}/{len(todo)} {w['label']} ({len(keys) - len(todo)} cached)", file=sys.stderr)
    return {k: json.loads((cache / f"{k}.json").read_text(encoding="utf-8")).get("text", "").strip()
            for k in keys}


# ── report ──────────────────────────────────────────────────────────────────


def judge(film: Path, wins: list[dict[str, Any]], heard: dict[str, str], threshold: float) -> list[dict[str, Any]]:
    out = []
    for w in wins:
        text = heard_text(heard.get(_key(film, w), ""))
        score = similarity(w["expected"], text)
        out.append({**w, "heard": text, "score": score, "flagged": score < threshold})
    return out


def report(results: list[dict[str, Any]], threshold: float) -> None:
    flagged = [r for r in results if r["flagged"]]
    print(f"Listened to {len(results)} line(s); {len(flagged)} under {threshold}. Children's high voices and "
          "one-word vocals transcribe poorly — a flag means listen to it, not that it is wrong.", file=sys.stderr)
    for r in flagged:
        print(f"  {r['label']:<6} {r['who'] or '?':<12} {r['score']:.2f}  {r['start']:7.2f}s  "
              f"expected «{r['expected']}»  heard «{r['heard'] or '(nothing)'}»", file=sys.stderr)


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
