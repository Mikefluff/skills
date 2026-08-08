#!/usr/bin/env python3
"""
writer-lint — offline regex linter for the writer skill.

Catches a high-recall subset of the neuroslop categories defined in
writer/SKILL.md, plus two things regex alone cannot see: chatbot copy-paste
artifacts (class A — a single hit is proof) and structural rhythm metrics
(uniform sentence length, bold density, verb echo across adjacent sentences).
Does NOT replace the full 4-layer cleaning pass — it is meant as a fast
pre-check ("does this draft already look like LLM output?") before asking
Claude to apply writer in clean/apply mode.

Two orthogonal outputs:
  * verdict  — how dense the slop is (clean / borderline / neuroslop suspected)
  * gate     — whether any HARD BAN fired (em-dash in RU prose, math signs in
               prose, negative parallelism, chopped drama, copy-paste artifact)

A text can be "clean" by density and still fail the gate on one pasted
`turn0search3`. That is the point: density is a judgement call, the gate is not.

Usage:
    python3 lint.py path/to/text.md
    python3 lint.py path/to/text.md --json
    cat text.md | python3 lint.py -

Exit codes:
    0 — clean (0-1 hits)
    1 — borderline (2-4 hits)
    2 — neuroslop suspected (5+ hits OR any category 3+ times)
    3 — hard ban present (gate failed; overrides the density verdict)

Class A artifact regexes are ported from smixs/humanizer-ru (MIT), which in
turn credits Vladimir-Human/humanizer-ru and petergyang/no-ai-slop (both MIT).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Iterable

# Each pattern is (category, regex, optional human label).
# Regex is matched case-insensitively unless inline (?-i) is used.
from lint_patterns import *  # noqa: F401,F403 — catalogues live next door
from lint_core import Hit, Report, _mask_code_blocks, _strip_inline_code, _structural_hits





def _artifact_hits(text: str) -> list[Hit]:
    """Pass 1 — class A copy-paste artifacts and invisible characters.

    Run against the raw (code-masked) text so URLs survive; backticked spans are
    blanked so that quoting an artifact is not itself a hit.
    """
    hits: list[Hit] = []
    source = _strip_inline_code(_mask_code_blocks(text)).splitlines()
    for line_idx, line in enumerate(source, start=1):
        for label, regex in ARTIFACTS_COMPILED:
            hits += [
                Hit(line=line_idx, col=m.start() + 1, category="COPYPASTE_ARTIFACT",
                    severity="blocker", match=f"{label}: {m.group(0)[:60]}")
                for m in regex.finditer(line)
            ]
        hits += [
            Hit(line=line_idx, col=m.start() + 1, category="ZERO_WIDTH",
                severity="caution",
                match="invisible character (CMSs and newsletters inject these "
                      "too — check the source)")
            for m in ZERO_WIDTH.finditer(line)
        ]
    return hits


def _line_hits(line_idx: int, line: str, fiction: bool) -> list[Hit]:
    """Pass 2 — hard bans and the phrase catalogue, for one line."""
    hits: list[Hit] = []
    # Markdown markers are blanked before the language probe so a quoted or
    # bulleted line is judged on its prose, not its punctuation.
    probe = MD_MARKER.sub("  ", line)
    is_ru = bool(CYRILLIC.search(probe))

    for cat, regex, ru_only in HARD_BANS_COMPILED:
        if ru_only and not is_ru:
            continue
        severity = "nit" if (fiction and cat == "EM_DASH_RU") else "blocker"
        hits += [
            Hit(line=line_idx, col=m.start() + 1, category=cat,
                severity=severity, match=m.group(0)[:80])
            for m in regex.finditer(probe)
        ]

    for cat, regex in COMPILED:
        hits += [
            Hit(line=line_idx, col=m.start() + 1, category=cat,
                severity=SEVERITY.get(cat, "caution"), match=m.group(0)[:80])
            for m in regex.finditer(line)
        ]
    return hits


def scan(text: str, skip_code_blocks: bool = True, fiction: bool = False) -> Report:
    """Scan text. `fiction` demotes the em-dash ban from blocker to nit.

    Why the exception: references/typography.md bans the em-dash in Russian prose
    and viral posts, but explicitly leaves it alone in book typesetting. In
    fiction the em-dash also opens dialogue lines, so a blanket blocker would
    flag every line of speech.
    """
    report = Report()
    scanned = _mask_code_blocks(text) if skip_code_blocks else text
    lines = scanned.splitlines()

    report.hits.extend(_artifact_hits(text))
    for line_idx, line in enumerate(lines, start=1):
        report.hits.extend(_line_hits(line_idx, line, fiction))
    report.hits.extend(_structural_hits(scanned, lines))

    report.hits.sort(key=lambda h: (h.line, h.col, h.category))
    return report


def format_human(report: Report) -> str:
    if not report.hits:
        return "writer-lint: clean (0 hits), gate passed\n"
    out: list[str] = []
    code, label = report.verdict()
    out.append(f"writer-lint: {label} ({report.total} hits)")
    if report.hard_bans:
        out.append(
            f"GATE FAILED — {report.hard_bans} hard ban(s). Fix these first, "
            f"then re-run; the density verdict is secondary."
        )
    else:
        out.append("gate passed: no hard bans.")
    out.append("")
    out.append("By category:")
    for cat, n in sorted(report.by_category.items(), key=lambda kv: -kv[1]):
        out.append(f"  {cat:<22} {n}")
    out.append("")
    out.append("Hits:")
    for h in report.hits[:200]:
        out.append(f"  L{h.line}:{h.col}  [{h.severity:<7}] {h.category:<22}  {h.match!r}")
    if len(report.hits) > 200:
        out.append(f"  ... and {len(report.hits) - 200} more")
    return "\n".join(out) + "\n"


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _report_json(report: Report, label: str) -> str:
    return json.dumps(
        {
            "verdict": label,
            "gate": report.gate(),
            "total": report.total,
            "hard_bans": report.hard_bans,
            "by_category": report.by_category,
            "by_severity": report.by_severity,
            "hits": [h.to_dict() for h in report.hits],
        },
        ensure_ascii=False,
        indent=2,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline regex linter for the writer skill.")
    parser.add_argument("path", help="Path to text file, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--scan-code-blocks",
        action="store_true",
        help="Also scan inside fenced code blocks (default: skipped).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only emit when verdict is not clean.",
    )
    parser.add_argument(
        "--aeo",
        action="store_true",
        help=("Answer-engine extractability check instead of the prose scan. "
              "A separate axis: a clean text can still be unquotable."),
    )
    parser.add_argument(
        "--fiction",
        action="store_true",
        help=("Fiction / book-typesetting mode: demote the RU em-dash ban to an "
              "advisory nit (dialogue dashes are legitimate there)."),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    text = read_input(args.path)

    # Extractability is orthogonal to slop density — deliberately a separate
    # report with its own exit codes rather than extra hits on the prose one.
    if args.aeo:
        import lint_aeo

        report = lint_aeo.scan(text)
        if args.json:
            import json as _json

            code, label = report.verdict()
            print(_json.dumps(
                {"verdict": label, "code": code, "stats": report.stats,
                 "findings": [f.to_dict() for f in report.findings]},
                ensure_ascii=False, indent=2,
            ))
        else:
            sys.stdout.write(lint_aeo.format_human(report))
        return report.verdict()[0]

    report = scan(text, skip_code_blocks=not args.scan_code_blocks, fiction=args.fiction)
    code, label = report.verdict()

    if args.json:
        print(_report_json(report, label))
    # --quiet means quiet: emit only when the density verdict is not clean.
    # Hard bans still set exit code 3 and still print on a normal run — but a
    # batch caller (the pre-commit hook) asked for silence and gets it, and
    # decides for itself what to do with the exit code. Printing the full report
    # for every hard ban buried each commit under hundreds of lines, because the
    # repo's own Russian documentation uses em-dashes throughout.
    elif not (args.quiet and code == 0):
        sys.stdout.write(format_human(report))

    # A hard ban outranks the density verdict: a text can be sparse in slop and
    # still carry one pasted `turn0search3`.
    return 3 if report.hard_bans else code


if __name__ == "__main__":
    sys.exit(main())
