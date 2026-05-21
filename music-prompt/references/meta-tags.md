# Meta-tag taxonomy — canonical 2026 set

The de-facto grammar for AI music. Bracketed cues steer section identity, vocal delivery, instrumentation, mix, and FX. Suno set the standard; Udio, ElevenLabs Music, and Sonauto v2 read the same dialect. Lyria 3 Pro is the outlier (natural-language only).

Use exact tags from this taxonomy. Invented tags are silently dropped.

---

## What meta tags are

A meta tag is a bracketed cue placed inside the lyrics box. Format:

```
[tag]
[tag | tag | tag]
[Verse 1 - Whispered]
[Verse: whispered vocals, acoustic guitar only]
```

Three shapes:

- Single tag: `[Chorus]`
- Stacked tags with `|`: `[Chorus | belted | gospel choir | wide reverb]`
- Parameterized (Suno v5+): `[Verse: whispered vocals, acoustic guitar only]`

Tags belong in the lyrics box, on their own line, never inline with lyric text. See [`lyrics-conventions.md`](./lyrics-conventions.md) for the lyrics-box vs style-box split.

---

## Tag categories

Eight categories. One tag per category in a single stack — never two structure tags or two vocal-character tags fighting each other.

### 1. Structure

Section headers. Each on its own line. The model uses these to gate dynamics, instrumentation density, and energy.

| Tag | Role |
|---|---|
| `[Intro]` | Opening, usually instrumental or vocal-light |
| `[Verse]` / `[Verse 1]` / `[Verse 2]` | Story-driving section, lower energy than chorus |
| `[Pre-Chorus]` | Build between verse and chorus |
| `[Chorus]` | Hook section, peak vocal + harmonic density |
| `[Post-Chorus]` | Tail after chorus, often vocal hook or instrumental phrase |
| `[Hook]` | Hip-hop / pop alternative to chorus |
| `[Bridge]` | Contrast section, new chord movement or key |
| `[Breakdown]` | Stripped section, energy drop |
| `[Build]` / `[Build-Up]` | Tension rise toward drop or chorus |
| `[Drop]` | EDM peak, full-bandwidth impact |
| `[Interlude]` | Short instrumental palate-cleanser |
| `[Instrumental Break]` | Longer instrumental, often solo |
| `[Outro]` | Closing section |
| `[End]` | Hard stop marker |
| `[Fade Out]` | Gradual volume taper to silence |

### 2. Vocal delivery

How the voice is performed. See [`vocal-tags.md`](./vocal-tags.md) for deep-dive + recipes.

| Tag | Role |
|---|---|
| `[Male Vocal]` / `[Female Vocal]` | Voice gender baseline |
| `[Duet]` | Two leads, alternating |
| `[Choir]` | Multi-voice ensemble |
| `[Harmony]` | Parallel vocal lines |
| `[Backing Vocals]` | Supporting voices behind lead |
| `[Stacked Harmonies]` | Layered 3-5 voice stack |
| `[Rap]` | Spoken-rhythmic delivery |
| `[Spoken Word]` | Talked, not sung |
| `[Whisper]` | Breathy, low-volume |
| `[Belted]` | Full-chest power |
| `[Falsetto]` | Light upper register, head-dominant |
| `[Head Voice]` | Upper register, lighter than chest |
| `[Chest Voice]` | Lower-register, body-resonant |
| `[Scream]` | Distorted shouted delivery |
| `[Operatic]` | Classical-trained vibrato |
| `[Melismatic]` | Multiple notes per syllable, R&B-style runs |
| `[Raspy]` | Gritty texture |
| `[Ad-lib]` | Improvised vocal fills |
| `[Humming]` | Wordless melodic vocal |
| `[Anthemic Chorus]` | Big, communal, festival-energy chorus |
| `[Crowd-Style Vocals]` | Group-sung, gang-vocal feel |

### 3. Vocal effects

Post-processing on the voice. Stack at most 3.

| Tag | Effect |
|---|---|
| `[Autotune]` | Pitch correction, audible artifact |
| `[Vocoder]` | Robotic carrier-modulated voice |
| `[Pitched Up]` | Sped / transposed up |
| `[Pitched Down]` | Slowed / transposed down |
| `[Doubled]` | Two takes layered tight |
| `[Telephone Filter]` | Band-limited, AM-radio narrow |
| `[Megaphone]` | Distorted bullhorn lo-fi |
| `[Distorted Vocal]` | Overdrive on the voice |
| `[Reverb-Wash Vocal]` | Long tail, atmospheric |
| `[Delay Throw]` | One-shot echo on a phrase tail |
| `[Whispered Layer]` | Whisper take under the lead |
| `[Tuned Male Vocal]` <!-- v5.5 --> | Modern trap autotune signature |
| `[Light Vocal Grit]` | Subtle raspy edge |

### 4. Instrumental

Instrument cues, organized by family. Deep dive in [`instrumental-tags.md`](./instrumental-tags.md).

| Tag | Family |
|---|---|
| `[Guitar Solo]` / `[Piano Solo]` / `[Saxophone Solo]` / `[Synth Solo]` / `[Drum Solo]` / `[Bass Solo]` | Solo cues |
| `[808 Bass]` / `[808 Sub Bass]` / `[Sidechained Synth Bass]` | Modern low-end |
| `[Strings Rise]` | Cinematic riser |
| `[Percussion Break]` | Drums-only section |
| `[Hammond Organ]` / `[Rhodes]` | Vintage keys |
| `[Analog Synth]` | Warm subtractive synth lead/pad |
| `[Jangly 60s Guitar]` / `[Pedal Steel Guitar]` | Era-specific guitar |
| `[Orchestral Strings]` | Full string section |
| `[Accordion]` / `[Harp]` / `[Banjo]` / `[Trumpet]` / `[Sitar]` | Color instruments |
| `[Distorted Power Chords]` / `[Whammy Bar Bends]` / `[Heavy Distortion]` | Rock guitar texture |
| `[Bass Slide-In]` | Pickup-note bass entrance |

### 5. Mix / production

Sound-shaping, not note-shaping. Full catalog in [`mix-production-tags.md`](./mix-production-tags.md).

| Tag | Effect |
|---|---|
| `[Lo-fi]` / `[Hi-fi]` | Fidelity baseline |
| `[Vinyl Crackle]` / `[Tape Saturation]` | Era texture |
| `[Sidechain]` / `[Pumping Compression]` | Dynamic ducking |
| `[Bitcrusher]` | Digital lo-fi |
| `[Radio Filter]` | Band-limited mix |
| `[Wide Stereo]` / `[Mono]` | Stereo image |
| `[Hall Reverb]` / `[Plate Reverb]` | Reverb space |
| `[Ping-Pong Delay]` | Stereo bouncing echo |
| `[Gated Drums]` | 80s gated reverb signature |
| `[Analog Warmth]` | Tube/tape harmonics |
| `[Light Reverb]` / `[Stereo Slapback]` | Subtle space |
| `[Warm Baritone EQ]` <!-- v5.5 --> | Low-mid emphasis for low-voice leads |
| `[Light Snare Reverb]` | Subtle snare tail |
| `[Modern Pop Polish]` | Streaming-optimized contemporary mix |

### 6. Energy / dynamics

Time, intensity, and modulation.

| Tag | Effect |
|---|---|
| `[Crescendo]` / `[Decrescendo]` | Gradual swell / fade |
| `[Fade In]` / `[Fade Out]` | Section entry / exit |
| `[Silence]` | Beat of rest |
| `[Half-Time]` / `[Double-Time]` | Feel switch without BPM change |
| `[Tempo: slow]` / `[Tempo: fast]` | Tempo nudge |
| `[Key Change]` / `[Modulate Up]` | Harmonic lift |
| `[Energy: Building]` / `[Energy: Explosive]` | Intensity cue |
| `[Atmosphere: Dreamy]` / `[Atmosphere: Cyberpunk]` | Mood cue |
| `[Bass Drop]` | EDM-style impact |
| `[Emotional Build-Up]` | Pop-ballad swell |

### 7. Era / genre anchors

These live in the STYLE box, not in lyrics-box brackets. They anchor genre and decade without explicit genre labels.

| Anchor | Reads as |
|---|---|
| `80s Synthwave` | DX7 keys, gated reverb, Linn Drum |
| `90s Boom Bap` | Sampled jazz, MPC swing |
| `2000s Pop-Punk` | Power chords, melodic male lead |
| `2010s EDM Festival` | Big-room drops, sidechain pump |
| `60s Motown` | Tambourine, walking bass, group BVs |
| `70s Disco` | Four-on-the-floor, strings, slap bass |
| `Y2K R&B` | Snappy hi-hats, vocoder bridges |
| `Modern Drill` | Slidey 808s, syncopated hats |
| `Phonk` | Cowbell, distorted bass, Memphis chops |
| `Hyperpop` | Pitched vocals, supersaws, sugar-rush mix |
| `Bedroom Pop` | Lofi guitar, dry vocal, room mic |
| `Afrobeats 2024` | Log drum, syncopated kick, Pidgin phrasing |
| `K-Pop 4th Gen` | Multi-section, beat-switches, glossy mix |
| `Lofi Hip-Hop` | Vinyl crackle, jazz keys, dusty drums |
| `Future Bass` | Pitched-vocal chops, wide supersaws |
| `Modern Pop` | Polished mix, stacked harmonies, syncopated rhythm |
| `80s Glam Metal` | Big snare, wide guitars, anthemic chorus |

### 8. FX cues

Production accents and transitions.

| Tag | Effect |
|---|---|
| `[Riser]` / `[Sweep]` | Tension ramp |
| `[Vinyl Stop]` / `[Tape Stop]` | Speed-down stop |
| `[Glitch]` | Stutter / repeat edit |
| `[Reverse Cymbal]` | Backwards swell |
| `[Sub Drop]` / `[Sub Drop Impact]` | Low-end punch |
| `[White Noise]` / `[Layered White Noise Riser]` | Hi-band ramp |
| `[Impact Hit]` | Cinematic boom |
| `[Foley]` | Real-world sound layer |
| `[Crowd Cheer]` | Live-ambient layer |
| `[Vinyl Pop]` | Single needle-drop click |
| `[Octave Harmony Stack]` <!-- v5.5 --> | One-octave doubled vocal/lead |
| `[Reverb Tail]` | Held wash after a cut |

---

## Stacking rules

- **Max 4-8 tags per stack.** Past 8 the model dilutes. 4-6 is the sweet spot.
- **One tag per category.** Don't stack `[Verse]` + `[Chorus]`. Don't stack `[Whisper]` + `[Belted]`.
- **Order inside the stack** (left to right): core genre / structure → era → mood → instrument → mix/FX → vocal direction.
- **Separator**: `|` with single spaces inside one bracket. `[Chorus | belted | gospel choir | wide reverb]`.
- **Parameterized form** (Suno v5+ only): `[Verse: whispered vocals, acoustic guitar only]` — colon, then comma-separated. Use when the description is closer to a sentence than a tag list.

Example legal stack:

```
[Chorus | anthemic chorus | 2010s EDM festival | sidechained synth bass | wide stereo | belted]
```

Six tags, one per category. Reads cleanly.

---

## Anti-patterns

- **Stacking 8+ tags.** Dilution; the model averages and ignores half.
- **Mixing unrelated genres.** `[808 Sub Bass]` + `[Pedal Steel Guitar]` reads as "country trap fusion" — only legal if that's the deliberate genre.
- **Inventing tags.** `[Dubstep Drop]` is not in the canonical set. Use `[Drop | dubstep | wobble bass]` or just `[Drop]`.
- **Stage directions inside lyric text without brackets.** "Then she shouts the next line" gets sung as a lyric. Use `[Scream]` or `(shouting)`.
- **Conflicting moods.** `[Atmosphere: Dreamy]` + `[Heavy Distortion]` confuses the model. Pick one.
- **Naming living artists or copyrighted songs.** "Like Beyoncé", "in the style of Drake" — blocked or scrubbed on Suno, Udio, Lyria.
- **Two structure tags in one stack.** `[Verse | Chorus]` is incoherent — the model picks one arbitrarily.

---

## Cross-links

- Vocal delivery deep-dive: [`vocal-tags.md`](./vocal-tags.md)
- Instrument catalog: [`instrumental-tags.md`](./instrumental-tags.md)
- Mix and production: [`mix-production-tags.md`](./mix-production-tags.md)
- Lyrics-box conventions: [`lyrics-conventions.md`](./lyrics-conventions.md)
- Section ordering and length: [`song-structure.md`](./song-structure.md)
