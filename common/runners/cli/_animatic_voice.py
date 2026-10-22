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
import re
import sys
import subprocess
from pathlib import Path
from typing import Any

from ..soundtrack import voice_filter
from . import _voice_lines

_MAX_TEMPO = 1.25
_CARRY = 0.0  # a line stays in its shot: carried over the cut it lands on the next face (users heard it as out of sync)
_SPILL = 0.4  # a line may run this far past its cut, as a J-cut into the next shot
_GAP = 0.08
_LINE_LUFS = -16
_GAIN_LIMIT = 12.0
_LEAD_TAGS = re.compile(r"(\s*\[[^\]]*\])*")


def gain_db(item: dict[str, Any]) -> float:
    """A line's or a vocal's own "gain_db" (a step louder or quieter in the voice mix), held to ±12 dB."""
    return max(-_GAIN_LIMIT, min(_GAIN_LIMIT, float(item.get("gain_db") or 0)))


def _entry(line: dict[str, Any], shot: dict[str, Any]) -> dict[str, Any]:
    """A dialogue line placed on the clock of the shot that says it."""
    line_at = float(shot.get("line_at") or 0.3)
    start = float(shot["clock_at"])
    return {**line, "label": shot["label"], "location": shot.get("location"),
            "at": round(start + line_at, 3), "room": float(shot["trim_seconds"]) - line_at + _SPILL,
            "shot_start": start, "shot_end": round(start + float(shot["trim_seconds"]), 3)}


def exchanges(plan: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Dialogue lines grouped into exchanges: speaking shots next to each other IN THE CUT (clock order, a
    restructure may reorder them) from the same screenplay scene. Shots dropped from the cut say nothing."""
    groups: list[list[dict[str, Any]]] = []
    last: tuple[int, Any] | None = None
    order = sorted((s for s in plan["shots"] if not s.get("cut")), key=lambda s: float(s["clock_at"]))
    for pos, shot in enumerate(order):
        said = shot.get("dialogue") or []
        if not said:
            last = None
            continue
        joins = last is not None and pos == last[0] + 1 and shot.get("scene") == last[1]
        for line in said:
            (groups[-1].append(_entry(line, shot)) if joins and groups else groups.append([_entry(line, shot)]))
        last = (pos, shot.get("scene"))
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


def _said(text: str) -> str:
    """The words alone: tags, case, ё and punctuation out."""
    return " ".join(re.sub(r"[\W_]+", " ", re.sub(r"\[[^\]]*\]", " ", text).lower().replace("ё", "е")).split())


def _text(line: dict[str, Any], accent: str = "") -> str:
    """The performance the voice-performance chain wrote, while it still says the line; a line edited since is
    read as it now stands, after the performance's leading tags. Else the delivery tag before the line."""
    performance = line.get("performance")
    if performance and _said(performance) == _said(line["line"]):
        return performance
    if performance:
        # the take is cached by its text: a stale performance would come back in the old words
        return f"{_LEAD_TAGS.match(performance).group(0).strip()} {line['line']}".strip()
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


def _request(group: list[dict[str, Any]], voices: dict[str, str],
             bible: dict[str, Any] | None) -> tuple[list[dict[str, str]], dict[str, Any] | None]:
    """What the exchange's take is asked with: each line's text and voice, and the room."""
    accents = _accents(bible or {})
    inputs = [{"text": _text(line, accents.get(line["who"], "")), "voice_id": voices[line["who"]]} for line in group]
    return inputs, effects(group, bible or {})


def _take_key(inputs: list[dict[str, str]], fx: dict[str, Any] | None, language: str | None) -> str:
    raw = [inputs, fx, "eleven_v4"] + ([language] if language else [])
    return hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:12]


def _take_paths(group: list[dict[str, Any]], voices: dict[str, str], cache: Path, language: str | None,
                bible: dict[str, Any] | None) -> tuple[tuple[Path, Path], tuple[Path, Path]]:
    """((take, timestamps) under the key, the same under the older key without the language)."""
    inputs, fx = _request(group, voices, bible)
    key, old = _take_key(inputs, fx, language), _take_key(inputs, fx, None)
    return (cache / f"{key}.mp3", cache / f"{key}.json"), (cache / f"{old}.mp3", cache / f"{old}.json")


def take_kept(group: list[dict[str, Any]], voices: dict[str, str], cache: Path, language: str | None,
              bible: dict[str, Any] | None = None) -> bool:
    """Whether the exchange's take is on disk, under either key, or every line of it was read in another take:
    reading it again buys nothing."""
    if any(all(f.is_file() for f in pair) for pair in _take_paths(group, voices, cache, language, bible)):
        return True
    return _read_before(group, voices, cache, language, bible) is not None


def _line_keys(group: list[dict[str, Any]], voices: dict[str, str], language: str | None,
               bible: dict[str, Any] | None) -> list[str]:
    """What each line of the group alone is asked with, as a key (see _voice_lines)."""
    inputs, fx = _request(group, voices, bible)
    return [_take_key([item], fx, language) for item in inputs]


def _read_before(group: list[dict[str, Any]], voices: dict[str, str], cache: Path, language: str | None,
                 bible: dict[str, Any] | None) -> list[Path] | None:
    return _voice_lines.read_before(cache, _line_keys(group, voices, language, bible))


def take_files(group: list[dict[str, Any]], voices: dict[str, str], cache: Path, language: str | None,
               bible: dict[str, Any] | None = None) -> tuple[Path, Path]:
    """(take, its timestamps) of the exchange, kept by text, voices, room, model and language. A take kept
    before the language was in its key is moved to its keyed name, never bought again."""
    (take, marks), legacy = _take_paths(group, voices, cache, language, bible)
    if not take.is_file() and all(f.is_file() for f in legacy):
        legacy[0].replace(take)
        legacy[1].replace(marks)
    return take, marks


def read_exchange(group: list[dict[str, Any]], voices: dict[str, str], cache: Path,
                  language: str | None, bible: dict[str, Any] | None = None) -> list[Path]:
    """One take for the whole exchange, cut into one clip per line (cached by text, voices and language)."""
    from ..providers.elevenlabs import dialogue

    inputs, fx = _request(group, voices, bible)
    cache.mkdir(parents=True, exist_ok=True)
    before = _read_before(group, voices, cache, language, bible)
    if before is not None:
        return before  # every line was read before, in this exchange or another: that first reading
    take, marks = take_files(group, voices, cache, language, bible)
    if not (take.is_file() and marks.is_file()):
        audio, segments = _clean_take(dialogue, inputs, language, fx)
        take.write_bytes(audio)
        marks.write_text(json.dumps(segments), encoding="utf-8")
    clips = _split(take, json.loads(marks.read_text(encoding="utf-8")), len(group), cache / take.stem)
    _voice_lines.remember(cache, _line_keys(group, voices, language, bible), clips)
    return clips


_NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
        "8": "eight", "9": "nine", "10": "ten", "98": "ninety eight", "512": "five hundred twelve"}


def _words(text: str) -> list[str]:
    """Spoken words, so a script and what Scribe heard compare: tags out, digits spelt, '%' and '.' said."""
    import re

    text = re.sub(r"\[[^\]]*\]", " ", text.lower()).replace("%", " percent").replace("ё", "е")
    text = re.sub(r"(\d)\.(\d)", r"\1 point \2", text)
    text = re.sub(r"\d+", lambda m: f" {_NUM.get(m.group(0), m.group(0))} ", text)
    # letters of any script: a Russian take is checked too, not read as having no words at all
    return re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)*", text.replace("-", " "))


def _errors(want: list[str], heard: list[str]) -> int:
    """Word edit distance: a repeat, a dropped word and a substituted one all count."""
    row = list(range(len(heard) + 1))
    for i, w in enumerate(want, 1):
        prev, row[0] = row[0], i
        for j, h in enumerate(heard, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (w != h))
    return row[-1]


def _clean_take(dialogue, inputs: list[dict[str, str]], language: str | None, fx) -> tuple[bytes, list]:
    """A take whose words are the script's. Eleven v4 sometimes repeats a phrase around an ellipsis or a dash
    ("After six — it's me" came back "After six, after six, it's me"); Scribe hears every take, and one that
    adds or drops words is read again, the second time with ellipses and dashes turned into [pause]."""
    import re

    from ..providers.elevenlabs import transcribe

    want = [w for item in inputs for w in _words(item["text"])]
    plain = [{**item, "text": re.sub(r"\s*(\.\.\.|…|—|--)\s*", " [pause] ", item["text"])} for item in inputs]
    best = None
    for attempt, batch in enumerate((inputs, plain, plain)):
        audio, segments = dialogue(batch, language=language, effects=fx)
        heard = [w for x in transcribe(audio, language) if x.get("type", "word") == "word" for w in _words(x["text"])]
        errors = _errors(want, heard)
        if best is None or errors < best[0]:
            best = (errors, audio, segments)
        if errors <= len(want) // 15:
            break
        print(f"  take {attempt + 1}: {errors} word errors in {len(want)}; reading again", file=sys.stderr)
    return best[1], best[2]


def _span(segments: list[dict[str, Any]], n: int) -> tuple[float, float | None]:
    """Where input line n starts and ends in the take."""
    own = [s for s in segments if int(s["dialogue_input_index"]) == n]
    if not own:
        return 0.0, None
    return min(s["start_time_seconds"] for s in own), max(s["end_time_seconds"] for s in own)


def _split(take: Path, segments: list[dict[str, Any]], count: int, stem: Path) -> list[Path]:
    """One clip per input line of the take, from its voice segments; a clip already cut the same way is kept."""
    from . import _stage_cache as sc

    stamps = sc.Stamps(stem.parent / "split.json")
    spans = [_span(segments, n) for n in range(count)]
    clips = []
    for n, (start, end) in enumerate(spans):
        # The take's segment ends run into the next speaker's first syllable; stop where they start.
        later = [s for s, _ in spans[n + 1:] if s > start]
        if later and (end is None or end > later[0] - 0.02):
            end = later[0] - 0.02
        clip = stem.with_name(f"{stem.name}-{n}.wav")
        stamp = sc.key(sc.file_sig(take), start, end, _TRIM)
        if not stamps.fresh(clip.name, stamp, clip):
            _cut(take, clip, start, end)
            stamps.set(clip.name, stamp)
        clips.append(clip)
    stamps.save()
    return clips


def _accents(bible: dict[str, Any]) -> dict[str, str]:
    """speaker → accent tag of their Voice Library voice ("light Vietnamese accent")."""
    people = [*(bible.get("cast") or []), *(bible.get("offscreen_voices") or [])]
    return {p["id"]: (p.get("voice_library") or {}).get("accent", "") for p in people}


# Ends trimmed, and a dead gap inside the line held to 0.4 s: v4 acts an ellipsis as a full stop and a
# [clears throat] as a scene, and a 3 s gap splits a line across two shots. Only true silence counts
# (-48 dB) and only past 0.6 s: a tighter trim (-36 dB, 0.18 s) cut the breaths and every actor's pause
# out of the SAME lines and left them choppy, a voice with holes in it.
_TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "silenceremove=stop_periods=-1:stop_duration=0.6:stop_threshold=-48dB:stop_silence=0.4")


def _cut(take: Path, clip: Path, start: float, end: float | None) -> None:
    """The line's stretch of the take, silence trimmed from both ends."""
    window = ["-ss", f"{max(0.0, start - 0.03):.3f}"] + (["-to", f"{end:.3f}"] if end else [])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *window, "-i", str(take), "-af", _TRIM,
                    "-ar", "48000", "-ac", "2", str(clip)], check=True, capture_output=True)


def _seconds(path: Path) -> float:
    """The file's length, probed once per version of the file."""
    from ._stage_cache import probed

    return probed(path, _probe)


def _probe(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip() or 0)


def _room(line: dict[str, Any], later: list[tuple[dict[str, Any], Path]]) -> float:
    """Seconds the line may play: its shot's room, and past the cut (a J/L cut, up to _CARRY s) while nobody
    else speaks yet. An acted take is longer than the generation's own speech; pressing it in kills the acting."""
    if not later:
        return line["room"] + _CARRY
    until_next = later[0][0]["at"] - line["at"] - _GAP
    return max(line["room"], min(until_next, line["room"] + _CARRY))


def say_rushed(line: dict[str, Any], tempo: float) -> None:
    """A rushed line loses its acting: say which, so the shot can be given room instead."""
    if tempo > 1.08:
        print(f"  {line.get('label', '?')}: line sped up x{tempo:.2f} to fit its shot", file=sys.stderr)


def _inside_shot(line: dict[str, Any], length: float) -> float:
    """Where the line starts: on the mouth (or its plan time), moved earlier when even at _MAX_TEMPO it would run
    past its shot: a voice running on over the cut lands on the next face, which reads as out of sync, worse than
    a start a little before the mouth. Never before the shot itself."""
    if "shot_end" not in line:
        return line["at"]
    latest = line["shot_end"] - length / _MAX_TEMPO
    return round(max(line["shot_start"] + 0.05, min(line["at"], latest)), 3)


def fit(lines: list[dict[str, Any]], clips: list[Path], say: bool = True) -> list[tuple[Path, float, float]]:
    """(clip, start on the clock, tempo) per line: sped up to fit its shot, never overlapping the line before.
    `say=False` leaves the rushed lines unsaid, for a placement that may be laid again."""
    placed, free_at = [], 0.0
    ordered = sorted(zip(lines, clips), key=lambda pair: pair[0]["at"])
    for n, (line, clip) in enumerate(ordered):
        length = _seconds(clip)
        at = max(_inside_shot(line, length), free_at + _GAP)
        room = line["shot_end"] - at if "shot_end" in line else _room(line, ordered[n + 1:])
        tempo = min(_MAX_TEMPO, max(1.0, length / max(room, 0.3)))
        if say:
            say_rushed(line, tempo)
        placed.append((clip, at, tempo))
        free_at = at + length / tempo
    return placed


def _level(clip: Path, gain: float) -> str:
    """The line's lift after loudnorm: its own gain_db, plus 5 dB for a one-word line."""
    # loudnorm measures under ~1 s badly and leaves a one-word line ("На.", "Ой!") under the score
    lift = gain + (5.0 if _seconds(clip) < 1.2 else 0.0)
    return f"volume={lift:g}dB,alimiter=limit=0.89," if lift else ""


def voice_pitch(bible: dict[str, Any], who: str) -> float:
    """The cast member's "voice_pitch" in semitones: a voice that reads older than the part (a library child voice
    that comes out adult in a dialogue take) lifted in the mix, no new voice needed."""
    return float(next((c.get("voice_pitch") or 0 for c in bible.get("cast") or [] if c["id"] == who), 0))


def voice_formant(bible: dict[str, Any], who: str) -> float:
    """The cast member's "voice_formant" in semitones: the throat made smaller apart from the pitch, with the child
    EQ (a child's timbre, not only a higher adult)."""
    return float(next((c.get("voice_formant") or 0 for c in bible.get("cast") or [] if c["id"] == who), 0))


def mix(placed: list[tuple[Path, float, float]], total: float, out: Path, gains: list[float] | None = None,
        pitches: list[tuple[float, float]] | None = None) -> None:
    """Every line at one loudness (moved by its gain_db, in `gains`), at its time and tempo, its speaker's pitch
    and throat ((semitones, formant) per line, in `pitches`), into one WAV of the cut's length."""
    inputs = ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    chains = []
    for n, (clip, at, tempo) in enumerate(placed, start=1):
        inputs += ["-i", str(clip)]
        ms = int(at * 1000)
        speed = f"atempo={tempo:.3f}," if tempo > 1.001 else ""
        shift, throat = (pitches[n - 1] if pitches else (0.0, 0.0))
        speed += f"{voice_filter(shift, throat)}," if (shift or throat) else ""
        lift = _level(clip, gains[n - 1] if gains else 0.0)
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,{speed}"
                      f"loudnorm=I={_LINE_LUFS}:TP=-1.5:LRA=11,{lift}aresample=48000,adelay={ms}|{ms}[l{n}]")
    lines = "".join(f"[l{n}]" for n in range(1, len(placed) + 1))
    graph = ";".join(chains + [f"[0:a]{lines}amix=inputs={len(placed) + 1}:normalize=0:duration=first[out]"])
    from ._stage_cache import run_once

    run_once(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
              "-c:a", "pcm_s16le", str(out)], out)
