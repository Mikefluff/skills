# Structured layout prompts (`json_prompt`)

Ideogram 4 takes layout as *structure* instead of prose. Where a text prompt says
"the poster reads OPEN KITCHEN at the top with a sunlit loft below", a structured
prompt says where each element goes and lets the model stop guessing.

That guessing is why prose layout prompts drift between runs: two calls with the
same sentence put the headline in two different places, and a carousel or an
aspect set stops looking like one thing.

`banner-maker`, `flyer-maker` and `logo-maker` already hold this structure — a
headline, a subhead, a CTA, a zone for each. Until now they flattened it into a
sentence for the model to re-infer.

---

## When it applies

Only on `ideogram-4-turbo` / `ideogram-4` / `ideogram-4-quality`. The v3 tiers
have no such field, and the provider **refuses** rather than sending a call whose
layout would be silently ignored — a picture built from nothing you specified is
worse than an error.

Everything else keeps using prose. This is one model's capability, not a new
house style.

---

## The shape

Put it in the plan item's `kwargs`, beside `size`. `prompt` stays as written —
it is the human-readable record in `prompts.md`, and the fallback if the run is
re-executed on a v3 tier.

```json
{
  "index": 1,
  "label": "poster-v1",
  "prompt": "<the prose version, unchanged>",
  "kwargs": {
    "size": "1024x1280",
    "json_prompt": {
      "canvas": {"aspect": "4:5", "background": "warm cream, subtle paper grain"},
      "blocks": [
        {"role": "headline", "text": "OPEN KITCHEN", "font": "bold condensed serif",
         "position": "top-center", "color": "#1b1b1b"},
        {"role": "subhead", "text": "Brooklyn — Est. 2026", "font": "sans",
         "position": "below-headline"},
        {"role": "image", "content": "sunlit loft kitchen, 85mm f/1.8",
         "position": "lower-two-thirds"},
        {"role": "cta", "text": "Tickets in bio", "position": "bottom-center"}
      ]
    }
  }
}
```

`role` is what the block is for, `position` is where it sits, `text` is copied
verbatim into the image. Blocks are drawn in order; later ones sit on top.

---

## Rules that still apply

- **Text length still governs.** Structure tells the model where a headline goes,
  not how to fit twelve words into a strip. The ≤8-word rule stands.
- **Do not restate the layout in the prose prompt.** If both are sent the model
  reconciles two descriptions of the same thing, which is the drift this removes.
  The provider sends one field or the other, never both.
- **Style anchors stay prose.** Palette, mood and medium belong in
  `canvas.background` and in block `font` / `color`, not as a second style essay.
- **Verify the same way.** A structured prompt renders text no more reliably than
  a prose one; it renders it in the *same place* every time. Check the output.
