# Music pairing — picking and prompting the soundtrack

How to pick a music style, build a music prompt, and pair it with the video.

---

## `--music-style auto`

Algorithm:

1. Read the chosen VIDEO style's `Suggested music style` field. This is the curated pairing.
2. Verify the music style exists in `common/style-library/music/`.
3. If exists → use.
4. If not (or if user disagrees with pairing) → fall back to algorithmic match:
   - Video style mood + pacing → music style mood + BPM range
   - Tag-overlap scoring same as carousel auto-pick

Examples of curated pairings (from each video style's `Suggested music style`):

| Video style | Suggested music |
|---|---|
| `wes-anderson-symmetric` | `cinematic-orchestral` (or `jazz-fusion` for whimsy) |
| `fincher-cold-lowkey` | `ambient-drone` |
| `wong-kar-wai-neon-dream` | `synthwave` (or `lofi-hiphop-chill` for slow scenes) |
| `nolan-imax-handheld` | `cinematic-orchestral` |
| `chazelle-musical-glow` | `jazz-fusion` (or `cinematic-orchestral` lush version) |
| `refn-neon-static` | `synthwave` (or `ambient-drone` for slowest scenes) |
| `tarkovsky-slow-meditative` | `ambient-drone` |
| `villeneuve-monumental` | `cinematic-orchestral` |
| `soderbergh-natural-light` | `jazz-fusion` (subtle) or `lofi-hiphop-chill` |
| `edgar-wright-snap-cuts` | `synthwave` (high-energy) or `k-pop` (kinetic) |
| `david-lynch-dream-static` | `ambient-drone` (industrial leaning) |
| `inarritu-long-take-handheld` | `cinematic-orchestral` (string-heavy) |

Each music style file's frontmatter has `energy: calm|warm|driving|aggressive` and `bpm_range`. Auto-pick prefers:

- Slow / static video → calm energy, lower BPM
- Kinetic / snap video → driving energy, higher BPM
- Atmospheric → warm energy, mid BPM
- Aggressive / urgent video → aggressive energy, higher BPM

---

## Provider auto-pick (`--music-provider auto`)

Decision tree:

```
1. Genre = vocal-friendly (per music style's vocal_friendly field) AND --instrumental off?
     → suno-v5-5  (best vocals, two-box workflow, English-strong)

2. Genre = vocal-friendly AND --instrumental on (default for reel)?
     → suno-v5-5  (instrumental mode works; can hum / chant if needed)
        OR stable-audio-2-5 (cleanest instrumental, weaker on vocals which we don't need anyway)

3. Genre = instrumental-only (ambient-drone, cinematic-orchestral, jazz-fusion when --instrumental on)?
     → stable-audio-2-5  (best for sound design)
        OR lyria-3-pro (cleanest licensing, label-safe for commercial use)

4. Genre = cinematic-orchestral AND user wants commercial-safe?
     → lyria-3-pro  (refuses artist mimicry; clean rights)

5. Fallback if no API keys available?
     → fal-music or replicate-music routers (cover MusicGen / Stable Audio Open)
```

---

## Building the music prompt

The music style library file has 4 paste-ready blocks per genre — pick the one matching your provider:

### Suno provider

Use the `Suno Style box (paste-ready, ≤200 chars)` and the `Suno meta-tag stacks (by section)` blocks.

```python
suno_style_box = music_style.section("Suno Style box (paste-ready, ≤200 chars)")
suno_stacks = music_style.section("Suno meta-tag stacks (by section)")
```

Build:
- Suno `--prompt` argument = Suno Style box text (≤200 chars, natural language, NO brackets)
- Suno `--lyrics` argument:
  - If `--instrumental on` (reel default): pass the meta-tag stacks ONLY, no lyric content. Use just structural sections: `[Intro | ambient drone | low BPM]\n\n[Build | ...]\n\n[Outro | ...]`.
  - If `--instrumental off` (rare for reels): generate lyrics matching the topic, embed structural tags.

### Lyria 3 Pro provider

```python
lyria_block = music_style.section("Lyria 3 Pro field-driven")
```

Parse the block — it's already structured with `prompt:`, `key:`, `BPM:`, `lyrics:` fields. Pass each as a separate API parameter.

### ElevenLabs Music provider

```python
eleven_prompt = music_style.section("ElevenLabs Music prompt")
```

Single-prompt model with bracketed cues + timing markers. Append `Duration: <reel_seconds + 2>s` to specify length.

### Stable Audio provider

```python
stable_prompt = music_style.section("Suno Style box (paste-ready, ≤200 chars)")  # fallback
```

If music style has dedicated `Stable Audio prompt` block, use it. Otherwise use the Suno Style box text — it's natural-language and works.

---

## Music duration

Set `duration_seconds = total_reel_duration + 2`. The `+2` is a safety margin:
- ffmpeg `-shortest` will clip music to video length, so generating 2s extra protects against under-length.
- ffmpeg `mix_audio_over_video` adds a 0.5s fade-out at the end (configurable in `ffmpeg.py`).

Provider min/max duration constraints:

| Provider | Min | Max |
|---|---|---|
| Suno v5.5 | ~20s | ~4 min |
| Lyria 3 Pro | 30s | ~6 min |
| ElevenLabs Music | 10s | 5 min |
| Stable Audio 2.5 | 1s | ~3 min |
| MusicGen | 1s | ~30s typical |

For 15s reels: all providers handle. For 30-60s reels: all handle.

Note: Suno may generate 30-60s minimum even if you ask for 15s. ffmpeg `-shortest` handles the truncation.

---

## Volume / mixing

ffmpeg `mix_audio_over_video` uses:

- `volume=0.8` (music at 80% — leaves headroom if video had ambient audio)
- `afade=t=out:st=<duration-0.5>:d=0.5` (0.5s fade-out at end)

For a reel where the music should DUCK under spoken dialogue:
- v1 doesn't support ducking. The shots either have spoken audio (Veo/Sora/Kling generated) OR background music — pick one.
- If shots have spoken audio AND you want music: use `--music-volume 0.3` and accept the mix is suboptimal. (Or use a real editor.)

For v2.4.0+: add `--mix-mode replace|duck|overlay`.

---

## Instrumental rules

For reels, `--video-instrumental on` is default (no lyrics). Why:

- Reel duration is short (15-30s) — lyrics get truncated, sound abrupt.
- Vocal frequencies clash with spoken dialogue from the video shots.
- Algorithm-driven feed quality cares more about hook + visual rhythm than lyric content.

When to override to `--video-instrumental off`:
- Music-video-style reel (band footage, performance shot)
- The lyrics are the message (e.g., a viral chorus that's the punchline)
- User explicitly asks

When instrumental on:
- For Suno: pass `--instrumental` flag (no lyrics box content, or just structural tags)
- For Lyria: leave `lyrics:` field empty
- For Eleven: prompt = "instrumental, no vocals, <genre + mood>"
- For Stable Audio: same — naturally instrumental

---

## Genre + reel-format pairing recommendations

Most-used pairings as of 2026:

| Reel type | Recommended music style |
|---|---|
| Product reveal (tech / e-com) | `synthwave` or `cinematic-orchestral` |
| Founder talking head | `lofi-hiphop-chill` or `ambient-drone` (subtle bed) |
| Educational explainer | `cinematic-orchestral` or `lofi-hiphop-chill` |
| Lifestyle / fashion | `afrobeats` or `synthwave` |
| Comedy / fast-paced | `k-pop` or `hyperpop` |
| Mood / atmospheric brand | `ambient-drone` |
| Sports / energy / workout | `hardcore-punk` or `drill-uk` (warn about copyright/aggression) |
| Calm / wellness / slow living | `ambient-drone` or `lofi-hiphop-chill` |

---

## What gets saved to `script.md`'s music section

````markdown
## Music

**Style**: <music-style-id> · <BPM range> · <energy>
**Provider**: <slug>
**Duration**: <seconds>
**Instrumental**: <yes/no>

### Prompt (paste into provider's UI if API call fails)

[Per-provider block, e.g.:]

#### Suno Style box

```
<text>
```

#### Suno Lyrics box

```
<text or empty for instrumental>
```
````

This means: even if API generation fails, the user has the music prompt to manually paste.
