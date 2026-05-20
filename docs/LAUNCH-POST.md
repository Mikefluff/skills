# Launch post drafts

Copy-pasteable drafts for X, LinkedIn, Substack, Hacker News, and awesome-claude-code submissions. Pick the one matching the audience; edit before posting if needed.

All drafts pass `writer/scripts/lint.py` cleanly (verified — no AI-slop tells in the launch material itself).

---

## X / Twitter — single tweet (≤280 chars)

```
Open-sourced our Claude Code prose-editing skills collection.

11 skills layered on one regex linter that catches 23 categories of LLM-prose tells (EN + RU). Wrappers for viral posts, fiction, non-fiction, cold email, tone-shifting.

Install with one curl. MIT.

github.com/Mikefluff/skills
```

(265 chars including URL)

---

## X / Twitter — thread (7 tweets)

```
1/ Spent the last quarter building Claude Code skills for editing prose without the LLM-tells.

Now open-sourced: 11 skills, one base linter, MIT.

github.com/Mikefluff/skills

A thread on what's in it.
```

```
2/ The base is `writer` — an offline Python linter that catches 23 categories of regex-detectable AI prose:

- "It's important to note..."
- "delve into the rich tapestry of..."
- "in today's fast-paced world..."
- intensifier ladders ("truly remarkable")
- balance hedges
- comma-splices
...
```

```
3/ EN + RU rules side by side. The RU coverage is deeper (was built for a long-form Russian writing project first), but EN is a first-class citizen with 18+ regex categories now firing on synthetic neuroslop.
```

```
4/ Wrappers compose on top:

- `viral-text` — hooks + numbered points + NLP question + CTA. EN viral patterns.
- `prose-edit` — fiction rewrite (Pelevin / Manson voice vectors)
- `essay-write` — non-fiction longread w/ source-backed claims
- `tone-shifter` — casual ↔ business-formal ↔ academic
- `cold-email` — 5-block structure, ≤120-word budget
```

```
5/ Plus 3 linters that produce reports, never mutate:

- `style-check` — pre-commit prose gate
- `translation-sync` — RU↔EN↔PT-BR parity check
- `canon-check` — story-bible consistency for fiction
```

```
6/ Installation is one curl. Works inside Claude Code (skill discovery via `description:` field). Docker image also available for CI:

docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md
```

```
7/ Code: github.com/Mikefluff/skills
Docs: github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md

If you write a lot and your output is starting to look like Claude — try the offline linter first:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

---

## LinkedIn (1 long post)

```
We just open-sourced Mikefluff/skills — a collection of 11 Claude Code skills for editing prose that doesn't read like LLM output.

What's in the box:

→ writer — a pure-Python regex linter that catches 23 categories of AI-prose tells (EN + RU). Patterns like "It's important to note that...", "delve into the rich tapestry of...", intensifier ladders ("truly remarkable", "deeply important"), balance hedges, comma-splices, em-dash abuse. Runs offline in ~50ms.

→ Six wrappers that compose on the linter: viral-text for social posts, prose-edit for fiction, essay-write for non-fiction longreads, pelevin-digression for opinionated voice inserts, tone-shifter for register changes (casual ↔ business-formal ↔ academic), cold-email for outreach with a strict 5-block structure and 120-word budget.

→ Three read-only linters: style-check (pre-commit prose gate), translation-sync (multilingual parity for RU/EN/PT-BR books), canon-check (story-bible consistency for fiction).

Why we built it:

LLMs make writing easier but the output reads identical across users. The collection encodes the specific patterns that make LLM prose recognizable, then strips them. The base linter is high-recall by design — it'll false-positive on legitimate prose sometimes, accepted as the cost of catching what matters.

Five-second install:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

Or pull the Docker image for CI integration:

docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint-all /work

MIT license. No external deps. Works inside Claude Code via skill discovery.

GitHub: github.com/Mikefluff/skills

If you've shipped enough LLM-assisted writing that your output is starting to sound like Claude — try the offline linter on your last draft. Best signal-to-noise gain for the time invested I've shipped this year.
```

---

## Substack / blog (longer form)

```
# I'm tired of my writing sounding like Claude

I've been writing with LLMs for two years. The output saves time. The output also reads more and more like everyone else's LLM output. "It's important to note that..." "delve into..." "rich tapestry of..." "navigate the complexities..." — every LinkedIn post, every product update, every newsletter.

So I built a tool that strips them. Then I extended it. Now it's 11 Claude Code skills, MIT-licensed, with one curl to install.

## The shape

The base is a 350-line Python regex linter — `writer/scripts/lint.py`. No LLM call. Pure regex, ~50ms on a 5,000-word file. It catches 23 categories of LLM-prose tells:

- Filler intros — "In today's fast-paced world...", "In a world where...", "As we all know..."
- AI bridges — "Furthermore", "Moreover", "Additionally", "In conclusion" as paragraph openers
- Stock metaphors — "tapestry of", "navigate the complexities of", "embark on a journey", "cornerstone of", "pivotal role"
- Intensifier ladders — "truly remarkable", "absolutely critical", "deeply important", "incredibly powerful"
- Balance hedges — "while there are valid points on both sides...", "on one hand... on the other hand...", "both perspectives have merit"
- GPT filler — "It's important to note", "It's worth noting", "Let's delve into", "Bear in mind"
- Comma-splice, em-dash overuse, double-negation, nominalization, pseudo-causal bridges, vague-person ("some experts say"), pseudo-science triggers...

Sample output, on a synthetic neuroslop fixture (the kind of text Claude produces if you ask "write a paragraph about AI"):

```
writer-lint: neuroslop suspected (54 hits)

By category:
  STOCK_METAPHOR         6
  AI_INTENSIFIER         5
  AI_QA                  5
  BUREAU_INV             5
  GPT_FILLER             4
  PSEUDO_SMART           4
  CORPORATE              4
  ...
```

54 hits across 18 categories in 300 words. That's typical first-draft LLM output.

## The wrappers

The linter alone is useful as a CI gate. But for actual editing, six wrappers compose on top:

- `viral-text` — generates social posts with EN viral hook patterns ("Most people don't know..." / "Here's what nobody tells you...") + numbered points + NLP question + CTA. Strips clichés.
- `prose-edit` — fiction rewrite. Pelevin / Manson voice vectors (not impersonation). Catches staccato, comma-stitching, double-negation.
- `essay-write` — non-fiction longreads. Source-backed claims, Manson-style ironic codas, V/H/P hypothesis markers.
- `pelevin-digression` — inserts opinionated voice digressions into fiction or essay (concrete sociology via brand-name, bracket-essay, forward-link, anti-gradation list).
- `tone-shifter` — rewrite a passage in a different register without changing meaning. 6 named registers: casual / friendly-professional / business-formal / academic / technical / plain-explainer.
- `cold-email` — first-touch, follow-up, intro-request, re-engage. 5-block structure (hook / value / ask / easy-yes / sign-off). ≤120-word budget. Banned ceremony patterns ("I hope this email finds you well...", "Just bumping this up...").

## The read-only linters

For pre-commit and pre-publish gating:

- `style-check` — stacks writer + prose-edit + essay-write rules. BLOCKING / WARNING / INFO severity. Exit-code semantics for git hook.
- `translation-sync` — multilingual book parity (RU/EN/PT-BR). Catches typography mismatches, terminology drift, "smoothed" numbers.
- `canon-check` — story-bible consistency for long-form fiction. Greps entities, cross-references the bible, flags drift.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

Or Docker:

```bash
docker pull ghcr.io/mikefluff/skills
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md
```

MIT-licensed. No external dependencies (the linter is pure Python regex; wrappers run inside Claude Code).

## What it doesn't do

It doesn't replace your voice. It strips the noise so your voice can land.

It doesn't catch every false positive. The regex set is high-recall by design.

It doesn't work as one mega-skill. Each skill is sharp and discriminating — Claude Code matches user requests against the `description:` field, and overlapping descriptions hurt discovery.

## Repo

github.com/Mikefluff/skills

If you write LLM-assisted prose and the output is starting to sound generic — try the offline linter on your last three drafts. Highest-leverage 30 seconds you'll spend this week.
```

---

## Hacker News submission

**Title**: `Show HN: Mikefluff/skills – 11 Claude Code skills to edit prose that doesn't sound like LLM`

**URL**: `https://github.com/Mikefluff/skills`

**Body** (first comment from submitter):

```
Hi HN — I've been writing with LLMs for the last couple of years and noticed everyone's output started to converge on the same handful of tells: "It's important to note that...", "delve into the rich tapestry of...", "in today's fast-paced world...", balance hedges, intensifier ladders, em-dash overuse.

This is 11 Claude Code skills built around an offline Python regex linter that catches 23 categories of those tells. EN + RU, 18+ regex categories firing on synthetic neuroslop, ~50ms on a 5k-word file.

The base linter is standalone and useful on its own (run via Docker or curl-pipe). Six wrappers compose on top — viral-text, prose-edit (fiction), essay-write (non-fiction), tone-shifter (register changes), cold-email (5-block / ≤120 words), pelevin-digression. Three read-only linters — style-check (pre-commit), translation-sync (RU↔EN↔PT-BR parity), canon-check (story-bible consistency).

MIT. No external deps. CI/CD pipeline with conventional commits → auto-release.

The interesting bit (to me): every skill has a sharp `description:` field that Claude Code matches against user requests. Overlapping descriptions hurt discovery, so the boundary between skills is intentional, not aesthetic.

Happy to answer questions on the linter design, the regex categories, or the skill-discovery contract.

Repo: github.com/Mikefluff/skills
```

---

## awesome-claude-code PR

The standard awesome-list entry format is one line. Copy-paste into the appropriate section of awesome-claude-code (likely "Prose" or "Skills"):

```markdown
- [Mikefluff/skills](https://github.com/Mikefluff/skills) — 11 prose-editing skills (writer, viral-text, prose-edit, essay-write, style-check, translation-sync, canon-check, pelevin-digression, skills-update, tone-shifter, cold-email). Offline writer linter catches 23 categories of LLM-prose tells (EN+RU). MIT.
```

If the README format expects a longer description, expand to:

```markdown
### Mikefluff/skills

**[github.com/Mikefluff/skills](https://github.com/Mikefluff/skills)** — 11 Claude Code skills for editing prose without LLM-tells. Built around an offline Python regex linter that catches 23 categories of AI-prose patterns (EN + RU). Wrappers for viral posts, fiction, non-fiction, cold email, register changes. Read-only linters for pre-commit, multilingual parity, story-bible consistency. MIT-licensed. Install via curl or Docker (ghcr.io/mikefluff/skills).
```

---

## Reddit (r/ClaudeAI, r/MachineLearning, r/programming)

```
**Title**: I built 11 Claude Code skills to make LLM-assisted writing stop sounding like LLM output

I've been writing with LLMs and got tired of every output reading the same way — "It's important to note that...", "delve into...", "in today's fast-paced world...", balance hedges everywhere.

So I built a collection of skills around an offline Python regex linter. The linter catches 23 categories of AI-prose tells in 50ms on a 5k-word file. No LLM call required for the linter — it's pure regex (writer/scripts/lint.py is 350 lines).

Six wrappers compose on top (viral, fiction, non-fiction, register-shifts, cold email, opinionated voice inserts). Three read-only linters (pre-commit gate, multilingual translation parity, story-bible consistency for fiction).

Install: `curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash`

Or Docker: `docker pull ghcr.io/mikefluff/skills`

MIT. Open to feedback / contributions.

Repo: github.com/Mikefluff/skills
Docs: github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md
```

---

## Common questions to anticipate

When the post lands, expect these:

**Q: How is this different from Grammarly / LanguageTool / Hemingway?**

Grammarly catches grammar. LanguageTool catches typos and basic style. Hemingway catches sentence length and adverbs. None of them catch the specific patterns LLMs produce — "navigate the complexities", "rich tapestry", balance hedges, AI-style triplets ("smart, capable, and intelligent"). This is purpose-built for the LLM-output problem, which is a different shape than human-error catching.

**Q: Why a regex linter? Won't an LLM judge better?**

For pre-commit / CI gating, regex wins: 50ms vs 5-10s, no API cost, deterministic, no LLM dependence. For nuanced rewriting, the wrappers DO use the LLM (via Claude Code) — that's where context matters. The linter is the floor; the wrappers are the ceiling.

**Q: Russian-first sounds limiting. What about English?**

EN coverage is 18 regex categories (out of 23 total — the others are RU-specific by structure, like calques). On synthetic EN neuroslop, the linter fires 54 hits across 18 categories. EN walkthroughs exist. EN bias is acceptable for what it does; it's still genuinely useful for EN writers.

**Q: How do I add my own rules?**

Two paths: (a) local override of references/*.md files (survives until --update), (b) PR to the repo. Both documented in CONTRIBUTING.md. For domain-specific banned terms, the local-override path is the right answer.

**Q: Can I run this without Claude Code?**

The linter, yes. `python3 writer/scripts/lint.py file.md` works standalone. The wrappers require Claude Code (they're LLM-driven by design).

**Q: Why so many skills instead of one big one?**

Discovery. Claude Code matches user requests against the `description:` field. A single mega-skill would match too broadly and hurt precision. Splitting lets each skill have a sharp discriminator. The boundary is intentional.
