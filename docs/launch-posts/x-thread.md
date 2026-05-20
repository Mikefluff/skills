# X / Twitter

## Single tweet (≤280 chars)

```
Open-sourced our Claude Code prose-editing skills collection.

17 skills layered on a regex linter that catches 28 categories of LLM-prose tells (EN + RU). Wrappers for landing copy, release notes, RFCs, cold email, viral posts, image/video prompts.

One-curl install. MIT.

github.com/Mikefluff/skills
```

(279 chars including URL)

---

## Thread (9 tweets)

```
1/ Spent the last few months building Claude Code skills for editing prose without the LLM-tells.

17 skills, one base linter, MIT. github.com/Mikefluff/skills

A thread on what's in it.
```

```
2/ The base is `writer` — an offline Python linter that catches 28 categories of regex-detectable AI prose:

- "It's important to note..."
- "delve into the rich tapestry of..."
- "in today's fast-paced world..."
- "we're excited to announce..."
- "revolutionary, game-changing..."
- intensifier ladders
- balance hedges
- comma-splices

EN + RU side-by-side. ~50ms on a 5K-word file.
```

```
3/ Linter v2 (just shipped) adds five marketing/product categories:

- MARKETING_HYPE (revolutionary, world-class, industry-leading, …)
- EMPTY_CTA (click here, learn more, get started alone)
- WEAK_OPENER (we're excited to announce, …)
- VAGUE_BENEFIT (save time, boost productivity)
- WRONG_TENSE_RELEASE (will support — for shipped work)

Plus severity tags (blocker/caution/nit) and code-fence-aware scanning.
```

```
4/ The prose wrappers (compose on `writer`):

- `viral-text` — hooks + numbered points + NLP question + CTA
- `prose-edit` — fiction rewrite (Pelevin / Manson voice vectors)
- `essay-write` — non-fiction longread (Manson coda, V/H/P markers)
- `tone-shifter` — register changes (casual ↔ business ↔ academic)
- `pelevin-digression` — voice digressions
```

```
5/ Product / tech wrappers (new this quarter):

- `landing-copy` — hero (Julian Shapiro 5-step), features, pricing, SEO meta, ad copy
- `release-notes` — Keep-a-Changelog format, per-audience tone
- `rfc-writer` — RFCs, ADRs, Tech Specs, Design Docs (RFC 2119 keywords)
- `microcopy` — error states, empty states, tooltips, buttons
- `cold-email` — 5-block / ≤120 words, banned ceremony patterns
```

```
6/ Visual prompt wrappers:

- `image-prompt` — MJ / DALL-E / Flux (6-part formula: subject + setting + style + lighting + camera + texture, per-model deltas)
- `video-prompt` — Kling / Veo / Sora / Runway (CHARACTER FIRST law, beat structure, pacing modes)
```

```
7/ Three read-only linters that produce reports, never mutate:

- `style-check` — pre-commit prose gate (BLOCKING / WARNING / INFO)
- `translation-sync` — RU↔EN↔PT-BR parity check (typography, terminology, anchor-quote drift)
- `canon-check` — story-bible consistency for fiction
```

```
8/ Installation is one curl. Works inside Claude Code (skill discovery via `description:` field). Docker image for CI:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md
```

```
9/ Code: github.com/Mikefluff/skills
Docs: github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md
Skill index: github.com/Mikefluff/skills/blob/main/docs/SKILL-INDEX.md

If your LLM-assisted output is starting to sound like Claude — run the offline linter on your last draft. Best signal-to-noise editing tool I've shipped this year.
```
