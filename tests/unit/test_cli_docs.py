"""A command printed in the docs has to be a command that runs.

Two kinds of flag look alike in this collection. `/logo-maker --variants 4` is a
skill-level convention: Claude reads it and writes a plan, and no parser is
involved. `python3 -m common.runners.cli.cover --plan-file plan.json --yes` is a
literal command a reader copies, and argparse answers a wrong one with
"unrecognized arguments" rather than with anything about what the doc meant.

Only the second kind is checkable, and only because every CLI module now exposes
a zero-arg `build_parser()`. Nine maker modules did not — their parser existed
only inside a call to `parse_args`, which is readable by running the command and
no other way.
"""

import argparse
import importlib
import importlib.util
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("check_cli_docs", ROOT / "scripts" / "check-cli-docs.py")
cli_docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli_docs)

CLI_DIR = ROOT / "common" / "runners" / "cli"
MODULES = sorted(p.stem for p in CLI_DIR.glob("*.py") if not p.stem.startswith("_"))


class TestParserSurface(unittest.TestCase):
    def test_every_cli_module_exposes_its_parser(self):
        for name in MODULES:
            with self.subTest(module=name):
                module = importlib.import_module(f"common.runners.cli.{name}")
                build = getattr(module, "build_parser", None)
                self.assertTrue(callable(build), f"{name} has no build_parser()")
                self.assertIsInstance(build(), argparse.ArgumentParser)

    def test_the_module_list_is_not_empty(self):
        self.assertGreater(len(MODULES), 20, "the CLI scan found almost nothing")


class TestDocumentedCommands(unittest.TestCase):
    def test_no_documented_command_would_be_rejected(self):
        failures, checked = cli_docs.audit()
        self.assertGreater(checked, 20, "the doc scan found almost nothing — it is broken, not clean")
        self.assertEqual([], failures, "\n\n" + "\n".join(failures))


class TestScanning(unittest.TestCase):
    def _commands(self, text: str, owner=None):
        path = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory())) / "doc.md"
        path.write_text(text, encoding="utf-8")
        return list(cli_docs._commands(path, owner))

    def test_a_wrapped_command_is_read_as_one(self):
        # Half the documented commands wrap across lines with a backslash; a
        # scanner that reads them line by line silently checks only the head.
        found = self._commands(
            "python3 -m common.runners.cli.cover \\\n  --plan-file p.json \\\n  --yes\n"
        )
        self.assertEqual(1, len(found))
        self.assertEqual(["--plan-file", "--yes"], found[0][2])

    def test_a_run_py_call_resolves_through_the_owning_skill(self):
        found = self._commands("python3 scripts/run.py --model veo-3-1\n", owner="video-prompt")
        self.assertEqual([("video", ["--model"])], [(m, f) for _, m, f in found])

    def test_skill_level_flags_are_not_treated_as_cli_flags(self):
        self.assertEqual([], self._commands("/logo-maker --brand Acme --variants 4 --execute\n"))


if __name__ == "__main__":
    unittest.main()
