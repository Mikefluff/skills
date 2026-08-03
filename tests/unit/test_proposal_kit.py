"""Unit tests for common/runners/proposal_kit.py photo generation.

generate_photo() is wrapped in a bare `except Exception: return False` — it is a
best-effort enrichment step and must never take down a proposal build. That also
means a mistake inside it is invisible: the caller sees "no photo" whether the
provider declined, the key was missing, or the code raised TypeError.

So the async path is tested directly.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import proposal_kit  # noqa: E402
from common.runners.providers.base import GenerationResult, JobHandle, Provider  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class SyncProvider(Provider):
    name = "fake-sync"
    modality = "image"
    requires_env: tuple[str, ...] = ()

    def generate(self, prompt, **kwargs):
        return GenerationResult(content=PNG, mime="image/png", extension="png")


class AsyncProvider(Provider):
    """Imagen and Nano Banana can answer with a JobHandle instead of an image."""

    name = "fake-async"
    modality = "image"
    requires_env: tuple[str, ...] = ()

    def __init__(self):
        self.polled = []

    def generate(self, prompt, **kwargs):
        return JobHandle(provider=self.name, job_id="job-1", started_at=0.0)

    def poll(self, handle, timeout=600.0):
        self.polled.append((handle.job_id, timeout))
        return GenerationResult(content=PNG, mime="image/png", extension="png")


class GeneratePhoto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name) / "img" / "vip-table.png"
        self.addCleanup(self._tmp.cleanup)

    def run_with(self, provider):
        with mock.patch.object(proposal_kit, "_pick_image_provider", return_value=provider):
            return proposal_kit.generate_photo("a VIP table", {"accent": "#ff0055"}, self.out)

    def test_sync_provider_writes_the_image(self):
        self.assertTrue(self.run_with(SyncProvider()))
        self.assertEqual(self.out.read_bytes(), PNG)

    def test_async_provider_is_polled_to_completion(self):
        # This is the regression: the JobHandle branch called the module-level
        # poll_until() with a provider where a zero-argument check callable was
        # expected. It raised TypeError, the bare except swallowed it, and every
        # async image provider silently produced no photo at all.
        provider = AsyncProvider()
        self.assertTrue(self.run_with(provider))
        self.assertEqual(self.out.read_bytes(), PNG)
        self.assertEqual(provider.polled, [("job-1", 180)])

    def test_no_configured_provider_returns_false_without_writing(self):
        self.assertFalse(self.run_with(None))
        self.assertFalse(self.out.exists())

    def test_provider_failure_is_swallowed(self):
        # A proposal build must survive a dead image endpoint.
        broken = SyncProvider()
        broken.generate = mock.Mock(side_effect=RuntimeError("vendor down"))
        self.assertFalse(self.run_with(broken))
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
