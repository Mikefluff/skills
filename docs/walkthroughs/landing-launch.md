---
title: "Write a launch landing page for a new product"
persona: "Founder shipping a marketing site for a v1 launch"
time: "30-45 minutes"
skills:
  - landing-copy
  - writer
  - microcopy
---

# A launch landing page — hero, features, pricing, FAQ, 404

Сценарий: ты launch'аешь v1 в пятницу. Сайт — single-page marketing, нужен полный stack секций: hero, three feature blocks, pricing table, FAQ, 404 page. Каждая секция со своими правилами и budget'ами. Не «AI-generated marketing slop», а нормальный copy, который читается и конвертирует.

Это работа для `landing-copy` (макро-секции) + `microcopy` (404, form labels, error states) + writer (общая чистка).

## Intent — три уровня skill stack

- **landing-copy** — hero, feature blocks, pricing rows, FAQ, CTAs. Длинные «sales» строки.
- **microcopy** — 404 page, form labels, button states, validation. Короткие «functional» строки.
- **writer** — финальный pass на всем. Antinyeyroslop, typography, intensifier ladder.

Каждый skill применяется к своей зоне. Не пытайся написать 404 page через landing-copy — wrong tool для wrong length.

## Intent — Julian Shapiro hero formula

Hero — это первая и единственная секция, которую читают 80% посетителей. Правило формы (см. `skills/landing-copy/references/hero-formula.md`):

```
[H1]   What it is + who it's for (one line, ≤ 12 words)
[Sub]  How it works + why it's different (one line, ≤ 20 words)
[CTA]  Specific action verb (≤ 4 words) + secondary low-friction option
[Soc.] Social proof OR specific outcome number (≤ 15 words)
```

Не «We empower X», не «Transform your Y», не «The future of Z». Specific. Concrete. One line each.

## Setup

Все три скилла установлены. Output формат: Markdown с section markers (parseable downstream by frontend build).

## Step 1. Invoke landing-copy with the product brief

```
/landing-copy launch-page "Ledger Guard"
```

Скилл задаёт seven вопросов (без всех — не пишет hero):

```
1. What does it do, in one sentence?
2. Who is it for? (one specific persona, not "businesses")
3. What's the strongest specific outcome? (one number or one named win)
4. What's the closest existing alternative + how is yours different?
5. Pricing model — flat / tiered / usage-based / enterprise-call?
6. What objection blocks the buy decision? (the one FAQ that matters)
7. Launch context — pre-revenue / paying customers / specific milestone?
```

## Step 2. Answers

1. **What** — Automated SOC 2 and KYC compliance workflows for SMB fintech.
2. **Who** — Pre-Series-A fintech founders (5-30 employees) who need SOC 2 in 8 weeks, not 8 months.
3. **Outcome** — Average customer reaches SOC 2 audit-ready in **47 days** (vs industry 6+ months).
4. **Alternatives** — Vanta and Drata (general-purpose). LG is fintech-specific, includes KYC workflows.
5. **Pricing** — three tiers: Startup ($299/mo), Growth ($899/mo), Scale (call).
6. **Top objection** — «We already have a compliance person» / «Why pay for software vs hire a consultant».
7. **Launch context** — 47 paying customers, $112K MRR, post-MVP, no funding yet.

## Step 3. The hero

```html
<section class="hero">
  <h1>SOC 2 and KYC for fintech startups — done in 47 days, not 6 months</h1>
  <p>Compliance workflows built for fintech, not retrofitted from generic
  SaaS. Plug into Stripe, Plaid, Persona, your bank.</p>

  <a class="cta-primary" href="/start">Start your 47-day audit</a>
  <a class="cta-secondary" href="/demo">See a 4-min demo</a>

  <p class="social-proof">47 fintech teams shipped SOC 2 reports through
  Ledger Guard in 2025. Average time-to-audit-ready: 47 days.</p>
</section>
```

Skill commentary inline:

- H1 — 12 words. Specific outcome (47 days), named compliance frames (SOC 2 + KYC), persona (fintech startups). No «empower», no «transform».
- Sub — 18 words. Differentiator (fintech-specific, not retrofitted) + concrete integrations. Specificity beats abstraction.
- CTA primary — «Start your 47-day audit» (specific verb + specific outcome, not «Get started»). Secondary — low-friction demo. Two CTAs cover both buyer types (action-takers + research-takers).
- Social proof — 21 words. Specific number (47), specific named outcome (SOC 2 reports), recency anchor (2025). Not «trusted by thousands».

## Step 4. The three feature blocks

Скилл собирает по pattern «Problem → Mechanism → Outcome» (см. `skills/landing-copy/references/feature-blocks.md`):

```html
<section class="features">
  <div class="feature">
    <h2>Pre-built fintech-specific controls</h2>
    <p><strong>Problem:</strong> Generic SOC 2 tools have ~80 controls.
    Fintech needs 140+: KYC, AML, transaction monitoring, sanctions.</p>
    <p><strong>How it works:</strong> 147 pre-mapped controls specific
    to fintech. Each one wired to evidence collection from Stripe,
    Plaid, Persona, AWS, Github.</p>
    <p><strong>Outcome:</strong> Most customers start at 31% control
    coverage on day 1, hit 95% by day 47.</p>
  </div>

  <div class="feature">
    <h2>Integrations that actually pull evidence</h2>
    <p><strong>Problem:</strong> Most compliance tools ask you to
    upload screenshots. That's not evidence — it's busywork.</p>
    <p><strong>How it works:</strong> Direct API integrations with
    Stripe, Plaid, Persona, AWS, Github, Okta, Linear. Evidence
    auto-collects nightly. Auditor reads the same source you do.</p>
    <p><strong>Outcome:</strong> Customers save an average of 86 hours
    per audit on evidence-gathering vs Vanta or Drata baseline.</p>
  </div>

  <div class="feature">
    <h2>Auditor handoff that doesn't break</h2>
    <p><strong>Problem:</strong> The audit-ready report often is not
    what your auditor actually wants. You scramble in week 6.</p>
    <p><strong>How it works:</strong> We work with five named audit
    firms (Prescient Assurance, A-LIGN, Schellman, Insight, Sensiba).
    Our reports match their intake schema, line-for-line.</p>
    <p><strong>Outcome:</strong> Zero customers needed a re-export
    pass in 2025. Auditor signs off on first submission.</p>
  </div>
</section>
```

Why this works (skill commentary):

- Each block has same structure (parallel structure helps scanability)
- Numbers are everywhere (147 controls, 31% → 95%, 86 hours, zero re-exports) — specificity > superlatives
- Named comparables (Vanta, Drata, audit firms) — credibility through names
- «How it works» is mechanism, not value-prop restating

## Step 5. Pricing — three tiers

```html
<section class="pricing">
  <h2>Pricing</h2>
  <p>Pay monthly. Cancel anytime. No setup fee, no audit fee.</p>

  <div class="tier">
    <h3>Startup — $299/mo</h3>
    <p>For pre-Series-A fintech with up to 10 employees.</p>
    <ul>
      <li>SOC 2 Type I, ready in 47 days</li>
      <li>5 integrations</li>
      <li>Async support (next business day)</li>
    </ul>
    <a class="cta" href="/start?plan=startup">Start at $299/mo</a>
  </div>

  <div class="tier featured">
    <h3>Growth — $899/mo</h3>
    <p>For Series-A fintech, 10-30 employees, SOC 2 Type II ready.</p>
    <ul>
      <li>Everything in Startup</li>
      <li>SOC 2 Type II (continuous monitoring)</li>
      <li>KYC + AML workflows</li>
      <li>Unlimited integrations</li>
      <li>Dedicated Slack channel, 4-hour response</li>
    </ul>
    <a class="cta" href="/start?plan=growth">Start at $899/mo</a>
  </div>

  <div class="tier">
    <h3>Scale — call us</h3>
    <p>For 30+ employee fintechs handling ISO 27001, PCI-DSS, or
    multi-region audits.</p>
    <a class="cta-secondary" href="/contact">Book 30 minutes</a>
  </div>
</section>
```

Skill rules applied:

- Tier names are not «Basic / Pro / Enterprise» — they're persona-anchored
- Each tier lists who it's for, not just features
- Price displayed (not «contact us» on first two — that signals zero-friction)
- Featured tier (Growth) visually highlighted (the math: 60% of customers should land here)
- «Scale — call us» is honest (custom contracts) but provides a specific small ask («Book 30 minutes», not «Contact sales»)

## Step 6. FAQ — answer the top objection first

Скилл сортирует FAQ by «blocking value» — the question that loses the sale first comes first:

```html
<section class="faq">
  <h2>Common questions</h2>

  <details open>
    <summary>We already have a compliance hire. Why pay for software?</summary>
    <p>Because your compliance hire's time is worth more than $899/mo.
    The software handles evidence collection, control mapping, and
    auditor handoff. Your hire handles judgement calls: scoping,
    interpreting findings, talking to the auditor. The split is the
    point.</p>
  </details>

  <details>
    <summary>How is this different from Vanta / Drata?</summary>
    <p>Vanta and Drata are general-purpose — built for SaaS first,
    bolted-on fintech later. We're fintech-only: 147 fintech-specific
    controls, KYC + AML workflows, direct integrations with Plaid /
    Persona / banking APIs. If you're not fintech, Vanta is probably
    a better fit.</p>
  </details>

  <details>
    <summary>What if our audit firm isn't on your list?</summary>
    <p>We support five auditors out of the box. For others, we generate
    standard SOC 2 reports (AICPA TSC). Migration usually takes one
    onboarding call. Worst case: your auditor reviews the same
    evidence, just from a slightly different export format.</p>
  </details>

  <details>
    <summary>Do I get a refund if we miss the 47-day target?</summary>
    <p>If your audit-ready date slips because of us (not you), one
    month free. If you skip controls or miss our timeline requests,
    that's on you — but we won't bill you for that month either,
    because you won't have used the product.</p>
  </details>
</section>
```

Why these four:

- #1 is the top objection (answered)
- #2 is the comparison ask (named alternatives, honest «not for you» case)
- #3 is the «what if I don't fit your happy path» question (defensive moat)
- #4 is the risk-reversal (refund policy in clear language)

## Step 7. The 404 — handed off to microcopy

`landing-copy` doesn't write 404. Это microcopy job (length budget, tone). Switch skill:

```
/microcopy 404-page "Ledger Guard"
```

Output:

```html
<section class="page-404">
  <h1>404 — that page doesn't exist</h1>
  <p>Maybe the link is stale, maybe you typed something different.
  Either way — you're not stuck.</p>

  <a class="cta-primary" href="/">Back to the homepage</a>
  <a class="cta-secondary" href="/docs">Read the docs</a>
  <a class="cta-tertiary" href="/contact">Tell us what you were looking for</a>
</section>
```

microcopy rules applied:

- No «Oops!» / «Whoops!» / «Sorry!»
- 12-word body (within microcopy budget)
- Three CTAs covering three user types (back / read / report)
- Last CTA («Tell us...») is the dev-feedback channel — useful for actual broken links
- Tone matches landing-copy (specific, low-blame, agency-respecting)

## Step 8. Writer-pass на всё

После того как все секции собраны, скилл прогоняет ОБЪЕДИНЁННЫЙ output через writer:

- Strip 23 antinyeyroslop categories (любой residue от «delve into», «navigate», «in conclusion»)
- Typography (smart quotes, em-dashes — особенно важно для landing copy на marketing site)
- Intensifier ladder (любые «truly significant» → «significant»)
- Sentence rhythm check (если 5 секций подряд имеют avg sentence 22 words — добавь короткое)

Это финальный sweep. Не пропускать.

## Concrete before / after — the hero, two versions

Before (LLM default «marketing voice»):

```
H1:   Empowering Fintech Innovators with World-Class Compliance
Sub:  Our cutting-edge platform leverages AI to streamline your SOC 2
      journey, helping you focus on what matters most: building.
CTA:  Get Started
SP:   Trusted by hundreds of fintech leaders worldwide.
```

Why bad:

- «Empowering» / «cutting-edge» / «leverages AI» / «what matters most» — five clichés in two lines
- No specific outcome
- «Get Started» is verb without object
- «Hundreds of leaders worldwide» = unverifiable, smells fake

After (landing-copy + writer):

```
H1:   SOC 2 and KYC for fintech startups — done in 47 days, not 6 months
Sub:  Compliance workflows built for fintech, not retrofitted from
      generic SaaS. Plug into Stripe, Plaid, Persona, your bank.
CTA:  Start your 47-day audit
SP:   47 fintech teams shipped SOC 2 reports through Ledger Guard in
      2025. Average time-to-audit-ready: 47 days.
```

Why better:

- Specific outcome (47 days) twice
- Named persona (fintech startups)
- Named integrations (Stripe, Plaid, Persona)
- CTA verb has object («Start your 47-day audit», not «Get started»)
- Social proof is verifiable specific number

## Когда НЕ использовать landing-copy

- **Long-form sales page (4000+ words)** — другой жанр. Используй `essay-write` с marketing tone-shift'ом, или специализированный sales-page approach.
- **Email campaign** — это `cold-email` (cold) или standalone email-copy подзадача. Landing rules не fit для inbox context.
- **Blog post / content marketing** — используй `viral-text` (если соц-формат) или `essay-write` (если longform).
- **Pure product UI strings** — microcopy. Landing-copy жёстче на длину и persuasion patterns, чем functional UI.

## Troubleshooting

### Hero H1 не помещается в 12 слов

Это сигнал, что value proposition не chiseled. Не «expand budget» — split: что главное slot, что в sub. «SOC 2 and KYC for fintech startups, with Plaid/Stripe integrations, in 47 days vs 6 months» = 18 слов = too much. Pick the strongest anchor (47 days), оставь integrations для feature block.

### Pricing tier names получились generic (Basic / Pro / Enterprise)

Скилл по дефолту против. «Startup / Growth / Scale» или «Solo / Team / Agency» — persona-anchored. Если все равно generic — sales context либо корпоративный, либо ленивый.

### FAQ выдал 12 вопросов

Cut. Скилл по дефолту просит ≤ 6. 12 FAQ — это либо marketing dump, либо product not ready (too many objections). Решай, какие 4-6 действительно блокируют sale.

### 404 page получился funny (joke-tone) — не подходит под бренд

Microcopy default mood — «neutral helpful». Если бренд — sober (finance, healthcare), `--tone serious` снимает шутки. Если бренд — playful (consumer app), `--tone playful` добавит slight humour. Никогда не добавляет «Oops!» — это banned regardless.

### Social proof number не реален / нет 47 customers

Не врать. Альтернативы: cite named customer (с разрешением), cite specific outcome без числа («Ledger Guard helped {Customer} pass SOC 2 in 38 days»), или drop social proof entirely. Fake social proof = trust collapse on first contact.

## Related

- [microcopy-error-states.md](microcopy-error-states.md) — родственная задача для product UI strings
- [cold-email-pitch.md](cold-email-pitch.md) — где landing-copy ссылается (link from email body to hero)
- [release-notes-saas.md](release-notes-saas.md) — что shipped (changelog), а не что promised (landing)
- [image-prompt-cover.md](image-prompt-cover.md) — для hero illustration к этой landing
- [skills/landing-copy/references/hero-formula.md](../../skills/landing-copy/references/hero-formula.md) — полная Hero formula
