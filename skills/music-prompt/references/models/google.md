# Google Lyria

Google's label-safe music model. Field-driven, 48 kHz stereo, watermarked.

---

## Lyria 3 / Lyria 3 Pro

**Strengths**: 48 kHz stereo, SynthID-watermarked (label-safe), longest individual sections, available across Vertex AI / Gemini API / AI Studio / Google Vids / Gemini app / ProducerAI.
**Weaknesses**: 3 min max hard cap; lyric languages limited to EN/ES/FR/JP; no formal bracket taxonomy; refuses artist-mimicry prompts.
**Execute via**: `--execute --model lyria-3-pro` (env: `GEMINI_API_KEY` + `LYRIA_API_ENABLED=1`) — Gemini API, paid preview.

**Model ids**: `lyria-3-pro-preview` (full song, ~3 min) and `lyria-3-clip-preview` (30-second clip, reachable as `--model lyria-3-clip`). Both emit 44.1 kHz stereo. The Clip tier is the one to reach for when you need many short pieces — stings, loops, bumpers — rather than one track.

Released March 25 2026.

### Syntax / Format rules

**Field-driven, not tag-driven** — the model takes structured inputs, not bracketed lyrics:

- `prompt` — natural-language description of the clip (genre, mood, instrumentation, energy, structural arc).
- `lyrics` — optional, EN/ES/FR/JP only.
- `key` — explicit musical key field (e.g. `A minor`, `C major`).
- `bpm` — explicit tempo field (integer).
- `seed` — optional, for reproducibility.

**Structural concepts inside the `prompt`** use natural language, NOT brackets:
```
"intro builds for 8 seconds, verse with sparse percussion, chorus opens up with full band, bridge breaks down to piano, final chorus returns wider"
```

Lyria parses `[Verse]` / `[Chorus]` as literal text, not as section headers — write structure as prose.

**No `|` stacking idiom** — Lyria is field-based; layered descriptors go into the `prompt` field as comma-separated phrases.

### Prompt template

```
prompt: {genre + sub-genre}, {mood descriptors}, {lead instrument + supporting instruments}, {production qualities}, {structural arc as prose — intro/verse/chorus/bridge/outro in plain English}
lyrics: {optional, EN/ES/FR/JP}
key: {e.g. A minor}
bpm: {integer}
```

### Example

```
prompt: cinematic indie folk, intimate and yearning, lead female vocal with breathy close-mic delivery, fingerpicked nylon-string guitar, soft brushed drums entering at verse 2, swelling cello pad on the bridge, wide reverberant production, 48kHz stereo polish. Structural arc: 6-second intro on solo guitar, verse 1 stays sparse with vocal and guitar only, brief pre-chorus lifts with cello, chorus opens up with brushed drums and harmonies, verse 2 keeps the chorus instrumentation, instrumental bridge swells cello and adds piano, final chorus widens further, 4-second outro returns to solo guitar.
lyrics: I left the porch light on for you / counted every car that wasn't yours / the kettle whistles in another room / and I forget what I was waiting for
key: D major
bpm: 78
```

### Notes / Pitfalls

- **Hard 3-min cap** — no extend, no scene-chain. Plan the song to fit.
- **Lyric language gate**: EN / ES / FR / JP only. Other languages return instrumental or degraded vocals.
- **No artist mimicry** — Google's safety layer is strict. "In the style of [artist]" gets refused or degraded. Describe production traits instead.
- **Structural granularity weaker than Suno** — you can't force exact section boundaries; the model interprets the arc loosely.
- **SynthID watermark is mandatory** and not removable — required for label-safe distribution, blocking for adversarial use cases.
- **Brackets are literal** — `[Chorus]` in the prompt or lyrics ends up sung or read aloud. Use prose only.
- **`key` and `bpm` are first-class fields** — set them explicitly. Putting "120 BPM in A minor" in the `prompt` works less reliably than the dedicated fields.
- Best surface for most users: Vertex AI (production), Gemini API (apps), AI Studio (prototyping). Google Vids embeds Lyria for in-product soundtrack generation; ProducerAI is the partner-facing creator tool.

---

## Music AI Sandbox / MusicFX DJ

**Execute via**: prompt-only — no public API; AI Studio / labs UI only.

Lyria-family DJ-style real-time tool. Mention for completeness only; not a song-writing surface.

- Real-time interactive: knobs for genre / mood / BPM that morph the stream live.
- Output is loop-friendly, not song-form.
- Use for: live performance, ambient bed for streaming, sound-design exploration.
- Not the right tool when the brief is "write a 3-min track" — go to Lyria 3 Pro for that.
