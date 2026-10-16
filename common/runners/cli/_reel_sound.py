"""Sound stage of a voiced film: generate the sources, snap the hits, mix, master.

The plan's `sound` block (written by the film chain alongside the prompts) says
what to generate and where each slice sits. Sources are generated before the
video if asked (`--sound-only`), so a soundtrack can be heard against the voice
before the expensive render is paid for; the picture, once it exists, only
moves the hits that asked to be snapped to it.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from .. import batch as batch_mod
from .. import config
from .. import ffmpeg as ff_mod
from .. import ffmpeg_film
from .. import soundtrack as st

_PROVIDER = {"music": "eleven-music", "sfx": "eleven-sfx"}


def _items(sources: list[dict[str, Any]], kind: str) -> list[batch_mod.BatchItem]:
    out = []
    for n, src in enumerate((s for s in sources if s.get("kind", "sfx") == kind), start=1):
        if kind == "music":
            plan = src["composition_plan"]
            # music_v1 plans have `sections`, v2 plans `chunks`; both carry duration_ms.
            parts = plan.get("sections") or plan.get("chunks") or []
            kwargs = {
                "composition_plan": plan,
                "model_id": src.get("model_id", "music_v1" if "sections" in plan else "music_v2"),
                "duration_seconds": sum(c["duration_ms"] for c in parts) / 1000,
            }
            prompt = ""
        else:
            kwargs = {k: src[k] for k in ("duration_seconds", "prompt_influence", "loop") if k in src}
            prompt = src["prompt"]
        out.append(batch_mod.BatchItem(index=n, label=src["id"], prompt=prompt, kwargs=kwargs))
    return out


def plan_items(sound: dict[str, Any]) -> dict[str, list[batch_mod.BatchItem]]:
    """{provider slug: items}, one batch per provider."""
    sources = sound.get("sources") or []
    return {_PROVIDER[kind]: items for kind in _PROVIDER if (items := _items(sources, kind))}


def estimate(sound: dict[str, Any] | None) -> Decimal:
    if not sound:
        return Decimal("0")
    total = Decimal("0")
    for slug, items in plan_items(sound).items():
        total += batch_mod.estimate_batch_cost(config.get_provider(slug), items) or Decimal("0")
    return total


def _spec_hash(src: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(src, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _load_index(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _cached(by_id: dict[str, dict[str, Any]], index: dict[str, Any]) -> dict[str, Path]:
    """Sources whose file exists and whose spec has not changed since it was made."""
    out = {}
    for sid, src in by_id.items():
        entry = index.get(sid)
        if entry and entry["hash"] == _spec_hash(src) and Path(entry["path"]).is_file():
            out[sid] = Path(entry["path"])
    return out


def _run(slug: str, items: list[batch_mod.BatchItem], sound_dir: Path) -> list[batch_mod.BatchItem]:
    return batch_mod.run_batch(
        config.get_provider(slug),
        items,
        batch_mod.BatchSpec(
            modality="audio",
            output_dir=sound_dir,
            manifest_path=sound_dir / f"manifest-{slug}.json",
            # ElevenLabs caps concurrent requests per plan; 2 is the smallest paid tier's cap.
            parallelism=int(os.environ.get("SKILLS_ELEVEN_CONCURRENCY", "2")),
            extension_hint="mp3",
        ),
    ).items


def generate(sound: dict[str, Any], output_dir: Path, *, resume: bool) -> dict[str, Path]:
    """Every source on disk, keyed by id. Raises RuntimeError if any failed.

    Reuse is keyed by id AND by a hash of the source's spec, never by position:
    a re-run of the chain may reorder sources or rewrite one prompt, and a
    positional cache would then hand the mix the wrong file under the right
    name. `resume=False` regenerates everything.
    """
    st.validate(sound)
    sound_dir = output_dir / "sound"
    index_path = sound_dir / "sources.json"
    index = _load_index(index_path) if resume else {}
    by_id = {src["id"]: src for src in sound.get("sources") or []}
    fresh = _cached(by_id, index)
    todo = {**sound, "sources": [src for sid, src in by_id.items() if sid not in fresh]}
    failed: list[str] = []
    for slug, items in plan_items(todo).items():
        for item in _run(slug, items, sound_dir):
            if item.status == "succeeded" and item.output_path:
                fresh[item.label] = Path(item.output_path)
                index[item.label] = {"path": item.output_path, "hash": _spec_hash(by_id[item.label])}
            else:
                failed.append(f"{item.label}: {item.error}")
    sound_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    if failed:
        raise RuntimeError("sound sources failed — " + "; ".join(failed))
    return fresh


def snapped(placements: list[st.Placement], picture: Path | None) -> list[st.Placement]:
    """Placements with `snap` moved onto the frame where the flash actually is."""
    if picture is None or not any(p.snap for p in placements):
        return placements
    hits = st.brightness_jumps(ffmpeg_film.luma_series(picture))
    out = []
    for p in placements:
        if p.snap:
            at = st.snap_time(p.at, hits)
            if at != p.at:
                print(f"  snap {p.source}: {p.at:.2f}s → {at:.2f}s", file=sys.stderr)
            p = st.Placement(**{**p.__dict__, "at": at})
        out.append(p)
    return out


def render(
    sound: dict[str, Any], sources: dict[str, Path], voice: Path, output: Path, picture: Path | None = None
) -> Path:
    """Mix voice + placed sources into `output` (WAV), mastered. Returns `output`."""
    placements = snapped(st.validate(sound), picture)
    total = float(sound.get("total_seconds") or 0) or (ff_mod.get_duration(voice) or 0.0)
    master = st.Master(**(sound.get("master") or {}))
    inputs, graph = st.build_graph(placements, sources, voice, total, master)
    ffmpeg_film.render_mix(inputs, graph, output)
    # What was actually placed, after snapping — the record to tune against.
    output.with_suffix(".placements.json").write_text(
        json.dumps([p.__dict__ for p in placements], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return output

