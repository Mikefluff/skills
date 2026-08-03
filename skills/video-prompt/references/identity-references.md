# Identity references

How to describe a referenced person or character across generations. The core rule — name the reference, don't re-describe physical traits.

---

## When to use this file

Any model with identity-reference capability: Sora 2 Cameos, Kling Elements, Runway Act-One, Higgsfield Soul ID, HunyuanCustom, Veo image references.

---

## The naming law

Once an identity is locked via cameo / element / ref image / performance source, the prompt should **name the character by label only**. Re-describing physical traits (hair, face, body, ethnicity) causes the model to drift away from the locked identity — it tries to render the description and the reference at the same time, and the description wins partially.

```
WRONG — "[ref:Sarah] with long brown hair and green eyes raises the wine glass."
RIGHT — "[ref:Sarah] raises the wine glass."
```

---

## Per-model identity systems

### Sora 2 Cameos

Consented identity insertion. The user uploads a Cameo of themselves (or someone with consent); the prompt references it by Cameo label.

```
[cameo:Sarah] sits at the dinner table.
```

### Kling Elements

Up to **4 reference images** per scene. Each labeled by role.

```
[ref:Character — Sarah]
[ref:Object — silver wine glass]
[ref:Style — 1970s 16mm film]
[ref:Environment — candle-lit dining room]
```

### Runway Act-One

**Performance transposition.** Capture facial performance from a source video (real actor), apply to a generated character. The source provides the performance (expressions, lip movement, timing); the target provides the appearance.

```
Performance source: <attached video of actor>
Target character: [ref:Sarah]
```

### Higgsfield Soul ID

Character lock across generations. Once Soul ID is created, every subsequent generation referencing that ID renders the same person, regardless of pose, wardrobe, lighting.

### HunyuanCustom

Multi-modal customization — accepts image, audio, video, and text inputs. Produces subject-consistent output that holds across formats. Useful for character + voice lock together.

### Veo references

Image references attached to the generation. The model uses the ref as identity anchor; the prompt names the subject by label only.

---

## Identity-label grammar

Pattern — `[ref:Name]` or model-specific (`[cameo:Name]`, `[soulid:Name]`). The model substitutes the locked identity.

First mention can include the label inline:

```
Sarah ([ref]) sits across from Marcus ([ref]) at the table.
```

After that, refer by name only:

```
Sarah raises the wine glass. Marcus tightens his grip on the napkin.
```

For multi-character — each gets a label.

---

## What you CAN describe

These change per shot and are expected in the prompt:

- **Wardrobe** — outfit changes are fine and won't break identity
- **Posture** — sitting, standing, leaning, the full range of body positions
- **Expression** — smiling, crying, jaw set, eyes narrowed
- **Action** — what they do, body-part-specific (the usual Beat 1/2/3 rules)
- **Mood / emotional state** — weary, furious, controlled, vulnerable

---

## What you CANNOT describe

These are locked by the reference. Mentioning them causes drift:

- **Hair color or length** — locked
- **Face shape, eye color, eye shape** — locked
- **Body type, height, build** — locked
- **Ethnicity, age** — locked
- **Distinguishing features** (freckles, scars, beard) — locked

---

## Template

```
Beat 1: [ref:Name] does <action>, wearing <wardrobe>, expression <emotional state>.
Beat 2: <escalation — body-part-specific action>
Beat 3: <resolution>

Camera: <one term>
```

---

## Anti-patterns

- "[ref:Sarah] with long brown hair" → overrides the ref, causes drift
- Re-attaching reference images mid-generation → identity confusion (especially on chained passes)
- Multiple references for the same character → confused identity (model averages them)
- Describing ethnicity or age alongside the ref → drift toward the description
- Putting the ref label inside a quote — `Sarah: "I told you, [ref:Sarah]..."` → broken; labels go outside speech
- Using the same label for two different references → identity collapse
- Forgetting to define the ref before first use → model treats it as plain text

---

## Example (wine-glass scene, two ref-locked characters)

References attached:
- `[ref:Sarah]` — character image
- `[ref:Marcus]` — character image

```
Beat 1 (0-2s): [ref:Sarah] sits across from [ref:Marcus] at a candle-lit dinner table, wearing a dark dress, expression weary. She raises a wine glass slowly, fingers tightening on the stem, gaze locking on Marcus.

Beat 2 (2-5s): Sarah leans forward, mouth shaping words continuously, jaw moving. Marcus, in a gray suit, holds still — throat working in one visible swallow, hand closing around his napkin.

Beat 3 (5-8s): Sarah sets the glass down with a soft clink, hand stays on the stem. Marcus drops his gaze, jaw tightens, then lifts his eyes back to her.

Camera: slow dolly push-in across the table, focus on Sarah's hand on the stem.
```

What's in the prompt — wardrobe (dark dress, gray suit), posture, expression, action.
What's NOT in the prompt — hair, face, eyes, body type, ethnicity, age. All locked by the refs.
