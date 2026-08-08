"""JSON-LD generation, and the AEO extractability linter.

The schema tests care most about the checks that refuse to emit something: a
statement in a Question node, a headline over the documented limit, an empty
FAQ. Structured data that disagrees with the page is the one mistake in this
area with a real downside, so the generator is built to say no.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/writer/scripts"))

import lint_aeo  # noqa: E402
from common.runners import schema_ld  # noqa: E402
from common.runners.cli.schema import extract_faq, parse_frontmatter  # noqa: E402


class TestArticle(unittest.TestCase):
    def meta(self, **kw) -> schema_ld.ArticleMeta:
        base = {"headline": "A headline", "date_published": "2026-08-05"}
        base.update(kw)
        return schema_ld.ArticleMeta(**base)

    def test_date_modified_defaults_to_published(self):
        # Freshness is read from both. A missing dateModified reads as abandoned.
        node = schema_ld.article(self.meta())
        self.assertEqual(node["dateModified"], "2026-08-05")

    def test_explicit_date_modified_wins(self):
        node = schema_ld.article(self.meta(date_modified="2026-09-01"))
        self.assertEqual(node["dateModified"], "2026-09-01")

    def test_headline_over_the_documented_limit_is_refused(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.article(self.meta(headline="x" * 111))

    def test_empty_headline_is_refused(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.article(self.meta(headline="   "))

    def test_author_is_an_entity_not_a_string(self):
        author = schema_ld.Author(name="A", knows_about=("SEO",), same_as=("https://x/",))
        node = schema_ld.article(self.meta(author=author))
        self.assertEqual(node["author"]["@type"], "Person")
        self.assertEqual(node["author"]["knowsAbout"], ["SEO"])
        self.assertEqual(node["author"]["sameAs"], ["https://x/"])

    def test_unset_fields_are_omitted_rather_than_empty(self):
        node = schema_ld.article(self.meta())
        for key in ("description", "url", "image", "author", "publisher"):
            self.assertNotIn(key, node)


class TestFaqPage(unittest.TestCase):
    def test_statement_headings_are_refused(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.faq_page([("Background", "Some text.")])

    def test_question_form_is_accepted(self):
        node = schema_ld.faq_page([("What is drift?", "A retired model id.")])
        entity = node["mainEntity"][0]
        self.assertEqual(entity["@type"], "Question")
        self.assertEqual(entity["acceptedAnswer"]["@type"], "Answer")

    def test_empty_faq_is_refused(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.faq_page([])

    def test_empty_answer_is_refused(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.faq_page([("What?", "  ")])


class TestRender(unittest.TestCase):
    def test_single_node_is_not_wrapped_in_a_graph(self):
        out = schema_ld.render([schema_ld.organization("N", "https://n/")], script_tag=False)
        self.assertNotIn("@graph", out)

    def test_several_nodes_share_one_graph_and_one_context(self):
        nodes = [
            schema_ld.organization("N", "https://n/"),
            schema_ld.faq_page([("What?", "This.")]),
        ]
        payload = json.loads(schema_ld.render(nodes, script_tag=False))
        self.assertIn("@graph", payload)
        self.assertEqual(len(payload["@graph"]), 2)
        for node in payload["@graph"]:
            self.assertNotIn("@context", node, "context belongs on the graph, not each node")

    def test_script_tag_is_the_default(self):
        out = schema_ld.render([schema_ld.organization("N", "https://n/")])
        self.assertTrue(out.startswith('<script type="application/ld+json">'))

    def test_rendering_nothing_is_an_error(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.render([])


class TestMarkdownExtraction(unittest.TestCase):
    POST = (
        "---\ntitle: A post\ndate: 2026-08-05\ntags: [a, b]\n---\n\n"
        "Opening answer.\n\n"
        "## What is drift?\n\nA retired model id.\n\n"
        "## Background\n\nNot a question, so not a pair.\n\n"
        "## How do you catch it?\n\nPin the ids in a test.\n"
    )

    def test_frontmatter_is_parsed_and_stripped(self):
        fields, body = parse_frontmatter(self.POST)
        self.assertEqual(fields["title"], "A post")
        self.assertFalse(body.startswith("---"))

    def test_only_question_headings_become_pairs(self):
        _, body = parse_frontmatter(self.POST)
        pairs = extract_faq(body)
        self.assertEqual([q for q, _ in pairs], ["What is drift?", "How do you catch it?"])

    def test_answer_text_comes_from_the_paragraph_under_the_heading(self):
        _, body = parse_frontmatter(self.POST)
        self.assertEqual(dict(extract_faq(body))["What is drift?"], "A retired model id.")

    def test_no_frontmatter_is_not_an_error(self):
        fields, body = parse_frontmatter("# Just a post\n\nText.")
        self.assertEqual(fields, {})
        self.assertTrue(body.startswith("# Just a post"))


class TestLlmsTxt(unittest.TestCase):
    def test_renders_title_and_summary(self):
        out = schema_ld.llms_txt(name="Site", summary="What it is.", sections=[])
        self.assertIn("# Site", out)
        self.assertIn("> What it is.", out)

    def test_sections_render_as_link_lists(self):
        section = schema_ld.LlmsSection(title="Docs", links=[("A", "https://a/", "note")])
        out = schema_ld.llms_txt(name="S", summary="x", sections=[section])
        self.assertIn("## Docs", out)
        self.assertIn("- [A](https://a/): note", out)

    def test_empty_name_is_refused(self):
        with self.assertRaises(schema_ld.SchemaError):
            schema_ld.llms_txt(name="", summary="x", sections=[])


GOOD = (
    "# How to catch model drift before it breaks production\n\n"
    + "Model drift breaks silently because nothing distinguishes a live model id from a "
    "string that used to resolve. The fix is a test that pins every vendor id, asserts each "
    "registered provider is priced, and fails after a fixed interval without manual "
    "re-verification. In one collection this caught three dead endpoints.\n\n"
    "## What is model drift?\n\nA vendor retires a model on its own schedule.\n\n"
    "## How do you detect it offline?\n\nPin the identifiers in a test.\n"
)

BAD = (
    "# How to fix model drift\n\n"
    "In this article we'll explore vendor model drift and why it matters.\n\n"
    "## Background\n\nVendors retire models.\n\n"
    "## Our approach\n\nWe built something.\n"
)


class TestAeoLinter(unittest.TestCase):
    def test_well_structured_page_is_clean(self):
        code, label = lint_aeo.scan(GOOD).verdict()
        self.assertEqual(code, 0, label)

    def test_preamble_opening_is_flagged(self):
        rules = {f.rule for f in lint_aeo.scan(BAD).findings}
        self.assertIn("answer-first", rules)

    def test_statement_headings_are_flagged(self):
        findings = [f for f in lint_aeo.scan(BAD).findings if f.rule == "headings"]
        self.assertTrue(findings)

    def test_question_headings_are_counted(self):
        self.assertEqual(lint_aeo.scan(GOOD).stats["question_headings"], 2)

    def test_missing_opening_paragraph_blocks(self):
        text = "# Title\n\n## A section\n\nBody.\n"
        report = lint_aeo.scan(text)
        self.assertTrue(report.blocks)
        self.assertEqual(report.verdict()[0], 2)

    def test_comparison_page_without_a_table_is_flagged(self):
        text = (
            "# Hugo vs Astro for a static blog\n\n"
            + "Hugo builds faster on large sites while Astro ships less JavaScript, so the "
            "choice comes down to whether build time or client weight is the binding "
            "constraint for the project you are actually shipping right now today.\n\n"
            "## Which is faster?\n\nHugo.\n"
        )
        rules = {f.rule for f in lint_aeo.scan(text).findings}
        self.assertIn("comparison-table", rules)

    def test_comparison_page_with_a_table_passes(self):
        text = (
            "# Hugo vs Astro for a static blog\n\n"
            + "Hugo builds faster on large sites while Astro ships less JavaScript, so the "
            "choice comes down to whether build time or client weight is the binding "
            "constraint for the project you are actually shipping right now today.\n\n"
            "## Which is faster?\n\n| Tool | Build |\n|---|---|\n| Hugo | fast |\n"
        )
        rules = {f.rule for f in lint_aeo.scan(text).findings}
        self.assertNotIn("comparison-table", rules)

    def test_code_fences_do_not_count_as_prose(self):
        text = GOOD + "\n## Is this counted?\n\n```\n" + ("word " * 200) + "\n```\n"
        chunk_hits = [f for f in lint_aeo.scan(text).findings if f.rule == "chunk-size"]
        self.assertEqual(chunk_hits, [])

    def test_russian_question_headings_are_recognised(self):
        self.assertTrue(lint_aeo._is_question("Как поймать дрейф моделей"))
        self.assertTrue(lint_aeo._is_question("Что это такое?"))
        self.assertFalse(lint_aeo._is_question("Предыстория"))

    def test_verdict_is_independent_of_the_prose_linter(self):
        # The AEO report has its own severities; nothing here should import or
        # mutate the slop verdict.
        report = lint_aeo.scan(GOOD)
        self.assertFalse(hasattr(report, "hard_bans"))


if __name__ == "__main__":
    unittest.main()
