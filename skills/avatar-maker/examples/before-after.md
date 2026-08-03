# avatar-maker — calibration

3 example sessions.

---

## Example 1 — Founder LinkedIn headshot (3 variants, single aspect)

### User says

> Make me a professional LinkedIn headshot from this photo: ./alex-selfie.jpg

### What happens

1. Command:

```
avatar-maker --photo ./alex-selfie.jpg \
             --style auto \
             --aspects square \
             --variants 3 \
             --execute
```

2. **Style auto-pick**: photoreal-friendly, professional → `kinfolk-minimal` (or `photo-editorial-bw` if the source has strong B&W feel). Default is kinfolk-minimal.

3. **Model auto**: `nano-banana-pro` (identity preserve for headshots).

4. **Cost**: 3 × $0.05 = $0.15. Under budget.

5. **Execute**: 3 parallel calls. ~15s wall time.

6. **Output**:
   ```
   ./generated/avatar/alex-selfie/
     square-v1.png   (1080×1080, kinfolk editorial palette, even lighting, neutral background)
     square-v2.png
     square-v3.png
     manifest.json
     style-used.md
     prompts.md
   ```

7. The user picks the best of 3 and uploads to LinkedIn.

### What to notice

- One command → 3 variants in ~15 seconds.
- Identity preserved by NBP; style anchor handles palette / lighting / background.
- 3 variants because identity-preserve runs are low-variance — you might not get a noticeable difference, but the framing/expression catches tiny variations.

---

## Example 2 — Black & white editorial portrait set

### User says

> Generate a B&W editorial portrait set from this photo. Make it feel like Magnum photojournalism. I want 5 takes so I can pick.

### Command

```
avatar-maker --photo ./me.jpg \
             --style photo-editorial-bw \
             --aspects square \
             --variants 5 \
             --execute
```

### What happens

- `--style photo-editorial-bw` explicit.
- 5 variants gives more chances to land the right expression + framing.
- Cost: 5 × $0.05 = $0.25.
- Output: 5 PNGs in `./generated/avatar/me/` (single aspect, 5 variants).

The variants will differ in:
- Expression (neutral vs. slight smile vs. contemplative)
- Eye line (camera-facing vs. off-camera)
- Light angle (front-key vs. side-key with shadow)
- Background detail (lighter vs. darker, more vs. less)

The IDENTITY stays the same across all 5 — that's NBP's strength.

### What to notice

- Higher variant count is the right move for editorial styles where the "feel" varies more than identity.
- Style-anchor "photojournalism" implies certain conventions (grain, contrast, candid-feel) that the model interprets per-variant.

---

## Example 3 — Cross-platform avatar set (4 aspects)

### User says

> I'm setting up new social accounts. I need an avatar that works for LinkedIn, Twitter, IG, and a YouTube channel. Same style throughout. Here's my photo: ./me.jpg

### Command

```
avatar-maker --photo ./me.jpg \
             --style gradient-mesh-modern \
             --aspects square,square-tight,cover,wide \
             --variants 2 \
             --execute
```

### What happens

- 4 aspects × 2 variants = 8 images.
- Cost: 8 × $0.05 = $0.40. Under budget.

### Output

```
./generated/avatar/me/
  square-v1.png         (1080×1080, profile pic for LinkedIn/Twitter/IG/GitHub)
  square-v2.png
  square-tight-v1.png   (1080×1080 but face-fills-frame for small thumbs)
  square-tight-v2.png
  cover-v1.png          (1080×1350, IG feed portrait / cover-banner area)
  cover-v2.png
  wide-v1.png           (1920×1080, Twitter header / YouTube banner base)
  wide-v2.png
  manifest.json
  style-used.md
  prompts.md
```

### Manual cropping next

The user takes the `wide-v1.png` into Photopea and crops:
- Twitter header (1500×500 — horizontal slice from `wide`)
- LinkedIn cover (1584×396 — same approach)
- YouTube banner (2560×1440 — upscale `wide` slightly, crop)

The skill doesn't auto-crop because banner safe-zones differ per platform (mobile / desktop / TV) — manual control beats lossy automation.

### What to notice

- Same style + same model across all 8 = consistent brand look across all platforms.
- 4 aspects + 2 variants is sweet-spot for "set me up for the next year" use case.
- Manual cropping for exact banner sizes is intentional friction.

---

## Anti-pattern (don't do this)

### Hyper-stylized illustration without expecting identity drift

❌

```
avatar-maker --photo ./me.jpg --style flat-vector-illustration --variants 1
```

Result: a flat-vector character that *resembles* you but the face becomes "illustrated" — exact identity gets lost.

If you want a stylized "you" illustration, use this command BUT expect the output to be "vector character based on me" rather than "exact me in vector style". The skill warns when illustration styles are picked.

### Using a tiny / heavily-filtered source

❌ Source: `IMG_1234.jpg` at 240×240 with heavy Instagram filter applied.

Result: the model can't extract clean identity. Output looks generic.

✓ Use a clean ≥800px source without filters.

### Stuffing too many style modifiers

❌

```
avatar-maker --photo ./me.jpg \
             --style kinfolk-minimal \
             --style-mod "but warmer with amber undertones and also include some art deco geometric elements behind the subject and make the lighting softer and add a subtle vignette and the clothing should be a navy turtleneck and..."
```

Result: model gets confused, output is muddled.

✓ Pick the closest library style + ONE short modifier (`--style-mod "wearing navy turtleneck, slightly warmer color temperature"`).

### Multi-person source photo

❌ Pass a group photo, expect all faces preserved.

Result: model picks one face, may blend features.

✓ Crop the source to just the subject before running.
