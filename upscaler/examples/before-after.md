# upscaler — calibration

3 example sessions.

---

## Example 1 — AI-gen image to print resolution

### User says

> Сгенерил картинку 1024×1024 для обложки, нужно 4× для печати.

### Command

```
upscaler --image ./generated/image/cover.png --scale 4 --execute
```

### What happens

1. Default model: `nightmareai/real-esrgan`.
2. Cost: ~$0.005.
3. Output: `./generated/upscaled/cover-4x.png` (4096×4096 PNG).
4. AI fills in detail consistent with the source — sharper edges, finer textures.

### Next steps

- For print: convert to CMYK in Affinity Publisher / InDesign.
- For web: keep RGB, optionally compress to JPEG.

---

## Example 2 — Old family portrait restoration

### User says

> Скан фотки 1972 года, низкое разрешение, лицо размытое. Восстанови.

### Command

```
upscaler --image ./grandma-1972.jpg --scale 4 --replicate-model tencentarc/gfpgan --execute
```

### What happens

1. Switched to `tencentarc/gfpgan` (face restoration).
2. Cost: ~$0.005.
3. Output: `./generated/upscaled/grandma-1972-4x.png` with restored face detail.
4. Background may be slightly less crisp than face (GFPGAN prioritizes face).

### Notes

- For very degraded photos: combine with manual cleanup in Photoshop / Affinity.
- For pictures with multiple people: GFPGAN handles 1-3 faces well; many faces → may distort secondary subjects.

---

## Example 3 — Product photo for e-commerce

### User says

> Фото товара 1080p с айфона, нужно для Shopify в 2000×2000.

### Command

```
upscaler --image ./shoe-iphone.jpg --scale 2 --replicate-model philz1337x/clarity-upscaler --output ./products/shoe-2k.png --execute
```

### What happens

1. `philz1337x/clarity-upscaler` selected (best texture preservation).
2. `--scale 2` (less aggressive — preserves product fidelity better than 4×).
3. Cost: ~$0.015.
4. Output: `./products/shoe-2k.png` (2160×2160 PNG, leather texture preserved).

### Anti-pattern (don't do this)

❌ Use Real-ESRGAN at 4× for a product shot — risks over-smoothing fabric / leather textures.

✓ Use Clarity Upscaler at 2× for product photography.

---

## Anti-patterns (across examples)

### Expecting magic restoration from extreme low-res

❌ 64×64 thumbnail → 4K photoreal output.

Upscale ratio too large. Result: heavily hallucinated, distorted.

✓ Accept moderate upscaling (2-4×) and combine with manual editing for severely degraded sources.

### Upscaling text-heavy documents

❌ Pass a screenshot of a code editor at 720p, expect crisp text at 4K.

Result: text edges blur slightly. Better to recapture at retina, or use vector OCR + re-render.

### Upscaling video frame-by-frame

❌ Extract 30 frames, upscale each, re-assemble.

Temporal coherence breaks. Result flickers.

✓ Use video-specific upscalers (Topaz Video AI, DaVinci Resolve Super Scale).

### Stacking multiple upscale passes

❌ 2× → 2× → 2× to get 8×.

Compound artifacts.

✓ Single 4× pass is cleaner. For 8×: use a model that natively supports it (Real-ESRGAN).
