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


def tracked_markdown(subtree: str | None) -> list[pathlib.Path]:
    args = ["git", "ls-files", "*.md"]
    if subtree:
        args = ["git", "ls-files", f"{subtree}/**/*.md", f"{subtree}/*.md"]
    out = subprocess.run(args, capture_output=True, text=True).stdout.split()
    return [pathlib.Path(p) for p in out]


def main() -> int:
    subtree = sys.argv[1] if len(sys.argv) > 1 else None
    files = tracked_markdown(subtree)
    broken: list[str] = []
    checked = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in LINK.finditer(text):
            target = m.group(1)
            if target.startswith(SKIP_SCHEME):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part or PLACEHOLDER.search(path_part):
                continue
            checked += 1
            if not (f.parent / path_part).exists():
                line = text[: m.start()].count("\n") + 1
                broken.append(f"  {f}:{line}  ->  {target}")
    if broken:
        print(f"links: FAILED — {len(broken)} broken of {checked} relative links\n")
        print("\n".join(broken))
        return 1
    print(f"links: OK ({checked} relative links across {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
