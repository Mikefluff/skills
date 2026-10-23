"""A job the vendor accepted but the run never saw finish is polled again on resume, not bought again."""

from __future__ import annotations

import tempfile
from pathlib import Path

from common.runners import batch
from common.runners.providers.base import GenerationResult, JobHandle


class _Flaky:
    name = "flaky"

    def __init__(self):
        self.submitted, self.polls = 0, 0

    def ensure_available(self):
        return None

    def generate(self, prompt, **kwargs):
        self.submitted += 1
        return JobHandle(provider="flaky", job_id=f"job{self.submitted}", started_at=0.0, poll_url="u")

    def poll(self, handle, timeout=600.0):
        self.polls += 1
        if self.polls == 1:
            from common.runners.errors import ProviderError
            raise ProviderError("flaky", None, "network error during poll")
        assert handle.job_id == "job1"
        return GenerationResult(content=b"x", mime="video/mp4", extension="mp4")


def test_a_timed_out_poll_is_resumed_on_the_same_job():
    out = Path(tempfile.mkdtemp())
    spec = batch.BatchSpec(modality="video", output_dir=out, manifest_path=out / "m.json", parallelism=1,
                           extension_hint="mp4")
    vendor = _Flaky()
    first = batch.run_batch(vendor, [batch.BatchItem(index=1, label="a", prompt="p")], spec)
    assert first.items[0].status == "failed" and first.items[0].pending_job["job_id"] == "job1"
    again = batch.run_batch(vendor, [batch.BatchItem(index=1, label="a", prompt="p")],
                            batch.BatchSpec(**{**spec.__dict__, "resume": True}))
    assert again.items[0].status == "succeeded" and vendor.submitted == 1
