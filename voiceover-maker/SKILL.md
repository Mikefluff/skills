---
name: voiceover-maker
description: "Text-to-speech skill — script in, MP3 out. Wraps the runner's audio modality (ElevenLabs eleven-tts + OpenAI gpt-4o-mini-tts). Supports voice picker, multilingual TTS (Eleven), speed control, and long-form scripts. Saves to ./generated/audio/<slug>.mp3. Optional --execute pattern: without it, returns the assembled script + provider notes; with it, calls the TTS API. Use when the user says 'voiceover for X', 'narration for this script', 'TTS this', 'read this aloud', 'озвучь', 'голосовая дорожка', 'диктор для видео'."
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
Convert text to spoken audio (MP3) using a TTS provider. Pick the right provider based on language + voice character needs. Output an MP3 ready to drop into a video editor / podcast track / reel.

Distinct from `music-prompt`:
- TTS is speech, not music. Different providers (Eleven TTS, OpenAI gpt-4o-mini-tts) vs. Suno/Udio/Lyria.
- No genre / meta-tags / two-box workflow.
- Output is one MP3 per call, not a song structure.

This skill does NOT:
- Generate music (use `music-prompt`).
- Compose voice + music together (use `audio-mix-maker` — planned, see ROADMAP).
- Lip-sync to a video — that requires separate tooling.
- Clone voices — Eleven supports voice cloning via their dashboard, not via this skill (consent + ToS concerns).
- Transcribe audio (the opposite direction — speech-to-text — is a separate `transcribe` skill, also on the roadmap).
- Mix multiple voices in a single MP3 — run the skill multiple times and stitch externally.
</objective>

## ROLE

Read the script text + optional voice + optional language → pick provider (Eleven for multilingual / long-form / quality voice control; OpenAI gpt-4o-mini-tts for cheap fast English-first TTS) → call the audio modality runner → save MP3.

## PIPELINE

1. **Resolve script source**:
   - `--prompt "<text>"` — inline script
   - `--prompt-file <path>` — read script from file
   - Or pipe via stdin (the runner accepts that too)

2. **Pick provider** — see `references/voice-picker.md`:
   - `--model auto`:
     - Multilingual (RU / DE / FR / JP / etc.) → `eleven-tts` (multilingual v2 by default)
     - Long-form (>2 min) → `eleven-tts` (better at sustained pacing)
     - English short-form quick demo → `gpt-4o-mini-tts` (cheaper, faster, but English-strong only)
     - Brand-voice consistency → `eleven-tts` with a specific voice_id
   - `--model <slug>`: explicit override

3. **Pick voice** — see `references/voice-picker.md`:
   - OpenAI: 6 named voices (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`). `--voice alloy` (default).
   - ElevenLabs: specific voice_ids from your Eleven library. `--voice-id <id>` (preferred for Eleven) or `--voice <name-alias>` if you've aliased one.

4. **Estimate cost + confirm** — based on character count.

5. **Execute** — calls the runner's audio CLI. Saves MP3.

6. **Output**:
   ```
   ./generated/audio/<timestamp>-<model>.mp3
   ```
   (or the path you specified via `--output`)

## MODES

### Input

- `voiceover-maker --prompt "<text>"` — inline
- `voiceover-maker --prompt-file <path>` — from file
- `voiceover-maker --prompt-file -` — from stdin (pipe support)

### Provider / voice

- `--model auto|gpt-4o-mini-tts|eleven-tts` — TTS provider (default auto)
- `--voice <name>` — for OpenAI: `alloy` / `echo` / `fable` / `onyx` / `nova` / `shimmer`. Fallback for Eleven (uses as voice_id if `--voice-id` not set).
- `--voice-id <eleven-id>` — explicit ElevenLabs voice_id
- `--speed N` — speech speed multiplier (0.5-2.0, provider-dependent)
- `--lang en|ru|de|...` — language hint (Eleven multilingual auto-detects; OpenAI is English-strong but handles others passably)

### Execution

- `--execute` — actually generate (else returns script + provider note)
- `--output <path>` — explicit output path
- `--yes` — skip cost confirmation
- `--check --model <slug>` — verify env + connectivity, no generation
- `--list-providers` — list TTS providers available given current env

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/voice-picker.md](references/voice-picker.md) | Step 2-3 — provider comparison, voice catalog (OpenAI 6 names + ElevenLabs popular IDs), when to pick which |
| [references/script-format.md](references/script-format.md) | Writing the script — sentence pacing, pauses, SSML support per provider, multi-paragraph handling |
| [references/troubleshoot.md](references/troubleshoot.md) | When the voice sounds wrong / cuts off / pronounces names badly |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: short EN announcement via OpenAI alloy voice, long RU narration via Eleven multilingual, brand-voice reading via a specific ElevenLabs voice_id.

## CONSTRAINTS

- **TTS provider availability is gated by env vars.** Eleven needs `ELEVENLABS_API_KEY`; OpenAI needs `OPENAI_API_KEY`. The skill auto-falls-back if the chosen provider's key is missing.

- **Cost per character**, not per call:
  - OpenAI gpt-4o-mini-tts: ~$0.015/minute spoken (very cheap)
  - ElevenLabs eleven-tts: ~$0.15/1000 chars (~$0.30 per minute)
  - Pick OpenAI for iteration; Eleven for final / multilingual / brand voice.

- **Multilingual: use Eleven.** OpenAI handles RU / DE / FR / etc. but accent is off. Eleven multilingual_v2 is the right pick for non-English work.

- **Long scripts → consider chunking.** Both providers have effective length caps (Eleven: ~5000 chars per call, OpenAI: 4096). Past that, split the script + concatenate the MP3s in your editor (or wait for the planned `subtitle-burner` companion that handles segment concat).

- **Pronunciation hints**: both providers respect basic phonetic spelling for unusual names. Eleven also supports SSML tags (`<phoneme>`).

- **Output format MP3 by default.** Most providers also support WAV / FLAC — pass `--format wav` if you need uncompressed audio (planned for v2.7).

- **`--execute` is opt-in by convention.** This skill defaults to `--execute` since TTS is "input → output" with no obvious "prompt-only" middle state (the prompt IS the script). If you want to preview cost first: `--cost-only`.

- **Never print API keys.** Mask in errors.

- **Output dir is `./generated/audio/`** by default.

- **Voice cloning is NOT supported here.** ElevenLabs supports voice cloning in their dashboard with consent flows. Don't use unauthorized voices.

## INVOCATION HINTS

When the user says any of:

- "voiceover for X", "narration for this script"
- "TTS this", "read this aloud"
- "make a podcast intro voice"
- "AI voice for my video"
- "озвучь", "голосовая дорожка", "диктор для видео"
- "сделай voice-over к этому тексту"

Defaults: `--model auto --voice alloy --execute`. If `--prompt-file` not given and no inline `--prompt`, reads from stdin or errors out.

If user mentions a specific language other than English: bias `--model eleven-tts`.

If user mentions "brand voice" / "consistent voice across episodes" / "branded podcast intro": bias `--model eleven-tts --voice-id <stable-id>`.

If user mentions "fast demo" / "quick test" / "cheap": bias `--model gpt-4o-mini-tts`.

This skill is distinct from:
- `music-prompt` — that's music. This is speech.
- `reel-builder` — that orchestrates video + music. This is bare TTS.
- `subtitle-burner` — that burns existing captions onto video. This generates new audio from text.

For voice-over a video AND music ducking under speech, the v2.7 `audio-mix-maker` will combine. Current workflow: generate voiceover here, generate music via `music-prompt`, mix manually in an editor (Audacity / GarageBand / DaVinci).
