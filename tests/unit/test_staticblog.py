"""The canonical source step.

Two things here decide whether the rest of the syndication chain is correct: the
URL predicted before the site rebuilds, and the refusal to clobber a file in
somebody's blog repository. Both are pinned.
"""

import datetime as dt
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import staticblog  # noqa: E402
from common.runners.staticblog import PostDraft  # noqa: E402
from common.runners.publishers.micropub import MicropubPublisher  # noqa: E402
from common.runners.publishers.qiita import QiitaPublisher  # noqa: E402
from common.runners.publishers.tumblr import TumblrPublisher  # noqa: E402
from common.runners.publishers.base import Post  # noqa: E402


def config(tmp: Path, **kw) -> staticblog.BlogConfig:
    base = {
        "content_dir": tmp,
        "url_pattern": "https://you.dev/posts/{slug}/",
        "filename_pattern": "{slug}.md",
    }
    base.update(kw)
    return staticblog.BlogConfig(**base)


class TestSlugify(unittest.TestCase):
    def test_cyrillic_is_transliterated_not_dropped(self):
        self.assertEqual(staticblog.slugify("Привет мир"), "privet-mir")

    def test_accents_decompose_rather_than_vanish(self):
        self.assertEqual(staticblog.slugify("Café Déjà vu"), "cafe-deja-vu")

    def test_punctuation_collapses_to_single_hyphens(self):
        self.assertEqual(staticblog.slugify("A -- B?! C"), "a-b-c")

    def test_never_returns_empty(self):
        # An all-punctuation title would otherwise produce a nameless file.
        self.assertEqual(staticblog.slugify("!!!"), "post")

    def test_no_leading_or_trailing_hyphen(self):
        slug = staticblog.slugify("  -- hello --  ")
        self.assertFalse(slug.startswith("-"))
        self.assertFalse(slug.endswith("-"))


class TestFrontmatter(unittest.TestCase):
    def test_empty_values_are_omitted(self):
        out = staticblog.render_frontmatter({"title": "x", "description": "", "tags": []})
        self.assertIn("title: x", out)
        self.assertNotIn("description", out)
        self.assertNotIn("tags", out)

    def test_booleans_render_unquoted(self):
        self.assertIn("draft: true", staticblog.render_frontmatter({"draft": True}))
        self.assertIn("draft: false", staticblog.render_frontmatter({"draft": False}))

    def test_colon_in_a_title_is_quoted(self):
        # `title: Model ids: gone` is invalid YAML and would break the build.
        out = staticblog.render_frontmatter({"title": "Model ids: gone"})
        self.assertIn('title: "Model ids: gone"', out)

    def test_embedded_quotes_are_escaped(self):
        out = staticblog.render_frontmatter({"title": 'He said "no"'})
        self.assertIn('\\"no\\"', out)


class TestWritePost(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_url_is_predicted_before_the_site_builds(self):
        drafted = staticblog.write_post(config(self.tmp), PostDraft(title="Hello World", body="x"))
        self.assertEqual(drafted.url, "https://you.dev/posts/hello-world/")

    def test_jekyll_filename_pattern_carries_the_date(self):
        drafted = staticblog.write_post(
            config(self.tmp, filename_pattern="{year}-{month}-{day}-{slug}.md"),
            PostDraft(title="Hello", body="x", when=dt.date(2026, 8, 5)),
        )
        self.assertEqual(drafted.path.name, "2026-08-05-hello.md")

    def test_dated_url_pattern_is_supported(self):
        drafted = staticblog.write_post(
            config(self.tmp, url_pattern="https://you.dev/{year}/{month}/{slug}/"),
            PostDraft(title="Hello", body="x", when=dt.date(2026, 8, 5)),
        )
        self.assertEqual(drafted.url, "https://you.dev/2026/08/hello/")

    def test_refuses_to_clobber_without_overwrite(self):
        staticblog.write_post(config(self.tmp), PostDraft(title="Hello", body="first"))
        with self.assertRaises(FileExistsError):
            staticblog.write_post(config(self.tmp), PostDraft(title="Hello", body="second"))

    def test_overwrite_is_opt_in_and_reports_it(self):
        staticblog.write_post(config(self.tmp), PostDraft(title="Hello", body="first"))
        drafted = staticblog.write_post(
            config(self.tmp), PostDraft(title="Hello", body="second"), overwrite=True
        )
        self.assertTrue(drafted.existed)
        self.assertIn("second", drafted.path.read_text(encoding="utf-8"))

    def test_body_follows_the_frontmatter_block(self):
        drafted = staticblog.write_post(
            config(self.tmp),
            PostDraft(title="T", body="# Body", description="d", tags=("a", "b")),
        )
        text = drafted.path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("tags: [a, b]", text)
        self.assertIn("\n\n# Body\n", text)

    def test_draft_field_can_be_disabled_for_generators_without_one(self):
        drafted = staticblog.write_post(config(self.tmp, draft_field=None), PostDraft(title="T", body="x"))
        self.assertNotIn("draft:", drafted.path.read_text(encoding="utf-8"))

    def test_missing_directories_are_created(self):
        nested = self.tmp / "content" / "posts"
        drafted = staticblog.write_post(config(nested), PostDraft(title="T", body="x"))
        self.assertTrue(drafted.path.is_file())


def article(**kw) -> Post:
    base = {
        "kind": "article",
        "title": "A title",
        "text": "Body text.",
        "hashtags": ("python",),
        "canonical_url": "https://you.dev/posts/a-title/",
    }
    base.update(kw)
    return Post(**base)


class TestTumblr(unittest.TestCase):
    def test_body_is_an_npf_markdown_block(self):
        blocks = TumblrPublisher()._content_blocks(article())
        self.assertEqual(blocks[0]["type"], "text")
        self.assertEqual(blocks[0]["subtype"], "markdown")

    def test_canonical_goes_into_the_body_since_there_is_no_field(self):
        text = TumblrPublisher()._content_blocks(article())[0]["text"]
        self.assertIn("https://you.dev/posts/a-title/", text)

    def test_warns_that_it_cannot_pass_ranking_signal(self):
        found = TumblrPublisher().preflight(article())
        self.assertTrue([v for v in found if v.field == "canonical_url"])

    def test_blog_id_with_a_path_is_rejected(self):
        os.environ["TUMBLR_BLOG_ID"] = "myblog.tumblr.com/posts"
        try:
            blocking = [
                v for v in TumblrPublisher().preflight(article()) if v.severity == "block"
            ]
            self.assertTrue(blocking)
        finally:
            del os.environ["TUMBLR_BLOG_ID"]


class TestQiita(unittest.TestCase):
    def test_requires_at_least_one_tag(self):
        blocking = [
            v for v in QiitaPublisher().preflight(article(hashtags=())) if v.severity == "block"
        ]
        self.assertTrue(blocking)

    def test_warns_when_the_body_is_not_japanese(self):
        warns = [v for v in QiitaPublisher().preflight(article()) if v.field == "text"]
        self.assertTrue(warns, "an English post on Qiita reaches nobody")

    def test_japanese_body_passes_without_the_language_warning(self):
        post = article(title="モデルIDの話", text="これは日本語の本文です。")
        warns = [v for v in QiitaPublisher().preflight(post) if v.field == "text"]
        self.assertEqual(warns, [])

    def test_tags_carry_a_versions_list(self):
        body = QiitaPublisher()._body(article(), draft=False)
        self.assertEqual(body["tags"], [{"name": "python", "versions": []}])

    def test_draft_maps_to_private(self):
        self.assertTrue(QiitaPublisher()._body(article(), draft=True)["private"])
        self.assertFalse(QiitaPublisher()._body(article(), draft=False)["private"])


class TestMicropub(unittest.TestCase):
    def test_every_property_value_is_an_array(self):
        # The spec requires it; a bare string is silently mishandled by some
        # endpoints and rejected by others.
        props = MicropubPublisher()._body(article())["properties"]
        for key, value in props.items():
            self.assertIsInstance(value, list, f"{key} must be an array")

    def test_type_is_h_entry(self):
        self.assertEqual(MicropubPublisher()._body(article())["type"], ["h-entry"])

    def test_canonical_is_sent_as_syndication(self):
        props = MicropubPublisher()._body(article())["properties"]
        self.assertEqual(props["syndication"], ["https://you.dev/posts/a-title/"])

    def test_relative_endpoint_is_rejected(self):
        os.environ["MICROPUB_ENDPOINT"] = "/micropub"
        try:
            blocking = [
                v for v in MicropubPublisher().preflight(article()) if v.severity == "block"
            ]
            self.assertTrue(blocking)
        finally:
            del os.environ["MICROPUB_ENDPOINT"]


if __name__ == "__main__":
    unittest.main()
