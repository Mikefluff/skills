"""The proposal CLI, run rather than imported.

Gate 14 proves this module imports. It does not execute a line of main(), and
the paydown's decomposition of this exact file shipped `_run_kit` with an
unbound name — caught by running the command, invisible to the whole suite.

So both output modes are driven end to end, and the assertions are on the
manifests and the files on disk, because that is the contract: a kit is a
directory an orchestrator reads, and a --quick run is a document a client
opens. An exit code of 0 over an empty directory would satisfy neither.

No network: the brand scrape, the screenshot, the asset download, the PDF
renderer and the image provider are all patched out. Each patch is also
asserted somewhere as a behaviour — "no headless browser" is a supported state
of the world, not just a way to keep the test offline.
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.proposal import brand as brand_mod  # noqa: E402
from common.runners.proposal import kit as kit_mod  # noqa: E402
from common.runners.cli import proposal as cli  # noqa: E402

OFFER = """\
Client: Acme Events
Phone: +66 812 345 678
Date: 12.09.2026
Event: Wedding
Manager: Dasha

Order:
1. Stage truss 6x4 m — 45 000 THB
2. LED screen 3x2 m - 78,500 THB
3. Sound system x2 — 120 000 THB

Total: 243 500 THB

Catalogue: https://shop.example.com/catalogue/lighting
"""

# An offer whose stated total disagrees with its items, for the warning paths.
BROKEN_OFFER = OFFER.replace("Total: 243 500 THB", "Total: 200 000 THB")

BRAND = {
    "url": "https://acme.example.com", "ok": True,
    "name": "Acme Staging", "tagline": "Мы строим сцены",
    "accent": "#F2AA4C", "accent2": "#101820", "bg": "#ffffff", "text": "#111111",
    "is_dark": False, "font_heading": "Inter", "font_body": "Inter",
    "google_fonts_url": None, "logo_url": None, "hero_url": None,
}


class ProposalCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.out = self.dir / "out"

    def offer_file(self, text=OFFER) -> Path:
        p = self.dir / "offer.txt"
        p.write_text(text, encoding="utf-8")
        return p

    def run_cli(self, argv_tail, *, screenshot=True, pdf=True, stdin=None, brand=None):
        """Run main() in-process. Returns (exit_code, stdout, stderr).

        The fakes are faithful, not merely typed: a screenshot that reports
        success writes a file, and so does a PDF. The first draft returned True
        without writing, and the manifest tests caught it — which is the whole
        point of asserting that every file a manifest lists is on disk.
        """
        argv = ["common.runners.cli.proposal", *argv_tail]
        out, err = io.StringIO(), io.StringIO()

        def fake_screenshot(url, dest):
            if not screenshot:
                return False
            Path(dest).write_bytes(b"\x89PNG\r\n\x1a\n")
            return True

        def fake_pdf(src, dest, **kwargs):
            if not pdf:
                return False
            Path(dest).write_bytes(b"%PDF-1.4\n")
            return True

        patches = [
            mock.patch.object(sys, "argv", argv),
            # Every door to the network, held shut.
            mock.patch.object(brand_mod, "extract", return_value=dict(brand or BRAND)),
            mock.patch.object(brand_mod, "enrich_items", return_value=0),
            mock.patch.object(kit_mod, "capture_screenshot", side_effect=fake_screenshot),
            mock.patch.object(kit_mod, "download_asset", return_value=None),
            mock.patch.object(kit_mod, "print_pdf", side_effect=fake_pdf),
            mock.patch.object(kit_mod, "_pick_image_provider", return_value=None),
        ]
        if stdin is not None:
            patches.append(mock.patch.object(sys, "stdin", io.StringIO(stdin)))
        with redirect_stdout(out), redirect_stderr(err):
            for p in patches:
                p.start()
            try:
                code = cli.main()
            except SystemExit as exc:  # argparse and _read_offer both use it
                code = exc.code
            finally:
                for p in reversed(patches):
                    p.stop()
        return code, out.getvalue(), err.getvalue()

    def manifest(self) -> dict:
        return json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))


class ExitCodes(ProposalCase):
    def test_parse_only_prints_json_and_stops(self):
        code, out, _err = self.run_cli(
            ["--offer", str(self.offer_file()), "--parse-only", "--no-brand"]
        )
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual(len(plan["items"]), 3)
        self.assertEqual(plan["client"]["name"], "Acme Events")
        self.assertFalse(self.out.exists(), "--parse-only must not write anything")

    def test_a_missing_offer_file_is_two(self):
        code, _out, err = self.run_cli(
            ["--offer", str(self.dir / "nope.txt"), "--no-brand", "--parse-only"]
        )
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_offer_from_stdin(self):
        code, out, _err = self.run_cli(
            ["--offer", "-", "--parse-only", "--no-brand"], stdin=OFFER
        )
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)["items"]), 3)

    def test_offer_text_inline(self):
        code, out, _err = self.run_cli(
            ["--offer-text", OFFER, "--parse-only", "--no-brand"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)["items"]), 3)

    def test_check_is_zero_when_requests_is_importable(self):
        code, _out, err = self.run_cli(["--check"])
        self.assertEqual(code, 0)
        self.assertIn("requests: OK", err)

    def test_check_with_an_unreachable_brand_is_two(self):
        code, _out, err = self.run_cli(
            ["--check", "--brand-url", "https://down.example.com"], brand={"ok": False}
        )
        self.assertEqual(code, 2)
        self.assertIn("UNREACHABLE", err)

    def test_pdf_from_a_missing_file_is_two(self):
        code, _out, err = self.run_cli(["--pdf-from", str(self.dir / "ghost.html")])
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_pdf_from_without_a_renderer_is_one_not_zero(self):
        src = self.dir / "authored.html"
        src.write_text("<!doctype html><html></html>", encoding="utf-8")
        code, _out, err = self.run_cli(["--pdf-from", str(src)], pdf=False)
        self.assertEqual(code, 1, "a PDF that was not produced must not report success")
        self.assertIn("Save as PDF", err)


class KitMode(ProposalCase):
    """The default mode: a directory an orchestrator reads."""

    def run_kit(self, extra=(), **kw):
        return self.run_cli(
            [
                "--offer", str(self.offer_file(kw.pop("offer", OFFER))),
                "--output", str(self.out),
                "--no-thumbnails", "--no-gen-photos", "--brand-url", "https://acme.example.com",
                *extra,
            ],
            **kw,
        )

    def test_kit_runs_and_writes_every_file_it_lists(self):
        code, out, _err = self.run_kit()
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), str(self.out), "the output dir goes to stdout")
        manifest = self.manifest()
        self.assertEqual(manifest["mode"], "kit")
        for name in manifest["files"]:
            with self.subTest(file=name):
                self.assertTrue((self.out / name).is_file(), f"{name} listed but not written")

    def test_the_brief_is_written_and_is_not_empty(self):
        self.run_kit()
        brief = (self.out / "BRIEF.md").read_text(encoding="utf-8")
        self.assertTrue(brief.startswith("# Proposal authoring brief"))
        self.assertIn("Acme Staging", brief)

    def test_the_manifest_carries_the_offer_arithmetic(self):
        self.run_kit()
        manifest = self.manifest()
        self.assertEqual(manifest["item_count"], 3)
        self.assertEqual(manifest["currency"], "THB")
        self.assertEqual(manifest["subtotal_computed"], 243500)
        self.assertFalse(manifest["total_mismatch"])

    def test_a_mismatched_total_reaches_the_manifest_and_stderr(self):
        _code, _out, err = self.run_kit(offer=BROKEN_OFFER)
        self.assertIn("⚠", err)
        manifest = self.manifest()
        self.assertTrue(manifest["total_mismatch"])
        self.assertEqual(manifest["total_stated"], 200000)
        self.assertEqual(manifest["subtotal_computed"], 243500)

    def test_no_screenshot_still_produces_a_kit(self):
        # A machine without a headless browser is a supported state, not a
        # failure — the kit ships without site.png and says so.
        code, _out, err = self.run_kit(screenshot=False)
        self.assertEqual(code, 0)
        self.assertIn("no headless browser", err)
        manifest = self.manifest()
        self.assertFalse(manifest["screenshot"])
        self.assertNotIn("site.png", manifest["files"])

    def test_the_screenshot_is_listed_only_when_it_was_taken(self):
        self.run_kit(screenshot=True)
        self.assertIn("site.png", self.manifest()["files"])

    def test_brand_and_offer_json_round_trip(self):
        self.run_kit()
        brand = json.loads((self.out / "brand.json").read_text(encoding="utf-8"))
        offer = json.loads((self.out / "offer.json").read_text(encoding="utf-8"))
        self.assertEqual(brand["name"], "Acme Staging")
        self.assertEqual(len(offer["items"]), 3)


class QuickMode(ProposalCase):
    """--quick: a document a client opens, no LLM in the loop."""

    def run_quick(self, extra=(), **kw):
        return self.run_cli(
            [
                "--offer", str(self.offer_file()),
                "--output", str(self.out),
                "--quick", "--no-thumbnails", "--no-gen-photos", "--no-brand",
                *extra,
            ],
            **kw,
        )

    def test_quick_writes_a_document_and_a_manifest(self):
        code, out, _err = self.run_quick()
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), str(self.out))
        html = (self.out / "proposal.html").read_text(encoding="utf-8")
        self.assertIn("</html>", html)
        self.assertIn("Acme Events", html)
        self.assertEqual(self.manifest()["mode"], "quick")

    def test_every_file_the_quick_manifest_lists_exists(self):
        self.run_quick()
        for name in self.manifest()["files"]:
            with self.subTest(file=name):
                self.assertTrue((self.out / name).is_file(), f"{name} listed but not written")

    def test_the_template_choice_is_recorded(self):
        self.run_quick(["--template", "invoice"])
        self.assertEqual(self.manifest()["template"], "invoice")

    def test_pdf_is_listed_only_when_one_was_rendered(self):
        self.run_quick(["--pdf"], pdf=False)
        manifest = self.manifest()
        self.assertNotIn("proposal.pdf", manifest["files"])

    def test_a_rendered_pdf_is_listed(self):
        # _run_quick stat()s the PDF to report its size, so a fake that returns
        # True without writing crashes here rather than lying.
        code, _out, err = self.run_quick(["--pdf"], pdf=True)
        self.assertEqual(code, 0)
        self.assertIn("proposal.pdf", self.manifest()["files"])
        self.assertTrue((self.out / "proposal.pdf").is_file())
        self.assertIn("PDF rendered", err)

    def test_currency_override_reaches_the_document(self):
        self.run_quick(["--currency", "usd"])
        self.assertEqual(self.manifest()["currency"], "USD")

    def test_accent_override_reaches_the_stylesheet(self):
        self.run_quick(["--accent", "#FF00AA"])
        html = (self.out / "proposal.html").read_text(encoding="utf-8")
        self.assertIn("#FF00AA", html)


class BothModesAgree(ProposalCase):
    """The fields _manifest_base promises are in both manifests."""

    SHARED = (
        "skill", "slug", "lang", "brand_url", "brand_ok", "accent", "font",
        "item_count", "currency", "subtotal_computed", "total_stated",
        "total_mismatch", "price_outliers", "thumbnails", "mode", "files",
    )

    def test_both_manifests_carry_the_shared_fields(self):
        for mode in ("kit", "quick"):
            with self.subTest(mode=mode):
                out = self.dir / f"out-{mode}"
                extra = ["--quick"] if mode == "quick" else []
                self.run_cli(
                    [
                        "--offer", str(self.offer_file()), "--output", str(out),
                        "--no-thumbnails", "--no-gen-photos", "--no-brand", *extra,
                    ]
                )
                manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
                for field in self.SHARED:
                    self.assertIn(field, manifest, f"{mode} manifest is missing {field}")
                self.assertEqual(manifest["mode"], mode)
                self.assertEqual(manifest["skill"], "proposal-maker")


if __name__ == "__main__":
    unittest.main()
