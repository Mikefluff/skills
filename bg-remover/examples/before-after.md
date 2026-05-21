# bg-remover — calibration

2 example sessions.

---

## Example 1 — Portrait photo → transparent for avatar use

### User says

> Remove the background from this photo: ./me.jpg. I want a transparent PNG.

### Command

```
bg-remover --image ./me.jpg --execute
```

### What happens

1. Default model: `851-labs/background-remover` via Replicate.
2. Cost: ~$0.001-0.005.
3. Output: `./generated/bg-removed/me-nobg.png` (same dimensions as input, transparent background, subject preserved).

### Next steps

User opens the transparent PNG in Photopea / Photoshop / Affinity, composites onto a new background (brand-colored, gradient, etc), exports as JPEG for upload.

Or uses the PNG directly as a sticker / overlay in design tools.

---

## Example 2 — Product shot for e-commerce listing

### User says

> Cut out this shoe from its background. I need a clean product photo with transparent background for my Shopify listing.

### Command

```
bg-remover --image ./shoe.jpg --output ./products/shoe-cutout.png --execute
```

### What happens

1. Uses default `851-labs/background-remover`.
2. Saves directly to `./products/shoe-cutout.png` (custom output path).

For Shopify upload:

1. Open `shoe-cutout.png` in image editor.
2. Place on a white background (Shopify requires non-transparent for product images).
3. Export as JPEG at 85% quality.
4. Upload.

```bash
# Or one-liner with ImageMagick:
convert shoe-cutout.png -background white -alpha remove -alpha off shoe-final.jpg
```

---

## Anti-pattern (don't do this)

### Using on a complex multi-subject photo

❌ Pass a photo with 5 people sitting at a table, expect all 5 cleanly cut out.

Result: model picks one main subject, others get partial removal.

✓ Crop the photo to ONE subject first, OR use a manual editor.

### Expecting AI-replaced background

❌ "Remove the background and replace with a beach scene."

This skill ONLY removes the background. For replacement, chain with another tool:

✓

```
bg-remover --image ./me.jpg --execute
# Then:
image-prompt --execute --model flux-kontext --image-url ./generated/bg-removed/me-nobg.png \
             --prompt "subject in front of tropical beach at sunset"
```

Or use any image editor to composite manually.

### Removing background from a video frame

❌ Pass a single MP4 frame, expect frame-by-frame video bg removal.

This is image-only. For video bg removal, you'd need to:

1. Extract frames via ffmpeg.
2. Run bg-remover on each frame.
3. Stitch back as video.

But this is BRITTLE — temporal coherence breaks. Use a real video bg removal tool (Runway, DaVinci Resolve, Premiere Pro's Roto Brush) instead.
