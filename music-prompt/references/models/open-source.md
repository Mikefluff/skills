# Open-source music models

Self-hostable + free-tier options. MusicGen for melody-conditioned instrumental, SongGeneration for vocals (esp. multilingual), Sonauto for stems + word-level alignment.

---

## Meta MusicGen / AudioCraft

**Strengths**: open weights (Apache 2.0), runs locally, melody conditioning via chromagram, 50 kHz output (2025 update), multilingual melody input.
**Weaknesses**: ~30s native (extendable but coherence drops), no singing vocals.

### Syntax / Format rules

- Text prompt — natural-language description of genre / instrumentation / mood / tempo.
- Optional melody/chromagram input — feed an audio file as a melodic guide; the model preserves the contour while swapping style.
- No formal brackets, no section headers — the native window is too short for full song structure.
- Parameters: `model_size` (small / medium / large / melody), `duration` (sec), `top_k`, `temperature`, `cfg_coef`.

**VRAM** (approximate):
- `small` (300M): ~8 GB
- `medium` (1.5B): ~12 GB
- `large` (3.3B): ~16 GB
- `melody` (1.5B + melody conditioning): ~12 GB

### Prompt template

```
{Genre + sub-genre}, {tempo / feel}, {key instrumentation}, {mood descriptors}, {production qualities}.
[Optional melody conditioning: pass an audio file as melodic guide.]
duration: {seconds, ≤30 native}
```

### Example

```
Upbeat jazz fusion, 110 BPM, walking electric bass, Rhodes electric piano comping with chorus effect, brushed drums with rim-clicks, soprano saxophone leading the melody, warm 1970s studio production, wide stereo, slight tape compression.
Melody conditioning: input.wav (8-bar saxophone phrase as melodic guide)
duration: 30
```

### Notes / Pitfalls

- **30s sweet spot** — past that, coherence drifts. For longer pieces, generate multiple 30s segments and crossfade.
- **Melody conditioning is the killer feature** — hum a melody, MusicGen renders it as any genre.
- **No singing** — strictly instrumental.
- Best surface: HuggingFace `audiocraft` repo, Replicate hosted endpoint, or local `transformers` + `audiocraft`.
- The 2025 update lifted output to 50 kHz — re-run old prompts on the new checkpoint for noticeably better fidelity.

---

## Tencent SongGeneration / LeVo

**Strengths**: open weights (~3B params, released 2025), strong on Chinese vocals + multilingual EN/ZH, fast inference.
**Weaknesses**: smaller English community, documentation mostly in Chinese, limited structure-tag taxonomy.

### Syntax / Format rules

- Text prompt (EN or ZH) — genre + mood + instrumentation + vocal description.
- Lyrics field — accepts EN, ZH, mixed.
- Limited structure tags — `[Verse]`, `[Chorus]`, `[Bridge]` work; deeper Suno-style stacking does not.
- Vocal language: declared either in the prompt or inferred from lyric script.

### Prompt template

```
prompt: {genre + sub-genre}, {mood}, {vocal type — male/female, language}, {instrumentation}, {production}.
lyrics:
[Verse]
{lines in target language}
[Chorus]
{lines in target language}
[Verse]
{lines in target language}
[Chorus]
{lines in target language}
```

### Example

```
prompt: modern bilingual pop ballad, warm and reflective, female lead vocal alternating Mandarin verses and English chorus, fingerpicked acoustic guitar, soft strings on the chorus, mid-tempo, polished radio mix.
lyrics:
[Verse]
夜里的灯光在窗外摇晃
我数着每一辆不是你的车
水壶在另一个房间沸腾
我忘了自己在等什么

[Chorus]
So tell me where the morning goes
when nobody comes home
tell me if you ever loved me
or if I dreamt it all alone

[Verse]
我把你的外套装进纸袋
写了封永远不会寄的信
猫还在门边等你
像她知道这一切的结局

[Chorus]
So tell me where the morning goes
when nobody comes home
tell me if you ever loved me
or if I dreamt it all alone
```

### Notes / Pitfalls

- **Strongest open-source vocal model** for ZH and ZH/EN bilingual work.
- **English-only prompts work** but quality leans best when at least one verse or chorus is in Mandarin.
- Documentation: primary repo + papers are in Chinese; community ports + English wrappers exist on HuggingFace.
- Use when: bilingual content, regional content for ZH market, self-hosted commercial work.

---

## Sonauto v2 Beta

**Strengths**: stems output (Vocals / Drums / Bass / Instrumental), word-level lyric alignment, melody conditioning, multilingual (EN / ES / FR / DE).
**Weaknesses**: 60-80s extensions per call (multi-call chaining needed for full songs), smaller tag corpus, closed model (paid but generous free tier).

### Syntax / Format rules

JSON-style API with three core fields:

- `prompt` — natural-language style description.
- `tags` — array of short genre/mood tags.
- `lyrics` — plain text lyrics with optional `[Verse]` / `[Chorus]` markers.

Melody conditioning: optional `melody_audio` input.

### Prompt template

```json
{
  "prompt": "{genre + sub-genre}, {mood}, {vocal type}, {instrumentation}, {era}",
  "tags": ["{genre}", "{mood-1}", "{mood-2}", "{instrument}", "{era}"],
  "lyrics": "[Verse]\n{lines}\n[Chorus]\n{lines}\n[Verse]\n{lines}\n[Chorus]\n{lines}",
  "melody_audio": "optional input.wav",
  "language": "en"
}
```

### Example

```json
{
  "prompt": "indie folk ballad, intimate and yearning, breathy female lead vocal, fingerpicked acoustic guitar, soft brushed drums, warm cello on bridge, 2020s polish",
  "tags": ["indie-folk", "ballad", "intimate", "fingerpicked-guitar", "female-vocal"],
  "lyrics": "[Verse]\nI left the porch light on for you\ncounted every car that wasn't yours\nthe kettle whistles in another room\nand I forget what I was waiting for\n[Chorus]\nso tell me where the morning goes\nwhen nobody comes home\ntell me if you ever loved me\nor if I dreamt it all alone",
  "language": "en"
}
```

### Notes / Pitfalls

- **Word-level lyric alignment** is the unique feature — exposed in the API response as timestamps per word. Useful for karaoke, captioning, sync tooling.
- **Stems on every gen** — Vocals / Drums / Bass / Instrumental returned by default.
- **Extensions cap at 60-80s** — full songs require chaining; the API exposes a continuation parameter.
- **Free tier is generous** for prototyping; paid tier unlocks commercial use + higher rate limits.
- **Melody conditioning** behaves like MusicGen's — hum a line, get it back styled.
