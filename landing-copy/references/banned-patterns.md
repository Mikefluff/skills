# Banned patterns

Strip these from any landing-page / SEO / ad copy. Each marks the text as low-quality marketing.

> **See also (shared across cold-email / landing-copy / release-notes):**
> [`common/references/banned-patterns-hype.md`](../../common/references/banned-patterns-hype.md) ·
> [`common/references/banned-patterns-preambles.md`](../../common/references/banned-patterns-preambles.md) ·
> [`common/references/banned-patterns-empty-cta.md`](../../common/references/banned-patterns-empty-cta.md)
>
> The base linter (`writer/scripts/lint.py`) catches the regex-detectable subset under `MARKETING_HYPE` / `WEAK_OPENER` / `EMPTY_CTA` / `VAGUE_BENEFIT`.

---

## 1. Marketing hype adjectives

Pure hype superlatives (`revolutionary`, `game-changing`, `world-class`, `industry-leading`,
`cutting-edge`, `best-in-class`, `groundbreaking`, `next-generation`, `state-of-the-art`,
`unparalleled`, `unmatched`, `innovative`) live in
[`common/references/banned-patterns-hype.md`](../../common/references/banned-patterns-hype.md).
The base linter catches them under `MARKETING_HYPE`.

Landing-page-specific adjectives — also banned without specifics:

| ❌ Banned | ✅ Replacement |
|---|---|
| `Award-winning` (without specific award) | (delete or cite the specific award) |
| `Powerful` | (delete or describe the power specifically) |
| `Robust` | (delete or describe robustness — "99.95% uptime, no maintenance windows") |
| `Enterprise-grade` | (delete or describe the enterprise capability — "SOC 2 Type II + audit logs") |
| `Lightning-fast` | "X% faster" with a number |
| `Seamless` | (delete) |
| `Intuitive` | (delete; if true, show with a screenshot/demo) |
| `User-friendly` | (delete) |

Rule: any adjective whose sole purpose is to praise without specifics gets deleted.

---

## 2. Vague claims

| ❌ Banned | ✅ Replacement |
|---|---|
| `Get more done` | "Ship 3x more features per quarter" (with specific verb + number) |
| `Save time` | "Save 5 hours per week" |
| `Boost productivity` | "Cut PR review time from 2 days to 4 hours" |
| `Streamline workflows` | (describe the specific workflow change) |
| `Improve efficiency` | "Reduce {process} time by N%" |
| `Take your X to the next level` | (delete entirely; meaningless) |
| `Unlock your potential` | (delete; coaching-jargon) |
| `Transform your business` | (delete OR describe the specific transformation) |
| `Achieve your goals` | (delete; meaningless) |
| `Empower your team` | "Give your team X" (specific capability) |

Rule: claims without a number or specific outcome get rewritten with one.

---

## 3. CTAs that don't work

Generic CTAs (`Click here`, `Tap here`, `Learn more`, `Read more`, `Find out more`,
`Get started` without object, `Submit`) live in
[`common/references/banned-patterns-empty-cta.md`](../../common/references/banned-patterns-empty-cta.md).
The base linter catches them under `EMPTY_CTA`.

Landing/ad-specific CTA bans — also strip:

| ❌ Banned CTA | ✅ Replacement |
|---|---|
| `Sign up today!` | "Sign up" (drop "today!" — adds nothing) |
| `Try it now` | "Try free" or "Start free trial" — specify the offer |
| `Contact us` | "Book demo" / "Email sales" — specify the channel |
| `Buy now` | "Buy Pro" / "Buy for $29/month" — specify the offer |

Rule: CTAs are verbs. Generic verbs ("get", "click", "submit") get replaced with destination-specific verbs.

---

## 4. Empty preambles

| ❌ Empty | ✅ Replace with |
|---|---|
| `Welcome to {brand}` | (delete; just start with the value prop) |
| `Hello, world` / `Hi there` | (delete) |
| `Looking for X?` | (rephrase as the offer: "X for {audience}") |
| `Are you tired of...?` | (rephrase as the offer) |
| `Did you know that...?` | (rephrase as the claim) |
| `Have you ever wondered...?` | (rephrase as the claim) |
| `In a world where...` | (rephrase as the offer) |
| `Imagine if...` | (rephrase as the claim) |

Rule: never write a sentence whose only purpose is introducing the next sentence.

---

## 5. We-language overuse (when audience is on the other side)

When the page is selling TO the audience, leading with "we" puts you in the wrong position.

| ❌ We-led | ✅ You-led / outcome-led |
|---|---|
| `We help teams ship faster.` | `Ship faster.` |
| `We make customer support easy.` | `Customer support that doesn't burn out your team.` |
| `We provide AI-powered code review.` | `AI code review that catches what humans miss.` |
| `We're a company that...` | (delete; the audience doesn't care about your story up front) |
| `Our platform offers...` | (start with the offer, not "our platform") |
| `At {brand}, we believe...` | (skip the philosophy; lead with the offer) |

Exception: testimonials, founder-direct sections, and the About page can use "we" liberally — those surfaces are about the brand. But the hero / features / pricing / ads are about the visitor's outcome.

---

## 6. Future tense for shipped product

| ❌ Future | ✅ Present |
|---|---|
| `Will help you ship faster` | `Helps you ship faster` (or "Ship faster") |
| `Will reduce your costs by 30%` | `Reduces your costs by 30%` |
| `Will catch bugs before they reach production` | `Catches bugs before production` |
| `Will be available in Q3` | (delete — only put SHIPPED features in landing copy) |
| `Coming soon: X` | (mostly delete — only useful if X is a pre-order / waitlist) |

Rule: marketing copy promotes what EXISTS today. Future-state language belongs in roadmap / blog, not landing.

---

## 7. Apologies / hedging

| ❌ Hedge | ✅ Direct |
|---|---|
| `We try to...` | `We {do thing}` (or just "{Brand} {does thing}") |
| `Often helps users...` | `Helps {audience} {outcome}` |
| `Can sometimes save you...` | `Saves you {specific amount}` |
| `Might be the right fit for...` | `For {specific audience}` |
| `Designed to help with...` | `Helps with {specific thing}` (drop "designed to") |
| `Aims to...` | (delete; commit to the claim) |

Marketing copy isn't a place for hedging. Either commit to the claim, or don't make it.

---

## 8. Generic numbers / metrics

| ❌ Useless metric | ✅ Useful metric |
|---|---|
| `Thousands of happy customers` | "12,400+ teams" (specific) or skip |
| `Many users love it` | (skip; or specific testimonial) |
| `Trusted by leading companies` | "Used by Stripe, Linear, Vercel" (with logos) |
| `99% uptime` (without context) | "99.95% uptime over the last 12 months" |
| `Saves time` | "Saves 5 hours per week" |
| `Faster than competitors` | "5x faster than {specific competitor}" — if you can prove |
| `Used by lots of people` | Pick: number, named customers, or skip |

Rule: any number on a landing page must be (a) specific, (b) verifiable, (c) recent.

---

## 9. Buzzword stacking

When you find 3+ marketing words in a row, delete most of them:

| ❌ Stacked | ✅ Pick one or none |
|---|---|
| `Innovative, intuitive, powerful platform` | "Code-review platform" + a specific differentiator |
| `World-class, enterprise-grade, scalable solution` | "Code-review tool used by enterprises" |
| `Beautiful, fast, easy-to-use design tool` | "Design tool" + the specific differentiator |
| `Smart, capable, intelligent AI assistant` | "AI code reviewer" |

Rule: empty adjective stacks signal "we couldn't think of anything specific". Replace with one specific claim.

---

## 10. AI / "Smart" / "Intelligent" overuse (2025+ specific)

These have become so overused they signal low-effort copy.

| ❌ Overused | ✅ Pick more precise |
|---|---|
| `AI-powered X` | "X that learns from {specific signal}" or "Built on GPT-4" (specific) |
| `Smart X` | (delete; describe what's smart specifically) |
| `Intelligent X` | (delete) |
| `Powered by AI` | (delete; either describe the AI's specific behavior or drop the claim) |
| `Machine learning algorithms` | (drop; describe what the algorithms do) |
| `Generative AI` | (drop unless the user knows + cares specifically) |

Rule: "AI" as a marketing word is now noise. Either describe the specific AI behavior, or skip.

---

## 11. Fake urgency

| ❌ Fake urgency | ✅ Real or skip |
|---|---|
| `Limited time offer!` (without actual deadline) | Drop or set a real deadline |
| `Act now!` | (delete) |
| `Don't miss out!` | (delete) |
| `Only X spots left!` (when not true) | Drop unless verifiable |
| `Sale ends soon!` (without date) | Specify the date |
| `🔥 HOT! 🔥` | (delete) |

Rule: fake urgency erodes trust permanently. Save urgency for real deadlines (Black Friday, beta-close, etc.).

---

## 12. Industry jargon when audience is mixed

| Audience | OK jargon | NOT OK |
|---|---|---|
| Developer tool | API, SDK, endpoint, JSON, REST, GraphQL | "Mission-critical workflows" |
| Consumer SaaS | Workspace, project, plan | API, SDK, microservices |
| Fintech | Reconciliation, settlement, KYC | Latency, throughput |
| Healthcare | HIPAA, EHR, claim | DevOps, agile |
| Marketing tool | CTR, CAC, LTV, attribution | Tensor, embedding |

Rule: use the AUDIENCE'S jargon, not your engineering team's.

---

## Quick strip-test

Before submitting any landing copy, run this scan:

1. `revolutionary` / `game-changing` / `industry-leading` / `world-class` → strip
2. `powerful` / `robust` / `enterprise-grade` (without specifics) → strip or specify
3. `seamless` / `intuitive` / `user-friendly` → strip or show specifics
4. `Get more done` / `Save time` / `Boost productivity` (without numbers) → add a number
5. `Click here` / `Learn more` / `Get started` → replace with destination verb
6. `Welcome to {brand}` / `Looking for X?` → cut, lead with offer
7. `We help/make/offer` (in hero) → rewrite as audience-outcome
8. `Will help you...` → "Helps you..." (present tense)
9. `Trusted by leading companies` → name the companies or cite a number
10. `AI-powered` / `Smart` / `Intelligent` → specify the AI behavior or drop

After the strip-pass, landing copy is typically 20-30% shorter and noticeably crisper.

---

## What to ADD (positive direction)

After stripping, the copy may need:

- **A specific number** for any "improved" / "saves" claim
- **A specific named customer** for any "trusted by" claim
- **A specific verb** for any generic CTA
- **A specific audience name** for any vague "users" / "teams"
- **A specific differentiator** for any category claim ("the CRM" → "the CRM for solo founders")

Add these. Don't add filler.

---

## Cross-references

- Surfaces and where these rules apply: [`surfaces.md`](surfaces.md)
- Hero writing (uses these bans): [`hero-formula.md`](hero-formula.md)
- Feature blocks (uses these bans): [`feature-blocks.md`](feature-blocks.md)
- SEO meta (uses these bans): [`seo-meta.md`](seo-meta.md)
- Ad copy (uses these bans): [`ad-copy.md`](ad-copy.md)
