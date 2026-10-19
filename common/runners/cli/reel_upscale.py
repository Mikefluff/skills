"""Upscale a film's rendered clips before the cut — 480p generations to twice their size, locally.

  python3 -m common.runners.cli.reel_upscale --plan-file <dir>/plan.json [--only t21,t30]

Every clip the cut uses (the reel manifest's, and a shot's own hand-cut "clip") goes through Real-ESRGAN's
realesr-animevideov3 model (made for animation; ncnn/Vulkan, runs on Apple silicon, nothing is paid) at 2x
and is written to <dir>/shots/hd/<name>.mp4 with its sound copied. A clip already upscaled is skipped. Set
"hd": true in the plan and `reel_animatic --clips` cuts from these at 1920x1080.

The binary is found through $REALESRGAN, then `realesrgan-ncnn-vulkan` on PATH, then ~/tools/realesrgan.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from ..errors import RunnerError
from . import reel_animatic

_MODEL = "realesr-animevideov3"
_FPS = 24


def binary() -> str:
    found = os.environ.get("REALESRGAN") or shutil.which("realesrgan-ncnn-vulkan")
    fallback = Path.home() / "tools" / "realesrgan" / "realesrgan-ncnn-vulkan"
    if found:
        return found
    if fallback.is_file():
        return str(fallback)
    raise RunnerError("Real-ESRGAN not found: set $REALESRGAN or install realesrgan-ncnn-vulkan")


def hd_path(clip: Path) -> Path:
    return clip.parent / "hd" / clip.name if clip.parent.name != "hd" else clip


def upscale(clip: Path, exe: str) -> Path:
    out = hd_path(clip)
    if out.is_file():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp, "in"), Path(tmp, "out")
        src.mkdir(), dst.mkdir()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vf", f"fps={_FPS}",
                        str(src / "f%05d.png")], check=True, capture_output=True)
        # the model directory sits next to the binary
        subprocess.run([exe, "-i", str(src), "-o", str(dst), "-n", _MODEL, "-s", "2", "-f", "png",
                        "-m", str(Path(exe).parent / "models")], check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(_FPS), "-i", str(dst / "f%05d.png"),
                        "-i", str(clip), "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "16",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", str(out)], check=True, capture_output=True)
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel_upscale")
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--only", help="comma-separated shot labels (default: every clip the cut uses)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    only = set((args.only or "").split(",")) - {""}
    try:
        exe = binary()
        clips = {k: v for k, v in reel_animatic.rendered(plan, hd=False).items() if not only or k in only}
        for n, (label, clip) in enumerate(sorted(clips.items()), 1):
            done = hd_path(clip).is_file()
            upscale(clip, exe)
            print(f"  {n}/{len(clips)} {label}{' (cached)' if done else ''}", file=sys.stderr)
    except (RunnerError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Upscaled: {len(clips)} clip(s) in {Path(plan['output_dir']) / 'shots' / 'hd'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
