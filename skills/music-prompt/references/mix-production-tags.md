# Mix and production tags — shaping sound, not notes

Mix tags don't change the melody or chords — they change the SOUND of the rendering. `[Lo-fi]` + `[Vinyl Crackle]` puts the same song in a different decade. `[Wide Stereo]` + `[Modern Pop Polish]` puts it on streaming charts.

Base catalog lives in [`meta-tags.md`](./meta-tags.md#5-mix--production). This file is the deep dive.

---

## Why mix tags matter

Two prompts with identical lyrics + identical instruments + identical vocal tags produce two very different songs if the mix tags differ:

- `[Lo-fi | vinyl crackle | mono | warm tape saturation]` → bedroom-producer 2018 SoundCloud.
- `[Modern Pop Polish | wide stereo | sidechain | hi-fi]` → top-40 streaming chart 2026.

Mix tags collapse era, fidelity, stereo image, and frequency balance into 2-4 cues.

---

## Era / decade aesthetics

Pick one. Stacking eras is incoherent — `[1980s Gated Reverb]` + `[Modern Pop Polish]` confuses the model.

| Tag | Era signature |
|---|---|
| `[1960s Mono Mix]` | Centered mono, narrow band, vintage tape |
| `[1970s Analog]` | Wide warmth, tape compression, room mics |
| `[1980s Gated Reverb]` | Big snare, gated tail, wide synths, polished |
| `[1990s DAT Crisp]` | Bright digital, less compression than 2000s |
| `[2000s Loudness War]` | Smashed dynamics, hyped highs |
| `[2010s EDM Loud]` | Sidechain pump, brick-wall limiting, wide |
| `[Modern Pop Polish]` | Streaming-optimized, controlled dynamics, subtle saturation |

---

## Stereo width

| Tag | Width |
|---|---|
| `[Mono]` | Centered, no stereo image |
| `[Narrow]` | Most elements panned center, light spread |
| `[Wide Stereo]` | Modern pop default, full stereo deployment |
| `[Extreme Stereo]` | Hard-panned, immersive |
| `[Headphone Mix]` | Optimized for binaural, close-mic detail |

---

## Reverb types

Reverb places the sound in a SPACE. Pick one space per stack.

| Tag | Space |
|---|---|
| `[Hall Reverb]` | Large concert hall, long natural tail |
| `[Plate Reverb]` | Studio plate, dense bright reflections |
| `[Spring Reverb]` | Surf / dub signature, boingy short tail |
| `[Room Reverb]` | Small studio room, natural |
| `[Cathedral Reverb]` | Vast religious space, very long tail |
| `[Dry Vocal]` | No reverb on vocal — intimate, close-mic |
| `[Drenched in Reverb]` | Maximum wet/dry, ambient pop |

---

## Delay types

Delay creates rhythmic echoes. Pick one — stacking delays creates a mess of competing tempos.

| Tag | Delay |
|---|---|
| `[Slapback Delay]` | Single short echo, 80-120ms, rockabilly / lead vocal |
| `[Stereo Slapback]` | Slapback panned across stereo field |
| `[Ping-Pong Delay]` | Echoes alternate left and right |
| `[Dub Delay]` | Long, filtered, feedback-heavy — reggae / dub |
| `[Quarter-Note Delay]` | Tempo-synced quarter notes |
| `[Eighth-Note Delay]` | Tempo-synced eighth notes |

---

## Compression / dynamics

| Tag | Effect |
|---|---|
| `[Pumping Compression]` | Audible breathing, 80s rock / modern EDM |
| `[Sidechain]` | Ducked against the kick, EDM signature |
| `[Heavily Compressed]` | Tight, controlled, loud |
| `[Loose Dynamics]` | Quiet quiet bits, loud loud bits — preserved dynamic range |
| `[Dynamic Mix]` | Moderate compression, room to breathe |

---

## Saturation / distortion

| Tag | Texture |
|---|---|
| `[Tape Saturation]` | Warm soft-clip, analog tape harmonics |
| `[Analog Warmth]` | Generic vintage harmonic enhancement |
| `[Tube Saturation]` | Tube preamp soft-clip |
| `[Bitcrusher]` | Digital lo-fi, sample-rate / bit-depth reduction |
| `[Lo-fi Crackle]` | Surface noise + warmth |
| `[Vinyl Crackle]` | Pops and clicks layer |

---

## Filters

| Tag | Effect |
|---|---|
| `[Telephone Filter]` | Band-pass mid-range, AM-radio |
| `[Radio Filter]` | Broader telephone, FM-radio |
| `[High-Pass Sweep]` | Filter sweep removing lows over time |
| `[Low-Pass Sweep]` | Filter sweep removing highs over time |
| `[Auto-Filter]` | Tempo-synced filter modulation |

---

## Mix glue

Overall character of the production.

| Tag | Character |
|---|---|
| `[Glued Mix]` | Cohesive bus compression, elements feel like one performance |
| `[Loose Garage Mix]` | Raw, untreated, indie / garage rock |
| `[Studio Polish]` | High-budget professional finish |
| `[Demo Quality]` | Deliberately rough — songwriting demo vibe |
| `[Bedroom Producer]` | DIY home-studio aesthetic |

---

## Mastering hints

Hint at the loudness target / playback context.

| Tag | Target |
|---|---|
| `[Loud Master]` | Maximized, modern streaming |
| `[Quiet Master]` | Dynamic, audiophile target |
| `[Vinyl Master]` | Less low-end, conservative |
| `[Streaming Optimized]` | -14 LUFS, Spotify-friendly |
| `[Club Master]` | Sub-frequency emphasis, hot |

---

## Anti-patterns

- **`[Lo-fi]` + `[Modern Pop Polish]`.** Contradictory. Pick one.
- **`[Dry Vocal]` + `[Drenched in Reverb]`.** Contradictory.
- **3+ reverbs in one stack.** `[Hall Reverb | Plate Reverb | Cathedral Reverb]` → soup. One space per stack.
- **3+ delays in one stack.** Same problem.
- **Two era tags.** `[1980s Gated Reverb]` + `[2010s EDM Loud]` — pick one decade.
- **Named outboard gear.** "Lexicon 480L", "SSL bus compressor" — works inconsistently. The two exceptions: SSL bus glue and Lexicon hall — the model has trained on those names enough to honor them sometimes. Anything more obscure is silently ignored.
- **Asking for a specific producer's mix.** "Mixed like Jack Antonoff", "Finneas-style mix" — partial honor at best, often scrubbed.

---

## Quick-pick cheat sheet

Two-tag combos that cover 80% of intent:

| Intent | Era + Width |
|---|---|
| Modern streaming hit | `[Modern Pop Polish] [Wide Stereo]` |
| Vintage warm rock | `[1970s Analog] [Wide Stereo]` |
| 80s synth banger | `[1980s Gated Reverb] [Wide Stereo]` |
| Lofi bedroom | `[Lo-fi] [Narrow]` or `[Mono]` |
| Trap | `[2010s EDM Loud] [Wide Stereo]` |
| Acoustic intimate | `[Dry Vocal] [Room Reverb]` |
| Club banger | `[Club Master] [Sidechain]` |
| Cinematic | `[Cathedral Reverb] [Extreme Stereo]` |

If you can only spend 2 tags on mix, spend them on era + width.

---

## Recipe examples

### 2026 modern pop

```
[Chorus | anthemic chorus | stacked harmonies | modern pop polish | wide stereo | sidechain]
```

### 80s synthwave

```
[Chorus | belted | gated reverb drums | 1980s gated reverb | wide stereo | fm bell synth]
```

### Bedroom lofi

```
[Verse | soft indie whisper | lo-fi | vinyl crackle | warm tape saturation | dry vocal | rhodes]
```

### Cinematic trailer build

```
[Build | strings rise | cathedral reverb | extreme stereo | layered white noise riser | sub drop impact]
```

### Dub reggae

```
[Verse | spoken word | dub delay | spring reverb | sidechain | offbeat guitar]
```

---

## RU терминология

| RU | EN tag |
|---|---|
| Холл-реверб / зальный | `[Hall Reverb]` |
| Плейт-реверб | `[Plate Reverb]` |
| Спринг-реверб (пружинка) | `[Spring Reverb]` |
| Кафедральный реверб | `[Cathedral Reverb]` |
| Сухой вокал | `[Dry Vocal]` |
| Слэпбэк | `[Slapback Delay]` / `[Stereo Slapback]` |
| Пинг-понг дилей | `[Ping-Pong Delay]` |
| Даб-дилей | `[Dub Delay]` |
| Сайдчейн / sidechain | `[Sidechain]` |
| Пампинг-компрессия | `[Pumping Compression]` |
| Жёсткая компрессия | `[Heavily Compressed]` |
| Тейп-сатурация | `[Tape Saturation]` |
| Аналоговая теплота | `[Analog Warmth]` |
| Битрашер | `[Bitcrusher]` |
| Винил-краклер | `[Vinyl Crackle]` |
| Лофи | `[Lo-fi]` |
| Хайфай / чистый | `[Hi-fi]` |
| Моно | `[Mono]` |
| Широкое стерео | `[Wide Stereo]` |
| Гейтед-реверб 80-х | `[1980s Gated Reverb]` |
| Современный поп-полиш | `[Modern Pop Polish]` |
| Лимитер / громкий мастер | `[Loud Master]` |
| Стриминг-мастер | `[Streaming Optimized]` |
| Клубный мастер | `[Club Master]` |
| Виниловый мастер | `[Vinyl Master]` |

---

## Cross-links

- Full tag catalog: [`meta-tags.md`](./meta-tags.md)
- Vocal-side processing: [`vocal-tags.md`](./vocal-tags.md)
- Lyrics-box vs style-box rules: [`lyrics-conventions.md`](./lyrics-conventions.md)
