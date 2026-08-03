#!/usr/bin/env python3
"""Resolve every relative markdown link in the repo.

Why this is separate from validate.sh: that check greps for `references/<f>.md`
and resolves it inside the *current* skill. It therefore cannot see three whole
classes of link, and all three had rotted before this script existed:

  * cross-skill  — docs/walkthroughs/* pointing into ../../<skill>/references/
  * docs-to-docs — docs/README.md, INSTALL.md, USER-GUIDE.md
  * repo root    — .github/ templates, CONTRIBUTING, SECURITY

Placeholders are skipped, not reported: a link target containing <angle
brackets>, "..." or a bare {curly} slot is documentation-of-a-format, not a
link. Anchors (#section) are checked for file existence only, not for the
anchor itself.

Usage:
    python3 scripts/check-links.py           # whole repo
    python3 scripts/check-links.py docs      # limit to a subtree

Exit: 0 clean, 1 broken links found.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

LINK = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+?)\s*\)")
PLACEHOLDER = re.compile(r"[<>{}]|\.\.\.|^path$|^slug$")
SKIP_SCHEME = ("http://", "https://", "mailto:", "tel:", "#", "data:")

# Backticked paths pointing at a skill's own reference files. Markdown-link
# checking misses these entirely, and nine of them had rotted into walkthroughs
# — `microcopy/references/banned.md` when the file is `banned-words.md`, and so
# on. Scoped deliberately to `<skill>/references/<file>.md`: broad path matching
# also hits user-project examples (`your-book/ru/chapters/ch07.md`), runtime
# outputs (`plan.json`, `script.md`) and /tmp paths, none of which exist here.
BACKTICK_REF = re.compile(r"`([a-z0-9][a-z0-9-]*/references/[A-Za-z0-9_./-]+\.md)`")


def tracked_markdown(subtree: str | None) -> list[pathlib.Path]:
    args = ["git", "ls-files", "*.md"]
    if subtree:
        args = ["git", "ls-files", f"{subtree}/**/*.md", f"{subtree}/*.md"]
    out = subprocess.run(args, capture_output=True, text=True).stdout.split()
    return [pathlib.Path(p) for p in out]


def _line_of(text: str, offset: int) -> int:
    return text[:offset].count("\n") + 1


def scan_markdown_links(path: pathlib.Path, text: str) -> tuple[int, list[str]]:
    """`[label](target)` links, resolved against the file's own directory."""
    checked = 0
    broken: list[str] = []
    for m in LINK.finditer(text):
        target = m.group(1)
        if target.startswith(SKIP_SCHEME):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part or PLACEHOLDER.search(path_part):
            continue
        checked += 1
        if not (path.parent / path_part).exists():
            broken.append(f"  {path}:{_line_of(text, m.start())}  ->  {target}")
    return checked, broken


def scan_backticked_refs(path: pathlib.Path, text: str, root: pathlib.Path) -> tuple[int, list[str]]:
    """Backticked `<skill>/references/<file>.md` — always repo-root-relative."""
    # CHANGELOG is exempt: a log records what was true when written, and its
    # entries legitimately name files that were later renamed or removed
    # (including the entry documenting these very fixes).
    if path.name == "CHANGELOG.md":
        return 0, []
    checked = 0
    broken: list[str] = []
    for m in BACKTICK_REF.finditer(text):
        target = m.group(1)
        checked += 1
        if not (root / target).exists():
            broken.append(
                f"  {path}:{_line_of(text, m.start())}  ->  `{target}`  (backticked ref)"
            )
    return checked, broken


def main() -> int:
    root = pathlib.Path(
        subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True).stdout.strip() or "."
    )
    subtree = sys.argv[1] if len(sys.argv) > 1 else None
    files = tracked_markdown(subtree)
    broken: list[str] = []
    checked = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for count, hits in (scan_markdown_links(f, text),
                            scan_backticked_refs(f, text, root)):
            checked += count
            broken += hits
    if broken:
        print(f"links: FAILED — {len(broken)} broken of {checked} relative links\n")
        print("\n".join(broken))
        return 1
    print(f"links: OK ({checked} relative links across {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
