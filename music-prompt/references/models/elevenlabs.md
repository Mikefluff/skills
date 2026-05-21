# ElevenLabs Music

The clean-licensing option. Strong vocals, fine-grained style control, unique exclude-styles capability.

---

## Eleven Music

**Strengths**: cleanest licensing story in the industry (training data declared safe), strong vocal realism, fine-grained style descriptors, **exclude-styles** capability (unique), multilingual lyrics.
**Weaknesses**: no formal `|` stacking; smaller community tag corpus; less structural granularity than Suno; no formal bracketed section headers.
**Execute via**: `--execute --model eleven-music` (env: `ELEVENLABS_API_KEY`) — ElevenLabs Music API.

Launched August 2025.

### Syntax / Format rules

**Single prompt field** — natural language with inline cues. Mixes:

- **Timing cues**: `"60 seconds"`, `"lyrics begin at 15 seconds"`, `"instrumental only after 1:45"`.
- **Musical cues**: `"130 BPM"`, `"in A minor"`, `"4/4 time"`.
- **Instrumentation**: `"solo electric guitar"`, `"two singers harmonizing in C"`, `"upright bass and brushed drums"`.
- **Bracketed style/instrument cues**: `"[energetic guitar solo]"`, `"[drum fill]"`, `"[bridge with strings]"`. These are inline directives, NOT section headers.
- **Sectional descriptors** (driven inline as prose): `"Intro / Verse / Chorus / Breakdown / Outro"` — written into the prompt, not as bracketed headers.

**Exclude-styles** (unique to Eleven):
```
"no abrupt ending"
"no new elements after the second chorus"
"no electronic drums"
"no auto-tune on the lead vocal"
```

**Composition plans** (advanced): layer a global style description with local per-section descriptors inside one prompt body. Mention only when fine control is needed; default to single-prompt for most work.

**Multilingual lyrics**: write lyrics in the target language directly inside the prompt; Eleven picks up the language and matches phonetics.

### Prompt template

```
{Duration in seconds}. {Tempo and key}. {Genre + sub-genre, mood, era}.
{Lead vocal description}. {Key instrumentation, including any solo cues with [brackets]}.
{Structural arc as inline prose: Intro / Verse / Chorus / Bridge / Outro with what happens in each}.
{Lyrics, plain text, language of choice}.
{Exclude-styles list at the end: "no ___, no ___, no ___".}
```

### Example

```
75 seconds. 92 BPM in A minor. Indie-folk ballad, intimate and yearning, 2020s production polish.
Breathy female lead vocal with close-mic delivery, light natural reverb, no auto-tune. Fingerpicked nylon-string guitar, soft brushed drums entering at the first chorus, [warm cello solo on the bridge], wide stereo reverb on the final chorus.
Structure: 8-second intro on solo guitar, Verse 1 stays sparse with vocal and guitar, Pre-Chorus lifts with cello pad, Chorus opens with brushed drums and stacked harmonies, Bridge breaks down to cello and lead vocal only, final Chorus returns wider, 6-second outro fading on solo guitar.
Lyrics:
I left the porch light on for you
counted every car that wasn't yours
the kettle whistles in another room
and I forget what I was waiting for
so tell me where the morning goes
when nobody comes home
tell me if you ever loved me
or if I dreamt it all alone

Exclude: no abrupt ending, no electronic drums, no auto-tune on the lead vocal, no new elements after the bridge.
```

### Notes / Pitfalls

- **Don't use Suno-style `|` stacking** — Eleven parses `[Chorus | anthemic | stacked]` as one literal directive, not as layered tags. Use plain inline brackets for single cues.
- **Don't expect Suno's section header convention** — Eleven treats `[Verse]` / `[Chorus]` as inline directives, not formal section starts. Use inline sectional words ("Intro", "Verse", "Chorus") inside the prose.
- **Exclude-styles is high-leverage** — the most consistent way to prevent the model's defaults from leaking in (auto-tune, electronic drums, big outros). Always include 2-4 excludes for production work.
- **Timing cues are honoured** — `"lyrics begin at 15 seconds"` is reliable.
- **Per-character credit pricing** — long generation budgets need monitoring on API.
- **API**: REST endpoint + Replicate availability. Composition plans exposed as structured input on the API tier.
- Strong choice when licensing scrutiny matters (advertising, broadcast, label-adjacent work) — training-data declarations are cleaner than competitors.
