# SEO meta + Open Graph + Twitter cards

Every page has three "preview" surfaces: Google search result, Facebook/LinkedIn share, X (Twitter) share. Each has its own char limit + best practices.

> **These surfaces are necessary and no longer sufficient.** Everything below is
> about being *clicked* from a results page. A growing share of queries never
> reach one: the answer is assembled by an engine that cites a handful of
> sources. Getting cited is decided by different things — page structure and
> structured data — and neither is a meta tag.
>
> The split is measurable. Of the pages an engine cites, the overlap with
> Google's own organic top-10 is about 76% for AI Overviews, 28% for Perplexity
> and **8% for ChatGPT**. Ranking well is close to unrelated to being quoted by
> ChatGPT.
>
> So treat this file as one of three layers:
>
> | Layer | What it decides | Where it lives |
> |---|---|---|
> | Meta + OG + cards | whether a human clicks | this file |
> | Page structure | whether an engine can extract a passage | `writer --aeo` |
> | Structured data | whether an engine picks yours to quote | [`schema-maker`](../../schema-maker/SKILL.md) |

---

## Page title (HTML `<title>`)

Used by:
- Browser tab
- Google search result (clickable headline)
- Open Graph fallback if `og:title` missing

### Length

- **Hard limit**: ~60 characters before Google truncates with "..."
- **Sweet spot**: 50-60 characters
- Mobile Google shows less (~45-50 chars) — front-load the keyword

### Pattern

```
{primary keyword + benefit} | {brand}
```

OR for category-broad pages:

```
{Category} — {differentiator} | {brand}
```

### Examples (homepage)

| ❌ Weak | ✅ Strong |
|---|---|
| `Welcome to Acme - The Best CRM` | `CRM for Solo Founders — Track Deals in 60s \| Acme` |
| `Notion - Your Workspace` | `Notion: All-in-One Workspace for Notes & Tasks \| Notion` |
| `Acme - We Help You Build Apps` | `Build apps without code in a weekend \| Acme` |

### Examples (category pages)

| Page type | Title pattern | Example |
|---|---|---|
| Homepage | `{primary value} — {qualifier} \| {brand}` | "CRM for Solo Founders — Track Deals in 60s \| Acme" |
| Pricing | `Pricing — {qualifier} \| {brand}` | "Pricing — Free for Solo, Affordable for Teams \| Acme" |
| Features | `{Feature category} — {benefit} \| {brand}` | "AI Code Review — Catch Bugs Before PR Merge \| Acme" |
| Blog post | `{Post topic} \| {brand} Blog` | "How to write a CRM in a weekend \| Acme Blog" |
| Comparison | `{Brand} vs {competitor} — {qualifier}` | "Acme vs Salesforce — Pricing & Features Compared" |

### Title anti-patterns

- ❌ Brand name first ("Acme - CRM for Solo Founders") — wastes the most-clicked-on real estate
- ❌ Keyword stuffing ("CRM Software Best CRM Top CRM 2026") — both Google-penalty and trust-destroying
- ❌ Generic ("Home page" / "Welcome" / "About us") — fails the search-result test
- ❌ All caps ("BEST CRM EVER") — Google may rewrite, looks spammy
- ❌ Question without answer hint ("Looking for a CRM?") — no value-prop visible

---

## Meta description

Used by:
- Google search result snippet (below the title)
- Sometimes (rare) other search engines / aggregators

### Length

- **Hard limit**: ~155-160 characters before Google truncates with "..."
- **Sweet spot**: 150-155 characters
- Mobile shows less (~120) but Google adapts; don't optimize for mobile-only

### Pattern

```
{one-sentence value prop with specific number/proof} {primary CTA hint}
```

### Examples (homepage)

| ❌ Weak | ✅ Strong |
|---|---|
| `Welcome to Acme. We offer the best CRM software for small businesses. Sign up today.` | `Acme is the CRM for solo founders. Track deals, automate follow-ups, no team licenses. Free for 25 contacts.` |
| `Acme is a powerful note-taking app with many features.` | `Acme combines notes, wikis, and project tracking. Used by 10,000+ teams. Free forever for personal use.` |

### Pattern variations

| Goal | Pattern | Example |
|---|---|---|
| Product overview | "{Product} {does X} for {audience}. {Differentiator}. {Free CTA or proof}." | "Acme is the CRM for solo founders. Track deals + automate follow-ups, no team seats. Free for 25 contacts." |
| Pricing page | "Plans from {price}. {Free option}. {Trust signal}." | "Plans from $0. Free for 10 users. Cancel anytime, no card required for free." |
| Feature page | "{Feature} {does X}. {Specific benefit + number}. {CTA}." | "AI Code Review catches bugs before your reviewer does. Avg 60% review-time reduction. Free for first 10 PRs/month." |
| Blog post | "{Post benefit}. {Length / format signal}. {Optional CTA}." | "Step-by-step guide to writing a CRM in a weekend. 12-minute read with code samples." |

### Meta description anti-patterns

- ❌ Repeating the title verbatim
- ❌ "Welcome to..." — wasted opening
- ❌ "Click here to learn more" — useless
- ❌ Sounding like a tweet ("We just launched! 🚀") — wrong register
- ❌ No specific value (just adjectives strung together)
- ❌ Calls to action without context ("Sign up today" — for what?)

---

## Open Graph (`og:` tags)

Used by:
- Facebook share preview
- LinkedIn share preview
- iMessage / WhatsApp / Slack / Discord link previews
- Generally: any platform that reads OG metadata

### Standard tags

```html
<meta property="og:type" content="website" />
<meta property="og:title" content="{Title — ≤60 chars}" />
<meta property="og:description" content="{Description — ≤200 chars}" />
<meta property="og:image" content="{1200×630px image URL}" />
<meta property="og:url" content="{canonical page URL}" />
<meta property="og:site_name" content="{Brand name}" />
```

### Differences vs SEO meta

| Surface | Title chars | Description chars | Special notes |
|---|---|---|---|
| `<title>` + `og:title` | ~60 | — | Usually identical |
| Meta description | — | ~155-160 | For search engines |
| `og:description` | — | ~200 | Slightly longer than meta description allowed |
| `og:image` | — | — | 1200×630px recommended (Facebook); LinkedIn uses 1200×627 |

### Pattern

`og:title` can usually equal `<title>`. `og:description` can be slightly more conversational than the meta description (since it appears in social shares, not search):

```html
<title>CRM for Solo Founders — Track Deals in 60s | Acme</title>
<meta name="description" content="Acme is the CRM for solo founders. Track deals + automate follow-ups, no team seats. Free for 25 contacts." />
<meta property="og:title" content="CRM for Solo Founders — Track Deals in 60s | Acme" />
<meta property="og:description" content="Track deals + automate follow-ups in 60 seconds. Free for 25 contacts. Built for solo founders who never need to share with a team." />
```

---

## Twitter cards (`twitter:` tags)

Used by:
- X (Twitter) share preview

### Two card types

| Type | When to use |
|---|---|
| `summary` | Default; small thumbnail + title + description |
| `summary_large_image` | Big preview with hero image; preferred for marketing pages |

### Tags

```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{Title — ≤70 chars}" />
<meta name="twitter:description" content="{Description — ≤200 chars}" />
<meta name="twitter:image" content="{1200×675px image URL — note Twitter's 16:9 ratio}" />
<meta name="twitter:site" content="@{brand-handle}" />
<meta name="twitter:creator" content="@{author-handle}" />  <!-- for blog posts -->
```

### Twitter-specific notes

- `twitter:image` is 1200×675px (16:9) — different from OG's 1200×630
- `twitter:description` can be slightly longer; X truncates at ~200 chars
- Card preview only appears on web Twitter; mobile X may show different render

---

## Per-page-type templates

### Homepage

```html
<title>{Primary value} for {audience} — {qualifier} | {Brand}</title>
<meta name="description" content="{Brand} {does X} for {audience}. {Differentiator}. {Pricing hint or free CTA}." />
<meta property="og:title" content="{Primary value} for {audience} — {qualifier} | {Brand}" />
<meta property="og:description" content="{Conversational version of the description, 1-2 sentences}." />
<meta property="og:image" content="{Hero illustration or product screenshot, 1200×630}" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{1200×675 variant of og:image}" />
```

### Pricing page

```html
<title>Pricing — {Free option + price range} | {Brand}</title>
<meta name="description" content="Plans from {free or price}. {Free option}. {Trust signal — cancel anytime / no card needed}." />
```

### Feature / product page

```html
<title>{Feature name} — {Benefit} | {Brand}</title>
<meta name="description" content="{Feature} {does X}. {Specific benefit + number if available}. {Proof / customer name if relevant}." />
```

### Blog post

```html
<title>{Post topic} | {Brand} Blog</title>
<meta name="description" content="{Post benefit summary}. {Length / format signal}. {Optional CTA at end}." />
<meta property="og:type" content="article" />
<meta property="article:author" content="{Author name}" />
<meta property="article:published_time" content="{ISO datetime}" />
<meta name="twitter:creator" content="@{author-handle}" />
```

### Comparison page

```html
<title>{Brand} vs {Competitor} — Pricing & Features Compared</title>
<meta name="description" content="{Brand} and {Competitor} compared on pricing, features, target use. {Brand} wins for {audience}; {Competitor} wins for {other audience}." />
```

---

## SEO-meta anti-patterns (all surfaces)

❌ Keyword stuffing ("CRM software best CRM 2026 CRM for startups CRM tool")
❌ Brand name first ("Acme - CRM for...")  — saves the most-clicked real estate for keyword
❌ Generic openers ("Welcome" / "Home" / "Our")
❌ All caps
❌ Title and meta description identical (waste of meta description)
❌ Sounding like an ad ("Click now! Special offer!")
❌ Promising what the page doesn't deliver (clickbait gets penalized + erodes trust)
❌ Missing meta description (Google generates its own from page content — usually worse)
❌ Forgetting to set `og:image` (Facebook / LinkedIn render no preview → drastically lower CTR)

---

## SEO-meta WIN patterns

✅ Front-load the keyword in title
✅ Specific value prop in description (number, name, outcome)
✅ Brand at the end of title (Google reads left-to-right; users do too)
✅ Conversational `og:description` (humans share these, not robots)
✅ High-quality `og:image` — clear, with text overlay if useful, branded
✅ Title length 50-60 chars; description 150-155 chars; one strong sentence each
✅ Different titles per page (don't have "Acme | All Your Needs" on every page)

---

## Structured data — the layer that decides citation

Schema used to buy a rich result. Google retired the FAQ rich result on
2026-05-07, and the expandable SERP block went with it. The markup did not stop
mattering; it changed job. Answer engines parse `FAQPage` first when choosing
whose answer to quote, and pages carrying Tier 1 types turn up in AI summaries
markedly more often than pages without.

What to add, in order of payoff:

| Type | Page | Note |
|---|---|---|
| `FAQPage` | anything with question headings | Highest impact — pairs lift verbatim |
| `HowTo` | tutorials, processes | Steps are pre-chunked, each independently quotable |
| `Article` | blog posts | Carries the author entity and both dates |
| `Organization` | site-wide, once | The publisher entity `Article` points at |

Generate it rather than hand-writing it:

```bash
python3 -m common.runners.cli.schema --from ./post.md \
  --url "https://you.dev/posts/slug/" \
  --author-name "Your Name" --knows-about "CRM,sales ops"
```

Three properties do disproportionate work and are easy to leave out:

- **`author` as a `Person` node**, not a string. A bare name is not an entity.
- **`knowsAbout`** on that person. Author authority became a direct ranking
  input in the March 2026 update, and this is where topical alignment is stated.
- **`dateModified`** as well as `datePublished`. Both feed freshness; a page with
  no modification date reads as abandoned regardless of when it last changed.

**The one thing here that can hurt.** Schema describing content that is not
visible on the page is spam under Google's structured-data policy and draws a
manual action. Every other item in this file either helps or does nothing;
this one has a downside. Describe what is actually there.

---

## Writing the meta so an engine can use it too

Small changes that serve both surfaces:

- **Meta description as a standalone claim.** Written as a complete sentence with
  the specific number in it, it can be lifted as an answer. Written as a teaser
  ("Find out how we…"), it cannot.
- **Question-form `<title>` for question-intent pages.** Engines match headings
  and titles against queries, and queries are questions.
- **Comparison pages need a table on the page**, not just in the description.
  Comparison queries are answered from tables far more often than from prose.

---

## Cross-references

- Char limits for every surface: [`char-limits.md`](char-limits.md)
- What to strip: [`banned-patterns.md`](banned-patterns.md)
- Hero writing (related, longer-form): [`hero-formula.md`](hero-formula.md)
- Structured data generation: [`schema-maker`](../../schema-maker/SKILL.md)
- Extractability check: `python3 skills/writer/scripts/lint.py <file> --aeo`
