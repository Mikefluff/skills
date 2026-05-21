# MCP probe — detecting and using Firecrawl + Exa

How to detect which external research MCPs are available, and what to do with them.

---

## Always-available (no probe needed)

- `WebSearch` — Google-style web search. Returns titles, URLs, snippets.
- `WebFetch` — fetches a specific URL and extracts the body content. Use AFTER WebSearch identifies promising URLs.

These are built-in Claude Code tools. No setup, always work.

---

## Optional MCPs (probe before using)

### Firecrawl MCP

**Tool prefix**: `mcp__firecrawl__*`

Common tools:
- `mcp__firecrawl__scrape` — deep scrape of a known URL (renders JS, follows redirects, returns clean markdown).
- `mcp__firecrawl__crawl` — multi-page crawl of a domain (follows internal links to a depth N).
- `mcp__firecrawl__search` — Firecrawl-powered web search with structured extraction.

**Best for**:
- Deep-dive on a specific company's site (pricing page + docs + blog all in one pass).
- Scraping documentation sites where WebFetch hits paywalls / rendering issues.
- Structured data extraction (pricing tables, feature matrices, customer logos).

**Don't use for**:
- Random web search (WebSearch is faster + cheaper).
- Sites that explicitly forbid scraping (respect robots.txt — Firecrawl does).

### Exa MCP

**Tool prefix**: `mcp__exa__*` (also sometimes `mcp__exa-search__*`)

Common tools:
- `mcp__exa__search` — neural/semantic web search. Better than Google for "find articles discussing the concept of X" rather than "find pages containing the words X".
- `mcp__exa__answer` — direct answer with cited sources.
- `mcp__exa__similar` — find pages similar to a given URL.

**Best for**:
- Finding non-obvious sources (academic-adjacent, niche newsletters, conference recaps).
- Searching by concept, not keyword (e.g. "essays arguing remote work is failing" surfaces actual essays, not job listings).
- Snowballing from one good source to other good ones via similar-search.

**Don't use for**:
- Time-sensitive news (Exa indexes lag a bit — use WebSearch for "today" or "yesterday" queries).
- High-volume queries (Exa is metered).

---

## Probe procedure

At skill startup, run a probe to detect what's available. The Claude Code runtime exposes available tools via the system prompt — check the deferred tools list or the active tool registry.

Pattern:

```text
1. Inspect the available tools list for tool names matching `mcp__firecrawl__*`.
2. If present → Firecrawl mode unlocked. Note `firecrawl: yes` in the brief metadata.
3. Same for `mcp__exa__*`.
4. If neither present → standard mode. WebSearch + WebFetch only.
```

If the user passes `--sources websearch,webfetch,firecrawl` but Firecrawl isn't installed, do NOT crash. Print:

> _(Skipped Firecrawl — MCP not configured. Install: see https://github.com/firecrawl/firecrawl-mcp )_

…and proceed with the remaining sources.

---

## Query plan by available source set

### Standard (WebSearch + WebFetch only)

1. Run WebSearch on every cluster query.
2. WebFetch the top 2-3 results per cluster for full content.
3. Extract facts from WebFetch'd content + WebSearch snippets.

### Standard + Firecrawl

1. Run WebSearch as above.
2. For any RESULT URL that points to a domain with rich content (company official site, documentation hub, multi-page guide):
   - Use `mcp__firecrawl__scrape` for clean markdown extraction (better than WebFetch on JS-heavy pages).
   - Optionally `mcp__firecrawl__crawl` if the question requires multiple pages from same domain.
3. WebFetch the rest.

### Standard + Exa

1. Run WebSearch on Cluster A (foundational) — these are usually well-indexed.
2. Run `mcp__exa__search` on Cluster B (recent) + Cluster C (contrarian) — semantic search finds these better.
3. For one strong source found: run `mcp__exa__similar` to find adjacent strong sources.
4. WebFetch top results for content extraction.

### Deep (all available)

1. Cluster A: WebSearch
2. Cluster B: WebSearch + Exa
3. Cluster C: Exa
4. Cluster D: WebSearch
5. Cluster E: Firecrawl crawl on 1-2 primary domains identified in earlier clusters
6. WebFetch / Firecrawl scrape for content extraction

---

## Failure modes

- **MCP timeout / 500**: print `(MCP <name> errored — skipping this query)` and continue with WebSearch fallback.
- **All sources empty**: don't fabricate. Return a brief with whatever was found + extensive "Out of reach" section.
- **Rate limit hit on WebSearch**: pause 30s, retry once, then proceed with what you have.

The brief always saves SOMETHING — even a 3-fact brief with one source is more useful than a crash.
