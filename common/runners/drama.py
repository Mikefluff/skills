"""Drama mode — a series of dialogue films, its bible, its director, and the checks on what came back.

A drama is the long form of reel-builder: scenes of up to 15 s in which several
characters speak in any language Seedance voices, cut into an episode of
minutes, and episodes that share one cast. Nothing here calls a model; the
runners `reel_cast` and `reel_check` do, and this module is what they agree on.

The bible (one per series, `<series>/bible.json`, written by the drama chain):

  {"title": "...", "language": "th", "aspect_ratio": "16:9", "look": "one paragraph: medium, stock, grade",
   "director": "director.md",                       # relative to the bible; see directors/
   "master": "master.png",                          # optional: the picture the film is drawn from; portraits,
                                                    # plates and any frame naming "master" copy it
   "cast": [{"id": "malai", "name": "Malai", "identity": "8-20 words the critic checks", "like": "<id of a
             character whose face this one shares — a twin, a double; drawn from that portrait>",
             "voice": "young woman, soft, quick", "prompt": "portrait prompt"}],
   "locations": [{"id": "village_storm", "description": "...", "prompt": "plate prompt"}]}

A location image fixes its weather and time of day: a calm-night plate under a
storm scene makes Seedance choose between them, so a change of light is a new
location id ("village_storm", "village_dawn"), not a sentence in the scene.

A scene in the plan carries "cast" (ids, in the order they are named), an
optional "location", "dialogue" ([{"who": id, "line": "..."}], the words in the
episode's language) and "body" — the Seedance prompt without its asset lines.
`compose()` writes those lines from the bible so no prompt counts images by hand.
`preflight()` sets the flags the vendor's filters need before the first render;
`screenplay_text()` is what the story reader (story-check-prompt.md) is given.
"""

from __future__ import annotations

import difflib
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any

from . import previs

DIRECTORS = Path(__file__).resolve().parents[1] / "video-prompt-library" / "directors"
MAX_IMAGES = 9  # one scene: its speakers and its plate; more and Seedance blends faces
MAX_VOICES = 2  # voice samples are cut to 7 s so two fit the 15 s of audio a generation is reliably given


class DramaError(ValueError):
    pass


def load_bible(path: Path) -> dict[str, Any]:
    bible = json.loads(path.read_text(encoding="utf-8"))
    bible["_dir"] = str(path.parent)
    return bible


def asset_path(bible: dict[str, Any], kind: str, item_id: str, suffix: str = ".png") -> Path:
    """Where a series asset lives: <series>/cast/<id>.png, <series>/cast/<id>.mp3 (voice), <series>/locations/<id>.png."""
    return Path(bible["_dir"]) / kind / f"{item_id}{suffix}"


def master_path(bible: dict[str, Any]) -> Path:
    """The picture a film is drawn from (bible["master"], relative to the bible): every portrait and plate copies it."""
    return Path(bible["_dir"]) / bible["master"]


def _by_id(bible: dict[str, Any], kind: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in bible.get(kind) or []}


def references(scene: dict[str, Any], bible: dict[str, Any]) -> tuple[list[str], list[str]]:
    """The scene's images in order (its cast, then its location) and the sentence naming each."""
    cast, places = _by_id(bible, "cast"), _by_id(bible, "locations")
    refs, lines = [], []
    for who in scene.get("cast") or []:
        person = cast[who]
        refs.append(str(asset_path(bible, "cast", who)))
        lines.append(f"Image {len(refs)} is {person['name']}: {person['identity']}. Keep this face, hair, build "
                     "and clothing exactly.")
    if scene.get("location"):
        refs.append(str(asset_path(bible, "locations", scene["location"])))
        lines.append(f"Image {len(refs)} is the location: {places[scene['location']]['description']}. "
                     "Keep its architecture, weather and light.")
    return refs, lines


def voices(scene: dict[str, Any], bible: dict[str, Any]) -> tuple[list[str], list[str]]:
    """The scene's speakers' voice samples in order of first line, and the sentence binding each to its speaker.

    Without one, Seedance invents a voice per generation and a character sounds
    like someone else in every scene. A reference is read for timbre and accent;
    it is told not to copy the sample's room, which it otherwise does.
    """
    cast = _by_id(bible, "cast")
    speakers = list(dict.fromkeys(line["who"] for line in scene.get("dialogue") or [] if line.get("who") in cast))
    refs, lines = [], []
    for who in speakers:
        if cast[who].get("voice_text"):
            refs.append(str(asset_path(bible, "cast", who, ".mp3")))
            lines.append(f"Audio {len(refs)} is {cast[who]['name']}'s voice: use it only for timbre, accent and pace; "
                         "do not copy its room, microphone or noise.")
    return refs, lines


def compose(scene: dict[str, Any], bible: dict[str, Any]) -> str:
    """The full Seedance prompt: asset lines, the episode's look, then the chain's body."""
    lines = references(scene, bible)[1] + voices(scene, bible)[1]
    look = f"[Overall style]: {bible['look']}" if bible.get("look") else ""
    return "\n".join(part for part in [*lines, look, scene["body"].strip()] if part)


def validate(plan: dict[str, Any], bible: dict[str, Any]) -> list[str]:
    """Problems with an episode against its bible, as sentences; empty when it can be cast and rendered."""
    problems = [] if bible.get("language") else ["bible has no language"]
    for scene in plan.get("shots") or []:
        label = scene.get("label", scene.get("index"))
        problems += [f"{label}: {problem}" for problem in _scene_problems(scene, bible)]
    return problems + _coverage_problems(plan)


def _scene_problems(scene: dict[str, Any], bible: dict[str, Any]) -> list[str]:
    cast, places = _by_id(bible, "cast"), _by_id(bible, "locations")
    in_scene = scene.get("cast") or []
    problems = [f"unknown cast {who!r}" for who in in_scene if who not in cast]
    if scene.get("location") and scene["location"] not in places:
        problems.append(f"unknown location {scene['location']!r}")
    speakers = {line.get("who") for line in scene.get("dialogue") or []}
    problems += [f"{who!r} speaks but is not in the scene's cast" for who in sorted(speakers - set(in_scene) - {None, "vo"})]
    problems += _size_problems(scene)
    if len(speakers & set(cast)) > MAX_VOICES:
        problems.append(f"more than {MAX_VOICES} speakers")
    return problems


def _coverage_problems(plan: dict[str, Any]) -> list[str]:
    """"coverage": every shot of an exchange names its wide; the wide names itself and carries no line."""
    shots = {s.get("label"): s for s in plan.get("shots") or []}
    problems = []
    for label, shot in shots.items():
        wide = shots.get(shot.get("coverage")) if shot.get("coverage") else None
        if shot.get("coverage") and (wide is None or wide.get("coverage") != wide.get("label")):
            problems.append(f"{label}: coverage {shot['coverage']!r} is not a wide that names itself")
        elif wide is shot and shot.get("dialogue"):
            problems.append(f"{label}: a coverage wide carries no line; the close-ups do")
    return problems


def _size_problems(scene: dict[str, Any]) -> list[str]:
    problems = [] if scene.get("body") or scene.get("clip") else ["no body"]  # a clip is cut in as it is
    if len(scene.get("cast") or []) + bool(scene.get("location")) > MAX_IMAGES:
        problems.append(f"more than {MAX_IMAGES} reference images")
    return problems


# ── preflight: the vendor's filters, met when the plan is assembled ─────────

_CHILD = re.compile(r"\b(baby|babies|toddler|infant|child|kid|boy|girl)\b", re.I)
_SINGING = re.compile(r"(?<!no )(?<!without )\b(sing|sings|singing|sang|sung|song|songs|lullaby|chant\w*)\b", re.I)
LOCKED_OFF = 0.025  # a previs camera whose position and aim drift less than this (metres) stands still


def is_child(person: dict[str, Any]) -> bool:
    """A cast member the bible marks as a child: "age" under 13, or a child's word in "voice" or "identity"."""
    if isinstance(person.get("age"), (int, float)):
        return person["age"] < 13
    return bool(_CHILD.search(f"{person.get('voice', '')} {person.get('identity', '')}"))


def _mute_reason(plan: dict[str, Any], shot: dict[str, Any], bible: dict[str, Any]) -> str | None:
    """Why the generation's own audio must be off: a child's voice or singing trips the copyright filter."""
    cast = _by_id(bible, "cast")
    said = {line.get("who") for line in shot.get("dialogue") or []}
    said |= {v.get("who") for v in plan.get("vocals") or [] if v.get("shot") == shot.get("label")}
    kids = sorted(cast[who]["name"] for who in said if who in cast and is_child(cast[who]))
    if kids:
        return f"a child speaks ({', '.join(kids)})"
    return "someone sings" if _SINGING.search(shot.get("body", "").split("[Strictly exclude]")[0]) else None


def locked_off(previs_shot: dict[str, Any]) -> bool:
    """A previs camera that neither moves nor turns."""
    keys = [k for k in previs.camera_keys(previs_shot) if k.get("pos") and k.get("look")]
    return bool(keys) and all(math.dist(k[axis], keys[0][axis]) <= LOCKED_OFF for k in keys for axis in ("pos", "look"))


def _still_previs(shot: dict[str, Any], cams: dict[str, Any]) -> bool:
    """Whether the shot's previs should go unsent: a locked-off camera, the flag not set, not a continuation."""
    if "no_previs" in shot or shot.get("extend") or shot.get("bridge") or shot.get("label") not in cams:
        return False
    return locked_off(cams[shot["label"]])


def preflight(plan: dict[str, Any], bible: dict[str, Any]) -> list[str]:
    """Flags a vendor's filters need, set before the first render instead of after a refusal; a note per flag set.

    `kwargs.generate_audio` false where a child speaks or someone sings (the cast's
    take replaces the generation's audio anyway). A locked-off previs camera is only
    noted: a still clip is sometimes read as footage to edit, but on the first film one
    such shot in five was refused, so `no_previs` stays a call made by eye. A key the
    plan already sets, true or false, is left as it is.
    """
    cams, notes = (plan.get("previs") or {}).get("shots") or {}, []
    for shot in plan.get("shots") or []:
        label, explicit = shot.get("label"), shot.get("clip") or "generate_audio" in (shot.get("kwargs") or {})
        why = None if explicit else _mute_reason(plan, shot, bible)
        if why:
            shot.setdefault("kwargs", {})["generate_audio"] = False
            notes.append(f"{label}: generate_audio off, {why}")
        if _still_previs(shot, cams):
            notes.append(f"{label}: the previs camera is locked off; if Seedance reads it as an edit, set no_previs")
    return notes


# ── the screenplay a reader checks before anything is drawn ─────────────────

_BOILERPLATE = re.compile(r"\s*(\[Strictly exclude\].*|No music\.|No dialogue, no music, no subtitles\.|"
                          r"Dialogue language: [^.]*\.)", re.S)


def _shot_text(shot: dict[str, Any], names: dict[str, str]) -> str:
    body = _BOILERPLATE.sub("", shot.get("body") or "").strip()
    lines = [f"  {names.get(d.get('who'), d.get('who'))}: {d['line']}" for d in shot.get("dialogue") or []
             if d.get("line") and d["line"] not in body]
    head = f"{shot.get('label')} (scene {shot['scene']})" if shot.get("scene") else str(shot.get("label"))
    return "\n".join([head, *([body] if body else []), *lines])


def _title_cards(plan: dict[str, Any]) -> dict[str, list[str]]:
    """The title cards with words, by the label they follow ("t00": before the first shot)."""
    cards: dict[str, list[str]] = {}
    for card in (plan.get("trailer") or {}).get("title_cards") or []:
        if card.get("text"):
            cards.setdefault(card.get("after", ""), []).append(f"[title card: {card['text']}]")
    return cards


def screenplay_text(plan: dict[str, Any], bible: dict[str, Any] | None = None) -> str:
    """The plan as a reader gets it: each shot's action and lines in film order, title cards where they fall."""
    names = {c["id"]: c.get("name", c["id"]) for c in (bible or {}).get("cast") or []}
    cards = _title_cards(plan)
    parts = [*cards.get("t00", [])]
    for shot in plan.get("shots") or []:
        if shot.get("body") or shot.get("dialogue"):
            parts.append(_shot_text(shot, names))
        parts += cards.get(shot.get("label"), [])
    return "\n\n".join(parts)


# ── directors ───────────────────────────────────────────────────────────────


def director(path_or_id: str, base: Path | None = None) -> str:
    """A director's rules with everything it `extends:` before it, base first.

    A director file is markdown with a first line `extends: <id>` (optional) and
    numbered rules after. A later rule with the same number replaces the earlier
    one, so a director that inherits sixty rules and changes three says only three.
    """
    path = Path(path_or_id)
    if not path.is_file():
        path = (base or DIRECTORS) / f"{path_or_id}.md"
    if not path.is_file():
        raise DramaError(f"director not found: {path_or_id}")
    text = path.read_text(encoding="utf-8")
    parent = re.match(r"extends:\s*(\S+)\s*\n", text)
    if not parent:
        return text
    head, rules = _rules(director(parent.group(1), base))
    own_head, own = _rules(text[parent.end():])
    rules.update(own)  # same number replaces in place; a new number goes at the end
    return "\n".join([head, own_head, *rules.values()]).strip() + "\n"


_RULE = re.compile(r"^(\d+)\. ", re.M)


def _rules(text: str) -> tuple[str, dict[str, str]]:
    """The text before the first numbered rule, and each rule (to the next one) by its number."""
    marks = list(_RULE.finditer(text))
    if not marks:
        return text.strip(), {}
    ends = [m.start() for m in marks[1:]] + [len(text)]
    return text[:marks[0].start()].strip(), {m.group(1): text[m.start():end].strip() for m, end in zip(marks, ends)}


# ── checks on what came back ────────────────────────────────────────────────


def _letters(text: str) -> str:
    """Letters and digits only, case-folded: Thai has no spaces, and STT adds some."""
    return "".join(ch for ch in unicodedata.normalize("NFC", text).casefold() if ch.isalnum()
                   or unicodedata.category(ch).startswith("M"))


def speech_match(expected: str, heard: str) -> float:
    """How much of the script was said, 0-1, by characters — so it works for scripts without word gaps."""
    want, got = _letters(expected), _letters(heard)
    if not want:
        return 1.0
    return difflib.SequenceMatcher(None, want, got, autojunk=False).ratio()


def scene_script(scene: dict[str, Any]) -> str:
    return " ".join(line["line"] for line in scene.get("dialogue") or [])
