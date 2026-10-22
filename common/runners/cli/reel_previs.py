"""Previs phase of a voiced film — the camera, designed in clay before any video.

  python3 -m common.runners.cli.reel_previs --plan-file <dir>/plan.json [--only s03,s04] [--auto-skip]

Reads plan["previs"] (written by the film chain), renders every shot's grey
blocking clip in Blender, headless — no cost, about a second of render per
second of film — and writes <dir>/previs/<label>.mp4, previs/contact.jpg
(first, middle and last frame of each shot, in order) and previs/animatic.mp4
(the clips cut exactly as the film will be, under the voice). Each shot then gets its
clip as @Video1 (`reference_videos`, uploaded through `media_host` on routes
that take only URLs). Watch the clips before paying for video: the camera,
the timing of every light and the blocking in them is what Seedance will do.
After rendering, each cast head is projected through the shot's camera (pure
Python, `previs.framing`): heads lost off the frame, cut at the edge of a close
shot or too small for the shot size named in the body are printed and written
to previs/framing.json; --auto-skip sets "no_previs" on those shots so the
storyboard keyframe leads instead. A shot with "open_on_frame" opens on its storyboard frame and takes no
previs: it is neither rendered nor handed a clip.

Nothing is rendered twice: previs/cache.json stamps each clip with the key of its job entry (camera, lens,
set, actors, length, frame size, the scene script), and a rerun sends Blender only the shots whose key moved;
the contact sheet and the cut are made again only when a clip, a trim or the voice changed.

Blender is found through $BLENDER, then `blender` on PATH, then the macOS
application bundle.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .. import config
from .. import ffmpeg_film
from .. import previs as pv
from ..errors import RunnerError
from . import _stage_cache as sc

_SCENE = Path(__file__).resolve().parents[1] / "blender" / "previs_scene.py"
_MAC = Path("/Applications/Blender.app/Contents/MacOS/Blender")
_SIZE = {"9:16": (480, 854), "16:9": (854, 480), "1:1": (640, 640), "4:5": (512, 640)}
_FPS = 24


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_previs")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--only", help="comma-separated shot labels to render (default: all); an unchanged clip is reused")
    parser.add_argument("--review", action="store_true",
                        help="have a vision model read each clip against its shot (a fraction of a cent per shot) "
                             "and write previs/review.json")
    parser.add_argument("--auto-skip", action="store_true",
                        help="set \"no_previs\": true on shots whose framing check flags a cast head lost, cut "
                             "or too small, so the storyboard keyframe leads instead (default: only report)")
    return parser


def blender_binary() -> str:
    for candidate in (os.environ.get("BLENDER"), shutil.which("blender"), str(_MAC) if _MAC.is_file() else None):
        if candidate:
            return candidate
    raise RunnerError("Blender not found: install it or set BLENDER to its executable")


def _wanted(entry: dict[str, Any], labels: set[str] | None) -> bool:
    """A shot to render: asked for (or all are), and not one that opens on its storyboard frame."""
    return not entry.get("open_on_frame") and (not labels or entry["label"] in labels)


def job(plan: dict[str, Any], out_dir: Path, labels: set[str] | None) -> dict[str, Any]:
    """The JSON the Blender script renders from: one entry per shot, keys expanded."""
    spec = plan["previs"]
    shots = []
    for entry in sorted(plan["shots"], key=lambda e: int(e["index"])):
        label = entry["label"]
        shot = spec["shots"].get(label)
        if not shot or not _wanted(entry, labels):
            continue
        shots.append({
            "label": label,
            "seconds": float((entry.get("kwargs") or {}).get("duration_seconds") or 5),
            "frames": str(out_dir / f"{label}-frames"),
            "props": spec["sets"][shot["set"]],
            "camera": pv.camera_keys(shot),
            "lens": shot.get("lens", 24),
            "shake": shot.get("shake", 0),
            "hero": shot.get("hero") or [],
            "actors": shot.get("actors") or [],
            "fire": shot.get("fire") or [],
            "extra": shot.get("extra") or [],
        })
    aspect = (plan["shots"][0].get("kwargs") or {}).get("aspect_ratio", "9:16")
    return {"size": _SIZE.get(aspect, _SIZE["9:16"]), "fps": _FPS, "shots": shots}


def _encode(frames: Path, out: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(_FPS), "-i", str(frames / "f%04d.jpg"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)],
                   check=True, capture_output=True)
    shutil.rmtree(frames)


def _contact(clips: list[tuple[Path, int]], out: Path) -> None:
    """Three frames per shot (start, middle, end), one row per shot."""
    inputs = [a for clip, _ in clips for a in ("-i", str(clip))]
    rows = []
    for i, (_, frames) in enumerate(clips):
        last = max(0, frames - 2)
        pick = f"eq(n\\,0)+eq(n\\,{last // 2})+eq(n\\,{last})"
        rows.append(f"[{i}:v]select='{pick}',scale=144:256,setsar=1,tile=3x1[r{i}]")
    stack = "".join(f"[r{i}]" for i in range(len(clips)))
    graph = ";".join(rows) + (f";{stack}vstack=inputs={len(clips)}[out]" if len(clips) > 1 else "")
    label = "[out]" if len(clips) > 1 else "[r0]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
                    "-map", label, "-frames:v", "1", "-fps_mode", "passthrough", str(out)],
                   check=True, capture_output=True)


def _check(plan: dict[str, Any]) -> None:
    if not plan.get("previs"):
        raise RunnerError("plan has no previs; rerun the film chain")
    durations = {e["label"]: float((e.get("kwargs") or {}).get("duration_seconds") or 5) for e in plan["shots"]}
    problems = pv.validate(plan["previs"], durations)
    if problems:
        raise RunnerError("previs spec has problems:\n  " + "\n  ".join(problems))


def _shot_key(shot: dict[str, Any], spec: dict[str, Any]) -> str:
    """A clip's cache key: everything Blender draws it from (its job entry, the frame size and rate, the scene
    script) — not the folder its frames go to, and not the shot's trim, which only the cut uses."""
    return sc.key({k: v for k, v in shot.items() if k != "frames"}, spec["size"], spec["fps"],
                  sc.file_sig(_SCENE)[1:])


def _stale(spec: dict[str, Any], out_dir: Path, stamps: sc.Stamps) -> dict[str, Any]:
    """The job cut down to the shots whose clip is missing or whose spec changed since it was rendered."""
    todo = [s for s in spec["shots"] if not stamps.fresh(s["label"], _shot_key(s, spec), out_dir / f"{s['label']}.mp4")]
    reused = len(spec["shots"]) - len(todo)
    if reused:
        print(f"Previs: {reused} clip(s) unchanged since their render, reused", file=sys.stderr)
    return {**spec, "shots": todo}


def _blender(spec: dict[str, Any], out_dir: Path, stamps: sc.Stamps | None = None) -> None:
    """Render the shots that need it headless, then encode each shot's frames to <label>.mp4."""
    stamps = stamps or sc.Stamps(out_dir / "cache.json")
    spec = _stale(spec, out_dir, stamps)
    if not spec["shots"]:
        return
    job_path = out_dir / "job.json"
    job_path.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    print(f"Previs: rendering {len(spec['shots'])} shot(s) in Blender…", file=sys.stderr)
    done = subprocess.run([blender_binary(), "-b", "--factory-startup", "--python", str(_SCENE), "--",
                           str(job_path)], capture_output=True, text=True)
    if done.returncode != 0 or "Traceback" in done.stderr + done.stdout:
        tail = (done.stderr or done.stdout)[-1500:]
        raise RunnerError(f"Blender failed:\n{tail}")
    for shot in spec["shots"]:
        _encode(Path(shot["frames"]), out_dir / f"{shot['label']}.mp4")
        stamps.set(shot["label"], _shot_key(shot, spec))
    stamps.save()


def _hand_clips(plan: dict[str, Any], out_dir: Path) -> list[tuple[Path, int]]:
    """Give each previs'd shot its clip as @Video1; the clips with their frame counts, in film order."""
    clips = []
    for entry in sorted(plan["shots"], key=lambda e: int(e["index"])):
        clip = out_dir / f"{entry['label']}.mp4"
        if entry["label"] in plan["previs"]["shots"] and clip.is_file() and not entry.get("open_on_frame"):
            kwargs = entry.setdefault("kwargs", {})
            if entry.get("no_previs"):
                # a still camera's clip is read as footage to edit, and the vendor wants the source's length
                # and ratio back: the shot keeps its previs for the animatic but goes without it
                kwargs.pop("reference_videos", None)
            else:
                kwargs["reference_videos"] = [str(clip)]
                kwargs.setdefault("media_host", "litterbox")
            clips.append((clip, round(float(kwargs.get("duration_seconds") or 5) * _FPS)))
    return clips


def _animatic(plan: dict[str, Any], out_dir: Path) -> bool:
    """The previs cut exactly as the film will be, with the voice: watch this before paying. False when a shot
    has no clip, so there is no cut to make."""
    shots = sorted(plan["shots"], key=lambda e: int(e["index"]))
    clips = [out_dir / f"{e['label']}.mp4" for e in shots]
    if not all(c.is_file() for c in clips):
        return False
    cuts = [(c, float(e.get("trim_seconds") or 5), float(e.get("trim_start") or 0)) for c, e in zip(clips, shots)]
    picture = out_dir / "animatic-picture.mp4"
    ffmpeg_film.concat_trimmed(cuts, picture)
    voice = Path((plan.get("voiceover") or {}).get("path") or "")
    if voice.is_file():
        ffmpeg_film.mux(picture, voice, out_dir / "animatic.mp4")
        picture.unlink()
    else:
        picture.replace(out_dir / "animatic.mp4")
    return True


def _derived(plan: dict[str, Any], out_dir: Path, clips: list[tuple[Path, int]], stamps: sc.Stamps) -> None:
    """The contact sheet and the previs cut, each made again only when what it is made from changed: the
    clips (and for the cut, every shot's trim and the voice)."""
    contact, cut = out_dir / "contact.jpg", out_dir / "animatic.mp4"
    contact_key = sc.key([(sc.file_sig(c), n) for c, n in clips])
    shots = sorted(plan["shots"], key=lambda e: int(e["index"]))
    cut_key = sc.key([(sc.file_sig(out_dir / f"{e['label']}.mp4"), e.get("trim_seconds"), e.get("trim_start"))
                      for e in shots], sc.file_sig((plan.get("voiceover") or {}).get("path") or ""))
    kept = []
    if stamps.fresh(contact.name, contact_key, contact):
        kept.append(contact.name)
    else:
        _contact(clips, contact)
        stamps.set(contact.name, contact_key)
    if stamps.fresh(cut.name, cut_key, cut):
        kept.append(cut.name)
    elif _animatic(plan, out_dir):
        stamps.set(cut.name, cut_key)
    if kept:
        print(f"Previs: {' and '.join(kept)} unchanged, kept", file=sys.stderr)
    stamps.save()


_REVIEW = """You are checking one shot of a clay previs (blocking: the people are coloured figures — big round heads, ears, a hair shape, arms — or, in older films, one brown figure with a black hat; boxes and cylinders are the set and its props; blocks flashing pale yellow are lights or effects firing. The image shows three separate frames of the same shot, left to right with white gaps between them: start, middle, end. A figure appearing in each of the three panels is the same hero at three moments, not a duplicate.

The shot is meant to be: {move} — {intent}
Lip-sync shot (his face must be readable while he speaks): {lip}

Return JSON only: {{"readable":0,"face":0,"issues":["..."],"fix":"one concrete change to camera keys, lens or props"}}
readable 0-10: can a viewer tell what is in frame and what the camera does (0 if a frame is mostly one flat colour, blown white, or the lens is inside or against an object; low if the hero appears twice).
face 0-10: for a lip-sync shot, is his face (the round head with the dark glasses) frontal or three-quarter and large enough in the middle frame; 10 if not a lip-sync shot."""


def _review(plan: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    """Each clip's start, middle and end, read by a vision model against what the shot is meant to be."""
    from ..providers.openrouter_image import judge

    report = {}
    for entry in sorted(plan["shots"], key=lambda e: int(e["index"])):
        clip, shot = out_dir / f"{entry['label']}.mp4", plan["previs"]["shots"].get(entry["label"])
        if not shot or not clip.is_file():
            continue
        strip = out_dir / f"{entry['label']}-review.jpg"
        frames = round(float(entry["kwargs"].get("duration_seconds") or 5) * _FPS)
        pick = f"eq(n\\,2)+eq(n\\,{frames // 2})+eq(n\\,{frames - 3})"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vf",
                        f"select='{pick}',scale=240:-1,tile=3x1:padding=12:color=white", "-frames:v", "1", "-fps_mode", "passthrough",
                        str(strip)], check=True, capture_output=True)
        verdict = judge(_REVIEW.format(move=shot.get("move_id", "?"), intent=entry["prompt"][:700],
                                       lip=bool(entry.get("lip_sync"))), [str(strip)])
        strip.unlink()
        report[entry["label"]] = {k: verdict.get(k) for k in ("readable", "face", "issues", "fix")}
        print(f"  {entry['label']}: readable {verdict.get('readable')}/10, face {verdict.get('face')}/10  "
              f"{'; '.join(verdict.get('issues') or [])[:150]}", file=sys.stderr)
    (out_dir / "review.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return report


def _framing(plan: dict[str, Any], out_dir: Path, labels: set[str] | None, skip: bool) -> dict[str, list[str]]:
    """Check where each cast head lands: previs/framing.json gets every flagged shot of the plan; the shots
    just rendered are printed and, with `skip`, taken off their previs."""
    report = pv.framing(plan)
    (out_dir / "framing.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    flags = {k: v for k, v in report.items() if not labels or k in labels}
    for label, problems in flags.items():
        more = f" (+{len(problems) - 3} more)" if len(problems) > 3 else ""
        print(f"  framing {label}: {'; '.join(problems[:3])}{more}", file=sys.stderr)
    if skip:
        for entry in plan["shots"]:
            if entry["label"] in flags:
                entry["no_previs"] = True
    verb = "set no_previs on" if skip else "flagged (--auto-skip drops their previs)"
    print(f"Previs framing: {len(flags)} shot(s) {verb}; {out_dir / 'framing.json'}", file=sys.stderr)
    return flags


def _save(path: Path, plan: dict[str, Any]) -> None:
    """Write the plan through a temporary file, so a crash never leaves half a plan; an unchanged plan is not
    rewritten."""
    sc.save_json(path, plan)


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    _check(plan)
    out_dir = Path(plan["output_dir"]) / "previs"
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = set((args.only or "").split(",")) - {""} or None
    stamps = sc.Stamps(out_dir / "cache.json")
    _blender(job(plan, out_dir, labels), out_dir, stamps)
    _framing(plan, out_dir, labels, getattr(args, "auto_skip", False))

    clips = _hand_clips(plan, out_dir)
    if clips:
        _derived(plan, out_dir, clips, stamps)
        if args.review:
            _review(plan, out_dir)
    _save(args.plan_file, plan)
    return {"clips": [c for c, _ in clips], "contact": out_dir / "contact.jpg"}


def main() -> int:
    args = build_parser().parse_args()
    if args.review:
        config.load_all_providers()  # loads the keys file the reviewer needs
    try:
        report = run(args)
    except (RunnerError, subprocess.CalledProcessError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Previs: {len(report['clips'])} clip(s); {report['contact']}; "
          f"{report['contact'].with_name('animatic.mp4')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
