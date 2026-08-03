# Prompt formula

Every prompt follows this 6-part structure. The first 12-15 words anchor the model — put the most-important parts first.

```
{subject + action} + {setting} + {style} + {lighting} + {camera/lens} + {texture/realism}
```

Each part is detailed below. Omit any part if irrelevant (e.g. abstract backgrounds don't need a camera).

---

## 1. Subject + action

The thing being depicted, and what it's doing. Be specific — don't say "a person", say "a confident woman in her thirties leaning on a marble countertop".

**Good**:
- "A confident business person standing arms-crossed"
- "A wireless earbuds case sitting on a marble surface"
- "A cozy café interior, a person reading at a window table"
- "An abstract gradient with flowing organic shapes"

**Bad**:
- "Someone professional" (vague — model picks generic stock photo)
- "Stuff on a table" (no subject anchor)
- "An office vibe" (no concrete subject)

---

## 2. Setting

Where and when. Provides context for lighting and color.

**Templates**:
- Place: "in a sunlit studio", "in a dim industrial loft", "in a forest clearing at dawn", "in a 1970s diner"
- Time: "at golden hour", "midnight", "noon", "dawn", "blue hour"
- Era: "1920s", "futuristic 2080s", "Renaissance", "Soviet 1960s"
- Weather: "after rain, wet pavement reflections", "overcast diffused light", "snow falling lightly"

**Bad**: "in a nice place", "any background", "modern setting".

---

## 3. Style

The aesthetic register. This is the single biggest lever for the model.

**Photographic styles**:
- `photorealistic` — sharp, lifelike (default for product / portrait)
- `editorial photo` — magazine style, considered composition
- `product shot` — clean, commercial advertising
- `documentary photo` — gritty, realistic, slightly unposed
- `cinematic` — film-like color grading, shallow depth of field
- `street photography` — candid, slight imperfection
- `35mm film` / `medium format film` — grain + warm tones

**Illustration styles**:
- `editorial illustration` — magazine illustration vibe
- `flat illustration` / `vector` — clean, minimal
- `watercolor` / `gouache` / `ink wash`
- `3D render` / `octane render` / `cinema 4D`
- `low-poly 3D` / `voxel`
- `pixel art` (16-bit, 8-bit)
- `oil painting` / `digital painting`
- `comic / graphic novel`
- `Studio Ghibli`-inspired (but don't name actual artists/studios literally for commercial use)

**Abstract / minimal**:
- `minimalist`
- `geometric` / `gradient`
- `noise art` / `glitch`
- `risograph print`

**Mixing**: combine 2-3 max, e.g. "editorial photo, cinematic color grading, 35mm film grain". Avoid 5+ style tags — model gets confused.

---

## 4. Lighting

The single highest-leverage modifier for photorealism. Be specific.

See [`lighting-vocabulary.md`](lighting-vocabulary.md) for the full dictionary. Quick reference:

- Portrait: "soft directional key light from upper left", "rim light", "split lighting", "Rembrandt lighting"
- Scene: "golden hour backlight", "overcast diffused light", "neon magenta glow", "single flickering fluorescent overhead"
- Hard vs soft: "hard shadows" vs "soft shadows"
- Quality: "warm ambient", "cool fill", "high key", "low key"

**Bad**: "good lighting", "dramatic lighting", "cinematic lighting" — too abstract. Always specify the light source AND direction AND quality.

---

## 5. Camera / lens (when photorealistic)

Helps photorealistic models commit to a "photo" aesthetic rather than illustration.

See [`camera-vocabulary.md`](camera-vocabulary.md) for full dictionary. Quick reference:

- **Portrait**: "85mm lens, f/1.8", "50mm prime, f/2.8"
- **Wide environmental**: "35mm wide, f/4"
- **Tight detail**: "macro 100mm, f/2.8, shallow depth of field"
- **Casual phone photo**: "smartphone photo, slight digital noise, daylight"
- **Quality tags**: "8K", "ultra-realistic", "photorealistic", "hyper-detailed", "sharp focus"

For illustration / 3D / abstract — omit camera entirely. It just confuses non-photo models.

---

## 6. Texture / realism

Final layer of credibility. Specifies what materials and surfaces look like.

- **People**: "natural skin texture, visible pores when appropriate, no plastic skin, realistic fabric, individual hair strands"
- **Products**: "realistic materials — brushed aluminum, soft-touch plastic, leather grain", "subtle reflections", "fine dust visible"
- **Scenes**: "condensation on glass", "fabric catches light", "steam rising", "wet pavement reflections"
- **Negative space**: "subtle shadows under subject", "depth in the background"

**Bad**: "high quality", "good details" — too generic. "Visible pores on the skin" is what makes it work.

---

## Putting it together — full template

### Template 1 — Portrait

```
{Subject and pose}, {setting},
{style} style,
{lighting setup},
{lens + aperture + camera-quality tags},
{skin and fabric texture details}
```

Example:
```
A confident woman in her thirties leaning on a marble countertop, in a sunlit Brooklyn loft kitchen at golden hour,
editorial photo style with cinematic color grading,
soft directional key light from the upper-left window, slight rim light catching her hair,
85mm lens f/1.8, shot on full-frame DSLR, ultra-realistic, sharp focus,
natural skin texture, visible pores, individual hair strands, realistic linen fabric with soft creases
```

### Template 2 — Product

```
Minimalist product photo of {object} on {surface},
{lighting},
{lens + camera quality tags},
{material textures + reflections}
```

Example:
```
Minimalist product photo of a brushed-aluminum wireless earbuds case on white Carrara marble,
soft directional sunlight from upper-right, subtle reflections in the marble,
50mm lens f/4, 8K, commercial advertising style,
realistic brushed metal with fine grain, subtle shadow under the case, depth in the soft white background
```

### Template 3 — Scene

```
{Scene with one focal subject}, {setting and time},
{style},
{lighting setup including ALL light sources by name},
{lens or pacing},
{tactile / atmospheric texture}
```

Example:
```
A cozy café interior at golden hour, one woman reading at a window table in soft focus background,
editorial photo, cinematic color grading,
warm golden hour backlight from the window, soft ambient fill, individual dust motes visible in the light beam,
35mm lens f/2.8, shallow depth of field, sharp focus on her hands and book,
worn leather chair texture, steam rising from a ceramic mug, condensation on the window
```

### Template 4 — Abstract

```
Abstract {form} with {colors / palette},
{geometry / movement description},
{style if any},
{rendering / quality}
```

Example:
```
Abstract gradient background with flowing organic shapes,
purple and blue tones blending into soft pink at the edges,
minimal design, gentle motion blur,
high resolution, smooth gradients, no banding
```

### Template 5 — Illustration

```
{Subject}, {style},
{composition / framing},
{color palette + mood},
{technical quality}
```

Example:
```
A solitary lighthouse on a cliff at dawn, watercolor illustration style with ink outlines,
loose composition, lighthouse off-center on the right,
muted warm palette — peach, mauve, soft slate blue,
high resolution, visible paper texture, soft watercolor bleed at edges
```

---

## Negative prompts (when to use)

Negative prompts work in Midjourney (`--no`), Flux, Stable Diffusion. DALL-E doesn't support them directly (encode as natural language: "without text, no watermark").

**Standard photorealistic negative**:
```
text, watermark, logo, distorted anatomy, extra fingers, blurry, low resolution, plastic skin, oversaturated
```

**Editorial / portrait additions**:
```
+ stock photo aesthetic, generic, airbrushed
```

**Product shot additions**:
```
+ dirty, scratched, dented (unless intentional)
```

See [`model-picker.md`](model-picker.md) and the per-vendor files in [`models/`](models/) for how each model handles negatives.

---

## Anti-patterns

❌ "Generate an image about cold emails" — no scene, no subject. Pick something concrete: "An empty inbox at 3am, screen glow lighting a tired face".

❌ "Make it look good" / "high quality professional image" — empty modifier. Strip and replace with specific quality tags.

❌ "A beautiful sunset with everything you'd want" — model can't commit to anything.

❌ Listing 8+ adjectives — model averages them and produces mush. 3-5 style/quality tags max.

❌ Naming real artists or celebrities — most commercial-license models block this; some output legally-risky results.

✅ "A close-up of an empty mailbox at dawn, weathered red metal flag tilted up, dew on the surface, golden hour backlight, 50mm lens f/2.8, photorealistic, visible flaking paint and metal grain" — specific, every part earned.

---

## 7. (conditional) References / multi-ref

This block fires only when the target model supports **image references** — Flux 2 Pro (≤10 refs), Flux Kontext (edit), Nano Banana Pro (14 refs, 5-people consistency), gpt-image-2 (≤16 refs), Seedream 4.5 (6 weighted refs), Midjourney v7 (`--sref` style, `--oref` Omni / identity).

When refs are attached, the prompt body changes:

- **Don't re-describe what the ref already shows.** If `[ref:Sarah]` carries her appearance, the prompt should NOT say "long brown hair, green eyes" — that overrides the ref and causes drift.
- **Name each ref by role.** Pattern: `[ref:character@1.0] [ref:style@0.9] [ref:palette@0.7] [ref:layout@0.6]` (Seedream 4.5 weighted-role syntax) or `--sref <url-or-code>` / `--oref <url>` (Midjourney v7).
- **Describe only what changes / what's new.** Wardrobe, action, expression, environment. Identity/style come from the ref.

### Pattern: identity-locked portrait

```
[ref:character@1.0] in a sunlit Brooklyn loft kitchen, wearing a linen apron, leaning on the marble countertop, gaze toward the window. Editorial photo. Soft directional key light from upper-left. 85mm f/1.8. Natural skin texture.
```

### Pattern: multi-ref composite (Seedream 4.5)

```
[ref:character@1.0] holding [ref:product@0.85], styled per [ref:style@0.7], on [ref:palette@0.7] background. Studio lighting, 50mm f/8, product-shot composition.
```

### Pattern: Kontext edit (deviation from the 6-part formula)

Kontext takes the source image as input. The prompt is **just the edit instruction** — no subject/setting/style block, because the image already carries them.

```
Replace the wine glass with a coffee mug. Keep the woman, the marble countertop, the warm window light, and her pose unchanged.
```

See [`editing-prompting.md`](editing-prompting.md) for the full edit/multi-ref grammar, per-model capability matrix, and preserve/change templates.

---

## Anti-patterns
