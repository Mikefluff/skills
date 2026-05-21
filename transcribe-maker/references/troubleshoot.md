# Troubleshooting — transcribe-maker

---

## File too large (>25 MB)

**Symptom**: error "file >25 MB — Whisper API limit".

**Fix**: see `references/preprocessing.md`. Quickest: re-encode to lower bitrate or extract audio from video.

---

## Wrong language detected

**Symptom**: Russian podcast → Latin transliteration.

**Cause**: auto-detect failed (often happens with multilingual or accented content).

**Fix**: pass `--lang ru` (or whatever ISO-639-1 code).

Common codes:
- en (English), ru (Russian), es (Spanish), fr (French), de (German)
- zh (Chinese), ja (Japanese), ko (Korean)
- pt (Portuguese), it (Italian), pl (Polish), tr (Turkish)
- Full list: ISO-639-1 codes

---

## Transcription has errors / hallucinations

**Symptom**: random text not present in audio, or wrong words.

**Causes + fixes**:

1. **Very quiet audio.** Whisper hallucinates plausible content during silences. Trim silences with ffmpeg (`silenceremove` filter).

2. **Background music.** Whisper sometimes "hears" lyrics that aren't there. Lower music in the audio mix before transcribing, or use audio-extraction filters to isolate speech.

3. **Heavy accent.** Whisper handles most accents but extreme ones can degrade. Try a smaller chunk to test.

4. **Technical jargon / proper nouns.** Whisper often substitutes with phonetic alternatives. Manual proofreading required.

5. **Temperature too low for problematic audio.** Try `--temperature 0.2` for slight variation; sometimes helps.

---

## Timestamps drift

**Symptom**: captions get progressively out of sync.

**Cause**: Whisper sometimes drops audio segments (rare bug).

**Fix**:

1. Re-run with same input; results vary slightly.
2. Manually adjust SRT timestamps for affected segments.
3. Use `--format verbose_json` and check `segments[].avg_logprob` / `no_speech_prob` — low scores indicate Whisper struggled.

---

## API key missing or invalid

**Symptom**: `missing env: OPENAI_API_KEY` or 401 error.

**Fix**:
- `/skills-keys add OPENAI_API_KEY sk-...`
- Verify: `/skills-keys verify OPENAI_API_KEY`

---

## File not found

**Symptom**: `input file not found`.

**Fix**: verify the path. Common issues:
- Relative vs absolute path
- Spaces in filename (quote the path)
- Wrong extension

---

## Output appears empty

**Symptom**: SRT file is 0 bytes or near-empty.

**Causes + fixes**:

1. **Audio is mostly silent / no speech.** Verify the input has speech.
2. **Wrong language hint** — Whisper failed to transcribe. Remove `--lang` or pass the correct one.
3. **File is mostly music.** Whisper transcribes speech, not music.

---

## Wrong output format

**Symptom**: requested SRT but got plain text or vice versa.

**Cause**: argparse mismatch.

**Fix**: confirm `--format srt|vtt|text|json|verbose_json` is one of the supported values.

---

## Want to translate transcript to English

Whisper supports translation via a different endpoint (`/v1/audio/translations`). The skill v1 only wraps transcription (same-language). For translation:

1. Transcribe in source language first.
2. Pass the text to a translation tool (DeepL, GPT-4, Google Translate).
3. Or use OpenAI's translation endpoint directly via curl:

```bash
curl https://api.openai.com/v1/audio/translations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file="@input.mp3" \
  -F model="whisper-1"
```

---

## Want speaker identification (diarization)

Whisper doesn't natively diarize. For multi-speaker tagging:

- **Deepgram** — best diarization API
- **AssemblyAI** — also good
- **pyannote** — open-source local diarization (heavy setup)

Not in scope for transcribe-maker v1.

---

## Cost is higher than expected

$0.006/min = $0.36/hour. If your bill is higher than expected:

- Check the file durations you've processed.
- Replay verbose_json output: Whisper bills based on input duration.

For very large transcription batches (>10 hours): consider running whisper.cpp locally (free, no API).

---

## Want to use a different Whisper variant (large-v3, etc.)

The API offers only `whisper-1` (general). For other variants (Whisper-large-v3, Distil-Whisper):

- Run locally via whisper.cpp or transformers
- The skill doesn't wrap local execution in v1

---

## Word-level timestamps

Use `--format verbose_json`. Each segment includes `words[]` array with per-word `start`, `end`, `probability`.

```bash
transcribe-maker --input video.mp4 --format verbose_json --output transcript.json --execute --yes
jq '.segments[].words[] | "\(.start) \(.word)"' transcript.json
```

---

## Want to chain with subtitle-burner

Standard workflow:

```bash
# Step 1: Transcribe
transcribe-maker --input ./video.mp4 --format srt --output ./captions.srt --execute --yes

# Step 2: Burn captions
subtitle-burner burn ./video.mp4 --subtitle ./captions.srt --style modern --output ./video-captioned.mp4
```

Or in one composed command via `reel-builder --captions auto` (planned — currently captions are user-provided in reel-builder).
