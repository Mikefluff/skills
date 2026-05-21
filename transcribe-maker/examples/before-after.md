# transcribe-maker — calibration

3 example sessions.

---

## Example 1 — Tutorial video to SRT

### User says

> Записал туториал на YouTube (10 минут). Нужны субтитры в SRT.

### Plan

```
transcribe-maker --input ./tutorial.mp4 --format srt --lang en --output ./tutorial.srt --execute
```

### What happens

1. Skill probes duration via ffprobe.
2. Estimates cost: 10 min × $0.006/min = $0.06.
3. Sends file to OpenAI Whisper API.
4. Saves SRT to `./tutorial.srt`.

### Next steps

Burn captions onto the video:

```
subtitle-burner burn ./tutorial.mp4 --subtitle ./tutorial.srt --style modern --output ./tutorial-captioned.mp4
```

Result: ready-to-upload video with burned-in captions.

---

## Example 2 — Russian podcast to plain text transcript

### User says

> У меня подкаст час, на русском. Нужна расшифровка в plain text для блог-поста.

### Plan

```
transcribe-maker --input ./podcast.mp3 --format text --lang ru --output ./podcast-transcript.txt --execute
```

### What happens

1. Cost: 60 min × $0.006 = $0.36.
2. Whisper transcribes in Russian (language hint accelerates).
3. Saves plain-text transcript (no timestamps).

### Notes

- For blog conversion: open the .txt in your editor, add headings + paragraph breaks, edit for readability.
- If the file is >25 MB: see `references/preprocessing.md` for splitting.

---

## Example 3 — Multilingual interview with word-level timestamps

### User says

> Интервью с английскими и русскими репликами. Нужны таймстампы для каждого слова — буду делать анимированные субтитры.

### Plan

```
transcribe-maker --input ./interview.mp4 --format verbose_json --output ./interview.json --execute
```

### What happens

1. Auto-detects dominant language.
2. Returns verbose JSON with segments[] and words[] (per-word start/end/probability).
3. Saves JSON to `./interview.json`.

### Next steps

Parse JSON for word-level animation:

```python
import json
with open("./interview.json") as f:
    data = json.load(f)
for segment in data["segments"]:
    for word in segment["words"]:
        print(f"{word['start']:.2f}s → {word['end']:.2f}s : {word['word']}")
```

Feed into After Effects / Premiere as a CSV for kinetic typography.

---

## Anti-patterns (don't do this)

### Upload 100 MB video file directly

❌ `transcribe-maker --input ./huge-podcast.mp4` when file >25 MB.

Result: API rejection.

✓ Extract audio first or compress: `ffmpeg -i huge.mp4 -vn -b:a 64k audio.mp3` → transcribe `audio.mp3`.

### Expect perfect accuracy without proofreading

❌ Ship raw Whisper output as production captions.

Result: name misspellings, technical jargon errors.

✓ Always proofread. Whisper is 95% accurate for clean English; lower for noisy/accented/technical content.

### Use Whisper for music transcription

❌ Pass a song expecting accurate lyrics.

Result: garbage or hallucinated lyrics.

✓ Whisper is SPEECH-only. For lyrics: use dedicated lyrics-extraction tools (manual or specialized services).

### Skip the `--lang` hint for non-English

❌ Russian podcast without `--lang ru`.

Auto-detect usually works, but the language hint speeds up + improves accuracy.

✓ Always pass `--lang` when you know the dominant language.
