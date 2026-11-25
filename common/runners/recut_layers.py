"""The overlay track: graphics and karaoke captions drawn frame by frame.

Chrome renders each graphic once to a transparent PNG; this module animates the
stills (pop, slide, fade) and draws the captions, then hands ffmpeg raw RGBA
frames on a pipe. A frame is only redrawn when something on it changed, which
is most of why a 40-second reel composites in seconds.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from PIL import Image, ImageDraw, ImageFont

from .recut_plan import CAPTION_Y, CAPTION_Y_STACK, FPS, H, W, Brand
from .recut_scene import Cue

_CHROME_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)
_CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")


def find_chrome() -> str | None:
    """$CHROME, then the usual install paths, then PATH."""
    override = os.environ.get("CHROME")
    if override:
        return override
    for path in _CHROME_PATHS:
        if Path(path).is_file():
            return path
    for name in _CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def screenshot(chrome: str, page: Path, png: Path, profile: Path) -> None:
    """One page to one transparent 1080x1920 PNG. Chrome sometimes exits before
    writing the file on a cold start, hence the retries."""
    for _ in range(3):
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
             "--default-background-color=00000000", "--virtual-time-budget=2500", "--force-device-scale-factor=1",
             f"--user-data-dir={profile}", f"--screenshot={png}", page.as_uri()],
            capture_output=True, check=False,
        )
        if png.exists():
            return
    raise RuntimeError(f"Chrome did not render {page}")


def render_pages(pages: list[str], cache: Path, chrome: str) -> list[tuple[Image.Image, int, int]]:
    """HTML pages to cropped RGBA stills with their position: [(image, x, y)].

    Cached by the page's hash, so an unchanged graphic is never rendered twice,
    and each worker keeps one browser profile — a fresh profile per launch made
    the first build ten times slower.
    """
    cache.mkdir(parents=True, exist_ok=True)

    def one(page: str) -> tuple[Image.Image, int, int]:
        key = hashlib.sha1(page.encode("utf-8")).hexdigest()[:16]
        png, source = cache / f"{key}.png", cache / f"{key}.html"
        if not png.exists():
            source.write_text(page, encoding="utf-8")
            profile = cache / f"chrome-{os.getpid()}-{threading.get_ident() % 100000}"
            screenshot(chrome, source, png, profile)
        image = Image.open(png).convert("RGBA")
        box = image.getbbox() or (0, 0, 2, 2)
        return image.crop(box), box[0], box[1]

    with ThreadPoolExecutor(6) as pool:
        return list(pool.map(one, pages))


def _ease_out(p: float) -> float:
    return 1 - (1 - p) ** 3


def _back_out(p: float, overshoot: float = 1.6) -> float:
    p -= 1
    return 1 + p * p * ((overshoot + 1) * p + overshoot)


_SLIDES = {"up": (0, 70), "down": (0, -60), "left": (-90, 0)}


@dataclass
class Layer:
    image: Image.Image
    x: int
    y: int
    cue: Cue

    def state(self, t: float) -> tuple | None:
        """(alpha, scale, dx, dy) at `t`, or None when off screen."""
        cue = self.cue
        if not cue.t0 <= t < cue.t1:
            return None
        arriving = min(1.0, (t - cue.t0) / cue.din) if cue.din else 1.0
        leaving = min(1.0, (cue.t1 - t) / cue.dout) if cue.dout else 1.0
        scale = 0.72 + 0.28 * _back_out(arriving) if cue.anim == "pop" else 1.0
        sx, sy = _SLIDES.get(cue.anim, (0, 0))
        rest = 1 - _ease_out(arriving)
        dy = round(rest * sy) + (round((1 - leaving) * 18) if leaving < 1 else 0)
        return (round(min(1.0, arriving * 2.2) * leaving, 2), round(scale, 3), round(rest * sx), dy)

    def draw(self, canvas: Image.Image, state: tuple) -> None:
        alpha, scale, dx, dy = state
        image, x, y = self.image, self.x + dx, self.y + dy
        if scale != 1.0:
            w, h = max(2, round(image.width * scale)), max(2, round(image.height * scale))
            x += (image.width - w) // 2
            y += (image.height - h) // 2
            image = image.resize((w, h), Image.BILINEAR)
        if alpha < 1.0:
            image = image.copy()
            image.putalpha(image.getchannel("A").point(lambda v: int(v * alpha)))
        paste(canvas, image, x, y)


def paste(canvas: Image.Image, image: Image.Image, x: int, y: int) -> None:
    """alpha_composite that tolerates an image hanging off the canvas."""
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(image.width, W - x), min(image.height, H - y)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (0, 0, image.width, image.height):
        image = image.crop((x0, y0, x1, y1))
    canvas.alpha_composite(image, (x + x0, y + y0))


def weighted_font(path: Path, size: int, weight: int) -> ImageFont.FreeTypeFont:
    """A variable font at a weight; a static font is returned as it is."""
    font = ImageFont.truetype(str(path), size)
    try:
        axes = font.get_variation_axes()
    except OSError:
        return font
    font.set_variation_by_axes([weight if _is_weight(axis) else axis["default"] for axis in axes])
    return font


def _is_weight(axis: dict) -> bool:
    name = axis.get("name", b"")
    return (name.decode() if isinstance(name, bytes) else str(name)).lower() == "weight"


class Captions:
    """Three words at a time, upper case, the spoken word on an accent plate."""

    MAX_WIDTH, PAD = 860, 34

    def __init__(self, groups: list[dict], brand: Brand):
        self.groups, self.brand = groups, brand
        self._images: dict[tuple[int, int], Image.Image] = {}
        self._fonts: dict[int, ImageFont.FreeTypeFont] = {}

    def _font(self, size: int) -> ImageFont.FreeTypeFont:
        if size not in self._fonts:
            self._fonts[size] = weighted_font(self.brand.text_font, size, self.brand.caption_weight)
        return self._fonts[size]

    def _wrap(self, words: list[str], size: int) -> tuple[list[list[tuple]], float]:
        font = self._font(size)
        space = font.getlength(" ") * 0.9
        lines, line, width = [], [], 0.0
        for i, word in enumerate(words):
            length = font.getlength(word)
            if line and width + space + length > self.MAX_WIDTH:
                lines.append(line)
                line, width = [], 0.0
            width += (space if line else 0) + length
            line.append((i, word, length))
        lines.append(line)
        return lines, space

    def _fit(self, words: list[str]) -> tuple[int, list[list[tuple]], float]:
        """The largest size at which the caption sits in two lines."""
        size = 76
        while True:
            lines, space = self._wrap(words, size)
            widest = max(sum(x[2] for x in ln) + space * (len(ln) - 1) for ln in lines)
            if (len(lines) <= 2 and widest <= self.MAX_WIDTH + 20) or size <= 46:
                return size, lines, space
            size -= 4

    def image(self, group: int, active: int) -> Image.Image:
        key = (group, active)
        if key not in self._images:
            self._images[key] = self._draw([w["text"].upper() for w in self.groups[group]["words"]], active)
        return self._images[key]

    def _draw(self, words: list[str], active: int) -> Image.Image:
        size, lines, space = self._fit(words)
        font, line_h = self._font(size), round(size * 1.2)
        text = Image.new("RGBA", (W, line_h * len(lines) + self.PAD * 2), (0, 0, 0, 0))
        shadow = Image.new("RGBA", text.size, (0, 0, 0, 0))
        draw, draw_shadow = ImageDraw.Draw(text), ImageDraw.Draw(shadow)
        for row, line in enumerate(lines):
            x = (W - (sum(w[2] for w in line) + space * (len(line) - 1))) / 2
            y = self.PAD + row * line_h
            for index, word, length in line:
                if index == active:
                    draw.rounded_rectangle((x - 16, y + size * 0.1, x + length + 16, y + size * 1.2), radius=18, fill=self.brand.accent)
                    draw.text((x, y), word, font=font, fill="#fff")
                else:
                    draw_shadow.text((x + 3, y + 5), word, font=font, fill=(0, 0, 0, 150), stroke_width=9, stroke_fill=(0, 0, 0, 150))
                    draw.text((x, y), word, font=font, fill="#fff", stroke_width=7, stroke_fill=self.brand.ink)
                x += length + space
        shadow.alpha_composite(text)
        return shadow

    def state(self, t: float) -> tuple | None:
        """(group, active word, scale) at `t`."""
        for index, group in enumerate(self.groups):
            if not group["t0"] <= t < group["t1"]:
                continue
            words = group["words"]
            active = max((i for i, w in enumerate(words) if w["t"] - 0.03 <= t), default=-1)
            if t > words[-1]["e"] + 0.25:
                active = -1
            return (index, active, round(0.86 + 0.14 * _ease_out(min(1.0, (t - group["t0"]) / 0.1)), 3))
        return None


def _caption_onto(canvas: Image.Image, captions: Captions, state: tuple, stacked: bool) -> None:
    group, active, scale = state
    image = captions.image(group, active)
    if scale != 1.0:
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.BILINEAR)
    y = CAPTION_Y_STACK if stacked else CAPTION_Y
    paste(canvas, image, (W - image.width) // 2, y - image.height // 2)


def frames(layers: list[Layer], captions: Captions, total: float,
           speech: float, stacked: Callable[[float], bool]) -> Iterator[bytes]:
    """Raw RGBA frames for the whole reel, redrawn only when the picture changes."""
    blank = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    last_signature, last_bytes = None, b""
    for n in range(round(total * FPS)):
        t = n / FPS
        states = [(i, s) for i, s in ((i, layer.state(t)) for i, layer in enumerate(layers)) if s]
        caption = captions.state(t) if t < speech else None
        signature = (tuple(states), caption, stacked(t))
        if signature != last_signature:
            canvas = blank.copy()
            for i, state in states:
                layers[i].draw(canvas, state)
            if caption:
                _caption_onto(canvas, captions, caption, stacked(t))
            last_bytes, last_signature = canvas.tobytes(), signature
        yield last_bytes
