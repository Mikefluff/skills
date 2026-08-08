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
  - a direct answer at the top of every section long enough to be chunked alone
  - evidence the page can be cited for: sources, figures, quotations

The published research that motivates this held the words constant and changed
only structure, across six engines. The 2026 follow-up measured the evidence
signals separately: citing sources +40% visibility, statistics +41%, quotations
+28%. No network calls, no model, same shape as the prose linter next door.

Thresholds, patterns and the parser live in lint_aeo_core.py.
"""


from lint_aeo_core import (
    ANSWER_MAX_WORDS,
    ANSWER_MIN_WORDS,
    EVIDENCE_MIN_KINDS,
    PARAGRAPH_MAX_WORDS,
    QUESTION_HEADING_RATIO,
    SECTION_ANSWER_MAX_WORDS,
    SECTION_ANSWER_THRESHOLD_WORDS,
    SECTION_MAX_WORDS,
    SECTION_MIN_WORDS,
    AeoReport,
    Finding,
    _Block,
    _COMPARISON,
    _PREAMBLE,
    _QUOTATION,
    _SOURCE,
    _STATISTIC,
    _is_question,
    _opening_block,
    _parse,
    _words,
)


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


def _evidence_kinds(text: str) -> list[str]:
    """Which of the three lift-carrying signals the page actually shows."""
    kinds = []
    if _SOURCE.search(text):
        kinds.append("sources")
    if _STATISTIC.search(text):
        kinds.append("statistics")
    if _QUOTATION.search(text):
        kinds.append("quotations")
    return kinds


def _check_evidence(text: str) -> list[Finding]:
    """Citing sources, quoting figures and quoting people are what get quoted.

    Measured separately across engines in 2026: citing sources +40% visibility,
    adding statistics +41%, adding quotations +28%. They compound, and a page
    showing none of the three is asking to be believed rather than cited.
    """
    kinds = _evidence_kinds(text)
    if len(kinds) >= EVIDENCE_MIN_KINDS:
        return []
    missing = [k for k in ("sources", "statistics", "quotations") if k not in kinds]
    return [
        Finding(
            1,
            "evidence",
            "warn",
            f"page shows {len(kinds)} of 3 evidence signals "
            f"({', '.join(kinds) or 'none'}); missing {', '.join(missing)} — "
            f"engines cite pages that show their working",
        )
    ]


def _check_section_answers(blocks: list[_Block]) -> list[Finding]:
    """Every section long enough to be chunked alone needs its own opening answer.

    The page-level answer only wins the query the title matches. A long section
    is retrieved on its own terms, and if it opens with setup rather than a
    claim, the passage that gets scored has nothing quotable at the top.
    """
    out: list[Finding] = []
    current: _Block | None = None
    first_paragraph: _Block | None = None
    words = 0

    def close() -> None:
        if current is None or words < SECTION_ANSWER_THRESHOLD_WORDS:
            return
        if first_paragraph is None:
            out.append(
                Finding(
                    current.line,
                    "section-answer",
                    "warn",
                    f"section '{current.text[:40]}' runs {words} words with no opening "
                    f"paragraph — the chunk starts on a list or a table",
                )
            )
            return
        opening = len(_words(first_paragraph.text))
        if opening > SECTION_ANSWER_MAX_WORDS or _PREAMBLE.match(first_paragraph.text):
            out.append(
                Finding(
                    first_paragraph.line,
                    "section-answer",
                    "warn",
                    f"section '{current.text[:40]}' opens with {opening} words of setup; "
                    f"a chunked section is scored on its own first sentences",
                )
            )

    for block in blocks:
        if block.kind == "heading" and block.level >= 2:
            close()
            current, first_paragraph, words = block, None, 0
            continue
        if current is None:
            continue
        words += len(_words(block.text))
        if first_paragraph is None and block.kind == "paragraph":
            first_paragraph = block
    close()
    return out


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
    findings += _check_evidence(text)
    findings += _check_section_answers(blocks)

    headings = [b for b in blocks if b.kind == "heading" and b.level >= 2]
    report = AeoReport(findings=findings)
    report.stats = {
        "words": len(_words(text)),
        "sections": len(headings),
        "question_headings": sum(1 for h in headings if _is_question(h.text)),
        "has_table": any(b.kind == "table" for b in blocks),
        "evidence": _evidence_kinds(text),
    }
    return report


def format_human(report: AeoReport) -> str:
    code, label = report.verdict()
    stats = report.stats
    out = [
        f"writer-aeo: {label} ({report.blocks} block, {report.warns} warn)",
        f"  {stats.get('words', 0)} words · {stats.get('sections', 0)} sections · "
        f"{stats.get('question_headings', 0)} question headings · "
        f"table: {'yes' if stats.get('has_table') else 'no'} · "
        f"evidence: {', '.join(stats.get('evidence') or []) or 'none'}",
    ]
    if report.findings:
        out.append("")
        for f in sorted(report.findings, key=lambda x: (x.severity != "block", x.line)):
            mark = {"block": "BLOCK", "warn": "warn ", "nit": "nit  "}[f.severity]
            out.append(f"  L{f.line:<4} [{mark}] {f.rule}: {f.message}")
    out.append("")
    return "\n".join(out)
