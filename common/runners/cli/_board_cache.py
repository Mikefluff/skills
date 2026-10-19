"""The storyboard's cache: which frames a run draws and why, and the key that decides it.

Split out of `cli/reel_board.py`, which re-exports these names. A frame's key is
taken from what it looks like only, so the same frame hashes the same at save and
at check whatever else its dict carries by then.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import spend


# What a frame looks like: its id (the file it is drawn to), the prompt and references it is drawn from, and the
# spec and check it is judged against. Nothing else is: the shot number moves whenever a shot is put in before it,
# "revised" is an editorial mark, and keys added at run time ("_ref_names") or by later stages are not the frame.
_LOOK = ("id", "prompt", "refs", "shot_spec", "check")


def _spec_hash(frame: dict[str, Any], identity: str) -> str:
    """The cache key of a frame, from _LOOK only — the same at save and at check, whatever else the dict carries."""
    spec = {k: frame[k] for k in _LOOK if k in frame}
    return hashlib.sha256(json.dumps([spec, identity], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def _why(frame: dict[str, Any], state: dict[str, Any], only: set[str], identity: str, out_dir: Path) -> str | None:
    """Why a frame is drawn this run (a `spend` reason), or None when its png is reused."""
    entry = state.get(frame["id"]) or {}
    if frame["id"] in only:
        return spend.ASKED
    if not (out_dir / f"{frame['id']}.png").is_file():
        return spend.FAILED if entry.get("failed") else spend.MISSING
    return spend.CHANGED if entry.get("hash") != _spec_hash(frame, identity) else None


def _stale(frames: list[dict[str, Any]], state: dict[str, Any], only: set[str], identity: str,
           out_dir: Path) -> list[tuple[dict[str, Any], str]]:
    """Frames to render, each with why: asked for by --only, missing, failed, or changed since their last render."""
    return [(f, why) for f in frames if (why := _why(f, state, only, identity, out_dir))]


def _summary(stale: list[tuple[dict[str, Any], str]], per_frame: Decimal, only: set[str]) -> None:
    lines = [(f["id"], per_frame, why) for f, why in stale]
    warnings = []
    extra = [f["id"] for f, why in stale if why != spend.ASKED]
    if only and extra:
        warnings.append(f"--only {','.join(sorted(only))} also draws {len(extra)} other frame(s) that are "
                        "missing or changed")
    if any(why == spend.CHANGED for _, why in stale):
        warnings.append("if only the cache rule changed, not the frames, --mark-current re-stamps them for free")
    spend.show("Board", lines, warnings)


def _restamp(state: dict[str, Any], fid: str, current: str) -> bool:
    """Stamp `current` as the frame's hash; True when it was not already. A png on disk is not a failure."""
    entry = state.get(fid) or {}
    if entry.get("hash") == current:
        return False
    state[fid] = {**{k: v for k, v in entry.items() if k != "failed"}, "hash": current}
    return True


def mark_current(args: argparse.Namespace) -> list[str]:
    """Re-stamp the stored hash of every frame whose png exists; nothing is drawn. Returns the ids re-stamped."""
    plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    board = plan.get("board") or {}
    out_dir = Path(plan["output_dir"]) / "board"
    state_path = out_dir / "board.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    only = set((args.only or "").split(",")) - {""}
    drawn = [f for f in board.get("frames") or []
             if (not only or f["id"] in only) and (out_dir / f"{f['id']}.png").is_file()]
    marked = [f["id"] for f in drawn if _restamp(state, f["id"], _spec_hash(f, board.get("identity", "")))]
    if marked:
        state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    return marked
