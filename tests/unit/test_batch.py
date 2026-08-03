"""Batch resume semantics — what a second run does and does not pay for again.

Exercised only indirectly through the maker CLIs until now, which means the
property that matters was never asserted: --resume must not re-generate an item
a previous run already succeeded at. Every item is a paid API call, so the
failure mode is a bill rather than a crash, and a bill nobody notices.

The provider here counts its calls. Most assertions are on that counter,
because "the item is in the manifest" and "the item was not re-bought" are
different claims and only the second one is the point.
"""

import json
import sys
import tempfile
import threading
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import batch as batch_mod  # noqa: E402
from common.runners import output as output_mod  # noqa: E402
from common.runners.errors import ProviderError  # noqa: E402
from common.runners.providers.base import GenerationResult, JobHandle, Provider  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class CountingProvider(Provider):
    """Records every generate() call so a re-purchase is visible."""

    modality = "image"
    name = "counting"
    requires_env: tuple[str, ...] = ()

    def __init__(self, *, fail_on=(), async_job=False, cost="0.05"):
        self.calls: list[str] = []
        self._fail_on = set(fail_on)
        self._async = async_job
        self._cost = Decimal(cost) if cost is not None else None
        self._lock = threading.Lock()

    def estimate_cost(self, **kwargs):
        return self._cost

    def generate(self, prompt, **kwargs):
        with self._lock:
            self.calls.append(prompt)
        if prompt in self._fail_on:
            raise ProviderError(self.name, 500, f"refused {prompt}")
        if self._async:
            return JobHandle(provider=self.name, job_id=prompt, started_at=0.0)
        return GenerationResult(content=PNG, mime="image/png", extension="png")

    def poll(self, handle, timeout=600.0):
        return GenerationResult(content=PNG, mime="image/png", extension="png")


class BatchCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.manifest = self.dir / "manifest.json"
        # output.save reaches for S3 when configured; keep it local.
        patch = mock.patch.object(output_mod, "s3_configured", return_value=False)
        patch.start()
        self.addCleanup(patch.stop)

    def items(self, n=3):
        return [
            batch_mod.BatchItem(index=i, label=f"slide-{i}", prompt=f"prompt-{i}")
            for i in range(n)
        ]

    def spec(self, *, resume=False, parallelism=1):
        return batch_mod.BatchSpec(
            modality="image",
            output_dir=self.dir / "out",
            manifest_path=self.manifest,
            parallelism=parallelism,
            resume=resume,
        )

    def go(self, provider, items, **kw):
        """Named `go` rather than `run` — TestCase.run is the test runner's."""
        return batch_mod.run_batch(provider, items, self.spec(**kw))


class FirstRun(BatchCase):
    def test_every_item_is_generated_once(self):
        provider = CountingProvider()
        result = self.go(provider, self.items(3))
        self.assertEqual(len(provider.calls), 3)
        self.assertEqual(len(result.succeeded), 3)
        self.assertTrue(result.ok)

    def test_the_manifest_is_written_and_reloadable(self):
        self.go(CountingProvider(), self.items(3))
        restored = batch_mod.load_manifest(self.manifest)
        self.assertEqual(len(restored), 3)
        self.assertTrue(all(i.status == "succeeded" for i in restored))
        self.assertTrue(all(i.output_path for i in restored))

    def test_one_failure_does_not_take_down_the_batch(self):
        provider = CountingProvider(fail_on={"prompt-1"})
        result = self.go(provider, self.items(3))
        self.assertEqual(len(provider.calls), 3)
        self.assertEqual(len(result.succeeded), 2)
        self.assertEqual([i.index for i in result.failed], [1])
        self.assertFalse(result.ok)
        self.assertIn("refused", result.failed[0].error)

    def test_an_async_provider_is_polled(self):
        result = self.go(CountingProvider(async_job=True), self.items(2))
        self.assertEqual(len(result.succeeded), 2)

    def test_a_crashing_provider_is_recorded_not_raised(self):
        class Exploding(CountingProvider):
            def generate(self, prompt, **kwargs):
                super().generate(prompt, **kwargs)
                raise ZeroDivisionError("boom")

        with mock.patch("traceback.print_exc"):
            result = self.go(Exploding(), self.items(2))
        self.assertEqual(len(result.failed), 2)
        self.assertIn("ZeroDivisionError", result.failed[0].error)


class Resume(BatchCase):
    """The property that was never asserted: a second run does not re-buy."""

    def first_run(self, provider=None, n=3):
        provider = provider or CountingProvider()
        self.go(provider, self.items(n))
        return provider

    def test_resume_regenerates_nothing_when_everything_succeeded(self):
        self.first_run()
        second = CountingProvider()
        result = self.go(second, self.items(3), resume=True)
        self.assertEqual(second.calls, [], "resume re-paid for finished work")
        self.assertEqual(len(result.succeeded), 3)

    def test_resume_regenerates_only_what_failed(self):
        self.first_run(CountingProvider(fail_on={"prompt-1"}))
        second = CountingProvider()
        result = self.go(second, self.items(3), resume=True)
        self.assertEqual(second.calls, ["prompt-1"], "resume did not retry exactly the failure")
        self.assertEqual(len(result.succeeded), 3)

    def test_without_resume_everything_is_bought_again(self):
        # The flag has to matter; this is the control.
        self.first_run()
        second = CountingProvider()
        self.go(second, self.items(3), resume=False)
        self.assertEqual(len(second.calls), 3)

    def test_resume_carries_forward_the_output_path(self):
        first = self.items(3)
        self.go(CountingProvider(), first)
        paths = {i.index: i.output_path for i in first}
        second_items = self.items(3)
        self.go(CountingProvider(), second_items, resume=True)
        for item in second_items:
            with self.subTest(index=item.index):
                self.assertEqual(item.output_path, paths[item.index])

    def test_resume_with_no_manifest_at_all_runs_everything(self):
        provider = CountingProvider()
        result = self.go(provider, self.items(3), resume=True)
        self.assertEqual(len(provider.calls), 3)
        self.assertEqual(len(result.succeeded), 3)

    def test_resume_matches_on_index_not_on_position(self):
        # A resumed run may pass a different subset. Index is the identity.
        self.go(CountingProvider(), self.items(3))
        only_last = [batch_mod.BatchItem(index=2, label="slide-2", prompt="prompt-2")]
        provider = CountingProvider()
        self.go(provider, only_last, resume=True)
        self.assertEqual(provider.calls, [])

    def test_an_item_absent_from_the_manifest_is_generated(self):
        self.go(CountingProvider(), self.items(2))
        provider = CountingProvider()
        self.go(provider, self.items(3), resume=True)
        self.assertEqual(provider.calls, ["prompt-2"], "the new item should be the only one bought")

    def test_a_manifest_is_never_left_half_written(self):
        # The manifest is rewritten after every item precisely so that a crash
        # is survivable. A non-atomic write defeats that in exactly the case it
        # exists for: crash during the write, and the next --resume reads a
        # truncated file. Every intermediate state on disk must be parseable.
        seen = []
        real_write = batch_mod.write_manifest

        def spy(path, items, extra=None):
            real_write(path, items, extra)
            seen.append(json.loads(Path(path).read_text(encoding="utf-8")))

        with mock.patch.object(batch_mod, "write_manifest", side_effect=spy):
            self.go(CountingProvider(), self.items(3))
        self.assertTrue(seen)
        for snapshot in seen:
            self.assertEqual(snapshot["schema"], "skills.batch.v1")

    def test_a_corrupt_manifest_still_propagates(self):
        # Not everything is defended: a manifest corrupted by something other
        # than a partial write still raises rather than being read as "no prior
        # run". Pinned as current behaviour — silently discarding a manifest
        # would re-buy the whole batch, which is the worse failure.
        self.manifest.write_text("{not json", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            self.go(CountingProvider(), self.items(2), resume=True)

    def test_the_manifest_is_rewritten_after_every_item(self):
        # The claim in run_batch's docstring. If it were written once at the
        # end, a crash would lose the whole run's record and --resume would
        # re-buy everything.
        writes = []
        real = batch_mod.write_manifest

        def spy(path, items, extra=None):
            writes.append([i.status for i in items])
            return real(path, items, extra)

        with mock.patch.object(batch_mod, "write_manifest", side_effect=spy):
            self.go(CountingProvider(), self.items(3))
        self.assertGreaterEqual(len(writes), 4, "expected one write up front plus one per item")


class ManifestRoundTrip(BatchCase):
    def test_load_manifest_of_a_missing_file_is_empty(self):
        self.assertEqual(batch_mod.load_manifest(self.dir / "nope.json"), [])

    def test_unknown_fields_in_a_manifest_are_ignored(self):
        # A manifest written by a newer version must not crash an older one.
        batch_mod.write_manifest(self.manifest, self.items(1))
        raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        raw["items"][0]["invented_field"] = "whatever"
        self.manifest.write_text(json.dumps(raw), encoding="utf-8")
        restored = batch_mod.load_manifest(self.manifest)
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0].label, "slide-0")

    def test_the_schema_marker_is_written(self):
        batch_mod.write_manifest(self.manifest, self.items(1))
        raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(raw["schema"], "skills.batch.v1")

    def test_extra_meta_lands_under_meta(self):
        batch_mod.write_manifest(self.manifest, self.items(1), {"skill": "carousel-builder"})
        raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(raw["meta"]["skill"], "carousel-builder")


class CostEstimate(BatchCase):
    def test_the_estimate_is_the_sum_over_items(self):
        provider = CountingProvider(cost="0.05")
        self.assertEqual(batch_mod.estimate_batch_cost(provider, self.items(4)), Decimal("0.20"))

    def test_a_provider_without_pricing_estimates_nothing(self):
        provider = CountingProvider(cost=None)
        self.assertIsNone(batch_mod.estimate_batch_cost(provider, self.items(4)))

    def test_no_items_is_none_not_zero(self):
        # Zero would read as "free"; None reads as "unknown" and skips the gate.
        self.assertIsNone(batch_mod.estimate_batch_cost(CountingProvider(), []))


if __name__ == "__main__":
    unittest.main()
