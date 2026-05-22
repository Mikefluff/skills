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
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import batch as batch_mod
from .. import config
from .. import cost as cost_mod
from .. import ffmpeg as ff_mod
from ..errors import CostConfirmationDeclined


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


def main() -> int:
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
    args = parser.parse_args()

    # `--plan-file -` reads from stdin (no intermediate file needed).
    if str(args.plan_file) == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            print("plan-file '-' (stdin) is empty", file=sys.stderr)
            return 2
        plan = json.loads(raw)
    else:
        if not args.plan_file.is_file():
            print(f"plan-file not found: {args.plan_file}", file=sys.stderr)
            return 2
        plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    if plan.get("schema") != "skills.reel.plan.v1":
        print(
            f"unexpected plan schema '{plan.get('schema')}'. Expected 'skills.reel.plan.v1'.",
            file=sys.stderr,
        )
        return 2

    video_provider_slug = plan.get("video_provider")
    music_provider_slug = plan.get("music_provider")
    if not video_provider_slug:
        print("plan missing 'video_provider'", file=sys.stderr)
        return 2

    shots = plan.get("shots") or []
    if not shots:
        print("plan has no shots", file=sys.stderr)
        return 2

    music_block = plan.get("music")
    captions_enabled = bool(plan.get("captions_enabled"))
    captions = plan.get("captions") or []

    output_dir = Path(plan.get("output_dir") or "./generated/reel/batch")
    output_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = output_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"

    config.load_all_providers()

    try:
        video_provider = config.get_provider(video_provider_slug)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if video_provider.modality != "video":
        print(f"'{video_provider_slug}' is {video_provider.modality}, not video.", file=sys.stderr)
        return 2

    music_provider = None
    if music_block and music_provider_slug:
        try:
            music_provider = config.get_provider(music_provider_slug)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if music_provider.modality != "music":
            print(f"'{music_provider_slug}' is {music_provider.modality}, not music.", file=sys.stderr)
            return 2

    # Build batch items: shots + (optional) music as one combined manifest
    items: list[batch_mod.BatchItem] = []
    for entry in shots:
        items.append(_make_item(entry, default_label=f"shot-{int(entry['index']):02d}"))
    music_item: batch_mod.BatchItem | None = None
    if music_block and music_provider is not None:
        music_item = batch_mod.BatchItem(
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

    # Cost estimate
    shot_items = [i for i in items if i.label.startswith("shot-")]
    estimated_video = batch_mod.estimate_batch_cost(video_provider, shot_items) or Decimal("0")
    estimated_music = Decimal("0")
    if music_item and music_provider is not None:
        per_music = music_provider.estimate_cost(**music_item.kwargs)
        if per_music is not None:
            estimated_music = per_music
    estimated_total = estimated_video + estimated_music

    if args.cost_only:
        print(f"video shots: {len(shot_items)} ({cost_mod.format_cost(estimated_video)})")
        if music_item is not None:
            print(f"music: 1 ({cost_mod.format_cost(estimated_music)})")
        print(f"total: {cost_mod.format_cost(estimated_total)}")
        return 0

    try:
        cost_mod.confirm_batch(
            estimated_total,
            n_items=len(shot_items) + (1 if music_item else 0),
            modality="reel",
            yes=args.yes,
        )
    except CostConfirmationDeclined as exc:
        print(str(exc), file=sys.stderr)
        return 3

    parallelism = int(plan.get("parallelism") or 2)
    extra_meta = {
        "skill": "reel-builder",
        "topic": plan.get("topic"),
        "aspect": plan.get("aspect"),
        "video_style_id": plan.get("video_style_id"),
        "music_style_id": plan.get("music_style_id"),
        "video_provider": video_provider_slug,
        "music_provider": music_provider_slug,
        "captions_enabled": captions_enabled,
        "estimated_total_cost_usd": str(estimated_total),
    }

    print(
        f"Reel batch: {len(shot_items)} shots via {video_provider_slug}"
        + (f" + music via {music_provider_slug}" if music_item else "")
        + f". Estimated {cost_mod.format_cost(estimated_total)}. Parallelism: {parallelism}.",
        file=sys.stderr,
    )

    # Stage 1: run shots
    shots_result = batch_mod.run_batch(
        video_provider,
        shot_items,
        modality="video",
        output_dir=shots_dir,
        manifest_path=manifest_path,
        parallelism=parallelism,
        resume=args.resume,
        extension_hint="mp4",
        on_progress=_print_progress,
        extra_meta=extra_meta,
    )

    if not shots_result.ok:
        failed = len(shots_result.failed)
        print(
            f"  {failed} shot(s) failed. Components saved; ffmpeg skipped. Re-run with --resume.",
            file=sys.stderr,
        )
        return 1

    # Stage 2: run music (separate sub-batch to keep dir layout clean)
    music_path: Path | None = None
    if music_item is not None and music_provider is not None:
        music_manifest = output_dir / "music-manifest.json"
        music_result = batch_mod.run_batch(
            music_provider,
            [music_item],
            modality="music",
            output_dir=output_dir,
            manifest_path=music_manifest,
            parallelism=1,
            resume=args.resume,
            extension_hint="mp3",
            on_progress=_print_progress,
            extra_meta={**extra_meta, "component": "music"},
        )
        if music_result.ok and music_result.items[0].output_path:
            music_path = Path(music_result.items[0].output_path)
            # Normalize music filename for ffmpeg
            target = output_dir / f"music{music_path.suffix}"
            if music_path != target:
                try:
                    music_path.replace(target)
                    music_path = target
                except OSError:
                    pass
        else:
            print("  music generation failed — proceeding with silent stitch", file=sys.stderr)

    # Stage 3: ffmpeg stitch
    if args.skip_stitch:
        print(f"\nReel components: {output_dir} (ffmpeg skipped via --skip-stitch)")
        return 0

    probe = ff_mod.detect_ffmpeg()
    if not probe.found:
        print("\nffmpeg not found — components saved; stitch skipped.", file=sys.stderr)
        print("Install: 'brew install ffmpeg' (mac) or 'apt-get install -y ffmpeg' (debian).", file=sys.stderr)
        return 0

    shot_paths = [Path(item.output_path) for item in shots_result.succeeded if item.output_path]
    shot_paths.sort(key=lambda p: p.name)

    concat_mp4 = output_dir / "concat.mp4"
    with_music_mp4 = output_dir / "with-music.mp4"
    final_mp4 = output_dir / "final.mp4"

    try:
        if len(shot_paths) >= 2:
            ff_mod.concat_videos(shot_paths, concat_mp4, ffmpeg_bin=probe.binary or "ffmpeg")
        else:
            # single shot — just copy
            import shutil as _shutil
            _shutil.copyfile(shot_paths[0], concat_mp4)
    except Exception as exc:  # noqa: BLE001
        print(f"\nffmpeg concat failed: {exc}", file=sys.stderr)
        return 1

    stitched = concat_mp4
    if music_path is not None and music_path.is_file():
        try:
            ff_mod.mix_audio_over_video(
                concat_mp4, music_path, with_music_mp4,
                audio_volume=0.8, fade_out=0.5, ffmpeg_bin=probe.binary or "ffmpeg",
            )
            stitched = with_music_mp4
        except Exception as exc:  # noqa: BLE001
            print(f"\nffmpeg music mix failed: {exc} — using silent reel.", file=sys.stderr)
            stitched = concat_mp4

    if captions_enabled and captions:
        try:
            cap_tuples = [(float(c["start"]), float(c["end"]), str(c["text"])) for c in captions]
            ff_mod.burn_captions(stitched, cap_tuples, final_mp4, ffmpeg_bin=probe.binary or "ffmpeg")
        except Exception as exc:  # noqa: BLE001
            print(f"\nffmpeg burn-captions failed: {exc} — using uncaptioned reel.", file=sys.stderr)
            import shutil as _shutil
            _shutil.copyfile(stitched, final_mp4)
    else:
        import shutil as _shutil
        _shutil.copyfile(stitched, final_mp4)

    print(f"\nReel: {final_mp4}")
    print(f"Components: {output_dir}/(shots/, music.mp3, script.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
