---
title: "Generate a Midjourney prompt for a blog cover"
persona: "Content marketer needing a hero image"
time: "3-5 minutes"
skills:
  - image-prompt
---

# A Midjourney prompt for a "Future of Work" blog cover

Сценарий: статья готова, нужна cover image — hero illustration для блога и OpenGraph. Хочется не stock-photo и не generic «AI art» с пятью пальцами. Тема — «future of work». Generator — Midjourney v6 (по дефолту). 16:9 для блога, 1.91:1 для OG.

Это работа для `image-prompt`. Скилл собирает по 6-part formula и добавляет model-specific flags.

## Intent — 6-part formula

Любой нормальный image prompt — это шесть слотов (см. `image-prompt/references/formula.md`):

1. **Subject** — что в кадре, конкретно. Не «person», а «a woman in her 40s, silver glasses, denim shirt».
2. **Setting** — где это происходит. Не «office», а «glass-walled coworking space at golden hour, plants spilling over the divider».
3. **Style** — визуальный жанр. «Editorial photography», «isometric illustration», «soft watercolour», «cinematic still».
4. **Lighting** — направление и качество света. «Backlit, warm rim light», «overcast diffused», «harsh midday shadows».
5. **Camera / lens** — какой объектив бы это снял (даже если illustration). «35mm, shallow DoF», «wide-angle 24mm, slight distortion», «macro 100mm».
6. **Texture / mood** — грану, surface quality, эмоциональный тон. «Film grain, slight teal-orange grade», «matte finish, muted palette».

Без хотя бы 5 из 6 слотов промпт даёт generic результат.

## Setup

Скилл установлен. Поддерживает per-model deltas (MJ, DALL-E 3, Flux, Nano Banana, SD). Параметр `--model` определяет суффиксы и доступные flags.

## Step 1. Invoke with the brief

```
/image-prompt "blog cover for a 'future of work' article" --model midjourney --ar 16:9
```

Скилл задаёт 3 уточнения (без них generic):

```
1. Mood — optimistic / ambivalent / dystopian / neutral-documentary?
2. People in frame — yes (how many, who) / no (object-only / environment-only)?
3. Aesthetic anchor — name one reference (photographer / illustrator / movie still / magazine)?
```

Если skip — выдаст generic. Если ответил specific — выдаст узкий prompt.

## Step 2. Concrete brief

Answers:

1. Mood — **ambivalent**. Не утопия, не дистопия. Зрелое «всё сложнее, чем мы думали».
2. People — **one person**, mid-30s, working alone in non-office environment.
3. Anchor — **Wes Anderson framing + Annie Leibovitz lighting**, editorial magazine spread.

## Step 3. The 6-part build

Скилл собирает prompt:

```
SUBJECT
A woman in her mid-30s sits cross-legged on a wooden floor with a thin
laptop, no desk, no chair, one cup of black coffee beside her.

SETTING
Empty industrial loft, exposed brick, single tall window letting in slanted
afternoon light. Power cables snake across the floor. No other furniture.

STYLE
Editorial magazine photography, Wes Anderson symmetry, Annie Leibovitz
lighting precision.

LIGHTING
Backlit from the window, warm late-afternoon rim light on her shoulders,
soft fill on her face from a reflective wall.

CAMERA / LENS
50mm prime, eye-level, shallow depth of field, subject perfectly centred.

TEXTURE / MOOD
Slight film grain, muted earth-tone palette (warm beige, cool brick red,
charcoal), introspective, neither hopeful nor bleak.
```

## Step 4. The MJ-final prompt (one-line)

Скилл компонует в Midjourney v6 syntax:

```
A woman in her mid-30s sitting cross-legged on a wooden floor with a thin
laptop, no desk no chair, one cup of black coffee beside her, empty industrial
loft, exposed brick, tall window with slanted afternoon light, power cables
across the floor, editorial magazine photography, Wes Anderson symmetry,
Annie Leibovitz lighting precision, backlit warm rim light on shoulders,
soft fill on face, 50mm prime, eye-level, shallow depth of field, subject
centred, slight film grain, muted earth-tone palette, introspective mood
--ar 16:9 --style raw --no text logo watermark hands-cropped fisheye
```

Flag breakdown:

- `--ar 16:9` — blog hero ratio (для OG переключи на `--ar 1.91:1`)
- `--style raw` — выключает MJ's default beautification, держит editorial look
- `--no text logo watermark` — defensive against MJ's text hallucinations
- `--no hands-cropped` — defensive against MJ cropping hands in mid-frame
- `--no fisheye` — anchor против wide-distortion default

Параметры `--stylize` / `--chaos` / `--weird` скилл по дефолту не ставит — они шумят. Добавь руками если хочешь больше randomness.

## Step 5. Variations

Скилл может выдать 3-4 варианта с фиксированным subject но разным style/lighting (для A/B на cover):

```
/image-prompt variations 4 --model midjourney
```

Каждый variant отличается одним из 6 слотов (style swap / lighting swap / setting swap). Это даёт ощутимо разные изображения для тестирования.

## Per-model deltas

Если ты используешь не MJ:

- **DALL-E 3** — `--ar` не работает; добавь «aspect ratio 16:9» в текст. Не любит negative prompts; убери `--no ...`.
- **Flux** — `--ar` работает; lighting описывать развёрнуто (Flux любит длинные prompts).
- **Nano Banana** — сильно меньше структуры; вторая половина prompt'а часто игнорируется. Держи под 50 слов.
- **Stable Diffusion** — negative prompt отдельным параметром, не через `--no`.

Скилл переключает синтаксис автоматически по `--model`.

## Когда НЕ использовать image-prompt

- **Простой stock-style photo** — Unsplash / Pexels быстрее и бесплатно.
- **Логотип / brand identity** — image generators плохо работают с typography и vector. Иди в Figma.
- **Технический diagram** — Mermaid / Excalidraw / руками. Image generators галлюцинируют схемы.
- **Photorealistic портрет реального человека** — права + ethical issues. Скилл откажется генерить prompts с named real people в photorealistic styles.

## Troubleshooting

### Midjourney продолжает рисовать generic «professional woman with laptop»

Скорее всего слабая subject specificity. Добавь возраст, одежду, позу, accessory — каждая деталь сужает. «A woman with a laptop» = stock. «A woman in her mid-30s, silver glasses, denim shirt, sitting cross-legged on a wooden floor with no desk, one cup of black coffee beside her» = unique.

### Hands / faces broken

Это MJ baseline issue, не prompt issue. Mitigations:

- держи subject в medium / wide shot (не close-up на руки)
- добавь `--no hands-cropped` (помогает 60%)
- если crucial — генерируй и потом fix in Photoshop / Generative Fill

### Стиль доминирует над subject

Убери одну style anchor. «Wes Anderson + Annie Leibovitz + editorial magazine» — три anchor'а одновременно. Оставь два. Скилл может вернуть три по дефолту, но это часто слишком сильный pull.

### Промпт работал, потом перестал (после MJ version bump)

MJ меняет defaults между версиями. Скилл версионируется — `image-prompt/references/midjourney-versions.md` хранит deltas. Запусти `/image-prompt --model midjourney --version 6.1` если хочешь pin старый стиль.

## Related

- [video-prompt-reel.md](video-prompt-reel.md) — родственная задача, но для motion
- [landing-launch.md](landing-launch.md) — куда эта cover, скорее всего, ляжет
- [viral-post.md](viral-post.md) — если cover для соц-поста, не для блога
- [image-prompt/references/formula.md](../../image-prompt/references/formula.md) — полная 6-part formula с примерами
