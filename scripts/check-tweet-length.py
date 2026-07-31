#!/usr/bin/env python3
"""Verify every fenced block in the X thread fits a tweet.

The draft claimed "all tweets ≤280 chars (verified)" and pointed at a one-liner
that no longer parsed the file correctly. A launch thread that overflows gets
silently truncated mid-sentence, so the claim needs a check that actually runs.

Usage:
    python3 scripts/check-tweet-length.py            # default: docs/launch-posts/x-thread.md
    python3 scripts/check-tweet-length.py <file>

Exit: 0 all fit, 1 something overflows.
"""
from __future__ import annotations

import pathlib
import re
import sys

LIMIT = 280
DEFAULT = "docs/launch-posts/x-thread.md"
# Fenced blocks that are shell snippets, not tweets.
SHELL = re.compile(r"^```(bash|sh|shell|console)")


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    target = root / (sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
    if not target.is_file():
        print(f"tweets: FAILED — {target} not found")
        return 1

    text = target.read_text(encoding="utf-8")
    blocks = re.findall(r"^```[a-z]*\n(.*?)^```", text, re.S | re.M)
    langs = re.findall(r"^```([a-z]*)\n", text, re.M)

    over = []
    checked = 0
    for lang, body in zip(langs, blocks):
        if lang:  # ```bash and friends are instructions, not tweets
            continue
        body = body.rstrip("\n")
        checked += 1
        n = len(body)
        first = body.split("\n", 1)[0][:58]
        marker = "OVER" if n > LIMIT else "ok"
        print(f"  {marker:>4}  {n:>3}/{LIMIT}  {first}…")
        if n > LIMIT:
            over.append((n, first))

    print()
    if over:
        print(f"tweets: FAILED — {len(over)} of {checked} exceed {LIMIT} characters")
        return 1
    print(f"tweets: OK ({checked} blocks, all within {LIMIT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
