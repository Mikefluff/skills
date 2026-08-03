# Substack / personal blog (long form)

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

```markdown
# I'm tired of my writing sounding like Claude

I've been writing with LLMs for two years. The output saves time. The output also reads more and more like everyone else's LLM output. "It's important to note that..." "delve into..." "rich tapestry of..." "navigate the complexities..." "we're excited to announce..." "revolutionary, game-changing..." — every LinkedIn post, every product update, every newsletter.

So I built a tool that strips them. Then I kept extending it. It is now 41 Claude Code skills, MIT-licensed, one curl to install.

## The shape

The base is a Python regex linter — `skills/writer/scripts/lint.py`, about a thousand lines. No LLM call, no dependencies, roughly 80ms on a 4,000-word file. It carries 25 catalogued categories of LLM-prose tells:

- **Filler intros** — "In today's fast-paced world...", "In a world where...", "As we all know..."
- **AI bridges** — "Furthermore", "Moreover", "Additionally", "In conclusion" as paragraph openers
- **Stock metaphors** — "tapestry of", "navigate the complexities of", "embark on a journey", "cornerstone of", "pivotal role"
- **Intensifier ladders** — "truly remarkable", "absolutely critical", "deeply important", "incredibly powerful"
- **Balance hedges** — "while there are valid points on both sides", "on one hand... on the other hand", "both perspectives have merit"
- **GPT filler** — "It's important to note", "It's worth noting", "Let's delve into", "Bear in mind"
- **Marketing hype** — "revolutionary", "game-changing", "world-class", "industry-leading", "cutting-edge", "best-in-class" — the register landing-page LLMs default to
- **Empty CTAs** — "click here", "learn more", "get started" (alone)
- **Weak openers** — "We're excited to announce", "We're thrilled to share"
- **Vague benefits** — "save time", "boost productivity", "get more done"
- Plus the rest: comma-splice, double negation, nominalization, pseudo-causal bridges, vague attribution ("some experts say"), pseudo-science triggers, AI triplets, synthetic-authenticity templates, and a pseudo-therapeutic register ("and that's okay", "you're not alone")

Sample output, on a synthetic neuroslop fixture (the kind of text Claude produces if you ask "write a paragraph about AI"):

\`\`\`
writer-lint: neuroslop suspected (54 hits)
gate passed: no hard bans.

By category:
  STOCK_METAPHOR         6
  AI_INTENSIFIER         5
  AI_QA                  5
  BUREAU_INV             5
  GPT_FILLER             4
  PSEUDO_SMART           4
  CORPORATE              4
  ...

By severity:
  blocker  0
  caution  52
  nit      2
\`\`\`

54 hits across 18 categories in 443 words. That is ordinary first-draft LLM output, not a caricature.

## The wrappers

The linter alone works as a CI gate. For actual editing, 21 wrappers compose on top. A selection:

**Prose** (5):
- `viral-text` — generates social posts with EN viral hook patterns + numbered points + NLP question + CTA. Strips clichés.
- `prose-edit` — fiction rewrite. Pelevin / Manson voice vectors (not impersonation). Catches staccato, comma-stitching, double-negation.
- `essay-write` — non-fiction longreads. Source-backed claims, Manson-style ironic codas, V/H/P hypothesis markers.
- `pelevin-digression` — inserts opinionated voice digressions (concrete sociology via brand-name, bracket-essay, forward-link, anti-gradation list).
- `tone-shifter` — rewrite a passage in a different register without changing meaning. 6 named registers: casual / friendly-professional / business-formal / academic / technical / plain-explainer.

**Product / tech-docs** (4):
- `landing-copy` — hero (Julian Shapiro 5-step formula + 5 alternative formulas), features, pricing, FAQ, SEO meta (title + description + Open Graph + Twitter), ad copy with strict per-platform char limits (Google RSA / Facebook / LinkedIn / X / Reddit / TikTok).
- `release-notes` — Keep-a-Changelog format with per-audience tone (end-user / dev / ops). Anti-marketing-fluff bans.
- `rfc-writer` — RFCs, ADRs, Tech Specs, Design Docs. Structure: context / problem / proposal / alternatives / consequences / decision. RFC 2119 keywords. Forces at-least-2-alternatives + "do nothing" baseline.
- `microcopy` — error messages, empty states, tooltips, button labels, modals, 404/500 pages, onboarding. ≤8 words for buttons, never blames user.

**Outreach** (1):
- `cold-email` — first-touch, follow-up, intro-request, re-engage. 5-block structure (hook / value / ask / easy-yes / sign-off). ≤120-word budget. Banned ceremony patterns.

**Visual prompts** (2):
- `image-prompt` — Midjourney, Flux, Imagen, Nano Banana Pro, gpt-image-2, Ideogram, Seedream and more. Six-part formula (subject, setting, style, lighting, camera, texture), per-model deltas, negative prompts.
- `video-prompt` — Kling / Veo / Sora / Runway / Pika / Hailuo / Luma. CHARACTER FIRST law, beat structure (Beat 1/2/3), exact camera vocabulary, pacing modes.

## The other half: AI media

Somewhere along the way this stopped being only a prose project.

There are prompt skills for image, video and music — 14, 20 and 10 model families respectively — each encoding what that specific model responds to rather than a generic template. Then an optional `--execute` layer that stops producing paste-ready text and actually calls the vendor API, saving real PNGs, MP4s and MP3s. 32 providers sit behind one interface.

That layer spends your money, so it confirms first. A single call estimated over ten cents prompts before running; a batch asks once for the aggregate rather than once per item, and warns when the total exceeds a per-modality budget. The price table the estimate uses is the same one the published docs are generated from, so the number you read is the number you get charged.

On top of both halves sit 13 orchestrators. `research-brief` gathers a topic with citations. `carousel-builder` turns that into an eight-slide deck with one consistent visual style and ready-to-post captions. `reel-builder` turns it into a vertical video with matched music, stitched with ffmpeg. `proposal-maker` takes a raw price list and produces an HTML commercial proposal styled from the client's own website, prices and links kept exact.

## The read-only linters

For pre-commit and pre-publish gating:

- `style-check` — stacks writer + prose-edit + essay-write rules. BLOCKING / WARNING / INFO severity. Exit-code semantics for git hook.
- `translation-sync` — multilingual book parity (RU/EN/PT-BR). Catches typography mismatches, terminology drift, "smoothed" numbers.
- `canon-check` — story-bible consistency for long-form fiction. Greps entities, cross-references the bible, flags drift.

## Install

\`\`\`bash
# Curl
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

# Or npm
npm install -g @mikefluff/skills && skills install

# Or Homebrew
brew install mikefluff/tap/skills

# Or Docker (for CI)
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md
\`\`\`

MIT-licensed. No external dependencies (the linter is pure Python regex; wrappers run inside Claude Code).

## What it doesn't do

It doesn't replace your voice. It strips the noise so your voice can land.

It doesn't catch every false positive. The regex set is high-recall by design.

It doesn't work as one mega-skill. Claude Code matches requests against each skill's `description:` field, so overlapping descriptions make the wrong skill fire. The boundaries are a discovery contract, not taste.

## Repo

github.com/Mikefluff/skills

If your LLM-assisted drafts have started sounding generic, run the offline linter over the last three. It takes a second per file, and the output names the pattern and quotes the line, so you can disagree with it specifically.
```
