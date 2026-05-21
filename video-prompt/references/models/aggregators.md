# Aggregators

Single interface, multiple backend models. Useful when the killer feature is a wrapper-level preset (named cameras, identity lock) rather than a single underlying model.

---

# Higgsfield AI Cinema Studio

**Strengths**: 70+ named camera presets, stackable up to 3 moves per shot, Soul ID character lock, Start + End frame keyframing, multi-backend routing.
**Weaknesses**: per-backend pricing inherited from underlying model; preset behaviour shifts subtly depending on which backend executes the shot.

## What it wraps

- Sora 2
- Veo 3.1
- Kling 3.0
- Seedance 2.0
- Wan 2.7

Pick a backend per shot, or let Higgsfield route automatically based on the preset.

## Killer features

- **Named camera presets** (70+): Bullet Time, Crash Zoom, 360 Rotation, FPV, Vertigo (dolly-zoom), Whip-Snap, Robo-arm, Speed Ramp, plus the standard set (push-in, pull-out, orbit, crane, dutch tilt, etc.).
- **Stackable moves**: up to 3 presets per shot. More than 3 collapses to noise.
- **Soul ID**: character identity lock across shots — register once, reference everywhere.
- **Start + End frame keyframing**: anchor opening and closing composition.

## Format rules

- Select preset(s) by exact name from the Higgsfield catalogue.
- Describe character action in Beat 1/2/3.
- Use Soul ID labels for identity instead of re-describing the character per shot.
- Backend selection (optional) — Higgsfield routes by default; override only when a backend's strengths matter (Sora 2 for audio, Hailuo via wrapper for physics, etc.). <!-- TODO: confirm Hailuo presence in Higgsfield backend list -->

## Higgsfield template

```
Backend: {optional — Sora 2 / Veo 3.1 / Kling 3.0 / Seedance / Wan 2.7}
Camera preset: {ONE or up to 3 stacked names from catalogue}
Soul ID: {registered identity label, optional}
Start frame: {reference, optional}
End frame: {reference, optional}

Beat 1: {action with body-part detail}
Beat 2: {escalation}
Beat 3: {resolution}

Lighting: {named sources}
```

## Example (Higgsfield — Crash Zoom + Vertigo on Veo 3.1)

```
Backend: Veo 3.1
Camera preset: Crash Zoom, then Vertigo (dolly-zoom out on Beat 3).
Soul ID: the_woman_v1
Start frame: woman_at_table_open.png

Beat 1: [the_woman_v1] raises the wine glass slowly at the candle-lit dinner table, fingers tightening on the stem, gaze locking on the man across from her.
Beat 2: she begins speaking — mouth shaping words continuously, jaw moving; he holds still, throat working in one swallow.
Beat 3: she sets the glass down with a soft clink, hand stays on the stem; the room appears to stretch as the camera vertigoes out.

Lighting: warm candle from below illuminating both faces, dim pendant overhead, condensation on the glass.
```

## Example (Higgsfield — Bullet Time, action scene)

```
Backend: Kling 3.0
Camera preset: Bullet Time (360 freeze-spin around subject on Beat 2).
Soul ID: the_runner_v1

Beat 1: [the_runner_v1] sprints across wet asphalt, feet pounding, water spraying with each step, jacket whipping behind.
Beat 2: he leaps — mid-air, suspended; rain droplets hang in space around him as the camera orbits 360.
Beat 3: he lands hard, knees bending to absorb, water exploding outward from the impact.

Lighting: cold sodium-vapour street lamps from above, neon shop signs casting magenta from frame-right onto wet asphalt.
```

## Notes

- Preset names are case-sensitive in the Higgsfield UI — use the catalogue spelling verbatim.
- Stacking >3 presets collapses motion; 2-preset stacks behave most predictably.
- Soul ID across multiple shots: register from a clean front-facing reference; the lock degrades on extreme angles.
- When dialogue + audio matter: select Sora 2 or Veo 3.1 as backend, add Dialogue / SFX / Ambient block (see `audio-tier.md`).
- Source: higgsfield.ai/ai-video.

---

## Universal aggregator anti-patterns

- Treating presets like prose ("camera does a bullet-time-ish move") — use the exact catalogue name or the wrapper falls back to generic.
- Stacking >3 presets — motion noise.
- Skipping Soul ID across a multi-shot scene — identity drifts shot-to-shot.
- Backend override without reason — Higgsfield's default routing is usually correct; override only for a specific strength.
