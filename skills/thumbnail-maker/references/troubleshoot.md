# Troubleshooting — thumbnail-maker

---

## Title doesn't render or is unreadable

**Causes + fixes**:

1. **Wrong model.** Flux / Imagen render text wrong often.
   - Fix: `--model ideogram-3-quality` (no face) or `--model gpt-image-2` (with face).

2. **Title too long.** Past 7 words = high failure rate.
   - Fix: shorten.

3. **Style anchor specifies a script-font** the model can't render at thumbnail scale.
   - Fix: `--style-mod "with bold sans-serif typography"`.

---

## Face placement is wrong

**Symptom**: Asked for `left` placement, face is centered.

**Cause**: AI image models don't perfectly honor placement constraints. They guide, not lock.

**Fix**:

1. Generate `--variants 3` per placement — picks the most-on-spec take.
2. Or pick a different placement: pass only `--placements left` and generate 5 variants of that.

---

## Face doesn't look like the original (identity drift)

**Symptom**: My face in the thumbnail looks similar but not exact.

**Causes + fixes**:

1. Wrong model. `nano-banana-pro` is the identity-preserve champion.
2. Source photo too small / blurry.
3. Style anchor pulls toward non-photographic medium.
   - Fix: pick photoreal styles + nano-banana-pro.

---

## Thumbnail looks too "clickbait-y"

If the output has exaggerated shock expression you didn't ask for:

- AI models trained on YouTube thumbnails sometimes default to "shock face".
- Fix: pass `--style-mod "natural confident expression, no shock, no exaggerated faces"`.

---

## Output doesn't fit YouTube's exact specs

**Cause**: YouTube wants 1280×720 minimum. Our default is 1920×1080 (higher quality, same aspect).

**Fix**:

1. 1920×1080 works fine — YouTube downscales.
2. If you specifically want 1280×720: `--type youtube --aspect 1280x720`.
3. If you want OG / blog 1200×630: `--type blog`.

---

## Text contrasts poorly with face background

**Symptom**: Title text disappears against a dark background or face area.

**Causes + fixes**:

1. **Style anchor's palette doesn't provide enough contrast.**
   - Fix: pick a high-contrast style (`bauhaus-primary`, `swiss-grid-poster`, `neon-cyberpunk`).

2. **Title color matches face area color.**
   - Fix: `--style-mod "with bright yellow or cyan title text"`.

---

## Layout collides — face + text overlap

**Symptom**: Title text sits on top of the face.

**Causes + fixes**:

1. **Placement constraint is soft.** Generate more variants (`--variants 3`).
2. **Long title pushes into face zone.**
   - Fix: shorten title to 3-5 words.

---

## Brand color isn't right

**Symptom**: Asked for muted teal accent; got bright magenta.

**Cause**: Style anchor overrides via `--style-mod` aren't always honored.

**Fix**:

1. Stronger `--style-mod`: "muted teal accent throughout, no purple or magenta".
2. Or change the base style: pick one whose anchor explicitly uses your brand color.
3. Or generate 5 variants and pick the on-brand one.

---

## Cost is higher than expected

<!-- prices: batch=9 -->

3 placements × 3 variants = 9 images. At nano-banana-pro = $1.21.

That's still under default $1.50 budget. If you're seeing confirmations:

- `--cost-only` to preview.
- Lower variants to 1 per placement.
- Use cheaper model (ideogram-3 vs ideogram-3-quality).
