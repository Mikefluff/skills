---
title: "Animate a still image with Kling for a Reel"
persona: "Short-form video creator (TikTok / Reels / Shorts)"
time: "5-10 minutes"
skills:
  - video-prompt
---

# A Kling prompt that turns a product hero shot into 5 seconds of motion

Сценарий: у тебя есть hero shot нового продукта — sleek bottle / device / app screen. Нужен 5-секундный clip для Instagram Reel или TikTok. Slow dolly push-in, чтобы зритель «провалился» в кадр, минимум background motion, продукт в фокусе всё время.

Это работа для `video-prompt`. Скилл собирает по CHARACTER FIRST law с beat-структурой и Kling-specific temporal markers.

## Intent — CHARACTER FIRST law

Главное правило video prompts (см. `skills/video-prompt/references/identity-references.md`):

> Subject (character / hero object) описывается ПЕРВЫМ, БУКВАЛЬНО, в полных словах. Перед лимит-чувствительной частью. Video models дропают first 30-40% prompt в кэш — туда нужно положить subject, иначе модель impro визирует character.

Это значит prompt начинается не с «cinematic shot of...», не с «in a futuristic lab...», а с физического описания того, что в кадре. Subject. Pose. Outfit / surface / material. Расположение в frame.

## Intent — Beat structure

5 секунд = 3 beats:

- **Beat 1 (0.0-1.5s)** — establishing. Камера держит subject в стартовой позиции. Минимум motion.
- **Beat 2 (1.5-3.5s)** — main motion. Dolly / pan / character action. Тот самый visual hook.
- **Beat 3 (3.5-5.0s)** — settle / hold. Motion затихает, кадр держит финальную позицию для CTA.

Без beats prompt ползёт в random direction — модель сама решает темп.

## Setup

Скилл установлен. Поддерживает Kling 1.6 / 2.0, Veo 3, Sora, Runway Gen-3, Pika, Hailuo, Luma. По умолчанию — Kling (best для image-to-video с тонкой motion).

## Step 1. Invoke with the brief

```
/video-prompt image-to-video --model kling --duration 5s
```

Скилл спрашивает 4 вещи:

```
1. Source image — describe the still in 1-2 sentences
2. Motion goal — what should happen in 5 seconds (one verb-led sentence)
3. Camera move — static / pan / dolly / orbit / handheld / crane / zoom
4. Mood / pacing — narrative / action / comedy / documentary / timelapse
```

## Step 2. Concrete brief

Source image: «An amber-coloured glass bottle of cold brew on a matte black stone surface, single softbox from upper left, condensation droplets on the bottle, slight blur in the background suggesting a kitchen counter.»

Motion goal: «slow push toward the bottle, condensation droplet rolls down the glass at 3 seconds, ending tight on the label»

Camera move: **dolly push-in** (slow, no shake)

Mood / pacing: **narrative** (slow build, premium feel, not action)

## Step 3. Apply CHARACTER FIRST + beats

Скилл собирает prompt:

```
SUBJECT (verbatim, character-first)
An amber-coloured glass bottle of cold brew, condensation droplets on the
glass, matte black stone surface beneath, blurred kitchen counter in the
background.

BEAT 1 (0.0-1.5s) — establishing
The bottle stands centred in frame, completely still. A single droplet of
condensation hangs near the top, not yet falling. Soft directional light
from upper left.

BEAT 2 (1.5-3.5s) — main motion
Camera dollies forward toward the bottle at a slow, even pace, no shake,
no rotation. At 3.0 seconds, a single condensation droplet rolls down the
side of the glass, leaving a slow trail. Background blur deepens as
focus pulls tighter.

BEAT 3 (3.5-5.0s) — settle
Camera stops with the label centred and crisp in frame. Droplet has
reached the base. Everything holds for 1.5 seconds. No additional motion.
```

## Step 4. The Kling-final prompt

Kling-specific temporal markers (см. `skills/video-prompt/references/models/i2v-tier.md`): use seconds as anchors, avoid relative «then», prefer «at 3.0s», use one camera-move verb per beat.

```
An amber-coloured glass bottle of cold brew with visible condensation
droplets on the glass, resting on a matte black stone surface, blurred
kitchen counter in the background, single softbox key light from upper
left. The bottle stays perfectly centred and motionless. Camera dollies
forward in a slow, even push-in, no shake, no rotation, no zoom. At 3.0
seconds, a single condensation droplet rolls down the right side of the
bottle, leaving a slow trail. Camera stops at the 3.5-second mark with
the bottle label crisp and centred in frame. Final 1.5 seconds: subject
holds, no additional motion, no background change. Cinematic, premium
beverage commercial, soft warm grade, shallow depth of field, 24fps
motion blur. Negative: no character, no hands, no zoom-out, no rotation,
no flicker.
```

Key Kling markers in this prompt:

- **«stays perfectly centred and motionless»** — anchor against Kling's habit of micro-jitter on still subjects
- **«at 3.0 seconds»** / **«at the 3.5-second mark»** — explicit temporal anchors (Kling honors these ~70% of the time)
- **«no shake, no rotation, no zoom»** — defensive against camera-move hallucinations
- **«24fps motion blur»** — cinematic feel anchor
- **Negative section** — Kling 1.6+ supports it via `--no` syntax or inline «no X» list

## Step 5. Iterate on the result

Если Kling вернул:

- **Camera shaking** — добавь «locked-off camera, no handheld feel» в Beat 2
- **Droplet не появился в 3.0s** — это miss rate Kling (~30% на temporal anchors). Re-run с тем же prompt 2-3 раза, выбери best. Или подвинь motion на 2.5s — раньше anchor работает чаще.
- **Background ожил (counter движется)** — добавь «background completely static, no motion in background, no people, no objects entering frame»
- **Bottle rotated slightly** — anchor «no rotation» в Subject и в Beat 1

## Per-model deltas

Если ты переключаешься на другой generator:

- **Veo 3** — поддерживает звук (можно описать «sound: soft droplet-roll, ambient kitchen hum»). Beat structure такая же.
- **Sora** — длиннее (до 20s). Beats масштабируются. Camera vocabulary шире (можно «35mm anamorphic»).
- **Runway Gen-3** — strict 10s max. Temporal markers слабее honored — лучше polagается на verbose motion description.
- **Pika** — image-to-video с keyframes; вместо beats — keyframe timestamps.
- **Hailuo** — strong на character motion, weak на static product shots. Не для этого случая.
- **Luma** — strongest motion physics, но любит добавить «cinematic» drift даже когда просишь static. Anchor sharper.

Скилл переключает синтаксис по `--model`.

## Когда НЕ использовать video-prompt

- **Простая stock loop (продукт вращается)** — записать руками или Adobe AE faster.
- **Анимация UI (mock app demo)** — Lottie / After Effects / Rive. Video gen overkill.
- **Talking-head с lip-sync** — HeyGen / D-ID / Synthesia tuned for this. Generic video gen дрифтит на лица.
- **Длинный narrative (>20s с сценами)** — генерируй посекциям и склеивай. Single-prompt длиннее 20s = random output.

## Troubleshooting

### Kling кадрирует продукт за пределы frame на dolly

Добавь в Subject: «bottle remains centred in frame at all times, never crops». В Beat 2: «camera stops before reaching the bottle, no cropping». Anchor нужен в двух местах.

### Слишком быстрая push-in (5 секунд проходят за 2)

Pacing-mode не настроен. Скилл по дефолту — narrative (slow). Если ставишь `--pacing action` — будет fast. Verify в команде: `/video-prompt ... --pacing narrative`.

### Появился человек в кадре, хотя не просили

Kling галлюцинирует characters на любых subjects, где может быть human context (kitchen, gym, office). Anchor в Negative: «no character, no person, no hands, no body parts». Если всё равно появляется — добавь в Subject: «product-only shot, no humans visible, no humans implied».

### Droplet в Beat 2 — single droplet hallucinates как множество

Anchor: «exactly one droplet, no other droplets moving, all other condensation stays still». Скилл по дефолту не пишет «exactly one» — это нужно requested если важно.

## Related

- [image-prompt-cover.md](image-prompt-cover.md) — родственная задача со 6-part formula для still
- [viral-post.md](viral-post.md) — если video идёт в виральный пост
- [landing-launch.md](landing-launch.md) — если video идёт на landing hero
- [skills/video-prompt/references/models/i2v-tier.md](../../skills/video-prompt/references/models/i2v-tier.md) — полный Kling syntax reference
