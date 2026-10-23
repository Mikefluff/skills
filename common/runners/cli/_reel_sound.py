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
import subprocess
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


def estimate(sound: dict[str, Any] | None, output_dir: Path | None = None) -> Decimal:
    """What generating the sources costs; with `output_dir`, only the ones its sound cache does not hold."""
    if not sound:
        return Decimal("0")
    if output_dir is not None:
        by_id = {src["id"]: src for src in sound.get("sources") or []}
        fresh = _cached(by_id, _load_index(output_dir / "sound" / "sources.json"))
        sound = {**sound, "sources": [src for sid, src in by_id.items() if sid not in fresh]}
    total = Decimal("0")
    for slug, items in plan_items(sound).items():
        total += batch_mod.estimate_batch_cost(config.get_provider(slug), items) or Decimal("0")
    return total


def _spec_hash(src: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(src, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _load_index(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _sections(src: dict[str, Any]) -> list[dict[str, Any]]:
    plan = src.get("composition_plan") or {}
    return plan.get("sections") or plan.get("chunks") or []


def _score_key(src: dict[str, Any]) -> str:
    """A music source's identity without its section lengths: a retime fits the take it has, never buys one."""
    spec = json.loads(json.dumps(src))
    spec.pop("duration_seconds", None)
    for sec in _sections(spec):
        sec.pop("duration_ms", None)
    return _spec_hash(spec)


def _entry(src: dict[str, Any], path: str) -> dict[str, Any]:
    """The index entry of a source just made: a music take also keeps the section lengths it was made at."""
    entry = {"path": path, "hash": _spec_hash(src)}
    if src.get("kind") == "music":
        entry.update(score=_score_key(src), made_ms=[sec["duration_ms"] for sec in _sections(src)])
    return entry


def _cached(by_id: dict[str, dict[str, Any]], index: dict[str, Any]) -> dict[str, Path]:
    """Sources whose file exists and whose spec has not changed since it was made; a music source whose
    sections only changed length counts as unchanged (it is fitted in the mix). An entry kept from before
    the music had its own key gets one while its spec still matches."""
    out = {}
    for sid, src in by_id.items():
        entry = index.get(sid)
        if not (entry and Path(entry["path"]).is_file()):
            continue
        if entry["hash"] == _spec_hash(src):
            if src.get("kind") == "music" and "score" not in entry:
                entry.update({k: v for k, v in _entry(src, entry["path"]).items() if k != "path"})
            out[sid] = Path(entry["path"])
        elif src.get("kind") == "music" and entry.get("score") == _score_key(src):
            out[sid] = Path(entry["path"])
    return out


def _fitted(src: dict[str, Any], entry: dict[str, Any], take: Path, sound_dir: Path) -> Path:
    """A music take made at other section lengths, each section time-stretched to its length now (cached)."""
    made, now = entry.get("made_ms"), [sec["duration_ms"] for sec in _sections(src)]
    if not made or made == now or len(made) != len(now):
        return take
    out = sound_dir / "fitted" / f"{src['id']}-{_spec_hash([str(take), made, now])}.wav"
    if out.is_file():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    bounds = [sum(made[:n]) / 1000 for n in range(len(made) + 1)]
    chains = []
    for n, length in enumerate(now):
        end = f":end={bounds[n + 1]:.3f}" if n + 1 < len(made) else ""  # the last runs to the take's own end
        tempo = min(2.0, max(0.5, made[n] / max(length, 1)))
        chains.append(f"[s{n}]atrim=start={bounds[n]:.3f}{end},asetpts=PTS-STARTPTS,atempo={tempo:.5f}[f{n}]")
    graph = (f"[0:a]asplit={len(now)}" + "".join(f"[s{n}]" for n in range(len(now))) + ";" + ";".join(chains)
             + ";" + "".join(f"[f{n}]" for n in range(len(now))) + f"concat=n={len(now)}:v=0:a=1[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(take), "-filter_complex", graph,
                    "-map", "[out]", str(out)], check=True, capture_output=True)
    print(f"  {src['id']}: the take fitted to its sections now, not bought again", file=sys.stderr)
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
    name. A music source is keyed without its section lengths: a retime that
    grows an act keeps the take and stretches each section to its new length
    (`_fitted`); a new take is asked for by changing anything else in its spec
    (a `"take": 2`), and `resume=False` regenerates everything.
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
                index[item.label] = _entry(by_id[item.label], item.output_path)
            else:
                failed.append(f"{item.label}: {item.error}")
    sound_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    if failed:
        raise RuntimeError("sound sources failed — " + "; ".join(failed))
    return _fit_all(fresh, by_id, index, sound_dir)


def _fit_all(fresh: dict[str, Path], by_id: dict[str, dict[str, Any]], index: dict[str, Any],
             sound_dir: Path) -> dict[str, Path]:
    """Every source's file, the music takes fitted to their sections now."""
    return {sid: _fitted(by_id[sid], index[sid], path, sound_dir) if sid in by_id and sid in index else path
            for sid, path in fresh.items()}


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


def _peak_db(path: Path) -> float:
    """The loudest sample of a file, dBFS (ffmpeg volumedetect)."""
    import re

    run = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True)
    found = re.search(r"max_volume:\s*(-?[\d.]+) dB", run.stderr)
    return float(found.group(1)) if found else 0.0


def leveled(placements: list[st.Placement], sound: dict[str, Any], sources: dict[str, Path]) -> list[st.Placement]:
    """With "sfx_peak" (dBFS) in the sound, every one-shot effect is first brought to that peak, then its own
    gain_db applies: ElevenLabs makes one explosion at -6 dB and the next at -25, and laid as made the hits
    vanished under the lines and the score."""
    target = sound.get("sfx_peak")
    if target is None:
        return placements
    from ._stage_cache import probed

    one_shots = {s["id"] for s in sound.get("sources") or [] if s.get("kind") == "sfx" and not s.get("loop")}
    out = []
    for p in placements:
        if p.source in one_shots and p.source in sources:
            lift = float(target) - probed(sources[p.source], _peak_db)
            p = st.Placement(**{**p.__dict__, "gain_db": p.gain_db + lift})
        out.append(p)
    return out


def render(
    sound: dict[str, Any], sources: dict[str, Path], voice: Path, output: Path, picture: Path | None = None
) -> Path:
    """Mix voice + placed sources into `output` (WAV), mastered. Returns `output`."""
    placements = leveled(snapped(st.validate(sound), picture), sound, sources)
    total = float(sound.get("total_seconds") or 0) or (ff_mod.get_duration(voice) or 0.0)
    master = st.Master(**(sound.get("master") or {}))
    inputs, graph = st.build_graph(placements, sources, voice, total, master)
    from ._stage_cache import run_once

    output.parent.mkdir(parents=True, exist_ok=True)
    # ffmpeg_film.render_mix's command, run only when its voices, sounds or graph moved
    run_once(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
              "-ar", "48000", "-c:a", "pcm_s16le", str(output)], output)
    # What was actually placed, after snapping — the record to tune against.
    output.with_suffix(".placements.json").write_text(
        json.dumps([p.__dict__ for p in placements], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return output

