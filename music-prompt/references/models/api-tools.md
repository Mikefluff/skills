# API-first tools: Riffusion + Mubert

Background music + parameter-driven generators. Different niche from Suno/Udio — these are for app/game/stream loops, not for "write me a song".

---

## Riffusion v5

**Strengths**: free unlimited via webapp (Jan 2025 release), cover-song workflow, simple UI.
**Weaknesses**: quality below Suno/Udio; official API on waitlist; no formal brackets or section taxonomy. <!-- TODO: confirm Riffusion API GA status -->

### Syntax / Format rules

- Free-text prompt only — natural language description.
- No formal brackets, no section headers, no `|` stacking.
- Cover-song workflow: paste a YouTube link or upload audio, prompt the new style — model preserves melody/structure, swaps timbre.
- Output: short clips (~30-60s native), extend via the webapp.

Third-party wrappers exist (musicapi.ai, aimusicapi.ai) for programmatic access while the official API is in waitlist.

### Prompt template

```
{Genre + sub-genre}, {mood}, {tempo feel}, {lead instrument + supporting layers}, {era / production style}.
```

### Example

```
Lo-fi hip-hop beat, mellow and nostalgic, 80 BPM, mellow Rhodes electric piano with slight detune, dusty sampled drums with vinyl crackle, soft upright bass, rainy-evening mood, 1990s tape compression aesthetic.
```

### Notes / Pitfalls

- **Free unlimited webapp** — best entry point for casual users and prototyping.
- **Cover-song mode** is the headline workflow: paste a track, describe a new style, get a cover.
- **Quality gap** vs Suno/Udio is real — not the right tool for finished releases, fine for sketches and demos.
- **API waitlist** — production integrations route through community wrappers for now.
- **Short clips** — extend through the webapp's continuation flow rather than asking for long single gens.

---

## Mubert API 3.0

**Strengths**: 12K+ track library, WebRTC streaming, licensing-safe by design (Mubert owns/licenses the source content), parameter-driven generation (mood / genre / BPM / duration).
**Weaknesses**: no vocals, no song-form output, not creative-prompt-driven — fully parameter-based.

### Syntax / Format rules

JSON API. Generation is driven by **structured parameters**, not free-text prompts.

Core fields:
- `mood` — e.g. `"focus"`, `"energetic"`, `"melancholic"`, `"uplifting"`, `"chill"`.
- `genre` — e.g. `"lo-fi-hip-hop"`, `"ambient"`, `"electronic"`, `"cinematic"`.
- `bpm` — integer, e.g. `90`.
- `duration` — seconds.
- `format` — `"mp3"`, `"wav"`, `"stream"` (WebRTC).

No lyric input, no creative prose prompt, no section structure.

### Prompt template

```json
{
  "mood": "{mood tag}",
  "genre": "{genre tag}",
  "bpm": {integer},
  "duration": {seconds},
  "format": "{mp3|wav|stream}"
}
```

### Example

```json
{
  "mood": "focus",
  "genre": "lo-fi-hip-hop",
  "bpm": 80,
  "duration": 600,
  "format": "stream"
}
```

### Notes / Pitfalls

- **Not for songwriting** — Mubert serves continuous, licensable background audio. The output is a stream or loop, not a track with verses and choruses.
- **Licensing is the headline value** — every byte returned is cleared for commercial use within Mubert's TOS.
- **WebRTC streaming** means you can drop a live audio bed into an app/game/stream without rendering and hosting files.
- **Parameter-driven** — there's no "in the style of" knob. If you need creative control, use Suno/Udio/Eleven and clear rights separately.

---

## When to use these tools

- **App / game / stream background audio** with clean licensing: **Mubert**.
- **Quick free sketches, cover-song experiments**: **Riffusion**.
- **Finished song with lyrics, verses, choruses, identity**: use **Suno / Udio / Eleven Music / Lyria** instead — neither tool on this page is built for song-form creative work.
