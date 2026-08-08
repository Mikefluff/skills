"""A "N skills" claim anywhere in the docs has to be the N that exists.

This is the sentence that rots first and is read most. `skills.json` advertised
"17 Claude Code skills" against 42 on disk; `QUICKSTART.md` told a new user to
expect 22 folders when there were 43, which turns the very first verification
step in the onboarding into a failed one; the launch copy quoted 41; and the
GitHub repository description — the single most-read line about the project —
said 42.

None of it is derivable from a version number, so nothing caught it. The count
is derivable from `skills.json`, which is what this checks.

Out of scope: the GitHub description and topics live on the remote and cannot be
asserted offline. `docs/distribution.md` carries them under its dated marker
instead.
"""

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTERED = len(json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))["skills"])

# "43 skills", "43 Claude Code skills", "43 skill folders".
CLAIM = re.compile(r"\b(\d{2})\s+(?:Claude Code\s+)?skill(?:s| folders?)\b", re.IGNORECASE)

# CHANGELOG is history: "shipped with 22 skills" was true when written.
# generated/ is output. `skills-update` quotes a v1.7.0 changelog inside its own
# worked examples — the number there is the sample's, and editing it to today's
# would make the example describe a release that never happened.
EXEMPT_PARTS = {".git", "node_modules", "generated", ".pytest_cache"}
EXEMPT_FILES = {"CHANGELOG.md"}
EXEMPT_DIRS = {pathlib.Path("skills/skills-update/examples")}


def _documents():
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if set(rel.parts) & EXEMPT_PARTS or rel.name in EXEMPT_FILES:
            continue
        if any(d in rel.parents for d in EXEMPT_DIRS):
            continue
        yield rel, path


class TestSkillCount(unittest.TestCase):
    def test_the_scan_reaches_the_docs(self):
        self.assertGreater(len(list(_documents())), 50, "the doc scan is broken, not the repo")

    def test_no_document_claims_a_count_that_is_not_the_count(self):
        wrong = []
        for rel, path in _documents():
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for found in CLAIM.finditer(line):
                    if int(found.group(1)) != REGISTERED:
                        wrong.append(f"{rel}:{lineno} claims '{found.group(0)}' — {REGISTERED} exist")
        self.assertEqual([], wrong, "\n" + "\n".join(wrong))

    def test_the_count_is_read_from_the_manifest_not_pinned_here(self):
        # A literal in this file would rot the same way the docs did.
        on_disk = sum(1 for p in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(on_disk, REGISTERED)


if __name__ == "__main__":
    unittest.main()
