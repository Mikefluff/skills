# Surfaces

A taxonomy of marketing-copy surfaces. Each has its own length budget, voice register, and structural conventions.

---

## Landing page sections

A typical landing page has 5-9 sections, top-to-bottom:

| Section | Purpose | Length |
|---|---|---|
| **Hero** | One screen of value; primary CTA | Headline ≤12 words, subheadline ≤25 words, CTA ≤4 words |
| **Social proof** | Logos / press / metrics / testimonials | Customer logos OR 2-3 quote testimonials OR aggregate numbers |
| **Features** | 3-6 capability blocks | Each block: title ≤8 words, body ≤40 words |
| **How it works** | 3-step flow showing the user journey | Each step: title ≤6 words, body ≤30 words |
| **Pricing** | Plans with feature differentiation | Plan name + tagline + bullet list + CTA |
| **FAQ** | Pre-answers common objections | Q ≤12 words, A ≤80 words |
| **Final CTA** | Repeat hero CTA before footer | Headline ≤10 words, CTA ≤4 words |
| **Footer** | Nav, legal, social | Standard nav links + tiny print |

---

## Hero section

The most-read part of any landing page. Most users decide whether to scroll based on the hero.

### Standard structure

```
Headline       ← The promise / outcome (≤12 words)
Subheadline    ← Who it's for + what it does (≤25 words)
[Primary CTA]  [Secondary CTA]
              ← Visual (screenshot / product video / illustration)
```

See [`hero-formula.md`](hero-formula.md) for the writing formula.

---

## Feature blocks

Groups of 3-6 capabilities, often presented as a grid.

### 3-block pattern (typical for top-of-funnel)

Each block: icon + title + 2-3 sentences.

### 6-block pattern (typical for mid-funnel)

Same shape, but more capabilities listed. Used when the product has many "killer" features.

### Detailed-feature pattern (typical for product page)

One feature gets a full section with: title, lead paragraph, bullet list, "more details" link, screenshot.

See [`feature-blocks.md`](feature-blocks.md).

---

## Pricing page

### Standard 3-plan structure (most common)

```
┌──────────┬──────────┬──────────┐
│  Free /  │  Pro     │  Team /  │
│  Starter │ (default)│ Business │
├──────────┼──────────┼──────────┤
│ $0       │ $X/mo    │ $Y/mo    │
│ tagline  │ tagline  │ tagline  │
│ features │ features │ features │
│ [CTA]    │ [CTA*]   │ [CTA]    │
└──────────┴──────────┴──────────┘
                * highlighted plan
```

### Per-plan copy

- **Plan name** (1-2 words): `Free` / `Pro` / `Business` / `Enterprise`
- **Tagline** (one short line, ≤12 words): "For solo builders shipping their first thing"
- **Price** (large): `$0/month` or `$29/user/month` or `Contact us`
- **Bullet list** (5-8 bullets, each ≤8 words): "Unlimited projects" / "10 team members"
- **CTA** (one button, ≤4 words): `Start free` / `Buy Pro` / `Contact sales`

### Free plan rules

- Always position as "Start free" not "Limited free version"
- Use "→ Upgrade anytime" small print, not "Forever free, no card"
- If the free plan has serious limits, name them positively: "Up to 3 projects" not "Limited to 3 projects"

### Enterprise / Business plan rules

- CTA is `Contact sales` or `Book demo`, not a self-serve purchase
- Tagline often says "Custom" or "For larger teams"
- Bullet list emphasizes governance: SSO, audit logs, SLA, dedicated support

---

## FAQ section

10 questions max for landing pages. The questions pre-answer objections.

### Standard structure

```
Q: {Question, ≤12 words}
A: {Answer, ≤80 words}
```

### Common FAQ topics

1. "How is this different from {competitor}?" — direct competitive Q
2. "Is there a free trial / free plan?" — pricing Q
3. "Can I cancel anytime?" — risk-reduction Q
4. "How long does setup take?" — friction Q
5. "What integrations do you support?" — compatibility Q
6. "Do you support {enterprise need: SSO/SOC2/etc.}?" — enterprise Q
7. "What if I exceed my plan's limits?" — billing-anxiety Q
8. "Where is my data stored?" — security Q
9. "Do you offer discounts (annual / nonprofit / education)?" — pricing Q
10. "Can I {migrate from} / {export to} {competitor}?" — switching Q

Don't include FAQ for the sake of having one. Each Q must address a real objection.

---

## SEO meta tags

Each page (homepage, pricing, features, blog post, etc.) needs:

### Title tag (HTML `<title>` + `og:title` + `twitter:title`)

- ≤60 characters (Google truncates after ~60)
- Pattern: `{primary keyword} — {differentiator} | {brand}`
- Examples:
  - "Free PDF Editor — Edit, Sign, Convert | PDFKit"
  - "Pricing — Plans for teams of any size | Acme"

### Meta description

- ≤160 characters (Google truncates after ~155)
- One sentence explaining what the page offers + a soft CTA
- Examples:
  - "Edit PDFs in your browser. Sign forms, redact pages, convert to Word. Free for 5 PDFs/month."
  - "Plans from $0 to enterprise. Free forever for solo builders. Start with 10 users in 60 seconds."

### Open Graph (Facebook / LinkedIn / iMessage previews)

- `og:title` (≤60 chars, same as `<title>` usually)
- `og:description` (≤200 chars, can be slightly longer than meta description)
- `og:image` (1200×630px recommended)
- `og:type` ("website" or "article")

### Twitter card

- `twitter:card` ("summary" or "summary_large_image")
- `twitter:title` (≤70 chars)
- `twitter:description` (≤200 chars)
- `twitter:image` (1200×675px for large_image)

See [`seo-meta.md`](seo-meta.md) for full template + per-page-type guidance.

---

## Paid ads

Each platform has its own char limits and conventions:

| Platform | Element | Char limit |
|---|---|---|
| **Google Ads** (Responsive Search Ad) | Headline (need 3-15) | 30 |
| | Description (need 2-4) | 90 |
| | Display path | 15 × 2 |
| **Facebook Ads** | Primary text | 125 (sometimes 600 — but truncate aggressively) |
| | Headline | 27 (single-line) or 40 (multi-line) |
| | Description | 27-30 |
| | CTA button | Picked from preset list |
| **LinkedIn Sponsored Content** | Intro text | 150 (before "see more") |
| | Headline | 70 |
| | Description | 100 |
| **X (Twitter) Promoted** | Tweet copy | 280 |
| | (No separate headline) | — |
| **Reddit Promoted** | Title | 300 |
| | Body | varies |
| **TikTok Ads** | Caption | 100 |

See [`ad-copy.md`](ad-copy.md) for per-platform templates + ratio rules.

---

## CTAs (Call-to-Action)

### CTA verbs by funnel position

| Funnel position | CTA verb | Example |
|---|---|---|
| Top of funnel (awareness) | "See", "Read", "Watch" | "See how it works" |
| Mid funnel (consideration) | "Try", "Compare", "Calculate" | "Try free" / "Compare plans" |
| Bottom funnel (purchase) | "Buy", "Subscribe", "Start" | "Buy Pro" / "Start free" |
| Demo / sales-led | "Book", "Schedule", "Talk to" | "Book demo" / "Talk to sales" |
| Newsletter / soft | "Get", "Subscribe", "Join" | "Get the newsletter" |

### Banned CTAs

- "Click here" → replace with the verb of the destination
- "Learn more" (if there's a more specific verb) — "See pricing" beats "Learn more"
- "Submit" → use the action ("Send message" / "Sign up")
- "Get started" → too vague; specify what they're starting ("Start free trial")

### CTA length

- ≤4 words for primary buttons
- Up to 6 words for secondary CTAs
- Verb first

---

## Audience-tone mapping

Marketing copy register matches the audience:

| Audience | Register | Examples |
|---|---|---|
| **Consumer SaaS** | Friendly-direct | "Photos that look like you, not like AI" |
| **B2B SMB** | Friendly-professional | "Run customer support without burning out your team" |
| **B2B Enterprise** | Formal-professional | "Enterprise-grade audit logs for compliance teams" |
| **Developer tools** | Terse-technical | "API docs in 3 minutes. Set the baseURL, ship." |
| **Creative tools** | Inspirational-direct | "Make the thing you've been thinking about" |
| **Fintech / health** | Trust-building, careful | "Bank-level security. Your data, your control." |

---

## Cross-references

- Hero writing formulas: [`hero-formula.md`](hero-formula.md)
- Feature blocks: [`feature-blocks.md`](feature-blocks.md)
- SEO + Open Graph + Twitter: [`seo-meta.md`](seo-meta.md)
- Paid ads per platform: [`ad-copy.md`](ad-copy.md)
- Quick char-limit table: [`char-limits.md`](char-limits.md)
- What to strip: [`banned-patterns.md`](banned-patterns.md)
