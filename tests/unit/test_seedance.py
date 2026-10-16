"""Seedance requests, and the seam chain that feeds them.

The prompt names references by position — @Image1, @Audio1 — so the order the
provider puts them on the wire is part of the prompt's meaning. A reordering
would not error; it would lip-sync the character to the wrong clip or dress
him in the seam frame. These tests pin the order, the two vendor quirks that
are 400s rather than bad films (ratio with a first frame, frames on fal's
reference route), and the chain: segment N+1 receives the frame segment N was
cut on, as its last image reference, or does not run at all.
"""

import base64
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import batch as batch_mod  # noqa: E402
from common.runners.cli import _reel_seams, reel  # noqa: E402
from common.runners.errors import ProviderError, RunnerError  # noqa: E402
from common.runners.providers import seedance  # noqa: E402


class ArkBody(unittest.TestCase):
    def setUp(self):
        self.provider = seedance.Seedance25Provider()

    def test_references_keep_their_order_and_roles(self):
        body = self.provider.build_body("p", {
            "reference_images": ["https://x/hero.png", "https://x/seam.png"],
            "reference_audio": ["https://x/vo.wav"],
            "duration_seconds": 30,
            "aspect_ratio": "9:16",
        })
        roles = [(c["type"], c.get("role")) for c in body["content"]]
        self.assertEqual(roles, [
            ("text", None),
            ("image_url", "reference_image"),
            ("image_url", "reference_image"),
            ("audio_url", "reference_audio"),
        ])
        self.assertEqual(body["content"][2]["image_url"]["url"], "https://x/seam.png")
        self.assertEqual(body["model"], "dreamina-seedance-2-5-260628")
        self.assertEqual((body["duration"], body["ratio"]), (30, "9:16"))

    def test_first_frame_forces_adaptive_ratio(self):
        body = self.provider.build_body("p", {"first_frame": "https://x/f.png", "aspect_ratio": "9:16"})
        self.assertEqual(body["ratio"], "adaptive")

    def test_local_files_go_inline(self):
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "vo.wav"
            wav.write_bytes(b"RIFF")
            url = seedance.as_url(str(wav))
        self.assertTrue(url.startswith("data:audio/"))
        self.assertEqual(base64.b64decode(url.split(",", 1)[1]), b"RIFF")

    def test_missing_reference_is_an_error_not_a_string(self):
        with self.assertRaises(ProviderError):
            seedance.as_url("/nope/hero.png")


class Pricing(unittest.TestCase):
    def test_byteplus_bills_tokens_not_seconds(self):
        # 30 s × 720 × 1280 × 24 / 1024 = 648,000 tokens.
        self.assertEqual(seedance.ark_tokens(30, "720p", "9:16"), 648_000)

    def test_thirty_seconds_at_720p_is_about_seven_dollars(self):
        est = seedance.Seedance25Provider().estimate_cost(duration_seconds=30, resolution="720p", aspect_ratio="9:16")
        self.assertAlmostEqual(float(est), 6.93, places=2)

    def test_1080p_costs_more_than_720p(self):
        p = seedance.Seedance25Provider()
        self.assertGreater(p.estimate_cost(duration_seconds=30, resolution="1080p"),
                           p.estimate_cost(duration_seconds=30, resolution="720p"))


class OpenRouterRoute(unittest.TestCase):
    def setUp(self):
        from common.runners.providers import openrouter_video
        self.provider = openrouter_video.OpenRouterSeedance25Provider()

    def test_references_go_images_then_audio_in_one_list(self):
        body = self.provider.build_body("p", {
            "reference_images": ["https://x/hero.png"], "reference_audio": ["https://x/vo.mp3"],
            "duration_seconds": 30, "aspect_ratio": "9:16", "resolution": "720p",
        })
        self.assertEqual([r["type"] for r in body["input_references"]], ["image_url", "audio_url"])
        self.assertEqual(body["model"], "bytedance/seedance-2.5")
        self.assertEqual((body["duration"], body["resolution"]), (30, "720p"))
        self.assertNotIn("frame_images", body)

    def test_frames_with_references_are_refused(self):
        # OpenRouter would silently drop every reference — the voice included.
        with self.assertRaises(ProviderError):
            self.provider.build_body("p", {"first_frame": "https://x/f.png", "reference_images": ["https://x/h.png"]})

    def test_local_audio_is_never_made_public_unasked(self):
        # The vendor refuses inline audio; uploading the user's voice is opt-in.
        with tempfile.TemporaryDirectory() as tmp:
            take = Path(tmp) / "vo.wav"
            take.write_bytes(b"RIFF")
            with self.assertRaises(ProviderError):
                self.provider.build_body("p", {"reference_audio": [str(take)]})

    def test_priced_like_byteplus(self):
        est = self.provider.estimate_cost(duration_seconds=30, resolution="720p", aspect_ratio="9:16")
        self.assertAlmostEqual(float(est), 6.93, places=2)


class FalRoute(unittest.TestCase):
    def test_kwargs_map_to_fal_fields(self):
        provider = seedance.FalSeedance25Provider()
        with mock.patch("common.runners.providers.fal._FalBase.generate") as base:
            provider.generate("p", reference_images=["https://x/h.png"],
                              reference_audio=["https://x/a.wav"], duration_seconds=12)
        sent = base.call_args.kwargs
        self.assertEqual(sent["image_urls"], ["https://x/h.png"])
        self.assertEqual(sent["audio_urls"], ["https://x/a.wav"])
        self.assertIsNone(sent["video_urls"])
        self.assertEqual(sent["duration"], 12)

    def test_frames_are_refused_on_the_reference_route(self):
        with self.assertRaises(ProviderError):
            seedance.FalSeedance25Provider().generate("p", first_frame="https://x/f.png")


class SeamChain(unittest.TestCase):
    def job(self, tmp, continuity=None):
        plan = {
            "schema": "skills.reel.plan.v1",
            "video_provider": "seedance-2-5",
            "output_dir": str(tmp),
            "shots": [
                {"index": 1, "prompt": "a", "trim_seconds": 14.2,
                 "kwargs": {"duration_seconds": 15, "reference_images": ["hero.png"]}},
                {"index": 2, "prompt": "b", "trim_seconds": 13.1, "continue_from_previous": True,
                 "kwargs": {"duration_seconds": 14, "reference_images": ["hero.png"]}},
            ],
        }
        if continuity:
            plan["continuity"] = continuity
        return reel.prepare(plan)

    def test_seam_frame_is_cut_at_the_trim_and_appended_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.job(Path(tmp))
            first, second = sorted(job.shot_items, key=lambda i: i.index)
            first.status, first.output_path = "succeeded", str(Path(tmp) / "shots" / "01.mp4")
            with mock.patch.object(_reel_seams.ffmpeg_film, "extract_frame") as grab:
                reel.seam_hook(job)(second)
            self.assertEqual(grab.call_args.kwargs["at"], 14.2)
            refs = second.kwargs["reference_images"]
            self.assertEqual(refs[0], "hero.png")
            self.assertTrue(refs[-1].endswith("seam-01.png"))
            self.assertTrue(job.chained)

    def test_a_designed_seam_can_hand_over_an_earlier_frame(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.job(Path(tmp))
            job.plan["shots"][1]["seam_frame_at"] = 7.0
            first, second = sorted(job.shot_items, key=lambda i: i.index)
            first.status, first.output_path = "succeeded", "x.mp4"
            with mock.patch.object(_reel_seams.ffmpeg_film, "extract_frame") as grab:
                reel.seam_hook(job)(second)
            self.assertEqual(grab.call_args.kwargs["at"], 7.0)

    def test_first_frame_mode_uses_the_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.job(Path(tmp), continuity="first_frame")
            first, second = sorted(job.shot_items, key=lambda i: i.index)
            first.status, first.output_path = "succeeded", "x.mp4"
            with mock.patch.object(_reel_seams.ffmpeg_film, "extract_frame"):
                reel.seam_hook(job)(second)
            self.assertTrue(second.kwargs["first_frame"].endswith("seam-01.png"))
            self.assertEqual(second.kwargs["reference_images"], ["hero.png"])

    def test_no_predecessor_no_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.job(Path(tmp))
            first, second = sorted(job.shot_items, key=lambda i: i.index)
            first.status = "failed"
            with self.assertRaises(RunnerError):
                reel.seam_hook(job)(second)

    def test_a_failed_hook_fails_the_item_without_calling_the_vendor(self):
        provider = mock.Mock()
        item = batch_mod.BatchItem(index=2, label="seg-02", prompt="b")
        spec = batch_mod.BatchSpec(
            modality="video", output_dir=Path("/tmp"), manifest_path=Path("/tmp/m.json"),
            before_item=mock.Mock(side_effect=RunnerError("no frame")),
        )
        batch_mod._run_item(provider, item, spec)
        self.assertEqual(item.status, "failed")
        provider.generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()


class StoryboardRoute(unittest.TestCase):
    def test_frames_go_up_with_every_reference_in_order(self):
        from common.runners.providers import openrouter_image
        body = openrouter_image.OpenRouterNanoBananaProProvider().build_body(
            "still", {"reference_images": ["https://x/hero.jpg", "https://x/f01.jpg"], "aspect_ratio": "9:16"})
        parts = body["messages"][0]["content"]
        self.assertEqual([p["type"] for p in parts], ["image_url", "image_url", "text"])
        self.assertEqual(parts[1]["image_url"]["url"], "https://x/f01.jpg")
        self.assertEqual(body["image_config"], {"aspect_ratio": "9:16", "image_size": "2K"})
        self.assertIn("image", body["modalities"])

    def test_an_unchanged_frame_is_not_rerolled(self):
        from common.runners.cli import reel_board
        frame = {"id": "f01", "prompt": "p", "shot_spec": "s"}
        self.assertEqual(reel_board._spec_hash(frame, "hat"), reel_board._spec_hash(dict(frame), "hat"))
        self.assertNotEqual(reel_board._spec_hash(frame, "hat"), reel_board._spec_hash({**frame, "prompt": "q"}, "hat"))


class BoardToShots(unittest.TestCase):
    def test_each_shot_gets_its_own_frame_the_right_way(self):
        from common.runners.cli import reel_board
        plan = {"shots": [{"index": 1, "kwargs": {}}, {"index": 2, "lip_sync": True, "kwargs": {}}]}
        frames = [{"id": "f01", "shot": 1}, {"id": "f02", "shot": 2}]
        reel_board._attach(plan, frames, [Path("f01.jpg"), Path("f02.jpg")], "hero.jpg")
        silent, speaking = (s["kwargs"] for s in plan["shots"])
        self.assertEqual(silent, {"first_frame": "f01.jpg"})
        self.assertEqual(speaking, {"reference_images": ["hero.jpg", "f02.jpg"]})
