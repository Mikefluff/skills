"""The sound a cut of rendered shots adds under the score: each place's bed, and each shot's own sound.

A trailer designed in the animatic has music, hits and a few room tones; the
places themselves are silent, and in a film the creaks, hums and footsteps are
half of what sells a room. Two layers fill it, both laid unducked under the
plan's own sound:

  beds        one loopable ambience per location the cut visits, generated from
              the bible's description and acoustics, laid across every run of
              consecutive shots in that place
  production  each rendered clip's own sound, its window as cut, levelled to one
              loudness. Any speech the generation made (its reading of the line,
              or words nobody wrote: a crowd shouting in Chinese, "Pass up!") is
              cut out by Scribe's word span, so only the room, the cloth and the
              props are left
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

_BED_SECONDS = 30.0
_BED_GAIN_DB = -20.0
_PRODUCTION_GAIN_DB = 0.0
# Generations come back 34 dB apart (-11 to -45 LUFS on the SAME trailer): every shot's own sound is
# levelled to one loudness under the score before it is placed, low end below the room cut.
_PRODUCTION_LUFS = -31.0
_VOICE_PAD = (0.12, 0.2)  # seconds kept clear before and after the clip's own voice

_ROOM = {"small_room": "a small room, close and dry", "big_room": "a large room with a short reverb",
         "hall": "a big hard hall with a long reverb", "street": "outdoors on a city street",
         "tunnel": "a concrete tunnel with a hard echo"}


def bed_id(location: str) -> str:
    return f"bed_{location}"


def bed_source(location: dict[str, Any]) -> dict[str, Any]:
    """The ambience of a place, from the bible's own words: no music, no voices, even enough to loop."""
    room = _ROOM.get(location.get("acoustics", ""), "")
    prompt = (f"Continuous ambience and room tone of {location['description'].rstrip('.')}"
              + (f", heard in {room}" if room else "")
              + ". Background only: its machines, air and distant life, no music, no speech, no sudden hits.")
    return {"id": bed_id(location["id"]), "kind": "sfx", "prompt": prompt, "duration_seconds": _BED_SECONDS,
            "loop": True, "prompt_influence": 0.5}


def _runs(plan: dict[str, Any]) -> list[tuple[str, float, float]]:
    """(location, from, to) for every run of consecutive shots in one place, on the cut's clock."""
    runs: list[list[Any]] = []
    for shot in sorted((s for s in plan["shots"] if not s.get("cut")), key=lambda s: float(s["clock_at"])):
        start, end = float(shot["clock_at"]), float(shot["clock_at"]) + float(shot["trim_seconds"])
        place = shot.get("location")
        if not place:
            continue
        if runs and runs[-1][0] == place and start - runs[-1][2] < 2.0:  # a title card between is the same run
            runs[-1][2] = end
        else:
            runs.append([place, start, end])
    return [(p, a, b) for p, a, b in runs]


def beds(plan: dict[str, Any], bible: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(sources, placements) for the places the cut visits; a run longer than a bed takes it again."""
    if any(src.get("loop") for src in (plan.get("sound") or {}).get("sources") or []):
        return [], []  # the film's own sound already lays a bed per place; a second one would double the room
    places = {loc["id"]: loc for loc in bible.get("locations") or []}
    sources, placements = {}, []
    for place, start, end in _runs(plan):
        if place not in places:
            continue
        sources[place] = bed_source(places[place])
        at = start
        while at < end - 0.05:
            length = min(_BED_SECONDS, end - at)
            placements.append({"source": bed_id(place), "at": round(at, 3), "length": round(length, 3),
                               "gain_db": _BED_GAIN_DB, "fade_in": 0.08, "fade_out": 0.12})
            at += length
    return list(sources.values()), placements


_SEPARATOR_MODEL = "vocals_mel_band_roformer.ckpt"  # Mel-Band RoFormer (Kim): vocals SDR ~12.6


def _separator() -> str | None:
    """audio-separator (python-audio-separator) from $AUDIO_SEPARATOR or PATH; None when it is not installed."""
    return os.environ.get("AUDIO_SEPARATOR") or shutil.which("audio-separator")


def has_audio(clip: Path) -> bool:
    """Whether the clip has a sound track at all (a shot rendered without sound has none); probed once."""
    from ._stage_cache import probed

    return probed(clip, _probe_audio)


def _probe_audio(clip: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(clip)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def without_voice(clip: Path, cache: Path) -> Path | None:
    """The clip's sound with its voice taken out by its contour (a vocal/background split), not by a hole in
    time: the room, the footsteps and the crash under the line stay whole. Cached next to the stems."""
    binary = _separator()
    if not binary:
        return None
    out = cache / f"{clip.stem}.{Path(_SEPARATOR_MODEL).stem}.background.wav"
    legacy = cache / f"{clip.stem}.background.wav"  # kept before the model was in the name: made by this model
    if not out.is_file() and legacy.is_file():
        legacy.replace(out)
    if out.is_file():
        return out
    work = cache / f"{clip.stem}.sep"
    work.mkdir(parents=True, exist_ok=True)
    src = work / "audio.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vn", "-ac", "2", "-ar", "44100", str(src)],
                   check=True, capture_output=True)
    models = os.environ.get("AUDIO_SEPARATOR_MODEL_DIR") or str(Path.home() / ".cache" / "audio-separator")
    done = subprocess.run([binary, str(src), "-m", _SEPARATOR_MODEL, "--model_file_dir", models, "--output_dir",
                           str(work), "--output_format", "WAV"], capture_output=True, text=True)
    # this model names its stems Vocals and Other; anything that is not the voice is the background
    stems = [f for f in work.glob("*.wav") if f != src and "(vocals)" not in f.stem.lower()]
    if done.returncode or not stems:
        shutil.rmtree(work, ignore_errors=True)
        return None
    stems[0].replace(out)
    shutil.rmtree(work, ignore_errors=True)
    return out


def production(shot: dict[str, Any], clip: Path, start: float, speech: list[float] | None, out: Path) -> Path:
    """The clip's sound over its used window, with its own voice cut out; WAV at 48 kHz stereo.

    With a separator installed the voice is removed by its contour and the rest plays at full level; without
    one, the window where the clip speaks is ducked instead. Kept beside it while the clip, its window, its
    speech and the separator are the same (stamps.json)."""
    from . import _stage_cache as sc

    stamps = sc.Stamps(out.parent / "stamps.json")
    stamp = sc.key(sc.file_sig(clip), round(float(start), 3), float(shot["trim_seconds"]), speech,
                   _SEPARATOR_MODEL if _separator() else None, _VOICE_PAD, _PRODUCTION_LUFS)
    if not stamps.fresh(out.name, stamp, out):
        _production(shot, clip, start, speech, out)
        if out.is_file():
            stamps.set(out.name, stamp)
            stamps.save()
    return out


def _production(shot: dict[str, Any], clip: Path, start: float, speech: list[float] | None, out: Path) -> Path:
    seconds = float(shot["trim_seconds"])
    if not has_audio(clip):
        # a silent render keeps its place in the mix as silence; the beds and effects carry the room
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                        "-t", f"{seconds:.3f}", str(out)], check=True, capture_output=True)
        return out
    clean = without_voice(clip, out.parent / "separated")
    af = [f"atrim=start={start:.3f}:end={start + seconds:.3f}", "asetpts=PTS-STARTPTS"]
    if speech and clean is None:
        a = max(0.0, speech[0] - _VOICE_PAD[0] - start)
        b = max(0.0, speech[1] + _VOICE_PAD[1] - start)
        if b > 0:
            # 50 ms ramps at each side of the hole, so the cut reads as the room, not as a click
            mid, half = (a + b) / 2, (b - a) / 2
            # ducked to -18 dB, not cut: a room that vanishes under every line is a hole the ear hears
            af.append(f"volume='0.125+0.875*min(1,max(0,(abs(t-{mid:.3f})-{half:.3f})/0.05))':eval=frame")
    af += ["highpass=f=70", f"loudnorm=I={_PRODUCTION_LUFS}:TP=-8:LRA=7", "aresample=48000",
           "aformat=channel_layouts=stereo", f"apad=whole_dur={seconds:.3f}"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clean or clip), "-vn", "-af", ",".join(af),
                    "-t", f"{seconds:.3f}", str(out)], check=True, capture_output=True)
    return out


def production_placement(source: str, shot: dict[str, Any]) -> dict[str, Any]:
    return {"source": source, "at": float(shot["clock_at"]), "length": float(shot["trim_seconds"]),
            "gain_db": _PRODUCTION_GAIN_DB, "fade_in": 0.02, "fade_out": 0.04}


def transients(stems: list[tuple[Path, float]]) -> list[tuple[float, float]]:
    """(clock time, rise in dB over 50 ms) of every sharp onset in the shots' own sound, 10 ms apart.

    A designed hit (the slap, the ram) belongs where the clip's action actually
    makes its noise, not where the animatic guessed it would be."""
    import numpy as np

    hits = []
    for wav, at in stems:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-ar", "8000",
                              "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32)
        frames = x[: len(x) // 80 * 80].reshape(-1, 80)
        db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-5)
        rise = db[5:] - db[:-5]
        hits += [(round(at + (i + 5) * 0.01, 3), float(r)) for i, r in enumerate(rise) if r > 10]
    return hits


# ── clean-up: one sound at a time, and a silence before the title ─────────────

_MUSIC = ("caper_groove", "caper_bigbeat", "score_main")
_KEEP = _MUSIC + ("record_scratch", "title_impact", "tape_stop")
_GAP = 0.45  # seconds two one-shot sounds must stand apart to be heard as two
_MONTAGE = ("escalation", "montage", "peak", "drop")
_BREATH_BED_DB = -28.0
_RISER_PEAK = 3.4  # seconds into the riser where it is loudest


def _breathes(plan: dict[str, Any]) -> bool:
    """Only a trailer breathes: it has title cards and a title/drop/peak/montage/button act."""
    trailer = plan.get("trailer") or {}
    acts = {a.get("name") for a in trailer.get("acts") or []}
    return bool(trailer.get("title_cards")) and bool(acts & {"title", "drop", "peak", "montage", "button"})


def _host(plan: dict[str, Any], end: float) -> dict[str, Any] | None:
    """The shot carrying the last narrated line before `end`, else the last shot before it."""
    shots = {s["label"]: s for s in plan["shots"] if not s.get("cut")}
    told = [shots[n["shot"]] for n in plan.get("narration") or [] if n.get("shot") in shots
            and float(shots[n["shot"]]["clock_at"]) < end]
    before = [s for s in shots.values() if float(s["clock_at"]) < end]
    return max(told or before, key=lambda s: float(s["clock_at"]), default=None)


def _breath(plan: dict[str, Any]) -> tuple[float, float] | None:
    """(from, to) of the silence before the title: from the start of the shot that carries the last narrated
    line before the last card (else the last shot before it) up to the card."""
    if not _breathes(plan):
        return None  # a film that ends on its picture keeps its sound to the last card; only a trailer breathes
    card = max(plan["trailer"]["title_cards"], key=lambda c: float(c["clock_at"]))
    end = float(card["clock_at"])
    host = _host(plan, end)
    return (float(host["clock_at"]), end) if host else None


class _Cut:
    """The cut's live shots and their acts, asked by clock time."""

    def __init__(self, plan: dict[str, Any]) -> None:
        from . import _trailer_retime as rt

        self.acts = rt._act_of(plan)
        self.shots = {s["label"]: s for s in plan["shots"] if not s.get("cut")}

    def shot_at(self, t: float) -> dict[str, Any] | None:
        return next((s for s in self.shots.values()
                     if float(s["clock_at"]) <= t < float(s["clock_at"]) + float(s["trim_seconds"])), None)

    def montage(self, t: float) -> bool:
        s = self.shot_at(t)
        return bool(s) and self.acts.get(s["label"]) in _MONTAGE


def _thin_montage(placements: list[dict[str, Any]], cut: _Cut) -> list[dict[str, Any]]:
    """In a montage act a silent shot loses its own sound and a bed run shorter than 2 s is dropped."""
    kept = []
    for p in placements:
        src, at = p["source"], float(p["at"])
        if src.startswith("prod_") and cut.montage(at) and not cut.shots.get(src[5:], {}).get("dialogue"):
            continue
        if src.startswith("bed") and cut.montage(at) and float(p.get("length") or 0) < 2.0:
            continue
        kept.append(p)
    return kept


def _second_vocal(p: dict[str, Any], cut: _Cut, voiced: set[str]) -> bool:
    """Whether `p` is a vocal on a montage shot that already has one (marks the shot voiced otherwise)."""
    if not p["source"].startswith("vocal_"):
        return False
    s = cut.shot_at(float(p["at"]))
    if not (s and cut.acts.get(s["label"]) in _MONTAGE):
        return False
    if s["label"] in voiced:
        return True
    voiced.add(s["label"])
    return False


def _rank(p: dict[str, Any], vocals_first: bool = False) -> tuple[int, float]:
    """Story hits first; then cut sounds before vocals in a trailer, vocals before cut sounds in a film (a whoosh
    can go, a character's reaction is the story); earlier first within each."""
    vocal, cut = p["source"].startswith("vocal_"), bool(p.get("cut"))
    tier = 0 if not (vocal or cut) else (1 if vocal == vocals_first else 2)
    return tier, float(p["at"])


def _is_vocal(p: dict[str, Any]) -> bool:
    return p["source"].startswith("vocal_")


def _one_shot(p: dict[str, Any]) -> bool:
    return not p.get("length") and p["source"] not in _KEEP and not p.get("strobe") and not p.get("keep")


def _crowded(p: dict[str, Any], chosen: list[dict[str, Any]], lanes: bool) -> bool:
    """Whether a sound already kept stands within _GAP of `p`; in a film (lanes) a voice and a sound effect sit in
    different bands and are heard together, so each is only crowded by its own kind."""
    at = float(p["at"])
    return any(abs(at - float(q["at"])) < _GAP for q in chosen if not lanes or _is_vocal(q) == _is_vocal(p))


def _space_one_shots(kept: list[dict[str, Any]], cut: _Cut, vocals_first: bool = False) -> list[dict[str, Any]]:
    """One-shot sounds at least _GAP apart: a story hit beats the rest, then a cut sound beats a vocal in a
    trailer. In a film voices and effects are spaced each in their own lane, a vocal before a cut sound.
    A placement marked "keep" is never thinned."""
    one_shots = [p for p in kept if _one_shot(p)]
    chosen: list[dict[str, Any]] = []
    voiced: set[str] = set()
    for p in sorted(one_shots, key=lambda q: _rank(q, vocals_first)):
        if _crowded(p, chosen, vocals_first) or _second_vocal(p, cut, voiced):
            continue
        chosen.append(p)
    drop = {id(p) for p in one_shots} - {id(p) for p in chosen}
    return [p for p in kept if id(p) not in drop]


def _in_breath(p: dict[str, Any], a: float, b: float) -> dict[str, Any] | None:
    """A placement as it plays across the silence (a, b); None when the silence takes it out."""
    src, at = p["source"], float(p["at"])
    end = at + float(p.get("length") or 0)
    if src == "tape_stop":
        return {**p, "at": round(a - 0.55, 3)}  # the score winds down onto the silence
    if src == "title_impact" and at >= a - 0.1:
        return p
    if a <= at < b:
        return {**p, "gain_db": _BREATH_BED_DB} if src.startswith("bed") else None  # a low room, not digital black
    if at < a < end and p.get("length"):
        return {**p, "length": round(a - at, 3), "fade_out": 0.02 if src in _MUSIC else 0.15}
    return p


def _room_under(sound: dict[str, Any], out: list[dict[str, Any]], cut: _Cut, breath: tuple[float, float]) -> None:
    """A bed that ran into the silence was cut at its edge: the room carries on under it, low."""
    a, b = breath
    host = cut.shot_at(a)
    if not (host and host.get("location")):
        return
    known = {src["id"] for src in sound["sources"]} | {p["source"] for p in sound["placements"]}
    covered = any(p["source"].startswith("bed") and float(p["at"]) <= a + 0.05
                  < float(p["at"]) + float(p.get("length") or 0) for p in out)
    if bed_id(host["location"]) in known and not covered:
        out.append({"source": bed_id(host["location"]), "at": a, "length": round(b - a, 3),
                    "gain_db": _BREATH_BED_DB, "fade_in": 0.3, "fade_out": 0.1})


def _release(sound: dict[str, Any], kept: list[dict[str, Any]], cut: _Cut, b: float) -> None:
    """The one sound in the silence (a freeze's camera flash) and the floor under the title's hit."""
    ids = {src["id"] for src in sound["sources"]}
    for shot in cut.shots.values():
        hold = shot.get("freeze")
        if hold and "flash_pop" in ids:
            # the freeze lands on a camera flash: the one sound in the silence
            kept.append({"source": "flash_pop", "at": round(float(shot["clock_at"]) + float(hold["at"]) - 0.25, 3),
                         "gain_db": 2.0, "fade_in": 0.0, "fade_out": 0.05})
    if "sub_drop" in ids:
        # the release: the title's band hit gets the floor under it
        kept.append({"source": "sub_drop", "at": round(b, 3), "gain_db": 1.0, "fade_in": 0.0, "fade_out": 0.3})


def _breathe(sound: dict[str, Any], kept: list[dict[str, Any]], cut: _Cut,
             breath: tuple[float, float]) -> list[dict[str, Any]]:
    """Before the title the score stops and everything with it but a low room; the title's hit is the release."""
    a, b = breath
    if any(src["id"] == "riser" for src in sound["sources"]):
        # the build peaks on the stop: the riser's top lands where the tape winds down
        kept.append({"source": "riser", "at": round(a - 0.55 - _RISER_PEAK, 3), "gain_db": -3.0,
                     "fade_in": 0.3, "fade_out": 0.05})
    out = [q for q in (_in_breath(p, a, b) for p in kept) if q is not None]
    _room_under(sound, out, cut, breath)
    _release(sound, out, cut, b)
    return out


def declutter(sound: dict[str, Any], plan: dict[str, Any]) -> None:
    """The mix thinned to what can be heard.

    The SAME peak stacked a hit, a grunt, a cut sound, a bed and the clip's own noise every 0.3 s: none of them
    read and the whole sounded dirty. Three rules:
      - one-shot sounds stand at least _GAP apart; a story hit beats the rest, a cut sound beats a vocal in a
        trailer and a vocal beats a cut sound in a film; "keep" exempts one; in a montage act a shot keeps one vocal
      - in a montage act a silent shot loses its own sound and a bed run shorter than 2 s is dropped
      - before the title the score stops and everything with it but a low room: the last line lands in silence
        and the title's hit is the release"""
    cut = _Cut(plan)
    kept = _space_one_shots(_thin_montage(sound["placements"], cut), cut, vocals_first=not _breathes(plan))
    breath = _breath(plan)
    sound["placements"] = _breathe(sound, kept, cut, breath) if breath else kept
