---
name: research-brief
description: "Produce a structured research brief on any topic — TL;DR, key facts with citations, notable quotes, suggested angles, open questions. 3-15 queries by depth, multi-source (WebSearch + WebFetch + optional Firecrawl/Exa MCP). Output is a markdown file ready for downstream consumption by carousel-builder, reel-builder, viral-text, essay-write, landing-copy. Use when the user says 'research X', 'gather facts on Y', 'brief me on Z', 'what's known about W', 'prepare research for a post / carousel / reel about Q'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
  - Bash
  - Grep
  - Glob
---

<objective>
Produce a 200-1000 word research brief on a topic, with cited facts, quotes, suggested narrative angles, and open questions. Save to a markdown file under `./generated/research/<topic-slug>.md` so downstream skills can ingest via `--research <path>`.

This skill does NOT:
- write the final post / carousel / reel (that's `essay-write` / `viral-text` / `carousel-builder` / `reel-builder`)
- run literature reviews requiring paywalled sources (Google Scholar, Pubmed — flag those as `out-of-reach` in the brief)
- give real-time prices / stocks / API quotas (use a dedicated tool, not WebSearch)
- replace primary-source domain research where the user already has expertise — the brief is a STARTING point, not a final word

Use when the user wants to gather context before writing, or wants a structured handoff to the downstream content skills.
</objective>

## ROLE

Read the topic → choose depth + sources → run search queries → extract facts with citations → synthesize into the canonical brief structure → save to `./generated/research/<slug>.md` → return the path so other skills can pick it up.

## PIPELINE

1. **Clarify if topic is broad**. "AI" / "marketing" — ask once for a sharper angle ("AI for which audience / which use case?"). Otherwise proceed.

2. **Pick depth**:
   - `--depth quick`: 3-5 WebSearch queries, 200-400 word brief. ~1-2 min wall time.
   - `--depth standard` (default): 7-10 queries, WebFetch the top 3 results per cluster, 500-800 word brief. ~3-5 min.
   - `--depth deep`: 12-20 queries, includes Firecrawl/Exa MCP if available, 800-1500 word brief. ~5-10 min.

3. **Probe available sources** (see `references/mcp-probe.md`):
   - `WebSearch` — always available inside Claude Code.
   - `WebFetch` — always available.
   - `mcp__firecrawl__*` — present if the user has Firecrawl MCP installed. Best for deep-crawl scrape of a known site.
   - `mcp__exa__*` — present if Exa MCP installed. Best for neural/semantic search and finding non-obvious sources.
   - Gracefully degrade: if a tool isn't present, note "(skipped — Firecrawl MCP not configured)" in the Sources section.

4. **Run query batches** — see `references/methodology.md`:
   - Cluster A: foundational definitions (what is X, history, key actors). 2-4 queries.
   - Cluster B: recent developments / news (last 6-12 months). 2-4 queries.
   - Cluster C: contrarian / failure modes / criticism. 1-3 queries.
   - Cluster D: data + numbers + named studies. 2-4 queries.
   - Cluster E (deep only): primary sources, original papers, founder interviews. 2-5 queries.

5. **Extract**: for each result, pull facts with the source URL, distinguishing between:
   - **Verified facts** (≥2 corroborating sources OR a primary source)
   - **Single-source claims** (note as such — `[single-source]`)
   - **Quotes** (named attribution + URL + access date)
   - **Open questions** (claims that couldn't be verified — list them as research gaps, don't fabricate confirmations)

6. **Synthesize into canonical structure** (see `references/output-format.md`):
   ```
   # <Topic>

   _Brief generated: <date>. Sources used: <N>. Depth: <quick|standard|deep>._

   ## TL;DR
   <3-sentence summary>

   ## Key facts
   - <fact> [#1]
   - <fact> [#2]
   - ...

   ## Notable quotes
   > "<quote>" — <attribution>, <publication>, <date> [#N]

   ## Suggested angles
   1. <angle one> — for <audience/format>
   2. <angle two> — ...
   3. <angle three> — ...

   ## Open questions
   - <unresolved question that came up>
   - ...

   ## Out of reach / requires expertise
   - <flag for things the user should verify manually>

   ## Sources
   1. [<title>](<url>) — accessed <YYYY-MM-DD>
   2. ...
   ```

7. **Write to disk**: `./generated/research/<topic-slug>-<YYYYMMDD>.md`. Slug = `kebab-case-of-topic`, max 40 chars. If file exists, append timestamp.

8. **Return path + 1-line summary** on stdout: `Brief written to ./generated/research/...md (N sources, TL;DR: ...)`.

## MODES

- `research-brief <topic>` — default standard depth
- `research-brief <topic> --depth quick|standard|deep` — control breadth
- `research-brief <topic> --sources websearch,webfetch,firecrawl,exa` — restrict to specific tools (default: all available)
- `research-brief <topic> --output <path>` — custom output path
- `research-brief <topic> --format brief|outline|article-ready` — controls verbosity (200 / 500 / 1000+ words)
- `research-brief <topic> --angles 3` — number of suggested narrative angles in the output (default 3)
- `research-brief <topic> --lang en|ru|mixed` — write the brief in that language (sources can be any)
- `research-brief <topic> --for carousel|reel|post|essay|landing` — bias the angles + structure toward a downstream format

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/methodology.md](references/methodology.md) | Always at step 4 — cluster definitions + query patterns + de-dup rules |
| [references/sources.md](references/sources.md) | Picking sources — what to trust, what to flag, primary vs. secondary, when to escalate to deep |
| [references/output-format.md](references/output-format.md) | Step 6 — exact section structure, citation format, slug rules, multilingual handling |
| [references/mcp-probe.md](references/mcp-probe.md) | Step 3 — how to detect Firecrawl/Exa MCP presence, what each adds, graceful fallback |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: standard depth on a tech topic (productivity software), quick depth on a cultural topic (a brand campaign), deep depth on a niche business topic (vertical AI in a specific industry).

## CONSTRAINTS

- **Cite every non-trivial claim.** Inline `[#N]` markers tied to the Sources list. No source = put it in "Open questions" instead of presenting as fact.
- **Don't fabricate sources.** If WebSearch returns nothing solid, say so. A short brief with 5 real sources beats a long one with invented ones.
- **Distinguish verified vs. single-source.** Two corroborating sources OR a primary source → verified. One link → mark `[single-source]` next to the fact.
- **Quote attributions need a person OR org + publication + date.** Anonymous "experts say" — don't include.
- **Date every source** with access date. Web changes fast — note when you read it.
- **Suggested angles must reference a specific downstream format** (carousel, reel, essay) — generic "you could write about X" is useless.
- **Open questions are mandatory** for `--depth standard` and `--depth deep`. The list of things you DIDN'T resolve is half the value.
- **Out of reach flag** — paywalled papers, NDA-protected info, vendor-specific pricing — list them, don't fake answers.
- **Output file path is always returned** on stdout, last line. Downstream skills parse for `--research <path>` ingestion.
- **Don't run the actual research if the file already exists for today's topic-slug + date** unless `--force-refresh` was passed. Print existing path and ask if user wants to refresh.
- **Language**: brief body follows `--lang`. Sources can be any language — translate quotes when needed, keep original in a `(original: ...)` annotation.
- **Never insert hype words** ("revolutionary", "game-changing", "stunning"). The brief is dry intelligence, not marketing.
- **Don't promote your own confidence**. If a source is weak, say "single blog post, no corroboration" — don't pad with "industry sources suggest".

## INVOCATION HINTS

When the user says any of:
- "research X", "look up X", "what's known about X"
- "gather facts on Y", "brief me on Y", "give me a primer on Y"
- "prepare research for a post / carousel / reel / video on Z"
- "what's the current state of X", "trends in X right now"
- "find sources for X", "verified facts about X"
- "I need numbers / stats / quotes on X"

RU triggers:
- «исследуй X», «собери информацию по Y»
- «что известно про X», «подготовь ресерч по X»
- «факты по теме X с источниками»
- «найди источники / цитаты / цифры по X»
- «бриф по X», «справку по X»

Defaults: `--depth standard --format brief --angles 3 --lang <user-message-language>`.

This skill is the upstream for `carousel-builder` and `reel-builder` — they accept `--research <path>` and ingest the brief automatically. Chain: `research-brief "topic" → carousel-builder --research ./generated/research/topic-YYYYMMDD.md` → 8 slides on the same topic with cited facts.
