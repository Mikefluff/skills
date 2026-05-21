---
name: reel-builder
description: "Orchestrator skill — turns a topic / research brief / script into a 9:16 vertical reel: 1-4 video shots + matched background music + ffmpeg-stitched final.mp4 with optional burned-in captions. Wraps viral-text (for script) + video-prompt --execute + music-prompt --execute + common video/music style library + ffmpeg. Modes: --topic / --research / --script-file; --shots 1-5; --shot-duration <seconds>; --style auto|<library-id>; --music-style auto|<library-id>; --aspect vertical|square|horizontal; --captions on|off; --execute; --resume. Outputs: ./generated/reel/<slug>/final.mp4 + shots/ + music.mp3 + script.md + manifest.json. Use when the user says 'make a reel about X', 'short video on Y', 'TikTok / Reels / Shorts about Z'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
End-to-end reel generator. Input: topic OR research brief OR pre-written script. Output: a single MP4 file with stitched video shots + background music + optional captions, plus the individual components (shots, music, script) for reuse.

This skill orchestrates:
1. `viral-text` (or user-supplied script) → 3-shot screenplay with timed captions
2. `video-prompt --execute` → N video shots via the chosen provider (Veo 3.1 / Sora 2 / Kling 3.0 / Runway Gen-4)
3. `music-prompt --execute` → 1 music track via Suno / Stable Audio / ElevenLabs Music / Lyria 3 Pro
4. `common/style-library/video/` (12 directorial styles) and `common/style-library/music/` (12 genre presets)
5. ffmpeg → concat shots, mix music, burn captions

Use when the user wants a finished reel, not just video prompts. Without `--execute`, returns assembled prompts; with `--execute`, generates the MP4.

This skill does NOT:
- Add a voiceover / TTS narrator (out of scope for v1 — would need ducking/mixing logic; planned v2.4.0)
- Composite multi-track edits beyond hard cuts (no dissolves, no transitions other than concat)
- Beat-sync shots to music BPM (would need BPM detection; planned later)
- Post to platforms — output is an MP4 you upload via the platform's UI
- Run editing software (Premiere / DaVinci / CapCut) — uses ffmpeg only
</objective>

## ROLE

Topic / research / script → build 1-4 shot screenplay with timing → resolve video style (directorial anchor) + music style (genre preset) → generate shots in parallel (async polling) + music in parallel → ffmpeg concat → ffmpeg audio mix → optional caption burn-in → print final paths.

## PIPELINE

1. **Resolve input source**:
   - `--script-file <path>`: read pre-written script with shot timing markers and captions (skip step 2)
   - `--research <path>`: read brief, extract key facts, condense into a 15-30 sec hook+payoff narrative
   - `--topic "<text>"`: invoke `viral-text` to draft a hook+beats+payoff script (~80-150 words)

2. **Plan shots** — see `references/shot-planning.md`:
   - Default: 3 shots × 5 sec = 15 sec total (TikTok / Reels sweet spot)
   - Single-shot mode: 1 shot × 8 sec (Veo 3.1 max) — for atmospheric / one-take pieces
   - Each shot has: index, screenplay line (action description), camera/composition note, dialogue or VO line (optional)
   - Shot 1 always carries the hook (must land in first 1-2 sec)

3. **Resolve video style** — see `references/style-resolution.md`:
   - `--style <id>`: load `common/style-library/video/<id>.md`. Use the `Shot anchor (per-shot prompt fragment)` block.
   - `--style auto`: pick from library based on topic/tone + pacing requirements.
   - Same anchor APPENDED to every shot's prompt. ONE style for the whole reel.

4. **Resolve music style** — see `references/music-pairing.md`:
   - `--music-style <id>`: load `common/style-library/music/<id>.md`. Use the Suno Style box + meta-tag stacks if Suno selected; or the Lyria field-driven block if Lyria; or the ElevenLabs prompt if Eleven.
   - `--music-style auto`: pick from library based on video style (each video style has a "Suggested music style" field — start there) + tempo requirement.
   - One music track for the whole reel.

5. **Pick providers** — see `references/model-picker.md`:
   - Video: `--video-provider auto|veo-3-1|sora-2|kling-3-0|runway-gen-4|fal-video`. Auto-pick by style requirements.
   - Music: `--music-provider auto|suno-v5-5|stable-audio-2-5|eleven-music|lyria-3-pro`. Auto by genre/instrumental.

6. **Build per-shot video prompts**:
   ```
   <shot anchor (video style)>

   <shot action: subject + motion + setting, 30-60 words>

   Composition: <framing from screenplay>.
   Duration: <N> seconds.
   Aspect: <9:16 vertical | 1:1 square | 16:9 horizontal>.

   <if shot has dialogue> Spoken: "<EXACT dialogue, ≤12 words>" (subject lips sync).
   ```

7. **Build music prompt** based on music-style library entry:
   - Suno: Style of Music box + Lyrics box (instrumental: empty/structured-tags-only)
   - Lyria: prompt + key + BPM + (optional lyrics)
   - Eleven: single prompt with bracketed cues + duration
   - Stable Audio: free-text instrumental composition

8. **Estimate cost** — sum video shots + music. Confirm batch if >$0.10 and not `--yes`.

9. **Execute in parallel**:
   - Video shots: parallelism N (default 2 — video calls are 30-90s each, more concurrency stresses rate limits)
   - Music: 1 call running concurrently
   - All async via JobHandle + poll-with-timeout
   - Manifest updated after each completion

10. **ffmpeg stitch** (only if all shots succeeded; partial failures stop here for safety):
    - Concat N shots in order: `ffmpeg -f concat -c copy → shots-concat.mp4`
    - Mix music: replace audio track with music.mp3, fade-out 0.5s at end → with-music.mp4
    - (If `--captions on`) Burn captions via drawtext filter per timed entry → final.mp4

11. **Output**:
    ```
    ./generated/reel/<slug>/
      final.mp4           # the finished reel (15s typically)
      shots/
        shot-1.mp4
        shot-2.mp4
        shot-3.mp4
      music.mp3
      script.md           # screenplay + captions + shot prompts
      manifest.json       # for --resume
      style-used.md       # video style + music style snapshot
    ```

    stdout last lines:
    ```
    Reel: ./generated/reel/<slug>/final.mp4
    Components: ./generated/reel/<slug>/{shots/, music.mp3, script.md}
    ```

## MODES

### Input

- `reel-builder --topic "<text>"` — draft script then generate
- `reel-builder --research <path>` — ingest research brief, derive script
- `reel-builder --script-file <path>` — use pre-written screenplay (see `references/shot-planning.md` for format)

### Structure

- `--shots N` — 1-5, default 3
- `--shot-duration S` — seconds per shot, default 5 (cap per-provider varies: Veo 8s, Sora 10s, Kling 8s)
- `--aspect vertical|square|horizontal` — 9:16 / 1:1 / 16:9, default vertical
- `--captions on|off` — burn timed captions via ffmpeg drawtext, default on

### Style

- `--style auto|<library-id>` — video directorial style (see `common/style-library/video/_index.md`)
- `--music-style auto|<library-id>` — music genre preset (see `common/style-library/music/_index.md`)
- `--style-mod "<override>"` — append tweak to video anchor

### Providers

- `--video-provider auto|veo-3-1|sora-2|kling-3-0|runway-gen-4|fal-video` — video API
- `--music-provider auto|suno-v5-5|stable-audio-2-5|eleven-music|lyria-3-pro` — music API
- `--video-instrumental on|off` — for music: pure instrumental (default on for reels — voiceover is out of scope v1)

### Execution

- `--execute` — actually generate (else returns plan + prompts)
- `--output <dir>` — custom output path
- `--parallelism N` — concurrent shot calls (default 2, max 4)
- `--yes` — skip cost confirmation
- `--resume` — pick up from manifest

### Inspection

- `--prompts-only` — assemble script + per-shot prompts + music prompt, save to script.md, exit
- `--cost-only` — print total estimated cost, exit
- `--check` — validate env vars + library files + ffmpeg available

### ffmpeg gating

- If ffmpeg is not detected on PATH:
  - With `--execute`: still generates shots + music, then prints the ffmpeg concat command for the user to run manually.
  - `--check`: reports the missing binary and the manual install command (brew install ffmpeg / apt-get install ffmpeg).
- `SKILLS_SKIP_FFMPEG=1`: don't attempt ffmpeg even if installed. Outputs stay separate.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/shot-planning.md](references/shot-planning.md) | Step 2 — shot count templates, timing, screenplay format, dialogue rules |
| [references/style-resolution.md](references/style-resolution.md) | Step 3 — directorial style auto-pick, `Inspired by` vs anchor, override semantics |
| [references/music-pairing.md](references/music-pairing.md) | Step 4-7 — music genre auto-pick from video style, BPM matching, instrumental rules, per-provider prompt mapping |
| [references/model-picker.md](references/model-picker.md) | Step 5 — video + music provider decision trees, capability matrix, cost preview |
| [references/ffmpeg-stitch.md](references/ffmpeg-stitch.md) | Step 10 — concat, audio mix, fade-out, burn-in caption filter syntax, ffmpeg gating |
| [references/captions.md](references/captions.md) | Caption writing — placement, line length, timing, accessibility |
| [references/troubleshoot.md](references/troubleshoot.md) | When shots fail, music doesn't match, ffmpeg errors, sync issues |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: 3-shot vertical reel from a topic with Suno music (Veo 3.1 + Suno v5.5), 1-shot atmospheric reel with Stable Audio (Sora 2 + Stable Audio), 4-shot product reel from research brief with Kling 3.0 + Lyria 3 Pro.

## CONSTRAINTS

- **One video provider for all shots.** Mixing Veo / Sora / Kling across shots breaks the look. Lock per-reel.

- **One music track per reel.** Not one per shot. The music plays under the whole sequence.

- **Music duration ≥ total video duration.** ffmpeg `-shortest` clips music to video length, so generate music a bit longer than reel. Default: reel_duration + 2s of music.

- **No voiceover / TTS in v1.** If the user asks "narrate this", suggest pasting voiceover separately via ElevenLabs TTS UI + manual mix. Voiceover orchestration with ducking is v2.4.0+.

- **Hard cuts only.** ffmpeg concat does straight cuts. No dissolves / wipes / fancy transitions.

- **First 1-2 seconds carry the hook.** Reel feeds scroll fast — if the opening doesn't land, audience leaves. The shot-planning reference enforces this in script structure.

- **9:16 vertical is the default.** 95%+ of reels are vertical. Override with `--aspect square|horizontal` only when targeting non-vertical platforms.

- **ffmpeg failure → graceful**: if ffmpeg fails (codec mismatch, exotic edge case), save shots + music separately and print the manual ffmpeg command. Don't lose the work.

- **Cost confirm ONCE per reel.** Sum across shots + music. Total typically $2-5; default budget cap is $4.00.

- **Captions stay under 8 words per line.** Mobile reading speed = ~3 words/sec. Don't stuff a paragraph into 5 seconds.

- **Never print API keys.** Mask in errors.

- **Output dir is `./generated/reel/<slug>/`** by default. Slug from topic, max 40 chars, kebab-case.

- **`--prompts-only` is the safety dry-run.** Each reel is $2-5 — always run `--prompts-only` first if iterating on script/style.

- **Manifest updates after every async completion.** `--resume` picks up succeeded shots / music; only re-runs failed components.

- **--resume cannot resume mid-ffmpeg.** ffmpeg stitch is final step. If stitch fails, components are saved; user re-runs `--resume` which will re-do only the ffmpeg part.

- **Style library is source of truth.** Don't write free-form directorial descriptions in this skill. If `--style auto` and library is thin for the genre, suggest a closest fit + `--style-mod "<override>"`.

## INVOCATION HINTS

When the user says any of:
- "reel about / on X", "Instagram reel", "TikTok video", "YouTube short"
- "short video on Y", "15-second video", "30-second video"
- "make a TikTok / reel / shorts about Z"
- "vertical video on Q"

RU triggers:
- «рил про X», «короткое видео про Y»
- «TikTok / Reels / Shorts про Z»
- «15-секундное видео», «30-секундный рил»
- «вертикальное видео про Q»

Defaults: `--shots 3 --shot-duration 5 --aspect vertical --captions on --video-provider auto --music-provider auto --video-instrumental on`. Without `--execute`, returns plan + prompts; with `--execute`, generates the MP4.

This skill is downstream of `research-brief` and is the most expensive in the collection — always recommend `--prompts-only` for first iteration. If the user only needs ONE shot (not a stitched reel), suggest `video-prompt --execute` instead — saves the orchestration overhead.
