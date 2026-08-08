# Providers — style-transfer

## Provider status (v2.10.1+)

| Provider | Image-to-image wired? | Notes |
|---|---|---|
| `flux-kontext` (default) | ✅ | BFL's native edit endpoint; best for natural-language style transfer |
| `nano-banana-pro` | ✅ | Gemini 3 Pro Image multimodal; identity preserve priority |
| `replicate-image` | ✅ | pass-through; works if the chosen Replicate model accepts `image` input field |
| `gpt-image-2` | ❌ | not wired in v1 — needs `/v1/images/edits` endpoint (tracked as future enhancement) |
| `flux-2-pro` / `flux-1-1-pro` | ❌ | text-to-image only; use flux-kontext for edits |

If you pick an unsupported provider, the skill exits with a clear error message.

---

## Default: `flux-kontext`

Black Forest Labs Flux Kontext — best in class for natural-language style transfer in 2026.

| Strength | Score |
|---|---|
| Natural-language style instruction | best |
| Identity preservation | very good (mid-tier; 60-80% depending on style) |
| Speed | fast (~10-15s) |
| Cost | $0.05 per edit |
| Source-image fidelity | excellent |

**Env var**: `BFL_API_KEY`.

**Use for**: most style-transfer tasks. Especially good for non-photoreal styles (watercolor, oil-painting, sketch).

---

## Identity-priority: `nano-banana-pro`

Google Nano Banana Pro — best identity preservation when face/person matters.

| Strength | Score |
|---|---|
| Identity preservation | best (~85-90%) |
| Stylization intensity | mid (less aggressive than Flux Kontext) |
| Speed | medium (~15-25s) |
| Cost | $0.05 per image |

**Env var**: `GEMINI_API_KEY`.

**Use for**: portraits where the person needs to remain recognizable. E.g., a portrait stylized as watercolor — Nano Banana Pro preserves the face better than Flux Kontext.

**Pitfall**: stylization is more subtle. For HEAVY stylization, use Flux Kontext.

---

## Specialized: Replicate-hosted style-transfer models

Via `--model replicate-image --replicate-model <slug>`:

- `cjwbw/instant-id` — face-focused, with InstantID style preservation
- `lucataco/sdxl-controlnet` — fine-grained control with ControlNet conditioning
- `tencentarc/photomaker` — Photomaker style transfer

| Strength | Score |
|---|---|
| Style fidelity | varies by model |
| Identity preservation | varies |
| Cost | $0.01-0.05 per image |
| Setup complexity | higher (model-specific kwargs) |

**Env var**: `REPLICATE_API_TOKEN`.

**Use for**: when you need a specific model behavior (e.g., InstantID for ID-preserved face transfer).

---

## Decision tree

```
General style transfer (most cases)
  → flux-kontext  (default)

Portrait where face needs to stay recognizable
  → nano-banana-pro

Specific Replicate model needed (InstantID, PhotoMaker, etc.)
  → replicate-image --replicate-model <slug>
```

---

## Cost guide

| Model | $/image | Speed |
|---|---|---|
| flux-kontext | $0.05 | ~10s |
| nano-banana-pro | $0.134 | ~20s |
| replicate-image (varies) | $0.01-0.05 | ~20-40s |

---

## Anti-defaults

Do NOT use for style-transfer:

- **gpt-image-2** — strong but not specifically tuned for style transfer (better at generation from scratch)
- **ideogram-3-quality** — text leader, but weaker on style transfer
- **veo / sora** — video models
- **suno / lyria** — music models
