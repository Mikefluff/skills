"""Transitions built in the edit, on both sides of a cut — the moves a trailer editor makes between shots.

Each cut has one type (shot_matrix.TRANSITIONS): the incoming shot gets the
"in" half on its first frames, the outgoing shot the "out" half on its last.
Both halves are ffmpeg filter fragments over a frame already scaled to the
cut's size, applied before the grade; a ramp also changes which source frames
the tail shows, so it is a window, not a filter.

  whip   out: the picture slides off left under a horizontal smear (0.15 s)
         in:  slides in from the right side's motion, settling by 0.35 s
  crash  out: snaps in a quarter in the last 3 frames;  in: lands a third tight, settles in 0.3 s
  wipe   a dark band (a back, a doorframe) crosses the lens: enters on the tail, leaves on the head
  flash  two white frames each side of the cut
  ramp   the tail's last 0.5 s shows 0.2 s of action: slow motion into a hard cut
  dip    the tail fades to black, the head fades up from it (0.35 s each): a jump in place or time
  iris   a circle closes on the tail and opens on the head (0.5 s each): the cartoon's own full stop
"""

from __future__ import annotations

_FPS = 24
TAIL = {"whip": 0.3, "wipe": 0.25, "flash": 0.08, "dip": 0.35, "iris": 0.5}
# A whip a viewer reads at full speed: 0.3 s each side, 40 % of the width travelled, a heavy smear.
# The smear is short: at 0.3 s of heavy blur each side, nine whips put 4.5 s of soap into the SAME cut.
_SLIDE, _SMEAR = 1.8, 45
RAMP = (0.5, 0.2)  # seconds of picture, seconds of action in it


def into(kind: str, w: int, h: int) -> str:
    """Filter fragment for the head of a shot entered by `kind` ("" for none)."""
    if kind == "whip":
        k = _SLIDE
        return (f"scale=iw*{k}:-2,crop=iw/{k}:ih/{k}:(iw-iw/{k})/2*(1-pow(1-min(t/0.35\\,1)\\,3)):(ih-ih/{k})/2,"
                f"gblur=sigma={_SMEAR}:sigmaV=0.01:steps=3:enable='lt(t,0.1)',"
                f"gblur=sigma=12:sigmaV=0.01:enable='between(t,0.1,0.17)',scale={w}:{h},setsar=1")
    if kind == "crash":
        n = round(0.3 * _FPS)
        return (f"zoompan=z='if(lt(in,{n}),1.6-0.6*pow(in/{n},0.5),1)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
                f":d=1:s={w}x{h}:fps={_FPS},setsar=1")
    if kind == "wipe":
        return f"gblur=sigma=12:sigmaV=0.01:enable='lt(t,{TAIL['wipe']})'"  # the band itself: wipes()
    if kind == "flash":
        return f"fade=t=in:st=0:d={TAIL['flash']}:color=white"
    if kind == "dip":
        return f"fade=t=in:st=0:d={TAIL['dip']}"
    if kind == "iris":
        return _iris(f"min(T/{TAIL['iris']}\\,1)")
    return ""


def _iris(progress: str) -> str:
    """Black outside a circle whose radius is `progress` (0 closed, 1 the frame's corners) of the half-diagonal."""
    keep = f"lt(hypot(X-W/2\\,Y-H/2)\\,hypot(W/2\\,H/2)*{progress})"
    return f"format=rgb24,geq=r='if({keep}\\,r(X\\,Y)\\,0)':g='if({keep}\\,g(X\\,Y)\\,0)':b='if({keep}\\,b(X\\,Y)\\,0)',format=yuv420p"


def out(kind: str, seconds: float, w: int, h: int) -> str:
    """Filter fragment for the tail of a shot left by `kind` ("" for none)."""
    if kind == "whip":
        d, a, k = TAIL["whip"], seconds - TAIL["whip"], _SLIDE
        return (f"scale=iw*{k}:-2,crop=iw/{k}:ih/{k}:(iw-iw/{k})/2*(1+pow(min(max((t-{a:.3f})/{d}\\,0)\\,1)\\,2)):"
                f"(ih-ih/{k})/2,gblur=sigma={_SMEAR}:sigmaV=0.01:steps=3:enable='gte(t,{a + d * 2 / 3:.3f})',"
                f"scale={w}:{h},setsar=1")
    if kind == "crash":
        n = max(1, round(seconds * _FPS))
        return (f"zoompan=z='if(gte(in,{n - 4}),1+0.5*pow((in-{n - 4})/4,2),1)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
                f":d=1:s={w}x{h}:fps={_FPS},setsar=1")
    if kind == "wipe":
        return f"gblur=sigma=12:sigmaV=0.01:enable='gte(t,{seconds - TAIL['wipe']:.3f})'"  # the band: wipes()
    if kind == "flash":
        return f"fade=t=out:st={seconds - TAIL['flash']:.3f}:d={TAIL['flash']}:color=white"
    if kind == "dip":
        return f"fade=t=out:st={seconds - TAIL['dip']:.3f}:d={TAIL['dip']}"
    if kind == "iris":
        a = seconds - TAIL["iris"]
        return _iris(f"(1-min(max((T-{a:.3f})/{TAIL['iris']}\\,0)\\,1))")
    return ""


def ramp_window(seconds: float) -> tuple[float, float, float]:
    """(normal seconds, slowed source seconds, slow factor) for a tail that ramps into its cut."""
    shown, action = RAMP
    shown = min(shown, seconds / 2)
    return seconds - shown, action * shown / RAMP[0], RAMP[0] / RAMP[1]


def wipes(into_kind: str, out_kind: str, seconds: float) -> list[tuple[str, str]]:
    """(overlay x expression, enable expression) of the dark band for each wiped side of a shot.

    The band is a black layer laid over the picture by `overlay` (whose `t` is time; drawbox's `t` is its
    border thickness, so a drawbox cannot move). It leaves to the right on the head, enters from the left on
    the tail, so the shape crossing the lens is continuous across the cut."""
    d = TAIL["wipe"]
    bands = []
    if into_kind == "wipe":
        bands.append((f"W*t/{d}", f"lt(t,{d})"))
    if out_kind == "wipe":
        a = seconds - d
        bands.append((f"-W+W*(t-{a:.3f})/{d}", f"gte(t,{a:.3f})"))
    return bands
