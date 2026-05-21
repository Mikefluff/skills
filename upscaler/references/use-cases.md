# Use cases — upscaler

Concrete scenarios where upscaling moves the needle.

---

## Upscaling AI-gen output

**Scenario**: you generated an image at 1024×1024 via `image-prompt`, need it at 4096×4096 for print or hero banner.

```
upscaler --image ./generated/image/cover.png --scale 4 --execute
```

**Model**: Real-ESRGAN default (works well on AI-gen output).
**Result**: 4096×4096 PNG.

**Tip**: most modern AI-gen models output at 1024-1536. Upscaling to 4× gives you 4K resolution, suitable for billboards, print materials, large-format hero images.

---

## Old family photo restoration

**Scenario**: scanned a 1970s family photo at 480p. Want to restore it.

```
upscaler --image ./grandma-1972.jpg --scale 4 --replicate-model tencentarc/gfpgan --execute
```

**Model**: GFPGAN (face-focused).
**Result**: 1920p portrait with restored facial detail.

**Tip**: for severely degraded photos (heavy grain, faded), a single upscale pass won't fix everything. Combine with manual editing in Affinity / Photoshop.

---

## Product photo enhancement for e-commerce

**Scenario**: phone-camera product photo at 1080p, want it crisp for Shopify product listing at 2000×2000.

```
upscaler --image ./shoe-iphone.jpg --scale 2 --replicate-model philz1337x/clarity-upscaler --execute
```

**Model**: Clarity Upscaler (high-fidelity).
**Result**: 2160p product photo with preserved texture detail (stitching, material weave).

**Tip**: for product shots: use Clarity Upscaler — Real-ESRGAN can over-smooth fabric / leather / metal surfaces.

---

## Game asset / illustration upscale

**Scenario**: 256×256 pixel art / illustration, want 4× larger for promotional materials.

```
upscaler --image ./sprite.png --scale 4 --execute
```

**Model**: Real-ESRGAN (handles illustration well).
**Result**: 1024×1024 illustration with sharp edges.

**Tip**: for pixel art specifically, you may want to preserve the pixelated aesthetic. Real-ESRGAN smooths pixels by default — for "preserve sharp pixels" use a nearest-neighbor scale instead of AI upscale (ffmpeg or ImageMagick `-filter point`).

---

## Screenshot for documentation

**Scenario**: low-DPI screenshot from a non-retina display, need to ship in docs that render on retina.

```
upscaler --image ./screenshot.png --scale 2 --execute
```

**Model**: Real-ESRGAN (text + UI elements render cleanly).
**Result**: 2× resolution screenshot, text edges crisp at retina display.

**Tip**: for UI screenshots, prefer recapturing at 2× from a retina display rather than upscaling. AI upscale of text can introduce subtle artifacts (font shape blurring).

---

## Headshot for professional profile

**Scenario**: phone selfie at 720p, want a higher-res version for LinkedIn / podcast cover.

```
upscaler --image ./me.jpg --scale 4 --face-enhance --execute
```

**Model**: Real-ESRGAN with face-enhance flag.
**Result**: 2880p portrait with enhanced face detail.

**Tip**: for podcast cover requiring 3000×3000: upscale → use `cover-maker --photo ./me-upscaled.png --medium podcast` for the full cover composition.

---

## Anti-use-cases (don't expect miracles)

### Reconstructing from extreme low-res

❌ 64×64 thumbnail → 4096×4096 photoreal.

The upscale ratio is too large; the model has insufficient information. Result: heavy hallucination, distorted details.

✓ For severe low-res sources: accept moderate upscaling (2-4×) and combine with manual restoration.

### Removing motion blur or heavy out-of-focus

❌ Pass a motion-blurred or out-of-focus shot, expect crisp output.

Upscalers add detail consistent with sharpness — they don't deblur or refocus.

✓ For motion deblur: use Topaz Sharpen AI (desktop) or `image-prompt --execute --model flux-kontext --prompt "sharp focus, no motion blur"` on a generated alternative.

### Removing JPEG compression artifacts

❌ Heavily-compressed JPEG (quality 30 or less) won't restore via upscale alone.

The artifacts get amplified rather than removed.

✓ For JPEG cleanup: use a dedicated denoiser first (Topaz DeNoise AI), then upscale.

### Upscaling video frames

❌ Extracting frames + upscaling + re-assembling.

Temporal coherence breaks; result flickers.

✓ For video: use a video-specific upscaler (Topaz Video AI, DaVinci Resolve Super Scale).
