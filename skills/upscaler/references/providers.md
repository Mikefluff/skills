# Providers — upscaler

All models hosted on Replicate. Picked via `--replicate-model <slug>`.

---

## Default: `nightmareai/real-esrgan`

The most popular general-purpose AI upscaler.

| Strength | Score |
|---|---|
| General-purpose detail enhancement | best |
| Face preservation (with `--face-enhance`) | very good |
| Speed | fast (~5-10s for 4×) |
| Cost | $0.005 for 4× / $0.015 for 8× |
| Max scale | 8× supported |
| Format | PNG / JPEG out |

**Use for**: most images (AI-gen output, photos, illustrations, screenshots).

**Pitfalls**: can over-smooth fine textures (hair, fabric). Use `--face-enhance` for portraits.

---

## Face-focused: `tencentarc/gfpgan`

Specialized for face restoration. Best at portraits, headshots, old family photos.

| Strength | Score |
|---|---|
| Face restoration (eyes, skin, hair detail) | best |
| Non-face content | not great — use Real-ESRGAN for body / background |
| Cost | $0.005 per image |
| Max scale | 2× / 4× |
| Format | PNG / JPEG |

**Use for**: portrait close-ups, headshots, ID photos, old scanned family photos.

**Pitfalls**: only optimized for faces — background may not upscale as cleanly.

---

## Alternative general: `jingyunliang/swinir`

Transformer-based upscaler. Different model family than ESRGAN.

| Strength | Score |
|---|---|
| Texture preservation (skin pores, fabric weave) | very good (slightly better than ESRGAN for natural textures) |
| Speed | medium (~15-20s) |
| Cost | $0.01 per image |
| Max scale | 4× |
| Format | PNG |

**Use for**: photoreal images where ESRGAN over-smooths textures.

---

## High-fidelity: `philz1337x/clarity-upscaler`

Newer model, designed for high-fidelity preservation (less "AI smoothing").

| Strength | Score |
|---|---|
| Preservation of original detail | best |
| Speed | slower (~30-60s) |
| Cost | $0.015-0.025 per image |
| Max scale | 4× |
| Format | PNG / JPEG |

**Use for**: where you need maximum fidelity to the source (product photography, archival material).

**Pitfalls**: more expensive + slower. Not for batch work.

---

## Decision tree

```
Generic image / AI-gen output / illustration
  → nightmareai/real-esrgan  (default)

Portrait close-up / face restoration
  → tencentarc/gfpgan
  OR --face-enhance with Real-ESRGAN

Photoreal with delicate textures (hair / fabric / skin)
  → jingyunliang/swinir

Product photography / archival / max-fidelity
  → philz1337x/clarity-upscaler
```

---

## Models NOT in this list

- **Topaz Photo AI** — not on Replicate (desktop app, paid license). Best-in-class but not API-accessible.
- **Adobe Super Resolution** — Photoshop / Lightroom only (Adobe Sensei).
- **Local rembg-style upscalers** — possible to run offline (Real-ESRGAN locally), but skill doesn't wrap local execution in v1.

---

## Cost guide (May 2026)

| Model | 2× cost | 4× cost | 8× cost |
|---|---|---|---|
| Real-ESRGAN | $0.003 | $0.005 | $0.015 |
| GFPGAN (face) | $0.005 | $0.005 | N/A |
| SwinIR | $0.008 | $0.010 | N/A |
| Clarity Upscaler | $0.015 | $0.020 | N/A |

Batch of 10 portraits at 4× via GFPGAN ≈ $0.05. Very affordable for most use cases.

For >100 images: consider running Real-ESRGAN locally (the model is open-source) rather than via API.
