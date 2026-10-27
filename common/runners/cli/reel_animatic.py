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

With --clips the same clock is cut from the rendered shots instead (the reel
manifest, or a shot's own "clip" for a composite cut by hand), and a shot not
yet rendered stays its storyboard frame, so a half-rendered trailer can be
watched. A speaking shot is trimmed where its mouth opens on the cast's line:
the generation speaks the line with its own voice, Scribe finds when (cached in
shots/mouths.json), and the trim puts that moment where the cast's take plays.
The plan's "grade" is laid on every clip. Writes <out>/trailer.mp4.

Each part of the picture (a clip's window with its transitions and grade, a still, a card) is encoded once
into <out>/parts/ and reused while nothing that makes it changes; the join is a stream copy (_animatic_parts).
The picture's signature, its parts' keys in order, is written next to the cut (<cut>.picture.json).

  python3 -m common.runners.cli.reel_animatic --plan-file <plan> --clips --audio-only --yes

--audio-only rebuilds the sound alone, exactly as the full run makes it (the lines on the same mouth marks
and fit, the vocals, the soundtrack and its mix), and lays it on the picture already in trailer.mp4 (or
animatic.mp4), its video stream copied. It is refused, naming the shots that changed, when the plan no longer
makes that picture: a trim, a window, a transition, a card, the grade, a new take. The plan is never saved
by it; a cut the lines would tighten is refused too, and --fit-lines with it is an error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from .. import config
from .. import cost as cost_mod
from .. import drama
from ..errors import CostConfirmationDeclined, ProviderError, RunnerError
from . import _reel_sound
from ._animatic_clips import (  # noqa: F401 — re-exported, the module's public names
    _length, clip_start, mouth_at, mouth_marks, rendered, speech, tighten,
)
from ._animatic_mix import land_punchlines, snap_to_action, with_places, with_vocals  # noqa: F401
from ._animatic_parts import cut_parts, picture  # noqa: F401
from ._animatic_picture import (  # noqa: F401
    _FONT, _FPS, _MOVES, Takes, Window, _bars, _card, _clip_part, _still, camera_move, frame_aligned, timeline,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_animatic")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--fit-lines", action="store_true",
                        help="lengthen every speaking shot to its line (rounded to the beat), move the rest of the "
                             "cut and its sound later, and save the plan before building")
    parser.add_argument("--clips", action="store_true",
                        help="cut the rendered shots (storyboard frames where none is rendered yet) into trailer.mp4")
    parser.add_argument("--audio-only", action="store_true",
                        help="rebuild only the sound and lay it on the picture already built; refused when the "
                             "plan no longer makes that picture")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    return parser


# ── the clock ───────────────────────────────────────────────────────────────


def lines(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Every dialogue line with where it starts on the clock."""
    out = []
    for shot in plan["shots"]:
        if shot.get("cut"):
            continue
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


def fit_lines(plan: dict[str, Any], bible: dict[str, Any], out: Path, clips: bool = False) -> dict[str, float]:
    """Read the lines, measure them, and conform the plan's cut to them; returns the shots that grew. With
    `clips` a rendered shot only grows, and no further than its take runs."""
    from . import _animatic_voice as av
    from . import _trailer_retime as rt

    groups = av.exchanges(plan)
    voices = av.voices_for(bible, {l["who"] for g in groups for l in g}, _library(), pick_voices)
    seconds = {}
    for group in groups:
        for line, clip in zip(group, av.read_exchange(group, voices, out / "animatic-lines", bible.get("language"), bible)):
            seconds[line["label"]] = seconds.get(line["label"], 0.0) + av._seconds(clip)
    limits = None
    if clips:
        takes = rendered(plan, hd=False)
        limits = {s["label"]: av._seconds(takes[s["label"]]) - float(s.get("trim_start") or 0)
                  for s in plan["shots"] if s["label"] in takes}
    lengths = rt.new_lengths(plan, seconds, limits)
    rt.retime(plan, lengths)
    return lengths


def _place(plan: dict[str, Any], bible: dict[str, Any],
           marks: dict[str, tuple[float, float, float]] | None = None) -> list[tuple[dict[str, Any], Path, float, float]]:
    """Every line read in the cast's voices (exchanges as one take) and fitted to its shot: (line, clip, start
    on the clock, tempo) in clock order. Nothing is mixed."""
    from . import _animatic_voice as av

    groups = av.exchanges(plan)
    speakers = {line["who"] for group in groups for line in group}
    voices = av.voices_for(bible, speakers, _library(), pick_voices)
    cache, language = Path(plan["output_dir"]) / "animatic-lines", bible.get("language")
    lines_, clips = [], []
    for group in groups:
        lines_ += group
        clips += av.read_exchange(group, voices, cache, language, bible)
    for line in lines_:
        if line["label"] in (marks or {}):
            # the rendered shot's mouth: the line starts there and is pressed to its length
            _, at, seconds = marks[line["label"]]
            # the line starts on the mouth but may run on to its shot's end: a take pressed to the generation's
            # own (fast) speech lost its acting, every line at the 1.25x cap
            to_end = line["at"] + line["room"] - at
            line["at"], line["room"] = at, max(max(seconds, 0.3) + 0.15, to_end)
    placed = av.fit(lines_, clips, say=False)
    return [(line, *spot) for line, spot in zip(sorted(lines_, key=lambda l: l["at"]), placed)]


def _ends(placed: list[tuple[dict[str, Any], Path, float, float]]) -> dict[str, float]:
    """label → where the speaking shot's last word ends on the clock."""
    from . import _animatic_voice as av

    return {line["label"]: round(at + av._seconds(clip) / tempo, 3) for line, clip, at, tempo in placed}


def _mix_lines(placed: list[tuple[dict[str, Any], Path, float, float]], bible: dict[str, Any], total: float,
               out: Path) -> dict[str, float]:
    """The placed lines as one WAV of the cut's length; returns where each speaking shot's first line starts."""
    from . import _animatic_voice as av

    for line, _, _, tempo in placed:
        av.say_rushed(line, tempo)
    av.mix([spot for _, *spot in placed], total, out, [av.gain_db(line) for line, *_ in placed],
           [(av.voice_pitch(bible, line["who"]), av.voice_formant(bible, line["who"])) for line, *_ in placed])
    onsets: dict[str, float] = {}
    for line, _, at, _ in placed:
        onsets.setdefault(line["label"], at)
    return onsets


def scratch_dialogue(plan: dict[str, Any], bible: dict[str, Any], total: float, out: Path,
                     marks: dict[str, tuple[float, float, float]] | None = None) -> tuple[Path, dict[str, float]]:
    """The trailer's lines in the cast's voices, exchanges read as one take, fitted to their shots, as one WAV;
    with where each speaking shot's first line starts on the clock."""
    placed = _place(plan, bible, marks)
    scratch_dialogue.ends = _ends(placed)  # where each speaking shot's last word ends, for tighten()
    return out, _mix_lines(placed, bible, total, out)


# ── main ────────────────────────────────────────────────────────────────────


def _save(args: argparse.Namespace, plan: dict[str, Any]) -> None:
    """The plan written back, only when it changed; never by --audio-only (a change is a picture build)."""
    from ._stage_cache import save_json

    if not getattr(args, "audio_only", False):
        save_json(args.plan_file, plan)


def _load(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """The plan, its bible and its output dir; with --fit-lines, the cut conformed to its lines and saved."""
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if not plan.get("sound") or not all("clock_at" in s for s in plan["shots"]):
        raise RunnerError("plan needs a `sound` block and `clock_at` on every shot; rerun the trailer chain")
    bible = drama.load_bible((args.plan_file.parent / plan["bible"]).resolve())
    out = Path(plan["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    if args.fit_lines:
        grew = fit_lines(plan, bible, out, clips=args.clips)
        _save(args, plan)
        print(f"Fit: {len(grew)} speaking shot(s) lengthened to their lines: "
              + ", ".join(f"{k} {v:.2f}s" for k, v in grew.items()), file=sys.stderr)
    return plan, bible, out


def _confirm(plan: dict[str, Any], bible: dict[str, Any], yes: bool) -> None:
    """Asks only for what this run buys: a cut whose takes, vocals and sounds are all kept asks nothing."""
    from . import _animatic_voice as av
    from ._animatic_mix import to_buy

    speakers = {line["who"] for group in av.exchanges(plan) for line in group} | {
        v["who"] for v in plan.get("vocals") or []} - {"crowd"}
    estimate, what = to_buy(plan, bible, av.voices_for(bible, speakers, _library(), pick_voices))
    if estimate > 0:
        print(f"To buy: {', '.join(what)}", file=sys.stderr)
        cost_mod.confirm(estimate, yes=yes)


def _dialogue(args: argparse.Namespace, plan: dict[str, Any], bible: dict[str, Any], out: Path,
              takes: Takes) -> Path:
    """The scratch dialogue on the cut's clock, mixed once; fills the takes' marks and onsets."""
    takes.marks = mouth_marks(plan, takes.clips)
    placed = _place(plan, bible, takes.marks)
    if args.clips and tighten(plan, _ends(placed), takes.clips):
        # dead air after the last word cut away: the clock moved, so the lines are laid again on it
        _save(args, plan)
        takes.marks = mouth_marks(plan, takes.clips)
        placed = _place(plan, bible, takes.marks)
    dialogue = out / "animatic-dialogue.wav"
    takes.onsets = _mix_lines(placed, bible, float(plan["sound"]["total_seconds"]), dialogue)
    return dialogue


def _narrate(plan: dict[str, Any], bible: dict[str, Any], dialogue: Path, out: Path) -> None:
    """The narrator joins the dialogue track: the score ducks under him as under any line."""
    if not plan.get("narration"):
        return
    from . import _animatic_voice as av
    from . import _drama_pass as dp

    who = plan.get("narrator") or "minh"
    speakers = {who} | {n["who"] for n in plan["narration"] if n.get("who")}
    voices = av.voices_for(bible, speakers, [], lambda rest, lib: {})
    dp.mix_narration(dialogue, dp.narration_files(plan, voices, out))


def _build(args: argparse.Namespace, plan: dict[str, Any], takes: Takes) -> None:
    """The trailer's build: an act accelerating into a strobe, recut and saved."""
    build = (plan.get("trailer") or {}).get("build")
    if not (args.clips and build):
        return
    from .. import shot_matrix
    from . import _trailer_retime as rt
    from . import _trailer_sound as ts

    breath = ts._breath(plan)
    added = rt.accelerate(plan, build["act"], breath[0] if breath else float(plan["sound"]["total_seconds"]),
                          build.get("strobe") or [], takes.clips, shot_matrix.speed)
    takes.clips = rendered(plan)
    _save(args, plan)
    print(f"Build: {build['act']} accelerates into a strobe of {len(added)}", file=sys.stderr)


def _soundtrack(args: argparse.Namespace, plan: dict[str, Any], bible: dict[str, Any], out: Path,
                takes: Takes) -> tuple[dict[str, Any], dict[str, Path]]:
    """The cut's sound and its sources; against the rendered clips, snapped, punchlines landed, decluttered."""
    sound = (with_places(plan, bible, takes.used or []) if args.clips
             else with_vocals(json.loads(json.dumps(plan["sound"])), plan, bible))
    sources = _reel_sound.generate(sound, out, resume=True)
    sources.update(sound.pop("_files", {}))
    if args.clips:
        snap_to_action(sound, sources)
        cuts = sorted(float(x["clock_at"]) + float(x["trim_seconds"]) for x in plan["shots"] if not x.get("cut"))
        land_punchlines(sound, sorted(takes.onsets.values()),
                        resume_at=lambda line: next((c for c in cuts if c > line + 0.3), None))
        from . import _trailer_sound as ts

        ts.declutter(sound, plan)
    return sound, sources


def _mux(pic: Path, soundtrack: Path, final: Path) -> None:
    """The picture's video stream copied, the soundtrack laid under it, into `final` (whole or not at all)."""
    work = final.with_name(f"{final.stem}.mux{final.suffix}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pic), "-i", str(soundtrack), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(work)],
                   check=True, capture_output=True)
    work.replace(final)


def _still_fresh(plan: dict[str, Any], out: Path, final: Path, takes: Takes) -> list:
    """--audio-only: the parts the plan makes now, refused unless they are the picture in `final`."""
    from . import _animatic_parts as parts

    made = cut_parts(plan, out / "board", takes)
    parts.fresh(final, made)
    return made


def run(args: argparse.Namespace) -> Path:
    from . import _animatic_parts as parts

    plan, bible, out = _load(args)
    _confirm(plan, bible, args.yes)
    takes = Takes(clips=rendered(plan) if args.clips else {}, used=[])
    final = out / ("trailer.mp4" if args.clips else "animatic.mp4")
    if args.audio_only:
        # before any sound is made: a stale picture is refused without spending on its lines
        _still_fresh(plan, out, final, Takes(clips=takes.clips, marks=mouth_marks(plan, takes.clips)))
    dialogue = _dialogue(args, plan, bible, out, takes)
    _narrate(plan, bible, dialogue, out)
    _build(args, plan, takes)
    if args.audio_only:
        made, pic = _still_fresh(plan, out, final, takes), final  # the lines may have moved the cut since
    else:
        made = cut_parts(plan, out / "board", takes)
        pic = parts.render(made, out / "animatic-picture.mp4")
    sound, sources = _soundtrack(args, plan, bible, out, takes)
    soundtrack = _reel_sound.render(sound, sources, dialogue, out / "soundtrack.wav")
    parts.signature_file(final).unlink(missing_ok=True)
    _mux(pic, soundtrack, final)
    parts.record(final, made)
    if not args.audio_only:
        pic.unlink()
    return final


def main() -> int:
    args = build_parser().parse_args()
    if args.audio_only and args.fit_lines:
        print("--fit-lines moves the cut: it needs a picture build, not --audio-only", file=sys.stderr)
        return 1
    config.load_all_providers()
    try:
        final = run(args)
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (RunnerError, ProviderError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"{'Trailer' if final.name == 'trailer.mp4' else 'Animatic'}: {final}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
