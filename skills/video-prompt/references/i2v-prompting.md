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

## Overlay-heavy i2v — 4-second budget (Veo Fast / Kling Fast / Sora Fast)

The dialect above (3-beat, 5-8s, multi-channel motion) is for cinematic i2v. **Use a different dialect when the source frame is an infographic, carousel slide, or composition where small text / stamps / typography MUST survive untouched.** The carousel-slide-as-source case is the high-risk failure mode — text wobbles, stamps re-render, characters morph.

### The 10 rules for overlay-heavy i2v on fast models

1. **Two sentences max** — `<one subject micro-verb>. <one global lock + style anchor>.` Don't paragraph.
2. **One motion verb per shot.** Pick exactly one: subject micro-gesture OR camera drift OR ambient light shift. Never combine. Stacking three motions is the #1 cause of "absurd" output.
3. **Quote locked text verbatim**, e.g. `Maintain the text "ОТВЕТСТВЕННОСТЬ = ДОХОД" on screen unchanged throughout.` Quoting is more reliable than "all text stays still".
4. **One global lock sentence** covers ALL props/text/overlays: `Keep everything else still. Maintain the style of the image.` (verbatim — works on Veo 3.1.)
5. **Ban rhetorical adjectives.** No `prosecutorial smirk deepening`, `cold-eyed knowing nod`, `pulses with weight`, `flashes brighter in sequence`. The model stages rhetoric literally and badly. Use measurable physical verbs only: `blinks once`, `head turns 5 degrees left`, `taps surface once`, `slow inhale`.
6. **Front-load identity in 8-15 words** before the action verb — age, build, hair, attire. Locks face/hands against morphing.
7. **Cap the prompt at ~80 words.** Over 150 words and the model re-renders the source frame instead of animating it — overlays melt, text mangles.
8. **Never name locked props by negation.** Don't write `the stamps don't move` — that summons them. Let the global lock cover all overlays implicitly.
9. **4 seconds, not 8**, on Fast variants when overlays are heavy. 8s multiplies drift exposure.
10. **Strip punitive / legal / financial verdict language** from the prompt body. Words like `REJECTED`, `DEBTOR`, `GRADE F-1`, `DEFAULT`, `BLACKLISTED`, `INCLUSIONS DETECTED` trip the safety filter and return `no videos`. If those terms are baked into the source image, that's fine — filters scan the PROMPT, not the image. Use neutral or fictional in-world codes (`ARCHIVED`, `SEALED`, `ZK-04`) when you must reference them.

### Template (overlay-heavy, 4s)

```
<identity 8-15 words: same character, age, build, hair, attire as in the source frame>, <one physical micro-verb, one degree of freedom>. Keep everything else still. Maintain the style of the image. <optional: Maintain the text "<exact string>" on screen unchanged throughout.>
```

### Before / after — rewriting an overlay-heavy shot

**Before (294 words, 5 stacked motions, 3 rhetorical adjectives, punitive labels — produces wobble + content-filter risk):**

```
The same 3D-cartoon character seated behind the bench in the lower-right of the frame slowly raises the critical-red rubber stamp tool in his hand and presses it down once over the bottom of the certificate where 'REJECTED · DEBTOR-MINDSET' is stamped, prosecutorial gemmologist's expression. The four 'GRADE F-1' / 'GRADE F-2' / 'GRADE F-3' / 'GRADE F-4' red stamps along the right margin of the four grading rows flash brighter in sequence top to bottom (РАЗОЧАРОВАНИЕ → РАЗДРАЖЕНИЕ → ОЗЛОБЛЕННОСТЬ → ВИКТИМНОСТЬ). The brass 10× jeweler's loupe resting on the corner of the certificate catches a slow incandescent glint. The warm brass desk-lamp pool of light shimmers very slowly. All text — the gold-foil 'ШКАЛА ВКЛЮЧЕНИЙ' headline, the certificate header [...], and the carousel markers '3 из 5' / 'листай →' — stays perfectly still and crisp.
```

**After (52 words, 1 motion, 0 rhetoric, 0 punitive labels — locked):**

```
The same red-bearded man in a wide-brim hat seated at the gemmologist's bench, taps a small brass stamp tool down once onto the paper. Keep everything else still. Maintain the style of the image.
```

The source frame already carries the certificate, stamps, text, headline. The prompt now describes ONLY what changes — one hand, one tap. Everything else is held by the global lock + style anchor.

### Veo 3.1 Fast — content filter heads-up

If the source image already shows punitive / legal / grading / financial-judgement language, you can keep it in the image but **strip it from the prompt body**. The safety filter scans the prompt text, not the rendered image. Returns of `no videos` are usually filter hits — silently dropped. Rephrase, don't escalate.

### Text-overlay preservation — the Veo 3.1 `last_frame` lever

The highest-ROI mechanism Google ships for constraining drift in i2v is **identical first and last frames**. Veo 3.1 accepts `last_frame` in its `GenerateVideosConfig`. Setting `last_frame == image` forces the model to interpolate back to the exact source pixels at the end of the clip — typography drift collapses because the model has nowhere to drift TO.

**How to use it:**

- In the shot's `kwargs`, set `"lock_first_last": true` — the runner's `google_video.py` provider reads this flag and passes the source frame as both `image` and `last_frame` to the Veo API.
- Add `"negative_prompt": "text warping, glyph distortion, melting letters, flickering text, re-rendered text, subtitle, caption overlay, watermark change, blurred text, deformed letters, no subtitles"` — Veo's negative-prompt parameter expects phrases (not negations like "no X").
- In the prompt body, name overlays explicitly as static graphics: `The Russian headline "<EXACT TEXT>" at the top is a static printed graphic element. The paper-tape caption at the bottom is a fixed printed sticker.` Veo treats unnamed overlay text as instructions and tries to act on it; naming it as a graphic element pins it.

**Why it works**: per Google's docs, `last_frame` is "the only documented mechanism for constraining drift in i2v" (paraphrased from the Vertex AI / google-genai `GenerateVideosConfig` field docs). The model performs a kind of frame interpolation between `image` and `last_frame`; when they're identical, the entire clip is bookended by the same overlay-pixel state, so text wobble has nowhere to land.

**Fallback**: some preview model IDs (specifically `veo-3.1-fast-generate-preview` at certain dates) reject `last_frame` with "Parameter Not Supported". The provider auto-retries without `last_frame` on that specific error — your shot still ships, just without the bookend. Other failures bubble up.

**When to skip**: if your shot intentionally ends in a different visual state from frame 0 (rare for overlay-heavy carousel slides — usually the slide IS the static composition + ONE micro-gesture), don't set `lock_first_last`. For carousel-to-reel discipline though, lock_first_last is the default.

**Sources for the lever**:
- Vertex AI Veo i2v with first/last frames: <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames>
- google-genai `GenerateVideosConfig`: `last_frame` — "Image to use as the last frame of generated videos. Only supported for image to video use cases."
- Forum: <https://discuss.ai.google.dev/t/veo-3-1-last-frame-parameter-not-supported/107529> — model-id gating.

### The contact-motion rule (spatial-anchor trap)

If the source frame shows a character interacting with a prop (signing, stamping, pointing, tapping, touching), do NOT describe the motion as **interaction with the target**. Describe it as **motion of the hand alone**. Naming the target forces the model to re-resolve where the target is relative to the hand, and it often breaks position — the stamp lands on empty desk, the pen taps air, the finger points off-screen.

**Wrong (target-anchored — re-grounds the target):**
- "taps the stamp tool down once onto the paper" → stamp lands wrong spot
- "points at the empty signature line" → finger drifts off the line
- "lifts a small stone with the brass tweezers and brings it to his eye" → tweezers grab wrong object

**Right (subject-anchored — motion of the hand only):**
- "the hand holding the stamp lowers 3 cm in place once"
- "the index finger extends forward once"
- "the hand holding the tweezers raises slowly toward the face"

The source frame already shows where the hand is, what it's holding, and what's beneath it. Describing only the hand's motion preserves the spatial relationships baked into the image. Describing the contact event forces re-grounding.

**Rule of thumb**: prepositions like *onto*, *into*, *at*, *toward*, *across*, *over* are red flags for spatial re-grounding. Replace with **in place**, **forward**, **down**, **up** — pure directional motion of the hand.

### When in doubt, motion budget

For a 4s overlay-heavy clip, you get exactly **one of these three slots**:
- **(a)** one character micro-gesture, OR
- **(b)** one slow camera drift (`slow dolly-in 3% over 4 seconds` / `gentle handheld micro-sway`), OR
- **(c)** one ambient light or material shift (`slow flicker on the candle`, `silk sheen drifts`).

Pick **one**. Don't try (a) + (b) + (c). The model will collide them.

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
