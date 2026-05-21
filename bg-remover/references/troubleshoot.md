# Troubleshooting — bg-remover

---

## Hair edges look chunky / fine wisps lost

**Cause**: Default model (851-labs) is general-purpose. Portrait-specific models do better on hair.

**Fix**: `--replicate-model pollinations/modnet` (MODNet, portrait-tuned).

---

## Part of the subject got removed

**Symptom**: Hand or hair edge missing in the output.

**Cause**: Model confused part of the subject for background (e.g., subject's hand near a background object of similar color).

**Fix**:

1. Try a different model: `--replicate-model lucataco/remove-bg`.
2. Manual touch-up in an image editor — paint back the missing region.
3. Use a cleaner source photo with better subject/background separation.

---

## Background still partially visible

**Symptom**: Faint outline / halo around subject.

**Causes + fixes**:

1. **Background and subject share color.** Hard problem; models leave color bleed at edges.
   - Fix: use a source with better contrast.

2. **Model didn't crop tightly enough.**
   - Fix: try `--replicate-model pollinations/modnet` for portraits or `cjwbw/rembg` for general.

3. **Edge alpha is too soft.**
   - Fix: open in image editor + apply "select transparent pixels → contract → fill with transparent" to harden edge.

---

## Output looks the same as input

**Symptom**: Background wasn't removed.

**Causes + fixes**:

1. **Provider call failed silently.** Check stderr for the error.

2. **Wrong file** — input wasn't what you thought it was.
   - Fix: verify the input file is the one with a background to remove.

3. **Model returned the original image** (rare bug).
   - Fix: try a different `--replicate-model`.

---

## Replicate API error

**Symptom**: `[replicate 401] unauthorized` or similar.

**Causes + fixes**:

1. **REPLICATE_API_TOKEN not set or wrong.**
   - Fix: `/skills-keys verify REPLICATE_API_TOKEN` to confirm. Update via `/skills-keys update REPLICATE_API_TOKEN r8_...`.

2. **Account out of credits.**
   - Fix: top up at replicate.com.

3. **Model slug doesn't exist.**
   - Fix: pass the correct `<username>/<model-name>` slug. Browse replicate.com/explore.

---

## Output PNG won't open / says corrupted

**Causes**:

1. **API call returned partial data.**
   - Fix: re-run.

2. **Disk full mid-write.**
   - Fix: free disk space + re-run.

---

## Cost is higher than expected

Replicate bg-removers are very cheap (~$0.001-0.005 per image). If your bill is high:

- Check your Replicate dashboard for actual costs.
- Make sure you're using a bg-remover, not a more expensive image-gen model.
- Batch processing many images adds up — track via `--cost-only`.

---

## Want to remove a SPECIFIC object (not background)

This skill removes the BACKGROUND — everything that's not the main subject. For selective object removal:

- Use Photoshop / Affinity / GIMP "content-aware fill" feature.
- Or AI alternatives: Replicate's `lucataco/clipdrop-cleanup` or similar inpainting models.
- Or `image-prompt --execute --model flux-kontext --image-url <photo> --prompt "remove the [specific object] from this image"`.

---

## Output has a colored fringe (chromatic aberration on edges)

**Symptom**: Edge of subject has unwanted color bleed (often dark or saturated).

**Cause**: Model picked up edge artifacts from JPEG compression in the source.

**Fix**: use a higher-quality source image (PNG / WebP / minimally compressed JPEG).

---

## Want a SOFT vignette around the subject (not hard cutout)

The skill produces hard cutouts. For soft vignettes / feathered edges:

1. Get the hard cutout from this skill.
2. In an image editor: select the alpha mask + apply Gaussian blur to soften.

Or use `image-prompt --execute --model flux-kontext --image-url <photo> --prompt "soft vignette focus on subject, dreamy background blur"` for AI-driven soft effect (different from bg removal).

---

## Local (no-API) alternative

If you don't want Replicate API costs:

```bash
pip install rembg
rembg i input.jpg output.png
```

This runs locally (downloads ~100MB model on first use). Free, offline, no API key.

The skill doesn't wrap local rembg in v1 — but use it independently.

---

## Subject is transparent / translucent (water, glass, smoke)

These are HARD for any bg-remover. Result usually has artifacts:

- Smoke / steam: partially removed; subject appears chunky
- Glass / water: model can't tell what's "background through the glass" vs background
- Hair lit from behind: similar issue

For these cases:

- Try multiple models and pick the best.
- Or accept manual touch-up in an image editor.
- For glass specifically: shoot the source against a neutral background, then composite manually.
