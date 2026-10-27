"""Upscale clips as they land — a film with "hd": true gets each newly rendered shot through Real-ESRGAN (see
reel_upscale) right after `reel` renders it, so the cut never waits on a batch upscale. Clips carried over
from an earlier run are left to `reel_upscale`; without the binary this is one line and nothing else."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from ..errors import RunnerError


def fresh_clips(items: list[Any]) -> list[Path]:
    """Clips this run rendered: succeeded items that went to the provider (a resumed one never started)."""
    return [Path(i.output_path) for i in items
            if i.status == "succeeded" and i.started_at is not None and i.output_path]


def upscale_new(plan: dict[str, Any], items: list[Any]) -> int:
    """How many of this run's clips now have an upscaled copy in shots/hd/."""
    clips = fresh_clips(items) if plan.get("hd") else []
    if not clips:
        return 0
    from . import reel_upscale

    try:
        exe = reel_upscale.binary()
    except RunnerError as exc:
        print(f"  hd: {exc} — clips left at render size", file=sys.stderr)
        return 0
    done = 0
    for clip in clips:
        try:
            reel_upscale.upscale(clip, exe)
            done += 1
        except subprocess.CalledProcessError as exc:
            print(f"  hd: {clip.name} not upscaled ({exc.cmd[0]} failed)", file=sys.stderr)
    print(f"  hd: {done}/{len(clips)} new clip(s) upscaled", file=sys.stderr)
    return done
