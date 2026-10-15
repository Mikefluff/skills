"""Voice phase of a voiced reel — script → ElevenLabs take → word timings → cut plan.

Runs before any prompt is written, because the prompts are written against it:
every visual event in a voiced film is pinned to the second its word is spoken,
and every segment boundary has to fall in a pause. Neither is knowable until the
voice exists.

  python3 -m common.runners.cli.reel_voice --script-file vo.txt --voice-id <id> \
      --output-dir ./generated/reel/<slug> [--max-seconds 30] [--lead 0.8] [--tail 1.5]

  # A recorded or previously generated take: forced alignment instead of TTS.
  python3 -m common.runners.cli.reel_voice --script-file vo.txt --voice-file take.mp3 ...

Writes into the output dir:
  voice/raw.mp3        the take as the vendor returned it
  voice/master.wav     the take on the film clock: `lead` of silence, speech, `tail`
  voice/seg-NN.wav     one lip-sync reference per segment, silence-padded to its request
  timing.json          words + segments on the film clock; input to the film prompt chain

The film clock is the master: segment N's prompt timecodes are relative to its
own start, and timing.json carries both.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .. import config
from .. import cost as cost_mod
from .. import ffmpeg as ff_mod
from .. import ffmpeg_film
from .. import voice_timing as vt
from ..errors import CostConfirmationDeclined, RunnerError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_voice")
    parser.add_argument("--script-file", type=Path, required=True, help="voiceover text with v4 direction tags, e.g. [dry, sarcastic]")
    parser.add_argument("--output-dir", type=Path, required=True)
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--voice-id", help="ElevenLabs voice id")
    src.add_argument("--voice-file", type=Path, help="existing take; aligned instead of synthesised")
    parser.add_argument("--model-id", default="eleven_v4", help="ElevenLabs TTS model (default eleven_v4)")
    parser.add_argument("--stability", type=float,
                        help="lower = more expressive and more varied between takes (vendor default if unset)")
    parser.add_argument("--takes", type=int, default=1,
                        help="generate N takes (voice/take-K.mp3); tags are guidance, so pick the best by ear")
    parser.add_argument("--pick", type=int, default=1, help="which take the film is cut against (existing takes are reused)")
    parser.add_argument("--tempo", type=float, default=1.0,
                        help="retime the picked take without changing pitch (e.g. 1.04 to fit a 30 s generation)")
    parser.add_argument("--max-seconds", type=float, default=30.0,
                        help="longest single generation: 30 for Seedance 2.5, 15 for 2.0")
    parser.add_argument("--min-seconds", type=float, default=4.0)
    parser.add_argument("--lead", type=float, default=0.8, help="picture before the first word (s)")
    parser.add_argument("--tail", type=float, default=1.5, help="picture after the last word (s)")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


def _synthesise(text: str, args: argparse.Namespace) -> tuple[bytes, list[vt.Word] | None]:
    kwargs: dict[str, Any] = {"model_id": args.model_id, "with_timestamps": True}
    if args.voice_id:
        kwargs["voice_id"] = args.voice_id
    if args.stability is not None:
        kwargs["stability"] = args.stability
    result = config.get_provider("eleven-tts").generate(text, **kwargs)
    alignment = result.extra.get("alignment")
    return result.content, (vt.words_from_alignment(alignment) if alignment else None)


def _align(audio: bytes, text: str) -> list[vt.Word]:
    from ..providers.elevenlabs import forced_alignment

    config.get_provider("eleven-tts").ensure_available()
    spoken = vt.strip_tags(text)
    return [vt.Word(w["text"], w["start"], w["end"]) for w in forced_alignment(audio, spoken) if w["text"].strip()]


def _takes(text: str, args: argparse.Namespace, voice_dir: Path) -> Path:
    """Every requested take on disk with its word timings; returns the picked one.

    A take already on disk is never regenerated, so `--pick 2` after a
    `--takes 3` run costs nothing — it only re-cuts the film against take 2.
    """
    missing = [k for k in range(1, args.takes + 1) if not (voice_dir / f"take-{k}.words.json").is_file()]
    if missing:
        estimate = config.get_provider("eleven-tts").estimate_cost(prompt=text)
        if estimate is not None:
            cost_mod.confirm_batch(estimate * len(missing), n_items=len(missing), modality="voice", yes=args.yes)
    for k in missing:
        audio, words = _synthesise(text, args)
        (voice_dir / f"take-{k}.mp3").write_bytes(audio)
        if words is None:
            print(f"  take {k}: no alignment in the TTS response — running forced alignment", file=sys.stderr)
            words = _align(audio, text)
        _save_words(voice_dir / f"take-{k}.words.json", words)
    return voice_dir / f"take-{args.pick}.mp3"


def _retimed(raw: Path, words: list[vt.Word], tempo: float, voice_dir: Path) -> tuple[Path, list[vt.Word]]:
    out = voice_dir / f"{raw.stem}-x{tempo:g}.wav"
    ffmpeg_film.retime(raw, out, tempo)
    return out, [vt.Word(w.text, round(w.start / tempo, 3), round(w.end / tempo, 3)) for w in words]


def _save_words(path: Path, words: list[vt.Word]) -> None:
    path.write_text(json.dumps([w.__dict__ for w in words], ensure_ascii=False), encoding="utf-8")


def _load_words(path: Path) -> list[vt.Word]:
    return [vt.Word(**w) for w in json.loads(path.read_text(encoding="utf-8"))]


def _shift(words: list[vt.Word], by: float) -> list[vt.Word]:
    return [vt.Word(w.text, round(w.start + by, 3), round(w.end + by, 3)) for w in words]


def _segment_audio(segs: list[vt.Segment], master: Path) -> list[dict[str, Any]]:
    """timing.json entries, each with the lip-sync reference its generation gets."""
    out = []
    for seg in segs:
        entry = seg.to_json()
        if len(segs) == 1:
            entry["audio"] = str(master)
        else:
            path = master.parent / f"seg-{seg.index:02d}.wav"
            ffmpeg_film.slice_audio(master, path, (seg.start, seg.end), seg.request_seconds)
            entry["audio"] = str(path)
        out.append(entry)
    return out


def run(args: argparse.Namespace) -> dict[str, Any]:
    text = args.script_file.read_text(encoding="utf-8").strip()
    if not text:
        raise RunnerError(f"script is empty: {args.script_file}")
    voice_dir = args.output_dir / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    if args.voice_file:
        raw = args.voice_file
        words = _align(raw.read_bytes(), text)
    else:
        raw = _takes(text, args, voice_dir)
        words = _load_words(raw.with_suffix(".words.json"))
    if args.tempo != 1.0:
        raw, words = _retimed(raw, words, args.tempo, voice_dir)
    if not words:
        raise RunnerError("no word timings — cannot plan cuts")

    speech_end = ff_mod.get_duration(raw) or words[-1].end
    total = round(args.lead + speech_end + args.tail, 3)
    words = _shift(words, args.lead)

    master = voice_dir / "master.wav"
    ffmpeg_film.pad_audio(raw, master, lead=args.lead, total=total)

    rules = vt.CutRules(max_seconds=args.max_seconds, min_seconds=args.min_seconds)
    out_segments = _segment_audio(vt.segments(words, total, rules), master)

    timing = {
        "schema": "skills.reel.timing.v1",
        "script": text,
        "total_seconds": total,
        "lead_seconds": args.lead,
        "tail_seconds": args.tail,
        "max_segment_seconds": args.max_seconds,
        "voice_master": str(master),
        "voice_take": str(raw),
        "tempo": args.tempo,
        "words": [{"text": w.text, "start": w.start, "end": w.end} for w in words],
        "segments": out_segments,
    }
    (args.output_dir / "timing.json").write_text(json.dumps(timing, indent=2, ensure_ascii=False), encoding="utf-8")
    return timing


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    if not ff_mod.detect_ffmpeg().found:
        print("ffmpeg is required for the voice phase (padding and slicing the take).", file=sys.stderr)
        return 2
    try:
        timing = run(args)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (RunnerError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    segs = timing["segments"]
    print(f"Voice: {timing['voice_master']} ({timing['total_seconds']:.2f}s on the film clock)", file=sys.stderr)
    for s in segs:
        print(f"  seg {s['index']}: {s['start']:.2f}-{s['end']:.2f}s → request {s['request_seconds']}s", file=sys.stderr)
    if len(segs) == 1:
        print("  one generation, no seams", file=sys.stderr)
    print(str(args.output_dir / "timing.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
