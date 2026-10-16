"""A device's view laid over a shot — the camera's OSD and the face system's boxes, in the film's identity.

When a scene shows footage being watched (a parking camera on a meeting-room
wall, a kiosk, a dash camera), the generation renders the picture and this
draws the machine on top of it: the camera's name, date and running clock, a
REC mark, and detection boxes that follow each tracked person with what the
system believes about them ("MINH TRAN 98.7%"). The boxes are keyed by hand
(times and pixel boxes read off the clip) in the shot's "overlay" block, so a
re-render keeps them, and they share the title cards' brackets and colours.

  "overlay": {"camera": "CAM 5A-142", "date": "2026-10-12", "clock": "23:41:07",
              "footer": "EIDOLON ONE  ·  FACE MATCH",
              "tracks": [{"label": "MINH TRAN  98.7%", "colour": "cyan", "until": 4.0,
                          "keys": [[1.0, 280, 140, 327, 280], [3.0, 307, 147, 363, 307]]}]}
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from .title_cards import CYAN, RED, WHITE, _brackets, _font, _MONO

_COLOURS = {"cyan": CYAN, "white": WHITE, "red": RED}


def _box_at(keys: list[list[float]], t: float) -> tuple[float, ...] | None:
    """The track's box at time t, interpolated between its keys; None outside them."""
    if not keys or t < keys[0][0] or t > keys[-1][0]:
        return None
    for (t0, *b0), (t1, *b1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return tuple(a + (b - a) * f for a, b in zip(b0, b1))
    return tuple(keys[-1][1:])


def _clock(start: str, t: float) -> str:
    h, m, s = (int(x) for x in start.split(":"))
    total = h * 3600 + m * 60 + s + int(t)
    return f"{total // 3600 % 24:02d}:{total // 60 % 60:02d}:{total % 60:02d}.{int((t % 1) * 100):02d}"


def _osd(draw: ImageDraw.ImageDraw, spec: dict[str, Any], t: float, size: tuple[int, int], font) -> None:
    """Camera name, date, running clock, REC blinking once a second, the system's footer."""
    w, h = size
    draw.text((16, 12), f"{spec.get('camera', 'CAM 01')}   {spec.get('date', '')}   {_clock(spec.get('clock', '00:00:00'), t)}",
              font=font, fill=WHITE)
    if int(t * 2) % 2 == 0:
        draw.ellipse([w - 86, 15, w - 74, 27], fill=RED)
    draw.text((w - 68, 12), "REC", font=font, fill=WHITE)
    draw.text((16, h - 30), spec.get("footer", ""), font=font, fill=CYAN)


def _tracks(draw: ImageDraw.ImageDraw, spec: dict[str, Any], t: float, font) -> None:
    for track in spec.get("tracks") or []:
        if t > float(track.get("until", 1e9)):
            continue
        box = _box_at(track["keys"], t)
        if box is None:
            continue
        colour = _COLOURS.get(track.get("colour", "cyan"), CYAN)
        _brackets(draw, box, colour, 1.0, stroke=(2, 4))
        below = track.get("label_at") == "below"  # two labels that would collide: one goes under its box
        draw.text((box[0] - 4, box[3] + 8 if below else box[1] - 22), track["label"], font=font, fill=colour)


def render(video: Path, spec: dict[str, Any], out: Path, *, ffmpeg_bin: str = "ffmpeg") -> Path:
    """`video` with the device's OSD and tracked boxes burned in, sound kept."""
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(probe[0]), int(probe[1])
    num, den = (int(x) for x in probe[2].split("/"))
    fps = num / den
    font = _font(_MONO, max(12, h // 30))
    reader = subprocess.Popen([ffmpeg_bin, "-loglevel", "error", "-i", str(video), "-f", "rawvideo",
                               "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    writer = subprocess.Popen([ffmpeg_bin, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-i", str(video), "-map", "0:v",
                               "-map", "1:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy",
                               str(out)], stdin=subprocess.PIPE)
    n, frame_bytes = 0, w * h * 3
    while True:
        raw = reader.stdout.read(frame_bytes)
        if len(raw) < frame_bytes:
            break
        img = Image.fromarray(np.frombuffer(raw, np.uint8).reshape(h, w, 3).copy())
        draw = ImageDraw.Draw(img)
        _osd(draw, spec, n / fps, (w, h), font)
        _tracks(draw, spec, n / fps, font)
        writer.stdin.write(img.tobytes())
        n += 1
    writer.stdin.close()
    reader.wait()
    if writer.wait() != 0:
        raise RuntimeError(f"ffmpeg failed burning the overlay into {video}")
    return out
