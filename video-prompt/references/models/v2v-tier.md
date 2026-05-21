# V2V-tier models

Video-to-video: you provide existing footage, the model transforms it. ONE action verb per call — Add / Remove / Replace / Relight / Re-angle / Restyle / Extend. Stacking verbs in a single prompt is the #1 failure mode.

---

# Runway Aleph

**Strengths**: most flexible V2V transformation (Add / Remove / Replace / Relight / Re-angle / Restyle / Extend), reference-image control, ~$0.18/sec.
**Weaknesses**: max 5s per call; verb-stacking degrades output sharply.
**Execute via**: `--execute --model aleph` (env: `RUNWAY_API_KEY`) — Runway API.

## Format rules (mandatory)

- ONE action verb per call. Pick one of: **Add / Remove / Replace / Relight / Re-angle / Restyle / Extend**.
- State the desired outcome with specificity — target object, target state, scope.
- Reference image attaches as `style_reference` or `subject_reference`.
- Source footage is the look — describe the change, not the source.

## Runway Aleph template

```
Action: {ONE verb — Add / Remove / Replace / Relight / Re-angle / Restyle / Extend}
Target: {what in the source frame}
Outcome: {desired state, with named details}
Scope: {full duration / specific seconds / specific region}

[Optional] Reference: {attached image label}
```

## Example (Aleph — Relight)

Source footage: woman and man at candle-lit dinner table, scene already shot.

```
Action: Relight
Target: the entire scene
Outcome: shift from candle-lit warm interior to cold pre-dawn blue, candle still flickering but dominated by ambient blue daylight from an unseen window left of frame; condensation on the wine glass catches the cold light.
Scope: full 5s duration.
```

## Example (Aleph — Add)

```
Action: Add
Target: the dinner-table scene
Outcome: gentle snowfall drifting past the window behind the man, slow and steady, snowflakes catching the candle glow as they pass.
Scope: full duration, snowfall begins at second 0 and continues uninterrupted.
```

## Notes

- One verb per call is law. Need to Relight AND Add? Two calls, chained.
- Aleph does not regenerate identity — character stays the source character. Use Act-One if you need a different performance.
- Reference images carry style/identity weight; the prompt carries the action.
- **Official Aleph verb canon**: `add`, `remove`, `change`, `replace`, `re-light`, `re-style` (hyphenated form preferred in Runway docs). The skill's broader set (`Re-angle`, `Extend`) is supported but the docs lead with the six above. Source: [help.runwayml.com — Aleph Prompting Guide](https://help.runwayml.com/hc/en-us/articles/43277392678803-Aleph-Prompting-Guide).
- **Trimming**: Aleph defaults to the first 5s of your input. For longer source footage, trim to the relevant segment in the UI before submitting — Aleph won't pick the right window automatically.

---

# Runway Act-One

**Strengths**: performance transposition — capture facial performance from a source video, apply to a generated character.
**Weaknesses**: faces only (no full-body performance transfer); needs clear source performance.
**Execute via**: `--execute --model act-one` (env: `RUNWAY_API_KEY`) — Runway API.

## Format rules

- Provide the performance source video.
- Describe the TARGET character (the one who will inherit the performance) — not the source actor.
- Single performance per call.

## Act-One template

```
Performance source: {source video label}
Target character: {description — body, age, look — to render performing the source's facial action}
Target environment: {where the target character is}
[Optional] Reference: {target character reference image}
```

## Example (Act-One)

```
Performance source: actor_take_07.mp4 (woman delivering monologue, eyes narrowing, jaw tensing across 8s).
Target character: a woman in her thirties at a candle-lit dinner table, dark hair, fingers resting on a wine glass.
Target environment: warm tungsten candle from below, dim pendant overhead, condensation on the glass.
```

## Notes

- Use when you have a strong human performance you want on a different rendered identity.
- Pair with Aleph for environment changes after the performance is locked.

---

# Luma Ray 3 Modify

**Strengths**: V2V with Start + End keyframe control, Character Reference swap on existing footage, available inside Dream Machine.
**Weaknesses**: shorter durations than Aleph; single transformation per call. **Max input/output duration: 10s** (5s or 10s options) at 540p / 720p / 1080p tiers (Dream Machine). Ray 3.14 Modify (Jan 2026 update) adds native 1080p, 4× speed-up, improved motion consistency. Sources: [Luma Ray3 Modify user guide](https://lumalabs.ai/learning-hub/ray3-modify-user-guide), [Modify Video help](https://lumaai-help.freshdesk.com/support/solutions/articles/151000220119-how-do-i-use-modify-video-to-transform-footage-while-preserving-motion-).
**Execute via**: prompt-only — no native Luma adapter in v2.2. Workaround: `--execute --model fal-video` if Luma model is mirrored on fal.ai (env: `FAL_KEY`); else prompt-only.

## Format rules

- ONE action verb per call.
- Start + End keyframe support — provide both as anchors when shape-change is large.
- Character Reference: attach reference image to swap identity while preserving performance/motion.

## Ray 3 Modify template

```
Action: {ONE verb}
Target: {what in the source}
Outcome: {desired state}
[Optional] Start frame: {reference}
[Optional] End frame: {reference}
[Optional] Character reference: {identity image}
```

## Example (Ray 3 Modify — Replace)

```
Action: Replace
Target: the wine glass in the woman's hand
Outcome: a clear cocktail glass with a single ice cube, condensation on the rim catching the candle glow.
Scope: full duration.
Character reference: (none — keep source character).
```

## Example (Ray 3 Modify — Restyle)

```
Action: Restyle
Target: full scene
Outcome: 1970s film stock look — soft grain, warm magenta cast on highlights, slight halation on the candle flame, mild gate weave on motion.
Scope: full duration.
```

## Notes

- Start + End frames are the cleanest way to control large transforms (e.g., snow accumulating, light shifting from dusk to night).
- Character Reference swap: identity changes, performance + motion stay locked to source.

---

# Pika 2.2 — Pikaswaps / Pikadditions / Pikaframes

**Strengths**: cheap, fast, one function per call, clear single-purpose tools.
**Weaknesses**: 1080p ceiling; small object scale works best; large-object swaps drift.
**Execute via**: prompt-only — no native Pika adapter in v2.2. Workaround: `--execute --model fal-video --fal-model fal-ai/pika-text-to-video` (env: `FAL_KEY`) if mirror available.

## Format rules

- ONE function per call. Pikaswaps, Pikadditions, Pikaframes are separate verbs, not stackable.
- Specify exact target with masking/region cues where possible.

## Pikaswaps (object replacement)

```
Function: Pikaswaps
Target: {object in source frame}
Replacement: {object — described concisely}
Scope: {full clip / specific seconds}
```

### Example (Pikaswaps)

```
Function: Pikaswaps
Target: the wine glass in the woman's right hand.
Replacement: a clear cocktail glass with a single ice cube, condensation on the rim.
Scope: full 5s.
```

## Pikadditions (insert objects)

```
Function: Pikadditions
Target environment: {where in the source frame}
Object: {what to insert + placement}
Behaviour: {static / motion description}
```

### Example (Pikadditions)

```
Function: Pikadditions
Target environment: the candle-lit dinner table.
Object: a small bouquet of white roses in a clear vase, placed slightly left of the candle.
Behaviour: static, with a single rose petal drifting down across Beat 3.
```

## Pikaframes (keyframe interpolation)

```
Function: Pikaframes
Start frame: {image}
End frame: {image}
Duration: {seconds}
Motion description: {body parts, repeated action between frames}
```

### Example (Pikaframes)

```
Function: Pikaframes
Start frame: woman holds wine glass raised, mouth closed, gaze on man.
End frame: woman has set glass down with hand still on stem, mouth closed, gaze still on man.
Duration: 5s.
Motion: she lowers the glass slowly, fingers shifting on the stem, mouth opening once mid-motion as she begins speaking, jaw moving on each syllable.
```

## Notes

- Pikaswaps: keep replacement object roughly the same size as the source object to minimise drift.
- Pikadditions: the simpler the inserted object, the more reliable. Add complex objects via a second Pikadditions call.
- Pikaframes: works best when start and end share the same character pose family — large pose changes break interpolation.

---

## Universal V2V anti-patterns

- Stacking verbs ("Add snowfall and relight to dusk and restyle as 1970s film") — split into separate calls.
- Re-describing the source content — the source IS the look. Describe the change.
- Vague targets ("change the lighting") — name the source, name the new state.
- Using V2V to fix identity drift from a prior I2V — use Character Reference instead.
