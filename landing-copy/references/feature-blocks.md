# Feature blocks

Where the landing page proves the hero's promise. Each feature block converts ONE capability into ONE user benefit.

---

## Standard pattern

```
[Icon / Visual]
{Feature title — ≤8 words}
{Feature body — ≤40 words}
[Optional: "Learn more →" link]
```

The icon anchors visual scanning. The title carries the user-facing label. The body explains the benefit.

---

## Title rules

The title is what the user reads first. It's NOT the technical feature name.

| ❌ Feature-name title (don't use) | ✅ Benefit title (use) |
|---|---|
| "API access" | "Build on top of Acme" |
| "SSO / SAML" | "One-click sign-in for your team" |
| "Custom fields" | "Track what matters to you" |
| "Dark mode" | "Dark mode for late-night writing" |
| "Real-time sync" | "Your team always sees the same thing" |
| "Audit logs" | "See who did what, when" |
| "Webhooks" | "Connect to your other tools" |
| "Database backups" | "Sleep through the night without worrying about data loss" |

Lead with the user outcome; the technical name follows in the body if relevant.

### Title length

- 4-8 words
- Verb-led when possible ("Track what matters", "Build on top of Acme")
- Avoid jargon unless audience is technical and jargon is the most-recognized term

---

## Body rules

The body explains WHO benefits and HOW. 1-3 sentences, ≤40 words total.

### Standard body pattern

```
{What it does, plain language}. {Who benefits / when to use}. {Optional: link out for details}.
```

Examples:

```
Title:  Catch bugs before your reviewer does
Body:   Acme reviews every PR, flags common issues, and suggests fixes — all
        before a human reviewer sees it. Used by teams of 5-50 engineers.
```

```
Title:  One-click sign-in for your team
Body:   Connect your existing SSO (Okta, Google Workspace, Azure AD) so your team
        signs in with one click. No password management.
```

```
Title:  See who did what, when
Body:   Every action in Acme is logged with user, timestamp, and IP. Export to your
        SIEM for compliance audits.
```

### Body anti-patterns

- Restating the title — body must add information
- Using marketing adjectives ("powerful", "intuitive", "beautiful") — show, don't tell
- Long sentences with multiple ideas — split or cut
- Hand-wavy "and more" — close the sentence or list specifics

---

## 3-block layout (top-of-funnel landing)

For when the product needs concise summary, not exhaustive feature list.

Each block: icon + title + 2-sentence body. Three blocks total.

### Pattern

Each block addresses ONE primary objection or value:
- Block 1: the headline benefit ("Speed")
- Block 2: the second-most-important benefit ("Quality")
- Block 3: the trust / safety benefit ("Security")

Example (for a code-review tool):

```
🚀 Faster PRs
Catches bugs in seconds, not days. Average team cuts review time 60%.

🎯 Better catches
Trained on 10M+ PRs from production codebases. Finds bugs your humans miss.

🔒 Your code stays yours
Code never leaves your VPC. SOC 2 Type II, GDPR, HIPAA available.
```

### When to use 3-block

- Top-of-funnel landing (homepage hero immediately after)
- Email-driven landing (visitor came from an ad, needs quick scan)
- Mobile-first product (less scroll real estate)
- Limited differentiated features (don't pad to 6 if you only have 3)

---

## 6-block layout (mid-funnel landing)

When the product has 5-7 distinct selling points and visitor is more invested.

### Pattern

Two rows × three columns. Each block: smaller icon + title + 1-sentence body.

Example (for a project-management tool):

```
[icon]                 [icon]                 [icon]
Real-time sync         Custom workflows       Time tracking
Your team always       Tailor stages to       Built-in. No
sees the same thing.   how your team works.   second tool needed.

[icon]                 [icon]                 [icon]
Integrations           Custom fields          Native mobile
Connects to Slack,     Track what matters     iOS + Android with
GitHub, Linear, etc.   to your projects.      full feature parity.
```

### When to use 6-block

- Product page (visitor came from a hero-section CTA, wants to see the breadth)
- Feature-comparison page
- Competitor-comparison page (this is the X we have that competitor doesn't)

---

## Detailed-feature pattern (deep dive)

When ONE feature is the killer differentiator and deserves a full section.

### Pattern

```
[Hero image / GIF showing the feature in action]

Section header:        {Bold positioning — ≤10 words}
Lead paragraph:        {2-3 sentences explaining the feature's value}

Bullet list:           [• Specific capability 1]
                       [• Specific capability 2]
                       [• Specific capability 3]
                       [• Specific capability 4]

[CTA button or link to docs]
```

Example (for an AI code-review tool):

```
[GIF: PR with inline AI comments appearing]

Section header:     Inline review comments, not after-the-fact summaries
Lead paragraph:     Acme reviews every line of every PR as your team pushes —
                    not after merge, not in a separate dashboard. Comments appear
                    where humans can act on them.

Bullet list:
  • Inline GitHub PR comments (mirrored in GitLab + Bitbucket)
  • Linked to the specific line + the related blame history
  • Severity tagged (BLOCKER / MAJOR / MINOR)
  • Dismissible per-comment with reasoning
  • Authority levels: auto-block, advisory, FYI

[See it in action →]
```

### When to use detailed-feature pattern

- The killer-differentiator feature (1-2 per landing page max)
- Features that require a visual to understand
- Features that competitors can't claim (so you can spend the real-estate)

---

## "How it works" 3-step

Adjacent to feature blocks. Shows the user journey in 3 steps.

### Pattern

```
1️⃣  {Step 1 title — ≤6 words}
    {Body — ≤30 words}

2️⃣  {Step 2 title — ≤6 words}
    {Body — ≤30 words}

3️⃣  {Step 3 title — ≤6 words}
    {Body — ≤30 words}
```

### When to use

- Onboarding-anxiety reduction (visitor wants to see "this won't take 2 hours")
- Products with non-obvious setup (the steps demystify)
- B2B sales-led products (the 3 steps map to "discovery / setup / value realization")

### Examples

```
1️⃣ Connect your repo                  Acme installs as a GitHub / GitLab / Bitbucket app. One-click.
2️⃣ Set your team's quality bar         Pick the rules that fire as blockers vs advisory. Sensible defaults.
3️⃣ Ship better code                    From day one, every PR gets a review. Your team gets back review hours.
```

---

## Social proof — adjacent to features

After (or interleaved with) features:

### Customer logo strip

```
"Trusted by teams at"
[Logo] [Logo] [Logo] [Logo] [Logo]
```

3-7 logos. Pick recognizable brands. Don't pad with logos no visitor knows.

### Quote testimonials

```
"{Quote — ≤30 words}"
— {Name}, {Title} at {Company}
```

Most effective when:
- Quote names a specific outcome (number, time saved, problem solved)
- Person is recognizable in the audience's industry
- Logo of the company sits next to the quote

Example:

```
"Acme cut our PR review queue from 18 to 4 in the first month.
The team got their afternoons back."
— Sarah Chen, Engineering Manager at Stripe   [Stripe logo]
```

### Aggregate numbers

```
10,000+ teams       100M+ PRs reviewed       4.8/5 on G2
```

Use when:
- Numbers are genuinely impressive (don't include "10+ customers" — looks small)
- Reviews are aggregated from real platforms (G2, Capterra, etc.) — name the source
- Pair with a logo strip for additional credibility

---

## Cross-references

- Where features sit on the page: [`surfaces.md`](surfaces.md)
- Hero (what comes before features): [`hero-formula.md`](hero-formula.md)
- What NOT to write: [`banned-patterns.md`](banned-patterns.md)
