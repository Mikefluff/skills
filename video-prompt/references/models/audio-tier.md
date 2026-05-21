# Audio-tier models

Models with native synchronized audio (dialogue + SFX + ambient) generated in one pass — no separate audio post. Beat 1/2/3 still applies. Every example below includes a Dialogue / SFX / Ambient block.

---

# Veo 3.1 (Google)

**Strengths**: native synchronized audio (dialogue + SFX + ambience) in a single pass, 4K, ~120ms lip-sync accuracy, scene-extend, reference-image conditioning, T2V + I2V.
**Weaknesses**: shorter base clip than open-source rivals; premium pricing on full tier.

Released Oct 2025. 4K rolled out Jan 2026. Fast tier ~$0.15/sec. <!-- TODO: confirm Veo 3.1 full-tier price/sec -->

## Format rules (mandatory)

- Beat 1/2/3 inside the visual block.
- Audio split into THREE labelled lines: `Dialogue:`, `SFX:`, `Ambient:`. Lip-sync targets the Dialogue line.
- One camera direction line.
- Scene-extend: write the next 8s as a fresh Beat 1/2/3, reference the prior clip explicitly.

## Veo 3.1 template

```
Beat 1: {character A action — body parts, repeated motion}
Beat 2: {character B reaction + escalation, mouth shaping if speaking}
Beat 3: {resolution — final pose, breath, micro-gesture}

Dialogue:
  Character A: "{exact line}"
  Character B: "{exact line}"
SFX: {1-3 named sounds with timing}
Ambient: {room tone / location bed}

Lighting: {named sources with direction}
Camera: {one exact term}
```

## Example (Veo 3.1)

```
Beat 1: She raises a wine glass slowly across the candle-lit dinner table, fingers tightening around the stem, gaze locking on him; he sets his fork down, jaw clenching.
Beat 2: She begins speaking — mouth shaping words continuously, lips moving on each syllable, eyes narrowing; he holds still, throat working in one visible swallow, fingers pressing into his napkin.
Beat 3: She sets the glass down with a soft clink, hand staying on the stem; his hand stays gripping the napkin, knuckles white, breath held.

Dialogue:
  Her: "You knew. You knew the whole time."
  Him: "It wasn't like that."
SFX: glass clink at end of Beat 3; quiet fork-on-plate tap mid-Beat 1.
Ambient: low restaurant murmur, distant piano, faint cutlery clatter from neighbouring tables.

Lighting: warm tungsten table-candle from below illuminating both faces, dim pendant overhead, condensation glinting on the wine glass.
Camera: slow dolly push-in across the table, focus locked on her hand on the stem.
```

## Notes

- Veo 3.1 Fast: same parser, less detail, ~$0.15/sec — use for iteration, switch to full tier for final.
- Dialogue lines longer than ~6 seconds drift in lip-sync; split across Beat 2 + Beat 3.
- Reference images: attach as `subject_reference` for identity, `style_reference` for look.
- Scene-extend chains to ~24s by concatenating three 8s prompts referencing the prior frame.

---

# Sora 2 / Sora 2 Pro (OpenAI)

**Strengths**: synchronized audio + dialogue, multi-shot inside one prompt, Cameos (consented identity insertion), strong physics.
**Weaknesses**: less granular camera control than Kling; default toward "cinematic" unless specified.

Sora 2 Pro ~$0.75/sec. <!-- TODO: confirm Sora 2 base-tier price/sec --> <!-- TODO: confirm Sora 2 max clip length -->

## Format rules

- Natural-language paragraph as a director's note — Sora 2 parses prose.
- Audio block follows the same Dialogue / SFX / Ambient split.
- Multi-shot uses explicit cues: `new shot:` or `cut to:` — Sora 2 is one of the few that renders this correctly.
- Cameos: reference the consented identity by registered label.

## Sora 2 template

```
{One paragraph: characters, location, beat 1 → beat 2 → beat 3 embedded as continuous prose with body-part detail.}

[new shot: {transition + next beat block if multi-shot}]

Dialogue:
  Character A: "{line}"
  Character B: "{line}"
SFX: {sounds + timing}
Ambient: {bed}

Lighting: {named sources}
Camera: {term or movement}
```

## Example (Sora 2)

```
A woman in her thirties sits across from a man at a candle-lit dinner table. She raises a wine glass slowly, fingers tightening around the stem, her gaze locked on his face as she leans forward. She begins speaking — mouth shaping words continuously, jaw tense, eyes narrowing — while he holds still, throat working in a single visible swallow, his fingers tightening on his napkin. As her words land, she sets the glass down with a soft clink, hand staying on the stem; his hand stays gripping the napkin, knuckles white.

Dialogue:
  Her: "You knew. You knew the whole time."
  Him: "It wasn't like that."
SFX: glass clink at the end; faint cutlery tap mid-scene.
Ambient: low restaurant murmur, distant piano, neighbouring-table cutlery.

Lighting: warm tungsten candle from below illuminating both faces; a single pendant lamp casts dim ambient from above; condensation glints on the wine glass.
Camera: slow dolly push-in across the table, subtle handheld vibration, sharp focus on her hand on the stem.
```

## Notes

- Sora 2 is the only major closed model that reliably handles `new shot:` inside a single prompt — use for short scenes that would otherwise need editing.
- Cameos require pre-registered consent; do not invoke unregistered identities.
- For best physics: name the contact (`glass meets table`, `napkin compresses under fingers`) — Sora 2 picks up tactile prose.
- Sora 2 Pro: same parser, higher resolution + longer attention.

---

# LTX-2 / LTX-2 Distilled (Lightricks — open-source)

**Strengths**: first open-weights model with native 4K + synchronized audio, 20s clips at 50fps. Distilled variant runs on consumer GPU (~24GB VRAM). <!-- TODO: confirm LTX-2 Distilled exact VRAM floor -->
**Weaknesses**: newer ecosystem, fewer tutorials; identity drift on longer clips.

## Format rules

- Natural-language paragraph + explicit audio block.
- Audio: `Dialogue:`, `SFX:`, `Ambient:` lines accepted same as Veo/Sora.
- 20s clips: structure as Beat 1 (0-7s) / Beat 2 (7-14s) / Beat 3 (14-20s).

## LTX-2 template

```
Beat 1 [0-7s]: {character action — body parts, repeated}
Beat 2 [7-14s]: {escalation + reaction}
Beat 3 [14-20s]: {resolution}

Dialogue:
  Character A: "{line}"
  Character B: "{line}"
SFX: {named sounds with timing}
Ambient: {bed}

Lighting: {named sources}
Camera: {one term}
```

## Example (LTX-2)

```
Beat 1 [0-7s]: She raises a wine glass slowly across the candle-lit dinner table, fingers tightening around the stem, gaze locking on him; he sets his fork down, jaw clenching once.
Beat 2 [7-14s]: She begins speaking — mouth shaping words continuously, jaw moving on each syllable, eyes narrowing; he holds still, throat working in one swallow, his hand gripping the napkin, knuckles whitening.
Beat 3 [14-20s]: She sets the glass down with a soft clink, hand staying on the stem; his hand stays clenched, breath held, candle flame flickering between them.

Dialogue:
  Her: "You knew. You knew the whole time."
  Him: "It wasn't like that."
SFX: glass clink at the end of Beat 3; quiet fork tap mid-Beat 1.
Ambient: low restaurant murmur, distant piano, faint cutlery from neighbouring tables.

Lighting: warm tungsten candle from below illuminating both faces, dim pendant overhead, condensation glinting on the glass.
Camera: slow dolly push-in across the table, focus locked on her hand on the stem.
```

## Notes

- LTX-2 Distilled: same prompt format, lower fidelity, runs on a single consumer GPU. Use for iteration.
- Open-weights — safe for on-prem / regulated workflows.
- 50fps output: native slow-motion conform without retiming.
- For identity stability past 20s: chain two clips and use a still from the last frame as reference.

---

## Universal audio-tier anti-patterns

- Mixing dialogue inside the visual paragraph — split it into the labelled block, lip-sync targets that line.
- Stacking >3 SFX events — model picks 1-2 and drops the rest.
- Vague ambient (`some background noise`) — name the location bed.
- Dialogue longer than ~6s in one beat — drift accumulates; split.
