"""Soundtrack of a voiced film: sources, placements, and the ffmpeg graph that mixes them.

Seedance's own audio is not used. It re-voices the reference, invents a score
nobody asked for, and puts every sound where the model guessed rather than where
the cut needs it. A film's sound is designed instead, the way a mixer would:

  sources     what gets generated once — music cues (Eleven Music, composition
              plan), sound effects and ambience beds (Eleven sound generation)
  placements  where a slice of a source sits on the film clock, how loud, with
              what treatment, and whether it ducks under the voice

A dramatic music edit is placements, not generation. A cue killed on the turn is
one placement ending there; the same cue heard again from far away is a second
placement of the same source, later offset, with `fx: "distant"`. Music models
cannot hold a 1.8-second silence (sections start at 3 s); a cut can.

Pure: spec validation, graph building, and the hit-snapping arithmetic. The
ffmpeg and API calls live in `ffmpeg_film` and `cli/_reel_sound`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Treatments a placement can ask for. Kept to a closed set so a prompt-writing
# model cannot hand ffmpeg an arbitrary filter string.
FX: dict[str, str] = {
    "none": "",
    # The prepared show, heard from outside it: top end gone, room around it.
    "distant": "lowpass=f=1100,aecho=0.8:0.55:70|140:0.35|0.22",
    # Through a wall or under water.
    "muffled": "lowpass=f=450",
    # Small speaker, monitor wedge.
    "thin": "highpass=f=500,lowpass=f=3500",
}


@dataclass(frozen=True)
class Placement:
    source: str
    at: float
    offset: float = 0.0
    length: float | None = None
    gain_db: float = 0.0
    fade_in: float = 0.01
    fade_out: float = 0.02
    fx: str = "none"
    duck: bool = False
    snap: bool = False
    pitch: float = 0.0  # semitones, timing kept (a child's voice lifted out of an adult range)

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "Placement":
        fields = {k: raw[k] for k in cls.__dataclass_fields__ if k in raw}
        placement = cls(**fields)
        if placement.fx not in FX:
            raise ValueError(f"placement of '{placement.source}': unknown fx '{placement.fx}' (have {sorted(FX)})")
        return placement


@dataclass(frozen=True)
class Master:
    lufs: float = -14.0
    true_peak: float = -1.0


def validate(sound: dict[str, Any]) -> list[Placement]:
    """Placements, checked against the declared sources. Raises ValueError."""
    ids = [s["id"] for s in sound.get("sources") or []]
    if len(ids) != len(set(ids)):
        raise ValueError("sound.sources has duplicate ids")
    placements = [Placement.from_json(p) for p in sound.get("placements") or []]
    for p in placements:
        if p.source not in ids:
            raise ValueError(f"placement refers to unknown source '{p.source}'")
        if p.at < 0 or p.offset < 0 or (p.length is not None and p.length <= 0):
            raise ValueError(f"placement of '{p.source}' at {p.at}: negative time or empty length")
    return placements


def pitch_filter(semitones: float) -> str:
    """A voice moved by `semitones`, its length kept (rubberband; formants move with it, as a smaller throat)."""
    return f"rubberband=pitch={2 ** (max(-12.0, min(12.0, semitones)) / 12):.4f}"


def _chain(index: int, p: Placement, label: str) -> str:
    parts = [f"[{index}:a]aresample=48000"]
    end = f":end={p.offset + p.length:.3f}" if p.length is not None else ""
    parts.append(f"atrim=start={p.offset:.3f}{end},asetpts=PTS-STARTPTS")
    if FX[p.fx]:
        parts.append(FX[p.fx])
    if p.pitch:
        parts.append(pitch_filter(p.pitch))
    parts.append(f"volume={p.gain_db:.1f}dB")
    if p.fade_in > 0:
        parts.append(f"afade=t=in:st=0:d={p.fade_in:.3f}")
    if p.fade_out > 0 and p.length is not None:
        parts.append(f"afade=t=out:st={max(0.0, p.length - p.fade_out):.3f}:d={p.fade_out:.3f}")
    parts.append(f"adelay={int(round(p.at * 1000))}:all=1")
    return ",".join(parts) + f"[{label}]"


def build_graph(
    placements: list[Placement], sources: dict[str, Path], voice: Path, total: float, master: Master = Master()
) -> tuple[list[str], str]:
    """(input args, filter_complex) for the full mix, output label [out].

    Input 0 is the voice. Ducked placements are summed and compressed with the
    voice as the key, so music drops under speech and comes back in the gaps;
    effects sit on top unducked, because a smoke cannon does not politely wait
    for a sentence to end.
    """
    inputs = ["-i", str(voice)]
    # The voice sits on top: +5 dB on its bus before anything is summed. Measured on a trailer, lines at
    # -16 LUFS under a -3 dB groove and room beds came out under everything once the master was normalised.
    chains = ["[0:a]aresample=48000,volume=5dB,asplit=2[voice][key]"]
    ducked, straight = [], ["[voice]"]
    for n, p in enumerate(placements, start=1):
        inputs += ["-i", str(sources[p.source])]
        label = f"p{n}"
        chains.append(_chain(n, p, label))
        (ducked if p.duck else straight).append(f"[{label}]")
    if ducked:
        chains.append(f"{''.join(ducked)}amix=inputs={len(ducked)}:normalize=0:duration=longest[bed]")
        chains.append("[bed][key]sidechaincompress=threshold=0.015:ratio=12:attack=10:release=350[ducked]")
        straight.append("[ducked]")
    else:
        chains.append("[key]anullsink")
    chains.append(
        f"{''.join(straight)}amix=inputs={len(straight)}:normalize=0:duration=longest,"
        f"atrim=end={total:.3f},apad=whole_dur={total:.3f},"
        f"loudnorm=I={master.lufs}:TP={master.true_peak}:LRA=11[out]"
    )
    return inputs, ";".join(chains)


def snap_time(at: float, hits: list[tuple[float, float]], *, window: float = 0.5, floor: float = 6.0) -> float:
    """Move a hit to the strongest visual jump within ±window, if one is strong enough.

    `hits` are (time, brightness jump on a 0-255 scale) per frame. The model
    stages "the drop flash at 5.4 s" somewhere near 5.4 s; the sound has to be
    where the flash actually is, or the viewer hears it before they see it.
    """
    near = [(t, mag) for t, mag in hits if abs(t - at) <= window and mag >= floor]
    if not near:
        return at
    return round(max(near, key=lambda h: h[1])[0], 3)


def brightness_jumps(lumas: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Per-frame (time, mean luma) → (time, absolute change from the previous frame)."""
    return [(t, abs(y - prev_y)) for (_, prev_y), (t, y) in zip(lumas, lumas[1:])]
