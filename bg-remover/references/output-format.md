# Output format — bg-remover

---

## Default output

- **Format**: PNG with alpha channel (4-channel RGBA)
- **Dimensions**: same as input
- **Filename**: `./generated/bg-removed/<input-stem>-nobg.png`

Example:

- Input: `./photos/me.jpg` (2400×3200 JPEG)
- Output: `./generated/bg-removed/me-nobg.png` (2400×3200 PNG-32 with transparency)

---

## Why PNG (not JPEG)

JPEG doesn't support transparency. Removing the background requires an alpha channel, which only PNG and WebP support.

If you need JPEG output (no transparency):

1. Run bg-remover to get the transparent PNG.
2. Open in an image editor (or use ImageMagick / sips).
3. Flatten onto your desired background color.
4. Export as JPEG.

```bash
# Mac, using sips:
sips -s format jpeg --background ffffff ./generated/bg-removed/me-nobg.png --out me-white-bg.jpg

# Or ImageMagick:
convert ./generated/bg-removed/me-nobg.png -background white -alpha remove -alpha off me-white-bg.jpg
```

---

## Downstream usage

### Composite onto a new background

In any image editor (Photoshop / Affinity / GIMP / Photopea / Pixelmator):

1. Open your new background image.
2. Drag the transparent PNG onto it as a new layer.
3. Scale / position as needed.
4. Flatten + export.

### Use as PNG sticker

Discord / Slack / Telegram sticker packs typically accept PNG with transparency directly.

### Use in design tool

Figma / Sketch / Affinity Designer accept transparent PNG as a starting asset.

### Use on a website

Embed as `<img src="me-nobg.png" alt="...">` — modern browsers all support alpha PNG. CSS can apply backgrounds behind.

### Avatar / profile pic

Most platforms auto-crop to circle and require non-transparent backgrounds. Add a background color first:

```bash
sips -s format png --background ffffff ./generated/bg-removed/me-nobg.png --out me-with-white-bg.png
```

---

## Quality preservation

The bg-remover doesn't re-encode or downscale the subject. The subject pixels stay 1:1 with the input.

What changes:

- Background pixels → transparent (alpha = 0)
- Edge pixels at subject boundary → semi-transparent (alpha 0-255 depending on edge detail)
- Hair / fur / fine detail edges → partial alpha gradient (model-dependent)

What stays the same:

- Subject color / contrast / detail
- Subject sharpness
- Image dimensions

---

## File size

Transparent PNGs are typically larger than equivalent JPEGs:

- 2400×3200 JPEG (95% quality): ~1.5 MB
- 2400×3200 PNG with alpha: ~5-8 MB

If file size matters (e.g., website performance), convert to WebP:

```bash
# Mac, sips:
sips -s format webp ./generated/bg-removed/me-nobg.png --out me-nobg.webp

# Or cwebp directly:
cwebp -q 90 me-nobg.png -o me-nobg.webp
```

WebP supports transparency AND has better compression than PNG.

---

## Batch processing

For multiple images, use a shell loop:

```bash
for img in ./photos/*.jpg; do
  bg-remover --image "$img"
done

# Or in parallel:
find ./photos -name "*.jpg" -print0 | xargs -0 -P 4 -I {} bg-remover --image {}
```

The skill processes one image per call but parallelism via shell scales linearly.
