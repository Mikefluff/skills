# Troubleshooting — logo-maker

---

## Text is garbled / misspelled

**Symptom**: variants show "LUNARVALT", "LunarVau1t", or other character corruption.

**Cause**: image-gen models often hallucinate near-correct text. Worst with long brand names + cursive styles.

**Fix**:

1. Switch to `--model ideogram-3-quality` (default; if you overrode it, switch back).
2. Shorten brand name in the prompt — try abbreviation (`LV` instead of `Lunar Vault`).
3. Re-roll: more variants = better odds (`--variants 8`).
4. Manual fix in vector tool: open the best variant, replace the text with proper typography in Illustrator / Affinity Designer.

---

## Logo looks generic / templates-y

**Symptom**: output looks like a free Canva template — generic gradient circle, generic sans-serif.

**Cause**: prompt was too vague.

**Fix**: be more specific:

- Reference an era: "art deco", "1970s underground concert poster", "Bauhaus 1923"
- Reference a feel: "engineered precision", "warm hand-lettered", "brutalist concrete"
- Reference a palette directly: "two tones — deep forest green and bone white"
- Reference a brand archetype: "for a coffee roaster in Portland, OR — heritage feel"

---

## Icon and text don't feel like one logo

**Symptom**: icon looks separate from the wordmark — like 2 logos stuck together.

**Cause**: prompt asked for both icon AND text, but didn't bind them.

**Fix**:

1. Pick ONE — wordmark OR illustrated. Don't ask for both in v1.
2. If both are needed: generate the icon first, then add typography in a vector tool.
3. OR cue the binding: "single logo composition with mark + wordmark integrated as one unit, vertical lockup".

---

## Background isn't transparent

**Symptom**: PNG has white background instead of transparent.

**Cause**: image-gen models output RGB on solid backgrounds; transparency is a downstream step.

**Fix**: chain with `bg-remover`:

```
logo-maker --brand "Lunar Vault" --execute
bg-remover --image ./generated/logo/lunar-vault/logo-v1.png --output ./generated/logo/lunar-vault/logo-v1-transparent.png --execute
```

---

## Palette is ignored

**Symptom**: requested "two tones, deep teal + warm cream"; output is multicolor.

**Cause**: vague palette hint. Models interpret "warm cream" liberally.

**Fix**: use hex codes:

```
--palette "exact two-tone palette: #1A4D5C deep teal AND #F4E9D8 warm cream — no other colors"
```

Or switch to `--model flux-2-pro` which respects exact palette constraints better.

---

## All variants look the same

**Symptom**: 4 variants — all nearly identical.

**Cause**: provider used the same seed (rare) or prompt was very narrow.

**Fix**:

1. Broaden the brief — let the model interpret.
2. Vary `--style-mod` per variant via manual runs (call the skill multiple times with different style modifiers).
3. Switch to `--model gpt-image-2` for more variance per call.

---

## I want a vector / SVG, not PNG

This skill outputs raster PNG only. To get SVG:

1. Pick the best variant.
2. Open in Illustrator / Affinity Designer / Vectornator.
3. Use auto-trace (Image Trace in Illustrator, Trace Bitmap in Inkscape).
4. Manually clean up the vector paths.

OR: use a service like `vectorizer.ai` to convert raster → vector.

The skill itself doesn't ship a vectorizer — would add a heavy dependency for a step that's better done with proper vector tools.

---

## Logo doesn't work at small sizes

**Symptom**: looks great at 1024px, illegible at favicon size (32px).

**Cause**: too much detail.

**Fix**:

1. Re-run with `--style minimal` (forces fewer elements).
2. Cue "designed to read at 32x32 pixels" in `--style-mod`.
3. Manually simplify in vector tool — remove fine details.

Logos must read at 16×16 favicon size. If yours doesn't, you have too much detail.

---

## Model didn't honor the style preset

**Symptom**: asked for `--style emblem`; got a wordmark.

**Cause**: prompt-style binding can fail when palette + style-mod conflicts.

**Fix**: explicitly mention the format in `--style-mod`:

```
--style emblem --style-mod "circular badge composition with brand name curved around the top edge, founded year at the bottom"
```

---

## I want to test before committing to API cost

Use `--prompts-only` to see the assembled prompts without spending. Run with `--cost-only` to see estimated total before generation.

---

## Trademark conflict concern

This skill cannot verify uniqueness. Before commercial use:

1. Run a USPTO trademark search (TESS — tmsearch.uspto.gov).
2. For non-US markets: WIPO Global Brand Database.
3. Reverse-image-search the variant on TinEye / Google Images.

If a similar mark exists in your category, generate new variants.
