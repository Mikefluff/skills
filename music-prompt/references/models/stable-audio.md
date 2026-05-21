# Stable Audio

Stability AI's audio family. Strong on sound design and instrumental, weak on vocals. Treat as a production/composition tool, not a song generator.

---

## Stable Audio 2.5

**Strengths**: enterprise-grade sound design + instrumental music, ARC post-training (only 8 inference steps — very fast), audio-to-audio supported, multi-part composition (intro / development / outro).
**Weaknesses**: 3 min hard cap; weak at vocals (treat as composition/production tool, not a song generator); not open-weights (the Open / Open Small variants are).

Released September 2025.

### Syntax / Format rules

**Free-text prompt + multi-part composition descriptors**. No formal brackets, no formal section headers.

- **Composition prose**: describe the full arc in one paragraph — `"intro builds with X, development moves to Y, outro resolves to Z"`.
- **Instrumentation lead-first**: name the primary instrument or texture first, then supporting layers.
- **Production qualities**: explicit (e.g. `"analog tape saturation"`, `"crisp transients"`, `"deep sub-bass"`, `"wide stereo field"`).
- **Tempo and key**: include as plain text (`"94 BPM"`, `"in D minor"`).
- **Audio-to-audio**: pass an input audio file + prompt to morph style while preserving structure. Useful for sound-design variations.
- **Length**: specify in seconds inside the prompt or via the dedicated `duration` parameter on API.

**No vocal generation** — don't request singing; the model degrades. If a track needs vocals, generate the bed here and overdub elsewhere.

Available via Replicate / fal / Stability API.

### Prompt template

```
{Duration in seconds}. {Tempo and key}. {Genre / sound-design category}, {mood / function}.
{Lead instrument or texture}, {2-4 supporting layers}, {production qualities}.
Structure: {intro — what happens}, {development — what changes}, {outro — how it resolves}.
```

### Example

```
90 seconds. 76 BPM in G minor. Cinematic underscore for a slow-burn tension scene, restrained and unresolved.
Lead bowed double-bass with hairline string noise, granular synth pad swelling underneath, sparse felt-piano notes, a single tuned-metal hit every 8 bars, low sub-rumble, wide stereo field, analog tape saturation, dark and uncompressed transients.
Structure: 12-second intro with bass and pad only, development at 0:12 introduces felt-piano and the tuned-metal hits while the pad widens and detunes, outro from 1:18 strips back to the bass and a single decaying piano note, no resolution to the tonic.
```

### Notes / Pitfalls

- **Don't expect singing** — vocal generation is poor. Use for instrumental, sound design, ambient, score, loops.
- **ARC = 8 inference steps** — gen is fast enough to iterate aggressively. Run many variations rather than over-engineering one prompt.
- **Audio-to-audio is the killer feature** for sound design — pass a rough sketch (even hummed or DAW-stubbed) + a style prompt to refine.
- **No formal section headers** — section structure is interpreted from prose. Be explicit about timing if you want predictable boundaries.
- **3-min cap** is hard. For longer cues, render multiple 3-min segments with overlapping transitions and cross-fade externally.
- **Not open-weights** — the closed 2.5 model is API-only. The Open variants below are the self-host path.

---

## Stable Audio Open / Open Small

Open-weights variants (released 2024-2025).

- **Stable Audio Open** — open-weights, runs on a workstation GPU, commercial-use license (check current terms before shipping).
- **Stable Audio Open Small** — smartphone-class capability, runs on-device for short generations.
- Quality below 2.5 but acceptable for sound design, loops, stems for layering.
- Use when on-prem / commercial / edge deployment matters more than peak quality.
- Same prompt conventions as 2.5 — free-text, instrumentation-led, no formal brackets.
