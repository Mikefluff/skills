---
name: transcribe-maker
description: "Transcribe audio / video to SRT / WebVTT / JSON / plain text via OpenAI Whisper or the GPT-4o transcribe models. Auto-detects language or accepts --lang ISO-639-1. $0.003-0.006/min. Pairs with subtitle-burner. API limit 25 MB/call. Use when: 'transcribe this video', 'subtitles from audio', 'speech to text', 'распознай речь', 'сделай субтитры из видео', 'whisper'."

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
Speech-to-text utility. Take audio or video file → output subtitle file (SRT / VTT) or transcript (JSON / text).

Distinct from `voiceover-maker`:
- voiceover-maker generates SPEECH from text. This goes the OPPOSITE direction: speech → text.
- Both wrap an OpenAI audio API endpoint.

Distinct from `subtitle-burner`:
- subtitle-burner takes an existing subtitle file and burns it into video. THIS skill GENERATES the subtitle file. Chain them: `transcribe-maker` → `subtitle-burner`.

This skill does NOT:
- Translate the transcript (Whisper supports it via separate endpoint; not exposed in v1 — use OpenAI's `/v1/audio/translations` directly if needed)
- Identify speakers / diarize (Whisper doesn't natively diarize — use deepgram or assemblyai for that)
- Process files >25 MB (Whisper API limit — split with ffmpeg first)
- Run locally (uses OpenAI API; for offline use whisper.cpp directly)
- Edit / clean up transcript (raw Whisper output may have minor errors — manual cleanup needed for production captions)
</objective>

## ROLE

Read audio/video input → call OpenAI Whisper API with the requested format → save subtitle / transcript file.

## PIPELINE

1. **Resolve input**:
   - `--input <path>` — audio (.mp3, .wav, .m4a) or video (.mp4, .mov, .webm) (required)

2. **Pick output format**:
   - `--format srt` (default) — for `subtitle-burner` consumption
   - `--format vtt` — WebVTT (YouTube / HTML5 `<track>`)
   - `--format text` — plain transcript, no timestamps
   - `--format json` — Whisper raw JSON (simple)
   - `--format verbose_json` — JSON with word-level timestamps + segments

3. **Resolve language** (optional):
   - `--lang en` / `--lang ru` / `--lang de` etc. — ISO-639-1 hint
   - Auto-detect if omitted

4. **Pre-flight**:
   - Check OPENAI_API_KEY set
   - Check file ≤25 MB
   - Cost estimate via ffprobe

5. **Execute** — POST to OpenAI `/v1/audio/transcriptions`.

6. **Save**:
   - Default: `<input-stem>.<format>` next to source
   - Custom: `--output <path>`

## MODES

### Required

- `transcribe-maker --input <path>`

### Optional

- `--format srt|vtt|json|text|verbose_json` (default `srt`)
- `--model whisper-1|gpt-4o-transcribe|gpt-4o-mini-transcribe` (default `whisper-1`)
- `--lang <ISO-639-1>` — language hint (default: auto-detect)
- `--temperature <0-1>` — Whisper sampling temp (default 0; deterministic)
- `--output <path>` — explicit output path
- `--yes` — skip cost confirmation
- `--check` — verify env + connectivity
- `--cost-only` — print estimated cost + exit

## PICKING A MODEL

The choice is decided by the output format, not by quality — only `whisper-1`
emits subtitles.

| Need | Model | Cost/min |
|---|---|---|
| SRT / VTT / word-level timestamps | `whisper-1` | $0.006 |
| Plain transcript, highest accuracy | `gpt-4o-transcribe` | $0.006 |
| Plain transcript, bulk / cheapest | `gpt-4o-mini-transcribe` | $0.003 |

The GPT-4o transcribe models return json/text only. Asking one of them for `srt`
fails fast with a message rather than handing `subtitle-burner` something it
cannot burn. So anything feeding the subtitle pipeline stays on `whisper-1`; the
GPT-4o tiers are for transcripts a human or an LLM will read.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/formats.md](references/formats.md) | Output format details, when to pick each, Whisper segment behavior |
| [references/preprocessing.md](references/preprocessing.md) | When file >25MB: how to split / compress with ffmpeg |
| [references/troubleshoot.md](references/troubleshoot.md) | When transcription has errors, language mis-detected, timestamps drift |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: tutorial video to SRT, Russian podcast to text transcript, multilingual interview with word-level timestamps.

## CONSTRAINTS

- **OpenAI API key required.** Set via `/skills-keys add OPENAI_API_KEY ...`.

- **File size limit: 25 MB.** Whisper API hard limit. For larger files:
  - Audio: re-encode to lower bitrate (`ffmpeg -i input.wav -b:a 64k input.mp3`)
  - Video: extract audio only (`ffmpeg -i video.mp4 -vn -acodec copy audio.aac`)
  - Long files: split with ffmpeg into <25 MB chunks, transcribe each, concatenate

- **Cost: ~$0.006/min.** A 60-min podcast = ~$0.36. Very affordable for most use cases.

- **Language auto-detect is good but not perfect.** For multilingual content, pass `--lang` explicitly for best results.

- **Whisper has known weaknesses**:
  - Names / proper nouns sometimes wrong
  - Technical jargon often substituted with phonetic alternatives
  - Very quiet audio → hallucination of plausible-but-wrong text
  - Background music interference

- **Always proofread for production use.** Raw Whisper output is ~95% accurate for clean speech; 80-90% for noisy/accented/technical content.

- **No speaker diarization.** Whisper transcribes ALL speech but doesn't tag who's speaking. For multi-speaker tagging: use Deepgram / AssemblyAI (not in scope for v1).

- **SRT format includes timestamps.** Word-level timestamps via `--format verbose_json`. Sentence-level via `--format srt` or `vtt`.

- **For burning captions on video**: chain with `subtitle-burner`:
  ```
  transcribe-maker --input video.mp4 --format srt --output captions.srt --execute
  subtitle-burner burn ./video.mp4 --subtitle ./captions.srt --style modern
  ```

- **Never print API keys.**

## INVOCATION HINTS

When the user says any of:

- "transcribe this video / audio", "subtitles from audio", "speech to text"
- "распознай речь", "сделай субтитры из видео", "превратить аудио в текст"
- "whisper this", "extract dialogue from video"

If the user wants final burned-in captions: suggest chaining with `subtitle-burner`.

If the user has only audio: transcribe works the same. If only video: works (transcribes audio track).

Defaults: `--format srt --temperature 0` (best for captions). For plain transcript / blog post draft: `--format text`. For analytics / word-level alignment: `--format verbose_json`.

This skill is distinct from:
- `voiceover-maker` — text → speech (opposite direction)
- `subtitle-burner` — burns existing subtitles onto video; this produces them
- `audio-mix-maker` — mixing, not recognition
- `music-prompt` — generates music, not transcription
