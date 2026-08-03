# ByteDance Seedream models

Unified gen + edit family with weighted multi-reference support. The 5.0
generation added a reasoning pre-pass and, in Pro, layered output.

Both tiers are served through ByteDance's BytePlus ModelArk API and mirrored on
the usual inference hosts. There is no native ByteDance adapter here — reach them
through the fal or Replicate routers.

---

## Seedream 5.0 Lite (Feb 2026)

**Strengths**: reasoning-focused entry tier — "Deep Thinking" plans the composition before rendering, which shows up most on multi-element scenes. Up to 14 reference images with weighted roles. $0.035 / image.
**Weaknesses**: the reasoning pre-pass adds latency; resolution ceiling below Pro.
**Execute via**: prompt-only. Workaround: `--execute --model replicate-image --replicate-model bytedance/seedream-5-lite` (env: `REPLICATE_API_TOKEN`).

---

## Seedream 5.0 Pro (Jul 2026)

**Strengths**: the flagship. Photographic realism plus two things nothing else in
this collection does — **layered output** (one render decomposes into 10+
editable PNG layers) and **spatial annotations** (mark up a reference image and
the model reads the markup as instruction). In-image text across roughly 14
languages. $0.075 / image up to 2.36 MP.
**Weaknesses**: smaller English-language community than Flux / SDXL; prompt grammar varies by host (Freepik / Wavespeed / fal expose slightly different fields).
**Execute via**: prompt-only. Workaround: `--execute --model fal-image --fal-model fal-ai/bytedance/seedream-v4/sequential-image` (env: `FAL_KEY`) until a v5 route is published by the host.

### Why layered output matters here

Every text-in-image skill in this collection carries the same caveat: the model
renders type *into* pixels, so a typo means regenerating the whole frame and
accepting a different composition. Layers break that trade. Text arrives as its
own PNG over the artwork, so a headline fix is an edit rather than a re-roll.

That changes the shape of `carousel-builder` and `flyer-maker` in particular —
their retry loop today is "regenerate the slide", which is what makes a set drift
in style. Worth revisiting once a layered route is wired.

---

## Weighted multi-reference (both tiers)

Assign each reference image a ROLE + WEIGHT. Default weights:

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

**Wire format**: roles go through the **API-side `references[]` array only** —
there is no canonical in-prompt `[ref:character@1.0]` notation. Hosts (fal,
Wavespeed, Freepik, Novita, CometAPI) accept image URLs or base64 and route them
via API fields. Inside the text prompt you can still nudge any token with the
SD-style `(word:1.2)` weighting — a soft hint, not a structured role assignment.

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
- 14 refs is the Lite cap; use the full set only for a brand lock (character + style + palette + layout + product + props).
- The reasoning pre-pass earns its latency on multi-element compositions. Skip it for single-subject portraits.

Sources: [Seedream 5.0 Lite (seed.bytedance.com)](https://seed.bytedance.com/en/blog/deeper-thinking-more-accurate-generation-introducing-seedream-5-0-lite), [fal.ai Seedream prompt guide](https://fal.ai/learn/devs/seedream-v4-5-prompt-guide).
