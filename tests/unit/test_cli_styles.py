"""The styles CLI, and the submission package a human carries to GitHub.

`submit` writes a directory someone opens a pull request from. Its two
documents are built with str.format() over templates full of shell snippets,
which is one typo away from shipping a literal `{style_id}` into a PR body —
and nobody would find out until it was public.

So the templates are checked for unresolved placeholders after formatting,
every subcommand's exit code is pinned, and `submit` is driven end to end
against a real file in a temporary user directory.

The rest of the CLI is table-driven — nine subcommands built from one _Sub
spec — so the parser is checked against that table rather than by hand: a
subcommand added to the tuple without its arguments would otherwise only fail
when someone ran it.
"""

import io
import re
import string
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import styles as styles_mod  # noqa: E402
from common.runners import styles_authoring  # noqa: E402
from common.runners.cli import _styles_submit as submit_mod  # noqa: E402
from common.runners.cli import styles as cli  # noqa: E402

STYLE_MD = """\
---
id: test-style
display: Test Style
modality: carousel
mood: [calm, precise]
tags: [minimal, editorial]
text_friendly: true
photoreal: false
---

**Vibe**: A test fixture that validates.

**Palette**: Ink black, paper white, one accent.

**Typography**: One serif, one sans.

**Medium**: Flat vector.

**Composition**: Centred, generous margins.

**Style anchor (carousel)**:
> A deliberately unremarkable style used to exercise the submission path
> without depending on whatever the bundled library happens to contain today.

**Style anchor (text-in-image mode)**:
> Same, with the headline set in the serif.

**Best for**: tests.

**Avoid for**: production.

**Suggested models**: none.

**Caption tone**: flat.
"""


def _unresolved(text: str) -> list[str]:
    """Placeholders str.format() would have filled but did not.

    Only single-brace fields count — `{{` is an escaped literal and the shell
    snippets in these templates are full of them.
    """
    return [
        name
        for _lit, name, _spec, _conv in string.Formatter().parse(text)
        if name is not None
    ]


class Templates(unittest.TestCase):
    """The two documents a submission package ships."""

    def style(self):
        return styles_mod.Style(
            "test-style", "carousel",
            {"display": "Test Style", "mood": ["calm"], "tags": ["minimal"]},
            STYLE_MD, Path("/tmp/test-style.md"),
        )

    def test_the_pr_description_has_no_unresolved_placeholder(self):
        for status in ("new", "override"):
            with self.subTest(status=status):
                body = submit_mod._build_pr_description(
                    self.style(), "carousel", "test-style", status
                )
                self.assertEqual(_unresolved(body), [], "unfilled placeholder in the PR body")
                self.assertNotIn("{", body.replace("{{", "").replace("}}", ""))

    def test_the_readme_has_no_unresolved_placeholder(self):
        readme = submit_mod._build_submission_readme("carousel", "test-style")
        self.assertEqual(_unresolved(readme), [])

    def test_every_field_the_pr_template_declares_is_supplied(self):
        # The failure this catches is additive: someone adds {author} to the
        # template and forgets the kwarg, and .format() raises at submit time
        # for a user rather than here.
        declared = set(_unresolved(submit_mod._PR_DESCRIPTION))
        body = submit_mod._build_pr_description(self.style(), "carousel", "test-style", "new")
        self.assertTrue(declared, "template declares no fields — did it stop using format()?")
        for field in declared:
            with self.subTest(field=field):
                self.assertNotIn("{" + field + "}", body)

    def test_the_readme_template_declares_only_what_it_is_given(self):
        self.assertEqual(set(_unresolved(submit_mod._SUBMISSION_README)), {"modality", "style_id"})

    def test_the_values_actually_reach_the_documents(self):
        body = submit_mod._build_pr_description(self.style(), "carousel", "test-style", "new")
        self.assertIn("test-style", body)
        self.assertIn("Test Style", body)
        self.assertIn("carousel", body)
        readme = submit_mod._build_submission_readme("video", "other-id")
        self.assertIn("video", readme)
        self.assertIn("other-id", readme)

    def test_override_and_new_produce_different_titles(self):
        new = submit_mod._build_pr_description(self.style(), "carousel", "test-style", "new")
        override = submit_mod._build_pr_description(
            self.style(), "carousel", "test-style", "override"
        )
        self.assertNotEqual(new, override)
        self.assertIn("Add", new)
        self.assertIn("Replace bundled", override)

    def test_empty_mood_and_tags_read_as_none_not_as_blank(self):
        bare = styles_mod.Style(
            "test-style", "carousel", {"display": "Test Style"}, STYLE_MD, Path("/tmp/x.md")
        )
        body = submit_mod._build_pr_description(bare, "carousel", "test-style", "new")
        self.assertIn("(none)", body)


class Parser(unittest.TestCase):
    """Nine subcommands from one table — checked against the table."""

    def test_every_subcommand_in_the_table_is_reachable(self):
        parser = cli.build_parser()
        actions = [a for a in parser._actions if hasattr(a, "choices") and a.choices]
        names = set(actions[0].choices)
        self.assertEqual(names, {s.name for s in cli._SUBCOMMANDS})

    def test_every_subcommand_binds_a_handler(self):
        for spec in cli._SUBCOMMANDS:
            with self.subTest(cmd=spec.name):
                argv = [spec.name]
                if not spec.optional_modality:
                    argv.append("carousel")
                if spec.wants_id and not spec.optional_id:
                    argv.append("some-id")
                args = cli.build_parser().parse_args(argv)
                self.assertIs(args.func, spec.handler)

    def test_no_subcommand_means_exit_two(self):
        with self.assertRaises(SystemExit) as caught:
            cli.build_parser().parse_args([])
        self.assertEqual(caught.exception.code, 2)

    def test_an_unknown_modality_is_rejected_by_the_parser(self):
        with self.assertRaises(SystemExit):
            cli.build_parser().parse_args(["show", "hologram", "x"])

    def test_list_flags_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            cli.build_parser().parse_args(["list", "--user-only", "--bundled-only"])


class SubmitCase(unittest.TestCase):
    """submit, run end to end against a temporary user library."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.user = self.root / "user-styles"
        (self.user / "carousel").mkdir(parents=True)
        (self.user / "carousel" / "test-style.md").write_text(STYLE_MD, encoding="utf-8")
        # submit writes its package into the current directory.
        import os

        origin = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, origin)

    def run_cli(self, argv_tail, *, status="new", style=None, issues=()):
        argv = ["common.runners.cli.styles", *argv_tail]
        out, err = io.StringIO(), io.StringIO()
        loaded = style if style is not None else styles_mod.Style(
            "test-style", "carousel",
            {"display": "Test Style", "mood": ["calm"], "tags": ["minimal"]},
            STYLE_MD, self.user / "carousel" / "test-style.md",
        )
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(styles_authoring, "user_dir", return_value=self.user),
            mock.patch.object(submit_mod.styles_authoring, "user_dir", return_value=self.user),
            mock.patch.object(submit_mod.styles_authoring, "resolution_status", return_value=status),
            mock.patch.object(submit_mod.styles_mod, "load_style", return_value=loaded),
            mock.patch.object(submit_mod.styles_validate, "validate_style", return_value=list(issues)),
        ]
        with redirect_stdout(out), redirect_stderr(err):
            for p in patches:
                p.start()
            try:
                code = cli.main()
            except SystemExit as exc:
                code = exc.code
            finally:
                for p in reversed(patches):
                    p.stop()
        return code, out.getvalue(), err.getvalue()

    def package(self) -> Path:
        found = sorted(self.root.glob("style-submission-*"))
        self.assertEqual(len(found), 1, f"expected one package, found {found}")
        return found[0]

    def test_submit_writes_the_three_files_it_promises(self):
        code, out, _err = self.run_cli(["submit", "carousel", "test-style"])
        self.assertEqual(code, 0, out)
        pkg = self.package()
        self.assertTrue((pkg / "PR-DESCRIPTION.md").is_file())
        self.assertTrue((pkg / "README.md").is_file())
        self.assertTrue(
            (pkg / "common" / "style-library" / "carousel" / "test-style.md").is_file(),
            "the style must sit at the exact path it lands at upstream",
        )

    def test_the_style_file_is_copied_verbatim(self):
        self.run_cli(["submit", "carousel", "test-style"])
        landed = self.package() / "common" / "style-library" / "carousel" / "test-style.md"
        self.assertEqual(landed.read_text(encoding="utf-8"), STYLE_MD)

    def test_the_written_documents_carry_no_unresolved_placeholder(self):
        # The whole reason this file exists: these two go to GitHub.
        self.run_cli(["submit", "carousel", "test-style"])
        pkg = self.package()
        for name in ("PR-DESCRIPTION.md", "README.md"):
            with self.subTest(doc=name):
                text = (pkg / name).read_text(encoding="utf-8")
                self.assertEqual(_unresolved(text), [], f"{name} shipped a placeholder")
                self.assertNotRegex(text, r"\{[a-z_]+\}")

    def test_a_missing_user_override_is_two(self):
        code, _out, err = self.run_cli(["submit", "carousel", "absent-style"])
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_validation_failure_blocks_the_submission(self):
        code, _out, err = self.run_cli(
            ["submit", "carousel", "test-style"], issues=["mood is required"]
        )
        self.assertNotEqual(code, 0, "an invalid style must not reach a PR")
        self.assertIn("mood is required", err)
        self.assertFalse(sorted(self.root.glob("style-submission-*")), "package written anyway")

    def test_force_overrides_the_validation_gate(self):
        code, _out, _err = self.run_cli(
            ["submit", "carousel", "test-style", "--force"], issues=["mood is required"]
        )
        self.assertEqual(code, 0)
        self.assertTrue(sorted(self.root.glob("style-submission-*")))

    def test_the_next_steps_name_the_package_that_was_written(self):
        _code, out, _err = self.run_cli(["submit", "carousel", "test-style"])
        pkg = self.package()
        self.assertIn(str(pkg), out)
        self.assertIn("PR-DESCRIPTION.md", out)


if __name__ == "__main__":
    unittest.main()
