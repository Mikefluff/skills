---
name: schema-maker
description: "Generate JSON-LD structured data (Article, FAQPage, HowTo, Organization, Person with knowsAbout) and llms.txt from a markdown post. Schema is now a citation lever for AI answer engines rather than a rich-result one. Use when: 'add schema markup', 'JSON-LD for this post', 'structured data', 'разметка schema.org', 'llms.txt'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Turn a finished markdown post into the structured data that decides whether an
answer engine can quote it. Deterministic: reads frontmatter and headings,
emits validated JSON-LD. No model call, no network.
</objective>

## ROLE

Structured data used to be about rich results in Google. That era ended on
2026-05-07, when Google retired the FAQ rich result. The markup did not stop
mattering — it changed job. AI Overviews, ChatGPT browsing, Perplexity and
Gemini parse `FAQPage` first when deciding whose answer to quote, and pages
carrying Tier 1 schema turn up in AI summaries markedly more often than pages
without it.

So this skill optimises for citation, not for a SERP widget.

Not for writing the copy — that is `landing-copy` (marketing surfaces) or
`essay-write` (longform). Not for checking whether the prose is extractable —
that is `writer --aeo`. This skill assumes the text exists and describes it.

## PIPELINE

1. **Read the post.** Frontmatter supplies title, date, description and tags.
   The body supplies the FAQ pairs.

2. **Extract Q&A automatically.** Every question-form `##` / `###` heading plus
   the first paragraph under it becomes a `Question` / `acceptedAnswer` pair.
   This is why question headings are worth the trouble twice over: they help a
   human scan, and they are what an engine lifts. Run `writer --aeo` first if
   the headings are still statements.

3. **Attach the author entity.** `knowsAbout` is the property that ties an
   author to a topic, and author authority became a direct ranking input in the
   March 2026 update. An author node without `knowsAbout` and `sameAs` is a
   name, not an entity.

4. **Emit one graph.** Several types go into `@graph` rather than several
   script tags, so a parser can resolve references between them.

5. **Paste into the page head.** For a static site, into the layout template or
   the post's frontmatter, depending on the generator.

```bash
python3 -m common.runners.cli.schema --from ./post.md \
  --url "https://you.dev/posts/model-drift/" \
  --author-name "Your Name" --author-url "https://you.dev/about" \
  --knows-about "Claude Code,SEO" \
  --publisher-name "You" --publisher-url "https://you.dev"
```

## MODES

- `--from <file.md>` — read frontmatter + body
- `--types article,faq,organization` — which nodes to emit (default `article,faq`)
- `--url` — canonical URL of the page
- `--author-name` / `--author-url` / `--knows-about` / `--same-as` — the author entity
- `--publisher-name` / `--publisher-url`
- `--date-modified` — ISO date; defaults to `datePublished`
- `--raw` — omit the `<script>` wrapper
- `--llms-txt --site-name X --site-summary Y` — render an llms.txt instead

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/types.md](references/types.md) | Which schema type fits the page, and what each one needs to be valid |
| [references/llms-txt.md](references/llms-txt.md) | Before promising anything about llms.txt — the honest state of the convention |

## CONSTRAINTS

- **Never describe content that is not on the page.** Schema that disagrees with
  the visible text is spam under Google's structured-data policy, and it is the
  one failure here that can cost a manual action rather than just doing nothing.
- **FAQ questions must be questions.** A statement in a `Question` node is
  rejected rather than emitted — the whole value is that engines lift the pair
  verbatim, and a statement defeats it.
- **`dateModified` is not optional in practice.** Freshness is read from both
  dates. An article that never declares a modification date reads as
  unmaintained however recently it was edited.
- **Headlines over 110 characters are rejected.** The Article type documents the
  limit and Google truncates past it.
- **Do not oversell llms.txt.** It is a community convention with no standards
  body and no vendor committed to reading it in production. Cheap and harmless,
  not a lever.
