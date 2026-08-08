#!/usr/bin/env python3
"""Keep the catalog blurb honest when a skill's own description changes.

Every skill describes itself twice. `SKILL.md` frontmatter carries the routing
contract — the text Claude reads when deciding whether this skill applies.
`skills.json` carries the catalog blurb, which becomes the README table, the
SKILL-INDEX and whatever a directory listing renders. All 43 pairs are written
independently, and they should be: one is addressed to a model choosing a tool,
the other to a person browsing a list. Forcing them identical would make both
worse.

What must not happen is the second one going quietly stale. `skills.json` claimed
"17 Claude Code skills" long after there were 42, and nothing noticed.

So this does not compare the two texts. It records the SKILL.md description that
the catalog blurb was last written against, and fails when that text moves. The
failure prints all three — what the description was, what it is now, and what the
catalog still says — so re-freezing is a decision rather than a keystroke.

Usage:
    python3 scripts/check-skill-descriptions.py            # check
    python3 scripts/check-skill-descriptions.py --freeze   # accept current text
"""
from __future__ import annotations

import difflib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills.json"
LOCK = ROOT / "docs" / "skill-descriptions.lock.json"

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.S)
_DESCRIPTION = re.compile(r"^description:[ \t]*(.*(?:\n[ \t]+.*)*)", re.M)


def skill_md_description(name: str) -> str | None:
    """The `description:` line from a skill's frontmatter, whitespace-normalised."""
    path = ROOT / "skills" / name / "SKILL.md"
    if not path.is_file():
        return None
    front = _FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not front:
        return None
    found = _DESCRIPTION.search(front.group(1))
    if not found:
        return None
    return " ".join(found.group(1).split()).strip("'\"")


def current() -> dict[str, str]:
    registered = json.loads(MANIFEST.read_text(encoding="utf-8"))["skills"]
    return {
        entry["name"]: desc
        for entry in registered
        if (desc := skill_md_description(entry["name"])) is not None
    }


def catalog() -> dict[str, str]:
    registered = json.loads(MANIFEST.read_text(encoding="utf-8"))["skills"]
    return {entry["name"]: entry.get("description", "") for entry in registered}


def _locked() -> dict[str, str]:
    if not LOCK.is_file():
        return {}
    return json.loads(LOCK.read_text(encoding="utf-8")).get("descriptions", {})


def _wrap(text: str, width: int = 92) -> str:
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    out.append(line)
    return "\n".join(f"        {ln}" for ln in out)


def _changed_report(name: str, was: str, now: str, blurb: str) -> str:
    words = difflib.SequenceMatcher(None, was.split(), now.split()).ratio()
    return (
        f"  ✗ {name} — SKILL.md description changed ({words:.0%} of the wording survives)\n"
        f"      was:\n{_wrap(was)}\n"
        f"      now:\n{_wrap(now)}\n"
        f"      skills.json still says:\n{_wrap(blurb)}"
    )


def audit() -> list[str]:
    live, locked, blurbs = current(), _locked(), catalog()
    failures = []
    for name, now in sorted(live.items()):
        if name not in locked:
            failures.append(
                f"  ✗ {name} — no locked description; write its skills.json blurb, then --freeze"
            )
        elif locked[name] != now:
            failures.append(_changed_report(name, locked[name], now, blurbs.get(name, "")))
    for name in sorted(set(locked) - set(live)):
        failures.append(f"  ✗ {name} — locked but no longer in skills.json; --freeze to drop it")
    return failures


def freeze() -> int:
    LOCK.write_text(
        json.dumps(
            {
                "_comment": (
                    "SKILL.md descriptions as of the last time the skills.json catalog blurb "
                    "was reconciled against them. Regenerate with "
                    "scripts/check-skill-descriptions.py --freeze, and only after re-reading "
                    "the blurb it belongs to."
                ),
                "descriptions": current(),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"descriptions: froze {len(current())} skills into {LOCK.relative_to(ROOT)}")
    return 0


def main() -> int:
    if "--freeze" in sys.argv:
        return freeze()
    failures = audit()
    if failures:
        print(f"descriptions: FAILED — {len(failures)} skill(s) drifted from the catalog")
        print("\n".join(failures))
        print(
            "\n  Re-read the skills.json blurb for each, update it if it now misleads,"
            "\n  then: python3 scripts/check-skill-descriptions.py --freeze"
        )
        return 1
    print(f"descriptions: OK ({len(current())} catalog blurbs reconciled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
