"""Lint core — the hit types, the text helpers, and the document-level detectors.

Split out of lint.py, which had grown past the module-size gate. These six look
at the text as a whole: how its sentence lengths vary, whether softeners pile up,
whether verbs repeat across adjacent sentences, whether formatting is standing in
for content, and whether a heading is immediately restated.

Most structural hits carry line=0 — they describe the document, not one
location. Everything here sits below lint.py so the detectors can share the
Hit type and the sentence helpers without importing the scanner back.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from lint_patterns import (
    BOLD_SPAN,
    COLON_REVEAL,
    HEADING,
    INLINE_CODE,
    NON_PROSE_LINE,
    SOFTENERS_EN,
    SOFTENERS_RU,
    SEVERITY,
    URL,
    VERB_SUFFIX,
)

@dataclass
class Hit:
    line: int
    col: int
    category: str
    match: str
    severity: str = "caution"

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "col": self.col,
            "category": self.category,
            "severity": self.severity,
            "match": self.match,
        }


@dataclass
class Report:
    hits: list[Hit] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.hits)

    @property
    def by_category(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for h in self.hits:
            out[h.category] = out.get(h.category, 0) + 1
        return out

    @property
    def by_severity(self) -> dict[str, int]:
        out: dict[str, int] = {"blocker": 0, "caution": 0, "nit": 0}
        for h in self.hits:
            out[h.severity] = out.get(h.severity, 0) + 1
        return out

    @property
    def hard_bans(self) -> int:
        return sum(1 for h in self.hits if h.severity == "blocker")

    def gate(self) -> str:
        """Pass/fail on hard bans, orthogonal to the density verdict."""
        return "fail" if self.hard_bans else "pass"

    def verdict(self) -> tuple[int, str]:
        """Density of probabilistic slop signals. Independent of the gate.

        Blockers are excluded on purpose. They are pass/fail facts, not evidence
        of machine authorship, and counting them wrecked the verdict: a Russian
        document with forty-eight legitimate em-dashes read as "neuroslop
        suspected" while carrying a single actual slop marker. Density answers
        "does this read like a model wrote it"; the gate answers "does this break
        a house rule". Mixing them lets a typography choice masquerade as slop.
        """
        counted = [h for h in self.hits if h.severity == "caution"]
        non_nit_total = len(counted)
        cats: dict[str, int] = {}
        for h in counted:
            cats[h.category] = cats.get(h.category, 0) + 1
        max_per_cat = max(cats.values(), default=0)
        if non_nit_total >= 5 or max_per_cat >= 3:
            return 2, "neuroslop suspected"
        if non_nit_total >= 2:
            return 1, "borderline"
        return 0, "clean"


def _mask_code_blocks(text: str) -> str:
    """Replace lines inside fenced code blocks with empty strings.

    Why: linter scans line-by-line and would otherwise flag "revolutionary" or
    "click here" inside code examples and command output. Markdown fences open
    with ``` or ~~~ at line start (after optional indent); the same delimiter
    closes the block.
    """
    out: list[str] = []
    fence: str | None = None  # active fence marker, or None
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                out.append("")
                continue
            out.append(line)
        else:
            out.append("")
            if stripped.startswith(fence):
                fence = None
    return "\n".join(out)


def _strip_inline_code(text: str) -> str:
    """Blank out `inline code` spans, preserving line and column positions.

    Why: an artifact quoted in documentation (``the `turn0search0` marker``) is a
    citation, not a paste. Replacing with spaces keeps reported columns honest.
    """
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), text)


def _prose_sentences(lines: list[str]) -> list[str]:
    """Sentences from prose lines only — no headings, tables, lists, quotes."""
    prose = " ".join(l for l in lines if l.strip() and not NON_PROSE_LINE.match(l))
    prose = URL.sub(" ", prose)
    prose = re.sub(r"\*\*|«|»", "", prose)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]


def _verb_stems(sentence: str) -> set[str]:
    stems = set()
    for w in re.findall(r"[а-яё]{5,}", sentence.lower()):
        if VERB_SUFFIX.search(w):
            stems.add(VERB_SUFFIX.sub("", w)[:6])
    return {s for s in stems if len(s) >= 4}


def _content_stems(text: str) -> set[str]:
    """Crude prefix stems, so «производительность» matches «производительности».

    Six characters is enough to separate distinct roots without pulling in a
    morphology library; inflection lives past that boundary in both RU and EN.
    """
    return {w[:6] for w in re.findall(r"[^\W\d_]{4,}", text.lower())}


def _doc_hit(category: str, message: str, line: int = 0) -> Hit:
    """A hit that describes the text as a whole. line=0 means "no one location"."""
    return Hit(line=line, col=0, category=category,
               severity=SEVERITY.get(category, "caution"), match=message)


def _rhythm_hits(lengths: list[int]) -> list[Hit]:
    """Burstiness. Human prose varies sentence length sharply; an LLM holds a
    near-constant width. This is the one AI tell regex cannot see."""
    if len(lengths) < 8:
        return []
    hits: list[Hit] = []
    diffs = [abs(a - b) for a, b in zip(lengths, lengths[1:])]
    mean_diff = sum(diffs) / len(diffs)
    if mean_diff < 4:
        hits.append(_doc_hit(
            "RHYTHM_MONOTONE",
            f"adjacent sentence lengths differ by {mean_diff:.1f} words on "
            f"average (live prose: 6+)"))
    if len(lengths) >= 10 and not any(n <= 8 for n in lengths):
        hits.append(_doc_hit(
            "RHYTHM_NO_SHORT",
            f"no sentence under 9 words across {len(lengths)} sentences — "
            f"no pauses, no accents"))
    return hits


def _hedge_hits(sentences: list[str]) -> list[Hit]:
    """Three or more softeners inside a single sentence."""
    hits: list[Hit] = []
    for sentence in sentences:
        low = sentence.lower()
        n = sum(low.count(w) for w in SOFTENERS_RU) + sum(low.count(w) for w in SOFTENERS_EN)
        if n >= 3:
            hits.append(_doc_hit("HEDGE_CASCADE", f"{n} softeners in one sentence: {sentence[:60]}"))
    return hits


def _colon_reveal_hits(lines: list[str]) -> list[Hit]:
    """A drum roll before an ordinary statement. Write the payoff as a plain sentence."""
    return [
        Hit(line=line_idx, col=m.start() + 1, category="COLON_REVEAL",
            severity="caution", match=m.group(0)[:60])
        for line_idx, line in enumerate(lines, start=1)
        for m in COLON_REVEAL.finditer(line)
    ]


def _verb_echo_hits(sentences: list[str]) -> list[Hit]:
    """Verb echo across adjacent sentences (RU).

    The repetition penalty makes the model vary nouns (hence synonym cycling)
    while it *duplicates* verbs into parallel constructions — "X предлагает…
    Y предлагает…". A human reaches for a different verb without thinking.
    """
    hits: list[Hit] = []
    for a, b in zip(sentences, sentences[1:]):
        shared = _verb_stems(a) & _verb_stems(b)
        if shared:
            hits.append(_doc_hit(
                "VERB_ECHO",
                f"«{sorted(shared)[0]}…» repeats in adjacent sentences: {b[:50]}"))
    return hits


def _bold_density_hits(text: str, words_total: int) -> list[Hit]:
    """Roughly one bold span per 200 words. Above that, formatting is standing
    in for content."""
    bold = len(BOLD_SPAN.findall(text))
    if words_total < 200 or bold <= words_total / 200 + 1:
        return []
    return [_doc_hit(
        "BOLD_DENSITY",
        f"{bold} bold spans across {words_total} words "
        f"(budget ~{max(1, words_total // 200)})")]


def _echoes_heading(title_stems: set[str], line: str) -> bool:
    """Does this line restate the heading rather than add to it?

    The discriminator is *restates vs. adds*, not overlap. A section's opening
    sentence naturally reuses the section's topic word and is not an echo:
    "## Where the canon may live" / "Non-fiction projects split canon across two
    sources:" shares stems but introduces five new ones. An echo introduces
    almost nothing — counting shared stems alone flagged ordinary documentation.
    """
    body_stems = _content_stems(INLINE_CODE.sub(" ", line))
    if not body_stems:
        return False
    return bool(title_stems & body_stems) and len(body_stems - title_stems) <= 2


def _heading_echo_hits(lines: list[str]) -> list[Hit]:
    """The line after a heading restates it — a warm-up lap before the content.

    Only the literal-repeat variant is detectable here. The semantic variant
    («## Производительность» → «Скорость имеет значение.») shares no stems and
    stays LLM territory — see references/structural-prose.md.
    """
    hits: list[Hit] = []
    for idx, line in enumerate(lines):
        heading = HEADING.match(line)
        if not heading:
            continue
        # Backticked spans are identifiers, not prose. "In `Physical invariants`:"
        # under a "Physical invariant" heading is a cross-reference, not an echo.
        title_stems = _content_stems(INLINE_CODE.sub(" ", heading.group(1)))
        if not title_stems:
            continue
        for offset, nxt in enumerate(lines[idx + 1: idx + 4]):
            if not nxt.strip():
                continue
            # A real paragraph reusing the term is normal prose. The tell is a
            # short standalone line carrying nothing but the heading again.
            if NON_PROSE_LINE.match(nxt) or len(nxt.split()) > 12:
                break
            if _echoes_heading(title_stems, nxt):
                hits.append(_doc_hit(
                    "HEADING_ECHO",
                    f"line restates the heading «{heading.group(1)[:40]}»",
                    line=idx + offset + 2))
            break
    return hits


def _structural_hits(text: str, lines: list[str]) -> list[Hit]:
    """Document-level checks that regex-per-line cannot express."""
    sentences = _prose_sentences(lines)
    lengths = [len(s.split()) for s in sentences]

    return (
        _rhythm_hits(lengths)
        + _hedge_hits(sentences)
        + _colon_reveal_hits(lines)
        + _verb_echo_hits(sentences)
        + _bold_density_hits(text, sum(lengths))
        + _heading_echo_hits(lines)
    )

