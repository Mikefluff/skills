"""What each platform limit is, and which vendor sentence backs it.

Split out of test_publish.py, which tests preflight *behaviour*. This file
tests the *numbers* — a different kind of claim with a different way of going
wrong. Preflight logic breaks when someone edits it; a constant breaks when a
vendor changes a page, silently, with nothing in this repo touched.

The first version of the publishing layer was written from memory and four
numbers were wrong, each in the direction that hurts: a cap four times too low,
a file limit three times too high, an upload allowance sixteen times too low,
and an API version already sunset. A plausible-looking wrong constant is
invisible in review, so it gets a test.

Sources, dates and the ~/✅ convention live in
skills/post-publisher/references/platform-limits.md. Change a number here and you must
change that table in the same commit — they drifted apart once and that is how
the four wrong ones survived.

Nothing in this file touches the network.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.publishers.instagram import InstagramPublisher  # noqa: E402
from common.runners.publishers.linkedin import LinkedInPublisher  # noqa: E402
from common.runners.publishers.telegram import TelegramPublisher  # noqa: E402
from common.runners.publishers.threads import ThreadsPublisher  # noqa: E402
from common.runners.publishers.tiktok import TikTokPublisher  # noqa: E402
from common.runners.publishers.x import XPublisher  # noqa: E402
from common.runners.publishers.youtube import YouTubePublisher  # noqa: E402


class TestVerifiedPlatformNumbers(unittest.TestCase):
    """Constants read off the vendors' live documentation on 2026-08-03.

    These exist because the first version of this layer was written from
    memory and four numbers were wrong, each in the direction that hurts: a
    cap four times too low, a file limit three times too high, an upload
    allowance sixteen times too low, and an API version already sunset. A
    plausible-looking wrong constant is invisible in review, so it gets a test.

    Sources are listed in skills/post-publisher/references/platform-limits.md.
    """

    def test_instagram_publishes_100_per_day_not_25(self):
        from common.runners.publishers.instagram import DAILY_POST_CAP

        self.assertEqual(DAILY_POST_CAP, 100)

    def test_instagram_reels_cap_at_300mb_not_1gb(self):
        self.assertEqual(InstagramPublisher.max_video_mb, 300.0)

    def test_instagram_caption_and_hashtag_limits(self):
        self.assertEqual(InstagramPublisher.max_text_chars, 2200)
        self.assertEqual(InstagramPublisher.max_hashtags, 30)
        self.assertEqual(InstagramPublisher.max_image_mb, 8.0)

    def test_instagram_carousel_holds_ten(self):
        self.assertEqual(InstagramPublisher.max_media, 10)

    def test_youtube_allows_100_uploads_per_day(self):
        # Not "1600 units of a 10,000/day pool" — uploads have their own meter.
        from common.runners.publishers.youtube import DAILY_UPLOAD_ALLOWANCE

        self.assertEqual(DAILY_UPLOAD_ALLOWANCE, 100)

    def test_linkedin_api_version_is_not_stale(self):
        # LinkedIn rejects versions older than roughly a year.
        from common.runners.publishers.linkedin import DEFAULT_VERSION

        self.assertGreaterEqual(int(DEFAULT_VERSION), 202600, "LinkedIn version has aged out")

    def test_threads_limits(self):
        self.assertEqual(ThreadsPublisher.max_text_chars, 500)
        self.assertEqual(ThreadsPublisher.max_media, 20)
        self.assertEqual(ThreadsPublisher.max_image_mb, 8.0)

    def test_x_accepts_at_most_four_images(self):
        # media_ids is documented as accepting 1-4 items.
        self.assertEqual(XPublisher.max_media, 4)
        self.assertEqual(XPublisher.max_text_chars, 280)

    def test_x_uploads_via_the_v2_endpoint_not_the_legacy_host(self):
        url = XPublisher().upload_url()
        self.assertEqual(url, "https://api.x.com/2/media/upload")
        self.assertNotIn("upload.twitter.com", url)

    def test_telegram_photo_limit_is_tighter_than_the_general_upload_cap(self):
        self.assertEqual(TelegramPublisher.max_image_mb, 10.0)
        self.assertEqual(TelegramPublisher.max_video_mb, 50.0)

    def test_tiktok_title_limit_and_max_size(self):
        self.assertEqual(TikTokPublisher.max_text_chars, 2200)
        self.assertEqual(TikTokPublisher.max_video_mb, 4096.0)

    def test_tiktok_chunk_bounds_match_the_documented_range(self):
        from common.runners.publishers.tiktok import MAX_CHUNK, MB, MIN_CHUNK

        self.assertEqual(MIN_CHUNK, 5 * MB)
        self.assertEqual(MAX_CHUNK, 64 * MB)

    def test_linkedin_multiimage_caps_at_twenty(self):
        self.assertEqual(LinkedInPublisher.max_media, 20)
        self.assertEqual(LinkedInPublisher.max_text_chars, 3000)


class TestSecondPassPlatformNumbers(unittest.TestCase):
    """The rows that were still marked ~ after the first sweep, read on 2026-08-03.

    The first pass could not machine-read Telegram's parameter tables (800 KB of
    HTML) or find X's media limits (they live on a best-practices page the
    chunked-upload guide links to but does not repeat). Both were read this
    time. Each assertion below quotes the sentence it is pinning, so that a
    future edit has to argue with the vendor rather than with the constant.

    Sources are listed in skills/post-publisher/references/platform-limits.md.
    """

    def test_telegram_message_and_caption_are_different_ceilings(self):
        # sendMessage.text: "1-4096 characters after entities parsing"
        # sendPhoto.caption: "0-1024 characters after entities parsing"
        from common.runners.publishers.telegram import CAPTION_LIMIT, MESSAGE_LIMIT

        self.assertEqual(MESSAGE_LIMIT, 4096)
        self.assertEqual(CAPTION_LIMIT, 1024)
        self.assertEqual(TelegramPublisher.max_text_chars, MESSAGE_LIMIT)

    def test_telegram_sendphoto_caps_at_ten_mb(self):
        # "The photo must be at most 10 MB in size."
        from common.runners.publishers.telegram import PHOTO_LIMIT_MB, UPLOAD_LIMIT_MB

        self.assertEqual(PHOTO_LIMIT_MB, 10.0)
        # "10 MB max size for photos, 50 MB for other files."
        self.assertEqual(UPLOAD_LIMIT_MB, 50.0)
        self.assertLess(PHOTO_LIMIT_MB, UPLOAD_LIMIT_MB)

    def test_x_image_and_video_sizes(self):
        # "Image size: <= 5 MB" / "File size: must not exceed 512 mb"
        self.assertEqual(XPublisher.max_image_mb, 5.0)
        self.assertEqual(XPublisher.max_video_mb, 512.0)

    def test_x_text_limit_is_280(self):
        # "Posts on X can contain up to 280 characters."
        from common.runners.publishers.x import TEXT_LIMIT

        self.assertEqual(TEXT_LIMIT, 280)

    def test_threads_video_is_one_gigabyte(self):
        # Previously "not stated in the docs read"; now documented: "1 GB maximum".
        self.assertEqual(ThreadsPublisher.max_video_mb, 1024.0)

    def test_tiktok_image_caps_at_twenty_mb(self):
        # "Maximum of 20MB for each image"
        self.assertEqual(TikTokPublisher.max_image_mb, 20.0)

    def test_tiktok_carousel_holds_thirty_five(self):
        # "An array containing up to 35 photo content URLs"
        self.assertEqual(TikTokPublisher.max_media, 35)

    def test_youtube_video_size_is_256_gb(self):
        # "256 GB or 12 hours, whichever is less"
        self.assertEqual(YouTubePublisher.max_video_mb, 256_000.0)

    def test_youtube_title_and_tag_budgets(self):
        # title: "maximum length of 100 characters"
        # tags:  "maximum length of 500 characters" across the whole list
        from common.runners.publishers.youtube import TAGS_TOTAL_LIMIT, TITLE_LIMIT

        self.assertEqual(TITLE_LIMIT, 100)
        self.assertEqual(TAGS_TOTAL_LIMIT, 500)

    def test_youtube_description_budget_is_bytes_and_nothing_elses_is(self):
        # "The property value has a maximum length of 5000 bytes" — the only
        # limit in this repo not stated in characters.
        from common.runners.publishers.youtube import DESCRIPTION_LIMIT

        self.assertEqual(DESCRIPTION_LIMIT, 5000)
        self.assertEqual(YouTubePublisher.text_unit, "bytes")
        for pub in (
            TelegramPublisher,
            ThreadsPublisher,
            InstagramPublisher,
            TikTokPublisher,
            XPublisher,
            LinkedInPublisher,
        ):
            self.assertEqual(pub.text_unit, "chars", pub.name)

    def test_linkedin_video_is_500_mb_not_the_5_gb_the_schema_claims(self):
        # The Videos API prose says "Between 75kb and 500MB"; the
        # fileSizeBytes field on the same page says 5GB. Take the smaller.
        self.assertEqual(LinkedInPublisher.max_video_mb, 500.0)

    def test_linkedin_text_limit_stays_unverified(self):
        # 3000 is what LinkedIn's composer enforces, not what its API documents.
        # This asserts the constant has not drifted, NOT that it is right — the
        # table keeps the row at ~ for exactly that reason.
        from common.runners.publishers.linkedin import TEXT_LIMIT

        self.assertEqual(TEXT_LIMIT, 3000)
