# Style presets — when to pick which

6 directions. Pick ONE per batch. Different styles imply different composition rules + different model strengths.

For broader stylistic coverage (when the brand has a clear "vibe" — luxury / tech / underground / outdoor / etc.), the shared 13-style library at [`common/visual-prompt-library/styles/_index.md`](../../../common/visual-prompt-library/styles/_index.md) (v2.14.1+) provides full Typography + Composition signature + Accent text color recipes — those plug directly into the LLM prompt step. Use the local presets below for logo-specific structural choices (wordmark / emblem / minimal / etc.); use the shared library for the stylistic flavor (cyber-noir / art-deco / vaporwave / etc.).

---

## `wordmark`

**For**: brand names that work as pure typography. Tech, SaaS, fashion, editorial.

**Composition**: Letters dominate. No icon (or tiny accent dot). Single weight or 2-weight contrast. Centered or left-aligned.

**Examples in the wild**: Google, IBM, Spotify, Vogue, FedEx (the arrow is hidden in the letterforms — too subtle for image-gen, so this is the wordmark-as-icon edge case).

**Best model**: `ideogram-3-quality` (text leader).

**Avoid**: brand names with >3 words (illegible at small sizes), or names that contain unusual characters (ampersands, slashes, foreign scripts mixed with Latin).

**Common mistake**: requesting "with an icon next to the wordmark" — splits the model's attention. Pick wordmark OR illustrated, not both.

---

## `minimal`

**For**: tech / B2B / professional services that want a quiet, geometric mark + optional brand name below.

**Composition**: Single geometric shape (circle, triangle, square, abstract polygon) + brand name in clean sans-serif below. Lots of whitespace.

**Examples in the wild**: Airbnb (Bélo mark), Mastercard (concentric circles), Apple (silhouette).

**Best model**: `ideogram-3-quality` (clean text), `gpt-image-2` (cleaner geometry when minimal).

**Avoid**: cluttering the mark — minimal means 1-2 shapes max.

**Common mistake**: asking for "modern minimal" tends to produce generic gradient circles. Be specific: "single hexagon outline, 2px stroke, brand name below in geometric sans".

---

## `illustrated`

**For**: hospitality, food, kids' products, artisan goods, mascots.

**Composition**: Pictorial element (animal, object, scene) — flat illustration aesthetic, limited palette, brand name integrated or below.

**Examples in the wild**: Starbucks (mermaid), Pringles (mustachioed man), MailChimp (Freddie the monkey).

**Best model**: `gpt-image-2` (best illustration), `flux-2-pro` (alternative).

**Avoid**: photoreal illustration — looks cheap as a logo. Cue "flat illustration", "vector aesthetic", "2-3 color illustration".

**Common mistake**: too much detail. Logos at small sizes lose detail — keep illustration to 3-5 shapes.

---

## `typographic`

**For**: editorial brands, design studios, fashion, luxury, hand-crafted feel.

**Composition**: Custom lettering — ornamental, hand-lettered, or display-type-driven. Often the only element on the page.

**Examples in the wild**: Coca-Cola (Spencerian script), New York Times (Old English masthead), Yves Saint Laurent (Cassandre's monogram).

**Best model**: `ideogram-3-quality` (best text rendering for custom letterforms).

**Avoid**: generic decorative fonts — be specific about the typography style ("blackletter", "Bodoni-inspired didone", "1970s display", "handwritten brush script").

**Common mistake**: asking for "fancy font logo" — too vague. Reference a typographic era or a specific feel ("art deco geometric letters", "1970s underground concert poster lettering").

---

## `geometric`

**For**: architecture, parametric design, engineering, mathematics, modern brands wanting structure.

**Composition**: Grid-aligned shapes, angular constructions, parametric forms. Often monochrome or 2-color.

**Examples in the wild**: Bauhaus marks, Penguin Books (oval), Renault (diamond), Lufthansa (crane in roundel).

**Best model**: `gpt-image-2` (clean geometry), `ideogram-3-quality` (when text-heavy).

**Avoid**: gradients, soft shadows — they fight the geometric aesthetic.

**Common mistake**: asking for "geometric logo" produces generic hexagon-with-letters output. Be specific: "intersecting triangles forming the letter A", "concentric squares decreasing in size, brand name below".

---

## `emblem`

**For**: heritage brands, breweries, coffee shops, motorcycle/automotive, sports clubs, military / fraternity feel.

**Composition**: Badge / seal / circular composition — typically text-around-edge + central icon + optional founding-year footer. Often boxed into a clear shape (shield, circle, hexagon).

**Examples in the wild**: Harley-Davidson, Stumptown Coffee, Starbucks (which is also an illustrated, but the circular emblem composition dominates), most beer brands.

**Best model**: `gpt-image-2` (best for complex compositions), `ideogram-3-quality` for clean text inside circle.

**Avoid**: too many elements. Emblems already have a lot — icon + circular text + footer. Don't add more.

**Common mistake**: requesting too much text inside the emblem ("BREW HOUSE EST 2024 ARTISAN COFFEE BROOKLYN NY") — becomes illegible. Pick 2 text rings max.

---

## Decision tree

```
Brand name only (≤3 words)
  → wordmark   (90% of SaaS / tech / editorial)

Brand name + icon, professional / corporate
  → minimal

Mascot / character / pictorial brand
  → illustrated

Custom lettering, ornamental, no icon
  → typographic

Angular / structured / engineered feel
  → geometric

Badge / seal / heritage feel
  → emblem
```

When in doubt for a tech / SaaS brand: start with `wordmark`. It's the safest, most timeless, and most likely to render text correctly across variants.
