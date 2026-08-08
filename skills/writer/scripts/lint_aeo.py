"""AEO extractability rules — a third axis, deliberately kept off the slop verdict.

`lint.py` already answers two orthogonal questions: how dense the slop is
(verdict) and whether a house rule broke (gate). Extractability is a third, and
mixing it into either would repeat the mistake `Report.verdict()` documents —
one kind of finding drowning out another it has nothing to do with. A text can
read beautifully and still be invisible to an answer engine, and the reverse.

What these rules encode: answer engines do not read pages, they chunk them into
passages, score each passage on its own, and cite the strongest one. So the
things that decide citation are structural, and they are measurable offline:

  - a direct answer inside the first extraction window
  - headings phrased as the questions people actually ask
  - paragraphs small enough to survive chunking intact
  - sections sized to one self-contained argument
  - a comparison table when the page answers a comparison query

The published research that motivates this held the words constant and changed
only structure, across six engines. No network calls, no model, same shape as
the prose linter next door.
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


def _check_answer_first(blocks: list[_Block]) -> list[Finding]:
    first = _opening_block(blocks)
    if first is None:
        return [
            Finding(
                1,
                "answer-first",
                "block",
                "no paragraph before the first section heading — the extraction "
                "window is empty, so there is nothing for an engine to quote",
            )
        ]

    out: list[Finding] = []
    count = len(_words(first.text))
    if count < ANSWER_MIN_WORDS:
        out.append(
            Finding(
                first.line,
                "answer-first",
                "warn",
                f"opening answer is {count} words; under {ANSWER_MIN_WORDS} rarely "
                f"carries a complete claim an engine can lift",
            )
        )
    elif count > ANSWER_MAX_WORDS:
        out.append(
            Finding(
                first.line,
                "answer-first",
                "warn",
                f"opening answer is {count} words; past {ANSWER_MAX_WORDS} it stops "
                f"being an answer and reads as preamble",
            )
        )

    if _PREAMBLE.match(first.text):
        out.append(
            Finding(
                first.line,
                "answer-first",
                "warn",
                "opening announces the article instead of answering it — the window "
                "is spent before the claim arrives",
            )
        )
    return out


def _check_headings(blocks: list[_Block]) -> list[Finding]:
    headings = [b for b in blocks if b.kind == "heading" and b.level >= 2]
    if not headings:
        return [
            Finding(
                1,
                "headings",
                "warn",
                "no section headings — the page is one undifferentiated chunk",
            )
        ]

    questions = [h for h in headings if _is_question(h.text)]
    ratio = len(questions) / len(headings)
    if ratio < QUESTION_HEADING_RATIO:
        return [
            Finding(
                headings[0].line,
                "headings",
                "warn",
                f"{len(questions)} of {len(headings)} headings are question-form "
                f"({ratio:.0%}); engines match headings against queries, and queries "
                f"are questions",
            )
        ]
    return []


def _check_paragraphs(blocks: list[_Block]) -> list[Finding]:
    out: list[Finding] = []
    for block in blocks:
        if block.kind != "paragraph":
            continue
        count = len(_words(block.text))
        if count > PARAGRAPH_MAX_WORDS:
            out.append(
                Finding(
                    block.line,
                    "chunk-size",
                    "warn",
                    f"paragraph is {count} words; past {PARAGRAPH_MAX_WORDS} it splits "
                    f"across chunks and neither half stands alone",
                )
            )
    return out


def _check_sections(blocks: list[_Block]) -> list[Finding]:
    """Words between one heading and the next."""
    out: list[Finding] = []
    current: _Block | None = None
    count = 0

    def close() -> None:
        nonlocal count
        if current is None or count == 0:
            return
        if count > SECTION_MAX_WORDS:
            out.append(
                Finding(
                    current.line,
                    "section-size",
                    "nit",
                    f"section '{current.text[:40]}' is {count} words; over "
                    f"{SECTION_MAX_WORDS} it holds more than one liftable argument",
                )
            )
        count = 0

    for block in blocks:
        if block.kind == "heading" and block.level >= 2:
            close()
            current = block
            continue
        if block.kind == "paragraph":
            count += len(_words(block.text))
    close()
    return out


def _check_comparison_table(blocks: list[_Block], title: str) -> list[Finding]:
    headings = " ".join(b.text for b in blocks if b.kind == "heading")
    if not _COMPARISON.search(f"{title} {headings}"):
        return []
    if any(b.kind == "table" for b in blocks):
        return []
    return [
        Finding(
            1,
            "comparison-table",
            "warn",
            "reads as a comparison but has no table — comparison queries are "
            "answered from tables far more often than from prose",
        )
    ]


def scan(text: str) -> AeoReport:
    lines = text.splitlines()
    blocks = _parse(lines)

    title = ""
    for block in blocks:
        if block.kind == "heading" and block.level == 1:
            title = block.text
            break

    findings: list[Finding] = []
    findings += _check_answer_first(blocks)
    findings += _check_headings(blocks)
    findings += _check_paragraphs(blocks)
    findings += _check_sections(blocks)
    findings += _check_comparison_table(blocks, title)

    headings = [b for b in blocks if b.kind == "heading" and b.level >= 2]
    report = AeoReport(findings=findings)
    report.stats = {
        "words": len(_words(text)),
        "sections": len(headings),
        "question_headings": sum(1 for h in headings if _is_question(h.text)),
        "has_table": any(b.kind == "table" for b in blocks),
    }
    return report


def format_human(report: AeoReport) -> str:
    code, label = report.verdict()
    stats = report.stats
    out = [
        f"writer-aeo: {label} ({report.blocks} block, {report.warns} warn)",
        f"  {stats.get('words', 0)} words · {stats.get('sections', 0)} sections · "
        f"{stats.get('question_headings', 0)} question headings · "
        f"table: {'yes' if stats.get('has_table') else 'no'}",
    ]
    if report.findings:
        out.append("")
        for f in sorted(report.findings, key=lambda x: (x.severity != "block", x.line)):
            mark = {"block": "BLOCK", "warn": "warn ", "nit": "nit  "}[f.severity]
            out.append(f"  L{f.line:<4} [{mark}] {f.rule}: {f.message}")
    out.append("")
    return "\n".join(out)
