"""What `reel` is about to buy: every shot, the music and each sound source it will generate, with why.

Mirrors the run exactly — the same resume, redo and only that `reel._generate`
hands the batch — so the confirmed total is what the run spends, not the cost
of every shot in the plan.
"""

from __future__ import annotations

from typing import Any

from .. import batch as batch_mod
from .. import config
from .. import spend
from . import _reel_sound


def _shots(job: Any, resume: bool, redo: frozenset[str], only: frozenset[str]) -> list[spend.Line]:
    items = getattr(job, "shot_items_all", job.shot_items) if only else job.shot_items
    pending = batch_mod.pending_reasons(items, job.manifest_path, resume=resume or bool(redo or only),
                                        redo=redo | only, only=only)
    return [(item.label, job.video_provider.estimate_cost(**item.kwargs), why) for item, why in pending]


def _music(job: Any, resume: bool) -> list[spend.Line]:
    if job.music_item is None or job.music_provider is None:
        return []
    pending = batch_mod.pending_reasons([job.music_item], job.output_dir / "music-manifest.json", resume=resume)
    return [("music", job.music_provider.estimate_cost(**job.music_item.kwargs), why) for _, why in pending]


def _sound(job: Any) -> list[spend.Line]:
    """Sources the sound stage will generate — even on --only; it reuses what it made from an unchanged spec."""
    sound = job.plan.get("sound")
    if not sound:
        return []
    index = _reel_sound._load_index(job.output_dir / "sound" / "sources.json")
    by_id = {src["id"]: src for src in sound.get("sources") or []}
    fresh = _reel_sound._cached(by_id, index)
    out = []
    for slug, items in _reel_sound.plan_items(sound).items():
        provider = config.get_provider(slug)
        out += [(f"sound:{item.label}", provider.estimate_cost(**item.kwargs),
                 spend.CHANGED if item.label in index else spend.MISSING)
                for item in items if item.label not in fresh]
    return out


def _warnings(shots: list[spend.Line], redo: frozenset[str], only: frozenset[str]) -> list[str]:
    extra = [label for label, _, why in shots if why != spend.ASKED]
    out = []
    if redo and extra:
        out.append(f"--redo {','.join(sorted(redo))} also renders {len(extra)} other shot(s) "
                   f"({', '.join(extra[:5])}{', …' if len(extra) > 5 else ''}); "
                   f"to render just these use --only {','.join(sorted(redo | only))}")
    again = [label for label, _, why in shots if why == spend.RERUN]
    if again:
        out.append(f"{len(again)} shot(s) already rendered are paid for again; add --resume to keep them")
    return out


def to_buy(job: Any, *, resume: bool, redo: frozenset[str], only: frozenset[str]) -> tuple[list[spend.Line], list[str]]:
    """(lines, warnings) for everything this run generates."""
    shots = _shots(job, resume, redo, only)
    lines = shots + _music(job, resume or bool(redo or only)) + _sound(job)
    return lines, _warnings(shots, redo, only)
