"""Subtitle parsers — SRT + VTT → list of (start_seconds, end_seconds, text) tuples.

Used by subtitle-burner to feed ffmpeg.burn_captions. No external deps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Cue:
    start: float
    end: float
    text: str

    def as_tuple(self) -> tuple[float, float, str]:
        return (self.start, self.end, self.text)


_TIMECODE_RE = re.compile(
    r"^(\d{1,2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[.,](\d{3})"
)


def _parse_timecode(s: str) -> tuple[float, float] | None:
    """Parse 'HH:MM:SS,mmm --> HH:MM:SS,mmm' (SRT, comma) or
    'HH:MM:SS.mmm --> HH:MM:SS.mmm' (VTT, dot). Returns (start, end) in seconds.
    """
    m = _TIMECODE_RE.match(s.strip())
    if not m:
        return None
    h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
    start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
    end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
    return start, end


_TAG_RE = re.compile(r"<[^>]+>")

# VTT blocks that carry metadata rather than a cue.
_VTT_METADATA = ("NOTE", "STYLE", "REGION")


def _split_blocks(text: str) -> list[str]:
    return re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())


def _cue_from_block(block: str, *, strip_tags: bool = False) -> Cue | None:
    """One cue from one block, or None if the block has no timecode or no text.

    Both formats allow a line before the timecode — an index in SRT, an
    optional cue identifier in VTT — so the timecode is found by scanning
    rather than assumed to sit first.
    """
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if len(lines) < 2:
        return None

    for index, line in enumerate(lines):
        span = _parse_timecode(line)
        if span is not None:
            break
    else:
        return None

    body = lines[index + 1:]
    if strip_tags:
        body = [_TAG_RE.sub("", ln) for ln in body]
    text = " ".join(ln.strip() for ln in body).strip()
    if not text:
        return None
    return Cue(start=span[0], end=span[1], text=text)


def parse_srt(text: str) -> list[Cue]:
    """Parse SRT subtitle text. Returns ordered list of Cue."""
    parsed = (_cue_from_block(block) for block in _split_blocks(text))
    return [cue for cue in parsed if cue is not None]


def parse_vtt(text: str) -> list[Cue]:
    """Parse WebVTT subtitle text. Returns ordered list of Cue."""
    content = text.replace("\r\n", "\n").strip()
    if content.startswith("WEBVTT"):
        # The header block is not a cue; everything after the first blank line is.
        parts = re.split(r"\n\s*\n", content, maxsplit=1)
        content = parts[1] if len(parts) > 1 else ""

    parsed = (
        # Inline tags (<c>, <i>, <b>, <v>, <ruby>) would be drawn literally.
        _cue_from_block(block, strip_tags=True)
        for block in _split_blocks(content)
        if not block.strip().startswith(_VTT_METADATA)
    )
    return [cue for cue in parsed if cue is not None]


def parse_file(path: Path) -> list[Cue]:
    """Parse SRT or VTT based on file extension."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".vtt":
        return parse_vtt(text)
    if suffix == ".srt":
        return parse_srt(text)
    # Auto-detect from content
    if text.lstrip().startswith("WEBVTT"):
        return parse_vtt(text)
    return parse_srt(text)


def parse_plain_text(text: str, *, video_duration: float, gap_seconds: float = 0.0) -> list[Cue]:
    """Split plain text into evenly-timed cues across a video.

    Each line of text becomes one cue. Total = N cues distributed evenly with
    optional gap between them.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines or video_duration <= 0:
        return []
    n = len(lines)
    per_line = (video_duration - gap_seconds * (n - 1)) / n
    if per_line <= 0:
        per_line = video_duration / n
        gap_seconds = 0
    cues: list[Cue] = []
    cursor = 0.0
    for ln in lines:
        end = min(cursor + per_line, video_duration)
        cues.append(Cue(start=cursor, end=end, text=ln))
        cursor = end + gap_seconds
    return cues


def cues_to_tuples(cues: Iterable[Cue]) -> list[tuple[float, float, str]]:
    return [c.as_tuple() for c in cues]
