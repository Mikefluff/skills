# image-prompt — calibration before/after pairs

Five paired examples covering portrait, product, scene, abstract, illustration. Each shows a weak prompt and the rewrite this skill should produce.

---

## Example 1 — Portrait

### Before (weak)

```
A businesswoman in an office, professional look, high quality
```

### After (Midjourney v6)

```
A confident woman in her thirties leaning on a polished white marble countertop in a sunlit Brooklyn loft kitchen at golden hour, editorial photo, soft directional key light from upper-left window, gentle rim light catching the hair, 85mm lens f/1.8, full-frame DSLR, natural skin texture, visible pores, individual hair strands, realistic linen fabric with soft creases, sharp focus on eyes, 8K, cinematic color grading --ar 4:5 --s 250 --style raw --no text, watermark, distorted anatomy, plastic skin
```

### Deltas applied

- "businesswoman" → "confident woman in her thirties" (specific)
- "in an office" → "leaning on polished white marble countertop in a sunlit Brooklyn loft kitchen" (setting + pose)
- "professional look" → editorial photo style (concrete style tag)
- "high quality" → 8K + cinematic color grading + sharp focus + visible pores (specific quality tags)
- Added lighting: golden hour, key light direction, rim light
- Added camera: 85mm f/1.8, full-frame DSLR
- Added texture: skin pores, fabric details
- Added MJ-specific params: `--ar 4:5`, `--style raw`, `--no` negative

---

## Example 2 — Product

### Before (weak)

```
Wireless earbuds case product shot
```

### After (Flux Pro)

```
Minimalist product photo of a brushed-aluminum wireless earbuds case on white Carrara marble surface, soft directional sunlight from upper-right, subtle reflections in the marble polish, 50mm lens f/4, 8K, commercial advertising style, photorealistic, realistic brushed metal grain, subtle shadow under the case, depth in the soft white background, sharp focus
```

Negative:
```
text, watermark, logo, scratched, dented, generic stock background, blurry, low resolution, distorted reflections
```

### Deltas applied

- Generic "product shot" → "minimalist product photo" + specific surface ("white Carrara marble")
- Specified lighting direction and source
- Added lens (50mm) and aperture (f/4) — product needs deep enough DOF
- Specified material texture ("brushed metal grain")
- Added shadow + background depth notes
- Added Flux-appropriate negative prompt

---

## Example 3 — Scene

### Before (weak)

```
Cozy cafe interior
```

### After (DALL-E 3)

```
A cozy café interior at golden hour, one woman in her thirties reading a book at a window table in soft focus background, editorial photo style with cinematic color grading. Lighting: warm golden hour backlight from the window casting long amber rays, soft ambient fill from a warm pendant lamp above her table, individual dust motes visible in the light beam. Camera: shot with 35mm lens at f/2.8 on a full-frame mirrorless camera, shallow depth of field, sharp focus on her hands and book. Texture: worn brown leather chair with creases, steam rising from a white ceramic mug, condensation on the window glass, soft wooden floor in the background. Aspect ratio: widescreen 16:9. Avoid: text, watermarks, distorted anatomy, plastic skin, sterile clean stock-photo aesthetic.
```

### Deltas applied

- "Cozy" → specific time + specific subject (woman reading at window)
- Added 3 named light sources (window, pendant, dust motes)
- Added camera body type (mirrorless) + lens + aperture
- Added 4 tactile details (leather creases, steam, condensation, wooden floor)
- DALL-E natural-language negative ("avoid... sterile stock-photo aesthetic")

---

## Example 4 — Abstract / background

### Before (weak)

```
Gradient background, nice colors
```

### After (Midjourney v6)

```
Abstract gradient background with flowing organic shapes, purple to blue transitioning into soft pink at the edges, minimal design with gentle motion blur, smooth gradients with no banding, high resolution, soft luminescent glow within the shapes --ar 16:9 --s 400 --no banding, text, harsh transitions
```

### Deltas applied

- "Gradient" → "abstract gradient with flowing organic shapes" (form)
- "Nice colors" → explicit palette (purple→blue→pink)
- Added technical quality ("no banding") — gradient art's biggest failure mode
- Added MJ `--s 400` for higher stylization (abstract benefits from MJ's creative side)
- Added negative ("banding") — the specific risk for this image type

---

## Example 5 — Illustration

### Before (weak)

```
Lighthouse illustration, watercolor
```

### After (Midjourney v6)

```
A solitary lighthouse on a windswept cliff at dawn, watercolor illustration with ink outline accents, loose composition with the lighthouse off-center on the right, muted warm palette — peach, mauve, soft slate blue, single warm light glowing from the top of the lighthouse, distant gulls in the wash of the sky, visible paper texture, soft watercolor bleed at the edges, hand-painted quality with subtle white space, high resolution --ar 3:2 --s 350 --style raw --no oversaturated, photorealistic, 3D rendered
```

### Deltas applied

- "Lighthouse illustration" → specific scene (cliff at dawn, off-center lighthouse, gulls)
- "Watercolor" → "watercolor illustration with ink outline accents" (technique combination)
- Added explicit palette (peach, mauve, slate)
- Added paper / bleed / hand-painted texture (the watercolor giveaway)
- Skipped camera tags (illustration, not photo)
- Added `--style raw` to keep MJ from over-styling
- Negative: removed photorealism and 3D (would conflict with watercolor)

---

## Pattern summary

The strong-prompt formula reliably wins:

1. **Specific subject + action** (not "professional", "nice", "cool")
2. **Specific setting** (time, place, era)
3. **Single style commitment** (editorial photo OR watercolor — never both)
4. **Named lighting sources + direction + quality** (not "good lighting" or "dramatic lighting")
5. **Lens + aperture + camera body** (when photo) OR skip (when illustration)
6. **Texture + materials** (the realism / craftsmanship layer)
7. **Model-specific syntax**: MJ params, DALL-E natural language, Flux negative
8. **Negative prompt** addressing the specific image's failure modes

Average word count of the weak prompts above: 4-6 words. Of the strong prompts: 40-80 words. The model needs the specificity to commit; vague input produces vague output.

---

## Example 6 (RU) — Обложка для статьи в RU-блоге

### Контекст

Пользователь пишет статью на русском про выгорание у разработчиков и просит обложку. Целевая площадка — RU-блог / Telegra.ph, формат 16:9. ТЗ от автора на русском: «обложка для лонгрида про выгорание программиста, что-то атмосферное, не баянное, не клавиатура с черепом, не human-with-laptop-stock».

### До (weak — то, как пользователь обычно сразу отдаёт модели)

```
Обложка для статьи про выгорание программиста, атмосферно
```

What's wrong:
- Жанр на RU, остальная модель ждёт EN-tags
- «Атмосферно» — пустое слово, как "good vibes"
- Нет subject, setting, lighting, camera, texture
- Нет negative — почти гарантированно вылезет «human + laptop» стоковый кадр

### После (Midjourney v6)

```
A solitary man in his thirties sitting on the edge of his unmade bed at 4 AM, monitor in the background still glowing with unfinished code, head bowed, hands resting limp on his knees, editorial documentary photo, low-key lighting — only the cold blue monitor glow from camera-right and a faint warm streetlamp through a half-curtained window from camera-left, 35mm lens f/1.8, full-frame mirrorless, shallow depth of field with sharp focus on his hands, natural skin texture with visible stubble and tired under-eye shadows, crumpled sheets in foreground, scattered coffee cup on the floor, muted desaturated color palette with teal-and-blue cast, cinematic color grading --ar 16:9 --s 250 --style raw --no laptop with skull, generic office, plastic skin, stock photo aesthetic, hopeful expression, sunshine
```

Negative (если модель поддерживает отдельным полем — Flux / SDXL):
```
laptop, keyboard, skull, generic office, stock photo, smiling face, business suit, daylight, sunshine, hopeful, multiple people, text, watermark
```

### Применённые дельты

- «Программист» → «солитарный мужчина 30+ на краю незастеленной постели в 4 утра» (specific scene вместо абстракции)
- «Атмосферно» → конкретный low-key + два названных источника света (cold monitor glow + faint streetlamp through curtain) + направление каждого
- Добавлены EN-теги по таблице из `lighting-vocabulary.md` § RU терминология: «холодный люминесцентный» → cold blue monitor glow; «тёплый ламповый» → warm streetlamp; «низкий ключ» → low-key
- Добавлены camera-теги (35mm f/1.8, full-frame mirrorless) — обложка должна выглядеть как editorial photo, не cartoon
- Texture: stubble, tired under-eye, crumpled sheets — добавляет «выгорание» через тело, не через метафору с черепом
- Negative addresses конкретный риск: «not laptop with skull, not generic office, not hopeful» — три самых частых fallback'а модели для тэга «burnout»
- MJ params: `--ar 16:9` для обложки лонгрида, `--style raw` чтобы убрать MJ-перестилизацию
- Промпт остался на EN — модель парсит точнее; RU был только в ТЗ от автора

---

## Example 7 — Text-in-image (poster)

### Before (weak)

```
Conference poster about AI ethics
```

What's wrong:
- No subject anchor
- No layout, no copy, no style
- Default models (MJ / Flux) butcher anything beyond 5 words

### After (Ideogram 3 Quality)

```
A minimalist editorial conference poster, vertical 2:3, deep navy background with a single warm spotlight from upper-left. Layout: large display-serif title centered upper-third reads "RESPONSIBLE AI". Below in smaller sans-serif: "Ethics Summit — November 14-16, 2026 — San Francisco". A subtle line illustration of a human silhouette and a digital silhouette overlapping in muted gold sits below the type. Bottom-right corner sans-serif tag: "ai-ethics-summit.com". High-contrast type. Soft paper-grain texture. Editorial / Pentagram-style restraint. Sharp focus on type.
```

### Deltas applied

- Specified the EXACT copy in the prompt (Ideogram 3 Quality reliably renders multi-line typography)
- Named the layout (title position, body position, tag position) — Ideogram parses spatial language
- Chose Ideogram 3 over Midjourney: legible text > "wow" factor for this use case
- Style anchor: "editorial / Pentagram-style restraint" gives a brand-design feel
- No `--ar` flag — Ideogram uses an API ratio parameter, not Midjourney syntax
- See `references/text-in-image.md` for which models can render which text lengths

---

## Example 8 — Edit + character consistency (Flux Kontext)

### Before (weak)

```
Make her dress red instead of blue
```

What's wrong:
- Doesn't tell the model what to preserve — model may "regenerate" the woman
- No source-image input flagged
- No preserve-list

### After (Flux Kontext)

Source image attached: portrait of a woman in a blue dress, sunlit Brooklyn loft kitchen.

```
Replace the dress with a deep crimson red dress of the same cut and length. Keep the woman's face, hair, pose, hands, the marble countertop, the kitchen background, and the warm window lighting unchanged.
```

### Deltas applied

- Kontext deviation: no 6-part formula — the source image carries subject / setting / style / lighting. Prompt = JUST the edit.
- Explicit preserve-list ("face, hair, pose, hands, countertop, background, lighting") — Kontext keys off this
- Specified the new attribute precisely ("deep crimson red, same cut and length") not just "red"
- See `references/editing-prompting.md` § Flux Kontext

For Nano Banana Pro the same edit is multi-turn in Gemini chat: generate base image, then "now make her dress crimson red, keep everything else".

---

## Example 9 — Multi-reference composite (Seedream 4.5)

### Before (weak)

```
Combine these three images into one
```

What's wrong:
- No roles assigned to refs (which ref is character? style? palette?)
- No weights
- No description of what the final scene IS

### After (Seedream 4.5)

References attached:
- `ref:character` — portrait of a woman in her thirties (weight 1.0)
- `ref:product` — a brushed-aluminum wireless earbuds case (weight 0.85)
- `ref:style` — a Vogue product editorial spread (weight 0.7)
- `ref:palette` — muted teal-and-orange swatch (weight 0.6)

```
[ref:character@1.0] holding [ref:product@0.85], styled per [ref:style@0.7], on [ref:palette@0.6] background. Editorial product portrait, soft directional studio light from upper-right, 50mm f/4, full-frame mirrorless, natural skin texture, brushed-metal grain on the product, sharp focus on the product in her hand, shallow depth of field on her face.
```

### Deltas applied

- Each ref assigned an explicit role (character / product / style / palette)
- Weights set per Seedream 4.5's role hierarchy (Character 1.0 — non-negotiable identity; Style 0.7 — guide, not lock)
- Prompt describes what the refs do NOT carry: action ("holding"), composition ("editorial product portrait"), lens, lighting
- Prompt does NOT re-describe the character's face / hair (locked by ref) or the product's metal (locked by ref)
- See `references/editing-prompting.md` § Multi-reference composition

For Flux 2 Pro multi-ref (≤10 refs) the syntax is similar; for gpt-image-2 the model handles up to 16 refs and infers roles from context.

---

## Example 10 — Open-weights + multilingual text (Qwen-Image 2.0)

### Before (weak)

```
Storefront sign in Chinese and English
```

What's wrong:
- No business name, no layout
- Midjourney / Flux / SDXL produce gibberish for non-Latin scripts
- No setting

### After (Qwen-Image 2.0)

```
A photorealistic photo of a small tea shop storefront in a Shanghai longtang at dusk. The wooden hanging sign above the door reads, in vertical Chinese calligraphy on the right: "茶馆", and in horizontal sans-serif English below: "STILL HOURS TEA". The shop window is warmly lit from inside; a soft amber paper lantern hangs beside the door. Wet cobblestone reflections of warm window light in the foreground. Editorial documentary photo, 35mm f/2.8, full-frame mirrorless, sharp focus on the sign, shallow depth of field on the background alley.
```

### Deltas applied

- Chose Qwen-Image 2.0: Apache-2.0 open-weights, native 2K, best in class for CJK + Latin mixed typography. SDXL / Midjourney would render the Chinese as nonsense glyphs.
- Specified EXACT copy and exact script for each line ("vertical Chinese calligraphy: 茶馆" / "horizontal sans-serif English: STILL HOURS TEA") — Qwen parses script + orientation hints
- Setting carries the cultural context (Shanghai longtang) so the model anchors the typography in the right visual culture
- Kept full 6-part formula because this is T2I, not edit
- See `references/text-in-image.md` § Multilingual rendering and `references/models/open-source.md` § Qwen-Image 2.0
