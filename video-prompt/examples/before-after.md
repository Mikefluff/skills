# video-prompt — calibration before/after pairs

Five paired examples covering hook, tension, breathing, POV, and timelapse shots. Each shows a weak prompt and the rewrite this skill should produce.

---

## Example 1 — Hook shot (confrontation)

### Before (weak)

```
A woman shouts at a man across a table. Camera zooms in.
```

What's wrong:
- Single-instance verb ("shouts") → frozen mouth
- No beat structure → model picks ONE pose
- Camera-first ("Camera zooms in") → frozen character
- No reactor description → man is a statue
- Generic camera ("zooms in")

### After (Kling 3.0)

```
First [0-1.5s]: She lunges forward in her chair, mouth opening wide as she begins shouting, jaw moving continuously, finger stabbing the air in 2-3 sharp jabs toward him, never fully returning to rest.

Then [1.5-4s]: The man across the table flinches at the first jab, shifts weight backward, jaw tightens, throat working in one visible swallow; she escalates — voice cracking on a second word, head shaking with each word burst, chest heaving with adrenaline.

Finally [4-6s]: She holds the final jab in place, finger inches from his face, shoulders rising and falling with sharp breath; he has dropped his gaze to the table, fingers tightening around the edge.

Lighting: warm tungsten candle from below illuminating both faces, dim ambient from a single pendant lamp overhead, the candle flame flickering slightly with her breath.

Texture: linen tablecloth shifts under her hand, individual hair strands catching the candlelight, fine droplets of sweat on his temple.

Camera: crash zoom into her face in the first 0.5 seconds, then handheld vibration locked tight on the gap between their faces, focus on her finger.
```

### Deltas applied

- Single "shouts" → repeated jaw/mouth/throat motion across 3 beats
- Added reactor (the man) with body detail in EACH beat
- Camera last (one sentence at the end)
- Hook-shot camera: crash zoom in the first 0.5s (per pacing rules)
- Named lighting sources with direction
- Tactile texture (tablecloth, hair, sweat)
- Kling temporal format: "First [0-1.5s]... Then [1.5-4s]... Finally [4-6s]"

---

## Example 2 — Tension hold (intimate moment)

### Before (weak)

```
Two people sit close, looking at each other. Slow romantic camera.
```

What's wrong:
- "Looking at each other" → synchronised statues
- Two characters merged
- Generic "slow romantic camera"
- No body detail

### After (Veo 3)

```
Beat 1: She slowly turns her face toward his, gaze locking on his eyes; her breath visibly catches once, lips parting slightly.

Beat 2: He holds eye contact, throat working in one slow swallow; she leans incrementally closer, her shoulders softening, a single piece of hair falling forward over her cheek.

Beat 3: He raises his hand slowly toward her face but stops halfway, hand suspended, both of them holding still except for breath; her eyes close briefly, then open.

Lighting: warm tungsten table-lamp from camera-right casting amber on both faces, soft cool ambient fill from a single distant window.

Camera: slow dolly push-in across the gap between them, subtle handheld vibration, rack focus from her eyes to his at Beat 3.
```

### Deltas applied

- "Looking at each other" → each character described separately in each beat
- Added micro-actions (breath catching, hair falling, hand suspending)
- "Slow romantic" → specific camera (slow dolly push-in + rack focus)
- Two named light sources with direction
- Rack focus motivated by the beat structure (shift at Beat 3)

---

## Example 3 — Breathing / resolution (alone)

### Before (weak)

```
He sits alone, sad, after the argument. Slow shot.
```

What's wrong:
- "Sad" — not a body description
- "Slow shot" — generic
- No micro-action to prevent frozen-pose output
- No environment for context

### After (Sora)

```
He sits alone at the table after she has left, his hand still resting on the empty wine glass. In the first moments, his gaze stays fixed on the glass, eyes unblinking. His chest rises and falls visibly in slow, controlled breaths — 2-3 full cycles during the shot. At the midpoint, his fingers tighten slightly around the stem and then release, the small motion repeating once more before he finally lets go. As the shot ends, his eyes drift toward the empty chair across from him; his jaw loosens, lips parting slightly.

Throughout: the candle on the table flickers irregularly, casting moving warm light across his face. A draft from a distant window stirs his hair faintly. The pendant lamp above casts a steady dim glow.

Camera: slow dolly pull-back across the table, subtle handheld vibration, focus locked on his hand on the glass.
```

### Deltas applied

- "Sad" → specific body description (unblinking gaze, breath cycles, fingers tightening then releasing)
- Repeated motion pattern ("repeats once more") prevents frozen
- Environment described (candle flicker, draft, pendant lamp)
- Camera matches breathing-mode pacing (slow pull-back, not aggressive)
- Sora-style narrative paragraph (no rigid beat markers needed)

---

## Example 4 — POV shot (action)

### Before (weak)

```
First person view of someone kiteboarding fast across water.
```

What's wrong:
- No POV body sensation
- Generic "fast"
- No physics for the equipment
- No environment interaction

### After (Kling 3.0)

```
First [0-2s]: POV first-person view from inside the kiteboarder's body — both arms gripping the control bar pulled hard right, kite-lines visibly taut and vibrating with tension, kite-bar trembling in the hands; body weight low and rotated toward the kite, hips angled into the carve.

Then [2-5s]: The water surface rises fast as the board cuts hard — edge angle visible at the bottom of frame, fanned water spray traveling across the right side of the field of view, individual droplets catching sunlight; the horizon tilts about 15° to the right with the carve.

Finally [5-7s]: As the carve completes, the kite-bar releases tension slightly, the spray dissipates, the body rises out of the low crouch; the horizon levels.

Lighting: hard noon sunlight from upper-left, sharp specular highlights on the water spray, deep blue tones in the unbroken water.

Texture: kite-lines vibrate with tension, individual water droplets visible suspended mid-arc, wet neoprene wetsuit catches highlights at the wrist.

Camera: POV first-person walk (substituted for sport), bobbing forward with the body's motion, slight handheld shake matching the chop of the water.
```

### Deltas applied

- "First person view" → explicit POV body sensation (arms gripping, body weight, hip angle)
- "Fast" → specific physics (edge angle, kite-line tension, spray trajectory, horizon tilt)
- Equipment specifically named (kiteboard, kite-bar, kite-lines)
- Environment described (water surface, sunlight, spray)
- POV camera direction matches the action (bobbing, slight shake)

---

## Example 5 — Timelapse (sunrise over city)

### Before (weak)

```
Time-lapse of sun rising over a city.
```

What's wrong:
- No beat structure
- No light progression details
- No texture / atmospheric detail
- Generic camera direction

### After (Veo 3 — timelapse mode)

```
Time-compressed sequence over 3-4 hours of sunrise.

Beat 1 [0-2s]: Deep blue pre-dawn ambient over a sleeping city; building lights still on, individual yellow window lamps glowing across the skyline; faint cool mist drifting across rooftops; first hint of warmth on the eastern horizon.

Beat 2 [2-5s]: Sky brightens rapidly — clouds traverse the frame in continuous motion, individual building lights begin switching off one by one across the city; warm orange spreads across the eastern horizon; reflections on glass towers begin to catch first light.

Beat 3 [5-8s]: Full sunrise — gold light floods the cityscape from camera-left, every window catches reflection; the last building lights extinguish; rooftop signs and trees catch sharp directional light; faint heat distortion rises from the skyline.

Lighting progression: cool blue ambient → first warm hint → gold flood → full directional warm.

Camera: locked wide shot, no movement; subtle handheld vibration only; rack focus subtle from foreground rooftop to mid-skyline at the midpoint.
```

### Deltas applied

- "Time-lapse" → explicit time-compression beat markers (3-4 hours over 8s)
- Specific light progression in each beat (pre-dawn → first hint → flood)
- Continuous motion elements (clouds, lights, mist) to give animation
- Camera matches timelapse convention (locked + subtle vibration for liveness)
- No characters → environment IS the subject; described in detail

---

## Common failure pattern across all 5 weak versions

Each weak prompt has the same shape:
1. ONE-sentence vague description
2. ONE vague camera direction
3. Zero beat structure
4. Zero body / equipment / environment specificity

This is exactly what makes the model freeze. The 8-12x word expansion of the strong version is what unlocks actual video generation.

---

## Quick takeaway

For any video prompt, before submitting, verify:

- [ ] CHARACTER FIRST (action precedes camera in the text)
- [ ] Beat 1 / 2 / 3 with time markers (for Kling: explicit; for Veo/Sora: at minimum implicit)
- [ ] Each character described separately if 2+
- [ ] Body parts named (not "reacts" / "gestures")
- [ ] Repeated/continuous language ("3-4 jabs", "never fully returns")
- [ ] Physical realism for equipment / sport
- [ ] One camera direction at the end
- [ ] Lighting source named
- [ ] Forbidden phrases stripped

---

## Example 6 (RU brief) — Утренний кадр, оживить still для Reels

### Контекст

Пользователь даёт ТЗ на русском: «оживи фотку, где девушка стоит у окна с чашкой кофе утром, нужен мягкий кадр на 5 секунд для Reels, наезд камеры и пар от кофе». Модель — Kling 3.0. Still: фронтальное фото, утренний свет от окна, девушка ~25 лет, держит белую кружку обеими руками, смотрит в окно.

### До (weak — то, как пользователь сразу отдаёт)

```
Девушка стоит у окна с кофе утром, наезд камеры, пар от кофе, мягкий кадр
```

What's wrong:
- RU всё письмо — Kling 3.0 парсит хуже EN
- «Стоит» — single-pose verb, гарантированный freeze
- «Наезд камеры» — camera-first нарушает CHARACTER FIRST
- Нет beat-structure
- «Пар от кофе» — без timing и continuity Kling нарисует один статичный wisp
- Нет environment-motion (шторы, свет, дыхание)
- Нет temporal-flow для Kling (нет «First [0-Xs]: ...»)

### После (Kling 3.0)

```
First [0-1.5s]: She wraps both hands around the white ceramic mug, slowly lifts it about 5 cm closer to her face, lips parting slightly as warm air from the coffee reaches her skin; her shoulders settle as she exhales once, breath visibly mingling with the rising coffee steam in the cold morning air near the window.

Then [1.5-3.5s]: She tilts the mug to take a small sip — chin dipping, eyelids briefly lowering, throat working in one swallow; the coffee steam continues to rise in a continuous twisting column, individual wisps catching backlight from the window; a single strand of hair falls forward across her cheek and she does not move to fix it.

Finally [3.5-5s]: She lowers the mug back to chest height, both hands still wrapped around it, gaze drifting from the window slightly toward the camera but not fully meeting it; steam continues; her chest rises and falls once more in a slow breath.

Lighting: soft golden hour backlight from the window casting warm rim on her hair and shoulders, gentle cool fill from the room interior, individual dust motes visible in the window beam.

Texture: white ceramic mug with subtle imperfections, coffee surface gently rippling from her breath, knit sweater with visible loops, soft skin texture with natural pores.

Camera: slow dolly push-in across the 5 seconds, ending tight on her face and mug; subtle handheld vibration throughout; rack focus from the steam wisps to her eyes at the midpoint.
```

### Применённые дельты

- RU «оживи фотку, наезд камеры» → EN cinematic-vocabulary («slow dolly push-in»), камера в самой последней секции (CHARACTER FIRST)
- «Стоит у окна» → 3-beat действие: подносит, делает глоток, опускает; каждый beat с body-detail
- «Пар от кофе» → continuous twisting column, individual wisps, catching backlight — конкретная физика, не один кадр
- Добавлены micro-actions (волос упал, не поправляет; вдох/выдох; глаза не смотрят прямо в камеру) — против frozen-pose
- Kling temporal-format `First [0-1.5s]... Then [1.5-3.5s]... Finally [3.5-5s]` — обязателен для Kling 3.0
- Lighting: «утренний мягкий» → golden hour backlight + warm rim + cool fill + dust motes (по таблице из `camera-vocabulary.md` § RU термины → EN)
- Texture: ceramic imperfections, coffee ripple, sweater loops — даёт модели зацепки для шевеления, не статики
- Rack focus в середине — мотивирован beat-structure, не «выглядит круто»
- Промпт собран на EN; RU-объяснение этого выбора живёт только в нашем диалоге с пользователем
