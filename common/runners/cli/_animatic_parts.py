"""The cut's parts — each clip, still and card encoded once, kept by everything that makes it, and joined.

A part's file is <out>/parts/<key>.mp4, the key a hash of its inputs (the clip's path, mtime and size, its
window, speed, the transitions on its head and tail, the grade, size and rate; a card's words or image; a
still's frame and camera) and of the code that draws it. A rerun encodes only the parts that changed; the
join is a stream copy of the files, so a part reused is the same bytes it was. A part no cut has used for two
days is deleted.

The parts' input keys in clock order are the picture's signature, written next to the cut
(<cut>.picture.json) when its picture is built: an --audio-only build lays new sound on that picture only
while the plan still makes the same parts, and names the shots that changed when it does not.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from ..errors import RunnerError
from . import _animatic_picture as ap
from ._animatic_clips import clip_start

_KEEP_SECONDS = 2 * 86400


@dataclass
class Part:
    """One part of the picture: whose it is, the inputs that make it, how it is drawn, and where it is kept."""
    label: str
    inputs: list
    draw: Callable[[Path], None]
    path: Path = field(init=False)
    key: str = field(init=False)
    home: Path = Path(".")

    def __post_init__(self) -> None:
        self.key = _hash(self.inputs)
        self.path = self.home / f"{_hash([self.key, _code()])}.mp4"


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()[:16]


@lru_cache(maxsize=1)
def _code() -> str:
    """The drawing code itself: a change to a transition, a grade or a card redraws what it touches."""
    from .. import cut_transitions, film_grade, title_cards

    sources = [inspect.getsource(m) for m in (cut_transitions, film_grade, title_cards)]
    sources += [inspect.getsource(f) for f in (ap._still, ap._card, ap._bars, ap._head_graph, ap._clip_part,
                                                ap._freeze)]
    return _hash(sources)


def _stat(path: Path) -> list:
    st = path.stat()
    return [str(path), st.st_mtime_ns, st.st_size]


# ── which parts the cut has ───────────────────────────────────────────────────


def _card_part(cut: ap._Cut, item: dict[str, Any], home: Path) -> Part:
    card = item["card"]
    image = [_stat(Path(card["image"]))] if card.get("image") else []
    bpm = ap.act_bpm_of(cut.plan, card.get("after", ""), 104.0)
    inputs = ["card", {k: v for k, v in card.items() if k != "clock_at"}, image, item["seconds"], cut.size, bpm]
    return Part(f"card {card.get('text', '')[:24]!r}", inputs,
                lambda out: ap._card(item, out, cut.size, cut.plan), home)


def _still_part(cut: ap._Cut, item: dict[str, Any], home: Path) -> Part:
    shot = item["shot"]
    image = cut.board_dir / f"{cut.frame_of.get(int(shot['index']), '')}.jpg"
    body = shot.get("body", "")

    def draw(out: Path) -> None:
        if not image.is_file():
            raise RunnerError(f"no storyboard frame for {shot['label']}: run reel_board first")
        ap._still(image, item["seconds"], out, cut.size, body)

    # a frame not drawn yet is still a part: an --audio-only build names it as changed instead of failing
    inputs = ["still", _stat(image) if image.is_file() else [str(image)], item["seconds"], cut.size, ap._FPS, body]
    return Part(shot["label"], inputs, draw, home)


def _clip_parts(cut: ap._Cut, item: dict[str, Any], nxt: dict[str, Any] | None, home: Path) -> list[Part]:
    """A rendered shot's window, and its freeze when it has one; its (shot, clip, start) goes to takes.used."""
    from .. import shot_matrix

    takes, shot = cut.takes, item["shot"]
    clip = takes.clips[shot["label"]]
    start = takes.marks.get(shot["label"], (None,))[0]
    if start is None:
        start = clip_start(shot, clip, takes.onsets.get(shot["label"]), cut.mouths)
    hold = shot.get("freeze")
    live = min(float(hold["at"]), item["seconds"] - 0.2) if hold else item["seconds"]
    win = ap.Window(clip, start, live, cut.cuts.get(shot["label"], "cut"), "cut" if hold else ap._leave(cut, nxt),
                    shot_matrix.speed(shot, cut.plan))
    grade = cut.plan.get("grade")
    inputs = ["clip", _stat(clip), win.start, win.seconds, win.into, win.leave, win.speed, cut.size, ap._FPS, grade]
    parts = [Part(shot["label"], inputs, lambda out: ap._clip_part(win, out, cut.size, grade), home)]
    if hold:
        own = parts[0]
        bpm = ap.act_bpm_of(cut.plan, shot["label"], 112.0)
        parts.append(Part(f"{shot['label']} freeze", ["freeze", own.key, item["seconds"], live, bpm, hold],
                          lambda out: ap._freeze(cut.plan, item, own.path, live, out), home))
    if takes.used is not None:
        takes.used.append((shot, clip, start))
    return parts


def cut_parts(plan: dict[str, Any], board_dir: Path, takes: ap.Takes | None = None) -> list[Part]:
    """The cut's parts in clock order, nothing drawn; each clip's (shot, clip, start) is appended to
    `takes.used`, as the picture would."""
    from .. import shot_matrix

    cut = ap._Cut(plan, board_dir, takes or ap.Takes(), ap._size(plan),
                  shot_matrix.transitions(plan),  # label → the transition into that shot
                  {int(f["shot"]): f["id"] for f in (plan.get("board") or {}).get("frames") or []},
                  Path(plan["output_dir"]) / "shots" / "mouths.json")
    home = Path(plan["output_dir"]) / "parts"
    items = ap.frame_aligned(ap.timeline(plan))
    parts: list[Part] = []
    for n, item in enumerate(items):
        nxt = items[n + 1] if n + 1 < len(items) else None
        if item["kind"] == "card":
            parts.append(_card_part(cut, item, home))
        elif item["shot"]["label"] in cut.takes.clips:
            parts += _clip_parts(cut, item, nxt, home)
        else:
            parts.append(_still_part(cut, item, home))
    return parts


# ── drawing and joining ───────────────────────────────────────────────────────


def _ensure(part: Part) -> bool:
    """The part's file, drawn unless it is already kept; True when it was drawn."""
    if part.path.is_file():
        os.utime(part.path)
        return False
    part.path.parent.mkdir(parents=True, exist_ok=True)
    work = part.path.with_name(f"{part.path.stem}.tmp.mp4")
    part.draw(work)
    work.replace(part.path)  # whole or not at all: a run stopped mid-encode leaves no half part
    return True


def _join(parts: list[Path], out: Path) -> None:
    import subprocess

    listing = out.parent / "animatic-parts.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(out)], check=True, capture_output=True)
    listing.unlink()


def _prune(home: Path, keep: set[Path]) -> None:
    """Parts no cut has used for two days, and any half-written one, deleted."""
    now = time.time()
    for f in home.glob("*.mp4"):
        if f not in keep and (f.name.endswith(".tmp.mp4") or now - f.stat().st_mtime > _KEEP_SECONDS):
            f.unlink()


def render(parts: list[Part], out: Path) -> Path:
    """The parts drawn (the kept ones reused) and joined into `out` by stream copy."""
    import sys

    drawn = sum(_ensure(p) for p in parts)
    print(f"Picture: {drawn} of {len(parts)} part(s) drawn, the rest reused", file=sys.stderr)
    _join([p.path for p in parts], out)
    if parts:
        _prune(parts[0].path.parent, {p.path for p in parts})
    return out


def picture(plan: dict[str, Any], board_dir: Path, out: Path, takes: ap.Takes | None = None) -> Path:
    """The cut as stills (or rendered clips) and cards, joined in clock order; each clip's (shot, clip, start)
    is appended to `takes.used`."""
    return render(cut_parts(plan, board_dir, takes), out)


# ── the picture's signature ───────────────────────────────────────────────────


def signature_file(cut: Path) -> Path:
    return cut.with_suffix(".picture.json")


def record(cut: Path, parts: list[Part]) -> None:
    """The signature of the picture now in `cut`."""
    signature_file(cut).write_text(json.dumps({"parts": [[p.label, p.key] for p in parts]}, indent=1) + "\n",
                                   encoding="utf-8")


def changes(old: list[list[str]], parts: list[Part]) -> str:
    """What differs between a recorded signature and the parts the plan makes now, in words."""
    before, now = {label: key for label, key in old}, {p.label: p.key for p in parts}
    sorts = {"changed": [k for k in now if before.get(k, now[k]) != now[k]],
             "new": [k for k in now if k not in before], "gone": [k for k in before if k not in now]}
    said = [f"{', '.join(names)} {what}" for what, names in sorts.items() if names]
    return "; ".join(said) or "the parts are in a different order"


def fresh(cut: Path, parts: list[Part]) -> None:
    """Raise unless `cut` holds the picture these parts make."""
    sig = signature_file(cut)
    if not (cut.is_file() and sig.is_file()):
        raise RunnerError(f"--audio-only needs a picture built with its signature ({sig.name} next to "
                          f"{cut.name}); build the picture once without --audio-only")
    old = json.loads(sig.read_text(encoding="utf-8"))["parts"]
    if [key for _, key in old] != [p.key for p in parts]:
        raise RunnerError(f"the picture in {cut.name} is stale — {changes(old, parts)}; a picture build is "
                          "needed (run without --audio-only)")
