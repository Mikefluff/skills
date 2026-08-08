# Troubleshooting — quote-card-maker

---

## Quote is garbled / misspelled

**Symptom**: variants show typos, missing letters, or reorganized words.

**Cause**: image-gen models hallucinate near-correct text, especially for long quotes.

**Fix**:

1. Confirm `--model ideogram-3-quality` (text leader; default).
2. Shorten the quote if possible — under 15 words renders more reliably.
3. Re-roll: more variants per aspect (`--variants 3`).
4. Manual fix: pick the closest variant, retype the quote correctly in Figma / Affinity Designer / Pixelmator.

---

## Attribution dominates / too prominent

**Symptom**: "— Søren Kierkegaard" is the same weight as the quote — feels backwards.

**Cause**: model interpreted attribution as another headline.

**Fix**:

1. Cue the hierarchy explicitly: `--style-mod "attribution in 30% smaller size, lighter weight, italic"`.
2. Switch style preset — `minimal-serif` and `editorial-magazine` are best at hierarchy.
3. Move attribution: `--style-mod "attribution in bottom-right corner, single line, small caps"`.

---

## Text wraps in weird places

**Symptom**: quote breaks mid-word, or wraps awkwardly across 5 short lines.

**Cause**: model doesn't follow text-wrap hints precisely.

**Fix**:

1. Provide explicit break hints: `--quote "Anxiety is the dizziness / of freedom."` (slash = line break hint).
2. Use `--style-mod "quote wrapped to maximum 3 lines, balanced line lengths"`.
3. Re-roll variants.

---

## Visual element distracts from quote

**Symptom**: background texture / illustrated element competes with text.

**Cause**: style preset bias too strong, or visual support over-cued.

**Fix**:

1. Strip visual support: `--style-mod "no decorative elements, pure typography, single color background"`.
2. Switch to a minimal style: `--style monochrome-bold` or `--style minimal-serif`.

---

## Style doesn't feel right for the quote

**Symptom**: vibrant gradient on a philosophy quote, or stark monochrome on a marketing quote.

**Cause**: `--style auto` made a bad call.

**Fix**: pick explicitly:

```
Literary / philosophy:    --style minimal-serif
Marketing / SaaS:         --style swiss-grid-poster  or  --style gradient-mesh-modern
Contrarian / manifesto:   --style monochrome-bold
Long literary spread:     --style editorial-magazine
Russian / constructivist: --style russian-constructivist  (with --lang ru)
```

---

## Cyrillic text renders badly

**Symptom**: Russian quote shows Latin-like glyphs or mangled Cyrillic.

**Cause**: model wasn't strongly cued for Cyrillic.

**Fix**:

1. Pass `--lang ru` (forces Cyrillic typography hint).
2. Pick a style that supports Cyrillic well: `russian-constructivist`, `monochrome-bold`, `minimal-serif`.
3. Confirm `--model ideogram-3-quality` — best Cyrillic of the text-strong models.

---

## All aspects look identical

**Symptom**: square / portrait / story all look the same.

**Cause**: the aspect change wasn't enforced in composition.

**Fix**:

1. Verify the plan has different sizes per item (check `prompts.md`).
2. Manually override: `--aspects square,portrait,story` — explicit list ensures different composition zones per aspect.

---

## Quote feels too sparse / boring

**Symptom**: lots of whitespace, quote looks lost.

**Cause**: type too small for the aspect.

**Fix**:

1. Cue larger type: `--style-mod "quote takes 70%+ of frame, maximum legibility, fills the composition"`.
2. Switch to `--style monochrome-bold` — defaults to dominant typography.

---

## Want transparent BG / overlay-ready

This skill produces solid-background cards by default. For transparent overlay use:

1. Chain with `bg-remover --image ./generated/quote/<slug>/square.png` — note: bg-remover treats the visual support as background; you may lose decorative elements.
2. OR: cue `--style-mod "transparent background, only text and attribution visible"`. Some models honor this; some don't.
3. OR: manual cleanup in Figma / Affinity Designer.

---

## Want longer quotes

Use `carousel-builder` instead. Quote cards are for ≤20 words. Long quotes:

```
carousel-builder
  --topic "philosophy of dread"
  --content "split this 60-word Kierkegaard quote across 4 slides: setup, development, climax, attribution"
  --slides 4
  --style minimal-serif
```

---

## Want a series of quotes from same author

Run quote-card-maker in a loop:

```bash
for q in "Anxiety is the dizziness of freedom." "Life can only be understood backwards." "Hope is the passion for the possible."; do
  quote-card-maker --quote "$q" --attribution "— Søren Kierkegaard" --style minimal-serif --execute --yes
done
```

Or, for a unified series, use carousel-builder with multiple slides — each slide one quote.

---

## Cost is higher than expected

3 aspects × ideogram-3-quality ($0.09) = $0.27 per quote. If you're running batches:

- Single variant per aspect: ~$0.27 per quote
- 3 variants per aspect across 3 aspects: ~$0.81 per quote

Track via `--cost-only` before committing.

---

## Want to test before committing

Use `--prompts-only` to see assembled prompts. Use `--cost-only` to see estimated total before generation. Use `--variants 1 --aspects square` for cheapest preview ($0.08).
