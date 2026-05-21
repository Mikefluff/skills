# Audio prompting

Native-audio models (Veo 3.1, Sora 2, LTX-2) generate dialogue, SFX, and ambience alongside the picture. The grammar is different from picture-only prompts.

---

## When to use this file

When the target model supports native audio: Veo 3.1, Sora 2, LTX-2.

---

## The three audio layers

- **Dialogue** — character speech, lip-synced when face is on camera
- **SFX** — discrete sounds tied to discrete events (footsteps, glass clink, door slam)
- **Ambient** — continuous bed underneath everything (bar chatter, traffic, wind)

---

## Hard cap

**≤5 total audio elements per 8s clip.** Count dialogue lines + SFX + ambient beds. Beyond five, the model muddles them and ducks the dialogue.

---

## Dialogue syntax

Pattern — `Character: "line"` with the colon and double quotes. This exact form triggers Veo 3.1 lip-sync.

```
Sarah: "I told you this would happen."
```

Prosody adverbs go BEFORE the quote, never inside. The quote contains literal speech only.

```
Sarah, weary voice: "I told you this would happen."
Marcus, shouts: "Then why didn't you stop me?"
Sarah, laughs through tears: "Because I wanted to be wrong."
```

Speech budget — ≤8s of actual speech per 8s clip. Faster pacing produces clipped lip-sync (mouth shapes lag the audio).

---

## SFX syntax

Pattern — `SFX: <sound>, <sound>` comma-separated, **max 3 per beat**.

```
SFX: glass clink, chair creak
```

Diegetic vs non-diegetic:
- **Diegetic** (in-world) — name the source: `glass clink`, `door slam`, `footsteps on tile`
- **Non-diegetic** (score) — say it explicitly: `score swells`, `music cue rises`, `sting on the cut`

---

## Ambient syntax

Pattern — `Ambient: <single continuous bed>`. One source per beat.

```
Ambient: low bar chatter, distant
Ambient: wind through dry grass
Ambient: refrigerator hum, kitchen at night
```

Foreground/background routing:
- "cuts through" → foreground (loud, present)
- "in the distance" → background (low, atmospheric)

```
Ambient: rain in the distance
SFX: thunder cuts through
```

---

## Lip-sync rules

- Face must be **visible in frame** for sync to engage. Off-screen voice loses sync.
- **No competing SFX during dialogue beats** — drop SFX to silence or background under the line. The model can't duck audio mid-generation; you have to write it ducked.
- Shape delivery with **prosody adverbs**, not punctuation inside the quote. No ellipsis-acting, no all-caps screaming, no `...` for pauses — these are ignored or rendered weirdly.

```
WRONG — Sarah: "I... told you... this would... happen."
RIGHT — Sarah, halting voice: "I told you this would happen."
```

---

## Talking-head template

```
Beat 1 (0-2s): <character physical setup — body and face composition>
Beat 2 (2-5s): <character begins line>
  Character: "<line>"
  Ambient: <single bed, low>
Beat 3 (5-8s): <character finishes line, reacts physically>
  SFX: <one discrete cue tied to the action>
Camera: <one term — slow push-in / static medium / shot-reverse-shot>
```

---

## Two-character dialogue template

```
Beat 1: <Character A action + line>
  A: "<line>"
Beat 2: <Character B reacts physically + line>
  B: "<line>"
  Ambient: <bed>
Beat 3: <both held tension or resolution>
  SFX: <one cue>
Camera: <single move>
```

---

## Music-video block (score-led)

When music drives the cut, lock beats to musical hits.

- **BPM cue** — name what lands on what: "Beat 1 lands on the kick, Beat 2 on the snare, Beat 3 on the cymbal swell"
- **Diegetic vs non-diegetic split** — say which: "non-diegetic score, no in-world sound" OR "diegetic radio in the car, non-diegetic synth bed underneath"

```
Beat 1 (0-2s): <visual action lands on kick>
Beat 2 (2-5s): <action escalates through snare hits>
Beat 3 (5-8s): <resolution on cymbal swell>
Music: non-diegetic synth, 96 BPM, kick on Beat 1, snare on Beat 2.
```

---

## Anti-patterns

- More than 3 SFX in 8s → muddled mix, all sounds equally quiet
- Music + dialogue + ambient + SFX all at full volume → noise floor, dialogue unintelligible
- Quoting text without the `Character:` prefix → no lip-sync trigger, model treats it as narration
- Acting via punctuation or ellipsis inside the quote → ignored or rendered as literal stutter
- Asking for specific copyrighted song lyrics → refusal or scrambled approximation
- Off-screen voice while expecting lip-sync → no sync (face must be visible)
- Dialogue + loud SFX in the same beat → SFX wins, dialogue unintelligible

---

## Example (Veo 3.1 — full)

Wine-glass dinner, two-character argument.

```
Beat 1 (0-2s): Sarah sits across from Marcus at a candle-lit table, her fingers tightening around the wine-glass stem, jaw set, gaze locked on his face.
  Ambient: low bar chatter, distant
Beat 2 (2-5s): Sarah leans forward, mouth shaping words continuously.
  Sarah, weary voice: "I told you this would happen."
  Marcus holds still, throat working in one visible swallow.
Beat 3 (5-8s): Marcus drops his gaze, jaw tightens, hand closes around his napkin.
  Marcus, low voice: "I know."
  SFX: glass set down soft clink

Lighting: warm tungsten candle from below, dim pendant overhead.
Camera: slow dolly push-in across the table, focus on Sarah's hand on the stem.
```

Five audio elements total: 2 dialogue lines, 1 SFX, 1 ambient bed, 1 implicit silence under Marcus's line. Within cap.
