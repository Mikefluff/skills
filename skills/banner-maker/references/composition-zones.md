# Composition zones — banner-maker

How the prompt template positions headline + CTA + brand + visual across presets.

---

## OG / LinkedIn-ad / Facebook-ad (1200×630-ish, ~1.91:1)

Most flexible — balanced composition.

```
+--------------------------------+
|  [brand mark, small, top-left] |
|                                |
|  [HEADLINE — dominant, 3-5     |
|   lines, large weight, LEFT or |
|   CENTER aligned]              |
|                                |
|  [subhead, optional, 1 line]   |
|                                |
|        [visual element,        |
|         optional, RIGHT half]  |
|                                |
|  [CTA button, bottom-right]    |
+--------------------------------+
```

- Headline ~50-60% of frame
- Visual: optional, 30-40% on right (or omitted for text-only banners)
- CTA: distinct from headline — usually a colored "button" or strongly underscored
- Brand mark: small, corner

---

## Twitter-card (1500×500, 3:1)

Very wide. Avatar mask on left (mobile) reduces effective left 30%.

```
+----------------------------------------------------+
|           [HEADLINE — large, CENTER or RIGHT, 1-2  |
|            lines, fits horizontal extreme]         |
|           [subhead optional, 1 line]               |
|                                                    |
|           [CTA — bottom-right]                     |
|  [avatar  [brand mark, optional]                   |
|   mask    |
+----------------------------------------------------+
```

- Avoid putting key content in left 30% (avatar overlap on mobile)
- Headline 1-2 lines max
- Brand mark bottom-left (out of avatar mask)

---

## Leaderboard (1456×180, ~8:1)

Extreme horizontal. Headline must fit one line.

```
+------------------------------------------------------+
| [brand]   [HEADLINE — 1 line, large, CENTER]  [CTA]  |
+------------------------------------------------------+
```

- Brand mark LEFT, single icon size
- Headline CENTER, ONE LINE, ≤5 words
- CTA RIGHT, button-style
- No subhead (no room)
- No visual element (no room)

---

## Mobile-banner (640×200, ~3.2:1)

Slightly less extreme than leaderboard but still very horizontal.

```
+------------------------------------+
|  [brand]  [HEADLINE — 1 line]      |
|                          [CTA]     |
+------------------------------------+
```

- Headline 1 line, ≤5 words
- CTA on its own line below headline (better than crammed inline)
- Brand mark top-left

---

## Medium-rectangle (600×500, ~6:5)

The "default Google Display" size. Near-square, most flexible after OG.

```
+----------------------------+
|  [brand, top-left]         |
|                            |
|  [HEADLINE — dominant,     |
|   2-3 lines]               |
|                            |
|     [visual, middle,       |
|      small/medium]         |
|                            |
|  [CTA, bottom, button]     |
+----------------------------+
```

- Headline 50-60%
- Visual: small middle element
- CTA: distinct button at bottom
- Brand: corner

---

## Wide-skyscraper (320×1200, ~1:3.75)

Extreme vertical. Stacked composition.

```
+----------+
| [brand]  |
|          |
| [HEAD-   |
|  LINE]   |
|          |
|          |
| [visual] |
|          |
|          |
| [sub-    |
|  head]   |
|          |
| [CTA]    |
+----------+
```

- Headline: 4-7 stacked lines (it's vertical — text wraps a lot)
- Visual: middle, small
- CTA: bottom

---

## Per-preset prompt template hints

All presets share these conventions:

1. **CTA is visually distinct.** Usually a colored "button" rectangle around the CTA text. The model auto-applies the dominant accent color from the palette.

2. **Brand mark is small.** Corner placement. Usually top-left (Western reading order). Cued as "brand wordmark" or "logo".

3. **Headline is BOLD.** Heaviest weight in the composition. Often 2-3× the size of supporting text.

4. **Subhead recedes.** Smaller, lighter weight, often italic or different color.

5. **Palette obeys style preset.** swiss-grid-poster = white + black + single accent. gradient-mesh-modern = vibrant gradient + white text. brutalist-grid = pure B&W high contrast.

6. **Negative space matters.** Banners aren't busy — they have a focal point + breathing room. Cluttered = looks like spam.

7. **Per-preset alignment**: OG / LinkedIn-ad / Facebook-ad center-aligned. Leaderboard / mobile-banner center-aligned. Skyscraper top-aligned (read top-to-bottom). Medium-rectangle left-aligned (most-common ad-layout convention).
