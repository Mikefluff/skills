# Providers — bg-remover

Replicate-hosted background removal models.

---

## Default: `851-labs/background-remover`

Most popular, accurate on most photos. Handles:

- Portraits (face + hair + clothing)
- Product shots (objects on plain background)
- Indoor scenes with clear subject
- Photographic and stylized images alike

Limits:

- Fine hair detail (wisps) can be lost
- Reflective / transparent objects (glass) can confuse it
- Subject color matching background (white shirt on white wall) is harder

Cost: ~$0.001 per image. Very cheap.

---

## Alternatives via `--replicate-model`

### `cjwbw/rembg`

Open-source `rembg` library hosted on Replicate. Same underlying technology as the local `rembg` Python package.

Good for: general-purpose, reproducible, free local-equivalent.

### `pollinations/modnet`

MODNet (Modular Mobile Network) — purpose-built for portrait segmentation.

Best for: human portraits, especially when hair edges matter. Slightly slower but higher fidelity on faces.

### `lucataco/remove-bg`

Alternative bg-removal model. Sometimes better on edge cases (e.g., products with shadows).

### Other Replicate options

Browse `replicate.com/explore?query=background+removal` for the full catalog. Pass any slug via `--replicate-model <username>/<model-name>`.

---

## When to override

- **Hair-focused portrait** (long hair, fine wisps): `--replicate-model pollinations/modnet`
- **Product shot with shadow / reflection**: try `lucataco/remove-bg` if default fails
- **Reproducibility for batch jobs**: `cjwbw/rembg` is the most-stable choice

---

## Local-only alternative (no API key)

If you don't want Replicate API costs, install `rembg` locally:

```bash
pip install rembg[gpu]   # or rembg without GPU
rembg i input.jpg output.png
```

This gives you offline background removal. The skill doesn't wrap local `rembg` in v1 — but you can use it independently.

---

## Cost preview

All Replicate bg-removers are roughly $0.001-0.005 per image. Even at $0.005 × 100 images = $0.50 — well under any budget.

No cost confirmation prompt under default thresholds.

---

## Provider env-var prerequisites

| Provider | Required env vars |
|---|---|
| All Replicate bg-removers | `REPLICATE_API_TOKEN` |

Verify with `/skills-keys verify REPLICATE_API_TOKEN`.
