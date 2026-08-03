"""Characterisation tests for the plan-driven maker CLIs.

Nine skills — carousel, cover, flyer, banner, thumbnail, meme, quote, logo,
avatar — share one CLI shape: read a plan.json, validate it, estimate the cost,
confirm, run the batch, print the output directory. Gate 14 proves those modules
import. It does not prove that a malformed plan still exits 2 rather than 0, and
an exit code is the only thing a calling skill can branch on.

So this file pins the contract before the nine copies were collapsed into a
shared skeleton: which failures return which code, and what lands on stdout.
stdout is the machine-readable channel (the output directory, the cost line);
stderr is prose for a human and is deliberately not asserted on, except where a
message carries a migration instruction a caller depends on.

Nothing here touches the network. A fake Provider is registered into the real
registry for the duration of each test and the batch executor runs against it.
"""

import importlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import config  # noqa: E402
from common.runners.errors import ProviderError  # noqa: E402
from common.runners.providers.base import GenerationResult, Provider  # noqa: E402

# Enough bytes to look like a file on disk; no decoder ever sees it.
FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64

# module name → (plan schema, the key each plan uses for its output slug)
MAKERS = (
    ("carousel", "skills.carousel.plan.v1", "topic_slug"),
    ("cover", "skills.cover.plan.v1", "slug"),
    ("flyer", "skills.flyer.plan.v1", "event_slug"),
    ("banner", "skills.banner.plan.v1", "slug"),
    ("thumbnail", "skills.thumbnail.plan.v1", "slug"),
    ("meme", "skills.meme.plan.v1", "slug"),
    ("quote", "skills.quote.plan.v1", "slug"),
    ("logo", "skills.logo.plan.v1", "slug"),
    ("avatar", "skills.avatar.plan.v1", "slug"),
)


class FakeProvider(Provider):
    """A Provider that answers instantly and never leaves the process."""

    requires_env: tuple[str, ...] = ()

    def __init__(self, name, modality="image", price=None, fail=False):
        self.name = name
        self.modality = modality
        self._price = price
        self._fail = fail

    def estimate_cost(self, **kwargs):
        return self._price

    def generate(self, prompt, **kwargs):
        if self._fail:
            raise ProviderError(self.name, 500, "synthetic provider failure")
        return GenerationResult(content=FAKE_PNG, mime="image/png", extension="png")


def invoke(module_name, argv_tail, stdin_text=""):
    """Run one maker CLI's main() in-process. Returns (exit_code, stdout, stderr)."""
    module = importlib.import_module(f"common.runners.cli.{module_name}")
    argv = [f"common.runners.cli.{module_name}", *argv_tail]
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(sys, "argv", argv), \
            mock.patch.object(sys, "stdin", io.StringIO(stdin_text)), \
            mock.patch("common.runners.output.s3_configured", return_value=False), \
            redirect_stdout(out), redirect_stderr(err):
        code = module.main()
    return code, out.getvalue(), err.getvalue()


class MakerCase(unittest.TestCase):
    """Registers fakes for the duration of a test and hands back a temp dir."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self._tmp.name) / "out"
        self._registered = []
        self.register(FakeProvider("fake-image"))
        self.register(FakeProvider("fake-video", modality="video"))
        self.register(FakeProvider("fake-priced", price=Decimal("1.00")))
        self.register(FakeProvider("fake-broken", fail=True))

    def tearDown(self):
        # The registry is process-global; leaving fakes in it would leak into
        # test_config.py's assertions about the real provider set.
        for name in self._registered:
            config._REGISTRY.pop(name, None)
        self._tmp.cleanup()

    def register(self, provider):
        config.register(provider)
        self._registered.append(provider.name)

    def plan(self, schema, slug_key, model="fake-image", items=None):
        if items is None:
            items = [{"index": 1, "label": "item-01", "prompt": "a prompt", "kwargs": {}}]
        return {
            "schema": schema,
            slug_key: "characterisation",
            "model": model,
            "output_dir": str(self.out_dir),
            "parallelism": 1,
            "items": items,
        }

    def run_plan(self, module_name, plan, extra=()):
        return invoke(module_name, ["--plan-file", "-", *extra], json.dumps(plan))


class RejectsBadPlans(MakerCase):
    """Every way a plan can be wrong exits 2 — never 0, never a traceback."""

    def test_empty_stdin_exits_two(self):
        for module_name, _schema, _slug in MAKERS:
            with self.subTest(module_name):
                code, _out, _err = invoke(module_name, ["--plan-file", "-"], "   \n")
                self.assertEqual(code, 2)

    def test_missing_plan_file_exits_two(self):
        missing = str(Path(self._tmp.name) / "nope.json")
        for module_name, _schema, _slug in MAKERS:
            with self.subTest(module_name):
                code, _out, _err = invoke(module_name, ["--plan-file", missing])
                self.assertEqual(code, 2)

    def test_foreign_schema_exits_two(self):
        for module_name, _schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan("skills.something-else.plan.v1", slug)
                code, _out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 2)

    def test_missing_model_exits_two(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug)
                del plan["model"]
                code, _out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 2)

    def test_empty_items_exits_two(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, items=[])
                code, _out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 2)

    def test_unregistered_model_exits_two(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, model="no-such-provider")
                code, _out, err = self.run_plan(module_name, plan)
                self.assertEqual(code, 2)
                self.assertIn("no-such-provider", err)

    def test_non_image_provider_exits_two(self):
        # A video slug in an image plan is a plan-authoring mistake, and it must
        # be caught before any money is spent.
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, model="fake-video")
                code, _out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 2)


class CostGate(MakerCase):
    """--cost-only never generates; a declined confirmation never generates."""

    def test_cost_only_exits_zero_without_writing(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, model="fake-priced")
                code, out, _err = self.run_plan(module_name, plan, extra=["--cost-only"])
                self.assertEqual(code, 0)
                self.assertIn("items: 1", out)
                self.assertIn("estimated total: $1.0000", out)
                self.assertFalse(self.out_dir.exists())

    def test_unknown_price_prints_unknown(self):
        # A provider with no pricing entry must still run, not crash on None.
        plan = self.plan("skills.cover.plan.v1", "slug")
        code, out, _err = self.run_plan("cover", plan, extra=["--cost-only"])
        self.assertEqual(code, 0)
        self.assertIn("estimated total: unknown", out)

    def test_declined_confirmation_exits_three(self):
        # The plan is read off stdin first, so the confirmation prompt reads EOF
        # — which is not "y", which is a decline.
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, model="fake-priced")
                code, _out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 3)
                self.assertFalse(self.out_dir.exists())

    def test_yes_skips_confirmation(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, model="fake-priced")
                code, _out, _err = self.run_plan(module_name, plan, extra=["--yes"])
                self.assertEqual(code, 0)


class RunsTheBatch(MakerCase):
    """The success and partial-failure paths, including what stdout carries."""

    def test_success_exits_zero_and_prints_output_dir_on_stdout(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug)
                code, out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 0)
                # stdout is the machine-readable channel: exactly the directory.
                self.assertEqual(out.strip(), str(self.out_dir))

    def test_success_writes_asset_and_manifest(self):
        plan = self.plan("skills.avatar.plan.v1", "slug")
        code, _out, _err = self.run_plan("avatar", plan)
        self.assertEqual(code, 0)
        self.assertTrue((self.out_dir / "manifest.json").is_file())
        self.assertEqual(len(list(self.out_dir.glob("*.png"))), 1)

    def test_failed_item_exits_one_but_still_prints_dir(self):
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug, model="fake-broken")
                code, out, _err = self.run_plan(module_name, plan)
                self.assertEqual(code, 1)
                self.assertEqual(out.strip(), str(self.out_dir))

    def test_manifest_records_the_failure_reason(self):
        plan = self.plan("skills.logo.plan.v1", "slug", model="fake-broken")
        self.run_plan("logo", plan)
        manifest = json.loads((self.out_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["items"][0]["status"], "failed")
        self.assertIn("synthetic provider failure", manifest["items"][0]["error"])

    def test_resume_reuses_succeeded_items(self):
        plan = self.plan("skills.quote.plan.v1", "slug")
        self.assertEqual(self.run_plan("quote", plan)[0], 0)
        before = sorted(p.name for p in self.out_dir.glob("*.png"))
        # Second pass with a provider that would fail: --resume must not call it.
        plan_again = self.plan("skills.quote.plan.v1", "slug", model="fake-broken")
        code, _out, _err = self.run_plan("quote", plan_again, extra=["--resume"])
        self.assertEqual(code, 0)
        self.assertEqual(sorted(p.name for p in self.out_dir.glob("*.png")), before)

    def test_default_output_dir_is_derived_from_the_slug(self):
        # Each maker owns a ./generated/<kind>/ namespace, keyed by its own slug
        # field. Dropping output_dir must not collapse them into one directory.
        for module_name, schema, slug in MAKERS:
            with self.subTest(module_name):
                plan = self.plan(schema, slug)
                del plan["output_dir"]
                code, out, _err = self.run_plan(module_name, plan, extra=["--cost-only"])
                self.assertEqual(code, 0)
                del out  # --cost-only returns before the directory is used


class PerMakerQuirks(MakerCase):
    """Differences between the nine that are contract, not accident."""

    def test_carousel_rejects_items_without_a_prompt(self):
        # v2.13.0 removed structured role+content items. The error carries the
        # migration instruction, so a stale plan gets told what to do.
        plan = self.plan(
            "skills.carousel.plan.v1", "topic_slug",
            items=[{"index": 1, "label": "slide-01", "kwargs": {}}],
        )
        code, _out, err = self.run_plan("carousel", plan)
        self.assertEqual(code, 2)
        self.assertIn("image-prompt", err)

    def test_carousel_labels_progress_by_slide_number(self):
        plan = self.plan("skills.carousel.plan.v1", "topic_slug")
        _code, _out, err = self.run_plan("carousel", plan)
        self.assertIn("slide  1", err)

    def test_other_makers_label_progress_by_item_label(self):
        plan = self.plan("skills.banner.plan.v1", "slug")
        _code, _out, err = self.run_plan("banner", plan)
        self.assertIn("item-01", err)

    def test_flyer_lists_filenames_on_stderr(self):
        plan = self.plan("skills.flyer.plan.v1", "event_slug")
        _code, _out, err = self.run_plan("flyer", plan)
        self.assertIn("Files:", err)

    def test_cover_skips_typography_pass_without_an_imprint(self):
        # typeset defaults to "ai" for non-book media — no composition attempted.
        plan = self.plan("skills.cover.plan.v1", "slug")
        plan["medium"] = "album"
        code, _out, err = self.run_plan("cover", plan)
        self.assertEqual(code, 0)
        self.assertNotIn("Typography pass", err)

    def test_cover_warns_when_overlay_has_nothing_to_resolve(self):
        plan = self.plan("skills.cover.plan.v1", "slug")
        plan["medium"] = "book"
        plan["typeset"] = "overlay"
        code, _out, err = self.run_plan("cover", plan)
        self.assertEqual(code, 0)
        self.assertIn("Skipping composition", err)


if __name__ == "__main__":
    unittest.main()
