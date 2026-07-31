# Model picker — avatar-maker

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision tree + capability matrix for identity-preserving portrait generation.

---

## Decision tree

```
1. Identity preservation is critical (the user's exact face must remain recognizable)?
     yes → nano-banana-pro  (default; best identity preserve in the industry)
     no  → continue (rare for avatars — usually you want identity preserved)

2. Style anchor pulls heavily toward a non-photographic medium?
     If style is illustrated / 3D / abstract:
        warn the user — identity is harder to preserve
        nano-banana-pro still does best, but expect "person who looks like X in that style"
     If style is photoreal:
        nano-banana-pro is ideal

3. Need extreme palette / texture transfer (move the photo into a specific era/aesthetic)?
     nano-banana-pro is OK but flux-2-pro / seedream-4.5 may transfer harder palette shifts at some identity cost.
     Trade-off: pick what the user prioritizes.

4. Photo has multiple people?
     nano-banana-pro picks one face. If the user wants all preserved (rare for "avatar" use):
        use image-prompt --execute --model gpt-image-2 with the group photo + explicit instruction
     For most "avatar" requests, one face is the intent.

5. Available env vars?
     drop candidates without env vars
     fallback: gpt-image-2 (decent identity preserve, supports multi-ref)
```

### Default pick

`auto` → `nano-banana-pro` if `GEMINI_API_KEY` is set.

Fallbacks (in order):
1. `gpt-image-2` if `OPENAI_API_KEY` set
2. `flux-2-pro` if `BFL_API_KEY` set
3. `replicate-image` router (variable)

---

## Capability matrix (for avatar use case)

| Slug | Provider | Identity preserve | Style transfer | Cost/variant | Latency | Best for avatar |
|---|---|---|---|---|---|---|
| `nano-banana-pro` | Google | excellent (industry-best) | good | $0.05 | 4-8s | DEFAULT pick |
| `gpt-image-2` | OpenAI | medium | medium | $0.05-0.10 | 6-10s | When NBP unavailable |
| `flux-2-pro` | BFL | good | excellent | $0.06 | 5-12s | When palette transfer matters more than exact identity |
| `flux-kontext` | BFL | good | excellent for edits | $0.05 | 5-10s | Edit-mode (e.g., "make this exact photo more polished") |
| `seedream-4.5` (via fal) | ByteDance | good | excellent for photoreal | $0.04 | 6-12s | Photoreal stylization |
| `imagen-4-ultra` | Google | good | good | $0.06 | 5-9s | Limited multi-ref but works for single portrait |

### Anti-recommendations for avatars

| Slug | Why not |
|---|---|
| `flux-schnell` | Too low fidelity for portrait detail |
| `ideogram-3` (any) | Text-rendering specialty; weaker on identity preserve |
| `imagen-4` (non-ultra) | No multi-ref support — can't accept your photo as input |

---

## Cost preview by run shape

| Aspects × variants | Model | Total |
|---|---|---|
| 1 × 3 (default) | nano-banana-pro | $0.15 |
| 1 × 5 | nano-banana-pro | $0.25 |
| 3 × 3 (cross-platform) | nano-banana-pro | $0.45 |
| 1 × 3 | gpt-image-2 (medium) | $0.15-0.30 |
| 1 × 3 | flux-2-pro | $0.18 |

All under default `SKILLS_CAROUSEL_BUDGET=$1.50` (avatar shares the carousel budget).

---

## When to override `auto`

- **Hyper-stylized avatar (anime / cartoon / illustrated)**: force `--model nano-banana-pro` STILL — it adapts better than alternatives, but accept that exact identity may shift. Or use `image-prompt --execute` with text-only prompt + reference image for style.

- **Brand-colored portrait (specific palette)**: force `--model flux-2-pro` if palette transfer is the priority.

- **Edit existing portrait** (the photo is already a great avatar but needs polish): use `image-prompt --execute --model flux-kontext --image-url <photo> --prompt "subtle polish: smoother skin, slightly warmer color temperature"`.

- **Multi-person photo and you want all preserved**: this skill is single-subject. Use `image-prompt --execute --model gpt-image-2 --image-url <group-photo> --prompt "..."` for group portraits.

- **Cheaper iteration on prompts/styles**: force `--model flux-schnell` for cheap fast preview (accept low fidelity), then final with `--model nano-banana-pro`.

---

## Identity preserve mechanics

How models do it:

- **Nano Banana Pro**: face encoder + identity vector injection. Best at preserving even with strong style transfer.
- **Flux Kontext**: edit-mode — operates ON the input image rather than generating from scratch. Preserves identity by design.
- **gpt-image-2**: multi-ref with image-context. Decent but face can drift.

Things that hurt identity preserve (any model):

- Source photo too small (<800px on short edge)
- Heavy shadow / backlight obscuring face
- Extreme angle (full profile, looking away)
- Multiple faces in source (model picks one, may blend)
- Style anchor that calls for non-photographic medium (illustration / 3D)

Things that help:

- Clean front-facing portrait, ≥800px
- Even lighting
- Single subject
- Photoreal style anchor
- Multiple variants — pick the best of 3-5

---

## Provider env-var prerequisites

| Provider | Required env vars |
|---|---|
| `nano-banana-pro` | `GEMINI_API_KEY` |
| `gpt-image-2` | `OPENAI_API_KEY` |
| `flux-2-pro` / `flux-kontext` | `BFL_API_KEY` |
| `seedream-4.5` (via fal) | `FAL_KEY` |
| `imagen-4-ultra` | `GEMINI_API_KEY` |

Run `/skills-keys verify` to confirm all configured providers are reachable.
