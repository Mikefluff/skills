"""Word timings from a TTS alignment, and the cut points a voiced film can survive.

A voiced film longer than one generation has to be made in pieces, and every
piece boundary is a place where the picture can jump and the voice can break.
The voice does not have to break: it is one continuous ElevenLabs take, laid
over the finished cut, and no segment ever carries its own copy of it. What
each segment does carry is a slice of that take as a lip-sync reference, so
the slice has to begin and end in silence — a cut through a word leaves one
segment mouthing half a syllable that the other segment repeats.

So cuts go in the pauses between words, preferring the longest ones and the
ones after a sentence ends, and never more than one generation apart. That is
an ordinary shortest-path problem over the pauses, solved here exactly rather
than greedily, because the greedy answer — cut as late as possible each time —
leaves a two-second runt at the end that no model renders well.

Pure functions, no ffmpeg and no network. The CLI in `cli/reel_voice.py` does
the I/O around them.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class Segment:
    """One generation's worth of film.

    `start`/`end` are positions in the master voice track. `request_seconds` is
    what the video model is asked for: whole seconds, at least the model's
    minimum, never less than the span — the overshoot is trimmed at stitch time
    and the next segment starts from the trimmed frame, not the generated one.
    """

    index: int
    start: float
    end: float
    request_seconds: int
    words: tuple[Word, ...]

    @property
    def span(self) -> float:
        return round(self.end - self.start, 3)

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    def to_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "start": self.start,
            "end": self.end,
            "span": self.span,
            "request_seconds": self.request_seconds,
            "text": self.text,
            # Relative to the segment, because that is the clock the segment's
            # prompt is written against: "[2.4s] he presses play".
            "words": [
                {**asdict(w), "start": round(w.start - self.start, 3), "end": round(w.end - self.start, 3)}
                for w in self.words
            ],
        }


@dataclass(frozen=True)
class CutRules:
    """Model limits plus how fussy to be about where a cut lands.

    min_gap: a pause shorter than this is a breath inside a phrase, not a
    place to cut. 0.18 s keeps sentence and clause boundaries and rejects the
    gaps ElevenLabs leaves between ordinary words.
    """

    max_seconds: float = 15.0
    min_seconds: float = 4.0
    min_gap: float = 0.18


_SENTENCE_END = (".", "!", "?", "…", ":", ";")


def words_from_alignment(alignment: dict[str, Any]) -> list[Word]:
    """Character-level ElevenLabs alignment → words.

    `/with-timestamps` returns three parallel lists — characters, their start
    times, their end times. A word is a maximal run of non-space characters;
    its span runs from its first character's start to its last one's end.
    Audio tags are direction, not speech, and are dropped whole — including
    v4's multi-word ones (`[dry, sarcastic]`), which a split on spaces would
    otherwise turn into the two "words" `[dry,` and `sarcastic]`.
    """
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    if not (len(chars) == len(starts) == len(ends)):
        raise ValueError("alignment lists differ in length")

    words: list[Word] = []
    buf: list[int] = []

    def flush() -> None:
        if buf:
            words.append(Word("".join(chars[i] for i in buf), float(starts[buf[0]]), float(ends[buf[-1]])))
            buf.clear()

    for i, spoken in enumerate(_spoken(chars)):
        if spoken:
            buf.append(i)
        else:
            flush()
    flush()
    return words


def _spoken(chars: list[str]) -> list[bool]:
    """Per character: part of a spoken word (not whitespace, not inside [...])."""
    out, depth = [], 0
    for ch in chars:
        if ch == "[":
            depth += 1
        out.append(depth == 0 and not ch.isspace() and ch != "]")
        if ch == "]":
            depth = max(0, depth - 1)
    return out


def strip_tags(text: str) -> str:
    """The words that are actually spoken — what forced alignment must be given."""
    return " ".join(re.sub(r"\[[^\]]*\]", " ", text).split())


def _gap_cost(before: Word, gap: float) -> float:
    """Cheaper the longer the pause, cheaper again after a full stop."""
    cost = 1.0 / gap
    if before.text.rstrip("»\"')").endswith(_SENTENCE_END):
        cost *= 0.35
    return cost


def _candidates(words: list[Word], rules: CutRules) -> list[tuple[float, float]]:
    """(cut time, cost) for every pause long enough to cut in."""
    out: list[tuple[float, float]] = []
    for before, after in zip(words, words[1:]):
        gap = after.start - before.end
        if gap >= rules.min_gap:
            out.append((round(before.end + gap / 2, 3), _gap_cost(before, gap)))
    return out


def plan_cuts(words: list[Word], total: float, rules: CutRules = CutRules()) -> list[float]:
    """Cut times, excluding 0 and `total`, minimising segments then cut cost.

    Raises ValueError when no assignment exists — a run of speech longer than
    one generation with no pause in it. The fix is in the script (add a
    `[pause]` or a full stop), not here.
    """
    if total <= rules.max_seconds:
        return []

    points = [(0.0, 0.0), *_candidates(words, rules), (round(total, 3), 0.0)]
    # best[i] = (segments, cost, previous index) for reaching points[i]
    best: list[tuple[int, float, int] | None] = [None] * len(points)
    best[0] = (0, 0.0, -1)
    for i in range(1, len(points)):
        t_i, c_i = points[i]
        for j in range(i):
            if best[j] is None:
                continue
            length = t_i - points[j][0]
            if length < rules.min_seconds or length > rules.max_seconds:
                continue
            segs, cost, _ = best[j]
            cand = (segs + 1, cost + c_i, j)
            if best[i] is None or cand[:2] < best[i][:2]:
                best[i] = cand
    if best[-1] is None:
        raise ValueError(
            f"no cut plan keeps every segment within {rules.min_seconds:g}-{rules.max_seconds:g}s "
            "with cuts in pauses; add a pause or a sentence break to the script"
        )

    cuts: list[float] = []
    i = best[-1][2]
    while i > 0:
        cuts.append(points[i][0])
        i = best[i][2]
    return sorted(cuts)


def segments(words: list[Word], total: float, rules: CutRules = CutRules()) -> list[Segment]:
    bounds = [0.0, *plan_cuts(words, total, rules), round(total, 3)]
    out: list[Segment] = []
    for n, (start, end) in enumerate(zip(bounds, bounds[1:]), start=1):
        inside = tuple(w for w in words if w.start >= start and w.end <= end)
        request = max(int(rules.min_seconds), math.ceil(end - start - 1e-6))
        out.append(Segment(n, start, end, request, inside))
    return out


# --- Conforming the voice to a generated picture ---------------------------
#
# A video model given the take as an audio reference does not play it back: it
# re-performs the script in its own rhythm, a second early here and two late
# there, and drops words. The mouth follows that performance, so laying the
# master take over the picture puts every line beside the lips that say it.
# Conforming moves the master instead: each phrase goes where the picture says
# it, stretched within limits to the length the picture says it in. The
# performance survives phrase by phrase; only the gaps between phrases change.


@dataclass(frozen=True)
class Move:
    """Master [src_start, src_end) played from `dst_start`, `tempo` times faster."""

    src_start: float
    src_end: float
    dst_start: float
    tempo: float = 1.0

    @property
    def dst_end(self) -> float:
        return self.dst_start + (self.src_end - self.src_start) / self.tempo


def _norm(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum())


def phrases(words: list[Word], pause: float = 0.25) -> list[list[Word]]:
    """Breath groups — the unit a performance is moved in.

    A run of words ends at a sentence end or at a pause of `pause` or longer.
    Sentences alone are too coarse: a model re-performing a line keeps its
    words but shortens its pauses, and a whole sentence moved as one block
    drifts off the mouth by the length of every pause it kept.
    """
    out: list[list[Word]] = [[]]
    for w, nxt in zip(words, [*words[1:], None]):
        out[-1].append(w)
        if w.text.rstrip("»\"')").endswith(_SENTENCE_END) or (nxt and nxt.start - w.end >= pause):
            out.append([])
    return [p for p in out if p]


def _matches(phrase: list[Word], heard: list[Word], from_: int) -> tuple[list[tuple[Word, Word]], int]:
    """In-order matches of the phrase's words in what the picture said.

    Words under three letters are skipped: "не" and "я" occur everywhere and
    a match on one of them is as likely to be the wrong sentence as the right one.
    """
    pairs, j = [], from_
    for w in phrase:
        key = _norm(w.text)
        if len(key) < 3:
            continue
        for k in range(j, min(j + 6, len(heard))):
            if _norm(heard[k].text) == key:
                pairs.append((w, heard[k]))
                j = k + 1
                break
    return pairs, j


@dataclass(frozen=True)
class ConformRules:
    """How far a phrase may be bent toward the picture.

    stretch: tempo bounds; past them a phrase sounds sped up or dragged.
    max_shift: farther than this, the model moved the phrase into another shot.
    pad: kept around each phrase so its attack and release are not clipped.
    gap: the least silence left between two moved phrases.
    """

    stretch: tuple[float, float] = (0.85, 1.15)
    max_shift: float = 2.0
    pad: float = 0.06
    gap: float = 0.05


def conform(
    master: list[Word],
    heard: list[Word],
    rules: ConformRules = ConformRules(),
    *,
    carry: bool = True,
) -> list[Move]:
    """One Move per phrase, in order and never overlapping.

    Tempo is measured start-to-start: the two transcripts end words
    differently (alignment keeps the release, speech-to-text clips it), starts
    they agree on. A phrase the picture says more than `rules.max_shift` away was
    moved by the model into another shot — over a cutaway, where the script
    pinned it and the sound design hits on it — so it stays where the master
    has it. A phrase the picture never says keeps its neighbour's shift — or,
    with `carry=False` (a film of separate shots, where unheard phrases are
    voice-over), stays where the master has it.
    """
    moves: list[Move] = []
    j, shift = 0, 0.0
    for phrase in phrases(master):
        pairs, j_next = _matches(phrase, heard, j)
        tempo = 1.0
        if pairs:
            deltas = sorted(h.start - m.start for m, h in pairs)
            median = deltas[len(deltas) // 2]
            if abs(median) <= rules.max_shift:
                j, shift = j_next, median
                (m0, h0), (m1, h1) = pairs[0], pairs[-1]
                if m1.start - m0.start >= 0.3 and h1.start > h0.start:
                    ratio = (m1.start - m0.start) / (h1.start - h0.start)
                    tempo = min(max(ratio, rules.stretch[0]), rules.stretch[1])
            else:
                shift = 0.0
        elif not carry:
            shift = 0.0
        src = (max(0.0, phrase[0].start - rules.pad), phrase[-1].end + rules.pad)
        dst = max(0.0, src[0] + shift)
        if moves:
            dst = max(dst, moves[-1].dst_end + rules.gap)
        moves.append(Move(round(src[0], 3), round(src[1], 3), round(dst, 3), round(tempo, 3)))
    return moves


def warp(moves: list[Move], t: float) -> float:
    """Where a moment of the master lands after conforming.

    Inside a phrase it moves with the phrase; between phrases it slides
    linearly from one phrase's end to the next one's start. A sound placed on
    a word stays on that word.
    """
    if not moves:
        return round(t, 3)
    first = moves[0]
    if t <= first.src_start:
        # The opening silence stretches or shrinks; the film still starts at 0.
        return round(t * first.dst_start / first.src_start, 3) if first.src_start > 0 else round(t, 3)
    for i, m in enumerate(moves):
        if t <= m.src_end:
            return round(m.dst_start + (t - m.src_start) / m.tempo, 3)
        nxt = moves[i + 1] if i + 1 < len(moves) else None
        if nxt and t < nxt.src_start:
            frac = (t - m.src_end) / (nxt.src_start - m.src_end)
            return round(m.dst_end + frac * (nxt.dst_start - m.dst_end), 3)
    last = moves[-1]
    return round(t + last.dst_end - last.src_end, 3)
