"""The catalog blurb has to have been written against the current skill.

A skill describes itself twice, on purpose. `SKILL.md` frontmatter is the
routing contract Claude reads; the `skills.json` blurb is what a person browsing
the README or SKILL-INDEX sees. All 43 pairs are independently worded and should
stay that way — a model picking a tool and a human scanning a table want
different sentences.

The failure mode is only ever one-directional: the skill changes, the catalog
does not. That is how `skills.json` came to advertise "17 Claude Code skills"
against 42 on disk. So the lock records the SKILL.md text each blurb was last
reconciled against, and this test fails the moment that text moves.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "check_skill_descriptions", ROOT / "scripts" / "check-skill-descriptions.py"
)
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


class TestDescriptionLock(unittest.TestCase):
    def test_every_blurb_was_written_against_the_current_description(self):
        failures = checker.audit()
        self.assertEqual(
            [],
            failures,
            "\n\n" + "\n".join(failures) + "\n\nRun: make freeze-descriptions",
        )

    def test_the_lock_covers_every_registered_skill(self):
        # A lock that silently stopped covering skills is the same bug one level
        # up: green because it checked nothing.
        registered = {s["name"] for s in json.loads((ROOT / "skills.json").read_text())["skills"]}
        self.assertEqual(registered, set(checker.current()))
        self.assertGreater(len(registered), 10)


class TestExtraction(unittest.TestCase):
    def test_reads_the_frontmatter_description(self):
        desc = checker.skill_md_description("writer")
        self.assertIsNotNone(desc)
        self.assertNotIn("\n", desc, "the description is normalised to one line")
        self.assertFalse(desc.startswith('"'), "surrounding quotes are stripped")

    def test_unknown_skill_reads_as_absent_rather_than_raising(self):
        self.assertIsNone(checker.skill_md_description("no-such-skill"))


if __name__ == "__main__":
    unittest.main()
