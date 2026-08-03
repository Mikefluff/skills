"""Unit tests for the publishing layer — Post, preflight, receipts, CLI parsing.

Publishing is the one irreversible thing this repo does, and preflight is the
gate in front of it. Every rule here exists so that a bad post is caught while
it is still a local dataclass rather than after it is visible to an audience.

Nothing in this file touches the network.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import receipts  # noqa: E402
from common.runners.cli import publish as publish_cli  # noqa: E402
from common.runners.publishers.base import Post, Publisher, PublishResult  # noqa: E402
from common.runners.publishers.instagram import InstagramPublisher  # noqa: E402
from common.runners.publishers.linkedin import LinkedInPublisher  # noqa: E402
from common.runners.publishers.telegram import TelegramPublisher  # noqa: E402
from common.runners.publishers.threads import ThreadsPublisher  # noqa: E402
from common.runners.publishers.tiktok import TikTokPublisher  # noqa: E402
from common.runners.publishers.x import XPublisher  # noqa: E402
from common.runners.publishers.youtube import YouTubePublisher  # noqa: E402


class DummyPublisher(Publisher):
    """Minimal publisher for exercising the generic rules in Publisher.preflight."""

    name = "dummy"
    supports = frozenset({"text", "image", "carousel"})
    supports_draft = True
    max_text_chars = 100
    max_hashtags = 3
    min_media = 0
    max_media = 2
    max_image_mb = 1.0

    def publish(self, post, *, draft=False):
        return PublishResult(platform=self.name, post_id="1", state="draft" if draft else "published")


class MediaCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def make(self, name, size=1024):
        p = self.dir / name
        p.write_bytes(b"x" * size)
        return p

    def blocks(self, violations):
        return [v for v in violations if v.severity == "block"]

    def fields(self, violations, severity=None):
        return [v.field for v in violations if severity is None or v.severity == severity]


class TestPostNormalisation(unittest.TestCase):
    def test_single_path_is_wrapped(self):
        self.assertEqual(Post(kind="image", media=Path("/a/b.png")).media, (Path("/a/b.png"),))

    def test_string_media_becomes_path(self):
        self.assertEqual(Post(kind="image", media="/a/b.png").media, (Path("/a/b.png"),))

    def test_list_of_strings_becomes_paths(self):
        post = Post(kind="carousel", media=["/a/1.png", "/a/2.png"])
        self.assertEqual(post.media, (Path("/a/1.png"), Path("/a/2.png")))

    def test_hashes_are_stripped_and_blanks_dropped(self):
        post = Post(kind="text", hashtags=["#smm", "  ", "автопостинг"])
        self.assertEqual(post.hashtags, ("smm", "автопостинг"))

    def test_rendered_text_appends_hashtags(self):
        post = Post(kind="text", text="Тело поста.", hashtags=["a", "b"])
        self.assertEqual(post.rendered_text(), "Тело поста.\n\n#a #b")

    def test_rendered_text_without_hashtags_is_untouched(self):
        self.assertEqual(Post(kind="text", text="Просто текст.").rendered_text(), "Просто текст.")

    def test_rendered_text_hashtags_only(self):
        self.assertEqual(Post(kind="text", hashtags=["a"]).rendered_text(), "#a")

    def test_alt_for_is_safe_past_the_end(self):
        post = Post(kind="carousel", alt_texts=["one"])
        self.assertEqual(post.alt_for(0), "one")
        self.assertEqual(post.alt_for(5), "")


class TestContentHash(MediaCase):
    def test_identical_posts_hash_alike(self):
        a = Post(kind="text", text="hello", hashtags=["x"])
        b = Post(kind="text", text="hello", hashtags=["x"])
        self.assertEqual(a.content_hash(), b.content_hash())

    def test_edited_caption_is_a_different_post(self):
        # The whole point of the receipt: fixing a typo and re-running must be
        # allowed through, while re-running the identical command must not.
        a = Post(kind="text", text="hello")
        b = Post(kind="text", text="hello!")
        self.assertNotEqual(a.content_hash(), b.content_hash())

    def test_whitespace_only_edits_do_not_count(self):
        a = Post(kind="text", text="hello")
        b = Post(kind="text", text="  hello  ")
        self.assertEqual(a.content_hash(), b.content_hash())

    def test_different_hashtags_change_the_hash(self):
        a = Post(kind="text", text="x", hashtags=["a"])
        b = Post(kind="text", text="x", hashtags=["b"])
        self.assertNotEqual(a.content_hash(), b.content_hash())

    def test_different_media_size_changes_the_hash(self):
        small = self.make("s.png", 10)
        post_a = Post(kind="image", media=[small])
        hash_a = post_a.content_hash()
        small.write_bytes(b"y" * 999)
        self.assertNotEqual(Post(kind="image", media=[small]).content_hash(), hash_a)

    def test_missing_media_still_hashes(self):
        # Must not raise — preflight reports the missing file, not content_hash.
        Post(kind="image", media=[self.dir / "nope.png"]).content_hash()


class TestGenericPreflight(MediaCase):
    def setUp(self):
        super().setUp()
        self.pub = DummyPublisher()

    def test_unsupported_kind_blocks(self):
        v = self.pub.preflight(Post(kind="video", media=[]))
        self.assertIn("kind", self.fields(self.blocks(v)))

    def test_text_over_limit_blocks(self):
        v = self.pub.preflight(Post(kind="text", text="я" * 101))
        self.assertIn("text", self.fields(self.blocks(v)))

    def test_hashtags_count_against_the_limit(self):
        # 90 chars of body plus "#a #b" tips it over 100.
        v = self.pub.preflight(Post(kind="text", text="я" * 96, hashtags=["a", "b"]))
        self.assertIn("text", self.fields(self.blocks(v)))

    def test_too_many_hashtags_warns_but_does_not_block(self):
        v = self.pub.preflight(Post(kind="text", text="ok", hashtags=["a", "b", "c", "d"]))
        self.assertEqual(self.blocks(v), [])
        self.assertIn("hashtags", self.fields(v, "warn"))

    def test_too_many_media_blocks(self):
        files = [self.make(f"{i}.png") for i in range(3)]
        v = self.pub.preflight(Post(kind="carousel", media=files))
        self.assertIn("media", self.fields(self.blocks(v)))

    def test_missing_file_blocks(self):
        v = self.pub.preflight(Post(kind="image", media=[self.dir / "ghost.png"]))
        self.assertTrue(any("not found" in x.message for x in self.blocks(v)))

    def test_empty_file_blocks(self):
        v = self.pub.preflight(Post(kind="image", media=[self.make("empty.png", 0)]))
        self.assertTrue(any("empty" in x.message for x in self.blocks(v)))

    def test_oversized_image_blocks(self):
        big = self.make("big.png", 2 * 1024 * 1024)
        v = self.pub.preflight(Post(kind="image", media=[big]))
        self.assertTrue(any("caps images" in x.message for x in self.blocks(v)))

    def test_unknown_extension_blocks(self):
        v = self.pub.preflight(Post(kind="image", media=[self.make("thing.psd")]))
        self.assertTrue(any("unrecognised" in x.message for x in self.blocks(v)))

    def test_missing_alt_text_warns_only(self):
        v = self.pub.preflight(Post(kind="image", media=[self.make("a.png")]))
        self.assertEqual(self.blocks(v), [])
        self.assertIn("alt_texts", self.fields(v, "warn"))

    def test_partial_alt_text_names_the_gap(self):
        # --alt is repeated per file, so describing the first slides and
        # forgetting the rest is likelier than omitting alt text entirely.
        files = [self.make(f"{i}.png") for i in range(2)]
        v = self.pub.preflight(Post(kind="carousel", media=files, text="ok", alt_texts=["only the first"]))
        warns = [x for x in v if x.field == "alt_texts"]
        self.assertEqual(len(warns), 1)
        self.assertIn("1 alt texts for 2 files", warns[0].message)
        self.assertIn("file 2", warns[0].message)

    def test_full_alt_text_does_not_warn(self):
        files = [self.make(f"{i}.png") for i in range(2)]
        v = self.pub.preflight(Post(kind="carousel", media=files, text="ok", alt_texts=["a", "b"]))
        self.assertEqual([x for x in v if x.field == "alt_texts"], [])

    def test_clean_post_has_no_findings(self):
        post = Post(kind="image", media=[self.make("a.png")], text="ok", alt_texts=["a chart"])
        self.assertEqual(self.pub.preflight(post), [])


class TestTelegramPreflight(MediaCase):
    def setUp(self):
        super().setUp()
        self.pub = TelegramPublisher()

    def test_long_text_is_fine_without_media(self):
        v = self.pub.preflight(Post(kind="text", text="я" * 2000))
        self.assertEqual(self.blocks(v), [])

    def test_same_text_blocks_once_media_is_attached(self):
        # 2000 chars is a legal message but an illegal caption. The rule that
        # catches this cannot live in max_text_chars — it depends on the kind.
        post = Post(kind="image", media=[self.make("a.png")], text="я" * 2000, alt_texts=["x"])
        blocks = self.blocks(self.pub.preflight(post))
        self.assertTrue(any("1024" in x.message for x in blocks))

    def test_text_over_the_message_limit_blocks(self):
        v = self.pub.preflight(Post(kind="text", text="я" * 5000))
        self.assertIn("text", self.fields(self.blocks(v)))

    def test_empty_text_post_blocks(self):
        v = self.pub.preflight(Post(kind="text", text="   "))
        self.assertIn("text", self.fields(self.blocks(v)))

    def test_album_of_one_blocks(self):
        post = Post(kind="carousel", media=[self.make("a.png")], alt_texts=["x"])
        self.assertTrue(any("at least 2" in x.message for x in self.blocks(self.pub.preflight(post))))

    def test_mixed_album_warns(self):
        post = Post(
            kind="carousel",
            media=[self.make("a.png"), self.make("b.mp4")],
            alt_texts=["x", "y"],
        )
        v = self.pub.preflight(post)
        self.assertEqual(self.blocks(v), [])
        self.assertIn("media", self.fields(v, "warn"))

    def test_eleven_slides_exceed_the_album_cap(self):
        files = [self.make(f"s{i}.png") for i in range(11)]
        post = Post(kind="carousel", media=files, alt_texts=["x"] * 11)
        self.assertTrue(any("at most 10" in x.message for x in self.blocks(self.pub.preflight(post))))

    def test_draft_is_refused_rather_than_silently_published(self):
        with self.assertRaises(Exception) as ctx:
            self.pub.publish(Post(kind="text", text="x"), draft=True)
        self.assertIn("draft", str(ctx.exception).lower())


class TestMetaPreflight(MediaCase):
    """Threads and Instagram. Nothing here reaches the network: the quota probe
    is gated on available() and token_ready(), both false without credentials."""

    def setUp(self):
        super().setUp()
        for var in (
            "S3_BUCKET",
            "S3_ACCESS_KEY",
            "S3_SECRET_KEY",
            "THREADS_APP_ID",
            "THREADS_APP_SECRET",
            "INSTAGRAM_APP_ID",
            "INSTAGRAM_APP_SECRET",
        ):
            self._unset(var)
        self.threads = ThreadsPublisher()
        self.instagram = InstagramPublisher()

    def _unset(self, var):
        import os

        saved = os.environ.pop(var, None)
        if saved is not None:
            self.addCleanup(os.environ.__setitem__, var, saved)

    def _with_s3(self):
        import os

        for k, v in (("S3_BUCKET", "b"), ("S3_ACCESS_KEY", "k"), ("S3_SECRET_KEY", "s")):
            os.environ[k] = v
            self.addCleanup(os.environ.pop, k, None)

    # ── the media-URL requirement ───────────────────────────────────────────

    def test_media_without_s3_blocks(self):
        post = Post(kind="image", media=[self.make("a.png")], alt_texts=["x"])
        blocks = self.blocks(self.threads.preflight(post))
        self.assertTrue(any("fetches media by URL" in x.message for x in blocks))

    def test_media_with_s3_is_allowed(self):
        self._with_s3()
        post = Post(kind="image", media=[self.make("a.png")], text="ok", alt_texts=["x"])
        self.assertEqual(self.blocks(self.threads.preflight(post)), [])

    def test_text_only_threads_post_needs_no_s3(self):
        # The reason Threads is the first platform worth connecting.
        self.assertEqual(self.blocks(self.threads.preflight(Post(kind="text", text="Привет."))), [])

    # ── Threads ─────────────────────────────────────────────────────────────

    def test_threads_500_char_limit(self):
        v = self.threads.preflight(Post(kind="text", text="я" * 501))
        self.assertIn("text", self.fields(self.blocks(v)))

    def test_threads_counts_hashtags_towards_the_limit(self):
        v = self.threads.preflight(Post(kind="text", text="я" * 495, hashtags=["smm"]))
        self.assertIn("text", self.fields(self.blocks(v)))

    def test_threads_carousel_cap(self):
        self._with_s3()
        files = [self.make(f"s{i}.png") for i in range(21)]
        post = Post(kind="carousel", media=files, alt_texts=["x"] * 21)
        self.assertTrue(any("at most" in x.message for x in self.blocks(self.threads.preflight(post))))

    def test_threads_empty_text_post_blocks(self):
        self.assertIn("text", self.fields(self.blocks(self.threads.preflight(Post(kind="text")))))

    # ── Instagram ───────────────────────────────────────────────────────────

    def test_instagram_refuses_text_only_posts(self):
        v = self.instagram.preflight(Post(kind="text", text="Просто текст."))
        self.assertIn("kind", self.fields(self.blocks(v)))

    def test_instagram_caption_limit(self):
        self._with_s3()
        post = Post(kind="image", media=[self.make("a.png")], text="я" * 2201, alt_texts=["x"])
        self.assertIn("text", self.fields(self.blocks(self.instagram.preflight(post))))

    def test_instagram_carousel_cap_is_ten(self):
        self._with_s3()
        files = [self.make(f"s{i}.png") for i in range(11)]
        post = Post(kind="carousel", media=files, alt_texts=["x"] * 11)
        self.assertTrue(any("at most" in x.message for x in self.blocks(self.instagram.preflight(post))))

    def test_instagram_ten_slides_are_fine(self):
        self._with_s3()
        files = [self.make(f"s{i}.png") for i in range(10)]
        post = Post(kind="carousel", media=files, text="ok", alt_texts=["x"] * 10)
        self.assertEqual(self.blocks(self.instagram.preflight(post)), [])

    def test_instagram_video_warns_that_it_becomes_a_reel(self):
        self._with_s3()
        post = Post(kind="video", media=[self.make("final.mp4")], text="ok", alt_texts=["x"])
        v = self.instagram.preflight(post)
        self.assertEqual(self.blocks(v), [])
        self.assertTrue(any("Reel" in x.message for x in v))

    def test_instagram_needs_at_least_one_file(self):
        v = self.instagram.preflight(Post(kind="image", media=[]))
        self.assertIn("media", self.fields(self.blocks(v)))

    def test_thirty_one_hashtags_warn(self):
        self._with_s3()
        post = Post(
            kind="image",
            media=[self.make("a.png")],
            text="ok",
            alt_texts=["x"],
            hashtags=[f"t{i}" for i in range(31)],
        )
        v = self.instagram.preflight(post)
        self.assertEqual(self.blocks(v), [])
        self.assertIn("hashtags", self.fields(v, "warn"))

    # ── media params ────────────────────────────────────────────────────────

    def test_instagram_video_container_is_reels(self):
        params = self.instagram._media_params(Path("a.mp4"), "https://x/a.mp4")
        self.assertEqual(params["media_type"], "REELS")

    def test_instagram_image_container_has_no_media_type(self):
        params = self.instagram._media_params(Path("a.png"), "https://x/a.png")
        self.assertEqual(params, {"image_url": "https://x/a.png"})

    def test_threads_distinguishes_image_from_video(self):
        self.assertEqual(self.threads._media_params(Path("a.png"), "u")["media_type"], "IMAGE")
        self.assertEqual(self.threads._media_params(Path("a.mp4"), "u")["media_type"], "VIDEO")


class TestTikTokPreflight(MediaCase):
    def setUp(self):
        super().setUp()
        import os

        for var in ("S3_BUCKET", "S3_ACCESS_KEY", "S3_SECRET_KEY"):
            saved = os.environ.pop(var, None)
            if saved is not None:
                self.addCleanup(os.environ.__setitem__, var, saved)
        self.pub = TikTokPublisher()

    def video(self, mb=1):
        return Post(
            kind="video", media=[self.make("final.mp4", mb * 1024 * 1024)], text="ok", alt_texts=["x"]
        )

    def test_direct_post_warns_about_the_audit(self):
        v = self.pub.preflight(self.video(), draft=False)
        self.assertTrue(any(x.field == "audit" for x in v))

    def test_draft_does_not_warn_about_the_audit(self):
        # The warning is about direct publishing; repeating it on the safe path
        # would train people to ignore it.
        v = self.pub.preflight(self.video(), draft=True)
        self.assertFalse(any(x.field == "audit" for x in v))

    def test_video_needs_no_s3(self):
        self.assertEqual(self.blocks(self.pub.preflight(self.video(), draft=True)), [])

    def test_photo_post_without_s3_blocks(self):
        post = Post(kind="carousel", media=[self.make("a.png"), self.make("b.png")], alt_texts=["x", "y"])
        self.assertTrue(any("PULL_FROM_URL" in x.message for x in self.blocks(self.pub.preflight(post))))

    def test_image_in_a_video_post_blocks(self):
        post = Post(kind="video", media=[self.make("a.png")], alt_texts=["x"])
        self.assertTrue(any("image in a video post" in x.message for x in self.blocks(self.pub.preflight(post))))

    def test_draft_is_supported(self):
        self.assertTrue(self.pub.supports_draft)

    def test_title_limit(self):
        post = Post(kind="video", media=[self.make("final.mp4")], text="я" * 2201, alt_texts=["x"])
        self.assertIn("text", self.fields(self.blocks(self.pub.preflight(post))))

    # ── chunking ────────────────────────────────────────────────────────────

    def test_a_single_chunk_always_declares_the_real_file_size(self):
        # TikTok rejects a chunk_size larger than video_size. Declaring the
        # nominal 20 MB for a 6 MB file is a rejection, not a rounding detail.
        from common.runners.publishers.tiktok import MAX_CHUNK, MB

        for size in (1024, 5 * MB, 6 * MB, 25 * MB, MAX_CHUNK):
            chunk, count = self.pub._chunk_plan(size)
            self.assertEqual(count, 1, f"{size} should be one chunk")
            self.assertEqual(chunk, size, f"{size}: chunk must equal the file size when count is 1")

    def test_large_file_splits_within_the_allowed_range(self):
        from common.runners.publishers.tiktok import MAX_CHUNK, MIN_CHUNK

        chunk, count = self.pub._chunk_plan(200 * 1024 * 1024)
        self.assertGreaterEqual(chunk, MIN_CHUNK)
        self.assertLessEqual(chunk, MAX_CHUNK)
        self.assertGreater(count, 1)

    def test_chunk_plan_never_over_declares_for_any_size(self):
        from common.runners.publishers.tiktok import MAX_CHUNK, MIN_CHUNK, MB

        for mb in (1, 5, 6, 20, 25, 64, 65, 100, 200, 201, 4096):
            size = mb * MB
            chunk, count = self.pub._chunk_plan(size)
            # Declared plan must fit inside the file — the last chunk absorbs
            # the remainder rather than becoming an undersized one.
            self.assertLessEqual(chunk * count, size, f"{mb}MB over-declares")
            self.assertLessEqual(chunk, size, f"{mb}MB: chunk exceeds the file")
            if count > 1:
                self.assertGreaterEqual(chunk, MIN_CHUNK, f"{mb}MB: chunk under the 5MB floor")
                self.assertLessEqual(chunk, MAX_CHUNK, f"{mb}MB: chunk over the 64MB ceiling")


class TestXPreflight(MediaCase):
    def setUp(self):
        super().setUp()
        self.pub = XPublisher()

    def test_280_char_limit(self):
        self.assertIn("text", self.fields(self.blocks(self.pub.preflight(Post(kind="text", text="я" * 281)))))

    def test_thread_parts_are_measured_individually(self):
        # A thread whose root fits but whose third post does not must be caught
        # here — X publishes the root before it ever sees post three.
        post = Post(kind="text", text="короткий корень", thread=["ок", "я" * 300])
        blocks = self.blocks(self.pub.preflight(post))
        self.assertTrue(any(x.field == "thread" and "post 3" in x.message for x in blocks))

    def test_empty_thread_part_blocks(self):
        post = Post(kind="text", text="корень", thread=["   "])
        self.assertIn("thread", self.fields(self.blocks(self.pub.preflight(post))))

    def test_valid_thread_passes(self):
        post = Post(kind="text", text="корень", thread=["второй", "третий"])
        self.assertEqual(self.blocks(self.pub.preflight(post)), [])

    def test_four_images_are_allowed(self):
        files = [self.make(f"{i}.png") for i in range(4)]
        post = Post(kind="carousel", media=files, text="ok", alt_texts=["x"] * 4)
        self.assertEqual(self.blocks(self.pub.preflight(post)), [])

    def test_five_images_block(self):
        files = [self.make(f"{i}.png") for i in range(5)]
        post = Post(kind="carousel", media=files, text="ok", alt_texts=["x"] * 5)
        self.assertIn("media", self.fields(self.blocks(self.pub.preflight(post))))

    def test_video_mixed_with_images_blocks(self):
        post = Post(
            kind="carousel", media=[self.make("a.mp4"), self.make("b.png")], text="ok", alt_texts=["x", "y"]
        )
        self.assertTrue(any("one video or up to four" in x.message for x in self.blocks(self.pub.preflight(post))))

    def test_no_draft_support(self):
        self.assertFalse(self.pub.supports_draft)
        self.assertIn("draft", self.fields(self.blocks(self.pub.preflight(Post(kind="text", text="x"), draft=True))))


class TestYouTubePreflight(MediaCase):
    def setUp(self):
        super().setUp()
        self.pub = YouTubePublisher()

    def test_only_video_is_supported(self):
        post = Post(kind="image", media=[self.make("a.png")], alt_texts=["x"])
        self.assertIn("kind", self.fields(self.blocks(self.pub.preflight(post))))

    def test_still_image_in_a_video_post_blocks(self):
        post = Post(kind="video", media=[self.make("a.png")], title="T", alt_texts=["x"])
        self.assertTrue(any("takes video" in x.message for x in self.blocks(self.pub.preflight(post))))

    def test_title_over_100_chars_blocks(self):
        post = Post(kind="video", media=[self.make("a.mp4")], title="я" * 101, alt_texts=["x"])
        self.assertIn("title", self.fields(self.blocks(self.pub.preflight(post))))

    def test_missing_title_warns(self):
        post = Post(kind="video", media=[self.make("a.mp4")], text="описание", alt_texts=["x"])
        v = self.pub.preflight(post)
        self.assertEqual(self.blocks(v), [])
        self.assertIn("title", self.fields(v, "warn"))

    def test_explicit_title_survives_an_empty_caption(self):
        # The inline version of this bound as (title or first_line) if text
        # else "Untitled", so an explicit --title was discarded whenever the
        # caption happened to be empty.
        self.assertEqual(
            self.pub._derive_title(Post(kind="video", title="Мой заголовок", text="")), "Мой заголовок"
        )

    def test_title_falls_back_to_the_first_non_blank_caption_line(self):
        post = Post(kind="video", text="\n\n  Первая строка\nвторая\n")
        self.assertEqual(self.pub._derive_title(post), "Первая строка")

    def test_title_falls_back_to_untitled(self):
        self.assertEqual(self.pub._derive_title(Post(kind="video", text="   \n  \n")), "Untitled")

    def test_derived_title_is_truncated(self):
        post = Post(kind="video", title="я" * 200)
        self.assertEqual(len(self.pub._derive_title(post)), 100)

    def test_quota_is_warned_about_on_publish_and_on_draft_alike(self):
        # A private upload costs the same 1600 units as a public one, so the
        # warning must not imply --draft is the cheap option.
        post = Post(kind="video", media=[self.make("a.mp4")], title="T", alt_texts=["x"])
        self.assertIn("quota", self.fields(self.pub.preflight(post, draft=False), "warn"))
        self.assertIn("quota", self.fields(self.pub.preflight(post, draft=True), "warn"))

    def test_draft_is_supported(self):
        self.assertTrue(self.pub.supports_draft)

    def test_oversized_tag_block(self):
        post = Post(
            kind="video",
            media=[self.make("a.mp4")],
            title="T",
            alt_texts=["x"],
            hashtags=["я" * 60] * 10,
        )
        self.assertIn("hashtags", self.fields(self.blocks(self.pub.preflight(post))))

    def test_cyrillic_description_is_measured_in_bytes(self):
        # snippet.description is "a maximum length of 5000 bytes", not
        # characters. Cyrillic is two bytes per character in UTF-8, so 3000
        # characters is 6000 bytes and YouTube rejects it. Counting code
        # points let it through.
        post = Post(
            kind="video", media=[self.make("a.mp4")], title="T", text="я" * 3000, alt_texts=["x"]
        )
        blocked = self.blocks(self.pub.preflight(post))
        self.assertIn("text", self.fields(blocked))
        self.assertTrue(any("bytes" in x.message for x in blocked), blocked)

    def test_an_ascii_description_under_5000_still_passes(self):
        # The same 3000 characters in ASCII are 3000 bytes and are fine —
        # the fix must not turn into "measure everything twice".
        post = Post(
            kind="video", media=[self.make("a.mp4")], title="T", text="a" * 3000, alt_texts=["x"]
        )
        self.assertEqual(self.blocks(self.pub.preflight(post)), [])

    def test_other_platforms_still_count_characters(self):
        # Only YouTube documents a byte budget. Telegram's 4096 is characters
        # "after entities parsing", so 3000 Cyrillic characters must pass.
        self.assertEqual(TelegramPublisher.text_unit, "chars")
        v = TelegramPublisher().preflight(Post(kind="text", text="я" * 3000))
        self.assertEqual(self.blocks(v), [])

    def test_description_truncation_cuts_bytes_and_keeps_characters_whole(self):
        # The send path's own guard. Slicing by code point produced 10000
        # bytes from a 5000-character cut; slicing raw bytes would produce a
        # half-character at the end.
        from common.runners.publishers.youtube import _truncate_bytes

        cut = _truncate_bytes("я" * 4000, 5000)
        self.assertLessEqual(len(cut.encode("utf-8")), 5000)
        self.assertEqual(cut, "я" * 2500)  # exactly, no partial character
        self.assertEqual(_truncate_bytes("короткий", 5000), "короткий")


class TestLinkedInPreflight(MediaCase):
    def setUp(self):
        super().setUp()
        self.pub = LinkedInPublisher()

    def test_3000_char_limit(self):
        self.assertIn("text", self.fields(self.blocks(self.pub.preflight(Post(kind="text", text="я" * 3001)))))

    def test_text_post_is_supported(self):
        self.assertEqual(self.blocks(self.pub.preflight(Post(kind="text", text="Пост."))), [])

    def test_empty_text_blocks(self):
        self.assertIn("text", self.fields(self.blocks(self.pub.preflight(Post(kind="text")))))

    def test_video_with_images_blocks(self):
        post = Post(
            kind="carousel", media=[self.make("a.mp4"), self.make("b.png")], text="ok", alt_texts=["x", "y"]
        )
        self.assertIn("media", self.fields(self.blocks(self.pub.preflight(post))))

    def test_organisation_author_warns_about_partner_gating(self):
        import os

        os.environ["LINKEDIN_AUTHOR_URN"] = "urn:li:organization:123"
        self.addCleanup(os.environ.pop, "LINKEDIN_AUTHOR_URN", None)
        v = self.pub.preflight(Post(kind="text", text="Пост."))
        self.assertIn("author", self.fields(v, "warn"))

    def test_no_draft_support(self):
        self.assertFalse(self.pub.supports_draft)


class TestDraftGating(MediaCase):
    def test_draft_on_a_platform_without_drafts_blocks(self):
        pub = TelegramPublisher()
        v = pub.preflight(Post(kind="text", text="x"), draft=True)
        self.assertIn("draft", self.fields(self.blocks(v)))

    def test_no_draft_flag_is_fine(self):
        pub = TelegramPublisher()
        self.assertEqual(self.blocks(pub.preflight(Post(kind="text", text="x"))), [])


class TestCaptionExtraction(unittest.TestCase):
    def test_main_post_heading_wins(self):
        md = "# Captions\n\n## Main post\n\nТело поста.\n\n## Per-slide alts\n\n1. Обложка\n"
        self.assertEqual(publish_cli.extract_caption(md), "Тело поста.")

    def test_russian_heading_is_recognised(self):
        md = "## Основной пост\n\nТело.\n\n## Другое\n\nне это\n"
        self.assertEqual(publish_cli.extract_caption(md), "Тело.")

    def test_heading_match_is_case_insensitive(self):
        self.assertEqual(publish_cli.extract_caption("## MAIN POST\n\nBody.\n"), "Body.")

    def test_without_a_known_heading_everything_is_used(self):
        # Better to over-include than to silently post an empty caption; the
        # dry-run preview is where the user catches it.
        md = "# Something\n\nline one\n\nline two\n"
        self.assertEqual(publish_cli.extract_caption(md), "line one\n\nline two")

    def test_stops_at_the_next_heading_of_any_level(self):
        md = "## Main post\n\nkeep\n\n### Sub\n\ndrop\n"
        self.assertEqual(publish_cli.extract_caption(md), "keep")

    def test_empty_file_yields_empty_caption(self):
        self.assertEqual(publish_cli.extract_caption(""), "")


class TestMediaDiscovery(MediaCase):
    def test_slides_sort_numerically_not_lexically(self):
        for i in (1, 2, 10, 11):
            self.make(f"slide-{i}.png")
        media, kind = publish_cli.discover_media(self.dir)
        self.assertEqual(kind, "carousel")
        self.assertEqual([m.name for m in media], ["slide-1.png", "slide-2.png", "slide-10.png", "slide-11.png"])

    def test_final_mp4_wins_over_slides(self):
        self.make("slide-1.png")
        self.make("final.mp4")
        media, kind = publish_cli.discover_media(self.dir)
        self.assertEqual(kind, "video")
        self.assertEqual(media[0].name, "final.mp4")

    def test_single_image_is_an_image_post(self):
        self.make("cover.png")
        self.assertEqual(publish_cli.discover_media(self.dir)[1], "image")

    def test_empty_dir_is_a_text_post(self):
        media, kind = publish_cli.discover_media(self.dir)
        self.assertEqual((media, kind), ([], "text"))

    def test_single_file_source(self):
        p = self.make("one.mp4")
        self.assertEqual(publish_cli.discover_media(p), ([p], "video"))

    def test_unsupported_single_file_raises(self):
        with self.assertRaises(Exception):
            publish_cli.discover_media(self.make("notes.txt"))


class TestReceipts(MediaCase):
    def result(self, platform="telegram"):
        return PublishResult(
            platform=platform, post_id="42", state="published", permalink="https://t.me/c/42"
        )

    def test_absent_receipt_file_is_empty(self):
        self.assertEqual(receipts.load(self.dir), [])
        self.assertIsNone(receipts.find(self.dir, "telegram", "abc"))

    def test_record_then_find(self):
        receipts.record(self.dir, self.result(), "hash-1")
        found = receipts.find(self.dir, "telegram", "hash-1")
        self.assertIsNotNone(found)
        self.assertEqual(found.permalink, "https://t.me/c/42")

    def test_find_is_scoped_to_the_platform(self):
        # Posting the same deck to Telegram must not mark Threads as done.
        receipts.record(self.dir, self.result("telegram"), "hash-1")
        self.assertIsNone(receipts.find(self.dir, "threads", "hash-1"))

    def test_find_is_scoped_to_the_content(self):
        receipts.record(self.dir, self.result(), "hash-1")
        self.assertIsNone(receipts.find(self.dir, "telegram", "hash-2"))

    def test_records_accumulate(self):
        receipts.record(self.dir, self.result("telegram"), "hash-1")
        receipts.record(self.dir, self.result("threads"), "hash-1")
        self.assertEqual(len(receipts.load(self.dir)), 2)

    def test_corrupt_receipt_does_not_raise(self):
        receipts.path_for(self.dir).write_text("{oops", encoding="utf-8")
        self.assertEqual(receipts.load(self.dir), [])

    # ── what actually blocks a run ──────────────────────────────────────────

    def draft(self, platform="instagram"):
        return PublishResult(platform=platform, post_id="c1", state="draft")

    def test_a_draft_does_not_block_publishing_it(self):
        # Staging, reviewing, then publishing is the documented Meta and TikTok
        # path. Treating the draft as "already done" turned the second half of
        # that into a --force, which is backwards — the user staged it in order
        # to publish it.
        receipts.record(self.dir, self.draft(), "hash-1")
        self.assertIsNone(receipts.find_blocking(self.dir, "instagram", "hash-1", drafting=False))

    def test_a_draft_blocks_drafting_again(self):
        receipts.record(self.dir, self.draft(), "hash-1")
        self.assertIsNotNone(receipts.find_blocking(self.dir, "instagram", "hash-1", drafting=True))

    def test_a_publication_blocks_publishing_again(self):
        receipts.record(self.dir, self.result("instagram"), "hash-1")
        self.assertIsNotNone(receipts.find_blocking(self.dir, "instagram", "hash-1", drafting=False))

    def test_a_publication_blocks_drafting_too(self):
        receipts.record(self.dir, self.result("instagram"), "hash-1")
        self.assertIsNotNone(receipts.find_blocking(self.dir, "instagram", "hash-1", drafting=True))

    def test_draft_then_publish_then_publish_is_blocked(self):
        # The full lifecycle: stage, publish, and only then refuse a repeat.
        receipts.record(self.dir, self.draft(), "hash-1")
        self.assertIsNone(receipts.find_blocking(self.dir, "instagram", "hash-1", drafting=False))
        receipts.record(self.dir, self.result("instagram"), "hash-1")
        self.assertIsNotNone(receipts.find_blocking(self.dir, "instagram", "hash-1", drafting=False))

    def test_find_returns_the_most_recent_receipt(self):
        receipts.record(self.dir, self.draft(), "hash-1")
        receipts.record(self.dir, self.result("instagram"), "hash-1")
        self.assertEqual(receipts.find(self.dir, "instagram", "hash-1").state, "published")

    def test_blocking_is_scoped_to_the_platform(self):
        receipts.record(self.dir, self.result("telegram"), "hash-1")
        self.assertIsNone(receipts.find_blocking(self.dir, "threads", "hash-1", drafting=False))

    def test_published_at_is_recorded(self):
        r = receipts.record(self.dir, self.result(), "hash-1")
        self.assertTrue(r.published_at.startswith("20"))


if __name__ == "__main__":
    unittest.main()
