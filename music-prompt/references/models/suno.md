# Suno

The headline music model. v5.5 is GA, v4.5 is the free-tier fallback.

---

## Suno v5.5

**Strengths**: deepest tag taxonomy + community corpus, 12-stem WAV export (Pro+), Voices (clone your singing voice into Personas), Custom Models (fine-tune on your catalog, Pro/Premier, up to 3), Suno Studio DAW, Replace Section inpainting, Remaster, Cover.
**Weaknesses**: free tier locked to v4.5; credit-based pricing; >8 stacked tags dilute; artist-name prompts get scrubbed.
**Execute via**: `--execute --model suno-v5-5` (env: `SUNO_API_KEY` + `SUNO_API_ENABLED=1`) — Suno API.

GA March 27 2026. Lineage: chirp-crow.

### Syntax / Format rules

**Two-box UI** — the single most important Suno rule:

- **Style of Music box** — ≤1000 chars, **natural language only, NO brackets**. Brackets here are ignored or break the gen. Lead with genre, then era / vocal type / instrumentation / production qualities / mood.
- **Lyrics box** — 3000 chars. **ALL bracketed tags live here**, each on its own line, separated from lyrics by blank lines.

**Tag stacking with `|`** (v5+):
```
[Chorus | anthemic chorus | stacked harmonies | modern pop polish]
```
Cap at 4-8 tags inside one bracket — past that, signal dilutes.

**Parameterized form** (v5+):
```
[Verse: whispered vocals, acoustic guitar only]
[Drop: hard 808s, half-time, distorted bass]
```

**Ad-libs**: parentheses on their own line, ≤3 words.
```
(yeah)
(one more time)
```

**Repetition**: physically duplicate the line. `(x2)` is unreliable.

**Section headers** (canonical): `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Breakdown]`, `[Drop]`, `[Solo]`, `[Outro]`, `[End]`.

### Prompt template

**Style of Music box** (NL, no brackets):
```
{genre + sub-genre}, {era or scene}, {lead vocal type + texture}, {key instrumentation}, {production qualities}, {tempo feel}, {mood}
```

**Lyrics box** (brackets + lines):
```
[Intro | {1-2 stacked tags}]

[Verse 1 | {stacked tags}]
{4-8 lyric lines}

[Pre-Chorus | {stacked tags}]
{2-4 lyric lines}

[Chorus | anthemic | stacked harmonies | {extra tag}]
{4 lyric lines}
{4 lyric lines}

(ad-lib)

[Verse 2 | {stacked tags}]
{4-8 lyric lines}

[Chorus | anthemic | stacked harmonies | {extra tag}]
{4 lyric lines}
{4 lyric lines}

[Bridge: {parameterized form — short directive}]
{2-4 lyric lines}

[Outro | {stacked tags}]
{2-4 lyric lines}

[End]
```

### Example

**Style of Music box**:
```
modern pop ballad, 2020s mainstream, breathy female lead with intimate close-mic'd delivery, fingerpicked acoustic guitar, soft piano pad, subtle 808 sub on choruses, hybrid orchestral strings on the bridge, wide stereo reverb, polished radio mix, mid-tempo, melancholic but hopeful
```

**Lyrics box**:
```
[Intro | fingerpicked guitar | ambient pad]

[Verse 1 | whispered vocals | close-mic'd | sparse]
I left the porch light on for you
Counted every car that wasn't yours
The kettle whistles in another room
And I forget what I was waiting for

[Pre-Chorus | swelling pad | rising tension]
And the floorboards know my name
The walls know every shape of pain

[Chorus | anthemic chorus | stacked harmonies | modern pop polish]
So tell me where the morning goes
When nobody comes home
Tell me if you ever loved me
Or if I dreamt it all alone

(oh, alone)

[Verse 2 | whispered vocals | piano enters]
I packed your jacket in a paper bag
Wrote a letter that I'll never send
The cat still waits beside the door
Like she remembers how this ends

[Chorus | anthemic chorus | stacked harmonies | modern pop polish]
So tell me where the morning goes
When nobody comes home
Tell me if you ever loved me
Or if I dreamt it all alone

[Bridge: hybrid orchestral strings, half-time drums, lead vocal opens up]
Maybe love was always leaving
Maybe staying was the lie
Maybe I'm the porch light burning
Long after the cars go by

[Chorus | anthemic chorus | stacked harmonies | modern pop polish | final lift]
So tell me where the morning goes
When nobody comes home
Tell me if you ever loved me
Or if I dreamt it all alone

[Outro | sparse guitar | fade]
I dreamt it all alone

[End]
```

### Notes / Pitfalls

- Writing tags in the Style box: silently ignored or breaks the gen — keep brackets in Lyrics only.
- Burying genre past character ~1000 in the Style box: silent truncation, the model never sees it. Lead with genre.
- Inventing tags (`[Epic Drop Section]`) — model parses unknowns as freeform text, results drift. Stick to canonical headers + stacked descriptors.
- Mixing genres unintentionally — `breakbeats` in a country prompt will surface. Style box must be coherent.
- Naming artists ("in the style of Taylor Swift") — scrubbed. Describe traits instead (breathy, fingerpicked, confessional).
- More than ~8 tags inside one bracket dilutes signal — pick the 4-6 strongest.
- `(x2)` and "repeat last 4 lines" are unreliable — duplicate the lines verbatim.
- Voices feature: train a Persona from your own singing voice, then call it per gen.
- Custom Models (Pro/Premier, up to 3): fine-tune on your own catalog; pick at gen time.
- Replace Section: inpainting on a finished track. Make-Same-Length toggle locks the section length.
- Remaster: improves mix/clarity without changing arrangement or identity.
- Cover: style transfer over an existing track — keep the melody, swap the genre.
- Studio: full DAW with 12-stem WAV export — for serious producers, not casual gens.
- My Taste: passive personalization layer — gens lean toward what you've kept.

---

## v4.5 → v5 → v5.5 migration

- Brackets-in-Lyrics-box-only rule: unchanged across all versions.
- `|` tag stacking inside brackets: added in **v5**.
- Parameterized form (`[Verse: directive]`): added in **v5**.
- Voices (vocal cloning into Personas), Custom Models, Suno Studio DAW, Replace Section, Remaster, Cover: all **v5.5**.
- 12-stem export: **v5.5** (Pro+).
- v4.5 is still available as the free-tier model and as a stylistic fallback — it has a softer, less polished mix character some genres prefer.
- Migration tip: a v4.5 prompt usually runs on v5.5 unchanged; the new value is in stacking + parameterized sections, not in rewriting old prompts.
