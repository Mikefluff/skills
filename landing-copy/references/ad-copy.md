# Ad copy per platform

Paid ads have strict char limits + per-platform conventions. Pick the platform's template.

---

## Google Ads — Responsive Search Ads (RSA)

The dominant Google Ad format. You provide 3-15 headlines and 2-4 descriptions; Google mixes them into combinations.

### Limits

- **Headline**: ≤ 30 characters (need 3-15 distinct)
- **Description**: ≤ 90 characters (need 2-4 distinct)
- **Display path**: ≤ 15 characters per path × 2 (e.g. `example.com/pricing/plans`)

### Strategy

You're optimizing for **all combinations** Google tries. Each headline should:
- Stand alone (Google may show it without the others)
- Cover a different angle (don't repeat)

Provide a mix:
- 2-3 headlines focused on the **brand name**
- 2-3 headlines focused on the **primary benefit**
- 2-3 headlines focused on **specific features**
- 1-2 headlines with **urgency / CTA** ("Free trial — 14 days")
- 1-2 headlines with **proof** ("Trusted by 10,000 teams")

### Example RSA

**Product**: code-review AI tool, B2B SaaS, targeting eng managers

**Headlines** (12 total, 30 chars max each):

```
AI Code Review for Teams         (28)
Cut PR Review Time 60%           (24)
Acme — AI Code Reviewer          (23)
Catch Bugs Before Merge          (22)
For Teams of 5-50 Engineers      (28)
Used by Stripe, Linear           (22)
Free 14-Day Trial — No Card      (28)
GitHub + GitLab + Bitbucket      (27)
Smart Review Comments            (22)
SOC 2 Compliant                  (15)
Trained on 10M+ Real PRs         (24)
2-Minute Setup, See Results Now  (29)
```

**Descriptions** (4 total, 90 chars max each):

```
AI reviews every PR in seconds. Catches bugs, suggests fixes, learns your team's style.  (85)
Free 14-day trial. No credit card required. Works with GitHub, GitLab, and Bitbucket.    (84)
Cut average PR review time from 2 days to 4 hours. Used by Stripe, Linear, and Vercel.   (88)
SOC 2 Type II certified. Your code never leaves your VPC. Audit logs for compliance.     (87)
```

**Display path**: `example.com/code-review/free-trial` (paths: `code-review` + `free-trial`)

---

## Facebook Ads / Instagram Ads / Meta Ads

Limits vary by placement (Feed vs Story vs Reels). Conservative defaults:

### Limits

- **Primary text**: ~125 characters before "See more" (max 600, but write ≤125)
- **Headline**: ≤ 27 characters (single line) or ≤ 40 (multi-line)
- **Description**: ≤ 27 characters (rare, only shown in some placements)
- **CTA button**: from preset list (Learn More, Shop Now, Sign Up, etc.)

### Strategy

Facebook is **visual-first** + **scroll-stop oriented**. The image / video does most of the work; copy provides context + CTA.

Primary text patterns:
- **Lead with the hook in first 5 words** (mobile users stop scrolling on the first line)
- **One concrete benefit + one specific number** if available
- **Question opener** ("Tired of X?") — uses curiosity
- **Direct address** ("Founders: you're shipping too slow because...")

### Example FB Ad (B2B SaaS — code review tool)

**Variant 1**:
```
Primary:  Engineering managers — your PR review queue is the bottleneck. Acme reviews every PR in 60 seconds. Cut your team's review time 60%. Free 14-day trial.
Headline: Cut PR Review Time 60%        (23)
Description: Free 14-Day Trial          (16)
CTA:      Start Free Trial
```

**Variant 2**:
```
Primary:  47 PRs in the queue. 3 reviewers. Half the team blocked. Sound familiar? Acme reviews PRs automatically, in seconds. Used by Stripe, Linear, Vercel.
Headline: AI Code Review                (15)
Description: Trusted by Stripe          (16)
CTA:      Learn More
```

**Variant 3**:
```
Primary:  "Acme cut our PR review queue from 18 to 4 in the first month. The team got their afternoons back." — Sarah, Engineering Manager at Stripe.
Headline: 60% Less Review Time          (20)
Description: Real Customer Story        (18)
CTA:      Watch Demo
```

The three variants test:
- Variant 1: benefit-led
- Variant 2: scenario-led (curiosity)
- Variant 3: testimonial-led

### Facebook anti-patterns

- ❌ More than 20% text in the image (FB may de-prioritize delivery)
- ❌ "Click here" / "Click now" — feels like spam
- ❌ All-caps in headline ("STOP WASTING TIME")
- ❌ Misleading clickbait — high engagement but conversion loss
- ❌ Generic stock photography

---

## LinkedIn Sponsored Content

### Limits

- **Intro text**: ~150 characters before "see more"
- **Headline**: ≤ 70 characters
- **Description**: ≤ 100 characters (rare placement)
- **CTA**: from preset list (Apply, Download, Learn More, Sign Up, Subscribe, etc.)

### Strategy

LinkedIn is **business-tone** + **higher-intent**. Visitors are scrolling for work-related content; B2B works better than B2C here.

Patterns that work:
- **Role-specific opener** ("Engineering Managers:") or industry ("For B2B SaaS founders:")
- **Specific business metric** (revenue, retention, headcount, time saved)
- **Industry credibility** (named customers, awards, certifications)

### Example LinkedIn Ad (B2B SaaS — code review tool)

```
Intro:     Engineering managers — your team's biggest bottleneck isn't writing code. It's reviewing it. Acme cuts PR review time 60% with AI-powered code analysis.
Headline:  Cut Your Team's PR Review Time 60% (with AI code review)
Description: Used by Stripe, Linear, Vercel. Free 14-day trial.
CTA:       Start Free Trial
```

Length check:
- Intro: ~167 chars — slightly over 150 limit; trim to:
  `Engineering managers — your team's biggest bottleneck isn't writing code. It's reviewing it. Acme cuts PR review time 60% with AI.` (~127)
- Headline: ~52 chars — under 70 ✓
- Description: ~52 chars — under 100 ✓

---

## X (Twitter) Promoted Posts

X ads are just promoted tweets. The constraint is the tweet itself + the X audience norms.

### Limits

- **Tweet copy**: 280 characters (with media counting as 24 chars from the limit)
- **Thread**: rare for ads; single promoted tweet most common

### Strategy

X is **conversational** + **opinion-led** + **fast**. Ads that feel like organic content perform better.

Patterns that work:
- **Tweet-native shape** (not corporate-marketing copy)
- **Strong opening hook** (first 7 words decide engagement)
- **Specific claim** (with number or named customer)
- **One link OR one CTA** — not both

### Example X Promoted Ad

**Variant 1** (founder-direct):
```
We built Acme because we got tired of waiting 2 days for PR reviews.

It reviews every PR in 60 seconds. Catches bugs. Suggests fixes.

Free 14-day trial — no card required.

acme.com/trial
```
(231 chars without URL)

**Variant 2** (counterintuitive):
```
Hot take: your slowest engineer isn't slow. They're waiting for PR review.

Acme reviews PRs in 60s, freeing your senior engineers to actually code.

Used by Stripe, Linear, Vercel.

acme.com
```
(214 chars without URL)

**Variant 3** (numbers):
```
PR review queue average across our 200 customers:

Before Acme: 18 PRs, 2.1 days avg wait
After Acme:  4 PRs, 4 hours avg wait

That's the metric we live by.

Try it free — acme.com/trial
```
(220 chars)

---

## Reddit Promoted Posts

### Limits

- **Title**: ≤ 300 characters
- **Body**: varies by subreddit; assume ≤500 chars for scannable

### Strategy

Reddit is **community-aware** + **anti-marketing**. Ads that feel salesy get downvoted and lose reach.

Patterns that work:
- **Subreddit-aware framing** (different copy for r/programming vs r/Entrepreneur vs r/saas)
- **Founder-direct voice** ("I built X because...") often outperforms corporate
- **One link** (in body, not title)
- **Long-form copy** can work where it can't elsewhere

---

## TikTok Ads

### Limits

- **Caption**: ≤ 100 characters
- **Video**: the platform; copy is secondary

### Strategy

TikTok is **video-first**, **trend-aware**, **short-attention**. Copy is just the caption — the video carries the message.

Patterns:
- **Hook in first 3 seconds** of video (this is video work, not copy work)
- **Caption**: ONE specific value claim or curiosity hook
- **Avoid**: branded language, corporate tone

---

## Cross-platform considerations

### Variants count

Always provide multiple variants — paid ad platforms optimize via A/B testing.

| Platform | Min variants | Max useful |
|---|---|---|
| Google RSA | 3 headlines, 2 descriptions | 15 headlines, 4 descriptions |
| Facebook | 3-5 ads | 10 ads in a campaign |
| LinkedIn | 2-3 ads | 5-7 ads |
| X | 2-3 promoted | 5 promoted |
| Reddit | 2-3 promoted | 3-5 promoted |

### Audience tagging

If the campaign targets multiple audiences (e.g. "engineering managers" vs "individual contributors"), write **separate copy variants per audience** — don't try to make one ad work for both.

### Brand voice consistency

Across platforms, the brand voice should be recognizable BUT register can shift:

- LinkedIn: more formal, role-led
- Facebook: more direct, benefit-led
- X: more conversational, opinion-led
- Reddit: more founder-voice, community-aware
- TikTok: more trend-aware, hook-led

A B2B SaaS shouldn't use the same copy on LinkedIn and X — the audience reads differently.

---

## What NOT to do across all platforms

❌ Marketing hype ("revolutionary", "game-changing")
❌ Generic CTAs ("Get started" / "Click here")
❌ Lying / misleading claims (ad-platform penalties + brand damage)
❌ Reusing the same copy across platforms (different audiences read differently)
❌ Single variant (no A/B test = no learning)
❌ All caps headlines (looks like spam on most platforms)
❌ Emoji-heavy copy on professional platforms (LinkedIn, B2B Google)
❌ "Limited time offer" without actually being limited (fake urgency = trust loss)

---

## Quick reference — picking the right ad platform

| If your audience is... | Best platform |
|---|---|
| Active job-seekers / B2B decision-makers | LinkedIn |
| General consumer with broad reach | Facebook / Instagram |
| Tech-curious / opinion-driven / fast scrollers | X (Twitter) |
| Niche-community-engaged | Reddit (right subreddit) |
| Gen Z / video-native | TikTok |
| High-intent search ("buying-mode") | Google Ads |
| Visual products (apparel / lifestyle) | Instagram / TikTok |
| Pure-play developers | Reddit r/programming + Twitter + sponsored newsletters |

---

## Cross-references

- Full char-limit table: [`char-limits.md`](char-limits.md)
- What to strip: [`banned-patterns.md`](banned-patterns.md)
- Hero formulas (for context): [`hero-formula.md`](hero-formula.md)
