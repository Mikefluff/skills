# Composition zones — quote-card-maker

How the prompt template positions text + minimal visual support across aspects.

---

## `square` (1080×1080)

Default aspect. Twitter / Instagram square / LinkedIn.

```
+-----------------------------+
|                             |
|  [quote text dominates      |
|   60-70% of the frame,      |
|   centered, large weight,   |
|   max 3 lines wrapped]      |
|                             |
|                             |
|  — attribution              |
+-----------------------------+
```

**Type sizing**: quote ~80-120pt depending on length. Attribution ~24-32pt, italic or small caps.

**Visual support**: optional thin horizontal rule between quote + attribution. Optional minimal background texture (subtle paper / linen / noise).

---

## `portrait` (1080×1350)

Instagram portrait — gets more reach than square.

```
+----------------------+
|                      |
|                      |
|                      |
|  [quote dominates    |
|   middle 60%,        |
|   centered or LEFT,  |
|   tall composition]  |
|                      |
|                      |
|                      |
|                      |
|  — attribution       |
|  [context optional]  |
+----------------------+
```

**Type sizing**: quote ~100-140pt. Attribution ~28-36pt.

**Visual support**: optional small visual element bottom-center (single geometric shape, single typographic ornament, single thin illustration).

---

## `story` (1080×1920)

Instagram Stories / Reels cover.

```
+--------------------+
|                    |
|                    |
|                    |
|  [quote in upper   |
|   middle, large    |
|   weight, 60-70%   |
|   of total frame   |
|   height]          |
|                    |
|                    |
|                    |
|                    |
|                    |
|                    |
|  — attribution     |
|                    |
|                    |
+--------------------+
```

**Type sizing**: quote ~120-180pt. Attribution ~32-44pt.

**Visual support**: more whitespace, attribution drops to bottom third. Optional brand mark in top-right corner (small).

---

## `landscape` (1200×630)

Twitter header / OG image / blog header.

```
+----------------------------------+
|                                  |
|   [quote dominates LEFT 60%,     |
|    multi-line, large weight]     |
|                                  |
|                                  |
|   — attribution                  |
|                                  |
+----------------------------------+
```

**Type sizing**: quote ~60-90pt. Attribution ~20-28pt.

**Visual support**: optional minimal visual on right 30-40% (texture / single illustration / abstract shape).

---

## Visual support rules

All aspects share these rules:

1. **No competing visual subject.** No people, no scenes, no detailed photography. Visual support is texture, single shapes, single ornaments, or pure background color.
2. **Palette obeys style preset.** Minimal-serif → cream + ink + accent. Monochrome-bold → black + white only. Gradient-mesh → bright but harmonized.
3. **Type hierarchy is strict.** Quote dominates. Attribution recedes. Context (if present) recedes further.
4. **Alignment is consistent.** Centered, or left-aligned, or right-aligned — pick one and hold it across all aspects in a batch.
5. **Optical centering, not mathematical.** Type sits slightly above the geometric center for visual balance.

---

## Per-style hints

**minimal-serif**: cream background (#F5F0E8), ink type (#1A1A1A), italic attribution. No accent color unless requested.

**swiss-grid-poster**: white BG, black type, single accent color (red / orange) on one element. Strict grid alignment.

**monochrome-bold**: pure black or white BG, opposite type. Quote can take 90% if punchy. Attribution near-invisible.

**editorial-magazine**: cream / ivory BG, mix of serif + sans (display serif quote, sans attribution). Dropcap initial on the quote's first letter (when natural).

**gradient-mesh-modern**: vibrant gradient BG (blue→violet, peach→pink, teal→lime). Type in white or near-white. Attribution lighter weight.

**russian-constructivist**: cream or red BG, heavy Cyrillic display type, angular ornaments allowed (single diagonal line, geometric shapes from constructivist vocabulary).
