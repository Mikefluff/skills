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

---

## Example 7 — Native dialogue scene (Veo 3.1)

### Before (weak)

```
A woman tells a man she's leaving him at a restaurant. They argue. Sad music plays.
```

What's wrong:
- No beat structure, single-instance verbs ("tells")
- No Dialogue / SFX / Ambient blocks — Veo 3.1's native-audio capability ignored
- "Sad music" is vague — no diegetic/non-diegetic split, no cue specificity
- Lip-sync trigger (`Character: "line"` format) missing entirely

### After (Veo 3.1)

```
Beat 1 (0-2s): She sets her wine glass down with a soft clink, both hands flat on the linen tablecloth, gaze locked on his face; her shoulders settle, breath in.

Beat 2 (2-5s): She delivers the line, jaw moving evenly, no hesitation.
  Character: "I'm not coming home tonight. Or any night after."
  Ambient: low murmur of restaurant conversation, distant clink of cutlery

Beat 3 (5-8s): He freezes for one beat, lips parting; throat works in a single swallow; his hand reaches halfway across the table and stops, suspended.
  SFX: muted single glass clink from a neighboring table

Camera: static medium two-shot held throughout, subtle handheld vibration, focus on the gap between their faces.
```

### Deltas applied

- Dialogue placed in Beat 2 (not Beat 1) — Veo 3.1 needs a setup frame to lock the face for lip-sync
- `Character: "..."` syntax with colon + double quotes — exact form that triggers Veo 3.1 lip-sync
- Ambient (restaurant murmur) dropped to background under the line, NOT competing
- One SFX cue tied to a physical beat — not on top of speech
- Camera held — no push-in during dialogue (camera-energy rule for dialogue-scene pacing)
- See `references/audio-prompting.md` and `references/pacing-modes.md` § Dialogue-scene

---

## Example 8 — I2V from still (Kling 3.0)

### Before (weak — common mistake)

```
A woman in a red dress raises a wine glass at a candle-lit table. Warm tones, slow push-in.
```

Source image attached: woman in red dress at candle-lit dinner table, wine glass on table.

What's wrong:
- Re-describes everything the model already sees (dress, glass, table, candle, warm tones) — wastes tokens and confuses the model into "regenerating" the frame
- Generic "raises" — single-instance verb → frozen pose
- No Kling temporal flow
- No physical tethers (what stays in frame, what moves)

### After (Kling 3.0)

```
First [0-1.5s]: She wraps her fingers around the stem of the glass, lifting it about 8cm off the table; her gaze stays locked across the table on the man, head tilting slightly forward.

Then [1.5-4s]: She continues raising the glass to chest height, jaw moving as her lips begin to part for a word; her shoulders settle, breath in; the man across the table flinches subtly, throat working in one swallow.

Finally [4-6s]: She holds the glass suspended at chest height, gaze unbroken; the candle flame flickers once with her breath.

Physical tether: the glass stays in her right hand throughout, never leaves the hand; the napkin in his lap stays draped; the candle stays upright.

Environment: the candle flame flickers irregularly; the linen tablecloth shifts subtly when her elbow moves.

Camera: slow dolly push-in across the 6 seconds, ending tight on the gap between their faces, focus on her hand on the stem.
```

### Deltas applied

- No re-description of dress, table, candle, warm tones — model sees those
- "Raises" → 3-beat motion: wrap, lift to chest, hold suspended
- Added the reactor (the man) — body detail in Beat 2
- Physical-tether block names what STAYS in frame (glass, napkin, candle) — Kling needs this to not teleport props
- Environment-motion (flame flicker, tablecloth shift) — gives the scene life without re-describing the static elements
- Kling temporal flow REQUIRED — `First [0-1.5s]... Then [1.5-4s]... Finally [4-6s]`
- See `references/i2v-prompting.md`

---

## Example 9 — V2V edit (Runway Aleph)

### Before (weak)

```
Take this daytime street footage and make it look like nighttime in winter with snow. Add a few people walking. Change the camera angle to low.
```

Source clip attached: 5s daytime street scene, three pedestrians walking, no snow.

What's wrong:
- Stacks three actions (relight + add + re-angle) in one prompt — Aleph produces unstable results
- "Make it look like" — no clear action verb
- "A few people" — vague target
- Exceeds Aleph's 5s constraint for multi-edit

### After (Runway Aleph — single-verb passes)

Pass 1 (relight to winter dusk):

```
Relight to winter dusk. Drop the sun to low warm orange on the horizon, cool blue ambient in the shadows. Keep the existing pedestrians, the existing buildings, and the existing camera position unchanged.
```

Pass 2 (add snowfall — chain from Pass 1 output):

```
Add light snowfall throughout the frame, gentle drift downward, no accumulation on the ground. Match the existing winter-dusk lighting. Keep everything else unchanged.
```

(Re-angle requires a separate generation in a different model — Aleph holds the original camera position.)

### Deltas applied

- One action verb per pass — `Relight` then `Add` — never stacked
- Each pass explicitly names what to PRESERVE (pedestrians, buildings, camera position)
- Each pass specifies the outcome with concrete properties (warm orange / cool blue, drift downward, no accumulation)
- 5s cap per Aleph generation respected
- Re-angle moved to a different model — Aleph is V2V, not view-synthesis
- See `references/v2v-editing.md`

---

## Example 10 — Multi-shot mini-scene (Sora 2)

### Before (weak)

```
A three-shot scene of a woman and a man at dinner. Wide establishing, then close-up on her hand, then her reaction. They look at each other.
```

What's wrong:
- No per-shot duration / framing breakdown
- Re-describes the characters each shot ("a woman", "her") — causes identity drift across shots
- No style anchor — lighting / grade will jump between shots
- "They look at each other" — synchronised statues
- No transitions

### After (Sora 2)

```
Shot 1 (3s, wide establishing): A candle-lit dinner table from across the room, the warm pendant lamp above casting a pool of light on the scene; both figures visible — [ref:Sarah] sits camera-left, [ref:Marcus] camera-right; the room around them in soft darkness.

new shot:

Shot 2 (5s, extreme close-up on hands): [ref:Sarah]'s right hand wraps slowly around the stem of a wine glass; her thumb traces the curve once; [ref:Marcus]'s hand enters frame from the right, fingers tightening on his napkin.

match cut on hand

Shot 3 (4s, medium two-shot): [ref:Sarah] lifts the wine glass to chest height, gaze locking on [ref:Marcus]; [ref:Marcus] holds eye contact, throat working in one slow swallow, jaw clenching once.

Style anchor: warm tungsten candle from below, dim ambient pendant overhead, editorial cinematic grade with shallow depth of field across all three shots.
```

### Deltas applied

- Each shot block has duration + framing + action
- Identity labels (`[ref:Sarah]`, `[ref:Marcus]`) used in every shot — physical traits NOT re-described between shots (locked by cameo refs)
- Multi-shot transitions explicit (`new shot:`, `match cut on hand`) — Sora 2 parses these
- One Style anchor sentence at the end binds all three shots' lighting / grade
- "Look at each other" → described per character per beat
- See `references/multi-shot.md` and `references/identity-references.md`

---

## Example 11 (RU audio) — Диалог на русском (Veo 3.1)

### Контекст

Пользователь даёт ТЗ на русском: «короткая RU-сцена, друг рассказывает мне новость в баре, надо чтобы он сказал реплику с интонацией усталости, плюс эмбиент бара, lip-sync должен совпасть». Модель — Veo 3.1.

### До (weak)

```
В баре друг говорит мне с усталым голосом: "Я ухожу из компании". Шум бара на фоне. Lip-sync.
```

What's wrong:
- Промпт на RU — Veo 3.1 парсит EN тело точнее, но RU-реплику внутри quotes держит хорошо
- Нет beat-structure
- Прозодика («усталым голосом») должна стоять ПЕРЕД quote — внутри quote только сама речь
- Нет лип-синк триггера (`Character: "line"` с двоеточием и двойными кавычками)
- Конкурирующее аудио (бар на фоне) не разведено по уровню

### После (Veo 3.1)

```
Beat 1 (0-2s): A man in his thirties sits across from the camera at a small bar table, weary voice, shoulders settled, eyes lowered to his half-empty glass; he draws a slow breath in, lips part.

Beat 2 (2-5s): He lifts his gaze to meet the camera, jaw moving evenly as he delivers the line.
  Character: "Я ухожу из компании. Завтра подаю заявление."
  Ambient: low bar chatter, distant clink of glasses, dropped under the line

Beat 3 (5-8s): He holds the gaze for one full beat, exhales softly, shoulders dropping further; his hand wraps around the glass.
  SFX: single muted glass clink from a neighboring table

Camera: static medium close-up held throughout, subtle handheld vibration, focus on his eyes; warm tungsten pendant from upper-right, cool blue ambient from a neon sign camera-left.
```

### Применённые дельты

- Body тело промпта — EN (Veo 3.1 парсит точнее); RU-реплика — verbatim внутри quotes (Veo 3.1 handles multilingual речь через `Character: "..."`)
- `Character: "Я ухожу из компании. Завтра подаю заявление."` — exact lip-sync trigger format (двоеточие + двойные кавычки)
- Прозодика «усталый голос» вынесена в `weary voice` ПЕРЕД quote, не внутрь
- Beat 2 несёт диалог; Beat 1 — setup для face-lock; Beat 3 — реакция
- Ambient «бар на фоне» → `low bar chatter, dropped under the line` — phrasing указывает модели понизить уровень под речь
- Один SFX cue (`single muted glass clink`) уложен в Beat 3, не на речь
- Camera static (dialogue-scene pacing) — никаких push-in во время реплики
- See `references/audio-prompting.md` и `references/pacing-modes.md` § Dialogue-scene
