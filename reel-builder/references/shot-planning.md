# Shot planning

How to break a topic / brief into shots with timing, screenplay, and captions.

---

## Shot count templates

### 1 shot × 8s — atmospheric / one-take

For: mood pieces, single character monologue, brand ID stings, product reveals where motion = the whole point.

Structure:
- Whole arc fits in one continuous take.
- Hook lands in first 1.5s (subject reveal + intent).
- Mid-shot: payoff / motion peak.
- End: lingering frame, possibly with subtle camera move.

### 3 shots × 5s = 15s — DEFAULT for Reels / TikTok

For: most narrative reels — hook → development → payoff.

| # | Role | Duration | Function |
|---|---|---|---|
| 1 | hook | 5s | Land the headline + setup question / claim |
| 2 | beat | 5s | Develop the idea OR show contrast |
| 3 | payoff | 5s | Resolve / land the conclusion / CTA |

### 4 shots × 5s = 20s — extended narrative

| # | Role | Duration | Function |
|---|---|---|---|
| 1 | hook | 5s | Headline |
| 2 | setup | 5s | Context / build-up |
| 3 | turn | 5s | Twist / reveal / surprise |
| 4 | payoff | 5s | Conclusion / CTA |

### 5 shots × 6s = 30s — long-form short

Used for explainers, B2B narratives, deeper hook+arc+resolution structure.

Roles: hook → setup → conflict → turn → payoff/CTA.

### Provider duration caps

| Provider | Max single-shot duration |
|---|---|
| Veo 3.1 | 8 seconds |
| Veo 3.1 Fast | 8 seconds |
| Sora 2 | 10 seconds |
| Sora 2 Pro | 20 seconds |
| Kling 3.0 Omni | 10 seconds |
| Kling 3.0 (legacy) | 5-10 seconds |
| Runway Gen-4 | 10 seconds |
| Runway Gen-4 Turbo | 10 seconds |
| Hailuo 02 | 6-10 seconds |

If `--shot-duration` exceeds provider cap → skill warns + clamps to max. To get longer single shots, use Sora 2 Pro (20s) or use Runway Aleph extend on a base shot.

---

## Screenplay format

When `--script-file <path>` is passed (user pre-writes), the file MUST follow this shape:

```markdown
# Reel script: <topic>

## Meta

- Total duration: 15s
- Aspect: vertical (9:16)
- Style: <video-style-id>
- Music: <music-style-id>

## Shots

### Shot 1 (hook) — 0:00-0:05

**Action**: <30-60 word visual description — subject + setting + motion>

**Composition**: <framing — wide / medium / close-up / extreme close-up; angle; movement>

**Caption (overlay)**: "<short overlay caption, 3-7 words>"

**Spoken (optional)**: "<dialogue line, ≤12 words>"  <!-- only if shot has on-camera speech -->

---

### Shot 2 (beat) — 0:05-0:10

[same structure]

---

### Shot 3 (payoff) — 0:10-0:15

[same structure]

---

## Post caption (for the platform's text field)

<1-3 sentences for the platform caption, NOT in the video>

#hashtag #hashtag ...
```

When the skill drafts the script itself (no `--script-file`), it writes this exact format to `./generated/reel/<slug>/script.md` BEFORE generation starts.

---

## The hook (first 1-2 seconds)

This is the single most important second of the reel. Mobile users scroll past in 1.5s.

Rules for shot 1 framing:

1. **Subject in frame from frame 1.** No fade-in from black, no logo intro, no establishing shot of an empty room.
2. **Motion or surprise in first second.** Static shots lose 60% more viewers in the first 2s than shots with motion.
3. **Pattern interrupt visually.** Unexpected color, scale, framing — give the algorithm something to optimize for "watched past 3s".
4. **Caption synced to first frame** if `--captions on`. The text headline should be readable at 0.5s.

Anti-patterns for shot 1:
- Empty room, panning slowly. (Boring.)
- Title card. (Sponsored ads do this — engagement tanks.)
- Slow zoom-in to subject. (Wastes the hook window.)
- Closing the laptop. (You'd be surprised — this is a common "reveal" framing that bombs.)

---

## Dialogue / spoken lines

If a shot includes on-camera dialogue (lip-synced):

- Limit: **≤12 words per shot**, hard cap. Models lose lip-sync past ~3 seconds of speech.
- Spoken line is passed to the provider via the `dialogue` field (Veo 3.1 / Sora 2 / Kling 3.0 Omni support this).
- Provider auto-syncs lip movement to the audio it generates.
- If you need >12 words of spoken content: split across multiple shots, OR (preferred) make it voiceover (currently out of scope — v2.4.0).

Models capable of in-clip dialogue + native audio (as of 2026-05):
- Veo 3.1 / Veo 3.1 Fast — native audio + dialogue + ambient
- Sora 2 — native audio + cameos + dialogue
- Kling 3.0 Omni — native audio + dialogue

Models NOT capable: Runway (visual only), most fal/replicate hosted ones.

If using a non-dialogue-capable provider, the music track carries all audio and shots are silent.

---

## Captions (text overlays burned via ffmpeg)

Defaults when `--captions on`:

- One caption per shot, synced to shot start/end.
- ≤8 words per caption (mobile reading speed = ~3 words/sec).
- Positioned in lower-third (about 70% down the frame) to avoid covering subjects.
- Font: bold sans-serif, white with 60% black backplate for readability.
- Font size: scaled to ~7% of frame height.

Caption text comes from the screenplay's `**Caption (overlay)**:` field per shot.

For accessibility, the post caption (platform text field) duplicates the spoken / key text — burned captions on video are a UX feature, not accessibility.

To override caption styling: edit the ffmpeg command in `references/ffmpeg-stitch.md` — currently fixed in v1.

To turn off: `--captions off`. The shots are stitched + music applied without text.

---

## Auto-script from `--topic`

The skill invokes `viral-text` with a custom template:

```
[viral-text input]
Topic: <topic>
Format: vertical 9:16 reel script
Shots: 3 × 5s
Constraints:
  - Shot 1 = hook (first 2 sec must land)
  - Shot 2 = beat (development or contrast)
  - Shot 3 = payoff (conclusion or CTA)
  - Each shot ≤12 words of dialogue if any
  - Caption per shot ≤8 words
Output: in the screenplay markdown format from reel-builder shot-planning ref
```

Result: a script.md draft. User can edit before running with `--script-file <draft>` if they want tweaks.

---

## Auto-script from `--research <brief>`

When research brief is the input:

1. TL;DR sentence 1 → Shot 1 hook
2. Key fact / contrarian frame → Shot 2 beat
3. Suggested angle's CTA → Shot 3 payoff
4. Notable quote (if present) → can be used as spoken line in any shot

The skill picks ONE angle from the brief's Suggested angles section and shapes the 3 shots around it.

---

## When to use fewer / more shots

- **1 shot**: brand sting, single-character monologue, product reveal where motion = the message.
- **3 shots (default)**: most narrative reels. Best for "tip / fact / list" content.
- **4 shots**: if there's a clear turn (twist / reveal). Don't add a 4th if it's just more development.
- **5 shots**: long-form B2B explainers, narrative microdocs. Audience drop-off past 25s is steep — only do 5 shots if you've validated the hook works.

---

## Anti-pattern: shot-too-short

Tempting to do 3 × 3s = 9s reel. Don't:

- Mobile attention requires ~1.5s to land each shot's content. 3s shots barely have time.
- ffmpeg concat of 3s shots feels jittery on most feeds.
- Generative video providers have minimum durations (Veo 3.1 minimum = 4s). Shorter shots get rejected.

Stick to 5s minimum per shot. 6s is even safer.
