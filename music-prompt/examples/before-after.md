# music-prompt — calibration before/after pairs

Six paired examples covering pop, drill, jazz fusion, orchestral, vocal-realism, and an RU example. Each shows a weak prompt and the rewrite this skill should produce.

---

## Example 1 — Anthemic modern pop chorus (Suno v5.5)

### Before (weak)

```
upbeat pop song about freedom
```

What's wrong:
- "Upbeat pop" — no BPM, no era, no vocal gender
- "About freedom" — theme without scene, no concrete imagery
- No section structure — Suno will guess at form
- No tag stacks — production stays generic

### After (Suno v5.5)

**Style box**

```
Anthemic modern pop, polished production, female lead vocal with stacked harmonies, four-on-the-floor kick, soaring synth lead at the chorus, bright handclaps, ~120 BPM, radio-ready mix.
```

**Lyrics box** (chorus-first composition — write the chorus, build verses toward it)

```
[Intro | modern pop | synth pluck | snap fx | 120 BPM]

[Verse 1 | pop verse | female lead vocal | sparse production | piano and pulse bass]
Twelve years of waiting at a kitchen-table light
Now I'm packing every promise into a single one-way flight

[Pre-Chorus | rising synth pad | drum build | filter sweep]
I can feel the engine running in my chest
Every red light turning into yes

[Chorus | anthemic chorus | stacked harmonies | modern pop polish | soaring synth lead | four-on-floor]
RUN, this is what running looks like
RUN, with the morning on my side
Every wall I ever built is in the rear-view burning bright
RUN, this is what running looks like tonight

[Verse 2 | pop verse | doubled vocal | layered synth pluck | clap on 2-and-4]
Used to apologize for taking up the air I breathe
Now my name's the only thing I owe and the only thing I keep

[Chorus | repeat with full production]

[Bridge | half-time | piano and vocal only | breathy intimate]

[Final Chorus | key change up a step | full mix | ad-lib runs | gang vocal "RUN!"]

[Outro | synth pluck reprise | reverb tail | fade]
```

### Deltas applied

- "Upbeat pop" → BPM (120), vocal gender (female + stacked harmonies), era ("modern"), instrumentation (four-on-floor, synth lead, claps)
- Theme "freedom" → concrete scene (kitchen-table light → one-way flight → rear-view burning)
- Added full section structure with `[Section | tag stack]` formatting
- Wrote the chorus FIRST, then verses leading into it — pop's load-bearing piece
- Key-change modulation at final chorus — pop-anthem convention named explicitly
- Bridge stripped to piano + vocal — dynamic contrast the model otherwise forgets

---

## Example 2 — Drill verse with sliding 808s (Suno v5.5)

### Before (weak)

```
drill song
```

What's wrong:
- No drill sub-genre (UK / Brooklyn / Chicago all sound different)
- No BPM — drill lives narrowly at 138-150
- No vocal direction — model defaults to generic rap delivery
- No mention of the load-bearing element (sliding 808s + dark piano motif)

### After (Suno v5.5)

**Style box**

```
UK drill, dark menacing piano motif, sliding 808 bassline, hi-hat triplets, syncopated kick on the off-beat, half-time feel, male rap vocal with London inflection, ~140 BPM, low-end heavy, atmospheric reverb on the piano.
```

**Lyrics box** (original lyrics — no copyrighted lines)

```
[Intro | drill | dark piano motif | sliding 808 entry | 140 BPM]
(yeah, yeah)

[Verse 1 | UK drill | male rap vocal | hi-hat triplets | sliding 808 | half-time]
Block-cold winter, breath cuts the air like a blade
Phone on silent in a stairwell, plans don't get re-made
Same names on the same lips, same rain on the same brick
Watch the kettle scream a verse while the city ticks

[Hook | drill hook | doubled vocal | sliding 808 emphasis | dark piano lead]
Same road, same rain, same name on the wall
One slip in this city and your whole life can fall
(brrt)

[Verse 2 | drill verse | menacing piano | sub bass | aggressive flow]
Headphones loud so the night feels less wide
Concrete keeps its secrets, that's the only side
Brother told me young, "Keep your circle the size of a fist"
Now I count the friends I've got on a one-hand list

[Outro | piano motif tail | reverb wash | 808 sub fade]
```

### Deltas applied

- "Drill song" → "UK drill" (specific sub-genre with its own 140 BPM + half-time signature)
- Added BPM, vocal accent ("London inflection"), and the two load-bearing elements (sliding 808 + dark piano motif)
- Section structure with tag stacks per section — drill hooks especially benefit from `| sliding 808 emphasis |` reminding the model
- Original lyrics referencing genre tropes (block, stairwell, kettle) without copying any known track
- "Brrt" ad-lib placed at end of hook — drill convention named explicitly

---

## Example 3 — Long-form jazz fusion track (Udio v4)

### Before (weak)

```
jazz instrumental, long
```

What's wrong:
- "Jazz" covers 100 years and 50 sub-genres — must specify era + instrumentation
- "Long" — no minute count, no section structure to fill the time
- No tempo or time signature — jazz fusion is famous for odd meters
- Wrong model for "long" — Suno tops at ~8 min and drifts; Udio v4 holds coherence to 10-15 min

### After (Udio v4)

**Why Udio**: Udio v4 is the only model that holds a coherent 10+ min instrumental without dropping the harmonic thread. Suno would fragment around the 5-min mark; Lyria 3 Pro hard-caps at 3 min per generation.

**Style prompt** (Udio's single-prompt format)

```
Jazz fusion instrumental in the spirit of Weather Report and early Pat Metheny Group, Rhodes electric piano comping with extended 13th and altered chords, fretless bass with melodic runs and chordal walks, brushed drums in 7/8 for the head, tempo shift into 4/4 for the solo sections, occasional shifts to 5/4, warm analog room sound, ~110 BPM, 9 minutes long, instrumental, no vocals.
```

**Section structure** (Udio responds to bracketed section hints even though it's looser than Suno)

```
[Head | jazz fusion | rhodes comping | fretless bass | brushed drums 7/8 | extended chords | 110 BPM]

[Verse | rhodes vamping | fretless bass walking | brush snare | 7/8 sustained]

[Solo | rhodes improvised solo | tempo shift to 4/4 | walking bass | brush ride pattern]

[Solo | fretless bass solo | sparse rhodes comping | brush snare | space-conscious]

[Bridge | shift to 5/4 | both rhodes and bass trading fours | drums responsive]

[Head out | return to 7/8 | rhodes lead | full band | extended chords | melodic resolution]

[Outro | rhodes sustain | bass walk-down | cymbal swell | reverb tail]
```

### Deltas applied

- "Jazz" → "jazz fusion" + named-era references (Weather Report, early Pat Metheny) for harmonic / sonic anchor
- "Instrumental" → reinforced with `no vocals` at end (Udio will sometimes sneak in scat)
- "Long" → explicit "9 minutes" + 7 sections that each have a job (head / verse / 2 solos / bridge / head out / outro)
- Specified time signatures (7/8, 4/4, 5/4) — Udio parses these and shifts cleanly at section boundaries
- Chose Udio for the length advantage; documented why in the prompt header

---

## Example 4 — Label-safe orchestral cue (Google Lyria 3 Pro)

### Before (weak)

```
epic orchestral track
```

What's wrong:
- "Epic" is the most-overused trailer adjective — model defaults to generic 2010s "Two Steps from Hell" stab pattern
- No emotional arc, no climax timing
- No BPM, no length, no key
- No mention of WHY Lyria 3 Pro — strict licensing matters here

### After (Google Lyria 3 Pro)

**Why Lyria 3 Pro**: Trained on licensed catalog with provenance metadata + SynthID watermark. The only major model where output is cleanly usable for label / brand / film work without rights anxiety. Lyria does not accept bracket meta-tags — uses natural language with structured side fields.

**Prompt** (NL, no brackets, no Suno-style stacks)

```
A cinematic orchestral cue building from a hushed, reflective opening into a triumphant final climax. The piece opens with low cello drone and distant wordless choir, joined at 0:30 by a solo violin carrying a yearning melodic line. At 1:00 brass and taiko drums enter with a gentle gallop, the choir swelling. At 1:45 the full orchestra arrives with soaring violins, brass swell, and triumphant taiko, the choir at full force. The piece resolves at 2:30 into a sustained string chord with a single piano note tail.
```

**Side fields**

```
Key:         D minor → D major (Picardy third at climax)
BPM:         90
Length:      3:00
Style:       Cinematic orchestral, film score, instrumental
Mood:        Reflective → triumphant
Watermark:   SynthID enabled (automatic, label-safe output)
```

### Deltas applied

- "Epic orchestral" → reflective-to-triumphant arc with explicit timestamps (0:30, 1:00, 1:45, 2:30)
- Named the structural devices: cello drone → solo violin → brass+taiko → full orchestra → resolution
- Used NL prose (Lyria's native input mode), NOT Suno bracket stacks — bracket syntax silently degrades Lyria output
- Specified key change (D minor → D major via Picardy third) — Lyria respects music-theory directives
- Explicit BPM, length, mood as structured fields (Lyria API has dedicated slots)
- Watermark line documents that this is the label-safe pick — SynthID enabled by default, not user-toggle

---

## Example 5 — Vocal clarity with exclude-styles (ElevenLabs Music)

### Before (weak)

```
indie folk song, female vocal
```

What's wrong:
- "Indie folk" is broad — Bon Iver vs Phoebe Bridgers vs Mumford are all "indie folk"
- "Female vocal" — no timbre, no delivery style, no breath quality
- No exclusion list — Eleven Music's killer feature (exclude-styles) is wasted
- No structure, no abrupt-ending guardrail

### After (ElevenLabs Music)

**Why Eleven Music**: strongest vocal realism in 2026 testing — sounds least synthetic of the major models. Exclude-styles parameter is unique: lets you bar specific tropes the model otherwise defaults to.

**Prompt** (single-prompt with bracketed style cues — Eleven supports light bracket syntax)

```
Intimate indie folk in the spirit of Phoebe Bridgers and early Bon Iver, breathy female alto vocal close-miked with audible inhale, fingerpicked nylon-string acoustic guitar, soft brushed snare entering at the chorus, distant pedal steel swell at the bridge, warm analog tape compression, ~88 BPM, 4 minutes.

[Verse 1 | nylon guitar fingerpicking | breathy alto vocal | sparse]
[Chorus | brushed snare entry | layered vocal | soft pedal steel underneath]
[Verse 2 | continues sparse | second vocal harmony entering]
[Bridge | pedal steel swell | doubled vocal | guitar palm-muted]
[Outro | final chorus phrase repeated | slow ritardando | full but soft mix]

Exclude styles: no abrupt ending, no electronic drums, no trap hi-hats, no auto-tune, no synth pads, no four-on-floor kick, no key change.
```

### Deltas applied

- "Indie folk" → named-artist anchors (Phoebe Bridgers, early Bon Iver) — Eleven parses these for timbre / production reference
- "Female vocal" → specific timbre ("breathy alto"), mic technique ("close-miked with audible inhale"), delivery ("intimate")
- Added the exclude-styles list — Eleven Music's signature feature, addresses what would otherwise sneak in
- Specified ritardando + slow outro to avoid Eleven's known abrupt-ending failure mode
- Light bracket section list — Eleven accepts these but treats them as advisory not strict (unlike Suno where they're load-bearing)
- ~88 BPM — slow enough for the intimate folk feel, fast enough to not drag

---

## Example 6 (RU) — Русская поп-баллада (Suno v5.5)

### Контекст

Пользователь пишет осеннюю поп-балладу для русскоязычного релиза. Просит русский текст, но автор не до конца понимает, что метатеги стиля надо держать на EN.

### До (weak)

```
Песня про осень на русском
```

What's wrong:
- Жанр запрошен на RU — Suno ждёт EN-теги в style box; русский в style box работает хуже
- «Про осень» — тема без сцены, без героя, без конкретики
- Нет указания вокального пола, темпа, инструментов
- Велик риск, что модель попробует переключаться между языками внутри строки — Suno в этом случае ломает произношение

### После (Suno v5.5)

**Style box** (EN — модель парсит точнее)

```
Russian-language melancholic pop ballad, female lead vocal with breathy alto delivery in Russian, warm grand piano foundation, lush string arrangement entering at the chorus, brushed drums on the second verse, autumnal cinematic mood, ~78 BPM, 4 minutes.
```

**Lyrics box** (RU тексты, EN секционные теги — переключение языков ТОЛЬКО на границе блока, не внутри строки)

```
[Intro | piano | warm strings entry | 78 BPM]

[Verse 1 | melancholic pop verse | breathy female alto | russian vocal | piano | sparse]
Сентябрь складывает плечи в моих окнах
Жёлтый свет на кухне как остывший чай
Я учусь не помнить твой телефон наизусть
Учусь, как осень, отпускать невзначай

[Pre-Chorus | rising piano figure | strings swell | drum brush entry]
И всё, что я хотела сказать в апреле,
Падает с веток в октябре

[Chorus | russian pop ballad chorus | belted female vocal | full strings | brushed drums | warm piano]
Осень, осень, я научилась дышать
Без твоего имени в каждом «привет»
Окна гаснут, остаётся лишь свет
Той осени, которой больше нет

[Verse 2 | second verse | doubled vocal | piano + strings sustained]
Лестница знает, как я возвращалась поздно
Чашка на полке хранит твою тень
Я собираю себя по горячим зёрнам кофе
По строчкам песен, по краешкам дней

[Bridge | piano and vocal only | intimate | breathy]
А может, осень — это просто способ
Научиться, наконец, замолчать

[Final Chorus | key change up a step | full production | vocal ad-libs]

[Outro | piano reprise | distant strings | reverb tail | fade]
```

### Применённые дельты

- Style box остался EN — Suno парсит инструменты, BPM, и vocal direction точнее по-английски. Указание «in Russian» внутри style box достаточно
- Секционные теги (`[Verse 1 | ... | russian vocal | ...]`) — на EN, но с пометкой `russian vocal`, чтобы модель не сбилась на английский на этом блоке
- Текст полностью на RU, никаких смешанных строк — переключение языков ТОЛЬКО на границе секции (а в этом примере вообще без переключения, весь текст RU)
- «Про осень» → конкретная сцена: жёлтый свет на кухне, телефон наизусть, кофе по зёрнам, лестница, чашка на полке — тактильные якоря вместо абстракции
- Добавлены breathy alto + key change на финальном припеве — каноничные приёмы русской поп-баллады, названы явно
- 78 BPM — баллад-tempo; быстрее уйдёт в гёрл-поп, медленнее в инди

---

## Pattern summary

The strong-music-prompt formula reliably wins:

1. **Genre with sub-genre and era** — not "pop", but "anthemic modern pop"; not "jazz", but "jazz fusion in the spirit of Weather Report"
2. **BPM inside the genre's narrow window** — drill at 140, hyperpop at 160, lo-fi at 85 — out-of-range tempo silently breaks the recipe
3. **Vocal direction**: gender + timbre + delivery + mic — "breathy alto close-miked with audible inhale" beats "female vocal"
4. **Named load-bearing instruments** — sliding 808 for drill, log drum for Afrobeats, Rhodes for fusion — the one element that makes the genre that genre
5. **Section structure with tag stacks** — `[Chorus | anthemic chorus | stacked harmonies | full mix]` per section, not one blanket style line
6. **Model-correct syntax** — Suno brackets, Udio NL with light brackets, Lyria pure NL + side fields, Eleven NL + exclude-styles
7. **Language switch at section boundary only** — never mid-line; Russian/Korean/Japanese topline in lyrics box, EN tags in style box
8. **Chorus-first composition for pop / anthems** — write the chorus before the verses; verses serve the chorus
9. **Exclude-list when supported** — Eleven Music's `Exclude styles:` line is free leverage; use it for the failure modes you've seen
10. **Right model for length and licensing** — Suno for ≤5 min vocal songs, Udio for long-form coherence, Lyria 3 Pro for label-safe, Eleven for vocal realism

Average word count of the weak prompts: 3-6 words. Of the strong prompts: 80-200 words of style + 200-400 words of structured lyrics box. The model needs the specificity to commit; vague input produces vague genre-pastiche.
