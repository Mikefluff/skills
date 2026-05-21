# Troubleshooting — style-transfer

---

## Style is too subtle (looks almost like the source)

**Symptom**: requested `--style watercolor` but output looks like the original photo with minor color shift.

**Cause**: provider preserved source too aggressively, or prompt cue wasn't strong enough.

**Fix**:

1. Switch to `flux-kontext` (more aggressive stylization than nano-banana-pro).
2. Strengthen the preset: `--prompt-mod "very strong watercolor effect, dominant brush stroke visibility, paper texture obvious"`.
3. Re-run with different `--style` or use `--style custom` with explicit description.

---

## Style is too aggressive (subject unrecognizable)

**Symptom**: heavy stylization removed all recognizable features.

**Cause**: provider too aggressive, or preset has high identity-loss.

**Fix**:

1. Switch to `--model nano-banana-pro` (better identity preserve).
2. Pick a gentler preset: `watercolor` / `sketch` (less destructive than `cyberpunk` / `vaporwave`).
3. Add identity-preserve cue: `--prompt-mod "preserve subject identity and recognizable features, apply style with restraint"`.

---

## Faces look distorted

**Symptom**: face geometry warped, eyes shifted, features asymmetric.

**Cause**: heavy stylization can break face geometry.

**Fix**:

1. Switch to `--model nano-banana-pro` (face-aware).
2. Or use Replicate face-focused model: `--model replicate-image --replicate-model cjwbw/instant-id`.
3. Pick a face-friendly preset: `watercolor` / `oil-painting` / `sketch` over `cyberpunk` / `low-poly`.

---

## Wrong palette / colors

**Symptom**: requested `--style cyberpunk` but result is muted.

**Cause**: source colors influenced the result too much.

**Fix**:

1. Add explicit palette in `--prompt-mod`: `"vibrant neon pink and cyan dominant, dark background"`.
2. For HEAVY palette override: use `--model flux-kontext` (best palette control).

---

## Output has artifacts (noise, weird textures)

**Symptom**: stylized output has visual glitches.

**Cause**: model interaction with source-image artifacts.

**Fix**:

1. Ensure source image is high quality (no JPEG compression artifacts).
2. Try a different `--model`.
3. Re-run — stylization is stochastic; different seeds → different artifacts.

---

## Style ignored entirely

**Symptom**: requested preset but output looks generic / no style applied.

**Cause**: provider not in edit/image-to-image mode, or kwargs not routed.

**Fix**:

1. Verify the model supports image-to-image (Flux Kontext does; gpt-image-2 partially does).
2. Check `--image` path is valid (typo or missing file leads to text-to-image generation instead).

---

## API key missing

**Symptom**: `missing env: BFL_API_KEY` or similar.

**Fix**:

- For Flux Kontext (default): `/skills-keys add BFL_API_KEY <key>`
- For Nano Banana Pro: `/skills-keys add GEMINI_API_KEY <key>`
- For Replicate: `/skills-keys add REPLICATE_API_TOKEN <key>`

Verify: `/skills-keys verify BFL_API_KEY`.

---

## "flux-kontext requires input_image" error

**Symptom**: error message about missing input_image.

**Cause**: in v2.10.0 the skill passed the wrong kwarg name. **Fixed in v2.10.1** — the provider now accepts both `input_image` and `image_url` aliases.

**Fix**: upgrade to v2.10.1: `skills-update`. If you cannot upgrade, pass `--image` correctly (the CLI in v2.10.1 routes it to the right kwarg per provider).

---

## "gpt-image-2 image-to-image edits not wired"

**Symptom**: error message saying gpt-image-2 isn't wired for image-to-image.

**Cause**: gpt-image-2's edit mode uses a different OpenAI endpoint (`/v1/images/edits`) than the standard `/v1/images/generations` the provider currently wraps. Wiring this is tracked as a future enhancement.

**Fix**: use `--model flux-kontext` or `--model nano-banana-pro` instead. Both fully support image-to-image.

---

## Nano Banana Pro returned the original image (no style applied)

**Symptom**: requested style but output looks identical to input.

**Cause** (v2.10.1+): possible — Gemini sometimes returns the reference image unchanged when the prompt is interpreted as a request to "describe" rather than "transform".

**Fix**:

1. Strengthen the prompt: include explicit transformation verbs ("transform into", "convert to") — these are baked into the preset.
2. Re-roll — Gemini is stochastic; sometimes the second call works.
3. Switch to `--model flux-kontext` (more reliable for style transfer).

---

## Cost is higher than expected

Default Flux Kontext is $0.05 per edit. For batch:

- Single image: $0.05
- 10 images in a loop: $0.50
- Replicate alternatives may be cheaper ($0.01-0.03) but variable

Use `--cost-only` to preview before committing.

---

## Want to style-transfer a video

This skill is image-only. Video style-transfer requires frame-by-frame with temporal coherence — different problem.

For video style-transfer:
- **Runway Gen-4 Aleph** (V2V) — best for short clips
- **Kaiber** (commercial) — animation/style on existing video
- **Final Cut / Premiere stylize effects** — non-AI but predictable

The skill doesn't wrap video style-transfer in v1.

---

## Want to combine 2 styles

❌ "Watercolor + cyberpunk in one output."

Image-gen models can't reliably combine 2 strong styles in one pass. Workaround:

1. Apply style 1: `style-transfer --image input.png --style watercolor`.
2. Apply style 2 to the result: `style-transfer --image watercolor-output.png --style cyberpunk`.

Result will be unpredictable. Manual editing in Photoshop / Affinity is usually a cleaner path for combined-style effects.

---

## Living-artist style request

❌ `--prompt-mod "in the style of [living artist]"`.

This is ethically + legally fraught. The model may approximate the artist's signature work, raising IP concerns.

✓ Use descriptive style language instead:
- "watercolor portrait with soft palette" (not "in the style of Andrew Wyeth")
- "geometric Bauhaus-inspired" (not "in the style of Wassily Kandinsky")
- "1920s constructivist poster" (not "in the style of Alexander Rodchenko")

---

## Want vector output

This skill outputs raster PNG. For vector:

1. Pick best variant.
2. Open in Illustrator / Affinity Designer / Vectornator.
3. Image Trace / auto-trace to vectorize.
4. Manual cleanup.

The output formats best for vectorization: `--style line-art` (clean outlines vectorize cleanly).

---

## Output dir / filename

Default: `./generated/stylized/<input-stem>-<style>.png`.

Override: `--output ./my-path/file.png`.

For batch: loop in shell:

```bash
for f in ./photos/*.jpg; do
  style-transfer --image "$f" --style watercolor --output "./watercolor/$(basename "$f" .jpg).png" --execute --yes
done
```
