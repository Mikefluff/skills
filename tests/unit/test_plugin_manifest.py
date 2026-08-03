"""The plugin manifests are the install path — a typo here is a broken marketplace.

`/plugin marketplace add Mikefluff/skills` reads .claude-plugin/marketplace.json and
nothing else. If a required field is missing, the skill directory is misspelled, or
the declared version drifts from VERSION, the failure lands on the user rather than
in CI. package.json already drifted to 1.9.0 while VERSION reached 2.22.0, which is
exactly the shape of mistake these tests exist to catch.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"

# Anthropic reserves these so third-party marketplaces cannot pose as official ones.
RESERVED_NAMES = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "claude-plugins-community", "claude-community", "anthropic-marketplace",
    "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
    "knowledge-work-plugins", "life-sciences", "claude-for-legal",
    "claude-for-financial-services", "financial-services-plugins",
    "first-party-plugins", "healthcare",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


class TestMarketplaceManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = _load(MARKETPLACE)

    def test_required_fields_present(self):
        for field in ("name", "owner", "plugins"):
            self.assertIn(field, self.data, f"marketplace.json is missing '{field}'")
        self.assertIn("name", self.data["owner"], "owner.name is required")
        self.assertTrue(self.data["plugins"], "marketplace lists no plugins")

    def test_marketplace_name_is_kebab_case_and_unreserved(self):
        name = self.data["name"]
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$", "name must be kebab-case")
        self.assertNotIn(name, RESERVED_NAMES, f"'{name}' is reserved for Anthropic")

    def test_every_plugin_entry_has_a_name_and_source(self):
        for entry in self.data["plugins"]:
            self.assertIn("name", entry)
            self.assertIn("source", entry, f"plugin '{entry.get('name')}' has no source")

    def test_declared_skill_paths_exist_and_hold_skills(self):
        for entry in self.data["plugins"]:
            declared = entry.get("skills")
            if not declared:
                continue
            paths = [declared] if isinstance(declared, str) else declared
            for rel in paths:
                target = (ROOT / rel).resolve()
                self.assertTrue(target.is_dir(), f"skills path '{rel}' is not a directory")
                found = list(target.glob("*/SKILL.md"))
                self.assertTrue(found, f"no <name>/SKILL.md found under '{rel}'")


class TestPluginManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = _load(PLUGIN)

    def test_name_matches_the_marketplace_entry(self):
        entries = {e["name"] for e in _load(MARKETPLACE)["plugins"]}
        self.assertIn(
            self.data["name"], entries,
            "plugin.json name does not appear in marketplace.json plugins",
        )

    def test_skill_count_claimed_in_the_description_is_true(self):
        skills = len(list((ROOT / "skills").glob("*/SKILL.md")))
        self.assertIn(
            str(skills), self.data["description"],
            f"description does not mention the real skill count ({skills})",
        )


class TestVersionParity(unittest.TestCase):
    """One version string, several files. bump.sh syncs them; this proves it did."""

    def test_manifests_match_the_version_file(self):
        version = _version()
        self.assertEqual(_load(PLUGIN)["version"], version, "plugin.json is out of sync")
        marketplace = _load(MARKETPLACE)
        self.assertEqual(marketplace["version"], version, "marketplace.json is out of sync")
        for entry in marketplace["plugins"]:
            self.assertEqual(
                entry.get("version"), version,
                f"marketplace plugin '{entry['name']}' is out of sync",
            )

    def test_package_json_matches_the_version_file(self):
        pkg = _load(ROOT / "package.json")
        self.assertEqual(pkg["version"], _version(), "package.json is out of sync")

    def test_skills_manifest_matches_the_version_file(self):
        manifest = _load(ROOT / "skills.json")
        self.assertEqual(manifest["version"], _version(), "skills.json is out of sync")


if __name__ == "__main__":
    unittest.main()
