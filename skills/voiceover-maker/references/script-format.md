# Script format — voiceover-maker

How to write a script for TTS that produces a natural-sounding voiceover.

---

## Basics

- Write the way you want it spoken.
- Period at the end of declarative sentences. Question mark for questions. Exclamation for emphasis.
- Commas for short pauses. Em-dashes (—) for longer dramatic pauses.
- One paragraph break = a longer pause.

Bad:

```
SLOW SOFTWARE: A Workshop For Solo Founders Who Want To Build Without Speed As The Only Metric
```

Sounds robotic — TTS reads each capital separately or mispaces.

Good:

```
Slow software. A workshop for solo founders who want to build without speed as the only metric.
```

Reads naturally.

---

## Pacing via punctuation

- `,` ≈ 250ms pause
- `;` ≈ 400ms pause
- `:` ≈ 350ms pause
- `.` ≈ 500ms pause
- `!`, `?` ≈ 500ms pause + intonation change
- `—` (em-dash) ≈ 600ms pause
- `…` (ellipsis) ≈ 800ms pause + trailing-off tone
- Paragraph break ≈ 1000ms pause

If you want a specific pause length on Eleven, use SSML:

```
This is the first sentence. <break time="2s"/> And now after a long pause.
```

OpenAI gpt-4o-mini-tts doesn't accept SSML; use ellipses + paragraph breaks instead.

---

## Emphasis

Both providers respond to capitalization for emphasis:

- "I really mean it" → flat
- "I REALLY mean it" → emphasis on "really"

Don't capitalize entire sentences — TTS may read each word slowly or letter-by-letter.

Eleven additionally supports SSML emphasis:

```
This is <emphasis level="strong">very</emphasis> important.
```

OpenAI ignores SSML — use caps + punctuation.

---

## Numbers + abbreviations

- `2026` → "twenty twenty-six"
- `15:00` → "fifteen hundred" (OpenAI) or "three p.m." if you write "3pm"
- `Q1 2026` → "Q one twenty twenty-six" — ambiguous. Write "Quarter one of twenty twenty-six".
- `URL`, `API`, `CEO` — read as letters most of the time. If you want it spelled-out as the word, just leave caps.
- Phone numbers: write with hyphens/spaces — "555-1234" reads as "five five five, one two three four" cleanly.

Decimals + currencies:

- `$1.50` → "one dollar and fifty cents" (OpenAI) — usually correct
- `1.50` (no $) → "one point five zero"
- `1,500` → "one thousand five hundred" — usually correct
- `1500` → "fifteen hundred" — sometimes "one five zero zero"

When in doubt, spell numbers as words for non-obvious cases.

---

## Names + pronunciation

Common-name conventions:

- `Mikhail` → may read as "Mick-hayl" or "Mik-eel" — both wrong. Write `Mick-hayil` (forced phonetic) or use Eleven SSML.
- `Чайковский` → write `Tchaikovsky` (English transliteration) or use Eleven multilingual + Cyrillic.
- Company names with mixed case (`iPhone`, `iPad`) — TTS handles these well usually.
- Product names you've invented: do a test call, adjust spelling phonetically if wrong.

Phonetic spelling for Eleven specifically:

```
<phoneme alphabet="ipa" ph="məˈkhaɪl">Mikhail</phoneme>
```

This requires IPA knowledge. Easier alternative: just respell phonetically in plain English.

---

## Multi-paragraph scripts

For voiceovers >1 minute, structure into paragraphs:

```
Welcome to the show.

Today's topic is slow software — what it means, why it matters, and how to ship it without losing your mind.

Let's start with a definition.
```

Each paragraph break = ~1s natural pause. Good for transitions between sections.

For chapters (think podcast episode with intro / body / outro):

```
[Intro music plays] Hi, I'm Alex, and this is the Slow Software podcast.

[End intro music] In today's episode...

[Outro music plays] Thanks for listening.
```

Bracketed cues like `[Intro music plays]` are NOT spoken by TTS providers — they're for YOU to know where to mix in non-speech elements during post-production. Don't expect the TTS to include them.

---

## Length limits

- **OpenAI gpt-4o-mini-tts**: 4096 chars per call.
- **ElevenLabs eleven-tts**: 5000 chars per call (model-dependent — multilingual_v2 supports up to 5000).

For longer scripts:

1. Split into chunks at paragraph breaks
2. Run TTS on each chunk
3. Stitch with `ffmpeg -i 'concat:part1.mp3|part2.mp3|...' -acodec copy combined.mp3`

The `subtitle-burner` skill has a sibling planned (`audio-concat`) that handles this — for now do it manually.

---

## Voice consistency across chunks

If you chunk a long script:

- Same `--voice` / `--voice-id` for all chunks
- Same provider (don't mix OpenAI + Eleven mid-script)
- Same speed / stability settings

Otherwise the chunks will sound like different speakers.

---

## Common gotchas

### Reading punctuation aloud

Sometimes TTS reads quotation marks: `"hello"` becomes "quote hello quote".

Fix: use the actual unicode curly quotes `"hello"` or remove them entirely.

### Pronouncing URLs

`https://example.com/path` will be read literally as "h-t-t-p-s colon slash slash..."

Fix: either remove URLs from the voiceover script (mention "link in description") or spell out: "example dot com slash path".

### Acronyms

Some acronyms read as words (NASA → "nasa") and some as letters (USB → "u s b"). Test, and if wrong, use periods to force letter-reading: "U.S.B."

### Punctuation in code

Code snippets read terribly in TTS — every symbol gets vocalized. Don't put code in voiceovers; reference it in the script and overlay the actual code visually if needed.

---

## SSML quick reference (Eleven only)

```xml
<speak>
  This is the first sentence.
  <break time="500ms"/>
  This has <emphasis level="strong">emphasis</emphasis>.
  My name is <phoneme alphabet="ipa" ph="məˈkhaɪl">Mikhail</phoneme>.
  <prosody rate="80%">Slow down here.</prosody>
  <prosody rate="120%">Speed up here.</prosody>
</speak>
```

OpenAI doesn't accept SSML. For pace control on OpenAI, use punctuation + multiple sentences.
