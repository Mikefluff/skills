# landing-copy — calibration before/after pairs

8 paired examples covering hero / feature / SEO / Google Ad / Facebook Ad / LinkedIn / Twitter / FAQ. Each shows a weak version → strong version with deltas.

---

## 1. Hero section (B2B SaaS, code-review tool)

### Before (weak)

```
Headline:    Powerful AI for Smarter Code Reviews
Subheadline: Acme is the revolutionary code review platform that empowers
             your team to ship faster than ever before. Built with cutting-edge
             AI technology.
CTA:         Get Started
```

What's wrong:
- "Powerful AI" / "Smarter" / "revolutionary" / "cutting-edge" — marketing hype
- "Ship faster than ever before" — vague, no number
- "Built with cutting-edge AI" — empty claim
- "Get Started" — vague CTA

### After (rewrite — Julian Shapiro formula)

```
Headline:    Cut PR review time from 2 days to 4 hours
Subheadline: Acme is an AI code reviewer for engineering teams of 5-50.
             Catches bugs, suggests fixes, ships PRs. Used by Stripe, Linear, Vercel.
CTA:         Try free for 14 days
Secondary:   See how it works
```

### Deltas applied
- Specific quantified benefit in headline (2 days → 4 hours)
- Subheadline: WHAT (AI code reviewer) + WHO (teams of 5-50) + DIFFERENTIATOR (catches bugs, suggests fixes, ships PRs) + PROOF (Stripe, Linear, Vercel)
- CTA specific to next action (14-day trial)
- Secondary CTA for not-yet-ready visitors

---

## 2. Feature block (3-block layout)

### Before (weak)

```
Block 1: Faster PRs
Title:   Lightning-fast PR reviews
Body:    Acme's powerful AI reviews your PRs incredibly quickly, helping your
         team be more productive.

Block 2: Better Quality
Title:   Improved code quality
Body:    Our advanced algorithms catch bugs that humans might miss, ensuring
         high-quality code shipped every time.

Block 3: Security
Title:   Enterprise-grade security
Body:    Acme is built with security in mind, featuring world-class protection
         for your sensitive code.
```

What's wrong:
- "Lightning-fast", "powerful", "advanced", "enterprise-grade", "world-class" — hype
- "Incredibly quickly" — no number
- "Catch bugs that humans might miss" — vague
- "Built with security in mind" — empty

### After (rewrite)

```
Block 1: 🚀 Faster PRs
Title:   60% less time in review queue
Body:    Acme reviews every PR in 60 seconds. Average team cuts review queue
         from 18 PRs to 4 in the first month.

Block 2: 🎯 Better catches
Title:   Trained on 10M+ production PRs
Body:    Acme is trained on real PRs from open-source and enterprise codebases.
         Finds bugs that humans miss in 12% of reviews.

Block 3: 🔒 Your code stays yours
Title:   Code never leaves your VPC
Body:    Acme runs in your AWS / GCP / Azure account. SOC 2 Type II, GDPR
         compliant, HIPAA-available.
```

### Deltas applied
- Specific numbers in each title (60%, 10M+, "never leaves")
- Body has specific outcomes (18 → 4 PRs, 12% catch rate)
- Security block names actual compliance (SOC 2, GDPR, HIPAA), not "enterprise-grade"
- Each block has ONE clear benefit + proof

---

## 3. SEO meta (homepage)

### Before (weak)

```html
<title>Acme - Code Review Software</title>
<meta name="description" content="Acme is the leading code review software. We help teams ship faster with our powerful AI. Sign up today!" />
```

What's wrong:
- Title: brand-first wastes the clickable real estate
- Title generic ("Code Review Software" — any tool can say this)
- Description: "leading" without proof, "powerful AI" hype, "sign up today" generic CTA

### After (rewrite)

```html
<title>AI Code Review for Engineering Teams — Cut Review Time 60% | Acme</title>
<meta name="description" content="Acme reviews PRs in 60 seconds. Used by Stripe, Linear, Vercel. SOC 2 Type II. Free 14-day trial — no card required." />
```

Length check:
- Title: 67 chars — slightly over 60 limit. Trim:
  `AI Code Review for Engineering Teams — Cut Review Time 60%` (58)
  or keep brand: `Code Review for Teams — Cut Review Time 60% | Acme` (51)
- Description: 132 chars — under 160 ✓

### Deltas applied
- Title: keyword-first ("AI Code Review for Engineering Teams"), specific benefit ("60%"), brand last
- Description: specific value (60s reviews), proof (Stripe + Linear + Vercel), trust signal (SOC 2), specific offer (14-day trial, no card)

---

## 4. Google Ad (Responsive Search Ad)

### Before (weak)

```
Headline 1: Acme - The Best Code Review Tool
Headline 2: Powerful AI Code Reviews
Headline 3: Sign Up Today for Free
Description 1: Acme is the leading code review tool. Save time and improve quality.
Description 2: Try Acme today and see why thousands of teams love us.
```

What's wrong:
- "Best" / "Powerful" hype
- All headlines repeat the same angle (no diversity)
- Descriptions vague ("Save time and improve quality" — no numbers)

### After (rewrite)

```
Headlines (12 distinct):
H1:  AI Code Review for Teams         (28)
H2:  Cut PR Review Time 60%           (24)
H3:  Acme — AI Code Reviewer          (23)
H4:  Catch Bugs Before Merge          (22)
H5:  For Teams of 5-50 Engineers      (28)
H6:  Used by Stripe, Linear, Vercel   (29)
H7:  Free 14-Day Trial — No Card      (28)
H8:  GitHub + GitLab + Bitbucket      (27)
H9:  SOC 2 Type II Compliant          (24)
H10: Trained on 10M+ Real PRs         (24)
H11: 2-Minute Setup, Review Now       (28)
H12: Stop Waiting 2 Days for PRs      (28)

Descriptions (4 distinct):
D1: AI reviews every PR in 60 seconds. Catches bugs, suggests fixes, learns your team's style.  (89)
D2: Free 14-day trial, no card required. Works with GitHub, GitLab, and Bitbucket.              (82)
D3: Cut PR review queue from 18 PRs to 4 in the first month. Used by Stripe, Linear, Vercel.    (89)
D4: SOC 2 Type II. Your code runs in your VPC, never leaves your cloud account.                  (78)

Display path: example.com/code-review/free-trial
```

### Deltas applied
- 12 distinct headlines covering 4 angles (brand, benefit, audience, proof)
- Each under 30 chars
- 4 descriptions, each with a specific number or proof point
- All 4 angles different — Google's ML can pick the best combination

---

## 5. Facebook Ad (with 3 variants)

### Before (weak)

```
Primary: We're excited to introduce Acme, the revolutionary AI code review tool!
         Sign up today!
Headline: Acme - Code Review
Description: Try Acme today
```

What's wrong:
- "Excited to introduce" + "revolutionary" — instant scroll
- Description: "Try Acme today" — no value prop

### After (rewrite — 3 variants)

**Variant 1** (benefit-led):
```
Primary:  Engineering managers — your PR review queue is the bottleneck. Acme reviews every PR in 60 seconds. Cut your team's review time 60%.  (148 — over 125; trim to ~125)
Trimmed:  Eng managers — your PR queue is the bottleneck. Acme reviews every PR in 60 seconds. Cut review time 60%.  (122)
Headline: Cut PR Review Time 60%       (23)
Description: Free 14-Day Trial         (16)
CTA:      Start Free Trial
```

**Variant 2** (scenario-led):
```
Primary:  47 PRs in the queue. 3 reviewers. Half the team blocked. Sound familiar? Acme reviews PRs in seconds. Used by Stripe, Linear, Vercel.  (130 — slight over; trim)
Trimmed:  47 PRs queued. 3 reviewers. Half the team blocked. Sound familiar? Acme reviews PRs automatically. Used by Stripe.  (118)
Headline: AI Code Review               (16)
Description: Trusted by Stripe         (15)
CTA:      Learn More
```

**Variant 3** (testimonial-led):
```
Primary:  "Acme cut our PR review queue from 18 to 4 in the first month. The team got their afternoons back." — Sarah, Eng Manager at Stripe.  (140 — over; trim)
Trimmed:  "Acme cut our review queue from 18 to 4 in the first month. The team got afternoons back." — Sarah, Stripe Eng Mgr.  (114)
Headline: 60% Less Review Time         (21)
Description: Real Customer Story       (19)
CTA:      Watch Demo
```

### Deltas applied
- 3 variants for A/B testing
- Each variant tests different copy angle (benefit / scenario / testimonial)
- All under 125-char "before See more" threshold
- CTAs match the variant's intent (Start Trial / Learn More / Watch Demo)

---

## 6. LinkedIn Sponsored Content

### Before (weak)

```
Intro:    Looking to improve your code reviews? Acme is the world-class
          AI code review platform trusted by thousands of teams worldwide.
Headline: Acme - The Leader in AI Code Review
Description: Sign up for a free trial today
```

What's wrong:
- "World-class" / "trusted by thousands" without specifics
- "Looking to improve...?" — generic question opener
- "The Leader" — empty claim

### After (rewrite)

```
Intro:     Engineering managers — your team's biggest bottleneck isn't writing code. It's reviewing it. Acme cuts PR review time 60% with AI.  (134)
Headline:  Cut Your Team's PR Review Time 60% with AI Code Review                                     (62)
Description: Used by Stripe, Linear, Vercel. Free 14-day trial — no card.                              (75)
CTA:       Start Free Trial
```

### Deltas applied
- Intro: role-specific opener ("Engineering managers")
- Specific bottleneck claim, specific number
- Headline: keyword (PR review time) + specific number (60%) + tech (AI code review)
- Description: customer proof + offer (free trial, no card)
- All under platform limits

---

## 7. X (Twitter) Promoted Post

### Before (weak)

```
Excited to launch Acme - the powerful new AI code review tool that's
changing the game! 🚀 Sign up today: acme.com  ✨

#AI #CodeReview #DevTools #Innovation
```

What's wrong:
- "Excited to launch" / "changing the game" — hype
- Emoji + hashtag overload (low signal-to-noise)
- "Powerful new AI" / "tool" — vague
- No clear value prop in first 7 words

### After (rewrite — 3 variants)

**Variant 1** (founder-direct):
```
We built Acme because we got tired of waiting 2 days for PR reviews.

It reviews every PR in 60 seconds. Catches bugs. Suggests fixes.

Free 14-day trial — no card required.

acme.com/trial
```
(218 chars without URL counted)

**Variant 2** (counter-intuitive):
```
Hot take: your slowest engineer isn't slow. They're waiting for PR review.

Acme reviews PRs in 60s, freeing your senior engineers to actually code.

Used by Stripe, Linear, Vercel.

acme.com
```
(204 chars)

**Variant 3** (numbers):
```
PR review queue average across our 200 customers:

Before Acme: 18 PRs, 2.1 days avg wait
After Acme:  4 PRs, 4 hours avg wait

That's the metric we live by.

Free 14-day trial — acme.com/trial
```
(208 chars)

### Deltas applied
- 3 variants for A/B
- All tweet-native shape (not corporate marketing)
- Each variant has a strong opening hook (first 7 words decide engagement)
- Specific claim per variant (60s reviews / queue stats / before-after)
- One CTA + one URL (clean, not link-stuffed)
- No emoji (X feed; emoji here would feel try-hard for the audience)

---

## 8. FAQ section

### Before (weak)

```
Q: Why should I choose Acme?
A: Acme is the world-class, powerful, AI-driven code review platform that's
   trusted by industry leaders. We offer unparalleled features at competitive
   prices.

Q: Is there a free trial?
A: Yes! We offer a free trial period to try Acme out.

Q: How does pricing work?
A: We have several pricing plans designed to fit your needs. Please check our
   pricing page for more details.

Q: Is my code safe?
A: Absolutely! We take security very seriously and have implemented many
   security measures to protect your data.
```

What's wrong:
- All Qs are vague
- All As are marketing hype without specifics
- "Industry-leading", "world-class" — banned
- "Several pricing plans designed to fit your needs" — meaningless
- "Many security measures" — opaque

### After (rewrite)

```
Q: How is Acme different from other code review tools (Codecov, SonarQube, etc.)?
A: Other tools analyze code post-merge or via dashboards. Acme reviews PRs
   inline, in real-time, as your team pushes. Comments appear directly in your
   PR — no extra dashboard, no separate workflow.

Q: Is there a free trial?
A: Yes — 14 days free, no credit card required. Includes all features. After the
   trial, you can either upgrade to a paid plan or continue with the free tier
   (up to 10 PRs/month, single repo).

Q: How does pricing work?
A: Three plans. **Free**: up to 10 PRs/month on 1 repo. **Pro**: $29/user/month,
   unlimited PRs + repos. **Business**: $99/user/month, SSO + audit logs + SOC 2
   reporting + dedicated CSM. Annual billing saves 20%. [See full pricing →]

Q: Is my code safe?
A: Acme runs in your own AWS / GCP / Azure account. Your code never leaves your
   VPC. We hold SOC 2 Type II certification, are GDPR-compliant, and HIPAA-
   available on the Business plan. Annual third-party security audits.

Q: How long does setup take?
A: ~2 minutes. Install the Acme app on GitHub / GitLab / Bitbucket, point it at
   your first repo, and Acme is reviewing PRs immediately. No build pipeline
   changes, no configuration files required.

Q: What if I exceed the free plan's 10 PRs/month?
A: Acme stops reviewing new PRs that month but doesn't auto-charge. We'll email
   you when you hit 8/10 and 10/10. You can upgrade anytime mid-month and Acme
   resumes immediately (no PR backlog penalty).
```

### Deltas applied
- Each Q addresses a real objection (competitor diff / trial / pricing / security / setup time / billing anxiety)
- Each A has specific facts (numbers, named competitors, certifications, exact pricing)
- "Industry-leading" / "world-class" / "many security measures" → specific claims with proof
- Pricing Q has actual prices (not "check pricing page")
- Security Q names specific certifications (SOC 2, GDPR, HIPAA)
- Free-tier overflow Q removes purchase anxiety with specifics

---

## Pattern summary

Across all 8 rewrites:

1. **Strip hype**: revolutionary / world-class / powerful / cutting-edge → deleted
2. **Specific numbers everywhere**: "ship faster" → "from 2 days to 4 hours"
3. **Specific verbs in CTAs**: "Get started" → "Start free trial"
4. **Named customers / proof**: "trusted by leading companies" → "Stripe, Linear, Vercel"
5. **Audience-tagged copy**: "engineers" → "engineering managers" / "teams of 5-50"
6. **Each surface respects its limits**: char budgets met, mobile-friendly
7. **Multiple variants for ads**: A/B testing built into the output
8. **Specific differentiators**: "AI code review" → "inline, in real-time, as your team pushes"
9. **Pricing transparent**: "several plans" → "Free / $29 / $99"
10. **No emoji where it looks try-hard** (LinkedIn / X / SEO meta); reserved for organic moments
