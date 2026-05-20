# Char limits — quick reference

Every surface, every limit, in one table. Going over = truncation in production.

---

## Master table

| Surface | Element | Hard limit (chars) | Sweet spot |
|---|---|---|---|
| **SEO** | `<title>` tag | 60 | 50-60 |
| **SEO** | `<meta name="description">` | 160 | 150-155 |
| **Open Graph** | `og:title` | 60 | 50-60 |
| **Open Graph** | `og:description` | 200 | 150-200 |
| **Twitter card** | `twitter:title` | 70 | 50-70 |
| **Twitter card** | `twitter:description` | 200 | 150-200 |
| **Hero** | Headline | (UX limit) ≤ 12 words / ≤ 60 chars | 5-9 words |
| **Hero** | Subheadline | (UX limit) ≤ 25 words / ≤ 150 chars | 15-25 words |
| **Hero** | Primary CTA | ≤ 4 words / ≤ 25 chars | 2-3 words |
| **Hero** | Secondary CTA | ≤ 6 words / ≤ 35 chars | 2-4 words |
| **Feature block** | Title | ≤ 8 words / ≤ 50 chars | 4-7 words |
| **Feature block** | Body | ≤ 40 words / ≤ 250 chars | 25-35 words |
| **Pricing plan** | Name | ≤ 2 words / ≤ 15 chars | 1 word |
| **Pricing plan** | Tagline | ≤ 12 words / ≤ 75 chars | 6-10 words |
| **Pricing plan** | Bullet | ≤ 8 words / ≤ 50 chars | 3-5 words |
| **Pricing plan** | CTA | ≤ 4 words / ≤ 25 chars | 2-3 words |
| **FAQ** | Question | ≤ 12 words / ≤ 75 chars | 5-10 words |
| **FAQ** | Answer | ≤ 80 words / ≤ 500 chars | 30-60 words |
| **Google Ads (RSA)** | Headline | 30 | 25-30 |
| **Google Ads (RSA)** | Description | 90 | 80-90 |
| **Google Ads (RSA)** | Display path | 15 × 2 | 8-12 each |
| **Google Ads (Sitelink)** | Title | 25 | 20-25 |
| **Google Ads (Sitelink)** | Description | 35 × 2 | 25-35 each |
| **Facebook Ads** | Primary text | 600 hard / 125 before "See more" | ≤ 125 |
| **Facebook Ads** | Headline | 27 (single line) / 40 (multi-line) | ≤ 27 |
| **Facebook Ads** | Description | 27-30 | 20-27 |
| **Instagram Story Ads** | Caption | similar to FB | similar |
| **LinkedIn Sponsored Content** | Intro text | 150 before "see more" | 100-150 |
| **LinkedIn Sponsored Content** | Headline | 70 | 50-70 |
| **LinkedIn Sponsored Content** | Description | 100 | 70-100 |
| **LinkedIn Text Ads** | Headline | 25 | ≤ 25 |
| **LinkedIn Text Ads** | Description | 75 | ≤ 75 |
| **LinkedIn Message Ads** | Subject | 60 | ≤ 60 |
| **LinkedIn Message Ads** | Body | 1500 | 200-500 (keep short) |
| **X (Twitter) Ads** | Tweet | 280 | ≤ 250 (leave room for URLs) |
| **Reddit Promoted Posts** | Title | 300 | 80-150 |
| **TikTok Ads** | Caption | 100 | ≤ 100 |
| **YouTube Ads (TrueView)** | Headline | 15 | ≤ 15 |
| **YouTube Ads (TrueView)** | Description (line 1) | 35 | ≤ 35 |
| **YouTube Ads (TrueView)** | Description (line 2) | 35 | ≤ 35 |
| **Newsletter ads (typical)** | Headline | 60-80 | 40-60 |
| **Newsletter ads (typical)** | Body | 200-400 | 200-300 |

---

## Per-channel notification limits (for marketing emails / push)

| Channel | Element | Limit |
|---|---|---|
| **Email subject (gmail mobile)** | — | ~30-40 chars before truncation |
| **Email preview text (gmail)** | — | ~90 chars before truncation |
| **Email subject (gmail desktop)** | — | ~60 chars |
| **iOS push notification body** | — | 178 chars (lock screen) |
| **Android push notification body** | — | ~240 chars |
| **Slack message preview** | — | ~140 chars |

If your marketing message goes through any of these, design for the truncation point.

---

## i18n expansion (when planning for multiple languages)

If the copy will be translated, the English version needs HEADROOM:

| English → Target | Typical expansion |
|---|---|
| English → German | +30-50% |
| English → Russian | +20-40% |
| English → French | +15-25% |
| English → Spanish | +10-25% |
| English → Italian | +10-20% |
| English → Portuguese | +10-25% |
| English → Japanese | -50% (CJK is denser) |
| English → Chinese (Simplified) | -50% to -60% |
| English → Korean | -40% to -50% |

### Practical impact

If your **English** Google Ad headline is 30 chars (the hard limit), the German version will be ~40 chars — over the limit. You'd need to write the English variant at 22-23 chars to leave room.

For multi-language campaigns:
- Headlines: design for **70% of the hard limit** in English to leave room for German/Russian/French
- Descriptions: design for **75% of the hard limit**
- CJK-only campaigns: design for **100% of hard limit** (no expansion concern)

---

## URL impact on Twitter / SMS / push

Twitter shortens all URLs to ~24 characters (`t.co` link), regardless of original length. Similarly:

- Bit.ly / branded short links: usually consistent length
- SMS shortlinks: 20-25 chars
- Push notification URLs: don't include the URL in the body; pass via metadata

### Practical impact

In a 280-char Twitter ad, ONE URL costs you 24 chars (you have ~256 for prose). TWO URLs cost ~48. Plan accordingly.

---

## Sanity-check process

Before publishing any copy:

1. **Read the copy in the target rendering surface** — not in your editor. Tweet preview, Facebook preview, Google Ad preview, browser tab.
2. **Verify on mobile** — most platforms show LESS on mobile than your desktop preview.
3. **If the copy was translated** — re-check the rendered length per locale.
4. **If you A/B test variants** — ensure each variant is within limit; many platforms don't show the variants that exceed the limit.

---

## Common over-limit failures

| Symptom | Cause | Fix |
|---|---|---|
| Title cut off with "..." in Google | `<title>` > 60 chars | Shorten title |
| Facebook ad showing only first 5 lines | Primary text > 125 chars | Move details below the fold OR trim |
| LinkedIn intro truncated mid-sentence | Intro > 150 chars | Trim or restructure so truncation point is clean |
| Twitter ad with URL pushing it over 280 | URL not accounted | Use a shortener proactively |
| German hero subheadline wrapping to 4 lines | English baseline too long | Plan for 70% headroom |
| Mobile email subject cut after "Get Started Tod..." | Subject too long | ≤ 30 chars for mobile |

---

## Cross-references

- Hero writing (uses these limits): [`hero-formula.md`](hero-formula.md)
- SEO meta tags (uses these limits): [`seo-meta.md`](seo-meta.md)
- Paid ads (uses these limits): [`ad-copy.md`](ad-copy.md)
