"""Directory submission packets.

The packets exist to be pasted into forms, so the failure that matters is a
packet that quietly describes the wrong project — a stale version, a missing
repo URL, an invented submission route. Facts are read from the repo rather
than typed in; these tests pin that they stay read.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import directories  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


class TestProjectFacts(unittest.TestCase):
    def test_facts_come_from_the_repo_not_from_constants(self):
        facts = directories.ProjectFacts.load(ROOT)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(facts.version, version)
        self.assertEqual(facts.name, pkg["name"])
        self.assertEqual(facts.license, pkg["license"])

    def test_repo_url_is_cleaned_for_display(self):
        facts = directories.ProjectFacts.load(ROOT)
        self.assertFalse(facts.repo.startswith("git+"), "git+ prefix is not pasteable")
        self.assertFalse(facts.repo.endswith(".git"), ".git suffix is not pasteable")
        self.assertTrue(facts.repo.startswith("https://"))

    def test_skill_count_is_counted_not_asserted(self):
        facts = directories.ProjectFacts.load(ROOT)
        self.assertEqual(facts.skill_count, len(list((ROOT / "skills").glob("*/SKILL.md"))))


class TestSpecs(unittest.TestCase):
    def test_default_order_covers_every_spec(self):
        self.assertEqual(set(directories.DEFAULT_ORDER), set(directories.SPECS))

    def test_every_spec_declares_a_route_and_a_link_type(self):
        for slug, spec in directories.SPECS.items():
            self.assertTrue(spec.route.strip(), f"{slug} has no submission route")
            self.assertIn(spec.link, {"dofollow", "nofollow", "unknown"}, slug)
            self.assertTrue(spec.steps, f"{slug} has no steps")

    def test_slugs_match_their_keys(self):
        for key, spec in directories.SPECS.items():
            self.assertEqual(key, spec.slug)

    def test_awesome_claude_code_warns_against_automated_submission(self):
        # Their CONTRIBUTING threatens a ban for PR/CLI submissions. If that
        # warning ever drops out of the packet, someone will automate it.
        notes = " ".join(directories.SPECS["awesome-claude-code"].notes).lower()
        self.assertIn("human", notes)
        self.assertIn("not", directories.SPECS["awesome-claude-code"].route.lower())


class TestPackets(unittest.TestCase):
    def setUp(self):
        self.out = Path(tempfile.mkdtemp())

    def test_one_file_per_directory(self):
        written = directories.write_packets(ROOT, self.out)
        self.assertEqual(len(written), len(directories.DEFAULT_ORDER))
        for path in written:
            self.assertTrue(path.is_file())

    def test_packet_carries_the_current_version(self):
        directories.write_packets(ROOT, self.out, directories=("npm",))
        text = (self.out / "submit-npm.md").read_text(encoding="utf-8")
        self.assertIn((ROOT / "VERSION").read_text(encoding="utf-8").strip(), text)

    def test_nofollow_directories_say_so_in_the_packet(self):
        directories.write_packets(ROOT, self.out, directories=("producthunt",))
        text = (self.out / "submit-producthunt.md").read_text(encoding="utf-8")
        self.assertIn("nofollow", text)
        self.assertIn("not for SEO", text)

    def test_unknown_directory_raises_rather_than_skipping(self):
        with self.assertRaises(KeyError):
            directories.write_packets(ROOT, self.out, directories=("myspace",))

    def test_subset_writes_only_what_was_asked_for(self):
        written = directories.write_packets(ROOT, self.out, directories=("npm", "sourceforge"))
        self.assertEqual([p.name for p in written], ["submit-npm.md", "submit-sourceforge.md"])


class TestNpmPackaging(unittest.TestCase):
    """The npm listing is the highest-authority one, so its manifest is pinned."""

    def setUp(self):
        self.pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    def test_bytecode_is_excluded_from_the_tarball(self):
        # `files` takes precedence over .npmignore, so the ignore file alone did
        # not stop __pycache__ shipping. Negation patterns are what fixed it.
        files = self.pkg["files"]
        self.assertIn("!**/__pycache__/**", files)
        self.assertIn("!**/*.pyc", files)

    def test_plugin_manifest_ships(self):
        self.assertIn(".claude-plugin/", self.pkg["files"])

    def test_homepage_and_repository_are_set(self):
        # These are the fields npm renders as links on the package page.
        self.assertTrue(self.pkg.get("homepage"))
        self.assertTrue((self.pkg.get("repository") or {}).get("url"))


if __name__ == "__main__":
    unittest.main()
