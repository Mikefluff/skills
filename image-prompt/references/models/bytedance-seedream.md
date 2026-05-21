# ByteDance Seedream models

Unified gen + edit family with weighted multi-reference support. 4K output.

---

## Seedream 4.5 (GA Dec 2025)

**Strengths**: unified gen + edit in one model; 4K output; up to 6 reference images with weighted role assignment (Character / Style / Palette / Layout); ~10× speed-up vs the original Seedream release; strong on Chinese + English typography.
**Weaknesses**: smaller English-language community than Flux / SDXL; prompt grammar varies by host (Freepik / Wavespeed / fal expose slightly different fields).
**Execute via**: prompt-only — no native ByteDance adapter in v2.2. Workaround: `--execute --model fal-image --fal-model fal-ai/bytedance/seedream-v4/sequential-image` (fal.ai mirror, env: `FAL_KEY`).

### Syntax

Weighted multi-reference roles — assign each reference image a ROLE + WEIGHT. Default weights:
- Character — 1.0 (identity lock, the strongest role)
- Style — 0.9 (palette + texture + lens look)
- Palette — 0.7 (color story only)
- Layout — 0.6 (composition / framing)

How weights are passed depends on the host API. Typical shape (host-dependent):

```
references: [
  { url: "...", role: "character", weight: 1.0 },
  { url: "...", role: "style",     weight: 0.9 },
  { url: "...", role: "palette",   weight: 0.7 },
  { url: "...", role: "layout",    weight: 0.6 },
]
```

**Wire format (May 2026)**: 4.5 exposes per-reference roles through the **API-side `references[]` array only** — there is no canonical in-prompt `[ref:character@1.0]` notation. Hosts (fal, Wavespeed, Freepik, Novita, CometAPI) all accept up to ~10 image URLs / base64 and route them via API fields. Inside the text prompt, you can still nudge any token with the SD-style `(word:1.2)` weighting (e.g. "(character:1.2)" — but only as a soft hint, not a structured role assignment). Sources: [fal.ai Seedream 4.5 guide](https://fal.ai/learn/devs/seedream-v4-5-prompt-guide), [evolink.ai prompt guide](https://evolink.ai/blog/seedream-prompt-guide-best-practices-2026).

### Prompt template

```
{subject + action + context}, {style tags}, {lighting}, {camera}, {texture}, {aspect}.
References: character=ref1 (1.0), style=ref2 (0.9), palette=ref3 (0.7), layout=ref4 (0.6).
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen at golden hour, editorial photo, cinematic color grading, soft directional window light, 85mm f/1.8, natural skin texture with visible pores, portrait 4:5.
References: character=founder-headshot.jpg (1.0), style=editorial-moodboard.jpg (0.9), palette=warm-cream-and-navy.jpg (0.7), layout=loft-kitchen-wide.jpg (0.6).
```

### Notes

- Character at 1.0 is the identity anchor — don't dilute it below 0.9 if face consistency matters.
- Layout at 0.6 is enough to suggest framing without forcing the reference composition.
- Lower Style to 0.7 if it's overpowering Character.
- 6 refs is the cap — pick the most informative four most of the time.

---

## Seedream 5.0 (Feb 2026)

**Strengths**: extends 4.5 with up to 10 reference slots; adds web-search-grounded generation and a reasoning pre-pass (composition planning before render); same weighted-role system.
**Weaknesses**: newer, less battle-tested; reasoning pre-pass adds latency.
**Execute via**: prompt-only — no native ByteDance adapter in v2.2. Workaround: `--execute --model fal-image --fal-model fal-ai/bytedance/seedream-v4/sequential-image` (fal.ai mirror, env: `FAL_KEY`).

### Syntax

Same role + weight model as 4.5, up to 10 references.

**Reasoning + grounding (May 2026)**: Seedream 5.0 (and 5.0 Lite) ship with **"Deep Thinking"** (intent-aware composition planning) and **real-time web search** baked into the base model — there is NO documented user-facing toggle name as of the 5.0 Lite release post. Behaviour is automatic on supported hosts (Runware, Replicate `bytedance/seedream-5-lite`, ByteDance Seed Studio). Default role weights inherit from 4.5; ByteDance has not published a separate 5.0 default-weight table. Sources: [Seedream 5.0 Lite blog (seed.bytedance.com)](https://seed.bytedance.com/en/blog/deeper-thinking-more-accurate-generation-introducing-seedream-5-0-lite), [genaintel 5.0 release guide](https://www.genaintel.com/guides/seedream-5-0-bytedance-release-guide).

### Prompt template

```
{subject + action + context}, {style}, {lighting}, {camera}, {texture}, {aspect}.
References (up to 10): character=... (1.0), style=... (0.9), palette=... (0.7), layout=... (0.6), ...
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen at golden hour, editorial photo, cinematic color grading, soft directional window light, 85mm f/1.8, natural skin texture with visible pores, portrait 4:5.
References: character=founder-headshot.jpg (1.0), style=editorial-moodboard.jpg (0.9), palette=warm-cream-and-navy.jpg (0.7), layout=loft-kitchen-wide.jpg (0.6), product=branded-mug.jpg (0.5), prop=open-cookbook.jpg (0.4).
```

### Notes

- Use 10 refs for full brand-set lock — character + style + palette + layout + product + props.
- Reasoning mode is worth the latency for multi-element compositions; skip it for single-subject portraits.
