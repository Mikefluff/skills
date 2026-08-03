# Troubleshooting — upscaler

---

## Output looks blurry / not actually upscaled

**Symptom**: 4× upscale looks identical to a 4× bicubic scale (no AI detail enhancement).

**Causes + fixes**:

1. **Source already at the target resolution.** Check input dimensions; if already high-res, AI upscale adds little.
2. **Source too degraded.** Heavy JPEG artifacts or extreme low-res leaves the model with nothing to work from.
3. **Wrong model.** Try `--replicate-model philz1337x/clarity-upscaler` for high-fidelity, or `jingyunliang/swinir` for textures.

---

## Faces look distorted / "plastic"

**Symptom**: portrait upscale produces uncanny-valley face — too smooth, melted eyes, etc.

**Cause**: Real-ESRGAN over-smooths faces by default.

**Fix**:

1. Add `--face-enhance` flag (enables GFPGAN-style face restoration via Real-ESRGAN).
2. Or switch to face-specialist model: `--replicate-model tencentarc/gfpgan`.
3. For old / damaged portraits: use GFPGAN + 2× scale (less aggressive than 4×).

---

## Text in image becomes blurry

**Symptom**: screenshot or document image has text smudged after upscale.

**Cause**: AI upscalers can interpolate text edges, blurring tight font shapes.

**Fix**:

1. Switch to `--replicate-model philz1337x/clarity-upscaler` (better text preservation).
2. For pure text documents: don't AI-upscale — use vector OCR + re-render at target resolution.
3. Re-capture screenshot at native retina resolution if possible.

---

## Output much larger file size than expected

**Symptom**: 4× upscale of 1MB JPEG → 25MB PNG.

**Cause**: PNG is uncompressed; upscaled image has 16× more pixels.

**Fix**:

1. Convert PNG → JPEG for non-transparent images: `magick output.png -quality 90 output.jpg` (typically 70-80% size reduction).
2. For web: use `tinypng` or `pngquant` to losslessly compress.
3. For maximum quality preservation in JPEG: quality 95+ (still much smaller than PNG).

---

## Artifacts at edges / halos

**Symptom**: subject has glowing / halo'd edges after upscale.

**Cause**: model misinterprets soft edges as detail boundaries.

**Fix**:

1. Try a different model: `--replicate-model jingyunliang/swinir` (transformer-based, different edge handling).
2. Lower scale: `--scale 2` instead of 4× often gives cleaner edges.
3. For severe halos: manual edge cleanup in Affinity / Photoshop after upscale.

---

## Wrong colors after upscale

**Symptom**: colors shift slightly (warmer / cooler / saturated differently).

**Cause**: upscaler may normalize / tone-map colors.

**Fix**:

1. Compare side-by-side; the shift is often subtle.
2. Color-correct in post: open original + upscaled in Photoshop / Affinity, sample colors, adjust upscaled to match.
3. Try `--replicate-model philz1337x/clarity-upscaler` (least color shift in our testing).

---

## Replicate API error

**Symptom**: `[replicate 401]` or similar.

**Fix**:

1. Verify token: `/skills-keys verify REPLICATE_API_TOKEN`.
2. Update if needed: `/skills-keys update REPLICATE_API_TOKEN r8_...`.
3. Check Replicate account credits at replicate.com/account.

---

## Model slug doesn't exist

**Symptom**: `model X/Y not found`.

**Fix**:

1. Verify slug at replicate.com/explore.
2. Use a working alternative from `references/providers.md`.
3. Check for typos in `--replicate-model` argument.

---

## 8× upscale doesn't work

**Symptom**: `--scale 8` fails or returns 4× anyway.

**Cause**: not all models support 8×.

**Fix**:

1. Verify your model supports 8× (Real-ESRGAN does; many alternatives cap at 4×).
2. For 8× from non-supporting models: chain two 2× or two 4× passes.
3. Note: stacked upscales compound artifacts. Single-pass 4× is usually higher quality than 2× → 2×.

---

## Output PNG has unwanted transparent areas

**Symptom**: parts of the image are transparent after upscale.

**Cause**: source had transparency that the upscaler preserved.

**Fix**:

1. If transparency wasn't intentional: composite onto a solid background first.
2. If transparency IS intentional: confirm output is RGBA PNG.

---

## Want offline (no API) upscaling

The skill doesn't wrap local execution in v1. Workaround:

```bash
# Install locally
pip install realesrgan basicsr

# Download model weights (one-time)
# See https://github.com/xinntao/Real-ESRGAN

# Run
realesrgan-ncnn-vulkan -i input.png -o output.png -s 4
```

This runs Real-ESRGAN locally. Free, offline, no API key. Slower than Replicate for single images, but better for batch (no per-image API cost).

---

## Cost is higher than expected

Real-ESRGAN 4× ≈ $0.005 per image. If your bill is high:

- Verify model: cheaper models (real-esrgan) vs premium (clarity-upscaler 3-4× more expensive).
- Verify scale: 8× costs more than 4×.
- Replicate dashboard shows per-call cost: replicate.com/account.

---

## Want batch upscaling

The skill runs single-image. For batch:

```bash
for img in ./photos/*.jpg; do
  upscaler --image "$img" --output "./upscaled/$(basename "$img" .jpg)-4x.png" --execute --yes
done
```

For >100 images: consider running Real-ESRGAN locally (free, no API) rather than via Replicate.
