# Walkthroughs

19 step-by-step recipes covering every skill, categorized by what you're trying to accomplish.

Each walkthrough is self-contained: input → expected commands → expected output. No skipping prerequisites — they assume only that `install.sh` has been run.

---

## Prose editing

The base layer. No API keys required.

| Walkthrough | Skills | What you'll do |
|---|---|---|
| [Edit a fiction chapter](fiction-chapter.md) | `prose-edit` → `writer` | Take a draft chapter, apply Pelevin/Manson voice vector, fix RU calques + structural synthesis, get a cleaner version back |
| [Draft a long-form essay](non-fiction.md) | `essay-write` → `writer` (+ optional `pelevin-digression`) | Open with a hook, build claims with sources, end with a question — Manson-style cadence in plain Russian |
| [Insert a Pelevin-style digression](digression-insertion.md) | `pelevin-digression` → `prose-edit` or `essay-write` | Hand-pick a passage, ask for a digression in the project's existing voice (12 structural techniques + 5 banned patterns) |
| [Rewrite in a different register](tone-shift.md) | `tone-shifter` → `writer` | Take a draft, shift formal↔casual / business↔academic / technical↔friendly / plain-explainer — 6 registers |
| [Verify a trilingual translation (RU/EN/PT-BR)](translation-parity.md) | `translation-sync` (linter) | Read-only parity check: typography, terminology canon, anchor-quote drift, names/patronymics/diminutives, cultural realia |
| [Audit a chapter against the story bible](canon-check-audit.md) | `canon-check` (linter) | Grep entities, cross-reference the project's story-bible, flag BLOCKING contradictions / WARNING gaps / INFO new details |
| [Run a read-only quality gate](style-check-gate.md) | `style-check` (linter) | Stack writer + prose-edit + essay-write rules with severity classes, route by path patterns |
| [Auto-lint every git commit](pre-commit-hook.md) | `style-check` (linter) | Wire `style-check` into `.git/hooks/pre-commit` — full Claude variant + offline-only fallback |

---

## Marketing & ops prose

Wrappers for specific tone budgets.

| Walkthrough | Skills | What you'll do |
|---|---|---|
| [Viral social post (RU)](viral-post.md) | `viral-text` → `writer` | 41-rule viral content recipe: hook + numbered points + micro-conclusion with NLP question + CTA |
| [Viral social post (EN)](en-viral-post.md) | `viral-text` → `writer` | Same recipe in English |
| [Cold outreach email](cold-email-pitch.md) | `cold-email` → `writer` | 5-block structure under 120 words, anti-ceremony patterns, anti-template subject |
| [Write UX microcopy (errors / empty states)](microcopy-error-states.md) | `microcopy` → `writer` | Error messages, empty states, tooltips, button labels — plain language, never blame user |
| [Write release notes for a SaaS](release-notes-saas.md) | `release-notes` → `writer` | Keep-a-Changelog format, per-audience tone, anti-marketing-fluff bans |
| [Write an RFC / ADR / design doc](rfc-architecture.md) | `rfc-writer` → `writer` | Context/problem/proposal/alternatives/consequences structure, RFC 2119 keywords |
| [Write landing + SEO + ad copy](landing-launch.md) | `landing-copy` → `writer` | Julian Shapiro hero formula, char limits per platform, multi-surface (hero / features / pricing / FAQ / SEO meta / ad copy) |

---

## AI media generation (prompts + optional execution)

These skills write paste-ready prompts. With API keys + `--execute`, they also generate real assets.

| Walkthrough | Skills | What you'll do |
|---|---|---|
| [Generate an image prompt + cover](image-prompt-cover.md) | `image-prompt` (+ `--execute`) | Write a per-model prompt for Midjourney / Flux 2 / Imagen 4 / Nano Banana Pro / gpt-image-2 / Ideogram / Seedream — character lock, multi-ref, text-in-image |
| [Generate a video prompt + reel](video-prompt-reel.md) | `video-prompt` (+ `--execute`) | Write a per-model prompt for Veo 3.1 / Sora 2 / Kling 3.0 / Runway Gen-4 — T2V / I2V / V2V / multi-shot / dialogue+audio |
| [Execute end-to-end (image + video + music API)](execute-end-to-end.md) | `image-prompt` / `video-prompt` / `music-prompt` + `--execute` | Full execution layer demo: prompt → API → real PNG/MP4/MP3 on disk + optional S3 mirror |

For AI music prompts specifically, see [`USER-GUIDE` § music](../USER-GUIDE.md#i-want-to-write-an-ai-music-prompt). There's no dedicated walkthrough yet — but the music-prompt SKILL.md + the 12-genre style library cover the workflow comprehensively.

---

## Orchestrators (end-to-end)

These chain multiple skills + the execute layer + style libraries into a single command.

| Walkthrough | Skills | What you'll do |
|---|---|---|
| [Research → carousel → reel (end-to-end)](research-to-carousel-reel.md) | `research-brief` + `carousel-builder` + `reel-builder` | One topic → cited research brief → 8-slide LinkedIn carousel → 15-second vertical reel. ~6-10 min wall time, $2-7 total cost depending on provider mix. The most ambitious recipe in the collection. |

---

## Quick navigation

By skill (jump straight to the SKILL.md):

**Base + linters**: [`writer`](../../writer/) · [`style-check`](../../style-check/) · [`translation-sync`](../../translation-sync/) · [`canon-check`](../../canon-check/)

**Prose wrappers**: [`viral-text`](../../viral-text/) · [`prose-edit`](../../prose-edit/) · [`essay-write`](../../essay-write/) · [`tone-shifter`](../../tone-shifter/) · [`cold-email`](../../cold-email/) · [`microcopy`](../../microcopy/) · [`release-notes`](../../release-notes/) · [`rfc-writer`](../../rfc-writer/) · [`landing-copy`](../../landing-copy/) · [`pelevin-digression`](../../pelevin-digression/)

**Media-gen wrappers**: [`image-prompt`](../../image-prompt/) · [`video-prompt`](../../video-prompt/) · [`music-prompt`](../../music-prompt/)

**Orchestrators**: [`research-brief`](../../research-brief/) · [`carousel-builder`](../../carousel-builder/) · [`reel-builder`](../../reel-builder/)

**Meta**: [`skills-update`](../../skills-update/) · [`skills-keys`](../../skills-keys/)

---

## What's missing

If you don't see a walkthrough for a scenario you care about — open an issue or PR. The fastest way to add one: copy a similar file (matching the persona/skill set), rename, edit. Frontmatter requirement:

```yaml
---
title: "<one-line scenario>"
persona: "<who would do this>"
time: "<estimated wall time>"
skills:
  - <skill-1>
  - <skill-2>
---
```

The `skills:` list is what the docs-consistency check parses to confirm coverage. Without it, CI fails.
