# Song structure — sections, ordering, length budgets

Section headers gate dynamics, instrumentation density, and energy. Get the structure right and the model fills in coherent music; get it wrong and you get four minutes of arrhythmic verse.

---

## The 5-block universal structure

```
Intro → Verse → Chorus → Bridge → Outro
```

Two verses and two choruses are the safe minimum. Optional inserts:

- `[Pre-Chorus]` — build between verse and chorus
- `[Post-Chorus]` — tail after chorus, often instrumental or vocal hook
- `[Drop]` — EDM peak after `[Build]`
- `[Breakdown]` — stripped low-energy contrast section
- `[Interlude]` — short instrumental palate cleanser

Full tag list in [`meta-tags.md`](./meta-tags.md#1-structure).

---

## Length budgets per model

| Model | Default length | Max coherent | Notes |
|---|---|---|---|
| Suno v5.5 | ~4 min | ~8 min on Pro | Hard cap rises with subscription tier |
| Udio v4 | variable | ~10 min | Best long-form coherence in 2026 |
| Lyria 3 Pro | up to 3 min | 3 min hard cap | No section brackets — natural language only |
| ElevenLabs Music | variable | ~5 min | Single prompt, brackets read as style cues |
| Stable Audio 2.5 | up to 3 min | 3 min hard cap | Loop / stem focus, weak on long-form |
| MusicGen | up to 30s | ~2 min stitched | Loop-centric |
| Riffusion | variable | ~3 min | Image-prompt-based, weaker on structure |
| Mubert | variable | streaming | Generative ambient, no song structure |
| Sonauto v2 | ~3 min | ~5 min | Bracket dialect compatible with Suno |
| Tencent SongGeneration | ~3 min | ~4 min | Mandarin-first, supports Suno brackets |

---

## Section header rules

- **Each header on its own line.** Never inline with lyric text. `[Chorus] We light it up` is wrong — the model sings "Chorus" as a word.
- **Suno**: tag goes in the **lyrics box only**. The style box takes natural-language descriptors without brackets. Mixing breaks both.
- **Udio**: insert via `/` autocomplete inside lyrics. The autocomplete menu lists canonical tags only — use it instead of typing.
- **Lyria 3 Pro**: no brackets at all. Use natural language: "first verse / first chorus / bridge / final chorus" inside the prompt text. Structural sections come from the prompt narrative.
- **ElevenLabs Music**: single-prompt model. Brackets read as style cues; section words are inferred from the prompt structure.

---

## Combining a section header with delivery

Two legal forms.

Short form (Suno-friendly):

```
[Verse 1 - Whispered]
```

Stacked form (universal):

```
[Chorus | anthemic chorus | stacked harmonies | wide stereo]
```

Parameterized form (Suno v5+):

```
[Verse: whispered vocals, acoustic guitar only]
```

Pick one form per stack. Don't mix `[Verse 1 - Whispered | belted]` — the dash and the pipe both want to be the separator.

---

## Order templates by genre

### Pop ballad (safe default)

```
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Pre-Chorus]
[Chorus]
[Bridge]
[Chorus]
[Outro]
```

### EDM banger

```
[Intro]
[Build]
[Drop]
[Verse]
[Build]
[Drop]
[Breakdown]
[Build]
[Drop]
[Outro]
```

### Hip-hop

```
[Intro]
[Verse 1]
[Hook]
[Verse 2]
[Hook]
[Bridge]
[Hook]
[Outro]
```

### Indie folk

```
[Intro | acoustic guitar | warm tape saturation]
[Verse 1]
[Verse 2]
[Chorus]
[Verse 3]
[Chorus]
[Bridge | piano solo]
[Outro | fade out]
```

### Gospel

```
[Intro]
[Verse 1]
[Chorus | gospel choir]
[Verse 2]
[Chorus | gospel choir]
[Bridge | key change | modulate up]
[Chorus | gospel choir | belted | crescendo]
[Outro]
```

### K-pop (4th gen)

```
[Intro]
[Verse 1 | member A]
[Pre-Chorus | member B]
[Chorus | stacked harmonies | modern pop polish]
[Post-Chorus | rap]
[Verse 2 | member C]
[Pre-Chorus]
[Chorus]
[Bridge | beat switch | half-time]
[Chorus | key change | modulate up]
[Outro]
```

### Country

```
[Intro | pedal steel guitar | acoustic guitar]
[Verse 1]
[Chorus]
[Verse 2]
[Chorus]
[Instrumental Break | pedal steel guitar | fiddle]
[Bridge]
[Chorus]
[Outro | fade out]
```

---

## Length-of-section hints

Suno reads minimum lyric content per section:

- **Too short** (1 line): the model skips or extends with hummed melody.
- **Sweet spot**: 4-8 lines per verse / chorus.
- **Too long** (8+ lines): the model compresses, often dropping the last 2-3 lines.

For instrumental sections, use the header alone:

```
[Instrumental Break | guitar solo | 16 bars]
```

The bar count is a hint, not a contract. Suno honors it ~60% of the time.

---

## Anti-patterns

- **Inventing structure tags.** `[Verse 5]` in a 4-minute song — the model usually only writes 2-3 verses worth of content. Stick to `[Verse]` / `[Verse 1]` / `[Verse 2]` / `[Verse 3]`.
- **Skipping the Intro tag.** The model adds an intro anyway, often in the wrong style. Always declare one.
- **Bridge before verse.** Models often resequence to put the bridge late. If you want it early, write the section but expect the model to ignore order ~40% of the time.
- **No section headers at all.** The model rolls a default verse-chorus-verse structure based on the style box. You lose all control.
- **Duplicating choruses with different tags.** `[Chorus | dry vocal]` then `[Chorus | wide reverb]` — the model averages and renders both the same way.

---

## Paste-ready full template

```
[Intro | warm tape saturation | soft acoustic guitar]

[Verse 1 | soft indie whisper | minimal drums]
<4-8 lines>

[Pre-Chorus | building energy | strings rise]
<2-4 lines>

[Chorus | anthemic chorus | stacked harmonies | wide stereo]
<4-6 lines>

[Verse 2 | soft indie whisper | minimal drums | brushed snare]
<4-8 lines>

[Pre-Chorus | building energy | strings rise]
<same as before, or slight variation>

[Chorus | anthemic chorus | stacked harmonies | wide stereo]
<same>

[Bridge | half-time | piano solo | dry vocal]
<2-4 lines>

[Chorus | anthemic chorus | stacked harmonies | wide stereo | crescendo]
<final chorus>

[Outro | fade out | tape stop]
```

---

## Cross-links

- Tag catalog: [`meta-tags.md`](./meta-tags.md)
- Vocal delivery for each section: [`vocal-tags.md`](./vocal-tags.md)
- Lyrics-box mechanics: [`lyrics-conventions.md`](./lyrics-conventions.md)
