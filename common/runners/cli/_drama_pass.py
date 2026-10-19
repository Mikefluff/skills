"""Apply a DRAMA PASS (drama-system-prompt.md) to a rendered trailer: recut, music, lines, and the human sound.

The pass is written by one LLM call against clips that already exist, so applying it costs nothing but the
voices: a new order and new lengths for part of the cut (the clock after it moves with it, title cards stay
behind their shot), the designed effects of each shot travel with the shot, the score in the recut stretch is
laid again from the pass's cues (cut, in, hit), flat lines get the new performance, and the vocals (breaths,
efforts, screams, a crowd) go into plan["vocals"] for the cut to voice and place.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_MUSIC = ("caper_groove", "caper_bigbeat", "score_main")
_SPLIT = 0.6  # a cue this close to the start of a music segment does not start a new one


def _lay(order: list[str], shots: dict[str, dict], lengths: dict[str, Any], cards: dict, at: float) -> float:
    """The clock laid along `order` from `at`, each card behind its shot; returns where the stretch ends."""
    for lab in order:
        shot = shots[lab]
        shot["clock_at"], shot["trim_seconds"] = round(at, 3), float(lengths.get(lab, shot["trim_seconds"]))
        at += shot["trim_seconds"]
        if lab in cards:
            cards[lab]["clock_at"] = round(at, 3)
            at += float(cards[lab]["seconds"])
    return at


def _shift_after(plan: dict[str, Any], cards: dict, moved: dict, end: float, delta: float) -> None:
    """Everything after the stretch moves by what the stretch gained or lost."""
    for shot in plan["shots"]:
        if shot["label"] not in moved and float(shot["clock_at"]) >= end - 0.01:
            shot["clock_at"] = round(float(shot["clock_at"]) + delta, 3)
    for card in cards.values():
        if card.get("after") not in moved and float(card["clock_at"]) >= end - 0.01:
            card["clock_at"] = round(float(card["clock_at"]) + delta, 3)


def recut(plan: dict[str, Any], cut: dict[str, Any]) -> float:
    """New order and lengths from the first label of `cut["order"]` on; returns where the recut starts."""
    shots = {s["label"]: s for s in plan["shots"]}
    order = cut["order"]
    start = float(shots[order[0]]["clock_at"])
    old = {lab: (float(shots[lab]["clock_at"]), float(shots[lab]["trim_seconds"])) for lab in order}
    cards = {c.get("after"): c for c in (plan.get("trailer") or {}).get("title_cards") or []}
    # where the stretch ended: its last shot or the card behind it, as they stood before the recut
    end_old = max([a + d for a, d in old.values()]
                  + [float(c["clock_at"]) + float(c["seconds"]) for lab, c in cards.items() if lab in order])
    delta = _lay(order, shots, cut["lengths"], cards, start) - end_old
    _move_effects(plan, old, start, end_old, delta)
    _shift_after(plan, cards, old, end_old, delta)
    plan["sound"]["total_seconds"] = round(float(plan["sound"]["total_seconds"]) + delta, 3)
    return start


def _move_effects(plan: dict[str, Any], old: dict[str, tuple[float, float]], start: float, end: float,
                  delta: float) -> None:
    """Every designed effect inside the stretch rides with the shot it sat in (same offset, clamped to the new
    length); music and room beds there are dropped (the cues and the beds lay them again); everything after
    the stretch moves by `delta`."""
    shots = {s["label"]: s for s in plan["shots"]}
    kept = []
    for p in plan["sound"]["placements"]:
        t = float(p["at"])
        if t < start - 0.05:
            kept.append(p)
            continue
        if t >= end - 0.01:
            kept.append({**p, "at": round(t + delta, 3)})
            continue
        if p["source"] in _MUSIC or p["source"].startswith("room_") or p["source"] == "data_hum":
            continue
        home = next((lab for lab, (a, d) in old.items() if a - 0.3 <= t < a + d), None)
        if home is None:
            continue  # sat on a card or between: the cues re-lay the hits
        shot = shots[home]
        offset = min(t - old[home][0], max(0.0, float(shot["trim_seconds"]) - 0.1))
        kept.append({**p, "at": round(float(shot["clock_at"]) + offset, 3)})
    plan["sound"]["placements"] = kept


@dataclass
class _Score:
    """Where the score is laid from, where the groove stood there, and the montage's span."""
    start: float
    playing: float | None
    m0: float
    m1: float


def _montage(plan: dict[str, Any]) -> tuple[float, float]:
    """The clock span of the montage (or the peak); far off when there is none."""
    acts = {a.get("name"): a for a in (plan.get("trailer") or {}).get("acts") or []}
    shots = {s["label"]: s for s in plan["shots"]}
    montage = acts.get("montage") or acts.get("peak") or {}
    m0 = float(shots[montage["from"]]["clock_at"]) if montage.get("from") in shots else 1e9
    m1 = (float(shots[montage["to"]]["clock_at"]) + float(shots[montage["to"]]["trim_seconds"])
          if montage.get("to") in shots else 1e9)
    return m0, m1


def _cue(cue: dict[str, Any], seg_start: float | None, sc: _Score) -> tuple[float | None, list[dict]]:
    """One cue against the segment playing: returns the new segment start and the placements it lays."""
    t, do = float(cue["at"]), cue["do"]
    if do == "hit":
        # the groove slams back in on the hit
        return (t if seg_start is None else seg_start), [{"source": "title_impact", "at": t, "gain_db": 2}]
    if do == "in" and seg_start is None:
        return t, []
    if do == "cut" and seg_start is not None:
        out = _segment(seg_start, t, sc)
        if "scratch" in (cue.get("why") or ""):
            out.append({"source": "record_scratch", "at": round(t - 0.25, 3), "gain_db": 0})
        return None, out
    return seg_start, []


def music(plan: dict[str, Any], cues: list[dict[str, Any]], start: float, end: float | None = None) -> None:
    """The score from `start` on, from the pass's cues: "in" starts a segment, "cut" ends it with a scratch
    when the cue says so, "hit" is the title impact. A segment in the montage plays the big beat."""
    playing = _offset_at(plan, start)
    sc = _Score(start, playing, *_montage(plan))
    seg_start = start if playing is not None else None
    placements = plan["sound"]["placements"]
    for cue in sorted(cues, key=lambda c: c["at"]):
        seg_start, laid = _cue(cue, seg_start, sc)
        placements += laid
    if seg_start is not None:
        placements += _segment(seg_start, end or float(plan["sound"]["total_seconds"]), sc)


def _segment(a: float, b: float, sc: _Score) -> list[dict]:
    if b - a < 0.2:
        return []
    if a < sc.m0 < b:  # the score changes gear where the montage starts
        return _segment(a, sc.m0, sc) + _segment(sc.m0, b, sc)
    big = sc.m0 - 0.1 <= a < sc.m1
    offset = (a - sc.m0) if big else ((sc.playing or 0.0) + (a - sc.start))
    return [{"source": "caper_bigbeat" if big else "caper_groove", "at": round(a, 3), "offset": round(max(0, offset), 3),
             "length": round(b - a, 3), "gain_db": 1 if big else -3, "duck": True, "fade_in": 0.01, "fade_out": 0.03}]


def _offset_at(plan: dict[str, Any], t: float) -> float | None:
    """Where in the groove the score is at clock `t`, from the placements before the recut."""
    for p in plan["sound"]["placements"]:
        if p["source"] == "caper_groove" and float(p["at"]) <= t < float(p["at"]) + float(p.get("length") or 1e9):
            return float(p.get("offset") or 0) + t - float(p["at"])
    return None


def lines(plan: dict[str, Any], performances: list[dict[str, Any]]) -> None:
    shots = {s["label"]: s for s in plan["shots"]}
    for item in performances:
        if shots.get(item["shot"], {}).get("dialogue"):
            shots[item["shot"]]["dialogue"][0]["performance"] = item["performance"]


# A vocal written as tags alone ("[groaning in pain]") has no text for Eleven v4 to voice; it gets the sound
# the tag names, spelt out.
_SOUNDS = [("pant", "Hah... hah... hah..."), ("sob", "Hhh... hh..."), ("sigh", "Haaah..."), ("laugh", "Hm. Hm."),
           ("scream", "Aaaah!"), ("groan", "Nnngh..."), ("grunt", "Hngh!"), ("strain", "Nngh—"),
           ("gasp", "Hh!"), ("breath", "Hhhh..."), ("exhale", "Hhh."), ("wince", "Tss—")]


def spoken(text: str) -> str:
    """The vocal's text with something to voice: tags alone get the sound they name."""
    import re

    if re.sub(r"\[[^\]]*\]", "", text).strip(" .—-"):
        return text
    tags = text.lower()
    return f"{text} " + next((sound for key, sound in _SOUNDS if key in tags), "Hhh...")


def _clean_vocal(vocal: dict[str, Any], voice_id: str):
    """A vocal whose words are its own: a breath must not come back as "Thank you" (it did, on a sharp intake)."""
    from .. import config
    from ..providers.elevenlabs import transcribe
    from ._animatic_voice import _errors, _words

    want = _words(vocal["text"])
    for _ in range(3):
        result = config.get_provider("eleven-tts").generate(spoken(vocal["text"]), voice_id=voice_id,
                                                            model_id="eleven_v4")
        heard = [w for x in transcribe(result.content) if x.get("type", "word") == "word"
                 for w in _words(x["text"]) if len(w) > 2]
        if _errors(want, heard) <= max(1, len(want) // 4):
            return result
    return None


def vocal_file(vocal: dict[str, Any], out: Path) -> Path:
    key = hashlib.sha256(f"{vocal['who']}|{vocal['text']}".encode()).hexdigest()[:12]
    return out / "sound" / "vocals" / f"{vocal['who']}-{key}.mp3"


def voice(vocals: list[dict[str, Any]], voices: dict[str, str], out: Path) -> dict[int, Path]:
    """Each vocal voiced once (cached by who and text): a cast member on Eleven v4 in their own voice, the
    crowd as a sound effect. Returns index → file."""
    from .. import config

    files = {}
    for n, vocal in enumerate(vocals):
        path = vocal_file(vocal, out)
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            if vocal["who"] == "crowd":
                result = config.get_provider("eleven-sfx").generate(
                    f"A crowd, {vocal['text'].strip('[]')}, close, no music", duration_seconds=2.0)
            elif vocal["who"] in voices:
                result = _clean_vocal(vocal, voices[vocal["who"]])
                if result is None:
                    continue  # it kept saying words it was never given: no vocal beats a wrong one
            else:
                continue
            path.write_bytes(result.content)
        files[n] = path
    return files


def placements(plan: dict[str, Any], files: dict[int, Path]) -> list[dict[str, Any]]:
    shots = {s["label"]: s for s in plan["shots"]}
    out = []
    for n, path in files.items():
        vocal = plan["vocals"][n]
        shot = shots[vocal["shot"]]
        if shot.get("cut"):
            continue
        out.append({"source": f"vocal_{n}", "at": round(float(shot["clock_at"]) + float(vocal["at"]), 3),
                    "gain_db": -3 if vocal["who"] == "crowd" else 1, "fade_in": 0.01, "fade_out": 0.05})
    return out


def cut_sounds(plan: dict[str, Any], design: dict[str, Any]) -> None:
    """A CUT SOUNDS design into the plan: its palette as sound sources, one placement per scored cut (at the
    incoming shot's clock plus the design's offset). The generic whooshes it replaces are removed."""
    sound = plan["sound"]
    sound["placements"] = [p for p in sound["placements"] if p["source"] not in ("whip_whoosh", "crash_swish")
                           and not p["source"].startswith("cut_")]
    ids = {s["id"] for s in sound["sources"]}
    for src in design["palette"]:
        if src["id"] not in ids:
            sound["sources"].append({"id": src["id"], "kind": "sfx", "prompt": src["prompt"],
                                     "duration_seconds": float(src.get("duration_seconds", 1.0)),
                                     "prompt_influence": 0.6})
    shots = {s["label"]: s for s in plan["shots"]}
    for cut in design["cuts"]:
        shot = shots.get(cut["into"])
        if shot and cut.get("sound"):
            sound["placements"].append({"source": cut["sound"], "cut": cut["into"],
                                        "at": round(max(0.0, float(shot["clock_at"]) + float(cut.get("offset", 0))), 3),
                                        "gain_db": float(cut.get("gain_db", -4))})


def narration_files(plan: dict[str, Any], voices: dict[str, str], out: Path) -> list[tuple[Path, float]]:
    """The narrator's lines voiced (cached like the vocals) with their clock times."""
    import subprocess

    who = plan.get("narrator") or "minh"
    lines = plan.get("narration") or []
    shots = {x["label"]: x for x in plan["shots"]}
    # a line may name its own speaker ("who"): an off-screen voice laid like the narrator's, no mouth to match
    files = voice([{"who": n.get("who") or who, "text": n["text"]} for n in lines], voices, out)
    placed, free = [], 0.0
    for i in sorted(files):
        # one voice, one line at a time: a line waits for the one before it to finish
        # anchored to its shot ("offset" into it), so a retime that moves the shot moves the line
        line = lines[i]
        at = (float(shots[line["shot"]]["clock_at"]) + float(line["offset"])) if "offset" in line else float(line["at"])
        at = max(at, free + 0.15)
        length = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                       "csv=p=0", str(files[i])], capture_output=True, text=True).stdout or 0)
        placed.append((files[i], at))
        free = at + length
    return placed


def mix_narration(dialogue: Path, lines: list[tuple[Path, float]]) -> None:
    """The narration laid into the dialogue track, so the score ducks under it as under any line."""
    import subprocess

    if not lines:
        return
    inputs, chains = ["-i", str(dialogue)], []
    for n, (path, at) in enumerate(lines, start=1):
        inputs += ["-i", str(path)]
        # a trailer narrator sits on the lens: proximity low end, presence, hard compression, a step louder
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=80,"
                      f"equalizer=f=140:t=q:w=1:g=3,equalizer=f=3200:t=q:w=1.2:g=3.5,"
                      f"acompressor=threshold=-22dB:ratio=5:attack=4:release=110:makeup=3,loudnorm=I=-14:TP=-1.5,"
                      f"adelay={int(at * 1000)}:all=1[n{n}]")
    mixed = "".join(f"[n{n}]" for n in range(1, len(lines) + 1))
    graph = ";".join(chains) + f";[0:a]{mixed}amix=inputs={len(lines) + 1}:normalize=0:duration=first[out]"
    tmp = dialogue.with_name(dialogue.stem + ".vo.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    str(tmp)], check=True, capture_output=True)
    tmp.replace(dialogue)


def _new_shots(plan: dict[str, Any], shots: dict[str, dict], new_shots: list[dict], next_index: int) -> list[str]:
    """New shots added to the plan (to be boarded and rendered); returns their labels."""
    new = []
    for n, ns in enumerate(new_shots):
        shot = {"index": next_index + n, "label": ns["label"], "scene": ns.get("scene"), "cast": ns.get("cast") or [],
                "location": ns.get("location"), "dialogue": [], "body": ns["body"], "trim_start": 0.3,
                "trim_seconds": float(ns["seconds"]), "kwargs": {"duration_seconds": 4, "resolution": "480p"},
                "board_prompt": ns.get("board_prompt")}
        plan["shots"].append(shot)
        shots[shot["label"]] = shot
        new.append(shot["label"])
    return new


def _relaid(source: str) -> bool:
    """The score, its scratches and hits, the beds and cut sounds: laid again after a restructure."""
    return (source in _MUSIC or source in ("record_scratch", "title_impact", "whip_whoosh", "crash_swish")
            or source.startswith(("room_", "data_hum", "cut_")))


def _carry(placements: list[dict], old: dict[str, tuple[float, float]], shots: dict[str, dict]) -> list[dict]:
    """Designed effects ride with their shots; those on dropped shots, cards or relaid sources go."""
    keep = []
    for p in placements:
        if _relaid(p["source"]):
            continue
        t = float(p["at"])
        home = next((lab for lab, (a, d) in old.items() if a - 0.05 <= t < a + d), None)
        if home is None or shots[home].get("cut"):
            continue
        offset = min(t - old[home][0], max(0.0, float(shots[home]["trim_seconds"]) - 0.1))
        keep.append({**p, "at": round(float(shots[home]["clock_at"]) + offset, 3)})
    return keep


def _pass_cues(st: dict[str, Any], shots: dict[str, dict]) -> list[dict]:
    """The pass's music cues on the new clock; a "scratch" is a cut that says so."""
    cues = []
    for c in st.get("music") or []:
        do = c["do"]
        cues.append({"at": round(float(shots[c["shot"]]["clock_at"]) + float(c.get("at", 0)), 3),
                     "do": "cut" if do == "scratch" else do,
                     "why": ("scratch " if do == "scratch" else "") + (c.get("why") or "")})
    return cues


def _reorder(shots: dict[str, dict], st: dict[str, Any]) -> dict[str, dict]:
    """Dropped shots leave the cut, the ordered ones are in it; returns the pass's cards by the shot they follow."""
    for lab in st.get("dropped") or []:
        shots[lab]["cut"] = True
    for lab in st["order"]:
        shots[lab].pop("cut", None)
    return {c["after"]: {**c, "seconds": float(c["seconds"])} for c in st.get("cards") or []}


def _anchor_narration(plan: dict[str, Any], st: dict[str, Any]) -> None:
    """The narrator and the narration anchored to its shots."""
    plan["narrator"] = st.get("narrator") or "minh"
    plan["narration"] = [{"shot": n["shot"], "offset": float(n.get("at", 0)), "text": n["text"]}
                         for n in st.get("narration") or []]


def restructure(plan: dict[str, Any], st: dict[str, Any], next_index: int) -> list[str]:
    """A RESTRUCTURE pass into the plan: dropped shots leave the cut ("cut": true, kept on disk), new shots
    are added (to be boarded and rendered), the clock is laid again from 0 in the new order with the new
    cards behind their shots, acts replaced, designed effects ride with their shots, the score is laid again
    from the pass's cues, and the narration is anchored to its shots. Returns the labels of new shots."""
    shots = {s["label"]: s for s in plan["shots"]}
    new = _new_shots(plan, shots, st.get("new_shots") or [], next_index)
    old = {lab: (float(s["clock_at"]), float(s["trim_seconds"])) for lab, s in shots.items() if "clock_at" in s}
    cards = _reorder(shots, st)
    at = _lay(st["order"], shots, st["lengths"], cards, 0.0)
    plan["trailer"]["title_cards"] = list(cards.values())
    plan["trailer"]["acts"] = st.get("acts") or plan["trailer"].get("acts")
    sound = plan["sound"]
    sound["placements"] = _carry(sound["placements"], old, shots)
    sound["total_seconds"] = round(at, 3)
    music(plan, _pass_cues(st, shots), 0.0, at)
    _anchor_narration(plan, st)
    return new
