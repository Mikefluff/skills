---
name: music-prompt
description: "Write prompts for 10+ frontier AI music generators (Suno v5.5, Udio v4, Google Lyria 3 Pro, ElevenLabs Music, Stable Audio 2.5, MusicGen, Tencent SongGeneration, Sonauto v2, Riffusion, Mubert). 2026 canonical meta-tag taxonomy (Structure / Vocal delivery / Vocal effects / Instrumental / Mix-production / Energy-dynamics / Era-genre / FX), `|` stacking, two-box Style+Lyrics workflow (Suno), exclude-styles (Eleven), field-driven (Lyria). Lyrics conventions: ad-libs, repetition, section headers, language switching. Use when the user says 'prompt for Suno / Udio / Lyria / Eleven Music', 'song about X', 'AI music prompt', 'meta tags for this chorus', 'cover song style', 'orchestral cue'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Generate a tight, model-aware prompt for AI music generation. Output: for two-box models (Suno, Udio) — separate Style of Music box + Lyrics box with embedded bracketed meta-tags; for single-prompt models (Eleven, Lyria, Stable Audio) — one well-formed prompt with bracketed cues and timing markers; for field-driven models (Lyria) — natural-language prompt + structured key/BPM/lyrics fields.

This skill does NOT call the music model — it produces text you paste into Suno / Udio / Lyria 3 / ElevenLabs Music / Stable Audio / Riffusion / Mubert / MusicGen / SongGeneration / Sonauto.

Use when the user wants a song, instrumental cue, cover, remix, jingle, background loop, talkbox / vocal arrangement, or a specific genre recipe. The skill picks the right model + correct tag taxonomy + the box-placement rules per model, and produces paste-ready output instead of generic "AI music".

This skill does NOT:
- generate the audio itself (that's the model)
- write traditional sheet music or MIDI files
- handle voice cloning workflow (that's a Suno Voices / ElevenLabs feature inside their tool)
- generate spoken-word audio for video/podcasts (use `video-prompt` audio block for in-clip dialogue; for standalone speech, use ElevenLabs voice tools)
</objective>

## ROLE

Read the request → identify subject + genre + intent (full song / instrumental / cover / loop / cue) → pick target model from `references/model-picker.md` → assemble Style box + Lyrics box (or single prompt depending on model) using the 8-category meta-tag taxonomy → apply per-model placement rules → return paste-ready output.

## PIPELINE

1. **Clarify if needed.** If the user gave only a topic ("song about loneliness"), pick a sensible genre default (modern pop ballad) and check before committing. If they gave genre + mood + structure, skip.

2. **Pick model from intent** — see `references/model-picker.md`:
   - Full song with vocals + lyrics → Suno v5.5
   - Longest coherent song (5-10 min) → Udio v4
   - Cinematic / orchestral cue → Stable Audio 2.5 or Lyria 3 Pro
   - Sound-design / instrumental → Stable Audio 2.5
   - Cleanest licensing → Lyria 3 Pro or ElevenLabs Music
   - Exclude-styles control → ElevenLabs Music
   - Stems / multi-track output → Suno (12 stems) or Udio (Stem Sep 2.0) or Sonauto v2
   - Voice clone → Suno Voices (Premier)
   - Cover / remix → Suno Cover or Udio remix
   - Self-host / open-weights → MusicGen / Stable Audio Open / Tencent SongGeneration
   - Background loops for apps → Mubert API
   - Free unlimited iteration → Riffusion

3. **Pick the genre recipe** — see `references/genre-recipes.md` for 12 ready-made stacks (hyperpop / drill / country / lo-fi / ambient / orchestral / K-Pop / Afrobeats / jazz fusion / hardcore punk / synthwave / gospel). Adapt; don't invent fresh stacks unless explicitly creative-fusion.

4. **Build the prompt** using the model's correct workflow:
   - **Suno (two-box)**: Style of Music box (≤1000 chars, natural-language genre/mood/instrument/era; NO brackets), Lyrics box (≤3000 chars, all `[bracketed]` section + delivery + FX tags on their own lines + the lyric content). See `references/models/suno.md`.
   - **Udio (one prompt + lyrics)**: style prompt natural-language; lyrics with `/`-inserted bracketed structural tags (atomic, no `|` stacking). See `references/models/udio.md`.
   - **ElevenLabs Music (single prompt)**: natural language with bracketed style cues + timing markers + exclude-styles. See `references/models/elevenlabs.md`.
   - **Lyria 3 Pro (field-driven)**: natural-language prompt + separate `lyrics`, `key`, `BPM` fields. No brackets. See `references/models/google.md`.
   - **Stable Audio 2.5 (free text)**: instrumental-focused, free-text prompt with multi-part composition. See `references/models/stable-audio.md`.

5. **Apply tag taxonomy** — see `references/meta-tags.md` for the canonical 8-category list (Structure / Vocal delivery / Vocal effects / Instrumental / Mix-production / Energy-dynamics / Era-genre / FX). Max 4-8 tags per stack. Order: core genre → era → mood → instrument → mix/FX → vocal direction. One tag per category in a stack.

6. **Apply lyrics conventions** — see `references/lyrics-conventions.md`:
   - Section headers on their own line.
   - Ad-libs in parens on their own line, ≤3 words.
   - Repetition: physically duplicate the line; `(x2)` unreliable.
   - Language switch: at section boundary, not within a line.
   - Stage directions ONLY in brackets; never as bare prose.

7. **Output.**
   - For Suno / Udio: two fenced blocks clearly labeled `Style of Music` and `Lyrics`.
   - For single-prompt models: one fenced block.
   - For field-driven (Lyria): structured `prompt:` / `lyrics:` / `key:` / `BPM:` block.
   - 1-line note: which model + recipe + key conventions applied.
   - If `--variants N` requested — N alternatives with different tag stacks or genre lean.

## MODES

- `music-prompt <topic-or-brief>` — generate default prompt (intent-routed model)
- `music-prompt <brief> --model <name>` — target a specific model. Valid: `suno-v5-5`, `suno-v4-5`, `udio-v4`, `udio-1-5`, `lyria-3-pro`, `lyria-3`, `eleven-music`, `stable-audio-2-5`, `stable-audio-open`, `musicgen`, `tencent-song-generation`, `sonauto-v2`, `riffusion`, `mubert`
- `music-prompt <brief> --genre <genre>` — force a genre recipe. Valid: `hyperpop`, `drill`, `country`, `lo-fi`, `ambient`, `orchestral`, `k-pop`, `afrobeats`, `jazz-fusion`, `hardcore-punk`, `synthwave`, `gospel`, plus free-form
- `music-prompt <brief> --instrumental` — instrumental only; lyrics box empty or omitted
- `music-prompt <brief> --lyrics file:<path>` — bring your own lyrics; skill embeds tags into them
- `music-prompt <brief> --exclude "<styles>"` — exclude-styles (works on ElevenLabs Music; degrades to negative-style note on others)
- `music-prompt <brief> --cover <reference-track-description>` — Suno Cover or Udio remix mode
- `music-prompt <brief> --extend` — Suno Extend or Udio extension mode; prompt continues an existing track
- `music-prompt <brief> --variants 3` — 3 alternatives with different tag stacks
- `music-prompt <brief> --improve` — user gives a weak prompt + describes the bad output; skill rewrites

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/model-picker.md](references/model-picker.md) | Always at step 2 — intent → model decision tree + capability matrix |
| [references/meta-tags.md](references/meta-tags.md) | Always at step 5 — 8-category canonical taxonomy + stacking rules |
| [references/song-structure.md](references/song-structure.md) | Structuring the song — section ordering, length budgets per model, genre templates |
| [references/vocal-tags.md](references/vocal-tags.md) | Picking vocal delivery + effects — voice character / register / style / backing / effects + mini-recipes |
| [references/instrumental-tags.md](references/instrumental-tags.md) | Picking instruments — drums / bass / guitars / keys / strings / brass / world + per-genre quick-picks |
| [references/mix-production-tags.md](references/mix-production-tags.md) | Shaping the sound — era / stereo width / reverb / delay / compression / saturation / mastering |
| [references/lyrics-conventions.md](references/lyrics-conventions.md) | Writing the lyrics box — Style vs Lyrics, ad-libs, repetition, language switch, per-model notes |
| [references/genre-recipes.md](references/genre-recipes.md) | Picking a genre — 12 paste-ready recipes with Style box + Lyrics box + variations |
| [references/models/suno.md](references/models/suno.md) | Suno v5.5 (+ v4.5 / v5 migration) |
| [references/models/udio.md](references/models/udio.md) | Udio v4 (+ v1.5 Allegro migration) |
| [references/models/google.md](references/models/google.md) | Google Lyria 3 / Lyria 3 Pro |
| [references/models/elevenlabs.md](references/models/elevenlabs.md) | ElevenLabs Music |
| [references/models/stable-audio.md](references/models/stable-audio.md) | Stable Audio 2.5 + Open / Open Small |
| [references/models/open-source.md](references/models/open-source.md) | MusicGen / AudioCraft + Tencent SongGeneration + Sonauto v2 |
| [references/models/api-tools.md](references/models/api-tools.md) | Riffusion + Mubert (API-first / background music) |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 6 calibration pairs covering anthemic modern pop (Suno), drill verse (Suno), long-form jazz fusion (Udio), label-safe orchestral (Lyria 3 Pro), indie folk with exclude-styles (ElevenLabs), RU pop ballad with language switching at section boundaries (Suno).

## CONSTRAINTS

- **Suno: brackets go in the LYRICS box ONLY**. The Style of Music box accepts natural language only — brackets there are ignored or break the gen.
- **Don't invent tags.** Every bracket tag must come from the canonical taxonomy in `references/meta-tags.md`. Invented tags (`[Dubstep Drop]` if not on the list) are ignored or hurt.
- **Max 4-8 tags per stack.** Past 8, the model dilutes. Front-load core genre + era + mood; instruments + FX + vocal direction follow.
- **One tag per category in a stack.** Don't combine two genres in one stack (`[hyperpop | country]`) unless deliberate fusion — combine two genres at most.
- **Order matters**: core genre → era → mood → instrument → mix/FX → vocal direction.
- **Section headers on their own line.** ALWAYS. `[Chorus]` then newline then lyric. Inline `[Chorus] We light it up` is sung literally.
- **Ad-libs in parens on own line, ≤3 words.** `(yeah)`, `(uh, ad-lib: oh)`.
- **Repetition: duplicate the line.** `(x2)` is unreliable across models.
- **Language switch at SECTION boundary, not within a line.** Verse 1 RU, Chorus EN is fine. `Я walking down the street tonight` is not.
- **Don't name living artists or copyrighted songs.** Suno / Udio / Lyria scrub or refuse. Use era + scene descriptors instead (`80s glam metal`, `2010s EDM festival`, `Y2K R&B`).
- **Don't write stage directions outside brackets.** "Then she shouts:" is sung as a lyric. Use `[Verse | shouted vocal]` instead.
- **Don't mix conflicting moods.** `[dark]` + `[happy]` randomizes the output. Pick one emotional anchor per section.
- **Don't bury the genre in the Style box past char-1000 on Suno.** Silent truncation. Front-load.
- **Lyria 3 Pro refuses artist-mimicry prompts.** Don't write "in the style of Hans Zimmer". Use "modern epic film score, brass swell, taiko drums" instead.
- **Stable Audio 2.5 is weak on vocals.** Treat as composition / sound design — don't expect singing.
- **For two-box models (Suno, Udio)**: output MUST clearly separate Style and Lyrics blocks. Don't paste them as one prompt.

## INVOCATION HINTS

When the user says any of:
- "prompt for Suno / Udio / Lyria / Eleven Music / Stable Audio / MusicGen / Riffusion / Mubert / Sonauto"
- "song about X", "track about X", "make me a song / track / instrumental"
- "AI music prompt", "music meta tags", "Suno meta tags"
- "cover song", "remix this track", "extend this song"
- "background loop", "jingle", "stinger", "intro music"
- "orchestral cue", "film score cue", "trailer music"
- "hip-hop verse / drill verse / lo-fi loop / synthwave instrumental / gospel chorus"
- "improve this music prompt"

RU triggers:
- «промпт для Suno / Udio / Lyria / Eleven Music / Stable Audio / MusicGen»
- «песня про X», «трек про X», «инструменталка про X»
- «AI-музыка промпт», «meta-теги для Suno»
- «cover-версия», «ремикс этого трека», «продли эту песню»
- «фоновая музыка», «джингл», «стингер», «вступление»
- «оркестровая кю / трейлер-музыка»
- «лофай-луп / синтвейв-инстру / госпел-припев»
- «улучши промпт для музыки»

The Style box and Lyrics box are usually written in English (Suno / Udio / Eleven parse EN best). Lyrics can be RU / multilingual where the model supports it (Suno + Eleven handle multilingual; Lyria limited to EN/ES/FR/JP; Udio works but less stable). Switch language at SECTION boundary, never within a line.

For pure-instrumental loops or background music: use `--instrumental` mode; lyrics box empty.

Use this skill. For static image — `image-prompt`. For video — `video-prompt`. For in-clip dialogue audio (4-15s talking-head with lip-sync) — `video-prompt` with `--audio` mode, not this skill.
