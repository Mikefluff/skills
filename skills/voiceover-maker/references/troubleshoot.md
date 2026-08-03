# Troubleshooting — voiceover-maker

When the voiceover doesn't sound right.

---

## Wrong voice / sounds different than expected

**Symptom**: Asked for `alloy`, got something else.

**Causes + fixes**:

1. **Wrong `--voice` parameter for the provider.**
   - OpenAI: use named voices (alloy / echo / fable / onyx / nova / shimmer).
   - Eleven: use `--voice-id <opaque-string>`, not `--voice <name>`.

2. **Provider auto-substituted.** If you passed `--model auto` and the voice name didn't match the resolved provider, the skill may have used a default.
   - Fix: explicit `--model gpt-4o-mini-tts --voice alloy` to lock it.

3. **`--voice` for Eleven without `--voice-id`.** Eleven falls back to a default if `--voice-id` isn't passed and `--voice` doesn't match a known alias.
   - Fix: pass `--voice-id` explicitly for Eleven.

---

## Voice cuts off mid-sentence

**Symptom**: Script is 4500 chars but the MP3 cuts at ~2 minutes.

**Cause**: Script exceeds provider's per-call character limit. OpenAI: 4096. Eleven: 5000.

**Fix**:

1. Split the script into chunks ≤4000 chars (safe margin).
2. Run voiceover-maker per chunk.
3. Stitch the MP3s with ffmpeg:
   ```bash
   ffmpeg -i 'concat:part1.mp3|part2.mp3|part3.mp3' -acodec copy combined.mp3
   ```

---

## Mispronounces a name or word

**Symptom**: "Mikhail" comes out as "Mick-hayl".

**Fixes**:

1. **Respell phonetically**: write `Mick-hay-eel` in the script.
2. **For Eleven**, use SSML phoneme:
   ```xml
   <phoneme alphabet="ipa" ph="məˈxaɪl">Mikhail</phoneme>
   ```
3. **Try a different voice** — some voices handle non-English names better.

---

## Reads punctuation aloud (quote marks)

**Symptom**: `"hello"` becomes "quote hello quote".

**Fix**: use unicode curly quotes `"hello"` or remove quotes entirely.

---

## Non-English text sounds robotic / heavy accent

**Symptom**: Russian / German / French text sounds off.

**Cause**: Wrong provider. OpenAI is English-optimized; non-English voices have a strong American accent.

**Fix**:

1. Use `--model eleven-tts` for non-English.
2. Pick a voice from Eleven's library native to the target language (browse the Eleven dashboard).
3. Pass `--voice-id <native-language-voice>` and `--lang <code>`.

---

## Speech sounds rushed / clipped

**Symptom**: TTS reads too fast, swallowing words.

**Fixes**:

1. **Add more punctuation** — commas + periods give the TTS pacing cues.
2. **Insert manual pauses** (Eleven):
   ```xml
   First sentence. <break time="500ms"/> Second sentence.
   ```
3. **For OpenAI**: use `--speed 0.85` (slows by 15%).

---

## Speech sounds slow / draggy

**Symptom**: TTS pauses too long, sounds bored.

**Fixes**:

1. **Remove excessive ellipses** (...) — they imply long trailing pauses.
2. **For OpenAI**: `--speed 1.1` or `1.15` (speeds up by 10-15%).
3. **For Eleven**: lower `--stability` (kwarg passed through, defaults 0.5). Lower stability = more expressive + slightly faster delivery.

---

## Output file doesn't exist after run

**Symptom**: Skill says success but no MP3 in `./generated/audio/`.

**Causes + fixes**:

1. **Looked in wrong dir.** Default is `./generated/audio/<timestamp>-<model>.mp3` — list `./generated/audio/`:
   ```bash
   ls -la ./generated/audio/
   ```

2. **`--output` was set to a different path.** Check stdout for the printed path.

3. **API call succeeded but write failed (disk full / permissions).** Check stderr for OSError.

---

## Multiple voices in one MP3

The skill produces one MP3 per call with one voice. To mix voices:

1. Generate each part separately with different `--voice` / `--voice-id`.
2. Concatenate with ffmpeg:
   ```bash
   ffmpeg -i 'concat:host.mp3|guest1.mp3|host2.mp3|guest2.mp3' -acodec copy episode.mp3
   ```
3. For overlapping dialogue / interruptions: use a real audio editor (Audacity, GarageBand, DaVinci Resolve).

---

## Audio quality is low / muffled

**Symptom**: Output sounds compressed / harsh.

**Causes + fixes**:

1. **MP3 default bitrate.** Most providers default to 128kbps. For higher quality:
   - OpenAI: `--format wav` (uncompressed) or `--format flac`.
   - Eleven: `--format wav` or `pcm`.
   (Note: these flags are planned for v2.7; current default is mp3.)

2. **Script has a lot of sibilance / fricatives** that compress badly. Acceptable trade-off.

---

## Speed flag has no effect

**Symptom**: `--speed 0.5` doesn't slow speech.

**Cause**: Not all providers support speed multipliers via this skill in v1.

- OpenAI gpt-4o-mini-tts: speed via `speed` parameter, accepted (0.25-4.0).
- Eleven: no direct speed multiplier; the model paces by punctuation + stability settings.

**Fix for Eleven**: use SSML `<prosody rate="80%">` or add more punctuation for slower delivery.

---

## "But it sounded fine in the web UI"

Sometimes a script reads beautifully in ElevenLabs / OpenAI playground but worse via API.

**Causes**:
- Web UIs sometimes apply different defaults (voice settings preset to highest quality)
- Web UIs may use a newer model version than the API endpoint

**Fix**: pass explicit voice settings via kwargs (stability, similarity_boost for Eleven). Compare to the web UI's settings.

---

## Cost confirmation triggered for what feels small

**Symptom**: 500-char script through OpenAI → ~$0.0008 cost (under threshold), no prompt. But 500-char script through Eleven → ~$0.075, still under $0.10 threshold, no prompt. So why did it prompt?

**Cause**: Bug somewhere or you misread the cost. Check `--cost-only` output:

```bash
voiceover-maker --prompt-file ./script.txt --model eleven-tts --cost-only
```

---

## Want to test cost without spending

**Use `--cost-only`**:

```bash
voiceover-maker --prompt "<script>" --model eleven-tts --cost-only
```

Or `--check`:

```bash
voiceover-maker --check --model eleven-tts
```

`--check` verifies env + connectivity without making a billable call.
