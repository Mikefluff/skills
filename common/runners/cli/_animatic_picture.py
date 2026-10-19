"""The animatic's picture — stills moved like their camera, title cards, rendered clips, joined on the clock.

Split out of reel_animatic; the names are re-exported there.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..errors import RunnerError
from ._animatic_clips import clip_start

_FPS = 24
_FONT = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"


def timeline(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Shots and title cards in clock order: {"kind", "at", "seconds", ...}."""
    items = [{"kind": "shot", "at": float(s["clock_at"]), "seconds": float(s["trim_seconds"]), "shot": s}
             for s in plan["shots"] if not s.get("cut")]  # "cut": dropped by a restructure, kept on disk
    items += [{"kind": "card", "at": float(c["clock_at"]), "seconds": float(c["seconds"]), "text": c["text"], "card": c}
              for c in (plan.get("trailer") or {}).get("title_cards") or []]
    return sorted(items, key=lambda item: item["at"])


# Camera move named in the shot body → how the still moves: (zoom from, zoom to, pan x from, pan x to, shake).
_MOVES = [
    (r"crash[- ]zoom", (1.0, 1.0, 0.0, 0.0, 0)),  # handled as a late snap below
    (r"whip", (1.08, 1.08, -0.06, 0.0, 0)),
    (r"pull[- ]?back|pulls back|dolly out|zoom out", (1.18, 1.0, 0.0, 0.0, 0)),
    (r"push[- ]?in|pushes in|dolly in|creep|zoom in", (1.0, 1.15, 0.0, 0.0, 0)),
    (r"track(s|ing)? left|dolly left|truck left|pan left", (1.1, 1.1, 0.04, -0.04, 0)),
    (r"track|dolly|truck|pan|arc|orbit", (1.1, 1.1, -0.04, 0.04, 0)),
    (r"hand-?held|shak", (1.08, 1.1, 0.0, 0.0, 6)),
]


def camera_move(body: str) -> tuple[float, float, float, float, int, bool]:
    """(zoom0, zoom1, x0, x1, shake px, crash) for the first move the shot body names; a slow push otherwise."""
    text = body.lower()
    crash = bool(re.search(r"crash[- ]zoom", text))
    for pattern, move in _MOVES[1:]:
        if re.search(pattern, text):
            return (*move, crash)
    return (1.0, 1.05, 0.0, 0.0, 0, crash)


def _still(image: Path, seconds: float, out: Path, size: str, body: str = "") -> None:
    """The frame, moved the way the shot's camera moves — the cut reads in motion, not as a slideshow."""
    w, h = (int(v) for v in size.split("x"))
    z0, z1, x0, x1, shake, crash = camera_move(body)
    n = max(1, round(seconds * _FPS))
    prog = f"(on/{n})"
    zoom = f"({z0}+({z1}-{z0})*{prog})" + (f"*(1+0.35*gte(on,{int(n * 0.7)}))" if crash else "")
    x = f"(iw-iw/zoom)/2+iw*({x0}+({x1}-{x0})*{prog})" + (f"+{shake}*sin(on*1.7)" if shake else "")
    y = "(ih-ih/zoom)/2" + (f"+{shake}*cos(on*2.3)" if shake else "")
    vf = (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
          f"zoompan=z='{zoom}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={_FPS},setsar=1")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(image), "-vf", vf, "-frames:v", str(n),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out)], check=True, capture_output=True)


def _card(item: dict[str, Any], out: Path, size: str, plan: dict[str, Any]) -> None:
    """An animated title card in the film's identity (title_cards), on the beat of the act it sits in."""
    from .. import title_cards
    from . import _trailer_retime as rt

    card = item["card"]
    if card.get("image"):
        # a card drawn in the film's own look (a lettered frame, the picture the film returns to), held on a slow push
        _still(Path(card["image"]), item["seconds"], out, size, card.get("move", "slow push-in"))
        return
    act = rt._act_of(plan).get(card.get("after", ""), "")
    w, h = (int(v) for v in size.split("x"))
    title_cards.render(title_cards.Card(card["text"], item["seconds"], bpm=rt.act_bpm(plan).get(act, 104.0),
                                        key=card.get("key"), label=card.get("label", "MATCH 98.7%"),
                                        size=(w, h)), out)


def _bars(clip: Path, start: float, seconds: float) -> str:
    """A crop that drops white side bars a generation sometimes pads its frame with ("" when there are none)."""
    from io import BytesIO

    from PIL import Image

    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start + seconds / 2:.3f}", "-i", str(clip),
                          "-frames:v", "1", "-vf", "scale=214:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    if not png:
        return ""
    im = Image.open(BytesIO(png)).convert("L")
    w, h = im.size
    px = im.load()
    white = lambda x: sum(px[x, y] for y in range(0, h, 4)) / len(range(0, h, 4)) > 235  # noqa: E731
    left = next((x for x in range(w // 3) if not white(x)), 0)
    right = next((x for x in range(w // 3) if not white(w - 1 - x)), 0)
    if left < 2 and right < 2:
        return ""
    a, b = (left + 1) / w, (right + 1) / w
    return f"crop=iw*{1 - a - b:.4f}:ih:iw*{a:.4f}:0,"


@dataclass
class Window:
    """The used window of a rendered shot and the edit's transition halves on its head and tail."""
    clip: Path
    start: float
    seconds: float
    into: str = "cut"
    leave: str = "cut"
    speed: float = 1.0


def _head_graph(win: Window, base: str) -> str:
    """The clip into [pre]: as is, or with a ramp tail slowed by drawn in-between frames."""
    from .. import cut_transitions as ct

    if win.leave != "ramp":
        return f"[0:v]{base}[pre]"
    normal, slow, factor = ct.ramp_window(win.seconds)
    return (f"[0:v]trim=0:{normal:.3f},setpts=PTS-STARTPTS[a];"
            f"[0:v]trim={normal:.3f}:{normal + slow:.3f},setpts=(PTS-STARTPTS)*{factor:.3f},"
            # in-between frames are drawn, not repeated: a repeated frame reads as a stutter, not slow motion
            f"minterpolate=fps={_FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1[b];"
            f"[a][b]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS,{base}[pre]")


def _clip_part(win: Window, out: Path, size: str, grade: str | None) -> None:
    """The used window of a rendered shot, at the cut's size and rate, picture only, graded, with the edit's
    transition halves on its head (`into`) and tail (`leave`) — see cut_transitions."""
    from .. import cut_transitions as ct
    from .. import film_grade

    w, h = (int(v) for v in size.split("x"))
    seconds = win.seconds
    fast = f"setpts=PTS/{win.speed:.3f}," if win.speed != 1.0 else ""  # undercranked action (shot_matrix.speed)
    # 480p generations blown up 1.5x: lanczos and a light unsharp, or the cut reads as soap
    base = (f"{fast}{_bars(win.clip, win.start, seconds)}scale={w}:{h}:force_original_aspect_ratio=increase:"
            f"flags=lanczos,crop={w}:{h},unsharp=5:5:0.7:3:3:0,fps={_FPS},setsar=1,"
            # a window longer than the clip (a shot lengthened to its line) holds the last frame, never runs short
            f"tpad=stop_mode=clone:stop_duration={seconds + 1:.3f}")
    moves = [f for f in (ct.into(win.into, w, h), ct.out(win.leave, seconds, w, h)) if f]
    tail = ",".join([*moves, *([film_grade.GRADES[grade]] if grade else [])])
    graph = _head_graph(win, base)
    label = "pre"
    for n, (x, on) in enumerate(ct.wipes(win.into, win.leave, seconds)):
        graph += (f";color=c=black:s={w}x{h}:r={_FPS}[k{n}];[{label}][k{n}]overlay=x='{x}':y=0:"
                  f"enable='{on}':eof_action=pass:shortest=1[w{n}]")
        label = f"w{n}"
    graph += f";[{label}]" + (tail or "null") + "[v]"
    filt = ["-filter_complex", graph, "-map", "[v]"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{win.start:.3f}", "-i", str(win.clip), "-an",
                    *filt, "-frames:v", str(max(1, round(seconds * _FPS))), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "18", str(out)], check=True, capture_output=True)


def frame_aligned(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each part's length in whole frames counted from the film's clock, not rounded part by part: 83 parts
    rounded on their own drift the picture off the sound by most of a second, and every later line misses
    its mouth."""
    for item in items:
        a, b = round(item["at"] * _FPS), round((item["at"] + item["seconds"]) * _FPS)
        item["seconds"] = max(1, b - a) / _FPS
    return items


@dataclass
class Takes:
    """The rendered side of a cut: label → clip, where each line starts, the mouth marks, and the (shot, clip,
    start) of every clip the picture used, appended as it goes."""
    clips: dict[str, Path] = field(default_factory=dict)
    onsets: dict[str, float] = field(default_factory=dict)
    marks: dict[str, tuple[float, float, float]] = field(default_factory=dict)
    used: list | None = None


@dataclass
class _Cut:
    plan: dict[str, Any]
    board_dir: Path
    takes: Takes
    size: str
    cuts: dict[str, str]
    frame_of: dict[int, str]
    mouths: Path


def _size(plan: dict[str, Any]) -> str:
    wide = (plan.get("board") or {}).get("aspect_ratio", "16:9") == "16:9"
    return ("1920x1080" if wide else "1080x1920") if plan.get("hd") else ("1280x720" if wide else "720x1280")


def _leave(cut: _Cut, nxt: dict[str, Any] | None) -> str:
    """Into a card: the card's own "into" (a black beat irised into), else the trailer's flash; the film's last
    shot leaves on the plan's "ending" (an iris closing on a face)."""
    if nxt is None:
        return cut.plan.get("ending", "cut")
    if nxt["kind"] == "card":
        return nxt["card"].get("into", "flash")
    return cut.cuts.get(nxt["shot"]["label"], "cut")


def _freeze(cut: _Cut, item: dict[str, Any], part: Path, live: float) -> Path:
    """The Ritchie freeze: the clip stops on its frame at `at` and the system reads the faces in it."""
    from .. import title_cards
    from . import _trailer_retime as rt

    shot, hold, plan = item["shot"], item["shot"]["freeze"], cut.plan
    still = part.with_suffix(".png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.05", "-i", str(part),
                    "-frames:v", "1", "-update", "1", str(still)], check=True, capture_output=True)
    frozen = part.with_name(part.stem + "-freeze.mp4")
    title_cards.freeze(still, item["seconds"] - live, frozen,
                       bpm=rt.act_bpm(plan).get(rt._act_of(plan).get(shot["label"], ""), 112.0),
                       boxes=hold.get("boxes"), caption=hold.get("caption"))
    still.unlink()
    return frozen


def _clip_item(cut: _Cut, item: dict[str, Any], nxt: dict[str, Any] | None, part: Path) -> list[Path]:
    from .. import shot_matrix

    takes = cut.takes
    shot, clip = item["shot"], takes.clips[item["shot"]["label"]]
    start = takes.marks.get(shot["label"], (None,))[0]
    if start is None:
        start = clip_start(shot, clip, takes.onsets.get(shot["label"]), cut.mouths)
    hold = shot.get("freeze")
    live = min(float(hold["at"]), item["seconds"] - 0.2) if hold else item["seconds"]
    _clip_part(Window(clip, start, live, cut.cuts.get(shot["label"], "cut"), "cut" if hold else _leave(cut, nxt),
                      shot_matrix.speed(shot, cut.plan)), part, cut.size, cut.plan.get("grade"))
    made = [part]
    if hold:
        made.append(_freeze(cut, item, part, live))
    if takes.used is not None:
        takes.used.append((shot, clip, start))
    return made


def _still_item(cut: _Cut, item: dict[str, Any], part: Path) -> None:
    image = cut.board_dir / f"{cut.frame_of.get(int(item['shot']['index']), '')}.jpg"
    if not image.is_file():
        raise RunnerError(f"no storyboard frame for {item['shot']['label']}: run reel_board first")
    _still(image, item["seconds"], part, cut.size, item["shot"].get("body", ""))


def _join(parts: list[Path], out: Path) -> None:
    listing = out.parent / "animatic-parts.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(out)], check=True, capture_output=True)
    for p in [*parts, listing]:
        p.unlink()


def picture(plan: dict[str, Any], board_dir: Path, out: Path, takes: Takes | None = None) -> Path:
    """The cut as stills (or rendered clips) and cards, joined in clock order; each clip's (shot, clip, start)
    is appended to `takes.used`."""
    from .. import shot_matrix

    cut = _Cut(plan, board_dir, takes or Takes(), _size(plan),
               shot_matrix.transitions(plan),  # label → the transition into that shot
               {int(f["shot"]): f["id"] for f in (plan.get("board") or {}).get("frames") or []},
               Path(plan["output_dir"]) / "shots" / "mouths.json")
    items = frame_aligned(timeline(plan))
    parts: list[Path] = []
    for n, item in enumerate(items):
        part = out.parent / f"animatic-part{n:03d}.mp4"
        nxt = items[n + 1] if n + 1 < len(items) else None
        if item["kind"] == "card":
            _card(item, part, cut.size, plan)
            parts.append(part)
        elif item["shot"]["label"] in cut.takes.clips:
            parts += _clip_item(cut, item, nxt, part)
        else:
            _still_item(cut, item, part)
            parts.append(part)
    _join(parts, out)
    return out
