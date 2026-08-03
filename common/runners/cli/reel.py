"""Reel orchestration CLI — generate shots + music, stitch with ffmpeg.

Plan format (schema = "skills.reel.plan.v1"):

  {
    "schema": "skills.reel.plan.v1",
    "topic": "...",
    "aspect": "vertical|square|horizontal",
    "video_style_id": "...",
    "music_style_id": "...",
    "video_provider": "veo-3-1",
    "music_provider": "suno-v5-5",
    "captions_enabled": true,
    "output_dir": "./generated/reel/<slug>",
    "parallelism": 2,
    "shots": [
      {"index": 1, "label": "shot-01-hook", "prompt": "<full>",
       "duration_seconds": 5, "kwargs": {"size": "1080x1920"}},
      ...
    ],
    "music": {
      "prompt": "<style box>",
      "lyrics": null,
      "instrumental": true,
      "duration_seconds": 17,
      "kwargs": {}
    },
    "captions": [
      {"start": 0.0, "end": 5.0, "text": "Caption 1"},
      ...
    ]
  }

Pipeline:
1. Generate shots in parallel (async polling).
2. Generate music in parallel with shots.
3. ffmpeg concat shots → music mix → burn captions.
4. Save final.mp4 + components.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import batch as batch_mod
from .. import config
from .. import cost as cost_mod
from .. import ffmpeg as ff_mod
from ..errors import CostConfirmationDeclined
from ._reel_stitch import stitch


def _print_progress(item: batch_mod.BatchItem) -> None:
    if item.status == "succeeded":
        out = item.output_path or "?"
        print(f"  ✓ {item.label}: {out}", file=sys.stderr)
    else:
        err = item.error or "unknown"
        print(f"  ✗ {item.label}: {err}", file=sys.stderr)


def _make_item(entry: dict[str, Any], default_label: str) -> batch_mod.BatchItem:
    return batch_mod.BatchItem(
        index=int(entry["index"]),
        label=str(entry.get("label") or default_label),
        prompt=str(entry["prompt"]),
        kwargs=dict(entry.get("kwargs") or {}),
    )


class PlanError(Exception):
    """Plan is unusable. Carries the message the CLI should print."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel")
    parser.add_argument("--plan-file", type=Path, required=True, help="path to plan.json")
    parser.add_argument("--resume", action="store_true", help="reuse succeeded items from manifest")
    parser.add_argument("--yes", action="store_true", help="skip cost confirmation")
    parser.add_argument(
        "--cost-only", action="store_true",
        help="print estimated total + per-component; do not generate",
    )
    parser.add_argument(
        "--skip-stitch", action="store_true",
        help="generate shots + music; don't run ffmpeg",
    )
    return parser


# ── plan ────────────────────────────────────────────────────────────────────


def load_plan(plan_file: Path) -> dict[str, Any]:
    """Read and validate plan.json. `--plan-file -` reads stdin."""
    if str(plan_file) == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            raise PlanError("plan-file '-' (stdin) is empty")
    else:
        if not plan_file.is_file():
            raise PlanError(f"plan-file not found: {plan_file}")
        raw = plan_file.read_text(encoding="utf-8")

    plan = json.loads(raw)
    if plan.get("schema") != "skills.reel.plan.v1":
        raise PlanError(
            f"unexpected plan schema '{plan.get('schema')}'. Expected 'skills.reel.plan.v1'."
        )
    if not plan.get("video_provider"):
        raise PlanError("plan missing 'video_provider'")
    if not (plan.get("shots") or []):
        raise PlanError("plan has no shots")
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

    @property
    def shots_dir(self) -> Path:
        return self.output_dir / "shots"

    @property
    def manifest_path(self) -> Path:
        return self.output_dir / "manifest.json"


def prepare(plan: dict[str, Any]) -> ReelJob:
    """Resolve providers, build batch items, create the output directories."""
    config.load_all_providers()
    video_provider = resolve_provider(plan["video_provider"], "video")

    music_block = plan.get("music")
    music_slug = plan.get("music_provider")
    music_provider = resolve_provider(music_slug, "music") if music_block and music_slug else None

    shot_items = [
        _make_item(entry, default_label=f"shot-{int(entry['index']):02d}")
        for entry in plan["shots"]
    ]
    music_item = _build_music_item(music_block) if music_block and music_provider else None

    output_dir = Path(plan.get("output_dir") or "./generated/reel/batch")
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


# ── cost ────────────────────────────────────────────────────────────────────


def estimate(job: ReelJob) -> tuple[Decimal, Decimal]:
    """(video, music) estimates. Kept separate so --cost-only can itemise."""
    video = batch_mod.estimate_batch_cost(job.video_provider, job.shot_items) or Decimal("0")
    music = Decimal("0")
    if job.music_item and job.music_provider is not None:
        per_music = job.music_provider.estimate_cost(**job.music_item.kwargs)
        if per_music is not None:
            music = per_music
    return video, music


def print_cost(job: ReelJob, video: Decimal, music: Decimal) -> int:
    print(f"video shots: {len(job.shot_items)} ({cost_mod.format_cost(video)})")
    if job.music_item is not None:
        print(f"music: 1 ({cost_mod.format_cost(music)})")
    print(f"total: {cost_mod.format_cost(video + music)}")
    return 0


def _meta(job: ReelJob, total: Decimal) -> dict[str, Any]:
    plan = job.plan
    return {
        "skill": "reel-builder",
        "topic": plan.get("topic"),
        "aspect": plan.get("aspect"),
        "video_style_id": plan.get("video_style_id"),
        "music_style_id": plan.get("music_style_id"),
        "video_provider": plan.get("video_provider"),
        "music_provider": plan.get("music_provider"),
        "captions_enabled": bool(plan.get("captions_enabled")),
        "estimated_total_cost_usd": str(total),
    }


# ── generation ──────────────────────────────────────────────────────────────


def run_shots(job: ReelJob, meta: dict[str, Any], *, resume: bool):
    return batch_mod.run_batch(
        job.video_provider,
        job.shot_items,
        modality="video",
        output_dir=job.shots_dir,
        manifest_path=job.manifest_path,
        parallelism=int(job.plan.get("parallelism") or 2),
        resume=resume,
        extension_hint="mp4",
        on_progress=_print_progress,
        extra_meta=meta,
    )


def run_music(job: ReelJob, meta: dict[str, Any], *, resume: bool) -> Path | None:
    """Separate sub-batch, so the directory layout stays readable."""
    if job.music_item is None or job.music_provider is None:
        return None
    result = batch_mod.run_batch(
        job.music_provider,
        [job.music_item],
        modality="music",
        output_dir=job.output_dir,
        manifest_path=job.output_dir / "music-manifest.json",
        parallelism=1,
        resume=resume,
        extension_hint="mp3",
        on_progress=_print_progress,
        extra_meta={**meta, "component": "music"},
    )
    if not (result.ok and result.items[0].output_path):
        print("  music generation failed — proceeding with silent stitch", file=sys.stderr)
        return None
    return _normalise_music_name(Path(result.items[0].output_path), job.output_dir)


def _normalise_music_name(path: Path, output_dir: Path) -> Path:
    """ffmpeg is handed a predictable name rather than a timestamped one."""
    target = output_dir / f"music{path.suffix}"
    if path == target:
        return path
    try:
        path.replace(target)
        return target
    except OSError:
        return path


# ── main ────────────────────────────────────────────────────────────────────


def main() -> int:
    args = build_parser().parse_args()

    try:
        job = prepare(load_plan(args.plan_file))
    except PlanError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    video_cost, music_cost = estimate(job)
    total = video_cost + music_cost
    if args.cost_only:
        return print_cost(job, video_cost, music_cost)

    try:
        cost_mod.confirm_batch(
            total,
            n_items=len(job.shot_items) + (1 if job.music_item else 0),
            modality="reel",
            yes=args.yes,
        )
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    meta = _meta(job, total)
    print(
        f"Reel batch: {len(job.shot_items)} shots via {job.plan['video_provider']}"
        + (f" + music via {job.plan.get('music_provider')}" if job.music_item else "")
        + f". Estimated {cost_mod.format_cost(total)}. "
        f"Parallelism: {job.plan.get('parallelism') or 2}.",
        file=sys.stderr,
    )

    shots_result = run_shots(job, meta, resume=args.resume)
    if not shots_result.ok:
        print(
            f"  {len(shots_result.failed)} shot(s) failed. Components saved; "
            f"ffmpeg skipped. Re-run with --resume.",
            file=sys.stderr,
        )
        return 1

    music_path = run_music(job, meta, resume=args.resume)

    if args.skip_stitch:
        print(f"\nReel components: {job.output_dir} (ffmpeg skipped via --skip-stitch)")
        return 0

    return stitch(job, shots_result, music_path)


if __name__ == "__main__":
    sys.exit(main())
