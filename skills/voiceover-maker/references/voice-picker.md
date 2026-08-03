# Voice picker — voiceover-maker

Provider comparison + voice catalog + when to pick which.

---

## Provider decision tree

```
1. Language?
     English-only? → either works; OpenAI gpt-4o-mini-tts is cheaper.
     Multilingual (RU/DE/FR/JP/etc.)? → eleven-tts (multilingual v2).

2. Script length?
     Short (<2 min spoken time, ~3000 chars)? → either.
     Long (>2 min)? → eleven-tts (better sustained pacing, fewer artifacts).

3. Brand voice consistency required?
     yes → eleven-tts with a specific voice_id you'll reuse across episodes.
     no  → either; OpenAI's 6 named voices give variety per call.

4. Need SSML / pronunciation control?
     yes → eleven-tts (supports <phoneme> + <break> + emphasis tags).
     no  → either.

5. Cost-sensitive?
     yes → gpt-4o-mini-tts (~$0.015/min spoken vs Eleven's ~$0.30/min).
     no  → eleven-tts for quality.

6. Available env vars?
     drop candidates without env vars
     fallback: whichever has a key
```

---

## OpenAI gpt-4o-mini-tts

**Env var**: `OPENAI_API_KEY`

**Cost**: $0.015 per minute of generated speech. Cheapest in the catalog.

**Voices**: 6 named, English-optimized.

| Voice | Character | Best for |
|---|---|---|
| `alloy` | Neutral, mid-range | Default; works for most narration |
| `echo` | Calm, slightly older male | Documentary / contemplative |
| `fable` | British-accented, expressive | Storytelling / fiction |
| `onyx` | Deep, authoritative male | Trailer / dramatic / corporate intro |
| `nova` | Warm female, energetic | Marketing / upbeat content |
| `shimmer` | Soft female, gentle | Lifestyle / wellness / podcast intro |

**Limits**:

- Max input: 4096 characters per call
- English: excellent
- Non-English: passable but accent is off; not recommended for production

**Format support**: mp3 (default), opus, aac, flac, wav, pcm.

**Speed**: supports speed multiplier (0.25-4.0 via OpenAI's `speed` parameter, but quality degrades outside 0.7-1.5).

---

## ElevenLabs eleven-tts

**Env var**: `ELEVENLABS_API_KEY`

**Cost**: ~$0.15 per 1000 characters ≈ $0.30 per minute of generated speech. 20× more expensive than OpenAI but quality justifies it for production.

**Voices**: extensive catalog via Eleven's voice library; you reference by `voice_id` (opaque string like `21m00Tcm4TlvDq8ikWAM`).

Popular default voices (built into all accounts):

| Voice ID | Name (Eleven library) | Character |
|---|---|---|
| `21m00Tcm4TlvDq8ikWAM` | Rachel | American female, calm narration |
| `AZnzlk1XvdvUeBnXmlld` | Domi | American female, energetic |
| `EXAVITQu4vr4xnSDxMaL` | Bella | American female, soft warm |
| `ErXwobaYiN019PkySvjV` | Antoni | American male, well-rounded |
| `MF3mGyEYCl7XYWbV9V6O` | Elli | American female, young |
| `TxGEqnHWrfWFTfGW9XjX` | Josh | American male, deep |
| `VR6AewLTigWG4xSOukaG` | Arnold | American male, crisp |
| `pNInz6obpgDQGcFmaJgB` | Adam | American male, deep narration |
| `yoZ06aMxZJJ28mfd3POQ` | Sam | American male, mature dynamic |

For non-English / multilingual: use the multilingual_v2 model (set automatically) with any of the above voices — accent transfers reasonably.

To pick or clone your own voice: do this in the Eleven dashboard, then use the resulting `voice_id` here via `--voice-id`.

**Limits**:

- Max input: 5000 characters per call (model dependent)
- Multilingual: 29 languages supported as of 2026

**Format support**: mp3 (default), pcm, wav, ulaw.

**Speed**: stability + similarity controls (kwargs), but no direct speed multiplier — TTS naturally adjusts pace based on punctuation + sentence structure.

---

## Default selection logic

`--model auto` resolves to:

1. If `--lang` is non-English → `eleven-tts`
2. If script length > 3000 chars → `eleven-tts`
3. If neither key is set → exit non-zero with setup hint
4. Otherwise → `gpt-4o-mini-tts` (cheaper, faster default)

If only one of `OPENAI_API_KEY` / `ELEVENLABS_API_KEY` is set, auto resolves to that one.

---

## When to override `auto`

- **Brand voice consistency across episodes**: force `eleven-tts` with a fixed `--voice-id`. Re-use the same ID every time.
- **A/B testing voices for a release**: run twice, compare. Same script, different `--voice`.
- **Quick iteration on script copy**: force `gpt-4o-mini-tts` for cheap fast preview, then final with Eleven.
- **High-emotion content (drama, comedy)**: force `eleven-tts` — better at conveying tone shifts.
- **Robotic / synthetic style intentionally**: OpenAI's voices have slightly more "AI-sounding" texture by design; can be a feature.

---

## Voice character cheat sheet

If you don't know which voice to pick:

| Content type | OpenAI pick | Eleven pick |
|---|---|---|
| Corporate / professional | `onyx` (male) / `nova` (female) | Adam / Rachel |
| Documentary / narration | `echo` (male) | Sam / Adam |
| Lifestyle / wellness | `shimmer` (female) | Bella / Elli |
| Marketing / upbeat | `nova` (female) | Domi / Antoni |
| Storytelling / fiction | `fable` (British) | Rachel (American) — or browse Eleven for accent-specific |
| Tutorial / educational | `alloy` (neutral) | Adam / Rachel |
| Podcast intro / outro | any with character — try a few | Use a SPECIFIC voice_id you reuse |

---

## Multilingual specifics (Eleven)

`eleven_multilingual_v2` is the default model when calling `eleven-tts`. Supports:

- English (all variants)
- Spanish, French, Italian, Portuguese
- German, Dutch, Polish, Czech
- Russian, Ukrainian
- Arabic, Hebrew
- Hindi, Bengali, Tamil, Telugu
- Mandarin, Cantonese, Korean, Japanese
- Indonesian, Malay, Vietnamese, Thai
- Turkish, Greek, Hungarian, Romanian

Pass `--lang ru` (or any ISO-639 code) as a hint; Eleven auto-detects from the script anyway.

For accent: pick a voice native to the target language for best quality. Russian-speaking voices in the Eleven library have IDs different from American voices — browse the dashboard to find the right voice_id.

---

## Pronunciation hints

Both providers respect:

- **Phonetic spelling**: write "Mick-haw-eel" instead of "Mikhail" for tricky names.
- **Capitalization-as-emphasis** sometimes works: "I REALLY mean it".
- **Punctuation = pacing**: commas → short pause; periods → longer; ellipses → longer still.

Eleven additionally supports:

- `<phoneme alphabet="ipa" ph="...">word</phoneme>` — IPA pronunciation override.
- `<break time="500ms"/>` — explicit pause.
- `<emphasis level="strong">word</emphasis>` — emphasis hint.

OpenAI gpt-4o-mini-tts doesn't accept SSML directly — embed cues via punctuation + capitalization instead.
