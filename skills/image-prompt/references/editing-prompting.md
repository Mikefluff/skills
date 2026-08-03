# Editing & multi-reference prompting

How to write prompts for image-to-image edits, character/identity locks, and multi-reference composition. The grammar is different from text-to-image — describe only what changes, not the source.

---

## When to use this file

Load this whenever the user supplies one or more input images and wants to edit, extend, recompose, or lock identity across generations.

---

## Edit-grammar fundamentals

- **Single change per generation.** Don't stack edits — chain them as multi-turn instead. "Change the dress to red AND move her to a beach AND swap the lighting" produces mush. Run three turns.
- **"Replace X with Y. Keep everything else locked."** This is the canonical pattern. Works on Kontext, Nano Banana Pro, gpt-image-2.
- **Don't re-describe the source image.** The model already sees it. Describing what's already there confuses the diff — the model thinks you want a regeneration, not an edit.
- **Name what must be preserved.** Explicit preserve list — face, pose, lighting, background, framing. Otherwise the model drifts.

---

## Per-model edit grammar

### Flux Kontext

- Pattern: `Replace [object] with [new description]. Preserve [face / pose / lighting / background].`
- Edit prompt: max 512 tokens.
- Reference context: 4K tokens.
- Strong at local edits; weaker at global recomposition.

```
Replace the white shirt with a navy wool turtleneck.
Preserve face, hair, pose, lighting, and background.
```

### Nano Banana Pro

- Multi-turn in Gemini chat. State edits sequentially across turns; the model carries scene state.
- After generating, you can say "now make her dress red" and it edits the previous output.
- Up to 14 input images; up to 5 people with identity preserved.

```
Turn 1: Generate the scene.
Turn 2: Now make her dress red. Everything else stays.
Turn 3: Now move the scene to a rooftop at golden hour. Keep her and the dress identical.
```

### gpt-image-2

- Natural language + explicit preserve list. Agentic — handles "make it consistent with the previous image" well across a conversation.
- Up to 16 reference images.
- Strong at "match the style of ref 3 but use the subject from ref 1".

```
Using the subject from image 1 and the lighting style from image 3,
generate a new shot in a sunlit kitchen. Preserve facial identity exactly.
```

### Seedream 4.5

- Weighted-role reference syntax. Each ref is named by role + weight.

```
Character: ref1.jpg, weight 1.0
Style: ref2.jpg, weight 0.9
Palette: ref3.jpg, weight 0.7
Layout: ref4.jpg, weight 0.6
Prompt: editorial portrait, soft window light, 85mm
```

---

## Character / identity locks

| Model | Mechanism | Limit |
|---|---|---|
| Midjourney v7 | `--oref <url>` flag | 2× GPU cost; not available on Fast / Draft / Conv / `--q 4` |
| Flux Kontext | Input source image + "preserve face / identity" | 1 source per call |
| Nano Banana Pro | Multi-image input | Up to 5 people; 14 input images total |
| gpt-image-2 | Reference image array | Up to 16 references |
| Seedream 4.5 | Weighted `Character` role | Weight 1.0 = full lock |

Use cases:
- Single hero, many shots → Midjourney `--oref` or Flux Kontext
- Group consistency (founder team headshots) → Nano Banana Pro
- Brand character + product + scene → Seedream weighted refs or gpt-image-2

---

## Multi-reference composition

When you need to blend multiple inputs — character + product + style + palette:

- **Seedream 4.5** weighted roles (Character 1.0 / Style 0.9 / Palette 0.7 / Layout 0.6) — most controllable.
- **Flux 2 Pro** multi-ref: up to 10 images, no explicit weights, ordering implies priority.
- **gpt-image-2**: up to 16 images, agentic prompt naming each by role.

Pattern: **name each ref by role, attach a weight**. Don't dump 6 images and hope.

```
Character: founder-headshot.jpg (1.0)
Product: app-screenshot.png (0.8)
Style: vogue-spread.jpg (0.7)
Palette: brand-palette.png (0.5)

Prompt: editorial portrait of the founder holding the phone showing the app,
soft window light, 85mm, magazine-spread composition.
```

---

## Per-model capability matrix

| Model | Edit | Identity lock | Max multi-ref | Multi-turn |
|---|---|---|---|---|
| Flux Kontext | ✓ | ✓ (single source) | 1 | no |
| Nano Banana Pro | ✓ | ✓ (5 people) | 14 | ✓ |
| gpt-image-2 | ✓ | ✓ | 16 | ✓ |
| Seedream 4.5 | ✓ | ✓ (weight 1.0) | weighted, many | partial |
| Midjourney v7 | partial | ✓ (`--oref`) | 1 (oref) | no |
| Flux 2 Pro | partial | ✓ | 10 | no |

---

## Preserve / change templates

### Single-attribute swap (dress color, hair, background)

```
Replace [attribute] with [new value].
Preserve face, pose, lighting, framing, and all other elements.
```

### Composition extension (uncrop / extend canvas)

```
Extend the canvas to the [left / right / top / bottom].
Continue the existing scene naturally — same lighting, same perspective, same style.
Do not alter the existing area.
```

### Style transfer onto existing image

```
Restyle the image in the style of [editorial photo / oil painting / 35mm film].
Preserve composition, subject identity, pose, and overall layout.
Change only the rendering style, color grading, and texture.
```

### Multi-character composite

```
Character A: [ref1] (weight 1.0)
Character B: [ref2] (weight 1.0)
Setting: [ref3] (weight 0.7) or described in text.

Prompt: Character A and Character B [action] in [setting],
[lighting], [lens], [style].
Preserve facial identity for both characters.
```

### Product-into-scene

```
Place the product from [product-ref] into the scene from [scene-ref].
Match the scene's lighting direction, quality, and color temperature.
Preserve the product's exact shape, material, and branding.
```

---

## Anti-patterns

❌ Re-describing the source image content — model already sees it. "A woman in a white shirt with brown hair sitting on a couch — now change her shirt to navy" wastes tokens and confuses the diff. Just say `Replace the white shirt with a navy wool turtleneck. Preserve everything else.`

❌ Stacking multiple edits in one prompt — "make her dress red AND move to the beach AND change to golden hour". Model averages and produces drift. Chain as separate turns.

❌ Mixing Midjourney `--` flags into Kontext / Nano Banana / gpt-image-2 natural-language prompts. `--oref --q 2 --style raw` belongs only in Midjourney. NL models ignore or break on it.

❌ No preserve list — model drifts. Always name what stays.

❌ More than 3 weighted refs in Seedream without thinking about priorities — weights compound and the lowest-weight ref still pulls. Cap at 4 roles.

✅ One change, one preserve list, one model — that's an edit. Anything more is a regeneration.
