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

Voiced film (optional — written by the film prompt chain from timing.json):

  "voiceover": {"path": "<out>/voice/master.wav"},   # the one take the viewer hears
  "continuity": "reference" | "first_frame",          # how a segment receives the seam frame
  shots[i].trim_seconds: 13.48                        # cut here; the overshoot is discarded
  shots[i].continue_from_previous: true               # open on the frame shot i-1 was cut on
  shots[i].seam_frame_at: 7.0                         # ...or hand over this earlier frame instead
                                                      # (a whiteout seam has nothing at the cut)
  shots[i].trim_start: 0.5                            # head handle: the cut starts here in the clip
  shots[i].lip_sync: true                             # one generation per shot: this shot gets
                                                      # its stretch of the master as @Audio1

A chained plan generates in order, one segment at a time, because each seam
frame exists only once the segment before it is done.

Pipeline:
1. Generate shots in parallel (async polling).
2. Generate music in parallel with shots.
3. ffmpeg concat shots → music mix → burn captions.
4. Save final.mp4 + components.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import batch as batch_mod
from .. import cost as cost_mod
from ..errors import CostConfirmationDeclined
from . import _reel_sound
from ._reel_plan import (  # noqa: F401 — re-exported: reel.prepare, reel.ReelJob, reel.Routed ...
    PlanError,
    ReelJob,
    Routed,
    _build_music_item,
    _make_item,
    load_plan,
    prepare,
    resolve_provider,
)
from ._reel_seams import lip_slices, seam_hook  # noqa: F401
from ._reel_stitch import stitch


def _print_progress(item: batch_mod.BatchItem) -> None:
    if item.status == "succeeded":
        out = item.output_path or "?"
        print(f"  ✓ {item.label}: {out}", file=sys.stderr)
    else:
        err = item.error or "unknown"
        print(f"  ✗ {item.label}: {err}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="common.runners.cli.reel")
    parser.add_argument("--plan-file", type=Path, required=True, help="path to plan.json")
    parser.add_argument("--resume", action="store_true", help="reuse succeeded items from manifest")
    parser.add_argument("--redo", default="",
                        help="comma-separated shot labels to generate again (implies --resume for the rest)")
    parser.add_argument("--only", default="",
                        help="comma-separated shot labels: render these and nothing else (implies --resume)")
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


# ── cost ────────────────────────────────────────────────────────────────────


def estimate(job: ReelJob) -> tuple[Decimal, Decimal]:
    """(video, music) estimates. Kept separate so --cost-only can itemise."""
    video = batch_mod.estimate_batch_cost(job.video_provider, job.shot_items) or Decimal("0")
    music = Decimal("0")
    if job.music_item and job.music_provider is not None:
        per_music = job.music_provider.estimate_cost(**job.music_item.kwargs)
        if per_music is not None:
            music = per_music
    # A film's designed soundtrack (cues + effects) is billed under music.
    return video, music + _reel_sound.estimate(job.plan.get("sound"))


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


def run_shots(job: ReelJob, meta: dict[str, Any], *, resume: bool, redo: frozenset[str] = frozenset(),
              only: frozenset[str] = frozenset()):
    chained = job.chained
    return batch_mod.run_batch(
        job.video_provider,
        sorted(job.shot_items, key=lambda it: it.index) if chained else job.shot_items,
        batch_mod.BatchSpec(
            modality="video",
            output_dir=job.shots_dir,
            manifest_path=job.manifest_path,
            parallelism=1 if chained else int(job.plan.get("parallelism") or 2),
            resume=resume,
            redo=redo,
            only=only,
            extension_hint="mp4",
            extra_meta=meta,
            before_item=seam_hook(job) if chained else None,
        ),
        on_progress=_print_progress,
    )


def run_music(job: ReelJob, meta: dict[str, Any], *, resume: bool) -> Path | None:
    """Separate sub-batch, so the directory layout stays readable."""
    if job.music_item is None or job.music_provider is None:
        return None
    result = batch_mod.run_batch(
        job.music_provider,
        [job.music_item],
        batch_mod.BatchSpec(
            modality="music",
            output_dir=job.output_dir,
            manifest_path=job.output_dir / "music-manifest.json",
            parallelism=1,
            resume=resume,
            extension_hint="mp3",
            extra_meta={**meta, "component": "music"},
        ),
        on_progress=_print_progress,
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


def _announce(job: ReelJob, total: Decimal) -> None:
    print(
        f"Reel batch: {len(job.shot_items)} shots via {job.plan['video_provider']}"
        + (f" + music via {job.plan.get('music_provider')}" if job.music_item else "")
        + f". Estimated {cost_mod.format_cost(total)}. "
        + ("Chained: segments run in order." if job.chained
           else f"Parallelism: {job.plan.get('parallelism') or 2}."),
        file=sys.stderr,
    )



def _labels(raw: str) -> frozenset[str]:
    return frozenset(x.strip() for x in raw.split(",") if x.strip())


def _narrow_to(job: ReelJob, only: frozenset[str]) -> None:
    """A test of one shot prices and runs that shot alone; the music is not part of it."""
    job.shot_items_all, job.shot_items = job.shot_items, [i for i in job.shot_items if i.label in only]
    job.music_item = None


def _confirm(job: ReelJob, total: Decimal, yes: bool) -> bool:
    try:
        cost_mod.confirm_batch(
            total,
            n_items=len(job.shot_items) + (1 if job.music_item else 0),
            modality="reel",
            yes=yes,
        )
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return False
    return True


def _generate(job: ReelJob, args: argparse.Namespace, meta: dict[str, Any], only: frozenset[str]) -> int:
    """Shots, then music and sound, then the stitch."""
    redo = _labels(args.redo)
    if redo:
        args.resume = True
    if only:
        job.shot_items = job.shot_items_all  # the manifest keeps every shot's record
        redo = redo | only
    shots_result = run_shots(job, meta, resume=args.resume, redo=redo, only=only)
    from .. import shot_matrix

    shot_matrix.record_takes(job.plan, job.shot_items, lambda it: job.video_provider.estimate_cost(**it.kwargs))
    if not shots_result.ok:
        print(
            f"  {len(shots_result.failed)} shot(s) failed. Components saved; "
            f"ffmpeg skipped. Re-run with --resume.",
            file=sys.stderr,
        )
        return 1

    music_path = run_music(job, meta, resume=args.resume)
    if job.plan.get("sound"):
        # resume=True: sources already rendered by `reel_sound` are not paid for twice.
        job.sound_sources = _reel_sound.generate(job.plan["sound"], job.output_dir, resume=True)

    if args.skip_stitch:
        print(f"\nReel components: {job.output_dir} (ffmpeg skipped via --skip-stitch)")
        return 0

    return stitch(job, shots_result, music_path)


def main() -> int:
    args = build_parser().parse_args()

    try:
        job = prepare(load_plan(args.plan_file))
    except PlanError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    only = _labels(args.only)
    if only:
        args.resume = True
        _narrow_to(job, only)
    video_cost, music_cost = estimate(job)
    if only:
        music_cost = Decimal("0")  # the sound is already made; a test shot pays for itself only
    total = video_cost + music_cost
    if args.cost_only:
        return print_cost(job, video_cost, music_cost)
    if not _confirm(job, total, args.yes):
        return 3

    meta = _meta(job, total)
    _announce(job, total)
    return _generate(job, args, meta, only)


if __name__ == "__main__":
    sys.exit(main())
