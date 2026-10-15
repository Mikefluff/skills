"""Previs phase of a voiced film — the camera, designed in clay before any video.

  python3 -m common.runners.cli.reel_previs --plan-file <dir>/plan.json [--only s03,s04]

Reads plan["previs"] (written by the film chain), renders every shot's grey
blocking clip in Blender, headless — no cost, about a second of render per
second of film — and writes <dir>/previs/<label>.mp4, previs/contact.jpg
(first, middle and last frame of each shot, in order) and previs/animatic.mp4
(the clips cut exactly as the film will be, under the voice). Each shot then gets its
clip as @Video1 (`reference_videos`, uploaded through `media_host` on routes
that take only URLs). Watch the clips before paying for video: the camera,
the timing of every light and the blocking in them is what Seedance will do.

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

_SCENE = Path(__file__).resolve().parents[1] / "blender" / "previs_scene.py"
_MAC = Path("/Applications/Blender.app/Contents/MacOS/Blender")
_SIZE = {"9:16": (480, 854), "16:9": (854, 480), "1:1": (640, 640), "4:5": (512, 640)}
_FPS = 24


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_previs")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--only", help="comma-separated shot labels to render (default: all)")
    parser.add_argument("--review", action="store_true",
                        help="have a vision model read each clip against its shot (a fraction of a cent per shot) "
                             "and write previs/review.json")
    return parser


def blender_binary() -> str:
    for candidate in (os.environ.get("BLENDER"), shutil.which("blender"), str(_MAC) if _MAC.is_file() else None):
        if candidate:
            return candidate
    raise RunnerError("Blender not found: install it or set BLENDER to its executable")


def job(plan: dict[str, Any], out_dir: Path, labels: set[str] | None) -> dict[str, Any]:
    """The JSON the Blender script renders from: one entry per shot, keys expanded."""
    spec = plan["previs"]
    shots = []
    for entry in sorted(plan["shots"], key=lambda e: int(e["index"])):
        label = entry["label"]
        shot = spec["shots"].get(label)
        if not shot or (labels and label not in labels):
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


def _blender(spec: dict[str, Any], out_dir: Path) -> None:
    """Render the job headless, then encode each shot's frames to <label>.mp4."""
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


def _hand_clips(plan: dict[str, Any], out_dir: Path) -> list[tuple[Path, int]]:
    """Give each previs'd shot its clip as @Video1; the clips with their frame counts, in film order."""
    clips = []
    for entry in sorted(plan["shots"], key=lambda e: int(e["index"])):
        clip = out_dir / f"{entry['label']}.mp4"
        if entry["label"] in plan["previs"]["shots"] and clip.is_file():
            kwargs = entry.setdefault("kwargs", {})
            kwargs["reference_videos"] = [str(clip)]
            kwargs.setdefault("media_host", "litterbox")
            clips.append((clip, round(float(kwargs.get("duration_seconds") or 5) * _FPS)))
    return clips


def _animatic(plan: dict[str, Any], out_dir: Path) -> None:
    """The previs cut exactly as the film will be, with the voice: watch this before paying."""
    shots = sorted(plan["shots"], key=lambda e: int(e["index"]))
    clips = [out_dir / f"{e['label']}.mp4" for e in shots]
    if not all(c.is_file() for c in clips):
        return
    cuts = [(c, float(e.get("trim_seconds") or 5), float(e.get("trim_start") or 0)) for c, e in zip(clips, shots)]
    picture = out_dir / "animatic-picture.mp4"
    ffmpeg_film.concat_trimmed(cuts, picture)
    voice = Path((plan.get("voiceover") or {}).get("path") or "")
    if voice.is_file():
        ffmpeg_film.mux(picture, voice, out_dir / "animatic.mp4")
        picture.unlink()
    else:
        picture.replace(out_dir / "animatic.mp4")


_REVIEW = """You are checking one shot of a clay previs (grey blocking: the brown figure with a black hat is the hero; boxes are decks, truss, lights; lit white blocks are lights firing). The image shows three separate frames of the same shot, left to right with white gaps between them: start, middle, end. A figure appearing in each of the three panels is the same hero at three moments, not a duplicate.

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


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    _check(plan)
    out_dir = Path(plan["output_dir"]) / "previs"
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = set((args.only or "").split(",")) - {""} or None
    _blender(job(plan, out_dir, labels), out_dir)

    clips = _hand_clips(plan, out_dir)
    if clips:
        _contact(clips, out_dir / "contact.jpg")
        _animatic(plan, out_dir)
        if args.review:
            _review(plan, out_dir)
    args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
