"""The reel stitch pipeline, and the three places it degrades instead of aborting.

concat → music → captions → final.mp4. Everything after the concat is optional,
and the module's whole thesis is that losing the render because the last
optional step failed would throw away every second of generation that paid for
it — video is the most expensive thing this repo produces.

Nothing checked that it still degrades. A refactor that let one of those
`except Exception` blocks re-raise would turn a silent reel into no reel, and
the only signal would be a user losing a batch they paid for.

So each failure is injected and the assertion is that final.mp4 exists anyway,
with the right content and the reason on stderr. ffmpeg itself is faked — this
is about the pipeline's decisions, not about the codec.
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import batch as batch_mod  # noqa: E402
from common.runners import ffmpeg as ff_mod  # noqa: E402
from common.runners.cli import _reel_stitch as stitch_mod  # noqa: E402


class FakeShots:
    def __init__(self, items):
        self.succeeded = items


@dataclass
class Fakes:
    """The three ffmpeg calls, each overridable to make it fail.

    A bag rather than three keyword arguments because the quality gate counts
    parameters and was right to: run_stitch had grown to seven, which is the
    signature that stops being readable.
    """

    concat: Callable | None = None
    mix: Callable | None = None
    burn: Callable | None = None


class StitchCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def shot(self, index, marker=None):
        path = self.dir / "shots" / f"{index:02d}-shot.mp4"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(marker or f"shot-{index}".encode())
        item = batch_mod.BatchItem(index=index, label=f"shot-{index}", prompt="p")
        item.status = "succeeded"
        item.output_path = str(path)
        return item

    def job(self, *, captions=None, captions_enabled=False):
        plan = {"captions_enabled": captions_enabled, "captions": captions or []}
        return mock.Mock(plan=plan, output_dir=self.dir)

    def run_stitch(self, job, shots, music=None, *, found=True, fakes=Fakes()):
        """Drive stitch() with ffmpeg faked. Returns (code, stderr)."""
        probe = ff_mod.FfmpegProbe(found=found, binary="ffmpeg" if found else None)

        def default_concat(paths, dest, ffmpeg_bin="ffmpeg"):
            Path(dest).write_bytes(b"".join(Path(p).read_bytes() for p in paths))

        def default_mix(video, audio, dest, opts, ffmpeg_bin="ffmpeg"):
            Path(dest).write_bytes(Path(video).read_bytes() + b"+music")

        def default_burn(video, tuples, dest, ffmpeg_bin="ffmpeg"):
            Path(dest).write_bytes(Path(video).read_bytes() + b"+captions")

        err = io.StringIO()
        with mock.patch.object(ff_mod, "detect_ffmpeg", return_value=probe), \
                mock.patch.object(ff_mod, "concat_videos",
                                  side_effect=fakes.concat or default_concat), \
                mock.patch.object(ff_mod, "mix_audio_over_video",
                                  side_effect=fakes.mix or default_mix), \
                mock.patch.object(ff_mod, "burn_captions",
                                  side_effect=fakes.burn or default_burn), \
                redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = stitch_mod.stitch(job, FakeShots(shots), music)
        return code, err.getvalue()

    def music(self):
        path = self.dir / "music.mp3"
        path.write_bytes(b"music")
        return path

    @property
    def final(self) -> Path:
        return self.dir / "final.mp4"


class HappyPath(StitchCase):
    def test_two_shots_are_concatenated_and_finalised(self):
        code, _err = self.run_stitch(self.job(), [self.shot(0), self.shot(1)])
        self.assertEqual(code, 0)
        self.assertTrue(self.final.is_file())
        self.assertEqual(self.final.read_bytes(), b"shot-0shot-1")

    def test_a_single_shot_skips_concat_entirely(self):
        called = []

        def concat(paths, dest, ffmpeg_bin="ffmpeg"):
            called.append(paths)
            Path(dest).write_bytes(b"")

        code, _err = self.run_stitch(self.job(), [self.shot(0)], fakes=Fakes(concat=concat))
        self.assertEqual(code, 0)
        self.assertEqual(called, [], "one shot needs no concat")
        self.assertEqual(self.final.read_bytes(), b"shot-0")

    def test_shots_concat_in_plan_order_not_in_finish_order(self):
        # The bug this guards: sorting by filename concats by timestamp, which
        # is when each shot *finished*. With parallel shots or a --resume retry
        # that is simply the wrong order, and the reel plays scrambled.
        late_first = [self.shot(2), self.shot(0), self.shot(1)]
        code, _err = self.run_stitch(self.job(), late_first)
        self.assertEqual(code, 0)
        self.assertEqual(self.final.read_bytes(), b"shot-0shot-1shot-2")

    def test_music_and_captions_both_apply(self):
        job = self.job(captions_enabled=True, captions=[{"start": 0, "end": 1, "text": "привет"}])
        code, _err = self.run_stitch(job, [self.shot(0)], self.music())
        self.assertEqual(code, 0)
        self.assertEqual(self.final.read_bytes(), b"shot-0+music+captions")

    def test_no_intermediate_file_is_left_beside_the_final_one(self):
        # _finalize renames rather than copies so the dir does not carry two
        # identical multi-MB files.
        self.run_stitch(self.job(), [self.shot(0), self.shot(1)])
        leftovers = sorted(p.name for p in self.dir.glob("*.mp4"))
        self.assertEqual(leftovers, ["final.mp4"], f"intermediates left: {leftovers}")


class DegradationPoints(StitchCase):
    """The three places failure must not cost the render."""

    def boom(self, *args, **kwargs):
        raise RuntimeError("ffmpeg exploded")

    def test_a_failed_music_mix_leaves_a_silent_reel(self):
        code, err = self.run_stitch(
            self.job(), [self.shot(0)], self.music(), fakes=Fakes(mix=self.boom)
        )
        self.assertEqual(code, 0, "a failed optional step must not fail the run")
        self.assertTrue(self.final.is_file())
        self.assertEqual(self.final.read_bytes(), b"shot-0", "music was silently applied anyway")
        self.assertIn("music mix failed", err)
        self.assertIn("silent reel", err)

    def test_a_failed_caption_burn_leaves_an_uncaptioned_reel(self):
        job = self.job(captions_enabled=True, captions=[{"start": 0, "end": 1, "text": "hi"}])
        code, err = self.run_stitch(job, [self.shot(0)], fakes=Fakes(burn=self.boom))
        self.assertEqual(code, 0)
        self.assertTrue(self.final.is_file())
        self.assertEqual(self.final.read_bytes(), b"shot-0")
        self.assertIn("burn-captions failed", err)
        self.assertIn("uncaptioned reel", err)

    def test_both_optional_steps_failing_still_produces_the_reel(self):
        job = self.job(captions_enabled=True, captions=[{"start": 0, "end": 1, "text": "hi"}])
        code, err = self.run_stitch(
            job, [self.shot(0)], self.music(), fakes=Fakes(mix=self.boom, burn=self.boom)
        )
        self.assertEqual(code, 0)
        self.assertEqual(self.final.read_bytes(), b"shot-0")
        self.assertIn("music mix failed", err)
        self.assertIn("burn-captions failed", err)

    def test_malformed_captions_degrade_rather_than_crash(self):
        # The float() and the dict lookups are inside the try for a reason: a
        # caption the planner got wrong must not cost the render.
        job = self.job(captions_enabled=True, captions=[{"start": "abc", "text": "hi"}])
        code, err = self.run_stitch(job, [self.shot(0)])
        self.assertEqual(code, 0)
        self.assertTrue(self.final.is_file())
        self.assertIn("burn-captions failed", err)

    def test_missing_music_file_is_not_an_error(self):
        code, err = self.run_stitch(self.job(), [self.shot(0)], self.dir / "absent.mp3")
        self.assertEqual(code, 0)
        self.assertEqual(self.final.read_bytes(), b"shot-0")
        self.assertNotIn("failed", err)

    def test_captions_present_but_disabled_are_not_burned(self):
        job = self.job(captions_enabled=False, captions=[{"start": 0, "end": 1, "text": "hi"}])
        code, _err = self.run_stitch(job, [self.shot(0)])
        self.assertEqual(code, 0)
        self.assertEqual(self.final.read_bytes(), b"shot-0")

    def test_captions_enabled_but_empty_are_not_burned(self):
        job = self.job(captions_enabled=True, captions=[])
        code, _err = self.run_stitch(job, [self.shot(0)])
        self.assertEqual(self.final.read_bytes(), b"shot-0")


class HardFailures(StitchCase):
    """The two things that are NOT degraded, and must stay that way."""

    def test_a_failed_concat_is_exit_one(self):
        # Without a concat there is nothing to salvage — degrading here would
        # report success over no video at all.
        def boom(*a, **k):
            raise RuntimeError("concat exploded")

        code, err = self.run_stitch(self.job(), [self.shot(0), self.shot(1)], fakes=Fakes(concat=boom))
        self.assertEqual(code, 1)
        self.assertIn("concat failed", err)
        self.assertFalse(self.final.exists())

    def test_absent_ffmpeg_is_zero_because_the_components_were_still_paid_for(self):
        # Exit 0 with no final.mp4 is deliberate: the shots exist and cost
        # money, so this is "saved, not stitched", not a failed run.
        code, err = self.run_stitch(self.job(), [self.shot(0)], found=False)
        self.assertEqual(code, 0)
        self.assertFalse(self.final.exists())
        self.assertIn("ffmpeg not found", err)
        self.assertIn("stitch skipped", err)


if __name__ == "__main__":
    unittest.main()
