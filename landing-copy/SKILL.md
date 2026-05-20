---
name: landing-copy
description: "Write marketing copy — landing page sections (hero/features/pricing/FAQ), SEO meta (title+description+OG+Twitter), ad copy (Google/Facebook/LinkedIn/X). Julian Shapiro hero formula, char limits per platform. Wraps `writer`. Use when user says 'landing page copy', 'SEO meta', 'Google Ad', 'hero section'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Write marketing strings for landing pages, SEO meta tags, social cards, and paid ads. Output: structured copy ready to drop into design / CMS / ad platform.

Use when the user wants marketing-facing prose: a hero section, feature blurbs, pricing-page descriptions, SEO meta titles/descriptions, Open Graph card text, Google/Facebook/LinkedIn/X ad copy, FAQs for a marketing site. Not for product UI strings — that's `microcopy`. Not for release notes — that's `release-notes`. Not for viral social posts — that's `viral-text`.

This skill does NOT:
- write product-UI microcopy (use `microcopy`)
- write release notes / changelogs (use `release-notes`)
- write viral social media posts (use `viral-text`)
- write longform marketing essays / blog posts (use `essay-write`)
- design page layouts (use a design tool)
</objective>

## ROLE

Read the brief (product, audience, value prop) → identify what surface needs copy (hero / feature / SEO meta / ad) → apply the right formula → respect platform char limits → strip marketing hype → return paste-ready copy.

## PIPELINE

1. **Get the inputs.** Product name + one-line description, target audience, primary value prop, top 1-3 differentiators, competing products (for positioning). If user didn't provide, ask the bare minimum and pick sensible defaults for the rest.

2. **Identify the surface.** See `references/surfaces.md`:
   - **Landing page sections**: hero / features / social proof / pricing / FAQ / footer / CTA
   - **SEO meta**: page title (≤60 chars) / meta description (≤160 chars)
   - **Open Graph**: og:title (≤60 chars) / og:description (≤200 chars)
   - **Twitter card**: title (≤70 chars) / description (≤200 chars)
   - **Google Ad**: headline (≤30 chars) × 3-15, description (≤90 chars) × 2-4
   - **Facebook Ad**: primary text (≤125 chars) / headline (≤27 chars) / description (≤27 chars)
   - **LinkedIn Sponsored Content**: intro (≤150 chars) / headline (≤70 chars) / description (≤100 chars)
   - **X (Twitter) Ad**: tweet copy (≤280 chars)

3. **Apply the formula for the surface.** See `references/hero-formula.md` for hero; `references/feature-blocks.md` for features; `references/seo-meta.md` for SEO/OG/Twitter; `references/ad-copy.md` for paid ads.

4. **Respect char limits.** Each platform truncates differently — see `references/char-limits.md`.

5. **Apply universal rules.** Plain language, specific value, no marketing hype, action-oriented CTAs. See `references/banned-patterns.md` for what to strip.

6. **Run `writer` final pass.** Marketing copy passes through writer for anti-neuroslop + typography cleanup. Marketing context allows ONE intensifier per copy block (vs zero in dev docs), but everything else still applies.

7. **Output.** One or multiple strings depending on surface. For ads — usually multiple variants (3-5) for A/B testing.

## MODES

- `landing-copy hero <product-brief>` — hero section (headline + subheadline + CTA)
- `landing-copy features <list-of-features>` — feature-block copy (3-7 features)
- `landing-copy faq <topic>` — FAQ entries (5-10)
- `landing-copy pricing <plans>` — pricing-page copy (plan name + description + CTA per plan)
- `landing-copy seo-meta <page>` — title + description for one page
- `landing-copy og-card <page>` — Open Graph + Twitter card for one page
- `landing-copy google-ad <product> --variants 3` — Google Ads responsive search ad with multiple headlines + descriptions
- `landing-copy facebook-ad <product> --variants 5` — Facebook Ads with primary text + headline + description
- `landing-copy linkedin-ad <product>` — LinkedIn sponsored content
- `landing-copy twitter-ad <product>` — X promoted post
- `landing-copy --improve <existing-copy>` — rewrite weak existing copy

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/surfaces.md](references/surfaces.md) | When identifying which surface you're writing for — full taxonomy with examples |
| [references/hero-formula.md](references/hero-formula.md) | When writing a hero section — Julian Shapiro 5-step + alternative formulas + when to use each |
| [references/feature-blocks.md](references/feature-blocks.md) | When writing feature-block copy — patterns for 3-feature / 6-feature / detailed-feature pages |
| [references/seo-meta.md](references/seo-meta.md) | When writing SEO meta titles + descriptions + Open Graph + Twitter cards |
| [references/ad-copy.md](references/ad-copy.md) | When writing paid ads — per-platform templates + variations + targeting hints |
| [references/char-limits.md](references/char-limits.md) | Quick-reference table for every char limit across every platform / surface |
| [references/banned-patterns.md](references/banned-patterns.md) | After draft — strip marketing fluff, vague claims, generic CTAs |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 8 calibration pairs covering hero / feature / SEO / Google Ad / Facebook Ad / LinkedIn / Twitter ad / FAQ.

## CONSTRAINTS

- **Specific value, not vague claims.** "Ship faster" → "Cut PR review time from 2 days to 4 hours". Numbers > adjectives.
- **No "world-class", "best-in-class", "revolutionary".** Strip on sight.
- **Lead with the user outcome, not the feature.** "AI-powered code review" → "Catch bugs before your reviewer does".
- **One concept per surface element.** Hero has ONE primary message. Feature block has ONE benefit. Ad has ONE click target.
- **CTA verbs are specific.** "Start free trial" / "Book demo" / "See pricing" — NOT "Get started" / "Learn more" (unless those genuinely match the next action).
- **Char limits are HARD ceilings.** Going over = truncation in production. Stay under.
- **No "Click here".** Replace with the verb of the destination ("Download report", not "Click here").
- **Match audience register.** B2B enterprise → formal-professional; consumer SaaS → friendly-direct; developer tool → terse-technical. See `references/surfaces.md`.
- **Localizable copy.** Avoid idioms, puns, culture-specific references for global products.
- **A/B variants for ads.** Always offer 3-5 variants for paid copy — testing is the design tool.

## INVOCATION HINTS

When the user says any of:
- "hero section / landing-page copy / headline + subheadline"
- "feature block / feature description"
- "pricing page copy"
- "FAQ for landing"
- "SEO title + description / meta description"
- "Open Graph / Twitter card text"
- "Google Ad / Facebook Ad / LinkedIn Ad / Twitter Ad copy"
- "improve this landing-page copy"

RU triggers (use the skill when the user writes any of):
- «текст для лендинга / лендинг на русском / копирайт для лендинга»
- «hero-секция / первый экран / заголовок и подзаголовок»
- «feature-блоки / описание фич»
- «текст страницы тарифов / pricing-страницы»
- «FAQ для лендинга»
- «SEO meta на русском / тайтл и дескрипшн»
- «Open Graph для статьи / OG-карточка»
- «Google Ads на русском / Яндекс.Директ»
- «реклама ВКонтакте / Telegram Ads / Facebook Ads на русском»
- «перепиши текст лендинга»

For RU hero patterns (тонкая контроверсия, обращение «вы», числа в RU-формате), see [`references/hero-formula.md`](references/hero-formula.md) section `RU hero patterns`.

Use this skill. For viral organic social posts → `viral-text`. For product-UI strings → `microcopy`. For release announcements → `release-notes`.
