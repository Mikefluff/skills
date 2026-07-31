#!/usr/bin/env python3
"""Lint the launch copy that lives inside fenced blocks.

Two layers of blindness meet in these files, and both were self-inflicted:

  1. `lint.py` masks fenced code blocks by default, and the launch copy IS the
     fenced block. Linting the file normally measures the surrounding notes.
  2. The files carry `lint-role: catalogue`, which makes the pre-commit hook skip
     them entirely — correct for the hook, fatal on its own.

Net effect: promotional copy for an anti-slop toolkit, written by an LLM, that
nothing ever checked. This closes that.

Quoted examples are the complication. These posts legitimately print
"revolutionary", "click here" and "delve into" because those are what the linter
catches. Rather than guess which hits are quotes, the known ones are frozen as a
baseline of (category, matched text) pairs. Anything not in the baseline is new
prose and fails. Adding a genuinely new example means updating the baseline on
purpose, which is the review moment worth having.

Usage:
    python3 scripts/check-launch-copy.py            # verify
    python3 scripts/check-launch-copy.py --update   # re-freeze the baseline

Exit: 0 clean, 1 unreviewed hits found.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests" / "snapshots" / "launch-copy.json"
TARGETS = sorted((ROOT / "docs" / "launch-posts").glob("*.md")) + [ROOT / "docs" / "LAUNCH-POST.md"]


def hits_for(path: pathlib.Path) -> list[list[str]]:
    """Caution-level hits with fenced blocks scanned, as [category, match] pairs."""
    out = subprocess.run(
        [sys.executable, str(ROOT / "writer" / "scripts" / "lint.py"),
         str(path), "--scan-code-blocks", "--json"],
        capture_output=True, text=True,
    ).stdout
    if not out.strip():
        return []
    data = json.loads(out)
    return sorted(
        [h["category"], h["match"]]
        for h in data["hits"] if h["severity"] == "caution"
    )


def collect() -> dict[str, list[list[str]]]:
    return {p.relative_to(ROOT).as_posix(): hits_for(p) for p in TARGETS if p.is_file()}


def main() -> int:
    current = collect()

    if "--update" in sys.argv:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        total = sum(len(v) for v in current.values())
        print(f"Updated {BASELINE.relative_to(ROOT)} — {total} reviewed hit(s) frozen")
        return 0

    if not BASELINE.is_file():
        print(f"launch-copy: FAILED — no baseline at {BASELINE.relative_to(ROOT)}")
        print("  run: python3 scripts/check-launch-copy.py --update")
        return 1

    known = json.loads(BASELINE.read_text(encoding="utf-8"))
    new: list[str] = []
    for path, hits in current.items():
        allowed = [tuple(h) for h in known.get(path, [])]
        for cat, match in hits:
            if (cat, match) in allowed:
                allowed.remove((cat, match))
                continue
            new.append(f"  {path}  [{cat}]  {match[:80]}")

    if new:
        print(f"launch-copy: FAILED — {len(new)} hit(s) not in the reviewed baseline\n")
        print("\n".join(new))
        print("\nEither fix the copy, or — if this is a deliberate new example —")
        print("re-freeze with: python3 scripts/check-launch-copy.py --update")
        return 1

    total = sum(len(v) for v in current.values())
    print(f"launch-copy: OK ({len(current)} files, {total} hits all reviewed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
