# Research methodology

How to plan query clusters, dedupe results, and decide when a fact is verified.

---

## Query clustering

Don't issue 10 queries on the same angle. Split the topic into 4-5 orthogonal clusters and run 2-4 queries per cluster.

### Cluster A — Foundational
What IS this thing, who started it, when, why does it exist.

Patterns:
- `"<topic>" definition site:<top-domain>`
- `<topic> history founder origin`
- `<topic> vs <closest-adjacent-concept>`
- `<topic> key actors companies people`

### Cluster B — Recent developments
Last 6-12 months. Always add a year tag.

Patterns:
- `<topic> 2026`
- `<topic> news <current-month>`
- `<topic> launch announcement`
- `<topic> trend <recent-year>`

### Cluster C — Contrarian / failure
Look for criticism, replication failures, retractions, "is X dead?" takes.

Patterns:
- `<topic> criticism problems`
- `is <topic> dead`
- `<topic> overhyped`
- `<topic> failures case study`
- `<topic> replication crisis` (for science topics)

### Cluster D — Numbers + studies
Quantitative + named research.

Patterns:
- `<topic> statistics <year>`
- `<topic> study results`
- `<topic> survey report`
- `<topic> market size`
- `<topic> growth rate`

### Cluster E — Primary sources (deep only)
Original papers, founder interviews, conference talks, company filings.

Patterns:
- `<topic> filetype:pdf`
- `<topic> interview founder`
- `<topic> keynote talk`
- `<topic> S-1 prospectus` (for SaaS / startups)
- `<topic> arxiv` (for AI/CS)

---

## Dedup rules

- **Same domain, same fact**: count once. Use the highest-authority page (e.g. company's official blog > a recap on TechCrunch > a Twitter screenshot).
- **Different domains, same exact quote**: only ONE source counts unless they're independently reporting it (vs. quoting each other). If three blogs cite the same TechCrunch article, that's still 1 source — TechCrunch.
- **Aggregator sites** (TechRadar / Tom's Guide / similar): treat as secondary; prefer the primary they're citing.
- **AI-generated articles** (telltale signs: generic structure, no author byline, recent domain registration, no editorial footprint): exclude. Note in "Out of reach" if it was the only source you found.

---

## Verification tiers

- **Verified**: ≥2 independent sources OR 1 primary source (company filing, founder statement, peer-reviewed paper).
- **Single-source**: exactly 1 secondary source. MUST be marked `[single-source]` in the brief.
- **Contradicted**: sources disagree. List both versions in Open Questions, don't pick a winner unless one is clearly more authoritative.
- **Unverified**: claim came up in your search but you can't find a source for it. → Open Questions.

---

## Source authority quick map

High authority (treat as primary):
- Company press releases, SEC filings, founder long-form posts
- Peer-reviewed journals, arXiv (note: arXiv is preprint — flag)
- Government statistical agencies (BLS, Eurostat, etc.)
- Established industry analysts with named methodology (Gartner, McKinsey, a16z research)

Mid authority:
- Established tech press (WSJ, FT, NYT, The Verge, Bloomberg, Reuters)
- Domain-specific publications (Nature News, Stratechery, Latent Space, Hacker News for tech)
- Academic Q&A (Stack Exchange answers with high upvotes + cited)

Low authority — corroborate before using:
- General-purpose blogs, Medium, Substack without track record
- Reddit (good for signal of community sentiment, weak for facts)
- Twitter/X (good for primary quotes from real accounts, weak for facts unless from verified expert)

Avoid:
- Content farms (often algorithmically generated)
- Affiliate-marketing sites disguised as reviews
- AI-summary sites with no original reporting

---

## Date handling

- Always note the source's publication date.
- For topics that change fast (AI, crypto, geopolitics): sources >12 months old should be flagged "<dated, may be outdated>".
- For topics that change slowly (history, definitions, math): older sources are fine.
- Quote dates from quoted material, not the article that quotes them.

---

## When to stop

Stop adding queries when:
- You've hit the depth target (3/7/15 by mode) AND found at least 5 distinct sources AND each cluster has ≥2 hits.
- New queries return the same domains you've already seen 3 times in a row.
- The topic is genuinely thin (very new, niche) — flag in "Out of reach" rather than pad with weak sources.
