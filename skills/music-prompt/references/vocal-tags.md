# Vocal tags — character, register, style, effects

The voice is the load-bearing element in 90% of songs. Without a tag, the model rolls a generic voice based on genre defaults. With tags, you steer voice character, register, phrasing style, and processing.

Base catalog lives in [`meta-tags.md`](./meta-tags.md#2-vocal-delivery). This file is the deep dive.

---

## Why vocal tags matter

Suno's default voice for "pop ballad" sounds different from its default for "indie folk" — but both defaults are generic. Tags collapse the variance:

- **No tag**: model picks. You roll dice.
- **`[Male Vocal]`**: gender locked. Timbre still random.
- **`[Male Vocal | raspy lead vocal | chest voice]`**: locked. Same prompt → consistent voice across re-rolls.

The further you go down the stack, the more controlled the output.

---

## Voice character tags

Descriptive identity. Pick ONE per stack.

| Tag | Character | When to use |
|---|---|---|
| `[Male Vocal]` | Generic male baseline | Default when gender matters but timbre doesn't |
| `[Female Vocal]` | Generic female baseline | Same, mirrored |
| `[Non-Binary Vocal]` <!-- v5.5 --> | Ambiguous, mid-register | Indie, electronic, when gender shouldn't read |
| `[Child Vocal]` | Young voice | Folk, lullaby, fantasy |
| `[Elderly Voice]` | Weathered, lower register | Storytelling, blues, gospel narration |
| `[Raspy Lead Vocal]` | Gritty texture, rock baseline | Rock, blues, country |
| `[Smooth Crooner]` | Round, mid-range, jazz-trained | Standards, smooth R&B, lounge |
| `[Belted Diva]` | Full-chest power, female | Pop ballad, gospel, musical theatre |
| `[Soft Indie Whisper]` | Breathy, intimate, close-mic | Indie folk, bedroom pop |
| `[Operatic Soprano]` | Classical, vibrato-heavy | Trailer music, neoclassical, art pop |
| `[Folk Storyteller]` | Conversational, mid-range | Folk, Americana, singer-songwriter |
| `[Hip-Hop Rapper]` | Rhythmic spoken delivery | Hip-hop, trap, drill |
| `[Trap Female Lead]` | Light, melodic, autotuned-adjacent | Modern trap, melodic rap |

---

## Register tags

Where in the voice the lead sits.

| Tag | Where it lives |
|---|---|
| `[Falsetto]` | Above the chest break — light, head-dominant |
| `[Head Voice]` | Upper register, lighter than chest, not strained |
| `[Mixed Voice]` | Blended chest and head — pop-ballad money zone |
| `[Chest Voice]` | Lower register, body-resonant |
| `[Belting]` | Full-chest power at the top of the range |

Pick one. Stacking `[Falsetto] + [Chest Voice]` is incoherent.

---

## Style tags

How the voice articulates.

| Tag | Articulation |
|---|---|
| `[Melismatic]` | Multiple notes per syllable, R&B / gospel runs |
| `[Staccato Phrasing]` | Short, detached notes |
| `[Legato Delivery]` | Smooth, connected notes |
| `[Talk-Singing / Sprechstimme]` | Halfway between speech and song |
| `[Whisper-Sing]` | Pitched whisper, melody preserved |

---

## Backing arrangement tags

Lead + supporting voices.

| Tag | Arrangement |
|---|---|
| `[Solo Lead]` | Single voice, no backing |
| `[Doubled Lead]` | Two takes of the same line, tight unison |
| `[Stacked Harmonies]` | 3-5 layered voices, modern pop signature |
| `[Choir]` | Multi-voice ensemble, classical or contemporary |
| `[Gospel Choir]` | Group call-and-response, full-throated |
| `[Backing Vocals]` | Supporting voices behind lead, lower in mix |
| `[Counter-Melody]` | Independent vocal line under the lead |
| `[Call-and-Response]` | Lead phrase + group answer |
| `[Crowd-Style Vocals]` | Group-sung, gang-vocal feel, anthemic |

---

## Vocal effects — by family

Stack at most 3 effect tags. Past 3 the model muddles which effect dominates.

### Autotune family

| Tag | Effect |
|---|---|
| `[Autotune]` | Audible pitch correction, T-Pain / modern trap signature |
| `[Heavy Autotune]` <!-- v5.5 --> | Maxed-out artifact, robotic |
| `[Subtle Pitch Correction]` | Polished but transparent — modern pop default |

Mini-recipe — trap verse:

```
[Verse | autotuned delivery | tuned male vocal | light reverb | stereo slapback]
```

### Lo-fi family

| Tag | Effect |
|---|---|
| `[Telephone Filter]` | Band-limited, narrow midrange — AM-radio feel |
| `[Megaphone]` | Distorted bullhorn, mid-frequency emphasis |
| `[Radio Filter]` | Broader telephone — FM-radio feel |

Mini-recipe — pre-chorus build:

```
[Pre-Chorus | telephone filter | building energy]
```

### Space family

| Tag | Space |
|---|---|
| `[Reverb-Wash Vocal]` | Long tail, atmospheric, often pre-delayed |
| `[Plate Reverb Vocal]` | Bright, dense, classic studio plate |
| `[Cathedral Reverb]` | Very long tail, vast church space |
| `[Slapback Delay]` | Single short echo, 50s rockabilly |
| `[Stereo Slapback]` | Slapback panned across the stereo field |
| `[Ping-Pong Delay]` | Echoes bounce L-R |

Mini-recipe — gospel climax:

```
[Chorus | belted female lead | gospel choir backing | hall reverb | crescendo]
```

### Distortion family

| Tag | Effect |
|---|---|
| `[Distorted Vocal]` | Hard clipping, aggressive |
| `[Tube Saturation]` <!-- v5.5 --> | Warm soft-clip on the voice |
| `[Bitcrusher Vocal]` | Digital lo-fi, 8-bit grit |
| `[Light Vocal Grit]` | Subtle raspy edge, not full distortion |

Mini-recipe — punk shouted chorus:

```
[Chorus | crowd-style vocals | distorted vocal | gang vocals]
```

### Pitch family

| Tag | Effect |
|---|---|
| `[Pitched Up]` | Sped or transposed up — Hyperpop signature |
| `[Pitched Down]` | Slowed or transposed down — phonk / chopped-and-screwed |
| `[Chipmunk Vocal]` <!-- v5.5 --> | Extreme upward pitch, cartoonish |
| `[Demon Vocal]` <!-- v5.5 --> | Extreme downward pitch, distorted |

Mini-recipe — hyperpop bridge:

```
[Bridge | pitched up | chipmunk vocal | glitch | supersaw lead]
```

---

## Mini-recipes — paste-ready

### Modern pop chorus

```
[Chorus | anthemic chorus | stacked harmonies | modern pop polish | wide stereo]
```

### Trap verse

```
[Verse | autotuned delivery | tuned male vocal | light reverb | stereo slapback | 808 sub bass]
```

### Indie whisper

```
[Verse | soft indie whisper | breath audible | warm tape saturation | dry vocal | acoustic guitar]
```

### Gospel climax

```
[Chorus | belted female lead | gospel choir backing | hall reverb | crescendo | modulate up]
```

### Rap hook

```
[Hook | hip-hop rapper | doubled lead | stereo slapback | 808 bass]
```

### Lo-fi melancholy

```
[Verse | soft indie whisper | telephone filter | vinyl crackle | rhodes]
```

---

## Anti-patterns

- **`[Autotune]` + `[Raspy]`.** They fight — autotune flattens transients, raspy needs them. Pick one.
- **`[Belted]` + `[Whisper]`.** Incoherent. The model averages and you get neither.
- **More than 3 vocal-effect tags.** `[Autotune | Telephone Filter | Reverb-Wash | Distorted | Pitched Up]` — model picks 1-2 and ignores the rest.
- **Naming a living artist's voice.** "Drake voice", "Beyoncé voice", "Bad Bunny voice" — blocked on Suno / Udio / Lyria, or silently scrubbed.
- **Naming a copyrighted song's vocal style.** Same — blocked.
- **Two character tags.** `[Raspy Lead Vocal | Smooth Crooner]` — pick one.
- **Two register tags.** `[Falsetto | Chest Voice]` — pick one.

---

## RU терминология

| RU | EN tag |
|---|---|
| Мужской вокал | `[Male Vocal]` |
| Женский вокал | `[Female Vocal]` |
| Хор | `[Choir]` / `[Gospel Choir]` |
| Бэк-вокал | `[Backing Vocals]` |
| Шёпот | `[Whisper]` / `[Whisper-Sing]` |
| Фальцет | `[Falsetto]` |
| Грудной регистр | `[Chest Voice]` |
| Микст | `[Mixed Voice]` |
| Бельтинг / громкая середина | `[Belting]` / `[Belted]` |
| Хриплый / с рыком | `[Raspy Lead Vocal]` / `[Light Vocal Grit]` |
| Оперный | `[Operatic Soprano]` |
| Мелизмы / R&B-роспевки | `[Melismatic]` |
| Рэп | `[Rap]` / `[Hip-Hop Rapper]` |
| Спокен-ворд / читка | `[Spoken Word]` |
| Дабл / удвоенный лид | `[Doubled Lead]` |
| Стак-гармонии | `[Stacked Harmonies]` |
| Автотюн | `[Autotune]` |
| Вокодер | `[Vocoder]` |
| Телефонный фильтр | `[Telephone Filter]` |
| Мегафон | `[Megaphone]` |
| Реверб-обмыв | `[Reverb-Wash Vocal]` |
| Холл / зальный реверб | `[Hall Reverb]` |
| Плейт-реверб | `[Plate Reverb]` |
| Слэпбэк | `[Slapback Delay]` / `[Stereo Slapback]` |
| Пинг-понг | `[Ping-Pong Delay]` |
| Питч вверх / вниз | `[Pitched Up]` / `[Pitched Down]` |

---

## Cross-links

- Full tag catalog: [`meta-tags.md`](./meta-tags.md)
- Instrument support for vocal arrangements: [`instrumental-tags.md`](./instrumental-tags.md)
- Mix-side vocal processing: [`mix-production-tags.md`](./mix-production-tags.md)
