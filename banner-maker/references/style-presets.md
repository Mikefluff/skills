# Style presets — banner-maker

Picks from the carousel style library biased toward text-strong + ad-friendly anchors. 5 recommended directions.

---

## `swiss-grid-poster` (default for B2B)

**For**: SaaS, B2B, professional services, fintech.

**Composition**: white BG, black geometric sans-serif headline (Helvetica / Inter), single accent color on CTA (often red / orange / electric blue). Strict grid alignment. Clean, professional, "trustworthy".

**Examples in the wild**: most modern SaaS landing-page hero banners.

---

## `gradient-mesh-modern` (default for consumer tech)

**For**: consumer apps, lifestyle brands, gaming, energy / optimism.

**Composition**: vibrant gradient BG (cyan→magenta, teal→lime, peach→pink), white headline, accent CTA in contrasting saturated color. Modern, attention-grabbing.

**Examples in the wild**: Stripe / Linear / Vercel marketing banners (these brands lean modern gradient).

---

## `brutalist-grid`

**For**: design-led brands, manifestos, contrarian tech positioning.

**Composition**: stark B&W or 2-color, oversized blocky headline, raw / unpolished aesthetic, often unconventional alignment.

**Examples in the wild**: Notion's punchier campaigns, Figma's design-system docs cover banners.

---

## `editorial-magazine`

**For**: content marketing, longform, premium publications, editorial brands.

**Composition**: cream / ivory BG, mix of display serif + sans, dropcap on headline first letter, magazine-spread feel.

**Examples in the wild**: New York Times Display ads, Substack longform OG images.

---

## `neon-cyberpunk`

**For**: gaming, web3, crypto, futurism, edgy tech.

**Composition**: black BG, neon (cyan / magenta / yellow) typography with glow, geometric grid, futuristic edge.

**Use sparingly** — feels dated in 2026 unless the brand is genuinely cyberpunk-aligned.

---

## Decision tree

```
B2B SaaS / fintech / professional
  → swiss-grid-poster

Consumer app / lifestyle / modern brand
  → gradient-mesh-modern

Design-led / manifesto / contrarian
  → brutalist-grid

Longform / editorial / premium
  → editorial-magazine

Gaming / web3 / cyberpunk
  → neon-cyberpunk
```

When in doubt: `--style auto` picks based on the brand voice cued in headline + CTA. "Start free trial" + "Acme Cloud" → swiss-grid-poster. "Launch tomorrow" + dynamic brand → gradient-mesh-modern.

---

## What carousel-library styles to AVOID for banners

- **kinfolk-minimal** — too quiet for ads, gets lost
- **photo-editorial-bw** — beautiful but lacks accent color for CTA emphasis
- **risograph-pastel** — too soft for high-conversion ad creatives
- **art-deco-gold** — feels luxury / event, not "click me"

If the user explicitly wants these for a non-ad-feel banner (e.g., a tasteful OG image for a longform essay), respect the override.
