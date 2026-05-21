# Image-to-video prompting

Motion-over-still. The model already sees the source frame. Different grammar from text-to-video.

---

## When to use this file

When prompting any I2V model: Kling I2V, Hailuo I2V, Runway Gen-4 I2V, Pika I2V, Veo I2V, Sora I2V.

---

## The motion-over-still law

The model **sees the source frame**. Re-describing what's already in the frame wastes tokens AND confuses the model — it tries to "regenerate" the still instead of animating it, producing drift in face, wardrobe, and lighting.

Describe ONLY:
- How subjects move
- How camera moves
- Environmental motion (wind, water, dust, steam, fabric)
- What happens that isn't already in the frame

---

## What goes IN the prompt

- **Subject motion** — which body parts move, frequency, timing, beat structure
- **Camera motion** — one term from `camera-vocabulary.md`
- **Environmental motion** — wind through hair, steam rising, water rippling, dust drifting
- **End-frame conditioning** — if the shot ends in a state different from frame 0, name it

---

## What does NOT go in the prompt

- Subject appearance — "a woman in a red dress" (model sees the dress)
- Lighting setup — "candle-lit warm tones" (model sees the light)
- Setting / background — "in a kitchen with a marble counter" (model sees the kitchen)
- Color grading — "warm cinematic tones" (model sees the grade)
- Wardrobe details — model sees them

---

## Physical-tether rule

Props visible in the frame must be **named with their motion or non-motion**. Otherwise they teleport, morph, or vanish.

For every prop in frame, write one phrase:

```
Physical tether:
  - wine glass stays in her right hand throughout
  - laptop screen glow continuous, doesn't blink
  - cigarette held loose between fingers, ash never falls
  - papers on the desk shift slightly with airflow
```

Posture and composition carry over from frame 0. If the subject is leaning forward, they stay leaning forward unless you say otherwise.

---

## First-frame / last-frame chaining

Modes that accept both: Kling `image_tail`, Higgsfield Start+End, Luma Ray3 Start+End.

When two frames are provided, **describe HOW the transition happens**, not what the end state looks like (the end frame is the reference).

Write:
- Motion arc — what path the body / object travels
- Timing — when each phase lands within the clip
- Camera path — how camera moves between the two frames

Don't write:
- What the end state looks like — it's the reference image

---

## Template

```
Beat 1 (0-2s): <character body motion — what shifts from frame 0>
Beat 2 (2-5s): <escalation — body plus environment>
Beat 3 (5-8s): <resolution or final pose>

Physical tether: <prop stays X, posture maintains Y>
Environment: <wind / water / steam / dust motion>
Camera: <one term>
```

---

## Anti-patterns

- "A woman in a red dress raises a wine glass" → re-describes the subject; model sees both the dress and the glass already
- "In a candle-lit kitchen with warm tones..." → re-describes lighting; model sees it
- Generic motion verbs — "performs", "moves", "interacts" → frozen pose
- Single-instance gestures — "she lifts the glass once" → frozen pose; use repeated or continuous
- Describing wardrobe in detail → model tries to re-render the outfit and drifts
- Forgetting the physical tether → props teleport or morph
- Re-listing background elements → wasted tokens, drift risk

---

## Example (Kling 3.0 I2V)

Source frame: a woman in her thirties at a candle-lit dinner table, holding a wine glass, looking across at a man.

**Before — re-describes the still (causes drift):**

```
A woman in her thirties at a candle-lit table raises a wine glass slowly, her red dress catching the warm tungsten light from below, fingers tightening on the stem, gaze locked on the man across the table in his dark suit.
```

The model now tries to re-render the dress, the candle, the suit, the lighting — and drifts away from the source frame on each.

**After — motion + tethers only:**

```
First [0-2s]: She raises the wine glass slowly, fingers tightening on the stem, gaze locking on him across the table.
Then [2-5s]: She leans forward; mouth shaping words continuously, jaw moving, eyes narrowing.
Finally [5-8s]: She sets the glass down with a soft clink, hand stays on the stem.

Physical tether: wine glass stays in her right hand until the set-down; candle flame steady on the table; his posture across from her unchanged until Beat 3.
Environment: hair strands shift slightly in the warm air, candle flame flickers once on Beat 2.
Camera: slow dolly push-in across the table, focus locked on her hand on the stem.
```

Same scene. Half the tokens. No appearance drift.
