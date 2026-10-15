"""Conform the voice to the picture — after generation, before the final mix.

Seedance takes the take as an audio reference but re-performs it: the mouth on
screen says each line up to a few seconds off the master and skips some words.
This step listens to what the picture says (ElevenLabs speech-to-text on the
generated audio), moves each phrase of the master take to where the mouth says
it, and rewrites the plan so the next stitch uses the conformed voice and every
sound placed on a word follows that word.

  python3 -m common.runners.cli.reel_conform --plan-file <dir>/plan.json \
      --picture <dir>/shots/<generated>.mp4
  python3 -m common.runners.cli.reel --plan-file <dir>/plan.json --resume --yes

A film of separate shots needs no --picture. Each lip-sync shot's clip is read
from the manifest and first slipped: its window moves later in the clip by the
model's lag, keeping the cut points. Then the residue is conformed, and
voice-over phrases stay where the master has them.

Writes voice/conformed.wav and voice/heard.json; edits plan.json in place
(voiceover path, the shot's trim, the times of sounds placed on words — snapped
hits stay on their picture events; master times are kept as `at_master`, so running it again starts from the same place).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .. import config
from .. import ffmpeg_film
from .. import voice_timing as vt
from ..errors import RunnerError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_conform")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--picture", type=Path,
                        help="one-generation film: the generated video, with the model's own audio still on it "
                             "(a film of separate shots is read from the manifest)")
    parser.add_argument("--language", default="ru", help="speech-to-text language code (default ru)")
    return parser


def _duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def _heard(picture: Path, cache: Path, language: str) -> list[vt.Word]:
    """What the picture's mouth says; cached per picture, since it never changes."""
    if cache.is_file():
        data = json.loads(cache.read_text(encoding="utf-8"))
        if data.get("picture") == picture.name:
            return [vt.Word(**w) for w in data["words"]]
    from ..providers.elevenlabs import transcribe

    config.get_provider("eleven-tts").ensure_available()
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / "heard.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(picture), "-vn", "-ac", "1", "-b:a", "128k",
                        str(mp3)], check=True, capture_output=True)
        words = [vt.Word(w["text"], w["start"], w["end"]) for w in transcribe(mp3.read_bytes(), language)]
    cache.write_text(json.dumps({"picture": picture.name, "words": [w.__dict__ for w in words]},
                                ensure_ascii=False, indent=1), encoding="utf-8")
    return words


def _retime_sound(sound: dict[str, Any], moves: list[vt.Move], length: float) -> None:
    sound["total_seconds"] = round(length, 3)
    for p in sound.get("placements") or []:
        if p.get("snap"):
            continue  # hits on picture events; the picture did not move
        at = p.setdefault("at_master", p["at"])
        p["at"] = vt.warp(moves, at)
        if p.get("length"):
            p.setdefault("length_master", p["length"])
            p["length"] = round(vt.warp(moves, at + p["length_master"]) - p["at"], 3)


def _shots(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(plan["shots"], key=lambda e: int(e["index"]))


def _cut(entry: dict[str, Any]) -> float:
    kwargs = entry.get("kwargs") or {}
    return float(entry.get("trim_seconds") or kwargs.get("duration_seconds") or 5)


def _lip_clips(plan: dict[str, Any], out_dir: Path) -> Iterator[tuple[dict[str, Any], Path, float, float]]:
    """Each lip-sync shot that generated, with where its cut starts on the film clock and how long it runs."""
    done = {int(it["index"]): Path(it["output_path"])
            for it in json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))["items"]
            if it.get("status") == "succeeded" and it.get("output_path")}
    film_at = 0.0
    for entry in _shots(plan):
        cut = _cut(entry)
        clip = done.get(int(entry["index"]))
        if entry.get("lip_sync") and clip:
            yield entry, clip, film_at, cut
        film_at += cut


def _clip_heard(clip: Path, out_dir: Path, language: str) -> list[vt.Word]:
    return _heard(clip, out_dir / "voice" / f"heard-{clip.stem}.json", language)


def _heard_shots(plan: dict[str, Any], out_dir: Path, language: str) -> tuple[list[vt.Word], float]:
    """A film of separate shots: what each lip-sync shot says, on the film clock."""
    heard = []
    for entry, clip, film_at, cut in _lip_clips(plan, out_dir):
        start = float(entry.get("trim_start") or 0)
        for w in _clip_heard(clip, out_dir, language):
            t = film_at + w.start - start
            if film_at <= t < film_at + cut:
                heard.append(vt.Word(w.text, round(t, 3), round(film_at + w.end - start, 3)))
    return heard, round(sum(_cut(e) for e in _shots(plan)), 2)


def _slip(plan: dict[str, Any], out_dir: Path, words: list[vt.Word], language: str) -> list[str]:
    """Slip each lip-sync shot by the model's lag, so its mouth meets the master where the cut is.

    Seedance starts the line late — 0.7-1.3 s on the trial film — and moving
    the voice to the mouth then pushes every voice-over line after it and runs
    the last word off the end of the film. An editor slips the picture instead:
    the same cut points, the shot's window taken later in its clip by the lag.
    The handle behind the window limits how far a shot can slip.
    """
    report = []
    for entry, clip, film_at, cut in _lip_clips(plan, out_dir):
        planned = float(entry.setdefault("trim_start_planned", entry.get("trim_start") or 0))
        inside = [w for w in words if film_at <= w.start < film_at + cut]
        pairs, _ = vt._matches(inside, _clip_heard(clip, out_dir, language), 0)
        if pairs:
            lags = sorted(h.start - (m.start - film_at + planned) for m, h in pairs)
            lag = lags[len(lags) // 2]
            room = _duration(clip) - planned - cut - 0.05
            slip = round(min(max(lag, -planned), room), 3)
            entry["trim_start"] = round(planned + slip, 3)
            report.append(f"{entry.get('label')}: lag {lag:+.2f}s, slipped {slip:+.2f}s")
    return report


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    out_dir = Path(plan["output_dir"])
    timing = json.loads((out_dir / "timing.json").read_text(encoding="utf-8"))
    master = Path(timing["voice_master"])
    words = [vt.Word(w["text"], w["start"], w["end"]) for w in timing["words"]]
    single = len(plan.get("shots") or []) == 1
    if single:
        if not args.picture:
            raise RunnerError("--picture is required for a one-generation film")
        heard = _heard(args.picture, out_dir / "voice" / "heard.json", args.language)
        length = round(_duration(args.picture), 2)
    else:
        slips = _slip(plan, out_dir, words, args.language)
        heard, length = _heard_shots(plan, out_dir, args.language)
    moves = vt.conform(words, heard, carry=single)
    conformed = out_dir / "voice" / "conformed.wav"
    ffmpeg_film.assemble(master, conformed, [(m.src_start, m.src_end, m.dst_start, m.tempo) for m in moves], length)

    plan["voiceover"] = {**(plan.get("voiceover") or {}), "path": str(conformed)}
    if single:
        plan["shots"][0]["trim_seconds"] = length
    if plan.get("sound"):
        _retime_sound(plan["sound"], moves, length)
    args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"moves": moves, "phrases": vt.phrases(words), "length": length, "heard": len(heard),
            "slips": [] if single else slips}


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    try:
        report = run(args)
    except (RunnerError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for line in report["slips"]:
        print(f"  slip {line}", file=sys.stderr)
    print(f"Heard {report['heard']} words; film {report['length']:.2f}s", file=sys.stderr)
    for move, phrase in zip(report["moves"], report["phrases"]):
        shift = move.dst_start - move.src_start
        text = " ".join(w.text for w in phrase)[:48]
        print(f"  {move.src_start:6.2f} → {move.dst_start:6.2f} ({shift:+.2f}s, ×{move.tempo:.2f})  {text}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
