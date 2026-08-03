# voiceover-maker — calibration

3 example sessions.

---

## Example 1 — Short EN announcement (OpenAI, alloy voice)

### User says

> Read this aloud: "Welcome to the Slow Software podcast. Today, we're talking about why shipping less is sometimes the right move."

### Command

```
voiceover-maker --prompt "Welcome to the Slow Software podcast. Today, we're talking about why shipping less is sometimes the right move." \
                --model gpt-4o-mini-tts \
                --voice alloy \
                --execute
```

### What happens

- Provider: OpenAI gpt-4o-mini-tts.
- Voice: alloy (default neutral).
- Cost: ~120 chars at $0.015/min × 0.6 min ≈ $0.009.
- Output: `./generated/audio/20260521-211530-gpt-4o-mini-tts.mp3` (~5 seconds, neutral American voice).

### What to notice

- One-line command, ~3 seconds end-to-end.
- OpenAI handles short English content best and cheapest.
- No `--cost-only` because the cost is trivially low.

---

## Example 2 — Long RU narration (Eleven multilingual)

### User says

> Озвучь этот текст профессиональным мужским голосом для подкаста. Это вступление к эпизоду про медленный софт.

(Script attached: 2500 chars in Russian)

### Command

```
voiceover-maker --prompt-file ./episode-intro-ru.txt \
                --model eleven-tts \
                --voice-id pNInz6obpgDQGcFmaJgB \
                --lang ru \
                --execute
```

### What happens

- Provider: Eleven multilingual_v2 (auto-selected because `--lang ru`).
- Voice: Adam (deep American male — works for RU via multilingual model, but for native-Russian voice, browse Eleven library for a native voice_id).
- Cost: 2500 chars at $0.15/1000 = $0.375. Above $0.10 — confirmation prompt:
  ```
  Estimated cost: $0.3750 USD. Proceed? [y/N]
  ```
- After `y`: output `./generated/audio/20260521-211845-eleven-tts.mp3` (~2 min of Russian narration with American-accented but understandable delivery).

### What to notice

- Eleven multilingual_v2 handles RU/DE/FR/JP/etc. — accent transfer is reasonable.
- For native accent: browse Eleven's library and use a Russian-native voice_id (different from Adam).
- Cost confirmation kicks in past $0.10 — Eleven is 20× more expensive than OpenAI, so this is the usual flow.

---

## Example 3 — Brand voice for podcast episode chunks

### User says

> I'm releasing a 5-episode podcast series. Same voice across all 5. Generate episode 1's intro.

(User has previously picked an Eleven voice_id they like: `21m00Tcm4TlvDq8ikWAM` — Rachel)

### Command

```
voiceover-maker --prompt-file ./episode-1-intro.txt \
                --model eleven-tts \
                --voice-id 21m00Tcm4TlvDq8ikWAM \
                --execute
```

### What happens

- Same voice_id used across the entire series — Rachel for all 5 episodes.
- Cost: depends on script length.
- Output saved with the model slug in the filename.

### Next episode

When generating episode 2, use the SAME voice_id:

```
voiceover-maker --prompt-file ./episode-2-intro.txt \
                --model eleven-tts \
                --voice-id 21m00Tcm4TlvDq8ikWAM \
                --execute
```

This is the most important pattern for branded content — voice_id is the brand asset, capture it once and reuse.

### What to notice

- Brand voice consistency = same provider + same voice_id, every time.
- The voice_id is the "brand" — pick once via the Eleven dashboard / their voice library, save it, reuse.
- Don't switch between OpenAI and Eleven mid-series — different vendors = different "speakers".

---

## Anti-pattern (don't do this)

### Reading SSML aloud via OpenAI

❌

```
voiceover-maker --prompt "Hello <break time='500ms'/> world" --model gpt-4o-mini-tts
```

Result: OpenAI reads "Hello break time five hundred milliseconds slash world".

✓ OpenAI doesn't accept SSML. Use punctuation for pacing:

```
voiceover-maker --prompt "Hello... world." --model gpt-4o-mini-tts
```

### Mixing OpenAI + Eleven mid-series

Episode 1 with `gpt-4o-mini-tts --voice alloy`. Episode 2 with `eleven-tts --voice-id rachel`. Result: listeners hear two different speakers, brand consistency broken.

✓ Pick one provider + one voice per series. Lock it.

### Long script in a single call

❌ 8000-char script → call cuts off at 4096 (OpenAI) or 5000 (Eleven) chars.

✓ Split into chunks ≤4000 chars + concatenate MP3s with ffmpeg.

### Voice cloning without permission

The skill doesn't support voice cloning. ElevenLabs supports it via their dashboard with explicit consent flows. Don't use unauthorized voices. Read Eleven's terms before cloning anyone's voice (including your own — for "your voice", clone it via the dashboard, get the voice_id, then use here).
