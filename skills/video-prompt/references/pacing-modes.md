# Pacing modes

Each mode has its own camera-energy rules and emotional beat structure. Pick one based on what the user is making.

---

## Narrative

Classic drama — hook, climax, resolution. Default mode for most short-form content.

### Rhythm law

After 2 dynamic shots → 1 calmer shot → back to dynamic.
No 3 consecutive slow cameras when tensionLevel > 5.

### Framing variation

Wide → extreme close-up → medium → wide. Don't stay in the same focal range for 3 shots.

### Per-beat camera energy

| Beat | Camera energy |
|---|---|
| **Hook** (first shot, must be aggressive) | Crash zoom / fast dolly in / whip pan into close-up. NEVER a slow establishing move on the hook. |
| **Tension / climax** | Dynamic, close, fast. Push-in, tracking, handheld, speed ramp. |
| **Breathing / resolution** | Slow camera (slow dolly, gentle pull-back), but NEVER fully static — even slow drift creates life. |

### Dopamine technique

For hook/tension/climax shots, structure the camera to create micro-tension-release within ONE shot:
- **Pattern A**: START wide (context) → SNAP to close-up on face/object (tension spike) → hold tight on reaction.
- **Pattern B**: START close on detail (mystery) → PULL BACK to reveal full scene (payoff).

---

## Action

Combat, chase, sport, intense physical activity.

### Rules

- Camera tracks subject motion physically — leading shots, FPV dives, side tracking
- Every shot has motion — locked is forbidden
- Speed ramps emphasize impact moments
- Handheld vibration on the hardest hits

### Per-beat

| Beat | Default camera |
|---|---|
| Setup | Side tracking + slow build, low-angle drone reveal |
| Tension | FPV drone dive, handheld shoulder-cam, leading shot |
| Impact | Crash zoom + speed ramp + bullet time |
| Reaction | Snap zoom to face + handheld + Dutch angle |
| Resolution | Crane up to wide + slow speed-up to real-time |

### Motion physics REQUIRED

For sport/equipment — name the specific physics. Kiteboard edge angles, BMX suspension compression, surfboard cut angles. Generic "rides the wave" produces incoherent output.

---

## Comedy

Timing-driven, often visual punchlines, exaggerated reactions.

### Rules

- Hold beats longer than narrative would — comic timing requires "wait for it" pause before the punchline
- Reactions are everything — focus on the reactor character's face, not the joker
- Camera is often static or very slow during setup, then SNAP to punchline reveal
- "Awkward zoom" (slow push-in on a deadpan face) is iconic comedy camera

### Per-beat

| Beat | Camera |
|---|---|
| Setup | Locked or subtle handheld, framing the situation |
| Tension / build | Slow dolly push-in on the reactor's face (awkward zoom) |
| Punchline | Snap zoom to the visual gag OR rack focus from setup to punchline |
| Reaction | Hold on the reactor's face for an extra 1-2 beats (longer than narrative would) |

### Forbidden in comedy

- Fast camera moves during the joke setup (kills timing)
- Cutting too quickly to the punchline (the wait IS the joke)

---

## Documentary

Candid, observational, slightly unposed.

### Rules

- Handheld shoulder-cam drift throughout — never locked
- Subjects often unaware of camera (look offscreen, don't address it)
- Available natural light only (no studio polish)
- Slight imperfection — light flicker, focus drift, slight overexpose
- Sound design is critical — describe ambient sound layers

### Per-beat

| Beat | Camera |
|---|---|
| Setup | Handheld observational shot, wide establishing |
| Subject talks / acts | Handheld medium, slight drift, rack focus if 2+ subjects |
| Action | Following shot or side tracking, handheld shaky if intense |
| Reveal | Slow handheld push-in, soft focus drift |
| Resolution | Wide pull-back via handheld, ambient sound rising |

### Documentary motion prompt template

```
Beat 1: {subject does what they would do unaware of camera}
Beat 2: {continued natural behavior, ambient detail}
Beat 3: {moment passes; subject moves on or settles}

Lighting: {available natural light only — name the source}
Camera: handheld shoulder-cam drift, slight focus float, available light only
```

---

## Timelapse / hyperlapse

Compressed time — change over hours, days, months.

### Rules

- Subject is usually environment / sky / construction / crowd
- People in foreground are often blurred motion (long-exposure feel)
- Light changes within the clip are the dramatic core (sunrise, sunset, day-to-night)
- Camera is either locked or hyperlapse-tracked (moving while time accelerates)

### Per-beat

| Beat | Camera + light |
|---|---|
| Start | Locked, time = T0, specific light state |
| Mid | Locked, time = T+hours/days; light has shifted |
| End | Locked, time = T+more; final light state |

OR for hyperlapse (camera moves while time accelerates):

| Beat | Camera + light |
|---|---|
| Start | Hyperlapse forward dolly, dawn |
| Mid | Hyperlapse continues, day |
| End | Hyperlapse continues, sunset / night |

### Timelapse template

```
Time-compressed sequence.
Beat 1 [0-Xs]: {scene at T0, light state described}
Beat 2 [X-Ys]: {scene at T+hours/days, light has shifted by D degrees, clouds traverse sky in seconds}
Beat 3 [Y-end]: {scene at T+final, light = end state}

Camera: locked / hyperlapse forward.
Light progression: {dawn → noon → sunset OR specific named states}
```

---

## Dialogue-scene

**When**: native-audio models (Veo 3.1, Sora 2, LTX-2) where dialogue IS the action. Talking-head shots, two-character argument, interview, confession.

**Rules**:
- Dialogue is the action — camera HOLDS (locked or subtle push-in, nothing punchier).
- Eye-line + lip + breath matter more than body motion. Frame the face.
- Shot-reverse-shot only via multi-shot block ([`multi-shot.md`](multi-shot.md)); inside one shot, hold one composition.
- Dialogue obeys the beat budget — see [`beat-structure.md`](beat-structure.md) § Beat structure with native dialogue.
- No competing SFX during speech beats. Drop ambient under the line.

**Per-beat camera**:
- Beat 1 (setup): static medium or slow push-in start. Face visible.
- Beat 2 (delivery): hold. No camera move during the line itself.
- Beat 3 (reaction): subtle settle. Optional rack focus to listener if two-shot.

**Template**:

```
Beat 1 (0-2s): <character physical setup — body settled, gaze locked, breath in>
Beat 2 (2-5s): <character delivers line>
  Character: "<line>"
  Ambient: <one bed, low>
Beat 3 (5-8s): <reaction — held tension or release>
  SFX: <one cue tied to action, if any>
Camera: static medium / slow push-in held throughout
```

See [`audio-prompting.md`](audio-prompting.md) for full dialogue/SFX/ambient grammar.

---

## Music-video

**When**: music or score leads the cut. Beat-synced camera punches, whip pans on transients, kinetic energy throughout.

**Rules**:
- Name the BPM or align camera beats to musical beats explicitly: "Beat 1 lands on the kick, Beat 2 on the snare hit, Beat 3 on the drop".
- Diegetic vs non-diegetic split — name the music source if in-world (record player, band on stage); otherwise it's score overlay.
- Camera moves on accents — whip pans on transients, crash zooms on the drop, freeze-frame on the iconic hit.
- Subject motion choreographed to the beat — gestures land on accents, not between them.

**Per-beat camera**:
- Beat 1 (downbeat): hard establish — wide or extreme close-up. Strong silhouette.
- Beat 2 (build): rising energy — push-in, orbit start, lateral track.
- Beat 3 (drop / final accent): release — whip pan, crash zoom, freeze frame, or fast pull-back.

**Template**:

```
Beat 1 (0-Xs, on kick): <wide or ECU setup, subject lands a defining pose>
Beat 2 (X-Ys, on snare/build): <energy rises, body moves on beats, camera matches>
Beat 3 (Y-end, on drop): <peak — whip pan / crash zoom / freeze>

Music: <BPM or beat reference — "120 BPM electronic, beat lands on every Beat 1">
Camera: <named moves aligned to beats>
```

Music-video pacing pairs naturally with `action` and `comedy` modes; rarely with `documentary`.

---

## How to pick

Default to **narrative** unless the user signals otherwise:

- User says "make a TikTok / Reel / Short" → narrative
- User says "fight scene" / "action sequence" → action
- User says "funny" / "comedy" / "meme" → comedy
- User says "real life" / "candid" / "documentary" → documentary
- User says "time passing" / "before and after" / "over a year" → timelapse

For 2+ second clips, only ONE mode applies per shot. Don't mix narrative + comedy in one prompt (the model can't render comedic timing AND dramatic camera at the same time).

---

## Cross-references

- Camera vocabulary: [`camera-vocabulary.md`](camera-vocabulary.md)
- CHARACTER FIRST + beat structure: [`beat-structure.md`](beat-structure.md)
- Per-model rules: [`models/_index.md`](models/_index.md) + per-tier files in [`models/`](models/)
- Native audio (dialogue / SFX / ambient): [`audio-prompting.md`](audio-prompting.md)
- I2V motion-over-still: [`i2v-prompting.md`](i2v-prompting.md)
- V2V edits: [`v2v-editing.md`](v2v-editing.md)
- Multi-shot: [`multi-shot.md`](multi-shot.md)
- Identity references: [`identity-references.md`](identity-references.md)
