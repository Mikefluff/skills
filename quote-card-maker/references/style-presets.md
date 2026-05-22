# Style presets — quote-card-maker

Local skill-specific presets biased toward text-dominant compositions. For broader coverage, the shared 13-style library at [`common/visual-prompt-library/styles/_index.md`](../../common/visual-prompt-library/styles/_index.md) (v2.14.1+) provides Typography genre + Composition signature + Accent text color for each named style — the LLM step pulls those fields into prompts automatically. Use the local presets below for quote-card-specific shortcuts; for richer style variety, pick from the shared library by name (`--style SCIENTIFIC` / `--style ART-DECO` / etc.). 6 recommended directions below.

---

## `minimal-serif`

**For**: literary, philosophical, contemplative quotes. Editorial / book-cover feel.

**Composition**: Quote in classical serif (Bodoni / Garamond / Baskerville feel) centered on cream or off-white background. Attribution in small italic or small caps below. Optional thin rule above attribution.

**Best for**: Kierkegaard, Tolstoy, Dostoevsky, contemporary essays.

**Library anchor**: `minimal-serif-magazine` (when present) or `editorial-magazine`.

---

## `swiss-grid-poster`

**For**: marketing aphorisms, contemporary brand quotes, design-thinking sayings.

**Composition**: Quote in heavy geometric sans-serif (Helvetica / Akzidenz / Inter feel) aligned to a 4-column grid. Attribution as a separate block bottom-left or bottom-right. Strong negative space.

**Best for**: business quotes, design quotes, marketing aphorisms.

**Library anchor**: `swiss-grid-poster`.

---

## `monochrome-bold`

**For**: punchy contrarian quotes, manifestos, "wake up and smell the coffee" energy.

**Composition**: Massive sans-serif typography in black on white or white on black. Quote dominates 80%+ of frame. Attribution barely visible — small, all-caps, single line.

**Best for**: Marcus Aurelius, Tyler Durden, Naval Ravikant, punchy startup wisdom.

**Library anchor**: `brutalist-grid` or `editorial-bw`.

---

## `editorial-magazine`

**For**: long-form literary quotes that benefit from a "spread" feel.

**Composition**: Magazine-spread aesthetic — display serif headline-quote at top, attribution in dropcap-style at bottom-right, single column of body text in the middle (if quote is longer).

**Best for**: Joan Didion, Susan Sontag, Tom Wolfe, New Yorker quotes.

**Library anchor**: `editorial-magazine`.

---

## `gradient-mesh-modern`

**For**: tech / SaaS / contemporary marketing — vibrant, optimistic feel.

**Composition**: Quote in modern geometric sans (Inter / Söhne / Manrope) on a gradient mesh background. Attribution below in lighter weight.

**Best for**: tech founder quotes, motivational SaaS pitches, energetic content.

**Library anchor**: `gradient-mesh-modern`.

---

## `russian-constructivist`

**For**: Russian literature quotes, political quotes, manifesto energy.

**Composition**: Heavy geometric Cyrillic display type, two-tone palette (often red + black or red + cream), angular typography, may include constructivist geometric shapes.

**Best for**: Mayakovsky, Lenin, contemporary Russian aphorisms.

**Library anchor**: `russian-constructivist` or `brutalist-grid` with `--lang ru`.

---

## Decision tree

```
Quote is literary / philosophical / contemplative
  → minimal-serif

Quote is contemporary marketing / brand / business
  → swiss-grid-poster

Quote is punchy / contrarian / manifesto-ish
  → monochrome-bold

Quote is long (15-20 words) and benefits from "spread" feel
  → editorial-magazine

Quote is tech / SaaS / optimistic energy
  → gradient-mesh-modern

Quote is in Russian and benefits from heritage typography
  → russian-constructivist
```

When in doubt: `--style auto` picks based on text length + language + content vibe (the skill assembles a brief and consults `references/composition-zones.md` to pick).
