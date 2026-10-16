"""Animated title cards in the film's own identity — drawn frame by frame, cut to the beat.

A trailer's cards are its typography. These are built from what the film is
about, a face-recognition system: a heavy condensed sans for the words (the
Ritchie poster register), a monospace "system" layer for the machine — the
detection brackets that snap around a word, a MATCH label, a confidence
number — and the film's grade for colour: teal-black ground, sodium amber,
warm white, scan cyan.

Motion, on the beat of the act the card sits in:
- each word slams in on its beat (or half-beat): scale 1.35 → 1, a smear of
  ghost copies behind it, a short camera shake;
- one beat before the end the detection brackets snap around the key word and
  the label types itself out;
- in the last frames the key word doubles, offset, in cyan — the machine
  seeing the SAME — and the card cuts to black.
The title card (one word, e.g. SAME) puts a bracket around each letter on its
beat, merges them into one around the word on the hit, with a white flash
frame and the subline typing underneath.

Pillow and numpy draw; ffmpeg encodes. Nothing here calls a model.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 24
BG = (11, 20, 22)
WHITE = (242, 237, 228)
AMBER = (242, 165, 49)
CYAN = (127, 242, 230)
RED = (230, 57, 70)
_HEAVY = ["/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
          "/System/Library/Fonts/Supplemental/Impact.ttf"]
_MONO = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Andale Mono.ttf"]


def _font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in paths:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


@dataclass
class Card:
    text: str
    seconds: float
    bpm: float = 104.0
    key: str | None = None            # the word the system locks on; default: the last word
    label: str = "MATCH 98.7%"        # the system's reading of the key word
    subline: str = "IDENTITY: CHRISTOPHER PARK  ·  CONFIDENCE 51%"
    size: tuple[int, int] = (1280, 720)
    words: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.words = self.text.split()
        if self.key is None:
            self.key = self.words[-1].strip(".,!?")

    @property
    def beat(self) -> float:
        return 60.0 / self.bpm

    @property
    def is_title(self) -> bool:
        return len(self.words) == 1


# ── layout ──────────────────────────────────────────────────────────────────


def _lines(card: Card, font: ImageFont.FreeTypeFont) -> list[list[str]]:
    """Words broken into at most two lines that fit 86 % of the width."""
    width = card.size[0] * 0.86
    if font.getlength(" ".join(card.words)) <= width or len(card.words) < 2:
        return [card.words]
    best = min(range(1, len(card.words)),
               key=lambda i: abs(font.getlength(" ".join(card.words[:i])) - font.getlength(" ".join(card.words[i:]))))
    return [card.words[:best], card.words[best:]]


def _boxes(card: Card, font: ImageFont.FreeTypeFont) -> list[tuple[str, tuple[float, float, float, float]]]:
    """(word, box) for every word, centred, in reading order."""
    w, h = card.size
    lines = _lines(card, font)
    asc, desc = font.getmetrics()
    line_h = (asc + desc) * 0.92
    top = h / 2 - line_h * len(lines) / 2
    out, space = [], font.getlength(" ")
    for row, words in enumerate(lines):
        x = w / 2 - font.getlength(" ".join(words)) / 2
        y = top + row * line_h
        for word in words:
            wl = font.getlength(word)
            out.append((word, (x, y, x + wl, y + asc + desc * 0.2)))
            x += wl + space
    return out


# ── drawing ─────────────────────────────────────────────────────────────────


def _ease_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def _word(img: Image.Image, word: str, box: tuple, font, look: tuple) -> None:
    """One word, slammed in: big and smeared on its first frames, settled after. `look` is (colour, age)."""
    colour, age = look
    draw = ImageDraw.Draw(img)
    settle = _ease_out(age / 0.14)
    scale = 1.35 - 0.35 * settle
    if scale > 1.001:
        big = _font([font.path], int(font.size * scale))
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        bw, bh = big.getlength(word), (box[3] - box[1]) * scale
        for ghost in range(3, 0, -1):  # the smear trailing the slam
            shade = tuple(int(c * (0.25 / ghost)) for c in colour)
            draw.text((cx - bw / 2 - ghost * 18 * (1 - settle), cy - bh / 2), word, font=big, fill=shade)
        draw.text((cx - bw / 2, cy - bh / 2), word, font=big, fill=colour)
    else:
        draw.text((box[0], box[1]), word, font=font, fill=colour)


def _brackets(draw: ImageDraw.ImageDraw, box: tuple, colour, grow: float, stroke: tuple = (4, 18)) -> None:
    """Corner brackets of a face-detection frame, snapping in from 1.3× size; stroke is (line width, padding)."""
    width, pad = stroke
    pad = pad + 40 * (1 - _ease_out(grow))
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    arm = min(x1 - x0, y1 - y0) * 0.22
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        draw.line([(x, y), (x + dx * arm, y)], fill=colour, width=width)
        draw.line([(x, y), (x, y + dy * arm)], fill=colour, width=width)


def _scan(draw: ImageDraw.ImageDraw, box: tuple, progress: float) -> None:
    """A scan line sweeping down the box and landmark dots lighting up behind it, like a face mesh."""
    if not 0 <= progress <= 1:
        return
    x0, y0, x1, y1 = box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10
    y = y0 + (y1 - y0) * progress
    draw.line([(x0, y), (x1, y)], fill=CYAN, width=2)
    local = np.random.default_rng(int(x0))
    for _ in range(60):
        px, py = local.uniform(x0, x1), local.uniform(y0, y1)
        if py <= y:
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=CYAN)


def _split(img: Image.Image, amount: int) -> Image.Image:
    """Red and cyan channels pulled apart by a few pixels — the punch of a hit frame."""
    if amount <= 0:
        return img
    r, g, b = img.split()
    r = r.transform(img.size, Image.Transform.AFFINE, (1, 0, amount, 0, 1, 0))
    b = b.transform(img.size, Image.Transform.AFFINE, (1, 0, -amount, 0, 1, 0))
    return Image.merge("RGB", (r, g, b))


def _typed(draw: ImageDraw.ImageDraw, xy: tuple, text: str, style: tuple, progress: float) -> None:
    """Text typing itself out; `style` is (font, colour)."""
    font, colour = style
    shown = text[: int(len(text) * max(0.0, min(1.0, progress)))]
    draw.text(xy, shown + ("▌" if 0 < progress < 1 else ""), font=font, fill=colour)


def _grain(img: Image.Image, rng: np.random.Generator) -> Image.Image:
    """Film grain and a vignette, different every frame."""
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    noise = rng.normal(0, 9, (h, w, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    vignette = 1 - 0.45 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.2
    a = a * vignette[..., None] + noise
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _shake(t: float, hits: list[float]) -> tuple[int, int]:
    """A few pixels of camera shake for 0.15 s after every hit."""
    for hit in hits:
        age = t - hit
        if 0 <= age < 0.15:
            k = (1 - age / 0.15) * 7
            return int(k * np.sin(age * 140)), int(k * np.cos(age * 110))
    return 0, 0


# ── frames ──────────────────────────────────────────────────────────────────


def _camera(img: Image.Image, t: float, hits: list[float], zoom: float = 1.0) -> Image.Image:
    """Shake after each hit, an optional punch-in zoom, and the channel split on the hit frames."""
    w, h = img.size
    dx, dy = _shake(t, hits)
    a = 1 / zoom
    img = img.transform(img.size, Image.Transform.AFFINE, (a, 0, w / 2 * (1 - a) - dx, 0, a, h / 2 * (1 - a) - dy),
                        fillcolor=BG)
    return _split(img, 7 if any(0 <= t - hit < 2 / FPS for hit in hits) else 0)


def _lock(draw: ImageDraw.ImageDraw, card: Card, key_box: tuple, since: float, mono) -> None:
    """The system locking on the key word: scan, brackets, typed label, red dot."""
    _scan(draw, key_box, since / (card.beat * 0.8))
    _brackets(draw, key_box, CYAN, since / 0.12)
    _typed(draw, (key_box[0] - 18, key_box[1] - 64), card.label, (mono, CYAN), since / (card.beat * 0.7))
    draw.ellipse([key_box[2] + 4, key_box[1] - 58, key_box[2] + 16, key_box[1] - 46], fill=RED)


def _phrase_frame(card: Card, t: float, fonts: tuple, rng) -> Image.Image:
    heavy, mono = fonts
    boxes = _boxes(card, heavy)
    step = card.beat if len(boxes) <= 3 else card.beat / 2
    hits = [0.1 + i * step for i in range(len(boxes))]
    lock = card.seconds - card.beat
    if card.seconds - t <= 2 / FPS:
        return Image.new("RGB", card.size, (0, 0, 0))
    img = Image.new("RGB", card.size, BG)
    for (word, box), hit in zip(boxes, hits):
        if t >= hit:
            _word(img, word, box, heavy, (AMBER if word.strip(".,!?") == card.key else WHITE, t - hit))
    draw = ImageDraw.Draw(img)
    key_box = next((b for wd, b in boxes if wd.strip(".,!?") == card.key), boxes[-1][1])
    if t >= lock:
        _lock(draw, card, key_box, t - lock, mono)
    if card.seconds - t < 0.3:  # the machine sees the SAME: the key word doubled, offset
        draw.text((key_box[0] + 14, key_box[1] + 6), card.key, font=heavy, fill=CYAN)
    return _grain(_camera(img, t, hits + [lock]), rng)


def _letters(card: Card, heavy) -> tuple[ImageFont.FreeTypeFont, list[tuple[str, tuple]], tuple]:
    """The title word as large as 72 % of the width allows: its font, each letter's box, the whole word's box."""
    w, h = card.size
    size = int(h * 0.62)
    while _font([heavy.path], size).getlength(card.words[0]) > w * 0.72:
        size -= 8
    big = _font([heavy.path], size)
    asc, desc = big.getmetrics()
    x, y0 = w / 2 - big.getlength(card.words[0]) / 2, h / 2 - (asc + desc) / 2 - 20
    letters = []
    for ch in card.words[0]:
        lw = big.getlength(ch)
        letters.append((ch, (x, y0, x + lw, y0 + asc + desc * 0.2)))
        x += lw
    return big, letters, (letters[0][1][0], y0, letters[-1][1][2], y0 + asc + desc * 0.2)


def _title_frame(card: Card, t: float, fonts: tuple, rng) -> Image.Image:
    heavy, mono = fonts
    big, letters, whole = _letters(card, heavy)
    merge = card.beat * len(letters)
    if merge <= t < merge + 1.0 / FPS:
        return Image.new("RGB", card.size, WHITE)  # the hit
    img = Image.new("RGB", card.size, BG)
    draw = ImageDraw.Draw(img)
    if merge <= t < merge + 0.25:  # the machine's double, offset, flickering out
        draw.text((whole[0] + 16, whole[1] + 8), card.words[0], font=big, fill=CYAN if int(t * FPS) % 2 else BG)
    for i, (ch, box) in enumerate(letters):
        if t >= i * card.beat:
            draw.text((box[0], box[1]), ch, font=big, fill=WHITE)
            if t < merge:
                _brackets(draw, box, CYAN, (t - i * card.beat) / 0.12, stroke=(3, 18))
    if t >= merge:
        _brackets(draw, whole, CYAN, (t - merge) / 0.15, stroke=(5, 18))
        _typed(draw, (whole[0], whole[3] + 48), card.subline, (mono, CYAN), (t - merge) / (card.beat * 2))
    zoom = 1 + 0.06 * (1 - _ease_out((t - merge) / 0.3)) if t >= merge else 1.0
    return _grain(_camera(img, t, [merge] + [i * card.beat for i in range(len(letters))], zoom), rng)


def _fitted(card: Card) -> ImageFont.FreeTypeFont:
    """The heavy face as large as fits: 86 % of the width on at most two lines, a third of the height per line."""
    w, h = card.size
    size = int(h * 0.34)
    while size > 40:
        font = _font(_HEAVY, size)
        lines = _lines(card, font)
        if all(font.getlength(" ".join(l)) <= w * 0.86 for l in lines) and len(lines) * size * 0.95 <= h * 0.62:
            return font
        size -= 6
    return _font(_HEAVY, size)


def render(card: Card, out: Path, *, ffmpeg_bin: str = "ffmpeg") -> Path:
    """Encode the card to an H.264 clip of exactly card.seconds."""
    w, h = card.size
    fonts = (_fitted(card) if not card.is_title else _font(_HEAVY, int(h * 0.2)), _font(_MONO, int(h * 0.034)))
    frames = max(1, round(card.seconds * FPS))
    rng = np.random.default_rng(len(card.text))
    draw_frame = _title_frame if card.is_title else _phrase_frame
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([ffmpeg_bin, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                             "-crf", "18", str(out)], stdin=subprocess.PIPE)
    for n in range(frames):
        proc.stdin.write(draw_frame(card, n / FPS, fonts, rng).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed encoding title card {card.text!r}")
    return out
