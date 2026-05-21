# ByteDance Seedream models

Unified gen + edit family with weighted multi-reference support. 4K output.

---

## Seedream 4.5 (GA Dec 2025)

**Strengths**: unified gen + edit in one model; 4K output; up to 6 reference images with weighted role assignment (Character / Style / Palette / Layout); ~10× speed-up vs the original Seedream release; strong on Chinese + English typography.
**Weaknesses**: smaller English-language community than Flux / SDXL; prompt grammar varies by host (Freepik / Wavespeed / fal expose slightly different fields).

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

<!-- TODO: confirm whether 4.5 exposes an in-prompt `[ref:character@1.0]` notation or only the API-side field; magichour.ai docs describe weight roles for 4.0 but not the wire format for 4.5 -->

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

### Syntax

Same role + weight model as 4.5, up to 10 references.

<!-- TODO: confirm 5.0 default-weight changes and exact reasoning-mode toggle name once stable docs land -->

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
