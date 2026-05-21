# Aspect presets — banner-maker

All output PNGs are at 2× retina resolution (real-world ad creatives ship at @2x). Divide by 2 if uploading to platforms that expect 1× dimensions.

---

## Social previews

### `og` (default)

- **Dimensions**: 1200×630 px
- **Aspect**: ~1.91:1
- **Use**: Open Graph image for blog posts, link previews on Twitter / Slack / Discord / Facebook
- **Spec**: most flexible; Facebook recommends ≥600×315 px
- **Text-safe zone**: center 1140×570 (avoid 30px margins)

### `twitter-card`

- **Dimensions**: 1500×500 px
- **Aspect**: 3:1
- **Use**: Twitter profile header
- **Spec**: max 5 MB
- **Text-safe zone**: avoid edges — left 30% may be partially hidden by avatar on mobile

### `facebook-ad`

- **Dimensions**: 1200×628 px
- **Aspect**: ~1.91:1 (similar to OG)
- **Use**: Facebook News Feed ad creative
- **Spec**: max 30 MB; text-on-image policy — keep text under 20% of image area

### `linkedin-ad`

- **Dimensions**: 1200×627 px
- **Aspect**: ~1.91:1
- **Use**: LinkedIn Sponsored Content single-image ad
- **Spec**: max 5 MB; PNG / JPG
- **Best practice**: subject 60-70% of frame, CTA bottom-right

---

## Google Display network (IAB standard sizes, 2×)

### `leaderboard`

- **Dimensions**: 1456×180 px (728×90 @2x)
- **Aspect**: ~8:1 (extreme horizontal)
- **Use**: top-of-page banner on Google Display
- **Spec**: max 150 KB file size at 1× resolution
- **Caveat**: headline must be very short (3-5 words) to fit one line

### `medium-rectangle`

- **Dimensions**: 600×500 px (300×250 @2x)
- **Aspect**: 6:5 (near-square)
- **Use**: most-common Google Display unit, sidebar / inline content
- **Spec**: max 150 KB at 1×
- **Highest-CTR IAB size**; default for any Display campaign

### `mobile-banner`

- **Dimensions**: 640×200 px (320×100 @2x)
- **Aspect**: ~3.2:1 (extreme horizontal, mobile)
- **Use**: bottom-of-screen mobile in-app ads
- **Spec**: max 150 KB at 1×

### `wide-skyscraper`

- **Dimensions**: 320×1200 px (160×600 @2x)
- **Aspect**: ~1:3.75 (extreme vertical)
- **Use**: sidebar on desktop publisher sites
- **Spec**: max 150 KB at 1×
- **Composition**: stacked vertical — headline TOP, visual middle, CTA BOTTOM

---

## Decision tree

```
Blog post / link preview / "shareable image"
  → og  (1200×630)

LinkedIn ad campaign
  → linkedin-ad (1200×627) — often used alongside og

Facebook News Feed ad
  → facebook-ad (1200×628)

Twitter profile header
  → twitter-card (1500×500)

Google Display campaign (default 2 sizes)
  → leaderboard + medium-rectangle

Mobile-first display campaign
  → mobile-banner + medium-rectangle

Desktop publisher sidebar
  → wide-skyscraper + medium-rectangle
```

Default `--presets og,linkedin-ad` covers the most-common shareable-link use case.
