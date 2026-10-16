"""Scratch dialogue for an animatic — the cast's own voices, exchanges read as exchanges, cut to the clock.

A line read alone has nobody to answer, so it comes out flat: a stand-in voice
reading words. Lines that answer each other ("ninety-eight point seven." /
"Percent?" / "Confidence.") are read here in one ElevenLabs Text to Dialogue
take, each speaker in the voice `reel_cast` designed for them, then cut apart
at the take's own timestamps and laid on the trailer clock.

A line is fitted to its shot: silence trimmed off both ends, sped up (pitch
kept, at most 1.25×) when it runs longer than the shot leaves it, and never
started before the previous line has finished.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

_MAX_TEMPO = 1.25
_SPILL = 0.4  # a line may run this far past its cut, as a J-cut into the next shot
_GAP = 0.08
_LINE_LUFS = -16


def exchanges(plan: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Dialogue lines grouped into exchanges: consecutive speaking shots from the same screenplay scene."""
    groups: list[list[dict[str, Any]]] = []
    last: tuple[int, Any] | None = None
    for shot in sorted(plan["shots"], key=lambda s: int(s["index"])):
        said = shot.get("dialogue") or []
        if not said:
            last = None
            continue
        for line in said:
            entry = {**line, "label": shot["label"], "location": shot.get("location"),
                     "at": round(float(shot["clock_at"]) + float(shot.get("line_at") or 0.3), 3),
                     "room": float(shot["trim_seconds"]) - float(shot.get("line_at") or 0.3) + _SPILL}
            joins = last is not None and int(shot["index"]) == last[0] + 1 and shot.get("scene") == last[1]
            (groups[-1].append(entry) if joins and groups else groups.append([entry]))
        last = (int(shot["index"]), shot.get("scene"))
    return groups


def voices_for(bible: dict[str, Any], speakers: set[str], library: list[dict[str, Any]],
               pick) -> dict[str, str]:
    """The designed voice of every speaker who has one (cast.json), a library stand-in for the rest."""
    state_path = Path(bible["_dir"]) / "cast.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    designed = {who: state[f"{who}:voice"]["voice_id"] for who in speakers
                if state.get(f"{who}:voice", {}).get("voice_id")}
    rest = [c for c in bible.get("cast") or [] if c["id"] in speakers - set(designed)]
    rest += [{"id": who, "identity": "woman, 30" if who == "vo" else "man, 40"}
             for who in sorted(speakers - set(designed) - {c["id"] for c in rest})]
    return {**pick(rest, library), **designed} if rest else designed


def _text(line: dict[str, Any], accent: str = "") -> str:
    """The performance the voice-performance chain wrote; else the delivery tag before the line."""
    if line.get("performance"):
        return line["performance"]
    lead = " ".join(f"[{tag}]" for tag in (accent, line.get("delivery")) if tag)
    return f"{lead} {line['line']}".strip()


def effects(group: list[dict[str, Any]], bible: dict[str, Any]) -> dict[str, Any] | None:
    """The room the exchange is in (the location's acoustics) and any device a speaker is heard through."""
    rooms = {l["id"]: l.get("acoustics") for l in bible.get("locations") or []}
    off = {v["id"]: v.get("audio_effects") or {} for v in bible.get("offscreen_voices") or []}
    out = {"environment_id": rooms[group[0]["location"]]} if rooms.get(group[0].get("location")) else {}
    for line in group:
        out.update(off.get(line["who"], {}))
    if out.get("filter_preset_id"):
        out.pop("environment_id", None)  # a recording is heard dry from its speaker, not in the room
    return out or None


def read_exchange(group: list[dict[str, Any]], voices: dict[str, str], cache: Path,
                  language: str | None, bible: dict[str, Any] | None = None) -> list[Path]:
    """One take for the whole exchange, cut into one clip per line (cached by text and voices)."""
    from ..providers.elevenlabs import dialogue

    accents = _accents(bible or {})
    inputs = [{"text": _text(line, accents.get(line["who"], "")), "voice_id": voices[line["who"]]} for line in group]
    fx = effects(group, bible or {})
    key = hashlib.sha256(json.dumps([inputs, fx, "eleven_v4"], sort_keys=True).encode()).hexdigest()[:12]
    take, marks = cache / f"{key}.mp3", cache / f"{key}.json"
    cache.mkdir(parents=True, exist_ok=True)
    if not (take.is_file() and marks.is_file()):
        audio, segments = dialogue(inputs, language=language, effects=fx)
        take.write_bytes(audio)
        marks.write_text(json.dumps(segments), encoding="utf-8")
    return _split(take, json.loads(marks.read_text(encoding="utf-8")), len(group), cache / key)


def _span(segments: list[dict[str, Any]], n: int) -> tuple[float, float | None]:
    """Where input line n starts and ends in the take."""
    own = [s for s in segments if int(s["dialogue_input_index"]) == n]
    if not own:
        return 0.0, None
    return min(s["start_time_seconds"] for s in own), max(s["end_time_seconds"] for s in own)


def _split(take: Path, segments: list[dict[str, Any]], count: int, stem: Path) -> list[Path]:
    """One clip per input line of the take, from its voice segments."""
    spans = [_span(segments, n) for n in range(count)]
    clips = []
    for n, (start, end) in enumerate(spans):
        # The take's segment ends run into the next speaker's first syllable; stop where they start.
        later = [s for s, _ in spans[n + 1:] if s > start]
        if later and (end is None or end > later[0] - 0.02):
            end = later[0] - 0.02
        clip = stem.with_name(f"{stem.name}-{n}.wav")
        _cut(take, clip, start, end)
        clips.append(clip)
    return clips


def _accents(bible: dict[str, Any]) -> dict[str, str]:
    """speaker → accent tag of their Voice Library voice ("light Vietnamese accent")."""
    people = [*(bible.get("cast") or []), *(bible.get("offscreen_voices") or [])]
    return {p["id"]: (p.get("voice_library") or {}).get("accent", "") for p in people}


def _cut(take: Path, clip: Path, start: float, end: float | None) -> None:
    """The line's stretch of the take, silence trimmed from both ends."""
    window = ["-ss", f"{max(0.0, start - 0.03):.3f}"] + (["-to", f"{end:.3f}"] if end else [])
    # Ends trimmed, and every pause inside the line held to 0.25 s: v4 acts an ellipsis
    # as a full stop and a [clears throat] as a scene, and a 3 s gap splits a line across two shots.
    trim = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-42dB:stop_silence=0.25")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *window, "-i", str(take), "-af", trim,
                    "-ar", "48000", "-ac", "2", str(clip)], check=True, capture_output=True)


def _seconds(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip() or 0)


def fit(lines: list[dict[str, Any]], clips: list[Path]) -> list[tuple[Path, float, float]]:
    """(clip, start on the clock, tempo) per line: sped up to fit its shot, never overlapping the line before."""
    placed, free_at = [], 0.0
    for line, clip in sorted(zip(lines, clips), key=lambda pair: pair[0]["at"]):
        length = _seconds(clip)
        tempo = min(_MAX_TEMPO, max(1.0, length / max(line["room"], 0.3)))
        at = max(line["at"], free_at + _GAP)
        placed.append((clip, at, tempo))
        free_at = at + length / tempo
    return placed


def mix(placed: list[tuple[Path, float, float]], total: float, out: Path) -> None:
    """Every line at one loudness, at its time and tempo, into one WAV of the cut's length."""
    inputs = ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    chains = []
    for n, (clip, at, tempo) in enumerate(placed, start=1):
        inputs += ["-i", str(clip)]
        ms = int(at * 1000)
        speed = f"atempo={tempo:.3f}," if tempo > 1.001 else ""
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,{speed}"
                      f"loudnorm=I={_LINE_LUFS}:TP=-1.5:LRA=11,aresample=48000,adelay={ms}|{ms}[l{n}]")
    lines = "".join(f"[l{n}]" for n in range(1, len(placed) + 1))
    graph = ";".join(chains + [f"[0:a]{lines}amix=inputs={len(placed) + 1}:normalize=0:duration=first[out]"])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-c:a", "pcm_s16le", str(out)], check=True, capture_output=True)
