"""AEO core — the thresholds, the pattern catalogue, and the block parser.

Split out of lint_aeo.py, which had grown past the module-size gate when the
evidence rules landed. This half is what a rule needs before it can look at
anything: the numbers a rule compares against, the regexes it matches with, and
the parse that turns a markdown file into the blocks an answer engine would
chunk it into.

The rules themselves stay in lint_aeo.py, above this, so they can share Finding
and the parser without importing the scanner back.
"""


from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field

# The first 40-60 words after the title are the primary extraction window. The
# band below is deliberately wider at the top: a 75-word answer still fits a
# chunk, while anything past that has stopped being an answer and become a
# preamble.
ANSWER_MIN_WORDS = 40
ANSWER_MAX_WORDS = 75

# One self-contained argument, measured between headings.
SECTION_MIN_WORDS = 100
SECTION_MAX_WORDS = 200

# An atomic paragraph is one idea. Past this it stops being one chunk.
PARAGRAPH_MAX_WORDS = 90

# Below this share of question-form headings the page reads as a document
# rather than as a set of answers.
QUESTION_HEADING_RATIO = 0.4

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_CODE_FENCE = re.compile(r"^\s*```")

# Interrogative openers, EN + RU. A heading ending in "?" counts regardless.
_QUESTION_WORDS = {
    "what", "how", "why", "when", "where", "which", "who", "can", "should",
    "is", "are", "does", "do", "will", "would",
    "что", "как", "почему", "зачем", "когда", "где", "какой", "какая", "какие",
    "кто", "нужно", "стоит", "можно", "чем",
}

# Openers that announce an article instead of answering. If the first paragraph
# starts like this, the extraction window is spent on throat-clearing.
_PREAMBLE = re.compile(
    r"^\s*(in this (article|post|guide)|this (article|post|guide)|let'?s |we'?ll |"
    r"have you ever|imagine |picture this|в этой (статье|заметке)|"
    r"сегодня (мы|я)|давайте |представьте |поговорим )",
    re.IGNORECASE,
)

# Words that signal the page answers a comparison query.
_COMPARISON = re.compile(
    r"\b(vs\.?|versus|compared? to|alternatives?|better than|which one|"
    r"против|сравнение|вместо|альтернатив|лучше чем|что выбрать)\b",
    re.IGNORECASE,
)

# A link out, an inline citation, or a named source. Engines quote pages that
# show their working; the 2026 measurements put citing sources at the top of the
# lift table, alongside statistics and quotations.
_SOURCE = re.compile(
    r"\]\(https?://|<https?://|\bhttps?://|\baccording to\b|\bпо данным\b|"
    r"\bисточник\b|\breports?\b\s+that\b",
    re.IGNORECASE,
)

# A figure with a unit, a percentage, a year, or a money amount. Bare small
# integers do not count — "three reasons" is not a statistic.
_STATISTIC = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:%|percent|процент)|"
    r"[$€£₽]\s*\d|\d+(?:[.,]\d+)?\s*(?:x|×)\b|"
    r"\b(?:19|20)\d{2}\b|\b\d{1,3}(?:[ ,]\d{3})+\b",
    re.IGNORECASE,
)

# A quoted sentence, or a markdown blockquote. Short quoted words are phrases,
# not quotations, so a minimum length applies.
_QUOTATION = re.compile(r"^>\s+\S|[«\"“][^»\"”]{25,}[»\"”]", re.MULTILINE)

# Below this the page is asserting rather than evidencing.
EVIDENCE_MIN_KINDS = 2

# A section long enough to be chunked on its own needs its own opening answer.
SECTION_ANSWER_THRESHOLD_WORDS = 120
SECTION_ANSWER_MAX_WORDS = 75


@dataclass
class Finding:
    line: int
    rule: str
    severity: str  # "block" | "warn" | "nit"
    message: str

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass
class AeoReport:
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def blocks(self) -> int:
        return sum(1 for f in self.findings if f.severity == "block")

    @property
    def warns(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warn")

    def verdict(self) -> tuple[int, str]:
        """0 extractable · 1 weak · 2 poor. Independent of the slop verdict."""
        if self.blocks:
            return 2, "poor extractability"
        if self.warns >= 3:
            return 2, "poor extractability"
        if self.warns:
            return 1, "weak extractability"
        return 0, "extractable"


def _words(text: str) -> list[str]:
    return re.findall(r"[\w'’-]+", text, re.UNICODE)


def _is_question(heading: str) -> bool:
    stripped = heading.strip().rstrip(":")
    if stripped.endswith("?"):
        return True
    first = _words(stripped.lower())
    return bool(first) and first[0] in _QUESTION_WORDS


@dataclass
class _Block:
    """A parsed markdown block: heading, paragraph, table row or fence."""

    kind: str
    line: int
    text: str
    level: int = 0


def _parse(lines: list[str]) -> list[_Block]:
    blocks: list[_Block] = []
    in_fence = False
    buffer: list[str] = []
    buffer_start = 0

    def flush() -> None:
        nonlocal buffer, buffer_start
        joined = " ".join(buffer).strip()
        if joined:
            blocks.append(_Block("paragraph", buffer_start, joined))
        buffer = []

    for number, raw in enumerate(lines, 1):
        if _CODE_FENCE.match(raw):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = _HEADING.match(raw)
        if heading:
            flush()
            blocks.append(
                _Block("heading", number, heading.group(2).strip(), len(heading.group(1)))
            )
            continue

        if _TABLE_ROW.match(raw):
            flush()
            blocks.append(_Block("table", number, raw.strip()))
            continue

        if not raw.strip():
            flush()
            continue

        if not buffer:
            buffer_start = number
        buffer.append(raw.strip())

    flush()
    return blocks


def _opening_block(blocks: list[_Block]) -> _Block | None:
    """The first paragraph before any H2 — the extraction window."""
    for block in blocks:
        if block.kind == "heading" and block.level >= 2:
            return None
        if block.kind == "paragraph":
            return block
    return None


