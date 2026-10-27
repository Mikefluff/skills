"""Plan stage of the reel pipeline: read plan.json, resolve providers, build the job.

Split out of `cli/reel.py` so the CLI module stays about orchestration; `reel`
re-exports every name here, so `reel.prepare`, `reel.ReelJob` etc. still work.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .. import batch as batch_mod
from .. import config
from ._reel_seams import lip_slices


class PlanError(Exception):
    """Plan is unusable. Carries the message the CLI should print."""


def _make_item(entry: dict[str, Any], default_label: str) -> batch_mod.BatchItem:
    return batch_mod.BatchItem(
        index=int(entry["index"]),
        label=str(entry.get("label") or default_label),
        prompt=str(entry["prompt"]),
        kwargs=dict(entry.get("kwargs") or {}),
    )


class Routed:
    """A plan's providers behind one face, so mixed routes share one batch and one manifest.

    Each item carries `_route` (a provider slug); generation, estimates and polling go to that provider."""

    modality = "video"

    def __init__(self, default: Any, others: dict[str, Any]):
        self.name, self._by = default.name, {default.name: default, **others}

    def _for(self, kwargs: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        kwargs = dict(kwargs)
        return self._by[kwargs.pop("_route", self.name)], kwargs

    def ensure_available(self) -> None:
        for provider in self._by.values():
            provider.ensure_available()

    def estimate_cost(self, **kwargs: Any):
        provider, rest = self._for(kwargs)
        return provider.estimate_cost(**rest)

    def generate(self, prompt: str, **kwargs: Any):
        provider, rest = self._for(kwargs)
        return provider.generate(prompt, **rest)

    def poll(self, handle: Any, timeout: float = 900.0):
        return self._by[handle.provider].poll(handle, timeout=timeout)


# ── plan ────────────────────────────────────────────────────────────────────


def _read_raw(plan_file: Path) -> str:
    """The plan's text; `-` reads stdin."""
    if str(plan_file) == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            raise PlanError("plan-file '-' (stdin) is empty")
        return raw
    if not plan_file.is_file():
        raise PlanError(f"plan-file not found: {plan_file}")
    return plan_file.read_text(encoding="utf-8")


def load_plan(plan_file: Path) -> dict[str, Any]:
    """Read and validate plan.json. `--plan-file -` reads stdin."""
    plan = json.loads(_read_raw(plan_file))
    if plan.get("schema") != "skills.reel.plan.v1":
        raise PlanError(
            f"unexpected plan schema '{plan.get('schema')}'. Expected 'skills.reel.plan.v1'."
        )
    if not plan.get("video_provider"):
        raise PlanError("plan missing 'video_provider'")
    if not (plan.get("shots") or []):
        raise PlanError("plan has no shots")
    if plan.get("bible") and not all(s.get("prompt") or s.get("clip") for s in plan["shots"]):
        raise PlanError("drama scenes have no prompts yet: run common.runners.cli.reel_cast on this plan first")
    return plan


def resolve_provider(slug: str, expected: str):
    try:
        provider = config.get_provider(slug)
    except KeyError as exc:
        raise PlanError(exc.args[0]) from exc
    if provider.modality != expected:
        raise PlanError(f"'{slug}' is {provider.modality}, not {expected}.")
    return provider


@dataclass
class ReelJob:
    """A validated plan plus everything resolved from it."""

    plan: dict[str, Any]
    video_provider: Any
    music_provider: Any | None
    shot_items: list[batch_mod.BatchItem]
    music_item: batch_mod.BatchItem | None
    output_dir: Path
    # Film mode's designed soundtrack, generated after the shots: id → file.
    sound_sources: dict[str, Path] = field(default_factory=dict)

    @property
    def shots_dir(self) -> Path:
        return self.output_dir / "shots"

    @property
    def manifest_path(self) -> Path:
        return self.output_dir / "manifest.json"

    @property
    def chained(self) -> bool:
        return any(entry.get("continue_from_previous") for entry in self.plan["shots"])

    def cut_seconds(self, index: int) -> float:
        """Where shot `index` is cut — its trim if the plan has one, else its full length."""
        entry = next(e for e in self.plan["shots"] if int(e["index"]) == index)
        kwargs = entry.get("kwargs") or {}
        return float(entry.get("trim_seconds") or kwargs.get("duration_seconds") or entry.get("duration_seconds") or 5)


def _route_shots(plan: dict[str, Any], shot_items: list[batch_mod.BatchItem], video_provider: Any) -> Any:
    """A shot naming its own provider: one batch, one manifest, each item sent its own way."""
    routes = {str(e["label"]): e["video_provider"] for e in plan["shots"] if e.get("video_provider")}
    if not routes:
        return video_provider
    for item in shot_items:
        item.kwargs["_route"] = routes.get(item.label, plan["video_provider"])
    return Routed(video_provider, {slug: resolve_provider(slug, "video") for slug in set(routes.values())})


def prepare(plan: dict[str, Any]) -> ReelJob:
    """Resolve providers, build batch items, create the output directories."""
    config.load_all_providers()
    video_provider = resolve_provider(plan["video_provider"], "video")

    music_block = plan.get("music")
    music_slug = plan.get("music_provider")
    music_provider = resolve_provider(music_slug, "music") if music_block and music_slug else None

    output_dir = Path(plan.get("output_dir") or "./generated/reel/batch")
    lip_slices(plan, output_dir)
    shot_items = [
        _make_item(entry, default_label=f"shot-{int(entry['index']):02d}")
        for entry in plan["shots"]
        if not entry.get("clip")  # cut by hand (a composite); not rendered
    ]
    video_provider = _route_shots(plan, shot_items, video_provider)
    music_item = _build_music_item(music_block) if music_block and music_provider else None

    job = ReelJob(plan, video_provider, music_provider, shot_items, music_item, output_dir)
    job.output_dir.mkdir(parents=True, exist_ok=True)
    job.shots_dir.mkdir(parents=True, exist_ok=True)
    return job


def _build_music_item(music_block: dict[str, Any]) -> batch_mod.BatchItem:
    return batch_mod.BatchItem(
        index=999,
        label="music",
        prompt=str(music_block.get("prompt") or ""),
        kwargs={
            **(music_block.get("kwargs") or {}),
            "instrumental": bool(music_block.get("instrumental")),
            "duration_seconds": float(music_block.get("duration_seconds") or 15),
            "lyrics": music_block.get("lyrics") or "",
        },
    )
