"""Lines read before: each line's clip kept by what that line alone was asked with.

A take is one request for a whole exchange, so its key changes whenever the exchange does: a silent shot put
in between two lines, or a speaking one cut, splits or joins exchanges, and every line in them was bought
again in another reading (the Tanya short lost its approved performances to a few coverage inserts). Each
line's clip is therefore also kept by its own key (its text, voice, room and language; _animatic_voice
makes it) in <cache>/lines.json, and an exchange whose lines were all read before is put together from
them, never bought again. The first reading of a line stays: it is the one the cut was judged with.
"""

from __future__ import annotations

import json
from pathlib import Path


def _known(cache: Path) -> dict[str, str]:
    path = cache / "lines.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def read_before(cache: Path, keys: list[str]) -> list[Path] | None:
    """Each line's clip from the take it was first read in, when every line was; else None."""
    known = _known(cache)
    clips = [cache / known[k] for k in keys if k in known]
    return clips if len(clips) == len(keys) and all(c.is_file() for c in clips) else None


def remember(cache: Path, keys: list[str], clips: list[Path]) -> None:
    """Record where each line of a take was cut to; a line already recorded keeps its first reading."""
    known = _known(cache)
    added = {k: c.name for k, c in zip(keys, clips) if k not in known}
    if added:
        (cache / "lines.json").write_text(json.dumps({**known, **added}, indent=1, sort_keys=True), encoding="utf-8")
