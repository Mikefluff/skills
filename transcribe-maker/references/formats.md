# Output formats — transcribe-maker

Whisper supports 5 output formats. Each suits a different downstream use.

---

## `srt` (default — best for captions)

**SubRip Subtitle** — the standard captions format. Used by VLC, YouTube, virtually every video player.

**Structure**:
```
1
00:00:00,000 --> 00:00:04,500
Welcome to the podcast.

2
00:00:04,500 --> 00:00:08,200
Today we're talking about software.
```

**Use for**: feeding into `subtitle-burner` to burn captions onto video; manual upload to YouTube; archival captions.

**Timestamp resolution**: millisecond.
**Segment length**: 5-15 seconds typically (Whisper auto-segments by sentence/natural pause).

---

## `vtt`

**WebVTT** — modern web-standard subtitles, used in HTML5 `<track>` elements.

**Structure**:
```
WEBVTT

00:00:00.000 --> 00:00:04.500
Welcome to the podcast.

00:00:04.500 --> 00:00:08.200
Today we're talking about software.
```

**Differences from SRT**:
- Header `WEBVTT` required
- Uses `.` for milliseconds (vs `,` in SRT)
- Supports styling cues (the skill doesn't add them; raw Whisper output)

**Use for**: web players, HTML5 video, modern streaming setups.

---

## `text`

**Plain text** — no timestamps. Just the transcript paragraph.

**Structure**:
```
Welcome to the podcast. Today we're talking about software. We have a special guest...
```

**Use for**: blog post drafts, search indexing, content analysis, ChatGPT context, manual editing into a clean article.

**No timestamps** — can't align back to source video. For that use SRT.

---

## `json`

**Simple JSON** with the transcript and language detection.

**Structure**:
```json
{
  "text": "Welcome to the podcast..."
}
```

(Plus possibly `task` and `language` fields.)

**Use for**: programmatic parsing where you just need text + detected language.

---

## `verbose_json`

**Detailed JSON** with word-level timestamps and segment data.

**Structure**:
```json
{
  "task": "transcribe",
  "language": "en",
  "duration": 60.5,
  "text": "Welcome to the podcast...",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 4.5,
      "text": " Welcome to the podcast.",
      "tokens": [...],
      "temperature": 0.0,
      "avg_logprob": -0.3,
      "compression_ratio": 1.2,
      "no_speech_prob": 0.01,
      "words": [
        {"word": "Welcome", "start": 0.1, "end": 0.6, "probability": 0.99},
        {"word": "to", "start": 0.6, "end": 0.7, "probability": 0.99},
        ...
      ]
    }
  ]
}
```

**Use for**: word-level video synchronization, animated captions (one word at a time), confidence-based filtering, advanced video editing workflows.

---

## Decision tree

```
Need captions for video burning / YouTube
  → srt

Need captions for HTML5 player
  → vtt

Need clean transcript text (blog post / search)
  → text

Need basic programmatic access
  → json

Need word-level timestamps (animated captions / sync)
  → verbose_json
```

---

## Whisper segmentation behavior

Whisper auto-segments transcripts at natural pauses + sentence boundaries.

- Average segment: 5-15 seconds
- Long monologues: up to 30 seconds per segment
- Very fast speech: 2-5 seconds

For different segmentation: split + concatenate manually, or use a different tool (Otter.ai allows manual re-segmentation).

---

## Language behavior

- Auto-detect works well for clear single-language audio
- Multilingual content (code-switching): pass `--lang` for the DOMINANT language; secondary language phrases may transliterate weirdly
- ISO-639-1 codes: en (English), ru (Russian), es (Spanish), fr (French), de (German), zh (Chinese), ja (Japanese), ko (Korean), etc.

For TRANSLATION (not transcription) to English: use OpenAI's `/v1/audio/translations` endpoint directly. The skill v1 only does same-language transcription.

---

## Temperature behavior

- `--temperature 0` (default): deterministic, single best transcription
- `--temperature 0.2-0.5`: slight variation, useful for re-rolling problematic segments
- `--temperature 1.0`: high variation, generally not useful for transcription

Stick with 0 unless you're debugging a problematic file.
