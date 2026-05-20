# Lighting vocabulary

The single highest-leverage modifier for photorealistic prompts. Always specify: **source + direction + quality**.

---

## Portrait lighting

### By light position (relative to subject)

| Position | Effect | Use when |
|---|---|---|
| **Key from upper-left/right** | Classic portrait look | Default; works for most subjects |
| **Rim light** (from behind) | Highlights edges | Cinematic, dramatic separation from background |
| **Backlight** (full backlit) | Silhouette + halo | Sunset, golden hour, mystery |
| **Split lighting** (90° side) | Half-lit face | Mood, drama, "noir" |
| **Rembrandt lighting** | Light from above + side, creates triangle of light on far cheek | Classic painterly portrait |
| **Butterfly lighting** | Light straight on, from above, slight shadow under nose | Beauty / fashion shots |
| **Loop lighting** | Slight side, soft shadow loops under nose | Natural everyday portraits |
| **Front flat** | Light straight on, no shadows | Avoid — looks like passport photo |

### By light quality

| Quality | Look | Example phrasing |
|---|---|---|
| **Hard light** | Sharp shadows, defined edges | "Hard noon sun casting sharp shadows" |
| **Soft light** | Smooth gradients, soft shadows | "Soft diffused light through sheer curtains" |
| **Diffused** | Spread evenly, low contrast | "Overcast diffused light, no harsh shadows" |
| **Specular** | Bright highlights on glossy surfaces | "Specular highlights catching metal edges" |

### Natural light timings (for portrait + scene)

| Time | Phrasing | Mood |
|---|---|---|
| **Golden hour** | "golden hour backlight", "warm late afternoon glow", "long shadows" | Romantic, hopeful |
| **Blue hour** | "blue hour twilight", "deep blue ambient with warm accent lights" | Melancholy, urban |
| **Magic hour** | Either golden or blue, transitional | Cinematic |
| **High noon** | "direct overhead sunlight, hard shadows" | Stark, exposed |
| **Overcast** | "overcast diffused light, flat shadows" | Documentary, even |
| **Pre-dawn** | "pre-dawn cool ambient, no shadows yet" | Quiet, introspective |
| **Midnight** | "moonlit, deep shadows, single warm window glow" | Mystery, solitude |

---

## Scene lighting (interior + exterior)

### Light sources to name explicitly

✅ Always name the specific source:
- "neon signs casting magenta glow from the right"
- "single flickering fluorescent overhead, harsh greenish cast"
- "LED panel from below illuminating the keyboard"
- "candlelight from a single source, warm orange tones"
- "TV screen flicker casting blue light across the room"
- "phone screen glow lighting one face"
- "car headlights cutting through fog from background"
- "fire pit warm flicker on faces from below"

❌ Avoid abstract:
- "dramatic lighting"
- "moody lighting"
- "cinematic lighting"
- "great atmosphere"

The abstract terms produce generic output. The named sources commit the model.

### Multi-source setups

For complex scenes, name 2-3 sources and how they interact:
- "Window backlight from upper-left + warm tungsten table lamp from right + faint TV glow in background"
- "Neon sign magenta key from right + cool moonlight blue fill from upper-left + faint streetlamp warm tones on wet pavement"

---

## Photographic terms

### Depth of field

- **Shallow depth of field**: subject sharp, background blurred. Add "f/1.8" or "f/2.8" for aperture.
- **Deep depth of field**: everything sharp. Add "f/8" or "f/11".
- **Soft bokeh**: pleasing out-of-focus highlights
- **Rack focus**: shift from one focus plane to another (mostly video — but useful note)

### Quality of focus

- "sharp focus on {subject}"
- "razor-sharp eyes" (portrait)
- "tack-sharp" (general sharpness)
- "soft focus on background" (intentional blur)

### Color quality

- "cinematic color grading" — film-like
- "teal-and-orange" — popular cinematic grade
- "warm color cast" / "cool color cast"
- "muted saturation" / "vibrant saturation"
- "desaturated" — film noir feel
- "monochromatic" — single dominant color
- "high contrast" / "low contrast"

---

## Abstract / illustration lighting

Less critical (model is not trying to be photographic), but still useful:

- "soft glow from within the shapes"
- "ambient light, no defined source"
- "luminescent edges"
- "subtle vignette darkening the corners"
- "even lighting, no shadows"
- "high key — bright and airy"
- "low key — dark with selective highlights"

---

## Atmospheric particles (advanced)

Adding particles in light makes scenes feel 10x more cinematic:

- "individual dust motes visible in the light beam"
- "smoke wafting through the light"
- "rain reflecting the light"
- "snowflakes catching the light"
- "morning mist diffusing the light"
- "humidity haze in the warm air"

---

## Templates for common scenarios

### Cozy interior

> "Warm golden hour backlight through window, soft ambient fill, single warm pendant lamp creating amber pool on the table, individual dust motes visible in the beam"

### Tech / cyberpunk

> "Neon magenta and cyan signs from above and right, single warm LED accent from below, wet pavement reflecting all light sources, faint atmospheric haze"

### Editorial portrait

> "Soft directional key light from upper-left through diffusion, gentle rim light catching the hair, neutral fill bouncing soft warmth back to the face"

### Stark / minimalist

> "Single overhead source, hard shadow on the wall behind, no fill, low key"

### Documentary / candid

> "Available natural light only, mixed window light + practical tungsten lamp, slight imperfection — no studio polish"

### Cinematic action

> "Hard key from camera-right backlight + cool blue fill on shadow side + faint warm bounce from below, atmospheric haze through the beams, anamorphic flare"

---

## Anti-patterns

❌ Multiple light source words without specifying which is dominant:
> "Backlight, sidelight, ambient, key, fill, rim, golden hour, blue hour"
The model picks one randomly. Pick ONE primary + 1-2 supporting.

❌ Quality words without source:
> "Cinematic professional dramatic moody"
No specific look. Replace with named sources + named quality.

❌ Lights that don't physically make sense:
> "Sunlight at night"
> "Backlight from below"
Model produces broken physics.

✅ Always commit to a specific configuration:
> "Single street lamp casting hard sodium-vapor warmth across the figure, deep shadows on the dry-cleaner's wall behind"

---

## RU терминология

Промпт всё равно лучше писать на английском — модели обучены преимущественно на EN-датасете. Эта секция нужна для двух кейсов: (1) пользователь даёт ТЗ на русском, и нужно понять, какой EN-термин подставить; (2) пользователь явно просит RU-промпт (редко — обычно для DALL-E 3 / Flux в режиме natural language).

### Свет — RU → EN маппинг

| RU термин | EN equivalent | Когда использовать |
|---|---|---|
| Контровой / контражур | rim light, backlight | Подсветка краёв силуэта сзади |
| Заполняющий / заливка | fill light | Подсветка теневой стороны |
| Рисующий / ключевой | key light | Основной источник, формирующий объём |
| Мягкий рассеянный | soft diffused | Через тюль, шторы, облака |
| Жёсткий направленный | hard directional | Полуденное солнце, прожектор |
| Тёплый ламповый / вольфрам | warm tungsten | Лампы накаливания, домашний свет |
| Холодный люминесцентный | cool fluorescent | Офисы, гаражи, морги |
| Неоновая подсветка | neon glow | Cyberpunk, ночной город |
| Свечной свет | candlelight | Романтическая, интимная сцена |
| Свет монитора / экрана | screen glow, monitor glow | Tech-сцена, ночь за работой |
| Лунный свет | moonlight | Ночные сцены |
| Контровой против солнца | sun-backlight, lens flare | Силуэт против солнца |

### Время суток

| RU | EN |
|---|---|
| Золотой час | golden hour |
| Синий час / сумерки | blue hour, twilight |
| Магический час | magic hour |
| Предрассветный | pre-dawn |
| Полдень / жёсткое полуденное | high noon, hard noon |
| Пасмурный | overcast |
| Ночь / полночь | moonlit, midnight |

### Качество света

| RU | EN |
|---|---|
| Высокий ключ / светло | high key |
| Низкий ключ / темно с акцентами | low key |
| Виньетирование | vignette |
| Боке | bokeh |
| Резкая глубина / всё резко | deep depth of field |
| Малая глубина / размытие | shallow depth of field |
| Сильный контраст | high contrast |
| Десатурация / приглушённые цвета | desaturated, muted saturation |
| Тёплый оттенок | warm color cast |
| Холодный оттенок | cool color cast |
| Кинематографический грейдинг | cinematic color grading |
| Тиал-оранж | teal-and-orange grade |

### Ракурс / положение камеры (если пользователь смешивает в одну строку с lighting)

| RU | EN |
|---|---|
| Низкий ракурс / снизу вверх | low angle, worm's-eye view |
| Высокий ракурс / сверху | high angle, bird's-eye view |
| Вид от первого лица | POV, first-person view |
| С уровня глаз | eye level |
| Голландский угол | Dutch angle |
| Крупный план | close-up |
| Средний план | medium shot |
| Общий план | wide shot |

### Когда оставлять RU в промпте

Только если:
- модель — DALL-E 3 (понимает RU прилично, но без deep-style-tags);
- сцена — российская/этно-специфичная («бабушкина квартира в хрущёвке», «двор в Воркуте», «троллейбус в Питере») — модели иногда лучше извлекают культурный контекст по RU-словам, чем по EN-переводу.

Во всех остальных случаях — переводить на EN по таблицам выше.
