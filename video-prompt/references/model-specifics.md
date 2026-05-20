# Video model specifics

Each video model parses prompts differently. Pick vocabulary for the target.

---

## Kling 3.0 / Kling 2 / Kling 1.6

**Strengths**: best motion physics (water, fabric, hair); excellent image-to-video; handles 5-10s clips.
**Weaknesses**: needs strict temporal structure; rejects vague camera direction.

### Format rules (mandatory)

Kling REQUIRES **temporal flow**. Every motion prompt must have beginning → middle → end structure with explicit time markers:

```
First [0-2s]: ... 
Then [2-4s]: ...
Finally [4s+]: ...
```

OR:

```
In the first second ... → at midpoint ... → ending on ...
```

### Required cinematic verbs

Use ONLY the named vocabulary from `camera-vocabulary.md`. Generic terms break Kling:
- ❌ "Camera moves forward" → ✅ "slow dolly push-in"
- ❌ "Camera circles" → ✅ "orbit 180" or "slow cinematic arc"

### Light sources — name them

Kling rewards specific light source naming:
- ❌ "Dramatic lighting"
- ✅ "Neon signs casting magenta glow from right", "single flickering fluorescent overhead", "golden hour backlight"

### Texture = realism

Include tactile detail to make output feel physically real:
- "condensation on glass"
- "fabric catches the light"
- "steam rising"
- "sweat on skin"
- "rain on leather jacket"

### Image_tail mode (end frame provided)

When you provide BOTH a start image AND an end image, Kling needs only HOW the camera and subjects move between the two frames. Do NOT describe what the final scene looks like (it's the reference image). Focus on camera path, subject motion arc, timing.

### No transition language

`cut to`, `fade to`, `dissolve`, `reveal` are EDIT terms. Kling can't render them inside one shot. Describe the physical movement instead.

### Kling template

```
First [0-2s]: {character action with beat 1 detail — body parts, repeated motion}
Then [2-5s]: {escalation — character A continues, character B reacts; environmental detail}
Finally [5-8s]: {resolution — final pose or held tension}

Lighting: {specific named sources with direction}
Texture: {1-2 specific tactile details}
Camera: {one exact term — slow dolly push-in / orbit 180 / etc.}
```

### Example (Kling 3.0)

```
First [0-2s]: She raises a wine glass slowly, fingers shifting around the stem, gaze locking on him across the table.
Then [2-5s]: She begins speaking — mouth shaping words continuously, jaw moving, eyes narrowing as she leans forward; he holds still, throat working in one visible swallow.
Finally [5-8s]: She sets the glass down with a soft clink, hand stays on the stem, breath held; his hand reaches for his napkin, fingers tense.

Lighting: warm tungsten table-candle from below illuminating both faces, dim ambient from a single pendant lamp above, condensation glinting on the wine glass.
Texture: linen tablecloth shifts with the glass, individual hair strands move slightly in the warm air.
Camera: slow dolly push-in across the table, subtle handheld vibration, focus locked on her hand on the glass.
```

---

## Veo 3 (Google)

**Strengths**: best at natural cinematography; understands narrative direction; good with people-doing-things.
**Weaknesses**: shorter clips (up to 8s typically); needs less rigid structure than Kling but still benefits from beat structure.

### Format

More flexible than Kling. Accepts beat structure without explicit time markers. Veo's parser handles "She walks to the door" + body detail well.

### Veo template

```
Beat 1: {character action — body specific, repeated}
Beat 2: {escalation}
Beat 3: {resolution}

[Optional environment / lighting sentence]
[Optional camera sentence]
```

### Example (Veo 3)

```
Beat 1: She raises a wine glass slowly, gaze locking on him across the candle-lit table. Her fingers shift around the stem; she leans forward slightly.
Beat 2: She begins speaking — mouth forming words continuously, lips shaping, jaw moving; he sits still, his throat working in one swallow, jaw clenching.
Beat 3: She sets the glass down softly, hand stays on the stem; he reaches for his napkin, fingers tightening on the fabric.

Warm tungsten candle from below, dim ambient pendant overhead.
Camera: slow dolly push-in across the table, focus on her hand.
```

---

## Sora (OpenAI)

**Strengths**: best at narrative scene description; handles physics extremely well; understands story logic.
**Weaknesses**: less specific camera control; tends toward "cinematic" defaults.

### Format

Natural-language paragraph. Sora parses it as a director's note, not a structured prompt. Beat structure helps but isn't required.

### Sora template

```
[One-paragraph description with embedded beats and physical detail]

[Separate sentence on lighting if needed]
[Separate sentence on camera if needed]
```

### Example (Sora)

```
A woman in her thirties sits across from a man at a candle-lit dinner table. In the first moment, she raises a wine glass slowly, fingers tightening around the stem, her gaze locked on his face as she leans forward. She begins speaking — mouth shaping words continuously, jaw tense, eyes narrowing — while he holds still, throat working in a single visible swallow, fingers tightening on his napkin. As her words land, she sets the glass down with a soft clink, hand staying on the stem; his hand stays gripping the napkin, knuckles white.

Warm tungsten candle from below illuminates both faces; a single pendant lamp casts dim ambient light from above. Condensation glints on the wine glass.

Camera: slow dolly push-in across the table, subtle handheld vibration, sharp focus on her hand on the stem.
```

### Sora notes

- Sora is the best model for physics ("a glass falls and shatters" actually shatters realistically)
- Use action verbs liberally — Sora picks up narrative
- Specifying clothes, textures, environmental detail strengthens the scene

---

## Runway Gen-3 / Gen-3 Turbo

**Strengths**: fast generation, image-to-video reliable; good for short action clips.
**Weaknesses**: ~4-10s max; less character animation depth than Kling/Veo; struggles with multi-character.

### Format

Shorter, action-focused. Beat structure works but Runway has the shortest attention; prefer 2-3 beats not 3-4.

### Runway template

```
{Character action — body specific, 1-2 sentences}
{Optional: brief escalation or reaction}
{Camera direction}
```

### Example (Runway)

```
She raises a wine glass slowly, fingers shifting around the stem, eyes locked across the table. She begins speaking, mouth shaping words continuously, jaw tense.

Camera: slow dolly push-in across the candle-lit table, focus on her hand.
```

### Runway notes

- Keep under 5 sentences total
- Two characters: pick ONE primary; the other can only "hold" or do simple reaction
- For high-action: Runway handles single-subject motion well, fails on multi-subject choreography

---

## Pika 2.0 / Pika 1.5

**Strengths**: cheap, fast iteration; good for stylized non-realistic.
**Weaknesses**: limited motion physics; short clips; character consistency drift.

### Format

Like Runway but even shorter. 3-4 sentences max.

### Pika template

```
{Single action with character detail}
{Camera direction}
```

### Example (Pika)

```
She raises a wine glass slowly while speaking, mouth shaping words, jaw tense, gaze locked across the table.

Camera: slow dolly push-in, candle-lit warm tones.
```

### Pika notes

- Best for stylized / animation / non-photorealistic
- Avoid complex multi-character scenes
- Use for quick concept tests before committing to Kling/Veo

---

## Hailuo / MiniMax

**Strengths**: good motion at low cost; Chinese-trained, handles East Asian subjects better.
**Weaknesses**: smaller community / less documentation; format conventions still emerging.

### Format

Similar to Runway / Pika — short, action-focused. Beat structure helps.

---

## Luma Dream Machine

**Strengths**: dreamy / surreal output; good camera moves.
**Weaknesses**: weaker character animation; better for abstract / atmospheric clips.

### Format

Like Pika. Keep it short, lean on atmosphere over character drama.

### Luma template

```
{Atmospheric/spatial action — environment-focused}
{Camera direction with mood emphasis}
```

### Example (Luma)

```
Mist drifts across a still lake at dawn, faint ripples spreading from an unseen source, soft golden light catching on the water surface.

Camera: slow drone fly-over rising and tilting down, gentle motion.
```

---

## Quick comparison

| Need | Best model |
|---|---|
| Character emotion / 2-person dialogue | Kling 3.0 |
| Best physics (water, fabric, hair, breakage) | Sora or Kling |
| Cinematic narrative scene | Veo 3 or Sora |
| Quick action clip | Runway Gen-3 |
| Stylized / animated look | Pika |
| Cheap iteration | Pika or Runway Turbo |
| East-Asian subjects | Hailuo |
| Atmospheric / surreal | Luma |

---

## Universal anti-patterns

❌ Vague camera direction across all models:
> "Cinematic camera work, dynamic shot"
Replace with exact term from `camera-vocabulary.md`.

❌ Multiple simultaneous camera moves:
> "Push-in with orbit with tilt up"
Pick one; layer two max if absolutely needed.

❌ Transition language inside one shot:
> "Camera pans to reveal, then cuts to the door"
The model can't render a "cut" within one shot.

❌ Multi-character "they look at each other":
> Synchronised statues. Describe EACH separately.

❌ Single-instance gestures:
> "He extends his arm" → frozen pose. Use repeated/continuous patterns.

❌ Generic action verbs:
> "Performs the activity" / "moves gracefully" / "reacts"
Name the specific physics / body parts / timing.

✅ The universal form that works on all models:
> {Beat 1: WHO does WHAT, body-part-specific, repeated language} {Beat 2: escalation / reaction} {Beat 3: resolution} {Lighting source named} {Camera: one exact term}
