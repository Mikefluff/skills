"""One grade over every shot of a cut — the look is laid on in the edit, not asked of each generation.

Generations colour every clip their own way: one comes back soft and even, the
next teal, the next flat. A film's look is one grade, so the cut applies it to
each clip after trimming, the same filter on every shot. A plan names its grade
("grade": "rocknrolla"); a plan without one is cut as rendered.

  rocknrolla — RocknRolla (2008, David Higgs): bleach-bypass contrast with the
               blacks crushed, steel-blue to teal shadows, skin pushed warm,
               desaturated mids, a red-orange halation round the practicals,
               visible grain moving per frame.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# Each filter is one -vf chain; internal pad labels are prefixed g* so the chain
# can sit inside a larger -filter_complex without clashing.
GRADES = {
    # an animated feature: generations from different takes brought to one candy look — gentle contrast,
    # a touch of saturation, blacks and whites set the same everywhere, no grain
    "candy": "eq=contrast=1.05:saturation=1.07:gamma=0.99,curves=all='0/0 0.05/0.03 0.5/0.51 0.95/0.97 1/1'",
    "rocknrolla": (
        # bleach bypass: the picture's own luma laid over it in overlay. The format is pinned before the
        # split: left open, ffmpeg carries the branch's gray back up the chain and the whole picture goes mono.
        "format=gbrp,split[ga][gb];[gb]format=gray,format=gbrp[gl];[ga]format=gbrp[gc];"
        "[gc][gl]blend=all_mode=overlay:all_opacity=0.3,"
        "eq=contrast=1.12:saturation=0.78:gamma=1.08,"
        # shadows to steel-blue, mids and highlights to warm skin
        "colorbalance=rs=-0.07:bs=0.08:rm=0.05:gm=0.01:bm=-0.04:rh=0.06:gh=0.02:bh=-0.05,"
        "curves=all='0/0 0.07/0.01 0.45/0.47 0.9/0.95 1/1',"
        # halation: the brightest parts blurred, tinted red-orange, screened back
        "split[gx][gy];[gy]curves=all='0/0 0.8/0 1/1',gblur=sigma=14,"
        "colorchannelmixer=rr=1:gg=0.45:bb=0.25[gh];[gx][gh]blend=all_mode=screen:all_opacity=0.35,"
        "noise=c0s=12:c0f=t+u,format=yuv420p"
    ),
}


def apply(clip: Path, grade: str | None, out: Path) -> Path:
    """`clip` with the named grade burnt in, sound copied; the clip itself when no grade is named."""
    if not grade:
        return clip
    if grade not in GRADES:
        raise ValueError(f"unknown grade {grade!r}; known: {', '.join(GRADES)}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-vf", GRADES[grade],
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy", str(out)],
                   check=True, capture_output=True)
    return out
