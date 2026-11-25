"""Covers and contact sheets for a recut series.

The cover is a frame of the speaker with the title set over it — the same
browser-rendered type as the reel, so the feed reads as one series. The contact
sheet is how a finished reel is checked without watching it sixteen times:
sixteen frames side by side show a caption over a face or a graphic that never
arrived at a glance.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from string import Template

from PIL import Image

from . import recut_css as css
from . import recut_layers as layers_mod
from .recut_plan import H, W, Plan
from .recut_scene import Scene, esc

COVER_FACE_Y = 620


def _frame_crop(zoom: float, face: tuple[float, float]) -> tuple[int, int, int, int]:
    """Scaled size and crop offset that put the face at the cover's focal point.

    Computed here, not in an ffmpeg expression: a comma inside `crop=` splits
    the filter and the frame comes out blank.
    """
    fx, fy = face
    w, h = round(W * zoom / 2) * 2, round(H * zoom / 2) * 2
    x = int(-max(min(0, W / 2 - fx * w), W - w))
    y = int(-max(min(0, COVER_FACE_Y - fy * h), H - h))
    return w, h, x, y


def _grab(plan: Plan, ep: dict, frame: Path) -> None:
    cover = ep.get("cover", {})
    zoom = float(cover.get("zoom", plan.presets(ep)["close"][0]))
    w, h, x, y = _frame_crop(zoom, tuple(ep["face"]))
    done = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", str(cover.get("t", 1.0)), "-i", str(plan.path(ep["src"])), "-frames:v", "1",
         "-vf", f"scale={w}:{h}:flags=lanczos,crop={W}:{H}:{x}:{y},eq=saturation=1.08:contrast=1.03", "-q:v", "2", str(frame)],
        capture_output=True, text=True, check=False,
    )
    if done.returncode:
        raise RuntimeError(f"cover frame for {ep['slug']} failed: {done.stderr[-200:]}")


def _cover_page(plan: Plan, ep: dict, frame: Path) -> str:
    brand = plan.brand
    lines = "".join(
        f'<div class="{"hl" if line.startswith("*") else "ln"}">{esc(line.strip("*"))}</div>'
        for line in ep.get("cover", {}).get("lines", ep["hook"])
    )
    badge = f"<b>{ep['n']}/{len(plan.episodes)}</b>" if len(plan.episodes) > 1 else ""
    series = f"<span>{esc(plan.series)}</span>" if plan.series else ""
    name, tld = brand.wordmark
    body = (f'<div class="bgi"></div><div class="sc"></div><div class="num">{badge}{series}</div>'
            f'<div class="ttl">{lines}</div><div class="site">{esc(name)}<em>{esc(tld)}</em></div>')
    extra = Template(css.COVER_CSS).substitute(frame=frame.as_uri(), accent=brand.accent, second=brand.second, ink=brand.ink)
    return Scene(brand, lambda t: t, 0.0).page(body, extra)


def cover(plan: Plan, ep: dict, chrome: str) -> Path:
    """`<out>/covers/<slug>.jpg`, 1080x1920."""
    work = plan.work / ep["slug"]
    work.mkdir(parents=True, exist_ok=True)
    frame, page, png = work / "cover_frame.jpg", work / "cover.html", work / "cover.png"
    _grab(plan, ep, frame)
    page.write_text(_cover_page(plan, ep, frame), encoding="utf-8")
    png.unlink(missing_ok=True)
    layers_mod.screenshot(chrome, page, png, plan.work / "png" / "chrome-cover")
    out = plan.out / "covers" / f"{ep['slug']}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.open(png).convert("RGB").save(out, quality=93)
    return out


def contact_sheet(video: Path, out: Path, seconds: float, frames: int = 16) -> Path:
    """Evenly spaced frames of a finished reel, in two rows."""
    out.parent.mkdir(parents=True, exist_ok=True)
    done = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(video),
         "-vf", f"fps={frames}/{seconds},scale=270:480,tile={frames // 2}x2", "-frames:v", "1", str(out)],
        capture_output=True, text=True, check=False,
    )
    if done.returncode:
        raise RuntimeError(f"contact sheet for {video.name} failed: {done.stderr[-200:]}")
    return out
