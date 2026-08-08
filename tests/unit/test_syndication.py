"""Article syndication — publishers, packets, and the canonical rule.

The thing worth guarding here is not the HTTP plumbing but the canonical
handling. Syndicating without a canonical URL is actively worse than not
syndicating: the same text on several domains makes search engines pick one,
and it is rarely the author's. So every path that can drop the canonical is
pinned, and the warning that says so is asserted rather than assumed.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import syndication  # noqa: E402
from common.runners.publishers.base import Post  # noqa: E402
from common.runners.publishers.devto import DevToPublisher  # noqa: E402
from common.runners.publishers.hashnode import HashnodePublisher  # noqa: E402
from common.runners.publishers.telegraph import (  # noqa: E402
    TelegraphPublisher,
    markdown_to_nodes,
)

BODY = "## Heading\n\nA [link](https://example.com) inline.\n\n- one\n- two"


def article(**kw) -> Post:
    base = {
        "kind": "article",
        "title": "A title",
        "text": BODY,
        "hashtags": ("python", "api"),
        "canonical_url": "https://mine.dev/post",
        "description": "An excerpt.",
    }
    base.update(kw)
    return Post(**base)


class TestArticlePreflight(unittest.TestCase):
    def test_missing_canonical_warns_but_does_not_block(self):
        found = DevToPublisher().preflight(article(canonical_url=None))
        canonical = [v for v in found if v.field == "canonical_url"]
        self.assertEqual(len(canonical), 1)
        self.assertEqual(canonical[0].severity, "warn")

    def test_relative_canonical_blocks(self):
        found = DevToPublisher().preflight(article(canonical_url="/post"))
        blocking = [v for v in found if v.severity == "block" and v.field == "canonical_url"]
        self.assertTrue(blocking, "a relative canonical is useless and must block")

    def test_article_needs_title_and_body(self):
        fields = {
            v.field
            for v in DevToPublisher().preflight(article(title="", text=""))
            if v.severity == "block"
        }
        self.assertIn("title", fields)
        self.assertIn("text", fields)

    def test_article_rules_do_not_fire_on_social_posts(self):
        found = [
            v
            for v in TelegraphPublisher().preflight(Post(kind="text", text="hi"))
            if v.field in {"canonical_url", "title"}
        ]
        self.assertEqual(found, [])

    def test_devto_blocks_a_fifth_tag(self):
        # The generic rule only warns; the API rejects, so dev.to must block.
        found = DevToPublisher().preflight(article(hashtags=("a", "b", "c", "d", "e")))
        blocking = [v for v in found if v.severity == "block" and v.field == "hashtags"]
        self.assertTrue(blocking)

    def test_devto_allows_exactly_four_tags(self):
        found = DevToPublisher().preflight(article(hashtags=("a", "b", "c", "d")))
        self.assertEqual([v for v in found if v.severity == "block"], [])


class TestDevToBody(unittest.TestCase):
    def test_canonical_and_tags_reach_the_wire(self):
        body = DevToPublisher()._body(article(), draft=False)["article"]
        self.assertEqual(body["canonical_url"], "https://mine.dev/post")
        self.assertEqual(body["tags"], ["python", "api"])
        self.assertTrue(body["published"])

    def test_draft_flips_published(self):
        body = DevToPublisher()._body(article(), draft=True)["article"]
        self.assertFalse(body["published"])

    def test_optional_fields_are_omitted_rather_than_sent_empty(self):
        body = DevToPublisher()._body(
            article(canonical_url=None, description="", series=None, hashtags=()), draft=False
        )["article"]
        for key in ("canonical_url", "description", "series", "tags", "main_image"):
            self.assertNotIn(key, body, f"{key} should be omitted when unset")


class TestHashnodeInput(unittest.TestCase):
    def setUp(self):
        import os

        os.environ.setdefault("HASHNODE_PUBLICATION_ID", "pub_test")

    def test_canonical_uses_hashnodes_spelling(self):
        payload = HashnodePublisher()._input(article())
        self.assertEqual(payload["originalArticleURL"], "https://mine.dev/post")

    def test_tags_are_objects_not_strings(self):
        payload = HashnodePublisher()._input(article())
        self.assertEqual(payload["tags"], [
            {"slug": "python", "name": "python"},
            {"slug": "api", "name": "api"},
        ])

    def test_draft_is_refused_with_an_explanation(self):
        blocking = [
            v
            for v in HashnodePublisher().preflight(article(), draft=True)
            if v.severity == "block"
        ]
        self.assertTrue(blocking)


class TestTelegraphConversion(unittest.TestCase):
    def test_heading_list_and_link_survive(self):
        nodes = markdown_to_nodes(BODY)
        tags = [n["tag"] for n in nodes if isinstance(n, dict)]
        self.assertEqual(tags, ["h3", "p", "ul"])

        paragraph = nodes[1]["children"]
        anchor = [c for c in paragraph if isinstance(c, dict)][0]
        self.assertEqual(anchor["tag"], "a")
        self.assertEqual(anchor["attrs"]["href"], "https://example.com")

    def test_list_items_are_wrapped_once(self):
        ul = markdown_to_nodes("- one\n- two\n- three")[0]
        self.assertEqual(ul["tag"], "ul")
        self.assertEqual(len(ul["children"]), 3)

    def test_code_fence_becomes_pre(self):
        nodes = markdown_to_nodes("```\nx = 1\n```")
        self.assertEqual(nodes[0]["tag"], "pre")
        self.assertIn("x = 1", nodes[0]["children"][0])

    def test_source_line_is_appended_when_canonical_is_set(self):
        content = TelegraphPublisher()._content(article())
        last = content[-1]
        self.assertEqual(last["tag"], "p")
        self.assertIn("Originally published at", last["children"][0])

    def test_no_source_line_without_canonical(self):
        content = TelegraphPublisher()._content(article(canonical_url=None))
        self.assertNotIn("Originally published at", str(content))

    def test_telegraph_is_honest_about_having_no_canonical_tag(self):
        found = TelegraphPublisher().preflight(article())
        notes = [v for v in found if v.field == "canonical_url" and v.severity == "warn"]
        self.assertTrue(notes, "Telegraph must say it cannot pass ranking signal home")


class TestPackets(unittest.TestCase):
    def test_every_manual_platform_gets_a_file(self):
        import tempfile

        out = Path(tempfile.mkdtemp())
        written = syndication.write_packets(article(), out)
        self.assertEqual(len(written), len(syndication.MANUAL_ORDER))
        for path in written:
            self.assertTrue(path.is_file())
            self.assertIn("## Body", path.read_text(encoding="utf-8"))

    def test_medium_packet_names_the_import_source(self):
        import tempfile

        out = Path(tempfile.mkdtemp())
        syndication.write_packets(article(), out, platforms=("medium",), devto_url="https://dev.to/a/b")
        text = (out / "packet-medium.md").read_text(encoding="utf-8")
        self.assertIn("https://dev.to/a/b", text)
        self.assertIn("Import a story", text)

    def test_missing_canonical_is_called_out_in_the_packet(self):
        import tempfile

        out = Path(tempfile.mkdtemp())
        syndication.write_packets(article(canonical_url=None), out, platforms=("habr",))
        text = (out / "packet-habr.md").read_text(encoding="utf-8")
        self.assertIn("No canonical URL was set", text)

    def test_unknown_platform_is_an_error_not_a_silent_skip(self):
        import tempfile

        with self.assertRaises(KeyError):
            syndication.write_packets(article(), Path(tempfile.mkdtemp()), platforms=("tumblr",))

    def test_plan_puts_devto_before_medium(self):
        steps = "\n".join(syndication.plan(article()))
        self.assertLess(steps.index("dev.to"), steps.index("Medium"))

    def test_plan_leads_with_the_missing_canonical_problem(self):
        first = syndication.plan(article(canonical_url=None))[0]
        self.assertIn("No canonical target", first)


class TestRegistration(unittest.TestCase):
    """Article and social publishing are separate sets, and must stay separate.

    The membership list is derived rather than typed in — hardcoding it meant
    adding a fourth article publisher turned this red for no real reason.
    """

    @staticmethod
    def _publishers():
        from common.runners import config

        config.load_all_publishers()
        return config.all_publishers()

    def test_the_expected_article_publishers_exist(self):
        by_name = {p.name: p for p in self._publishers()}
        for name in ("devto", "telegraph", "hashnode", "tumblr", "qiita", "micropub"):
            self.assertIn(name, by_name)

    def test_article_publishers_accept_nothing_else(self):
        for pub in self._publishers():
            if "article" not in pub.supports:
                continue
            self.assertEqual(
                pub.supports,
                frozenset({"article"}),
                f"{pub.name} mixes article and social kinds; preflight rules differ",
            )

    def test_social_publishers_do_not_claim_articles(self):
        for pub in self._publishers():
            if pub.supports == frozenset({"article"}):
                continue
            self.assertNotIn("article", pub.supports, f"{pub.name} should not accept articles")


if __name__ == "__main__":
    unittest.main()
