# Schema types — which one, and what it needs

Tier 1 is the set that moves AI citation rates. Everything else is optional
detail that mostly does not pay for the maintenance.

| Type | Page it fits | Why it earns citations |
|---|---|---|
| `FAQPage` | anything with question headings | Highest impact — engines lift Q&A pairs verbatim, no interpretation needed |
| `HowTo` | process / tutorial | Steps are pre-chunked, so each is independently quotable |
| `Article` | everything else | Carries the E-E-A-T properties: author entity, dates, publisher |
| `Organization` | site-wide, once | Establishes the publisher entity the Article points at |
| `Person` | author page | Where `knowsAbout` actually lives |

---

## FAQPage

The one worth reaching for first. Google retired the FAQ **rich result** on
2026-05-07 — the expandable SERP block is gone and is not coming back — but the
markup stayed valid, and its job changed from click-through to citation.

Requirements enforced here:

- At least one pair.
- The question must end in `?`. A statement heading is rejected, because the
  point is verbatim extraction and a statement extracts as noise.
- The answer must be non-empty and should be self-contained — an engine quoting
  it will not carry the surrounding paragraph.

Generated automatically from question-form `##` / `###` headings plus the first
paragraph under each. If nothing is generated, the headings are statements;
`writer --aeo` flags exactly that.

## HowTo

For process-intent pages. Each step gets a `name` and a `text`. Keep the step
name short enough to read as a label and put the substance in the text — the
name is what appears in a summarised answer.

## Article

The properties that matter are not the obvious ones:

- **`author`** as a `Person` node, not a string. A bare name is not an entity.
- **`knowsAbout`** on that person, listing the topics they can be trusted on.
  This is where topical alignment between an author and a query is declared, and
  author authority became a direct ranking input in the March 2026 update.
- **`sameAs`** with profile URLs that corroborate the entity — GitHub, LinkedIn,
  a personal domain.
- **`dateModified`** alongside `datePublished`. Both feed freshness. An article
  with no modification date reads as abandoned.
- **`headline`** at 110 characters or fewer. Longer is rejected here; the type
  documents the limit and Google truncates past it.

## Organization

Site-wide, emitted once, usually on the home page. The `Article`'s `publisher`
field points at the same entity, so keep the `name` and `url` byte-identical
between the two or they resolve as different organisations.

## Person

The author page. Same node as the `author` inside an Article, plus `@context`.
Worth its own page: entity confidence is easier to establish when there is a URL
that describes the person and nothing else.

---

## The rule that can actually hurt you

Everything above either helps or does nothing. There is one exception.

**Schema that describes content not visible on the page is spam** under Google's
structured-data policy, and it draws a manual action rather than being ignored.
Marking up a FAQ that is not on the page, or claiming an author who did not
write it, is the one mistake in this file with a downside. Describe what is
there.
