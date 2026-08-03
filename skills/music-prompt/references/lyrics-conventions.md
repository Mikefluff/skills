# Lyrics conventions — how the box reads what you write

The lyrics box is parsed line-by-line. Section headers, lyric content, ad-libs, and stage directions each have a place — get the place wrong and the model sings the wrong thing.

---

## The lyrics box vs the style box

Two separate inputs on Suno (and conceptually on Udio, Sonauto, Tencent SongGeneration). Mixing the two confuses both.

| Input | Holds | Format |
|---|---|---|
| **Lyrics box** | Song content + section headers + vocal cues + ad-libs | Brackets for tags, parens for ad-libs, plain text for lyrics |
| **Style box** | Genre + mood + era + instrument descriptors | Natural language, no brackets |

Hard rule: brackets in the lyrics box, plain prose in the style box.

Examples:

```
[Lyrics box]
[Verse 1 | soft indie whisper]
Walking down the street tonight
The neon signs are humming bright

[Style box]
indie folk, 2020s bedroom pop, warm tape saturation, soft male vocal, acoustic guitar, brushed snare
```

Anti-example (do NOT do this):

```
[Lyrics box]
[indie folk, soft male vocal, acoustic guitar]
[Verse 1]
Walking down the street tonight
```

The genre tag belongs in the style box. Mixing dilutes both fields.

---

## Section headers on their own line

Always. Never inline.

```
[Chorus]
We light it up like fire
We light it up like fire
```

Not:

```
[Chorus] We light it up like fire
We light it up like fire
```

The second form sings "Chorus" as a lyric.

---

## Ad-libs

Vocal fills, exclamations, atmospheric phrases. Use parentheses on their own line, ≤3 words.

```
(yeah)
(uh)
(one more time)
(ad-lib: yeah, oh)
```

Place them between sections or between lines:

```
[Chorus]
We light it up like fire
(yeah)
We light it up like fire
(oh, oh)

[Verse 2]
...
```

Long ad-libs (≥4 words) are sung as full lyrics. Keep them short.

---

## Repetition

Models honor physical duplication, not notation. To repeat a chorus four times, write it four times.

```
[Chorus]
We light it up like fire
We light it up like fire
We light it up like fire
We light it up like fire
```

Not:

```
[Chorus]
We light it up like fire (x4)
```

`(x4)` is parsed inconsistently across Suno, Udio, and ElevenLabs. Some renders honor it, most ignore it.

---

## Language switching

Multi-language songs work on Suno and ElevenLabs Music. Less stable on Udio. Best practice: switch at SECTION boundaries.

Works:

```
[Verse 1]
Шёл по улицам ночным
Неон гудел над городом

[Chorus]
We light it up like fire
We light it up like fire
```

Doesn't work reliably:

```
[Verse 1]
Walking down the улицы tonight
Неоновые signs are humming bright
```

Mid-line code-switching gets mangled. Switch on section boundaries.

---

## Combined section + delivery tags

Two legal forms.

Short form (Suno-friendly):

```
[Verse 1 - Whispered]
```

Full stacking:

```
[Verse 1 | whispered | acoustic guitar only]
```

Don't mix the dash and the pipe in one tag:

```
[Verse 1 - Whispered | belted]
```

This is ambiguous. The dash wants to be a separator, the pipe wants to be a separator — pick one.

---

## Stage directions

NEVER in the lyrics box without brackets. The model will sing them.

Wrong:

```
[Verse 1]
She stood in the doorway
Then she shouts: We light it up!
```

The model sings "Then she shouts colon".

Right (option A — vocal cue tag):

```
[Verse 1]
She stood in the doorway

[Pre-Chorus | shouting | scream]
We light it up!
```

Right (option B — ad-lib direction):

```
[Verse 1]
She stood in the doorway
(shouting)
We light it up!
```

---

## Paste-ready Suno template

```
[Intro | warm tape saturation | soft acoustic guitar]

[Verse 1 | soft indie whisper | minimal drums]
Walking down the street tonight
The neon signs are humming bright

[Pre-Chorus | building energy | strings rise]
And I can feel it coming on

[Chorus | anthemic chorus | stacked harmonies | wide stereo]
We light it up like fire
We light it up like fire

[Verse 2 | soft indie whisper | minimal drums | brushed snare]
Past the corner, past the line
Every step is mine

[Bridge | half-time | piano solo | dry vocal]
And maybe I was wrong

[Chorus | anthemic chorus | stacked harmonies | wide stereo | crescendo]
We light it up like fire

(yeah, yeah)

[Outro | fade out | tape stop]
```

Style box for the same song:

```
indie folk-pop, 2020s bedroom pop crossover, soft male lead vocal, warm tape saturation, acoustic guitar, brushed snare, wide stereo, modern pop polish
```

---

## Pitfalls table

| Mistake | Why it breaks | Fix |
|---|---|---|
| `[Chorus] We light it up` (inline) | Model sings "Chorus" | Put header on its own line |
| Genre tags in lyrics box | Dilutes both boxes | Move to style box |
| `(x2)` repetition notation | Inconsistent honor | Duplicate the lines physically |
| `She shouts: ...` | Model sings the direction | Use `[Scream]` tag or `(shouting)` ad-lib |
| Mid-line code-switch | Mangled rendering | Switch at section boundary |
| 8+ tags in one stack | Model averages, ignores half | Cap at 4-6 |
| `[Verse 1 - Whispered \| belted]` mixed separators | Ambiguous parser | Pick dash OR pipe |
| Long ad-lib `(she sings softly as the wind blows)` | Sung as a full lyric | Cap ad-libs at 3 words |
| `[Verse 5]` in a 4-min song | Model writes 2-3 verses worth | Use `[Verse]` / `[Verse 1]` / `[Verse 2]` / `[Verse 3]` |
| `[Dry Vocal]` + `[Drenched in Reverb]` | Contradictory | Pick one |
| Naming a living artist | Blocked or scrubbed | Describe the style with tags instead |

---

## Per-model notes

### Suno v5.5

- Lyrics box: 3000 characters.
- Style box: 1000 characters on v4.5+. Silent truncation past 1000.
- Bracket dialect fully supported including stacking and parameterized form.
- Section + delivery dash form (`[Verse 1 - Whispered]`) supported.
- Persona / Style Reference (audio upload) optional — overrides style box partially.

### Udio v4

- Lyrics box accepts brackets via `/` autocomplete inside lyrics. The menu lists canonical tags only — use it instead of typing.
- Style box-equivalent is the prompt sidebar.
- Stacking with `|` works.
- Parameterized form less consistent than on Suno.
- Best long-form coherence in 2026 (~10 min).

### Lyria 3 Pro

- Separate lyrics field, no brackets idiomatic.
- Structure conveyed via natural language: "first verse / first chorus / bridge / final chorus".
- Style box equivalent is the prompt field — natural-language only.
- 3 min hard cap.

### ElevenLabs Music

- Single prompt field (no separate lyrics/style boxes).
- Brackets read as style cues. Section words inferred from prompt structure.
- Multi-language stable.
- Variable length up to ~5 min.

### Sonauto v2

- Suno-compatible bracket dialect.
- ~3 min default, up to ~5 min.

### Tencent SongGeneration

- Mandarin-first but supports Suno brackets.
- ~3 min default.

### Stable Audio 2.5

- 3 min hard cap.
- Loop / stem focus, weak on song-structure tags.
- Best used with sparse tag stacks — heavy stacking confuses it.

### MusicGen

- Up to 30s per generation, ~2 min stitched.
- Loop-centric — section tags less meaningful.

### Riffusion

- Image-prompt-based engine.
- Brackets honored partially.
- ~3 min.

### Mubert

- Streaming generative ambient.
- No song structure — ignore section tags.

---

## RU notes

| RU | EN convention |
|---|---|
| Текст / лирика — поле для слов и тегов | lyrics box |
| Стиль / описание — поле для жанра и звука | style box |
| Ад-либ / вокальная вставка в скобках | `(yeah)` / `(uh)` / `(ad-lib: yeah)` |
| Заголовок секции на своей строке | section header on own line |
| Повторение припева — физически дублируй строки | duplicate lines, not `(x2)` |
| Переключение языков на границе секций | switch at section boundary |
| Сценические ремарки — через тег `[Scream]` или ад-либ `(shouting)` | never as inline prose |

---

## Cross-links

- Tag catalog: [`meta-tags.md`](./meta-tags.md)
- Section ordering + length: [`song-structure.md`](./song-structure.md)
- Vocal delivery details: [`vocal-tags.md`](./vocal-tags.md)
- Instrument support: [`instrumental-tags.md`](./instrumental-tags.md)
- Mix and production: [`mix-production-tags.md`](./mix-production-tags.md)
