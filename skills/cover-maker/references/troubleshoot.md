# Troubleshooting — cover-maker

When the cover doesn't come out right.

---

## Title text is misspelled / cut off

**Symptom**: "Lunar Vault" comes out as "Luner Vaut" or letters render as garbage.

**Causes + fixes**:

1. **Wrong model.** Nano Banana 2 / Flux render text wrong 30-60% of the time.
   - Fix: `--model ideogram-3-quality` (default) or `--model gpt-image-2`.

2. **Title too long.** >6 words = high failure rate.
   - Fix: shorten the title; move secondary info to `--subtitle`.

3. **Title contains tricky characters.** `™`, `&`, `—` sometimes break.
   - Fix: simplify or accept; check output and re-run failed variants.

4. **Style anchor specifies a script-font that the model can't render cleanly at small subtitle size.**
   - Fix: simplify typography via `--style-mod "with cleaner sans-serif typography"`.

---

## Author / artist photo doesn't get embedded

**Symptom**: Pass `--photo ./me.jpg`, but the output cover has a generic person, not me.

**Causes + fixes**:

1. **Model isn't ref-capable**. ideogram-3-quality has limited 1-style-ref; doesn't preserve identity well.
   - Fix: use `--model nano-banana-pro` for identity preserve, OR use `--model gpt-image-2` for multi-ref + identity balance.

2. **Photo wasn't passed through**. Check manifest.json `kwargs.image_url`.

3. **Photo path / URL doesn't work**. Check file exists, is readable, URL is publicly fetchable.

4. **Photo is too low-res**. Face becomes blurry when scaled up.
   - Fix: use ≥800px on short edge.

5. **Style anchor overpowers photo**. Heavy illustration style + identifiable face = identity loss.
   - Fix: use photoreal-friendly styles for author/artist covers.

---

## Wrong aspect ratio output

**Symptom**: Asked for `book` (2:3 portrait), got 1024×1024.

**Causes + fixes**:

1. **Model doesn't honor exact aspects**. Some providers round to nearest standard.
   - Fix: use models known to honor non-square: `ideogram-3-quality`, `gpt-image-2`, `nano-banana-pro`, `flux-2-pro`.

2. **--aspect parameter override didn't propagate**. Check the manifest.

---

## Layout looks crowded / multiple text elements compete

**Symptom**: Title + subtitle + creator + cover-line all overlapping or fighting for visual space.

**Causes + fixes**:

1. **Too many text elements**. Past 4, the AI image model crowds.
   - Fix: drop `--subtitle` OR drop `--creator` for the variant.

2. **Long title**. 7-word title leaves no room for subtitle / creator.
   - Fix: shorten title.

3. **Aspect too tight for content**. Squeezing a 4-text-element layout into `podcast` (1:1) is harder than `book` (2:3).
   - Fix: drop to a portrait aspect for content-dense covers.

---

## Style drifts across variants

**Symptom**: Variant 1 is editorial calm, variant 2 is brutalist.

**Causes + fixes**:

1. **Style anchor too vague** (`--style auto` with non-specific topic).
   - Fix: explicit `--style <id>`.

2. **Variants are inherently stochastic.** That's the feature.
   - Fix: pick the best variant or generate more.

---

## Magazine cover lines don't render

**Symptom**: Pass `--subtitle "Cover line 1, Cover line 2"` for a magazine, only the first renders.

**Cause**: The skill takes `--subtitle` as a SINGLE text. Magazines often have 3-7 separate cover lines.

**Fix**: v1 limitation. For multi-cover-line magazines:

- Use `--subtitle "<one main cover-line>"`
- Add the other cover lines as a `--style-mod "with additional cover-line teasers reading 'Inside: X', 'New: Y', '15 ways to Z' arranged around the hero"`

Future v2 might support `--cover-lines <list>` for magazines specifically.

---

## Photo subject doesn't look like the original

**Symptom**: The author / artist face in the output is close but not exactly the same.

**Causes + fixes**:

1. **Wrong model.** Identity preserve is Nano Banana Pro's strength.
   - Fix: `--model nano-banana-pro`.

2. **Conflict between style and photo.** Heavily illustrated style + photoreal face = compromise.
   - Fix: pick photoreal styles (`kinfolk-minimal`, `photo-editorial-bw`).

---

## Cover doesn't feel "professional enough"

Subjective, but common patterns to fix:

1. **Style mismatch with medium.**
   - Memphis-90s style on a literary fiction book = wrong feel.
   - Fix: pick a style appropriate to the medium (see `cover-types.md` per-medium recommendations).

2. **Random palette.** Auto-pick may produce something neutral.
   - Fix: explicit style + `--style-mod "with [brand color] accents"`.

3. **Generic-feeling visual**.
   - Fix: pass `--photo` with a specific reference image — even a mood-board screenshot helps.

4. **Wrong model.** Flux-schnell looks rough at cover scale.
   - Fix: bump to a higher-fidelity model.

---

## Output not print-ready

**Symptom**: 2400×3600 pixel cover looks blurry when printed.

**Cause**: Default 150 DPI; print needs 300 DPI.

**Fix**:

1. Generate at the medium's default (RGB 150 DPI).
2. Open in Photoshop / Affinity.
3. Upscale to 300 DPI (`Image → Resize → set DPI to 300`, keep print dimensions).
4. Sharpen lightly (unsharp mask).
5. Convert RGB → CMYK.
6. Export PDF for print.

---

## "Output looks AI-generated"

Yes — it is. The cover models are trained on existing book / album / podcast covers; output has that texture.

To reduce the AI-ness:

1. **Provide a specific photo** — `--photo` references your own asset, anchoring the output.
2. **Use a strong specific style** — vague auto-pick produces vague output.
3. **Layer manual design over the AI output** — open in Affinity / Photoshop, overlay your own typography, refine.
4. **Iterate via `--variants 5-10`** — pick the most "designed" feeling take.
5. **Use `--model flux-kontext` to refine an existing draft** rather than generating from scratch.

The skill is for STARTING POINTS or quick comps. For final commercial use, expect to refine manually.

---

## I want spine / back-cover too

The skill produces front-cover only.

**For full book wrap** (spine + back cover):

1. Generate front cover here.
2. Open in Affinity Publisher / Adobe InDesign.
3. Create back cover + spine manually (designer's craft, not the skill's job).

A future `book-wrap-maker` is on the roadmap but lower priority.

---

## Output text says wrong language

**Symptom**: Cover for a Russian book has English-looking title rendering.

**Causes + fixes**:

1. **--lang not set or mis-detected**.
   - Fix: pass `--lang ru` explicitly.

2. **Wrong model for Cyrillic**. Some models render Cyrillic as approximated Latin.
   - Fix: `--model gpt-image-2` (best non-Latin text rendering).

3. **Mixed language in title** (e.g., "Russian Soul: Записки" — Latin + Cyrillic in one title).
   - Fix: pick one language; run separately for bilingual editions.
