# Sources — what to trust, when to escalate

Detailed reference for picking sources. Used at step 5 (extract).

---

## Tier 1 — Primary

Direct from the source. Treat as authoritative unless the source itself is dubious.

| Type | Examples | Notes |
|---|---|---|
| Company official | press releases, official blog, S-1 filings, annual reports, product changelogs | Sole authority for what the company itself says about itself. Watch for marketing spin on third-party claims. |
| Founder / executive | named long-form post, conference keynote, podcast appearance | Quote directly. Note that a founder's opinion is not industry consensus. |
| Peer-reviewed paper | journal article with DOI | High trust on methodology. Cite as `<authors et al., <journal>, <year>`. |
| Preprint | arXiv, bioRxiv, SSRN | Annotate `[preprint, not peer-reviewed]`. |
| Government / regulator | SEC, FTC, EU Commission, BLS, ONS | Trustworthy for raw data; their interpretations carry institutional bias. |
| Court filing | direct PDFs from PACER, public dockets | Authoritative for what was said in litigation. |

---

## Tier 2 — Established secondary

Reputable journalism + named industry analysis. Most facts in a brief will come from here.

| Type | Examples |
|---|---|
| Tier-1 business press | WSJ, FT, Bloomberg, Reuters, NYT, Economist |
| Tier-1 tech press | The Verge, Wired, MIT Tech Review, Stratechery (Ben Thompson), Latent Space |
| Industry analysts | Gartner, IDC, Forrester, a16z, Y Combinator essays, Stripe / OpenAI / Anthropic posts |
| Academic-adjacent | Quanta, Nautilus, Aeon, Nature News, Science News |

These get cited freely. Note publication + date. Be aware of paywalls — note if the link is gated.

---

## Tier 3 — Use with corroboration

Useful for trend signal, weaker for facts.

| Type | Use for | Don't use for |
|---|---|---|
| Reddit (relevant subreddit) | community sentiment, user pain points, anecdata | factual claims about companies, products, statistics |
| Hacker News | technical discussion, contrarian takes, primary-source aggregator | as a citation by itself |
| Twitter / X (verified accounts of named experts) | primary quotes, breaking news | second-hand claims, "I heard that..." |
| Substack / Medium with track record | analyst takes, long-form opinions | numerical claims unless they show source |
| Stack Exchange (highly-voted answers) | technical specifics | non-technical generalities |

For a Tier 3 source: ALWAYS pair with at least one Tier 1 or Tier 2 source.

---

## Tier 4 — Avoid

These almost never make a brief stronger:

- Content-farm sites (TopNarcissist101.com / RankBestBlender.com etc — search-spam shape)
- Affiliate review sites disguised as journalism
- AI-summary sites with no original reporting (telltale: generic structure, no byline, vague claims)
- Twitter/X anonymous accounts unless the screenshot itself is the news
- Quora answers (low signal-to-noise, sometimes literally AI)

If a Tier 4 source is your ONLY hit on a fact: list the fact in Open Questions, not as a verified claim.

---

## When to escalate to deep mode

Some topics return mostly Tier 3 or 4 on standard depth. Indicators that you should re-run with `--depth deep`:

- Less than 3 Tier 1/2 sources in your initial 7-10 queries
- Multiple contradicting facts from low-authority sources
- The topic is industry-niche (vertical SaaS, specific scientific subfield, narrow geographic market) — primary sources hide in PDFs and conference proceedings
- The topic is new (<3 months old) — established secondary press hasn't caught up

In `--depth deep`, prioritize Cluster E (primary sources). Use Firecrawl MCP if available to deep-crawl specific company sites; use Exa MCP for semantic discovery of non-obvious sources.

---

## Multilingual sources

For topics with strong non-English signal (a brand campaign in Asia, a regulatory shift in Brazil, a Russian-language community):

- Don't skip non-English sources just because the brief is in English. Quote in original + provide translation: `> "<orig>" — translated: "<en>" — <attribution>`.
- Mark `[non-EN source]` in citations so the reader knows to verify with their own knowledge.
- For numbers: include the original currency / unit if not USD / SI — add conversion in parens.

---

## Out-of-reach flagging

The brief MUST have an "Out of reach / requires expertise" section IF any of:

- Paywalled primary sources you couldn't access (Bloomberg Terminal, JSTOR locked, vendor's enterprise white paper behind a form)
- NDA-protected info (private market valuations, internal company numbers)
- Vendor-specific pricing not on public pages (Salesforce / Oracle / IBM enterprise pricing)
- Real-time data the brief shouldn't claim (current stock prices, today's API quotas)
- Topics where the brief writer (you / the AI) genuinely lacks domain expertise to evaluate — say so

Flag these so the downstream user knows what to fill in themselves.
