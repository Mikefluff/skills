---
name: upscaler
description: "Image upscaling utility — image in, upscaled image out (2× / 4× / 8×). Wraps Replicate upscalers (Real-ESRGAN default; GFPGAN for faces, SwinIR, clarity-upscaler). Optional --face-enhance for portrait restoration. Use when: 'upscale', 'enhance resolution', 'sharpen low-res image', 'make this bigger', 'улучши разрешение', 'увеличь фотку', 'апскейл'."

license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Image upscaling utility. Single input image → output upscaled by 2× / 4× / 8× factor. Sharper, higher resolution, with AI-based detail interpolation (vs simple bilinear / bicubic).

This skill does NOT:
- Generate new content — it ENHANCES existing pixels via super-resolution models
- Magic-restore an image from junk-tier (16×16 thumbnail to 4K HD) — input quality matters; garbage in, garbage out
- Handle video — one frame at a time only
- Vectorize — output remains raster PNG
- Remove background (chain with `bg-remover`)
- Fix major artifacts (deep blur, motion blur, JPEG mosquito noise at extreme levels) — works best on mildly low-res / soft images
</objective>

## ROLE

Read input image → call a Replicate-hosted upscaler → save the upscaled output at the requested scale factor.

## PIPELINE

1. **Resolve input**:
   - `--image <path-or-url>` (required)

2. **Pick provider**:
   - Default: `nightmareai/real-esrgan` (popular general-purpose, ~$0.005/image at 4×)
   - Alternatives via `--replicate-model <id>`:
     - `nightmareai/real-esrgan` — default; best general
     - `tencentarc/gfpgan` — face-focused (best for portraits)
     - `jingyunliang/swinir` — alternative general
     - `philz1337x/clarity-upscaler` — high-fidelity preservation, slower
   - Other Replicate upscalers: pass via `--replicate-model <slug>`

3. **Scale**: `--scale 2|4|8` (default 4).

4. **Face enhance** (optional): `--face-enhance` enables face restoration (Real-ESRGAN supports GFPGAN-style face restoration as a flag).

5. **Execute** via the Replicate router (REPLICATE_API_TOKEN required).

6. **Save**:
   - Default: `./generated/upscaled/<input-stem>-4x.png` (or `-2x.png` / `-8x.png`)
   - Custom: `--output <path>`

## MODES

### Required

- `upscaler --image <path-or-url>`

### Options

- `--scale 2|4|8` — upscaling factor (default 4)
- `--output <path>` — explicit output path
- `--replicate-model <id>` — override default upscaler model
- `--face-enhance` — enable face restoration (works with Real-ESRGAN, GFPGAN)
- `--yes` — skip cost confirmation
- `--check` — verify REPLICATE_API_TOKEN + connectivity

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/providers.md](references/providers.md) | Replicate upscaler model comparison + when to pick which |
| [references/use-cases.md](references/use-cases.md) | Real-world scenarios (old photo restoration, product shots, low-res AI gen output) |
| [references/troubleshoot.md](references/troubleshoot.md) | When output is blurry, faces get distorted, artifacts appear |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: AI-gen image at higher resolution, old family photo restoration, product shot enhancement.

## CONSTRAINTS

- **Single image per call.** For batch: run in a shell loop.

- **Replicate API key required.** Set via `/skills-keys add REPLICATE_API_TOKEN r8_...`.

- **Cost**: ~$0.005-0.02 per image depending on model and scale. 4× cheapest; 8× ~3× more expensive.

- **Input quality matters.** Models can enhance mildly-low-res images (480p → 1920p, soft → sharp). They CANNOT magic-restore severely degraded images.

- **Face preservation**: use `--face-enhance` or switch to `--replicate-model tencentarc/gfpgan` for portraits. Without this, generic upscalers may distort facial features.

- **Output dimensions** = input × scale factor. A 512×512 input at `--scale 4` → 2048×2048 output. Plan disk space.

- **Output format is PNG by default.** Source format preserved when possible; transparent backgrounds maintained.

- **Default 4×** is the most-supported scale across all upscalers. Some models don't support 8×.

- **No re-encoding to JPEG by skill.** If you need JPEG: convert after via `magick` or Photoshop / Affinity.

- **Never print API keys.**

- **Output dir is `./generated/upscaled/`** by default.

## INVOCATION HINTS

When the user says any of:

- "upscale this image", "enhance the resolution"
- "make this bigger / sharper", "fix this low-res image"
- "4x upscale", "8x upscale"
- "улучши разрешение", "увеличь фотку", "апскейл", "повысь разрешение"
- "сделай четче"

Defaults: `--image <path>` (required); 4× via Real-ESRGAN; saves to `./generated/upscaled/<stem>-4x.png`.

For portrait / face photos: prefer `--face-enhance` or `--replicate-model tencentarc/gfpgan`.

For AI-gen output to upscale: default (Real-ESRGAN) works well; the model is trained on a mix of real + AI imagery.

This skill is distinct from:
- `image-prompt` / `cover-maker` / etc. — they GENERATE new images. This ENHANCES existing.
- `bg-remover` — that's segmentation (transparent BG). This is super-resolution.
- `style-transfer` (planned) — that's stylization. This is resolution.
- `style-check` etc. — those are text linters, not visual utilities.
