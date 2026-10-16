"""Screen replacement — footage played on a screen inside a generated shot, behind the people in front of it.

A generation is asked to leave its screen a flat, even glow (it cannot draw
our footage on it faithfully). Here the footage is warped onto the screen's
four corners, keyed by hand at a few times and interpolated (the camera may
push), and laid only where the plate still shows that glow — so a head
in front of the screen stays in front. The insert is dimmed and lifted toward
the screen's own colour so it reads as light coming off a panel, not a paste.

  python -c "from common.runners import screen_replace as s; s.render(plate, insert, keys, out)"
  keys: [[t, [[x,y] top-left, top-right, bottom-right, bottom-left]], ...] in plate pixels
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def _probe(video: Path) -> tuple[int, int, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    num, den = (int(x) for x in out[2].split("/"))
    return int(out[0]), int(out[1]), num / den


def _frames(video: Path, w: int, h: int, start: float = 0.0):
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", str(video),
                             "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE)
    size = w * h * 3
    while True:
        raw = proc.stdout.read(size)
        if len(raw) < size:
            break
        yield np.frombuffer(raw, np.uint8).reshape(h, w, 3)
    proc.wait()


def corners_at(keys: list, t: float) -> list[list[float]]:
    """The screen's four corners at time t, linear between keys, held outside them."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, c0), (t1, c1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return [[a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f] for a, b in zip(c0, c1)]
    return keys[-1][1]


def _coeffs(dst: list[list[float]], w: int, h: int) -> list[float]:
    """PIL perspective coefficients mapping the plate's quad back to the insert's rectangle."""
    src = [[0, 0], [w, 0], [w, h], [0, h]]
    rows = []
    for (x, y), (u, v) in zip(dst, src):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    rhs = [c for pair in src for c in pair]
    return list(np.linalg.solve(np.array(rows, float), np.array(rhs, float)))


def _key(plate: np.ndarray, warped_alpha: np.ndarray) -> np.ndarray:
    """Where the plate still shows the screen's glow (bright, low saturation) inside the quad; feathered."""
    p = plate.astype(np.float32)
    bright = p.mean(axis=2) > 140
    # The glow is cool (blue over red); pale skin and blonde hair are warm, so they stay in front.
    flat = ((p.max(axis=2) - p.min(axis=2)) < 70) & (p[..., 2] - p[..., 0] > 14)
    mask = Image.fromarray(((bright & flat) * warped_alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    return np.asarray(mask, np.float32)[..., None] / 255.0


def composite(plate: np.ndarray, insert: np.ndarray, corners: list[list[float]],
              holdouts: list | None = None) -> np.ndarray:
    """`holdouts`: [x0, y0, x1, y1] boxes never keyed — a pale head that crosses the screen's edge."""
    h, w = plate.shape[:2]
    ih, iw = insert.shape[:2]
    coeffs = _coeffs(corners, iw, ih)
    warped = Image.fromarray(insert).transform((w, h), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
    alpha = Image.new("L", (iw, ih), 255).transform((w, h), Image.Transform.PERSPECTIVE, coeffs)
    region = np.asarray(alpha, np.float32) / 255.0
    for x0, y0, x1, y1 in holdouts or []:
        region[int(y0):int(y1), int(x0):int(x1)] = 0
    m = _key(plate, region)
    glow = np.asarray(warped, np.float32) * 0.82 + np.array([18, 30, 34], np.float32)  # light off a panel
    return (plate * (1 - m) + np.clip(glow, 0, 255) * m).astype(np.uint8)


def render(plate: Path, insert: Path, keys: list, out: Path, **opts) -> Path:
    """opts: insert_start (seconds into the insert), holdouts (boxes never keyed)."""
    insert_start, holdouts = float(opts.get("insert_start", 0.0)), opts.get("holdouts")
    """The plate with `insert` (from insert_start) playing on its screen; the plate's sound kept."""
    w, h, fps = _probe(plate)
    iw, ih, _ = _probe(insert)
    writer = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-i", str(plate), "-map", "0:v",
                               "-map", "1:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy",
                               "-shortest", str(out)], stdin=subprocess.PIPE)
    inserts = _frames(insert, iw, ih, insert_start)
    last = None
    for n, frame in enumerate(_frames(plate, w, h)):
        last = next(inserts, last)
        out_frame = composite(frame, last, corners_at(keys, n / fps), holdouts) if last is not None else frame
        writer.stdin.write(out_frame.tobytes())
    writer.stdin.close()
    if writer.wait() != 0:
        raise RuntimeError(f"ffmpeg failed writing {out}")
    return out
