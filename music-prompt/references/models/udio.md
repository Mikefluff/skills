# Udio

Coherent-long-form rival to Suno. Smaller community, cleaner licensing, longer songs.

---

## Udio v4

**Strengths**: longest coherent songs (~10 min on v4), phase-coherent Stem Separation 2.0 (Vocals / Bass / Drums / Other), label-licensed catalog (cleaner licensing posture than Suno).
**Weaknesses**: smaller community tag corpus; downloads/stems intermittently gated during the UMG licensing transition; no formal mood/emotion tag category.

### Syntax / Format rules

**Single style prompt box** + Lyrics box. Tags are inserted inside lyrics via `/` autocomplete.

**Official tag set** (structural + dynamic + ensemble only):
- Structural: `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Hook]`, `[Bridge]`, `[Instrumental Bridge]`, `[Intro]`, `[Outro]`
- Dynamic: `[Drop]`, `[Pre-Drop]`, `[Build]`, `[Breakdown]`
- Ensemble: `[Choir]`, `[Spoken Word]`, `[Announcer]`, `[Sample]`, `[All]`

Mood/emotion tags (`[angry verse]`, `[crowd sings]`, `[whispered]`) work in practice but are **undocumented** — treat as best-effort.

**Style prompt structure**:
```
{topic}, {genre tags}, {mood descriptors}, {era}, in the style of {composer / scene / production era}
```

Artist-voice copy is blocked. The "in the style of" slot captures vibe (e.g. "70s Stevie Wonder Motown production", "early-2000s J Dilla beat-tape") but won't impersonate a living artist's voice.

**Manual mode**: disables Udio's auto-refinements (auto-intro extension, smoothing). Use when you want exact control over starts/ends and section length.

**Atomic tags**: Udio tags are not stackable — `[Chorus | anthemic | stacked]` does not parse like Suno. Use one tag per bracket; put the descriptive layer in the style prompt instead.

### Prompt template

**Style prompt**:
```
{topic/subject}, {primary genre}, {sub-genre}, {2-3 mood descriptors}, {era or production scene}, in the style of {composer or scene, NOT a living artist}
```

**Lyrics**:
```
[Intro]

[Verse]
{4-8 lyric lines}

[Pre-Chorus]
{2-4 lines}

[Chorus]
{4 lines}

[Verse]
{4-8 lines}

[Chorus]
{4 lines}

[Instrumental Bridge]

[Bridge]
{2-4 lines}

[Chorus]
{4 lines}

[Outro]
```

### Example

**Style prompt**:
```
late-night confession about a city that won't sleep, jazz fusion, neo-soul, smoky, contemplative, slow-burning, mid-1970s Blue Note production, in the style of Roy Ayers and Patrice Rushen
```

**Lyrics**:
```
[Intro]

[Verse]
The avenue is empty but the windows still glow
Somebody's piano two floors below
I press my hand against the cold glass pane
And listen to the city remember my name

[Pre-Chorus]
Every street has a song that it sings
Every door is a door to something

[Chorus]
And I'm walking, walking, walking home
Through the night that wears me like a hat
I'm walking, walking, walking home
And I forget what I'm walking back to

[Verse]
A taxi waits, the driver reads the news
Steam climbs from the grate like it's got somewhere to be
A saxophone two avenues away
Cuts the dark into the shape of me

[Chorus]
And I'm walking, walking, walking home
Through the night that wears me like a hat
I'm walking, walking, walking home
And I forget what I'm walking back to

[Instrumental Bridge]

[Bridge]
The city is a body and the body is a song
And the song is just the sound of belonging

[Chorus]
And I'm walking, walking, walking home
Through the night that wears me like a hat
I'm walking, walking, walking home
And I forget what I'm walking back to

[Outro]
```

### Notes / Pitfalls

- **Emotion lives in the style prompt**, not in tags. `[angry verse]` will sometimes work, but never bet the song on undocumented tags. Write "angry, jaw-clenched, accusatory" into the style prompt.
- **No `|` stacking** — Udio tags are atomic. Stacking gets parsed as literal section names.
- **Stems gated** during the UMG licensing transition — Pro/Enterprise unlock, but availability fluctuates. If stems matter, verify before committing.
- **No artist-voice copy** — "in the style of Beyoncé" returns a generic R&B vocal; "in the style of [composer / scene]" works for production vibe.
- Long-form coherence is Udio's headline advantage — write actual 3-verse / 2-bridge songs and let v4 sustain them.
- Manual mode is the right choice when you intend to splice/extend with external editing; it stops Udio from auto-extending intros and outros.
- Developer Platform API (Pro/Enterprise) exposes generation + stem separation programmatically — useful for batch workflows.

---

## v1.5 Allegro → v4 migration

- **v1.5 Allegro** (March 2025) capped coherent gens at ~4 min and shipped first-gen stems.
- **v4** (2026) extends coherent length to ~10 min and ships **Stem Separation 2.0** (phase-coherent — mixable stems, not just isolated tracks).
- Tag taxonomy is identical between v1.5 and v4 — no prompt rewrite needed.
- The "in the style of" slot got stricter on living-artist filtering in v4. Older Allegro prompts that leaned on artist names will return more generic results.
- v4 introduced the public Developer Platform API; Allegro was UI-only.
