# I2V-tier models

Image-to-video: you provide a still, the model animates it. CRITICAL — the source frame is the look. Do NOT re-describe it. Describe motion only: body parts, repeated action, camera path, timing.

---

# Kling 3.0

**Strengths**: cheap premium tier (~$0.10/sec), top-tier motion physics (cloth, hair, water), **native 4K @ 60fps**, **up to 15s** clips, **native synchronized audio** (Omni variant), **AI Director multi-shot** (up to 6 shots in one 15s generation), **multi-speaker dialogue** via `<<<voice_1>>>` syntax. Supports EN / CN / JP / KR / ES dialogue.
**Weaknesses**: rejects vague camera direction; demands explicit temporal flow.
**Execute via**: `--execute --model kling-3` (env: `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET`) — Kuaishou Kling API.

**Multi-shot Director note**: Kling 3.0 has Auto mode (model plans shots) and Custom mode (you specify per-shot duration + framing + content). Multi-speaker dialogue uses `Character <<<voice_1>>> said, "line"` syntax. See [kling.ai blog — Omni native lip-sync guide](https://kling.ai/blog/kling-video-3-omni-native-lip-sync-audio-guide).

## Format rules (mandatory)

Temporal flow REQUIRED. Every motion prompt has begin → middle → end with explicit time markers:

```
First [0-2s]: ...
Then [2-5s]: ...
Finally [5-8s]: ...
```

- Named camera vocabulary only (see `camera-vocabulary.md`). Generic terms break Kling.
- Name light sources with direction.
- No transition language (`cut to`, `fade to`).
- Image_tail mode (start + end frame): describe ONLY the camera path and motion arc between frames. The end frame IS the destination.

## Kling 3.0 template

```
First [0-2s]: {motion onset — body parts, gesture begins}
Then [2-5s]: {escalation — second character reacts, environmental detail}
Finally [5-8s]: {resolution — final pose or held tension}

Lighting: {named sources with direction}
Texture: {1-2 tactile details}
Camera: {one exact term}
```

## Example (Kling 3.0)

Source frame: woman and man seated at candle-lit dinner table, wine glasses present. Prompt describes motion only.

```
First [0-2s]: She raises the wine glass slowly, fingers shifting around the stem, gaze locking on him across the table.
Then [2-5s]: She begins speaking — mouth shaping words continuously, jaw moving on each syllable, eyes narrowing as she leans forward; he holds still, throat working in one visible swallow.
Finally [5-8s]: She sets the glass down with a soft clink, hand stays on the stem; his hand reaches for the napkin, fingers tightening on the fabric.

Lighting: warm candle from below illuminating both faces, dim pendant overhead, condensation glinting on the glass.
Texture: linen tablecloth shifts as the glass meets it, individual hair strands move slightly in the warm air.
Camera: slow dolly push-in across the table, subtle handheld vibration, focus locked on her hand on the stem.
```

---

# Kling 2.6 Elements

**Strengths**: 4 reference images per scene for multi-element identity (character + outfit + prop + location).
**Weaknesses**: same format demands as Kling 3.0; identity drift if labels collide.
**Execute via**: `--execute --model kling-3` (env: `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET`) — Kuaishou Kling API (Elements via same endpoint).

## Format rules

- Same temporal flow as Kling 3.0.
- Each reference image carries a label; reuse the label inside the prompt instead of re-describing.

## Kling Elements template

```
References:
  [REF_A] = {character label, e.g. "the_woman"}
  [REF_B] = {outfit / second character}
  [REF_C] = {prop, e.g. "the_glass"}
  [REF_D] = {location, e.g. "the_table"}

First [0-2s]: [REF_A] {action with body-part detail}
Then [2-5s]: [REF_A] and [REF_B] {escalation}
Finally [5-8s]: [REF_C] {resolution detail}

Lighting / Texture / Camera: {standard Kling blocks}
```

## Example (Kling Elements)

```
References:
  [REF_A] = the_woman
  [REF_B] = the_man
  [REF_C] = the_wine_glass
  [REF_D] = the_dinner_table

First [0-2s]: [REF_A] raises [REF_C] slowly at [REF_D], fingers shifting around the stem, gaze locking on [REF_B].
Then [2-5s]: [REF_A] begins speaking — mouth shaping words continuously, jaw moving; [REF_B] holds still, throat working in one swallow.
Finally [5-8s]: [REF_A] sets [REF_C] down with a soft clink, hand stays on the stem; [REF_B] reaches for the napkin, fingers tense.

Lighting: warm candle from below, dim pendant overhead.
Texture: condensation on [REF_C], linen shifts under [REF_C].
Camera: slow dolly push-in across [REF_D], focus on her hand.
```

## Notes

- Use Elements when the same character returns across multiple shots — register once, reference everywhere.
- Identity labels are case-insensitive but underscore-separated; avoid spaces.

---

# Kling Master

**Strengths**: dedicated camera-control tier — pairs cleanly with named cinematic verbs.
**Weaknesses**: more expensive than Kling 3.0; same temporal-flow demand.
**Execute via**: `--execute --model kling-3` (env: `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET`) — Kuaishou Kling API (Master tier via same endpoint).

## Format rules

- Same temporal flow.
- Camera direction can be more aggressive — explicit speed ramps, multi-axis moves (within reason).

## Kling Master template

```
First [0-2s]: {action}
Then [2-5s]: {action + camera evolution}
Finally [5-8s]: {action + camera resolution}

Camera direction (per beat):
  Beat 1: {term, e.g. slow dolly push-in}
  Beat 2: {term, e.g. orbit 90 right}
  Beat 3: {term, e.g. settle on close-up}

Lighting / Texture: {standard blocks}
```

## Example (Kling Master)

```
First [0-2s]: She raises the wine glass slowly, fingers shifting on the stem, gaze locking on him.
Then [2-5s]: She begins speaking — mouth shaping words continuously, jaw moving; he holds still, throat working in a swallow.
Finally [5-8s]: She sets the glass down with a soft clink, hand stays on the stem; his hand reaches for the napkin.

Camera direction:
  Beat 1: slow dolly push-in across the table.
  Beat 2: subtle orbit 30 right, focus shifting from her hand to her face.
  Beat 3: settle on a tight two-shot, focus locked on the glass.

Lighting: warm candle from below, dim pendant overhead, condensation on the glass.
Texture: linen shifts as the glass meets it.
```

---

# Hailuo 02 / Hailuo 02 Pro (MiniMax)

**Strengths**: strongest physics for gymnastics, cloth, water, hair; 1080p; ~$0.28/clip on base tier.
**Weaknesses**: shorter attention than Kling/Veo; dialogue scenes weaker than physics-driven scenes.
**Execute via**: prompt-only — no native MiniMax adapter in v2.2. Workaround: `--execute --model fal-video --fal-model fal-ai/minimax/hailuo-02/pro/text-to-video` (env: `FAL_KEY`).

## Format rules

- Beat 1/2/3 (no strict time markers required).
- Physics-first language — name the contact, force, surface.

## Hailuo 02 template

```
Beat 1: {action with physical contact named}
Beat 2: {force / momentum continues}
Beat 3: {resolution — settle, rebound, or held pose}

Lighting: {named sources}
Camera: {one term}
```

## Example (Hailuo 02)

Source frame: woman and man at candle-lit dinner table.

```
Beat 1: She raises the wine glass slowly, fingers tightening around the stem, the liquid sloshing against the glass walls; her gaze locks on him.
Beat 2: She begins speaking — mouth shaping words continuously, jaw moving on each syllable; he holds still, throat working in one swallow, his napkin compressing under his fingers.
Beat 3: She sets the glass down with a soft clink, the liquid settling with a brief ripple; his hand stays gripped on the napkin, fabric creasing.

Lighting: warm candle from below, dim pendant overhead, condensation on the glass.
Camera: slow dolly push-in across the table, focus on her hand.
```

## Notes

- Hailuo 02 Pro: same parser, higher fidelity, 1080p @ 24-30fps. **Max duration: 10s** (6s or 10s options). Sources: [hailuo-02.com](https://hailuo-02.com/), [fal.ai Hailuo-02 pro](https://fal.ai/models/fal-ai/minimax/hailuo-02/pro/text-to-video).
- Best returns on prompts that name the physics (liquid sloshing, fabric compressing, hair catching the air).

---

# Runway Gen-4 / Gen-4 Turbo

**Strengths**: fast I2V, reliable for short action clips, reference-image support, good identity stability up to 10s.
**Weaknesses**: less character-emotion depth than Kling/Veo; Turbo trades detail for speed.
**Execute via**: `--execute --model gen-4` / `gen-4-turbo` (env: `RUNWAY_API_KEY`) — Runway API.

## Format rules

- 2-3 beats. Runway has the shortest attention.
- One camera direction line.

## Runway Gen-4 template

```
{Character action — body specific, 1-2 sentences}
{Brief escalation or reaction}
Camera: {one term}
```

## Example (Runway Gen-4)

```
She raises the wine glass slowly, fingers shifting on the stem, gaze locking on him across the table. She begins speaking, mouth shaping words continuously, jaw tense.

Camera: slow dolly push-in across the candle-lit table, focus on her hand.
```

## Notes

- Gen-4 Turbo: same parser, cheaper, less detail — use for previews then re-render on Gen-4.
- Two characters: pick ONE primary, the second can only hold or do a simple reaction.

---

# Pika 2.2

**Strengths**: cheap stylized output, 1080p, 10s clips. Bundles Pikaframes (keyframe interpolation), Pikadditions (insert objects), Pikaswaps (object replacement) — V2V details in `v2v-tier.md`.
**Weaknesses**: weaker physics; character consistency drifts on longer clips.
**Execute via**: prompt-only — no native Pika adapter in v2.2. Workaround: `--execute --model fal-video --fal-model fal-ai/pika-text-to-video` (env: `FAL_KEY`) if mirror available.

## Format rules

- 3-4 sentences max.
- One camera direction line.

## Pika 2.2 template

```
{Single action with character detail}
{Camera direction}
```

## Example (Pika 2.2)

```
She raises a wine glass slowly while speaking, mouth shaping words, jaw tense, gaze locked across the candle-lit table.

Camera: slow dolly push-in, warm candle tones.
```

## Notes

- Best for stylized / animation / non-photorealistic looks.
- Avoid complex multi-character choreography.
- Pikaframes / Pikadditions / Pikaswaps live in `v2v-tier.md` — Pika 2.2 is the only model that mixes T2V/I2V and V2V in one product.

---

## Universal I2V anti-patterns

- Re-describing the source frame ("a woman in a red dress sits at a candle-lit table…") — the frame already encodes that. Wastes tokens, can cause drift.
- "Camera circles" with no source frame anchor — pick named term + duration.
- Speaking long dialogue without audio support — these models have no native audio. Add separately.
- Multi-character "they look at each other" — describe each separately or the model freezes them.
