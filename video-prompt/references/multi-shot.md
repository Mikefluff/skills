# Multi-shot prompts

Multiple shots in one generation. Sora 2, Seedance 1.0 Pro, Veo scene-extend, Kling Elements.

---

## When to use this file

When the model can render more than one shot per generation and you want a mini-scene instead of a single clip.

---

## The shot-block format

```
Shot 1 (3s, medium): <action beat>
Shot 2 (5s, close-up): <action beat>
Shot 3 (2s, wide): <resolution>

Style anchor: <one shared style sentence applied to all shots>
```

Each shot block carries: duration, framing, action beat. The style anchor at the end locks consistency across all shots.

---

## Transition vocabulary

Recognized by Sora 2 and most multi-shot models. Place between shot blocks.

- `new shot:` — hard cut
- `cut to:` — hard cut, same energy
- `match cut on [hand / eye / gesture]` — graphic match across shots
- `dissolve to:` — soft blend, time/place shift
- `whip pan to:` — fast motion blur transition

---

## Style anchor

One sentence at the **end** of the prompt that applies to all shots. Locks character appearance, lighting, color grade, era, film stock.

```
Style anchor: warm tungsten candle-light throughout, soft 35mm film grain, shallow depth of field, naturalistic skin tones.
```

Without this, lighting and grade jump between shots.

---

## Identity labels

For multi-character or recurring characters across shots — use named labels instead of re-describing physical appearance. Re-describing each time causes drift.

```
[ref:Sarah] — woman, thirties, dark hair, dark dress
[ref:Marcus] — man, forties, gray suit

Shot 1: [ref:Sarah] raises a wine glass.
Shot 2: [ref:Marcus] tightens his grip on the napkin.
```

Define each label once at the top OR rely on attached reference images. See `identity-references.md` for the full system.

---

## Per-model multi-shot limits

- **Sora 2** — ~3-5 shots per prompt, total 10-15s clip length
- **Seedance 1.0 Pro** — native multi-shot narrative, designed for it
- **Veo scene-extend** — extends an existing clip by N seconds; one continuation per call
- **Kling Elements** — multi-element references per scene, not multi-shot per se (each element can be a character, prop, style, environment)

---

## Template (paste-ready)

```
Shot 1 (3s, wide establishing): [ref:Sarah] sits across from [ref:Marcus] at a candle-lit dinner table; her fingers tighten on the wine-glass stem, gaze locking on his face.

cut to:

Shot 2 (3s, close-up on hands): [ref:Sarah]'s hand on the wine-glass stem, fingers shifting; [ref:Marcus]'s hand closes around his napkin, knuckles whitening.

cut to:

Shot 3 (4s, medium on Marcus): [ref:Marcus] drops his gaze, jaw tightens, swallows once, then lifts his eyes back to [ref:Sarah].

Style anchor: warm tungsten candle-light from below, dim pendant overhead, soft 35mm grain, shallow depth of field, naturalistic skin tones throughout.
```

---

## Anti-patterns

- Different physical descriptions in each shot — "a woman with dark hair" / "a brunette woman" / "a woman in her thirties" → character drift
- No style anchor → lighting, grade, and stock jump between shots
- Re-describing the same character physically in every shot → token waste, drift compounds per shot
- Too many shots in one prompt — Sora 2 caps around 5; beyond that, quality collapses
- Conflicting framing — Shot 1 wide, Shot 2 wide, Shot 3 wide → no visual rhythm; vary focal range
- Missing transition vocab between shots → model picks one shot or muddles cuts
- Style anchor at the top → some models drop it after the first shot; keep it at the end

---

## Example (Sora 2 — three-shot wine-glass scene)

```
Shot 1 (3s, wide establishing): [ref:Sarah] and [ref:Marcus] sit across from each other at a candle-lit dinner table. [ref:Sarah] raises a wine glass slowly, fingers tightening on the stem, gaze locking on [ref:Marcus] across the table.

match cut on the wine-glass stem:

Shot 2 (3s, close-up on hands): [ref:Sarah]'s fingers on the wine-glass stem, condensation glinting; [ref:Marcus]'s hand enters frame from the right, closes around the linen napkin, knuckles whitening.

cut to:

Shot 3 (4s, medium on Marcus): [ref:Marcus] drops his gaze to the napkin, jaw tightens, throat works in one visible swallow; he lifts his eyes back to [ref:Sarah], expression controlled.

Style anchor: warm tungsten candle-light from below, dim pendant lamp overhead, soft 35mm film grain, shallow depth of field, naturalistic skin tones, condensation on the wine glass throughout.
```

Three shots, 10 seconds total, one match cut and one straight cut, two ref-locked identities, one style anchor.
