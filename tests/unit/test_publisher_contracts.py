"""Pins the field names each article publisher sends to its vendor.

The two live bugs found in the ElevenLabs integration — a duration field under
the wrong name, lyrics dropped because the vendor moved them into the prompt —
were both caught by reading documentation, not by the suite. Both were field-name
mistakes, and a field-name mistake is invisible to a test that only checks the
value it just put in: `body["duration_secs"] == 30` passes whether or not the
vendor has ever heard of `duration_secs`.

What an offline test can pin is the vocabulary. Each publisher's request body is
compared against the field list from the vendor's own documentation, cited below.
An invented field fails, a renamed one fails, and a required one going missing
fails. What this cannot prove is that the vendor still accepts the vocabulary —
that needs a recorded response fixture and a key, and is still open on the
roadmap. Treating this as the whole job would be the mistake.

Sources, checked 2026-08-08:
  dev.to     — https://developers.forem.com/api/v1#tag/articles/operation/createArticle
  Qiita      — https://qiita.com/api/v2/docs#post-apiv2items
  Micropub   — https://www.w3.org/TR/micropub/#create (JSON syntax, h-entry)
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners.publishers.base import Post  # noqa: E402
from common.runners.publishers.devto import DevToPublisher  # noqa: E402
from common.runners.publishers.micropub import MicropubPublisher  # noqa: E402
from common.runners.publishers.qiita import QiitaPublisher  # noqa: E402

# Every field the vendor documents for article creation. A body key outside this
# set is either a typo or a field the vendor never had.
DEVTO_FIELDS = {
    "title", "body_markdown", "published", "series", "main_image",
    "canonical_url", "description", "tags", "organization_id",
}
QIITA_FIELDS = {"title", "body", "tags", "private", "tweet", "group_url_name"}
MICROPUB_PROPERTIES = {
    "name", "content", "summary", "category", "syndication",
    "published", "mp-syndicate-to", "mp-slug",
}


def article(**kw) -> Post:
    base = {
        "kind": "article",
        "title": "A title",
        "text": "## Heading\n\nBody text.",
        "hashtags": ("python", "api"),
        "canonical_url": "https://mine.dev/post",
        "description": "An excerpt.",
    }
    base.update(kw)
    return Post(**base)


class TestDevTo(unittest.TestCase):
    def body(self, **kw):
        return DevToPublisher()._body(article(**kw), draft=False)["article"]

    def test_no_field_outside_the_documented_set(self):
        rich = self.body(series="A series", extra={"cover_url": "https://i/x.png", "organization_id": "7"})
        self.assertEqual(set(), set(rich) - DEVTO_FIELDS, "field the API does not document")

    def test_the_required_fields_are_always_present(self):
        # `published` is what decides draft vs live. Omitting it is not neutral:
        # the API defaults to draft, so a missing key silently unpublishes.
        for key in ("title", "body_markdown", "published"):
            self.assertIn(key, self.body())

    def test_markdown_reaches_the_markdown_field(self):
        self.assertIn("## Heading", self.body()["body_markdown"])

    def test_optional_fields_are_omitted_rather_than_sent_empty(self):
        bare = self.body(hashtags=(), canonical_url=None, description="")
        self.assertEqual(set(), {"tags", "canonical_url", "description"} & set(bare))


class TestQiita(unittest.TestCase):
    def body(self, **kw):
        return QiitaPublisher()._body(article(**kw), draft=False)

    def test_no_field_outside_the_documented_set(self):
        self.assertEqual(set(), set(self.body()) - QIITA_FIELDS)

    def test_tags_carry_the_versions_key_the_schema_requires(self):
        # Qiita rejects a tag object without `versions`; an empty list means
        # "no version constraint", which is what a prose article wants.
        for tag in self.body()["tags"]:
            self.assertEqual({"name", "versions"}, set(tag))
            self.assertIsInstance(tag["versions"], list)

    def test_draft_maps_to_private_not_to_a_published_flag(self):
        self.assertIs(True, QiitaPublisher()._body(article(), draft=True)["private"])
        self.assertIs(False, self.body()["private"])

    def test_canonical_survives_as_a_first_published_note(self):
        # Qiita has no canonical field at all, so the URL has to ride in the
        # body or it is lost — which is the failure the canonical rule exists
        # to prevent.
        self.assertIn("https://mine.dev/post", self.body()["body"])


class TestMicropub(unittest.TestCase):
    def body(self, **kw):
        return MicropubPublisher()._body(article(**kw))

    def test_the_envelope_is_an_h_entry(self):
        self.assertEqual(["h-entry"], self.body()["type"])
        self.assertEqual({"type", "properties"}, set(self.body()))

    def test_no_property_outside_the_documented_vocabulary(self):
        rich = self.body(extra={"syndicate_to": ["https://twitter.com/"]})
        self.assertEqual(set(), set(rich["properties"]) - MICROPUB_PROPERTIES)

    def test_every_property_value_is_an_array(self):
        # The JSON syntax requires it. A bare string is accepted by some
        # implementations and rejected by others, which is the worst case:
        # it works until the user switches host.
        for key, value in self.body()["properties"].items():
            with self.subTest(property=key):
                self.assertIsInstance(value, list, f"{key} must be an array")


if __name__ == "__main__":
    unittest.main()
