"""What stays of a talking-head clip, and where each word lands afterwards.

Three decisions, all made from the transcript's word timings and the silences
ffmpeg hears, none of them from a frame:

  * the opener is trimmed inside a pause, never inside a word;
  * a pause longer than a breath is shortened, not removed — a jump cut with no
    air at all reads as a mistake;
  * every later time (a caption, a graphic, a cutaway) is given on the original
    clock and moved by `Timeline.at`.

Also here: finding the takes that say the same thing, and the line said twice
inside one take. Both are text comparisons and need no picture either.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .recut_plan import FPS

Span = tuple[float, float]

# A pause is tightened only when longer than this, and this much air is kept on
# each side of the cut so the speaker still breathes.
LONG_PAUSE = 0.72
AIR_BEFORE, AIR_AFTER = 0.26, 0.2

MAX_WORDS, MAX_CHARS, GROUP_GAP = 3, 19, 0.34
# Short words that close a thought and must not be carried to the next caption.
CLOSERS = frozenset({"нет", "да", "no", "yes", "não", "sim", "br"})

_SILENCE_START = re.compile(r"silence_start: ([\d.]+)")
_SILENCE_END = re.compile(r"silence_end: ([\d.]+)")
_DASHES = re.compile(r"[—–\-]+")
_TOKEN = re.compile(r"[\w$%]+", re.UNICODE)


def parse_silences(ffmpeg_stderr: str) -> list[Span]:
    """The (start, end) pairs out of a `silencedetect` run."""
    starts = [float(x) for x in _SILENCE_START.findall(ffmpeg_stderr)]
    ends = [float(x) for x in _SILENCE_END.findall(ffmpeg_stderr)]
    return list(zip(starts, ends))


@dataclass(frozen=True)
class Timeline:
    keep: tuple[Span, ...]
    removed: tuple[Span, ...]
    fps: int = FPS

    @property
    def total(self) -> float:
        return _frame(sum(b - a for a, b in self.keep), self.fps)

    @property
    def cuts(self) -> list[float]:
        """Where the kept pieces join, on the new clock."""
        points, clock = [], 0.0
        for a, b in self.keep[:-1]:
            clock += b - a
            points.append(_frame(clock, self.fps))
        return points

    def at(self, t: float) -> float:
        """A second on the original clip, on the new clock."""
        clock = 0.0
        for a, b in self.keep:
            if t < a:
                return clock
            if t <= b:
                return clock + (t - a)
            clock += b - a
        return clock

    def kept(self, t: float) -> bool:
        return any(a - 1e-6 <= t <= b + 1e-6 for a, b in self.keep)


def _frame(t: float, fps: int) -> float:
    return round(t * fps) / fps


def _snap_start(start: float, silences: list[Span]) -> float:
    """Move an opener trim into the pause it sits next to."""
    for s, e in silences:
        if s - 0.1 <= start <= e + 0.35:
            start = max(s, e - 0.14)
    return max(0.0, start - 0.03) if start else 0.0


def _snap_end(duration: float, speech_end: float, silences: list[Span]) -> float:
    """End half a second after the last word, sooner when silence starts there."""
    end = min(duration, speech_end + 0.5)
    for s, _ in silences:
        if s >= speech_end - 0.25:
            return min(duration, max(s + 0.4, speech_end + 0.3))
    return end


def _merge(removed: list[Span], fps: int) -> list[Span]:
    merged: list[Span] = []
    for a, b in sorted(removed):
        a, b = _frame(a, fps), _frame(b, fps)
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def _pause_trims(silences: list[Span], window: Span, removed: list[Span]) -> list[Span]:
    start, end = window
    trims = []
    for s, e in silences:
        inside = s > start and e < end and e - s > LONG_PAUSE
        if inside and not any(a <= s and e <= b for a, b in removed):
            trims.append((s + AIR_BEFORE, e - AIR_AFTER))
    return trims


def plan_timeline(duration: float, speech_end: float, silences: list[Span],
                  start: float = 0.0, cuts: tuple = ()) -> Timeline:
    """Trim the opener, drop the named cuts, tighten long pauses, end after the last word."""
    start = _snap_start(start, silences)
    end = _snap_end(duration, speech_end, silences)
    removed: list[Span] = [(0.0, start)] if start > 0 else []
    removed += [(float(a), float(b)) for a, b in cuts]
    removed += _pause_trims(silences, (start, end), removed)
    removed.append((end, duration + 9))
    merged = _merge(removed, FPS)
    keep, clock = [], 0.0
    for a, b in merged:
        if a > clock:
            keep.append((clock, a))
        clock = b
    return Timeline(tuple(keep), tuple(merged), FPS)


def _fixed(word: dict, fixes: list) -> str:
    text = word["word"].strip()
    for at, replacement in fixes:
        if abs(word["start"] - at) < 0.11:
            text = replacement
    return text.strip("«»\"")


def remap_words(words: list[dict], timeline: Timeline, fixes: tuple = ()) -> list[dict]:
    """Whisper's words on the new clock: cut ones dropped, misheard ones replaced.

    A fix is `[second, "text"]`; an empty text drops the word.
    """
    out = []
    for word in words:
        middle = (word["start"] + word["end"]) / 2
        if not timeline.kept(middle) and not timeline.kept(word["start"]):
            continue
        text = _fixed(word, list(fixes))
        if not text or _DASHES.fullmatch(text):
            continue
        end = max(word["end"], word["start"] + 0.08)
        out.append({"t": timeline.at(word["start"]), "e": timeline.at(end), "text": text})
    return out


def _carry(group: list[dict], gap: float) -> list[dict]:
    """A short word left hanging at the end of a caption opens the next one instead."""
    last = group[-1]["text"]
    if gap <= GROUP_GAP and len(group) > 1 and len(last) <= 3 and last.lower() not in CLOSERS:
        return [group.pop()]
    return []


def _split(words: list[dict]) -> list[list[dict]]:
    groups, current = [], []
    for word in words:
        gap = word["t"] - current[-1]["e"] if current else 0.0
        chars = sum(len(x["text"]) for x in current) + len(current)
        full = len(current) >= MAX_WORDS or chars + len(word["text"]) > MAX_CHARS
        if current and (gap > GROUP_GAP or full):
            carried = _carry(current, gap)
            groups.append(current)
            current = carried
        current.append(word)
    if current:
        groups.append(current)
    return groups


def _no_orphans(groups: list[list[dict]]) -> list[list[dict]]:
    """A one- or two-letter word never gets a caption to itself."""
    kept = []
    for i, group in enumerate(groups):
        alone = len(group) == 1 and len(group[0]["text"]) <= 2
        if kept and alone and i + 1 < len(groups):
            groups[i + 1].insert(0, group[0])
            continue
        kept.append(group)
    return [g for g in kept if g]


def caption_groups(words: list[dict]) -> list[dict]:
    """Words into captions of up to three, each on screen until the next starts."""
    groups = _no_orphans(_split(words))
    out = []
    for i, group in enumerate(groups):
        t0 = max(0.0, group[0]["t"] - 0.04)
        following = groups[i + 1][0]["t"] - 0.04 if i + 1 < len(groups) else group[-1]["e"] + 0.5
        out.append({"t0": t0, "t1": min(following, group[-1]["e"] + 0.55), "words": group})
    return out


# ───────────────────────── duplicate takes and repeated lines ─────────────────────────


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


def _shingles(tokens: list[str], size: int = 3) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + size]) for i in range(max(0, len(tokens) - size + 1))}


def overlap(a: str, b: str) -> float:
    """How much of the shorter text is inside the longer one, 0..1."""
    sa, sb = _shingles(_tokens(a)), _shingles(_tokens(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / min(len(sa), len(sb))


def duplicate_takes(texts: dict[str, str], threshold: float = 0.6) -> list[list[str]]:
    """Groups of clips that say the same thing, longest text first in each group.

    A take that is a fragment of another counts: the comparison is against the
    shorter text, so a clip cut off mid-sentence still finds its full version.
    """
    names = sorted(texts)
    group_of = {name: name for name in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if overlap(texts[a], texts[b]) >= threshold:
                old, new = group_of[b], group_of[a]
                for name in names:
                    if group_of[name] == old:
                        group_of[name] = new
    groups: dict[str, list[str]] = {}
    for name in names:
        groups.setdefault(group_of[name], []).append(name)
    return [sorted(g, key=lambda n: -len(texts[n])) for g in groups.values() if len(g) > 1]


def repeated_lines(words: list[dict], size: int = 3, within: float = 6.0) -> list[tuple[float, float, str]]:
    """A phrase said twice within a few seconds: (first start, second start, phrase).

    The usual cause is a restart the camera kept. Cut from the first start to
    the second and the line is said once. A phrase that returns later in the
    take is the speaker's own emphasis, not a restart, and is left alone.
    """
    tokens = [(_tokens(w["word"]) or [""])[0] for w in words]
    seen: dict[tuple[str, ...], int] = {}
    found, skip_until = [], -1
    for i in range(len(tokens) - size + 1):
        gram = tuple(tokens[i:i + size])
        if "" in gram or i <= skip_until:
            continue
        first = seen.get(gram, i)
        seen[gram] = i
        if first != i and i - first >= size and words[i]["start"] - words[first]["start"] <= within:
            found.append((words[first]["start"], words[i]["start"], " ".join(gram)))
            skip_until = i + size
    return found
