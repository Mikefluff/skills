#!/usr/bin/env python3
"""
lint-description.py — score the SKILL.md frontmatter `description:` field of a
single skill folder against discovery-quality heuristics.

The `description` field is what Claude Code uses to match a user's intent to a
skill. Bad descriptions = invisible skill. This linter flags common issues:

- too short (< 80 chars — can't disambiguate from siblings)
- too long  (> 350 chars — verbosity dilutes the matching signal)
- prefix smell  ("This skill…", "A skill that…", "Used to…")
- missing invocation hint (no "use when", "invoked by", "use before", etc.)
- internal-repo-path bleed (description mentions concrete user paths like
  "books/god-academy/" — those should live in the body, not the description)

Usage:
    python3 scripts/lint-description.py <skill-dir>
    python3 scripts/lint-description.py --json <skill-dir>

Exit codes: always 0 — this linter is advisory, not blocking.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# Heuristics
MIN_LEN = 80
SOFT_MIN = 120
SOFT_MAX = 300
MAX_LEN = 350

BAD_PREFIXES = (
    "this skill",
    "a skill that",
    "used to",
    "this is a skill",
    "the skill",
)

INVOKE_HINTS = (
    "use when",
    "use before",
    "use after",
    "invoked by",
    "invoke when",
    "triggers when",
    "trigger when",
    "use to",
    "use for",
    "when the user",
    "when a user",
    "перед ",
    "при ",
    "когда ",
    "use this skill",
)

INTERNAL_PATH_PATTERNS = (
    re.compile(r"\bbooks/god-academy/"),
    re.compile(r"\bbooks/era-arkhitektorov/"),
    re.compile(r"\bbooks/heavenly-code/"),
    re.compile(r"\bbooks/\*/{ru,en,pt-br}"),
)


def extract_description(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    in_fm = False
    desc_lines: list[str] = []
    capturing = False
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if not in_fm:
            continue
        if capturing:
            # Continuation of folded scalar (next-line continues description).
            if line.startswith(" ") or line.startswith("\t"):
                desc_lines.append(line.strip())
                continue
            else:
                break
        m = re.match(r'^description:\s*"?(.*?)"?\s*$', line)
        if m:
            desc_lines.append(m.group(1))
            capturing = True
    if not desc_lines:
        return None
    return " ".join(desc_lines).strip().strip('"')


def length_finding(n: int) -> dict | None:
    """At most one finding — the length bands are ordered, not independent."""
    if n < MIN_LEN:
        return {
            "level": "WARN",
            "code": "too_short",
            "msg": f"description is {n} chars (< {MIN_LEN}) — too short to disambiguate from sibling skills",
        }
    if n < SOFT_MIN:
        return {
            "level": "INFO",
            "code": "borderline_short",
            "msg": f"description is {n} chars — borderline; sweet spot is {SOFT_MIN}-{SOFT_MAX}",
        }
    if n > MAX_LEN:
        return {
            "level": "WARN",
            "code": "too_long",
            "msg": f"description is {n} chars (> {MAX_LEN}) — verbosity dilutes matching signal",
        }
    if n > SOFT_MAX:
        return {
            "level": "INFO",
            "code": "borderline_long",
            "msg": f"description is {n} chars — borderline; sweet spot is {SOFT_MIN}-{SOFT_MAX}",
        }
    return None


def style_findings(desc: str) -> list[dict]:
    """Opening phrase, invocation hint, internal-path bleed. One finding each."""
    findings: list[dict] = []
    low = desc.lower().lstrip()

    for bad in BAD_PREFIXES:
        if low.startswith(bad):
            findings.append({
                "level": "WARN",
                "code": "bad_prefix",
                "msg": f'starts with "{bad}…" — replace with imperative verb or noun phrase',
            })
            break

    if not any(hint in low for hint in INVOKE_HINTS):
        findings.append({
            "level": "INFO",
            "code": "no_invocation_hint",
            "msg": 'no invocation hint (no "use when" / "invoke when" / "use before" / etc.)',
        })

    for pat in INTERNAL_PATH_PATTERNS:
        if pat.search(desc):
            findings.append({
                "level": "WARN",
                "code": "internal_path_bleed",
                "msg": f'mentions internal path "{pat.pattern}" — move detail to body, keep description abstract',
            })
            break

    return findings


def lint(desc: str) -> list[dict]:
    findings: list[dict] = []
    length = length_finding(len(desc))
    if length is not None:
        findings.append(length)
    findings += style_findings(desc)
    return findings


def verdict_of(findings: Iterable[dict]) -> str:
    levels = {f["level"] for f in findings}
    if "WARN" in levels:
        return "WARN"
    if "INFO" in levels:
        return "INFO"
    return "PASS"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("skill_dir", help="path to skill directory (containing SKILL.md)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    sk = Path(args.skill_dir)
    md = sk / "SKILL.md"
    if not md.exists():
        print(f"  ⚠ description: SKILL.md not found at {md}", file=sys.stderr)
        return 0

    desc = extract_description(md)
    if desc is None:
        print(f"  ⚠ description: could not extract from frontmatter", file=sys.stderr)
        return 0

    findings = lint(desc)
    verdict = verdict_of(findings)

    if args.json:
        print(json.dumps({
            "skill": sk.name,
            "length": len(desc),
            "verdict": verdict,
            "findings": findings,
        }, ensure_ascii=False, indent=2))
        return 0

    # Human output — lines prefixed with two spaces, fits in validate.sh's per-skill block
    for f in findings:
        symbol = "⚠" if f["level"] == "WARN" else "·"
        print(f"  {symbol} description: {f['msg']}")

    # Final per-skill verdict line (so validate.sh can aggregate)
    print(f"  ⎯ description-verdict: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
