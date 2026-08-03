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

Любой нормальный image prompt — это шесть слотов (см. `skills/image-prompt/references/prompt-formula.md`):

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

## Step 6 — Cross-model comparison (same brief, three engines)

Один и тот же 6-part brief даёт сильно разные результаты в DALL-E 3, MJ v6 и Flux 1.1 Pro. Не из-за «качества» модели — у каждой свой acoustic profile. Скилл умеет генерить три параллельные версии одного промпта:

```
/image-prompt compare --models midjourney,dalle3,flux
```

Что меняется per model:

- **DALL-E 3** — лучше всех делает **текст-в-изображении**. Если на cover нужен заголовок книги, лозунг, надпись на табличке — DALL-E 3. У него же лучшая follow-instruction на длинных prompt'ах (он буквально читает каждое предложение). Минусы: рендер слишком «гладкий», editorial-grain не вытягивает; `--ar` игнорирует.
- **MJ v6** — лучше всех делает **painterly / editorial / cinematic**. Если нужна film-grain, magazine-look, Wes Anderson framing — это MJ. Минусы: галлюцинирует текст (любое слово на cover превратит в нечитаемый mock-text), руки/пальцы — vintage-проблема, требует `--no` defensive.
- **Flux 1.1 Pro** — лучше всех делает **photorealism + skin texture + lighting physics**. Если нужно фото-реальный портрет, реалистичное освещение, не «AI face» — это Flux. Минусы: композиционно проще MJ (не вытягивает сложные multi-element scenes), styling reference менее точный.

Side-by-side для одного и того же brief'а («woman in industrial loft, editorial»):

| Term в prompt'е                    | DALL-E 3                        | MJ v6                           | Flux 1.1 Pro                    |
|------------------------------------|---------------------------------|----------------------------------|----------------------------------|
| `--ar 16:9`                        | игнорирует (текст «aspect 16:9» в prompt) | работает напрямую | работает напрямую |
| `--no text logo`                   | игнорирует, не делает text сам  | работает, важно для безопасности | не нужно, photorealism не галлюцинирует слова |
| «editorial magazine»               | даёт generic glossy             | даёт точный editorial-look      | даёт photo-look, не magazine    |
| «35mm film grain»                  | слабый grain, gloss доминирует  | сильный, аутентичный grain      | очень тонкий, photorealistic     |
| «Wes Anderson symmetry»            | понимает framing, не цвет       | понимает framing + colour palette | понимает только framing       |
| named photographer ref             | обрезает имена (safety)         | понимает 200+ имён              | понимает 50+ имён, остальные — generic |
| длинный prompt (60+ слов)          | читает целиком, follows         | читает первые 40 слов, остальное вес 0.3 | читает 80%, остальное 0.5 |
| text-в-изображении («Future of Work» на постере) | работает, читаемо | mock-text, нечитаемо | работает в half, треть случаев |

Practical rule: один brief, три prompt'а, три engine'а. Берёшь лучший. Скилл сохраняет три выхода в `outputs/<topic>-<engine>.txt` — можно вернуться через неделю.

## Step 7 — Refinement loop (v1 не то, что делать)

Первый рендер почти никогда не финальный. Четыре опции, в порядке возрастающей сложности:

```
┌─ v1 не то ─┐
│
├─ маленькая правка (subject прав, style/lighting слегка не туда)
│   → VARY (subtle) в MJ
│   → "edit prompt" в DALL-E 3
│   → small param tweak в Flux
│
├─ Composition правильная, исполнение слабое
│   → UPSCALE (subtle)
│   → или re-roll без изменения prompt'а (RNG fix)
│
├─ Style/lighting сильно не то, subject ОК
│   → VARY (strong) с одной правкой в prompt
│   → или REROLL с swap'ом одного из 6 слотов (style swap, lighting swap)
│
└─ Composition fundamentally wrong (subject не центр, кадр обрезан)
    → новый prompt с пересмотром Subject + Setting
    → не VARY — VARY сохраняет composition, тебе нужна другая
```

Decision tree, словами:

1. **Re-roll** (тот же prompt, новый seed). Бесплатно, быстро. Берёшь когда composition хорошая, но cuts/details сломаны (руки, лицо, текст). 30% случаев фиксит просто новый roll.
2. **Vary subtle** (MJ-специфичный). Берёшь когда image **почти** правильный — одна деталь не та (cup of coffee стоит не там, поза почти-почти). Vary subtle двигает 5-10% пикселей.
3. **Vary strong**. Берёшь когда subject правильный, всё остальное надо переснять. Это самый частый случай.
4. **Add params**. Если style drift'ит — добавь `--stylize 50` (понижение, не повышение!). Если detail теряется — добавь `--style raw`. Если composition слишком safe — добавь `--chaos 25`.
5. **Upscale**. Только когда тебе нравится v1, нужна резкость. Upscale **не** меняет content. Если ждёшь, что upscale «починит» руки — нет, не починит.
6. **Rewrite prompt**. Самая дорогая опция (теряешь 1-3 минуты на пересборку 6 слотов). Делаешь когда ничто из выше не помогло за 3-4 итерации. Часто реальная причина — wrong style anchor (см. Troubleshooting → «Стиль доминирует»).

Правило: не делай больше 4 итераций на один cover. Если за 4 не сошлось — bug в Subject или Setting слое, не в style. Возвращайся к Step 3 и переписывай brief.

## Step 8 — RU brief → EN prompt (полный пример)

Скилл с v1.7 принимает RU brief и сам собирает EN prompt — image generators (особенно MJ и Flux) на EN работают сильно лучше. RU prompt напрямую — это потеря 30-40% understanding.

Worked example. Запуск:

```
/image-prompt "обложка для эссе про тёмную сторону ремоут-работы" \
  --model midjourney --ar 16:9 --lang-input ru
```

RU brief (то, что ты ввёл):

```
Обложка для эссе про тёмную сторону ремоут-работы. Не радостная картинка из
LinkedIn. Тема: изоляция, размытие границ дом/работа, тихая выгораемость.
Один человек, дома, поздний вечер, экран ноутбука — единственный источник
света. Минимально, не дистопия — скорее меланхолия. Стиль — Edward Hopper
встретил Saul Leiter (городское одиночество + цвет).
```

Скилл сначала переводит intent (не пословно), потом собирает 6-part:

```
SUBJECT
A person in their late 30s sitting at a small kitchen table, slightly hunched
over a thin laptop. No headphones, no second screen, no plants. A cold cup
of coffee, half-full, beside the laptop.

SETTING
Small apartment kitchen, 11 PM, all overhead lights off. The laptop screen
is the only light source. A window in the background shows night-city silhouette,
some distant lit windows.

STYLE
Edward Hopper composition (isolated figure, urban interior, geometric framing)
crossed with Saul Leiter colour palette (deep teal, warm amber from screen,
muted reds). Editorial illustration, not photograph.

LIGHTING
Single source — laptop screen, cool 6500K, illuminating face from below at
~30° angle. No fill light. Background falls to deep shadow. Slight cyan
spill on chin and forearms.

CAMERA / LENS
35mm equivalent, slight angle from corner of room (not straight-on), eye-level
with subject, medium-wide shot — includes table, laptop, and window.

TEXTURE / MOOD
Painterly with visible brushwork, muted saturation except for screen-cyan,
melancholic but not despairing. Quiet, not dramatic. Stillness.
```

Final MJ-prompt:

```
A person in their late 30s sitting at a small kitchen table hunched over a
thin laptop, cold half-full cup of coffee beside it, small apartment kitchen
at 11 PM, all overhead lights off, laptop screen as only light source, window
showing night-city silhouette with distant lit windows, Edward Hopper
composition with Saul Leiter colour palette, deep teal and warm amber and
muted reds, editorial illustration, painterly visible brushwork, single light
source from laptop at 30 degrees below face, slight cyan spill on chin and
forearms, 35mm, slight corner angle, eye-level medium-wide shot, melancholic
muted saturation, quiet stillness --ar 16:9 --style raw --stylize 150
--no text logo watermark photograph hands-cropped
```

Что скилл сделал автоматически при RU → EN:

- «тёмная сторона» → не translated literally as «dark side» (cringe). Передал через mood + lighting (single screen-light, deep shadow).
- «Hopper + Leiter» — оставил имена (оба понимаются MJ).
- «не дистопия — меланхолия» — не как negation в prompt'е (MJ плохо парсит negation в free-text), а как direct mood + colour palette.
- «городское одиночество» — не дословно «urban loneliness» (clichéd), а через subject + setting + framing (isolated figure, geometric composition, single light).

Сохрани RU-brief и EN-prompt вместе (скилл делает это автоматически в `outputs/<slug>.brief.md`) — если через месяц захочешь переснять, вернёшься к brief'у, не к prompt'у.

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

MJ меняет defaults между версиями. Скилл версионируется — `skills/image-prompt/references/models/midjourney.md` хранит deltas. Запусти `/image-prompt --model midjourney --version 6.1` если хочешь pin старый стиль.

### Слишком литерально (image буквально иллюстрирует слова prompt'а)

Признак: ты написал «introspective mood», MJ нарисовал женщину с грустным лицом, прижимающую руку к груди. Промпт принят как stage direction, не как atmosphere.

Лечение:

- Убери emotion-words из Subject и Texture/Mood. Передавай настроение через **lighting + composition**, не через «emotional» прилагательные. «Introspective» в Subject → выкинуть. «Single side light, face partially in shadow, gaze off-frame» — то же настроение, не литерально.
- DALL-E 3 особенно склонен к буквализму. Если работаешь с DALL-E, держи atmosphere в lighting/colour, не в mood-словах.

### Hands / fingers сломаны (классика)

Mitigations упомянуты выше (`--no hands-cropped`, medium/wide shot). Дополнительно:

- **MJ v6+** — лучше v5, но не починено. Hands в close-up = ставка 50/50 даже у v6.1.
- **Flux 1.1 Pro** — самые «честные» руки из трёх. Если cover требует видимые руки крупно — переключайся на Flux, не борись с MJ.
- **DALL-E 3** — стилизованные руки (illustration / painterly) — хорошо. Фотореалистичные — те же проблемы что у MJ.
- Универсальный fix — генеришь image без hands в кадре (поза hand-behind-back, hand-out-of-frame, hand-holding-object-that-hides-fingers). Cheating, но работает.

### Текст в изображении превратился в нечитаемое мочало

MJ и Flux галлюцинируют любой текст. «THE FUTURE OF WORK» на cover превратится в `TGE FBTURE OE VORK`. Опции:

- **DALL-E 3** — почти всегда читаемо для коротких слов (≤ 4 слова). Для cover с заголовком — переключайся.
- **MJ + Photoshop** — генеришь image без текста (`--no text`), добавляешь typography руками в Figma/Photoshop. 95% случаев это правильное решение — текст на cover должен быть в проектном font'е, не в AI-mock'е.
- **Flux** — лучше MJ, хуже DALL-E. Работает для слов ≤ 6 букв, длиннее — fail.

### Style drift (style anchor «утёк» в неожиданные места)

Признак: указал «Wes Anderson framing», получил Wes Anderson framing **и** Wes Anderson colour palette (пастельные розовые-голубые) **и** Wes Anderson typography. Один anchor — три эффекта, два из которых ты не заказывал.

Лечение:

- Сужай anchor. Не «Wes Anderson», а «Wes Anderson **symmetry**» или «Wes Anderson **framing**, **not colour**». Скилл умеет генерить scoped reference: `--ref-style "wes-anderson:framing-only"`.
- Используй conflicting anchors как противовес. «Wes Anderson framing + Roger Deakins colour» — framing берётся от первого, colour от второго.
- В крайнем случае — `--no pastel` если ты получил pastel'ный палитру без запроса.

### Watermark / signature случайно видимый

MJ иногда генерит fake signatures в углу (имитация artist signature). Flux иногда штампует quasi-watermark на photorealistic. Лечение:

- `--no signature watermark stamp` — defensive prefix
- В DALL-E 3 — после генерации Adobe Express / Photoshop remove (модель сама не уберёт)
- Если повторяется на одном subject'е — твой Style anchor намекает на «professional photograph», в котором watermark естественен. Убери reference, измени Style на «editorial illustration» или «conceptual photography» (без слова `photograph` голого).

## Related

- [video-prompt-reel.md](video-prompt-reel.md) — родственная задача, но для motion
- [landing-launch.md](landing-launch.md) — куда эта cover, скорее всего, ляжет
- [viral-post.md](viral-post.md) — если cover для соц-поста, не для блога
- [skills/image-prompt/references/prompt-formula.md](../../skills/image-prompt/references/prompt-formula.md) — полная 6-part formula с примерами
