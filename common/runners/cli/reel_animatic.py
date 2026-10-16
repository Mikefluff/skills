"""Animatic of a cut — the storyboard on its clock, with title cards, scratch dialogue and the soundtrack.

  python3 -m common.runners.cli.reel_animatic --plan-file <dir>/plan.json [--yes]

Watch the edit before any video is paid for. Each shot is its storyboard
frame held for the shot's used length, each title card a black card with its
words, in the order of the trailer clock (`clock_at` on shots and title cards,
written by the chain). Every dialogue line is read by a stand-in voice from the
account's ElevenLabs library, picked by the character's sex and age, and placed
at the shot's `clock_at` + `line_at`; that track is the key the music ducks
under. The plan's `sound` block is generated (or reused) and mixed exactly as
the final cut will be. Writes <out>/animatic.mp4, <out>/animatic-dialogue.wav
and <out>/soundtrack.wav.

The stand-in voices are only for timing and rhythm: in the film the shots
speak with Seedance's own voices.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import config
from .. import cost as cost_mod
from .. import drama
from ..errors import CostConfirmationDeclined, ProviderError, RunnerError
from . import _reel_sound

_FPS = 24
_FONT = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_animatic")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--fit-lines", action="store_true",
                        help="lengthen every speaking shot to its line (rounded to the beat), move the rest of the "
                             "cut and its sound later, and save the plan before building")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


# ── the clock ───────────────────────────────────────────────────────────────


def timeline(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Shots and title cards in clock order: {"kind", "at", "seconds", ...}."""
    items = [{"kind": "shot", "at": float(s["clock_at"]), "seconds": float(s["trim_seconds"]), "shot": s}
             for s in plan["shots"]]
    items += [{"kind": "card", "at": float(c["clock_at"]), "seconds": float(c["seconds"]), "text": c["text"], "card": c}
              for c in (plan.get("trailer") or {}).get("title_cards") or []]
    return sorted(items, key=lambda item: item["at"])


def lines(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Every dialogue line with where it starts on the clock."""
    out = []
    for shot in plan["shots"]:
        for line in shot.get("dialogue") or []:
            # eleven_v3 reads a leading [tag] as direction: "[flat, tired] I'm not Christopher Park."
            text = f"[{line['delivery']}] {line['line']}" if line.get("delivery") else line["line"]
            out.append({"who": line["who"], "line": text,
                        "at": round(float(shot["clock_at"]) + float(shot.get("line_at") or 0.3), 3)})
    return out


# ── stand-in voices ─────────────────────────────────────────────────────────


def _sex_age(identity: str) -> tuple[str, int]:
    sex = "female" if re.search(r"\b(woman|girl|female)\b", identity, re.I) else "male"
    age = re.search(r"\b(\d{2})\b", identity)
    return sex, int(age.group(1)) if age else 35


def _bucket(age: int) -> str:
    return "young" if age < 30 else "old" if age >= 55 else "middle_aged"


def pick_voices(cast: list[dict[str, Any]], library: list[dict[str, Any]]) -> dict[str, str]:
    """cast id → voice id: same sex, nearest age bucket, a different voice per character while any are left."""
    used: set[str] = set()
    chosen = {}
    for person in cast:
        sex, age = _sex_age(person.get("identity", ""))
        same_sex = [v for v in library if (v.get("labels") or {}).get("gender") == sex] or library
        # Telling two characters apart by ear matters more than an exact age match.
        ranked = sorted(same_sex, key=lambda v: (v["voice_id"] in used,
                                                  (v.get("labels") or {}).get("age") != _bucket(age)))
        chosen[person["id"]] = ranked[0]["voice_id"]
        used.add(ranked[0]["voice_id"])
    return chosen


def _library() -> list[dict[str, Any]]:
    from ..providers import _http

    resp = _http.get("eleven-tts", "https://api.elevenlabs.io/v1/voices",
                     headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]})
    voices = resp.json().get("voices") or []
    if not voices:
        raise RunnerError("the ElevenLabs account has no voices to stand in for the cast")
    return voices


def fit_lines(plan: dict[str, Any], bible: dict[str, Any], out: Path) -> dict[str, float]:
    """Read the lines, measure them, and conform the plan's cut to them; returns the shots that grew."""
    from . import _animatic_voice as av
    from . import _trailer_retime as rt

    groups = av.exchanges(plan)
    voices = av.voices_for(bible, {l["who"] for g in groups for l in g}, _library(), pick_voices)
    seconds = {}
    for group in groups:
        for line, clip in zip(group, av.read_exchange(group, voices, out / "animatic-lines", bible.get("language"), bible)):
            seconds[line["label"]] = seconds.get(line["label"], 0.0) + av._seconds(clip)
    lengths = rt.new_lengths(plan, seconds)
    rt.retime(plan, lengths)
    return lengths


def scratch_dialogue(plan: dict[str, Any], bible: dict[str, Any], total: float, out: Path) -> Path:
    """The trailer's lines in the cast's voices, exchanges read as one take, fitted to their shots, as one WAV."""
    from . import _animatic_voice as av

    groups = av.exchanges(plan)
    speakers = {line["who"] for group in groups for line in group}
    voices = av.voices_for(bible, speakers, _library(), pick_voices)
    cache, language = out.parent / "animatic-lines", bible.get("language")
    lines_, clips = [], []
    for group in groups:
        lines_ += group
        clips += av.read_exchange(group, voices, cache, language, bible)
    av.mix(av.fit(lines_, clips), total, out)
    return out


# ── picture ─────────────────────────────────────────────────────────────────


# Camera move named in the shot body → how the still moves: (zoom from, zoom to, pan x from, pan x to, shake).
_MOVES = [
    (r"crash[- ]zoom", (1.0, 1.0, 0.0, 0.0, 0)),  # handled as a late snap below
    (r"whip", (1.08, 1.08, -0.06, 0.0, 0)),
    (r"pull[- ]?back|pulls back|dolly out|zoom out", (1.18, 1.0, 0.0, 0.0, 0)),
    (r"push[- ]?in|pushes in|dolly in|creep|zoom in", (1.0, 1.15, 0.0, 0.0, 0)),
    (r"track(s|ing)? left|dolly left|truck left|pan left", (1.1, 1.1, 0.04, -0.04, 0)),
    (r"track|dolly|truck|pan|arc|orbit", (1.1, 1.1, -0.04, 0.04, 0)),
    (r"hand-?held|shak", (1.08, 1.1, 0.0, 0.0, 6)),
]


def camera_move(body: str) -> tuple[float, float, float, float, int, bool]:
    """(zoom0, zoom1, x0, x1, shake px, crash) for the first move the shot body names; a slow push otherwise."""
    text = body.lower()
    crash = bool(re.search(r"crash[- ]zoom", text))
    for pattern, move in _MOVES[1:]:
        if re.search(pattern, text):
            return (*move, crash)
    return (1.0, 1.05, 0.0, 0.0, 0, crash)


def _still(image: Path, seconds: float, out: Path, size: str, body: str = "") -> None:
    """The frame, moved the way the shot's camera moves — the cut reads in motion, not as a slideshow."""
    w, h = (int(v) for v in size.split("x"))
    z0, z1, x0, x1, shake, crash = camera_move(body)
    n = max(1, round(seconds * _FPS))
    prog = f"(on/{n})"
    zoom = f"({z0}+({z1}-{z0})*{prog})" + (f"*(1+0.35*gte(on,{int(n * 0.7)}))" if crash else "")
    x = f"(iw-iw/zoom)/2+iw*({x0}+({x1}-{x0})*{prog})" + (f"+{shake}*sin(on*1.7)" if shake else "")
    y = "(ih-ih/zoom)/2" + (f"+{shake}*cos(on*2.3)" if shake else "")
    vf = (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
          f"zoompan=z='{zoom}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={_FPS},setsar=1")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(image), "-vf", vf, "-frames:v", str(n),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out)], check=True, capture_output=True)


def _card(item: dict[str, Any], out: Path, size: str, plan: dict[str, Any]) -> None:
    """An animated title card in the film's identity (title_cards), on the beat of the act it sits in."""
    from .. import title_cards
    from . import _trailer_retime as rt

    card = item["card"]
    act = rt._act_of(plan).get(card.get("after", ""), "")
    w, h = (int(v) for v in size.split("x"))
    title_cards.render(title_cards.Card(card["text"], item["seconds"], bpm=rt.act_bpm(plan).get(act, 104.0),
                                        key=card.get("key"), label=card.get("label", "MATCH 98.7%"),
                                        size=(w, h)), out)


def picture(plan: dict[str, Any], board_dir: Path, out: Path) -> Path:
    """The cut as stills and cards, joined in clock order."""
    size = "1280x720" if (plan.get("board") or {}).get("aspect_ratio", "16:9") == "16:9" else "720x1280"
    frame_of = {int(f["shot"]): f["id"] for f in (plan.get("board") or {}).get("frames") or []}
    parts = []
    for n, item in enumerate(timeline(plan)):
        part = out.parent / f"animatic-part{n:03d}.mp4"
        if item["kind"] == "card":
            _card(item, part, size, plan)
        else:
            image = board_dir / f"{frame_of.get(int(item['shot']['index']), '')}.jpg"
            if not image.is_file():
                raise RunnerError(f"no storyboard frame for {item['shot']['label']}: run reel_board first")
            _still(image, item["seconds"], part, size, item["shot"].get("body", ""))
        parts.append(part)
    listing = out.parent / "animatic-parts.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(out)], check=True, capture_output=True)
    for p in [*parts, listing]:
        p.unlink()
    return out


# ── main ────────────────────────────────────────────────────────────────────


def run(args: argparse.Namespace) -> Path:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if not plan.get("sound") or not all("clock_at" in s for s in plan["shots"]):
        raise RunnerError("plan needs a `sound` block and `clock_at` on every shot; rerun the trailer chain")
    bible = drama.load_bible((args.plan_file.parent / plan["bible"]).resolve())
    out = Path(plan["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    if args.fit_lines:
        grew = fit_lines(plan, bible, out)
        args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Fit: {len(grew)} speaking shot(s) lengthened to their lines: "
              + ", ".join(f"{k} {v:.2f}s" for k, v in grew.items()), file=sys.stderr)
    total = float(plan["sound"]["total_seconds"])
    script = " ".join(l["line"] for l in lines(plan))
    estimate = _reel_sound.estimate(plan["sound"]) + (config.get_provider("eleven-tts").estimate_cost(text=script)
                                                       or Decimal("0"))
    cost_mod.confirm(estimate, yes=args.yes)

    pic = picture(plan, out / "board", out / "animatic-picture.mp4")
    dialogue = scratch_dialogue(plan, bible, total, out / "animatic-dialogue.wav")
    sources = _reel_sound.generate(plan["sound"], out, resume=True)
    soundtrack = _reel_sound.render(plan["sound"], sources, dialogue, out / "soundtrack.wav")
    final = out / "animatic.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pic), "-i", str(soundtrack), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(final)],
                   check=True, capture_output=True)
    pic.unlink()
    return final


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_providers()
    try:
        final = run(args)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (RunnerError, ProviderError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Animatic: {final}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
