# Captions — writing and timing

How to write the burned-in captions for a reel.

---

## Length budget

Per caption (one per shot in v1):
- **3-8 words** is the sweet spot. Mobile reading speed ~3 words/sec; a 5s shot allows ~12-15 words but reading + watching split attention favors brevity.
- Punctuation counts toward visual weight. Avoid commas unless they create rhythm: "Faster. Cheaper. Open." beats "Faster, cheaper, and open."
- All-caps for high-impact reels (Edgar Wright / hyperpop / drill style). Sentence case for editorial / documentary tone (Soderbergh / Tarkovsky / Villeneuve).

---

## Placement

Always lower-third (about 70% down the frame from top). This avoids:
- The subject's face area in the upper half
- Mobile UI bars (status bar at top, navigation/dock at bottom)
- The TikTok / Instagram / YouTube Shorts UI overlays (right edge, bottom edge)

Specifically:
- Vertical 9:16: y = 70% of frame height (frame is 1920 tall → y ≈ 1344 from top)
- Square 1:1: y = 70% (1080 → y ≈ 756)
- Horizontal 16:9: y = 75% (1080 → y ≈ 810) — more space at bottom of horizontal

ffmpeg drawtext filter: `y=h-(text_h*2.5)` puts text ~2.5 text-heights from the bottom — works for default font size 48 → ~120px from bottom edge on 1920p.

---

## Timing

By default, each caption is on-screen for the duration of its shot:

```
Shot 1: 0:00 - 0:05  → Caption 1 visible 0:00 - 0:05
Shot 2: 0:05 - 0:10  → Caption 2 visible 0:05 - 0:10
Shot 3: 0:10 - 0:15  → Caption 3 visible 0:10 - 0:15
```

Slight delay (0.2s after shot start, 0.3s before shot end) can feel more polished:

```
Shot 1: 0:00 - 0:05  → Caption visible 0:00.2 - 0:04.7
```

But: in TikTok/Reels feeds, viewers may scroll IN mid-shot — so don't make captions appear with too much delay. v1 uses shot-aligned timing (no offset).

---

## Caption content patterns

### Hook patterns

Strong:
- "The 4-tool stack that wins."
- "Why 73% of founders switched."
- "This is what changed in 2026."
- "Stop doing this."
- "Watch what happens at 0:10."

Weak (avoid):
- "Hey, welcome to my video!" (waste)
- "In this video, I'll show you..." (waste)
- "Get ready to learn!" (waste)
- "🔥 New trend alert! 🔥" (emoji + hype = scrolled)

### Beat / development patterns

Strong:
- Setup + payoff: "First: <thing>." then "But then..."
- Contrast: "Old way." vs "New way."
- Question: "Why does this work?"
- Stat: "73% saved 8 hours/week."

Weak:
- Adjective stacking: "Amazing, incredible, life-changing..." (hype, undelivered)
- Acronyms without expansion: "ROAS up 4x." (only works if audience knows ROAS)

### Payoff / CTA patterns

Strong:
- Call-to-action: "Save this." / "Try it tonight."
- Question: "What's in your stack?"
- Tease: "Full guide in bio."
- Stat-bookend: "From 0 to $50K in 90 days."

Weak:
- "Follow for more!" (every reel says this; banalized)
- "Comment below 👇" (without specific thing to comment)
- "Like and subscribe!" (only works on YouTube, scrolled past on Reels)

---

## Caption style by directorial video style

| Video style | Caption tone |
|---|---|
| `wes-anderson-symmetric` | dry, deadpan, often short literal labels ("Day 1." "Day 47.") |
| `fincher-cold-lowkey` | terse, intelligent, often single words ("Evidence." "Method." "Outcome.") |
| `wong-kar-wai-neon-dream` | melancholic, poetic, slightly elliptical ("In the city we forgot.") |
| `nolan-imax-handheld` | urgent, declarative, expandable to longer sentences ("Time is the only currency.") |
| `chazelle-musical-glow` | romantic, rhythmic, often two-beats ("Spring. Then snow.") |
| `refn-neon-static` | minimal, detached, often single words ("Drive." "Hunt.") |
| `tarkovsky-slow-meditative` | sparse, philosophical, intentionally slow to surface ("Watch the water.") |
| `villeneuve-monumental` | declarative, vast-scaled ("A century before us.") |
| `soderbergh-natural-light` | observational, almost transcript-like ("She said no.") |
| `edgar-wright-snap-cuts` | punchy, rhythmic, often 3-word triplets ("Make. Coffee. Now.") |
| `david-lynch-dream-static` | uncanny, ambiguous, often question-form ("Why does she stay?") |
| `inarritu-long-take-handheld` | tense, direct ("We're not going home.") |

---

## Multi-language captions

For non-English captions (Russian / Chinese / Spanish / etc):

- **v1 limitation**: default ffmpeg font may not have glyphs for Cyrillic / CJK / Arabic / etc. Result: captions render as empty boxes or fallback characters.
- **Workaround**: edit `common/runners/ffmpeg.py` `burn_captions()` to pass `:fontfile=/path/to/font-with-coverage.ttf`. Specify path to a TTF with the script you need (e.g., Inter, Noto Sans, IBM Plex Sans — all have wide coverage).
- **Future**: `--caption-font <path>` flag (v2.4.0+).

Avoid mixing scripts in one caption: "Привет world!" — most fonts have one or the other.

---

## Caption-free reels

`--captions off` for:
- Atmospheric / mood reels where text would break the spell (Tarkovsky / Lynch / Refn styles)
- Music-video reels where the music carries everything
- B2B brand pieces with no specific message — just feel

These reels rely entirely on:
- Visual storytelling in shots
- Music tone-setting
- The platform caption (text below the video) doing the message work

---

## Caption sync to spoken dialogue

If a shot has spoken dialogue (Veo / Sora / Kling native audio):

- Caption SHOULD match (or transcribe) the spoken line. Otherwise mismatch is jarring.
- Caption shows from spoken-line-start through end (which is the whole shot for v1's coarse timing).
- v1 doesn't auto-extract spoken transcription from generated video — user must write the caption matching what they put in `Spoken: "..."` field of the screenplay.

---

## Storage in script.md

The screenplay's `**Caption (overlay)**:` field per shot is the source. captions list passed to ffmpeg:

```python
captions = [
    (0.0, 5.0, "The 4-tool stack."),
    (5.0, 10.0, "73% of founders use it."),
    (10.0, 15.0, "Save for later."),
]
```

Timing comes from shot start/end. Text comes from the screenplay field. ffmpeg renders.
