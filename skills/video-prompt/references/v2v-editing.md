# Video-to-video editing

Editing existing footage with V2V models. Action-verb-first grammar. One verb per pass.

---

## When to use this file

When prompting V2V editors: Runway Aleph, Luma Ray 3 Modify, Pika 2.2 (Pikaswaps / Pikadditions / Pikaframes).

---

## The action-verb-first law

Every V2V prompt begins with **one** of these verbs:

- **Add** — insert object / element
- **Remove** — delete object / element
- **Replace** — swap one thing for another
- **Relight** — change lighting condition
- **Re-angle** — change camera angle
- **Restyle** — change visual style
- **Extend** — lengthen the clip forward or backward

One verb per generation. Stack edits by chaining multiple passes.

---

## Single-change-per-pass

Doing two things in one call produces unstable results — the model splits attention and both edits come out half-baked.

```
WRONG — "Add snowfall and relight to dusk and remove the parked car."
RIGHT — Pass 1: Remove the parked car.
        Pass 2: Add snowfall over the empty street.
        Pass 3: Relight the whole clip to dusk.
```

Order matters. Remove before Add. Restyle and Relight last (they apply across everything).

---

## Per-model duration caps

- **Runway Aleph** — 5s max per generation
- **Luma Ray 3 Modify** — full clip, no hard cap in docs
- **Pikaswaps / Pikadditions / Pikaframes** — per-clip limits TBD; treat as short (≤5s) until tested

---

## Per-verb grammar

### Add

```
Add [object] at [position]. Make it [property]. Match the existing [lighting / style / perspective].
```

```
Add a black umbrella above the woman's head. Make it semi-translucent. Match the existing overhead street-light direction.
```

### Remove

```
Remove [object]. Fill the area naturally.
```

```
Remove the parked red car on the right. Fill the area naturally with the existing curb and street.
```

### Replace

```
Replace [original object] with [new object]. Match [perspective / scale / lighting].
```

```
Replace the coffee mug with a wine glass. Match perspective, scale, and the warm candle lighting.
```

### Relight

```
Relight to [target condition — golden hour / dusk / overcast / neon / candlelight]. Keep [composition / props / action] unchanged.
```

```
Relight to dusk — cool blue ambient, warm window glow from the right. Keep composition, props, and subject action unchanged.
```

### Re-angle

```
Re-angle camera to [new angle — low / high / over-shoulder / behind]. Keep [subject action] unchanged.
```

```
Re-angle camera to low-angle from her left side. Keep subject action and timing unchanged.
```

### Restyle

```
Restyle to [target style — anime / oil painting / watercolor / 1970s film / pencil sketch]. Preserve [identity / composition].
```

```
Restyle to 1970s 16mm film — grain, warm color shift, slight halation. Preserve identity and composition.
```

### Extend

```
Extend the clip [N seconds] [forward / backward]. <Beat description of what happens next>.
```

```
Extend the clip 3 seconds forward. Beat 1: she sets the glass down with a soft clink. Beat 2: she rises and turns toward the door, jacket catching the candle light.
```

---

## Reference-image control

Luma and Pika accept a reference image alongside the V2V prompt — for style or character lock. Say what the reference is for.

```
Restyle to match the attached reference image (color palette and grain). Preserve identity and composition.
```

```
Replace the man at the table with the character in the attached reference image. Match the existing lighting and perspective.
```

---

## Pikaswaps / Pikadditions / Pikaframes

- **Pikaswaps** — object replacement. One swap per call. Reference image optional. `Replace X with Y` grammar.
- **Pikadditions** — insert new objects. One addition per call. `Add X at [position]` grammar.
- **Pikaframes** — keyframe interpolation. Provide start frame + end frame; model interpolates motion between. Describe **how** the transition happens (motion arc, timing), not the end state.

```
Pikaframes — Beat 1 (0-2s): she begins to turn from the window.
              Beat 2 (2-4s): mid-rotation, hair catching the light.
              Beat 3 (4-5s): she lands facing the camera, ending on the reference end-frame.
```

---

## Template

```
<Action verb> <target>. Match <existing properties to preserve>. <Optional outcome specificity>.
```

---

## Anti-patterns

- Stacking verbs — "Add snowfall AND relight to dusk AND remove the car" → unstable, partial edits
- Vague targets — "Change the mood" → no action verb, no target, model freelances
- Re-describing the whole scene — wastes tokens, confuses the edit, drifts the unchanged regions
- Missing the "match" clause on Add / Replace → new element looks pasted in (wrong perspective, wrong light)
- Restyle without preserving identity — face drifts beyond recognition
- Re-angle that contradicts subject motion — model picks one and drops the other

---

## Example (Runway Aleph)

Source clip: 5s daytime street, parked cars, pedestrians, overcast.

**Before — stacked verbs (unstable):**

```
Add snowfall, relight to dusk, and remove the red car.
```

Result — snowfall is sparse, dusk lighting is half-applied, the red car is partially removed (silhouette ghost remaining).

**After — three sequential passes:**

```
Pass 1 — Remove the red car parked on the right. Fill the area naturally with the existing curb and street.

Pass 2 — Relight to dusk: cool blue ambient overall, warm tungsten glow from the shop windows on the left. Keep composition, props, and pedestrian action unchanged.

Pass 3 — Add light snowfall across the full frame. Make it slow-drifting, medium density. Match the dusk lighting and the existing overhead street-lamp direction.
```

Three clean passes. Each edit lands fully. Total time ≈ 3× single-pass cost; total quality far higher.
