#!/usr/bin/env python3
"""Lint the AFTER samples inside examples/before-after.md files.

Why this exists as a separate check: calibration samples live inside fenced code
blocks, and `writer/scripts/lint.py` masks fenced blocks by default. So the one
thing a model copies verbatim — the "После" sample — is exactly the thing the
linter never sees. This closes that hole.

BEFORE samples are supposed to violate the rules; only AFTER samples are checked.

Scope is deliberately narrow. Only three hard bans apply:
    EM_DASH_RU, NEG_PARALLEL, CHOPPED_DRAMA
MATH_SIGN_PROSE is excluded because inside samples the signs are usually
legitimate: RFC specs (`p95 <= 5 s`), UI paths (Настройки -> Тема), tool report
output. Flagging those would train people to ignore the check.

Per-file opt-out via an HTML comment anywhere in the file:
    <!-- after-samples: fiction -->  em-dash allowed (dialogue dashes, lyrics)
    <!-- after-samples: none -->     skip entirely (tool output, not prose)

Usage:
    python3 scripts/check-after-samples.py            # all skills
    python3 scripts/check-after-samples.py writer     # one skill

Exit: 0 clean, 1 violations found.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "writer" / "scripts"))
import lint as L  # noqa: E402

CHECKED = {"EM_DASH_RU", "NEG_PARALLEL", "CHOPPED_DRAMA"}
MODE = re.compile(r"<!--\s*after-samples:\s*(fiction|none)\s*-->", re.I)
AFTER_HEADING = re.compile(r"(после|after|надо|правильно)", re.I)
BEFORE_HEADING = re.compile(r"(\bдо\b|before|было|плохо|халтура|неправильно)", re.I)
# Inside a mixed BEFORE:/AFTER:/WHY: block, the line prefix wins over the heading.
LINE_ROLE = re.compile(r"^\s*(BEFORE|БЫЛО|ПЛОХО|WHY|ПОЧЕМУ)\s*:", re.I)


def after_sample_lines(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    mode = None
    in_fence = False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("#") or s.startswith("**"):
            if AFTER_HEADING.search(s):
                mode = "after"
            elif BEFORE_HEADING.search(s):
                mode = "before"
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence and mode == "after" and not LINE_ROLE.match(line):
            out.append((i, line))
    return out


def check(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    m = MODE.search(text)
    declared = m.group(1).lower() if m else "prose"
    if declared == "none":
        return []
    problems: list[str] = []
    for lineno, line in after_sample_lines(text):
        if not L.CYRILLIC.search(line):
            continue
        probe = L.MD_MARKER.sub("  ", line)
        for cat, rx, _ru_only in L.HARD_BANS_COMPILED:
            if cat not in CHECKED:
                continue
            if declared == "fiction" and cat == "EM_DASH_RU":
                continue
            if rx.search(probe):
                problems.append(f"  {path}:{lineno}  [{cat}]  {line.strip()[:88]}")
                break
    return problems


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    pattern = f"{sys.argv[1]}/examples/before-after.md" if len(sys.argv) > 1 else "*/examples/before-after.md"
    files = sorted(root.glob(pattern))
    if not files:
        print(f"no example files matched {pattern}")
        return 0
    all_problems: list[str] = []
    for f in files:
        all_problems.extend(check(f.relative_to(root)))
    if all_problems:
        print("after-samples: FAILED — hard bans inside AFTER calibration samples")
        print("(a model copies these verbatim, punctuation included)\n")
        print("\n".join(all_problems))
        print(
            "\nFix the sample, or declare the file's kind with an HTML comment:\n"
            "  <!-- after-samples: fiction -->   dialogue dashes / lyrics\n"
            "  <!-- after-samples: none -->      tool output, not prose"
        )
        return 1
    print(f"after-samples: OK ({len(files)} file(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
