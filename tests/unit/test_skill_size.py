"""A SKILL.md is loaded whole; its references are not.

That is the deal progressive disclosure makes, and the collection already keeps
it — every skill over ten thousand characters carries a load-on-demand table and
links out to `references/`. This test exists so the deal survives the next
skill, not because it is currently broken.

It also fixes a measurement. The roadmap flagged `writer/SKILL.md` as ~27 KB and
asked whether its body should move into references. 27 KB is its size on disk in
UTF-8, where every Cyrillic character costs two bytes and 59% of the file is
Cyrillic. In characters — the unit that maps to context — it is 16,633, which is
smaller than `carousel-builder`, and its Layer 1 section is an index of 25
category names pointing at the full catalogue rather than a copy of it. The file
was doing the right thing; the number was in the wrong unit.
"""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILLS = sorted(ROOT.glob("skills/*/SKILL.md"))

# Generous: the largest today is 278 lines. This is a tripwire for a skill that
# has stopped summarising and started inlining, not a style rule.
MAX_LINES = 400

# Past this, a flat SKILL.md is carrying detail that belongs behind a link.
DISCLOSURE_THRESHOLD_CHARS = 10_000

REFERENCE_LINK = re.compile(r"\(references/[^)]+\.md\)")


class TestSkillBodies(unittest.TestCase):
    def test_the_scan_found_the_skills(self):
        self.assertGreater(len(SKILLS), 10, "the SKILL.md scan is broken, not the repo")

    def test_no_skill_body_runs_past_the_cap(self):
        for path in SKILLS:
            with self.subTest(skill=path.parts[-2]):
                lines = len(path.read_text(encoding="utf-8").splitlines())
                self.assertLessEqual(
                    lines,
                    MAX_LINES,
                    f"{path.parts[-2]}/SKILL.md is {lines} lines — move detail into references/",
                )

    def test_long_skills_disclose_progressively(self):
        for path in SKILLS:
            text = path.read_text(encoding="utf-8")
            if len(text) < DISCLOSURE_THRESHOLD_CHARS:
                continue
            with self.subTest(skill=path.parts[-2]):
                self.assertTrue(
                    REFERENCE_LINK.search(text),
                    f"{path.parts[-2]}/SKILL.md is {len(text)} chars with no references/ link — "
                    f"everything in it is loaded on every invocation",
                )
                self.assertTrue(
                    (path.parent / "references").is_dir(),
                    f"{path.parts[-2]} links to references/ but has no such directory",
                )

    def test_size_is_measured_in_characters(self):
        # The claim this test corrects: writer is not the largest body, and
        # bytes said otherwise only because Cyrillic costs two of them.
        writer = (ROOT / "skills" / "writer" / "SKILL.md").read_text(encoding="utf-8")
        largest = max(len(p.read_text(encoding="utf-8")) for p in SKILLS)
        self.assertLess(len(writer), largest)
        self.assertGreater(len(writer.encode("utf-8")), len(writer) * 1.5)


if __name__ == "__main__":
    unittest.main()
