# Troubleshooting — avatar-maker

When the avatar doesn't come out right.

---

## Face doesn't look like the original

**Symptom**: The output is "a person who kind of resembles" instead of "this specific person".

**Causes + fixes**:

1. **Wrong model.** Models other than Nano Banana Pro lose identity often.
   - Fix: `--model nano-banana-pro`.

2. **Source photo too small / blurry.** Model can't extract identity cleanly.
   - Fix: use a ≥800px on short edge photo. Higher is better (up to ~2000px).

3. **Heavy backlight / shadow / partial occlusion in source.**
   - Fix: use a clean, evenly lit front-facing or 3/4 photo.

4. **Style anchor pulls toward non-photographic medium.** If style says "flat vector illustration", identity necessarily reduces.
   - Fix: use a photoreal style — `kinfolk-minimal`, `photo-editorial-bw`, `gradient-mesh-modern`, `dark-academia`.
   - Or accept identity drift if you wanted a stylized avatar.

5. **Multiple people in source.** Model picks one face, may blend features.
   - Fix: crop the source to just the subject before passing it in.

6. **Source has heavy makeup / costume / props that the model treats as "identity"**.
   - Fix: use a photo of the subject without distinctive accessories (or accept that the accessory becomes "part of the identity" in the output).

---

## All 3 variants look identical

**Symptom**: `--variants 3` returns three near-identical images.

**Causes + fixes**:

1. **Model is very stable on the chosen prompt.** Nano Banana Pro is intentionally low-variance on identity-preserve.
   - Fix: this is usually GOOD — identity is preserved. Pick whichever variant has the framing/expression you like best.
   - If you want more variation: `--style-mod "varied facial expression and angle"`.

2. **Same seed reused.** Some providers reuse seeds for batch calls.
   - Fix: explicit `--seed` flags aren't exposed in v1; the variation comes from the model's natural stochasticity.

---

## Style drifts across variants

**Symptom**: Variant 1 is golden-hour outdoor, variant 2 is studio-light indoor, variant 3 is something else entirely.

**Causes + fixes**:

1. **Style anchor too vague.** `--style auto` may pick something generic.
   - Fix: `--style <specific-id>` — pin to a library entry with a strong style anchor.

2. **Style chosen has too many options.** `gradient-mesh-modern` allows wide interpretation; `swiss-grid-poster` is tight.
   - Fix: pick a style with stricter constraints (`photo-editorial-bw`, `kinfolk-minimal`).

3. **Prompt-side content competes with style anchor.**
   - Fix: keep extra `--style-mod` short. Long modifiers confuse the model.

---

## Aspect ratio wrong

**Symptom**: Asked for `square` (1080×1080), got 1024×1024.

**Causes + fixes**:

1. **Model rounded to its nearest supported aspect.**
   - Fix: usually fine for 1:1 — both 1024×1024 and 1080×1080 are accepted by most platforms. If exact size matters, resize in image editor.

2. **Wrong model for size honoring.** `flux-schnell` defaults to 1024×1024 regardless.
   - Fix: use `nano-banana-pro`, `gpt-image-2`, `nano-banana-2`, or `flux-2-pro` — all honor requested sizes.

---

## Cover-banner output doesn't fit LinkedIn / Twitter / YouTube banner exact dimensions

**Symptom**: `cover` (1080×1350) doesn't match LinkedIn cover (1584×396) or Twitter header (1500×500).

**Cause**: Banner dimensions vary per platform and are weird aspect ratios. The skill provides `wide` (1920×1080, 16:9) as a starting point — you crop in your image editor for the exact banner size.

**Fix**:

1. Generate at `wide` aspect (1920×1080).
2. Open in Photoshop / Affinity / Photopea (free, browser-based).
3. Crop to the target banner aspect:
   - LinkedIn personal cover: 1584×396 (~4:1) — crop a horizontal slice
   - LinkedIn company cover: 1192×220 (~5.4:1) — same
   - Twitter header: 1500×500 (3:1) — crop a horizontal slice
   - YouTube banner: 2560×1440 (16:9) — match aspect, upscale slightly

This is intentional friction — banner crops have platform-specific safe-zones (different on desktop / mobile / TV) that are best handled manually.

---

## Photo doesn't load / "image_url not found" error

**Symptom**: Pass `--photo ./me.jpg` but the runner errors with "file not found" or "URL fetch failed".

**Causes + fixes**:

1. **Wrong path.** `--photo ./me.jpg` is relative to wherever you ran the skill from.
   - Fix: use absolute path: `--photo /Users/you/photos/me.jpg`.

2. **File permissions.** File exists but isn't readable.
   - Fix: `chmod u+r ./me.jpg`.

3. **URL not publicly accessible.** Provider can't fetch a private URL.
   - Fix: upload to a public location (S3 / imgur / Cloudinary) first.

4. **File format not supported.** HEIC from iPhone sometimes fails.
   - Fix: convert to JPG: `sips -s format jpeg me.HEIC --out me.jpg` (Mac) or use an online converter.

---

## Output looks like a different age / ethnicity / gender than source

**Symptom**: 35-year-old male source photo → output looks like a 25-year-old female.

**Cause**: Model misread identity attributes. Often happens with:
- Heavy filters on source
- Ambiguous facial features in source (very young / very androgynous)
- Style anchor that conflicts with source attributes (e.g., source is older but anchor calls for "youthful")

**Fix**:

1. Use a clean source photo with clear attributes.
2. Add explicit attribute hints via `--style-mod "preserve subject's <age> / <gender> / <ethnicity> as in the source"` (the model will respect this more).
3. Switch to `--model nano-banana-pro` if not already.
4. Re-roll with `--variants 5` — sometimes one of the takes gets it right.

---

## "Plastic" / over-smoothed skin in output

**Symptom**: Output looks like a beauty-filter version of the subject — skin too smooth, features too perfect.

**Causes + fixes**:

1. **Model's default for portraits.** Most generative models apply implicit "beauty mode" — younger skin, fewer pores, more symmetry.
   - Fix: `--style-mod "natural unretouched skin texture, visible pores, asymmetric realistic features"`.

2. **Source photo was already heavily filtered.** Model inherits and amplifies.
   - Fix: use an unfiltered source photo. If only filtered photos are available, accept the smoothed look.

---

## Background looks weird / random

**Symptom**: Foreground subject is great, but background has artifacts / nonsensical objects.

**Causes + fixes**:

1. **Style anchor doesn't specify the background.**
   - Fix: `--style-mod "soft out-of-focus neutral studio background"` or `"warm interior with shallow depth of field"`.

2. **Aspect choice exposes more background.** `story` (9:16 full-body) shows much more environment than `square-tight`.
   - Fix: use a tighter aspect, OR add background guidance via `--style-mod`.

---

## Want a specific outfit / clothing

The skill doesn't accept outfit instructions as a separate flag in v1. Pass via `--style-mod`:

```bash
avatar-maker --photo ./me.jpg --style-mod "wearing a charcoal blazer over a white shirt, no tie"
```

The model preserves the face but applies the clothing guidance. Note: clothing accuracy varies — explicit color + simple garment names work better than detailed fashion descriptions.

---

## "But the source photo IS perfect, why does the output look worse?"

Sometimes the source IS the ideal — you wanted a stylized variant. Reset expectations:

- The output is NOT a touched-up version of the source. It's a NEW image with the same identity but the style anchor's palette + composition + lighting applied.
- If you just want a polished version of the source, this is not the right skill. Use `image-prompt --execute --model flux-kontext --image-url <photo> --prompt "subtle polish, no major changes"` instead.
- Or use Photoshop / Lightroom / Affinity for non-AI retouching.

The avatar-maker is for "I have a photo, I want N variants in a brand style." Not for "polish my source photo."
