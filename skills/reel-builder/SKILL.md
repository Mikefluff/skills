---
name: reel-builder
description: "Turn a topic / research brief / script into a 9:16 vertical reel: 1-4 shots + matched music + ffmpeg-stitched final.mp4 with optional burned-in captions; film mode makes a voiced film — ElevenLabs take, Seedance lip-sync to a character photo, cuts only in speech pauses, beats pinned to word timings; drama mode makes episodes of dialogue films with a recurring cast, scenes voiced by Seedance in the series' language and the speech checked by transcription. Use when: 'make a reel about X', 'short video on Y', 'TikTok / Reels / Shorts about Z', 'voiced Seedance film', 'next episode of the series', 'озвученный ролик', 'сними кино на тайском'."

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

**Film mode** is the voiced variant: an ElevenLabs take, a character who lip-syncs to it via Seedance 2.x, and a dramatic arc whose events land on the words. It has its own five-phase pipeline — see [FILM MODE](#film-mode) below.

**Drama mode** is the long form: a series bible, a director's rules, a judged cast, and episodes of 15-second scenes in which the characters speak and Seedance voices them — see [DRAMA MODE](#drama-mode).

This skill does NOT:
- Add a narrator over an ordinary reel — voice is film mode only, where the picture is cut against it
- Composite multi-track edits beyond hard cuts (no dissolves; designed transitions happen inside a generation)
- Beat-sync shots to music BPM (would need BPM detection; planned later)
- Post to platforms — that is `post-publisher`, which takes this skill's output directory (the `final.mp4`) as its input
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
   - Video: `--video-provider auto|veo-3-1|veo-3-1-fast|veo-3-1-lite|kling-3|runway-gen-4-5|fal-video`. Auto-pick by style requirements.
   - Music: `--music-provider auto|suno-v5-5|stable-audio-2-5|eleven-music|lyria-3-pro`. Auto by genre/instrumental.

6. **Build per-shot video prompts via the shared chain** — DO NOT hand-write prompts per shot. Instead, spawn ONE Agent with the canonical SYSTEM_PROMPT at [`../common/video-prompt-library/system-prompt.md`](../../common/video-prompt-library/system-prompt.md):

   - Load the SYSTEM_PROMPT verbatim from that file.
   - Fill `buildUserMessage(opts)` per the shape in the same file:
     - Mode: `i2v` (default — when carousel slides / poster frames are present) or `t2v` (script-from-scratch).
     - For i2v: pass each source frame's `image_url` + a one-line summary of the in-image overlay text per shot (the LLM uses it to choose which one motion fits the slide's rhetoric, then strips it from the output prompt).
     - For t2v: pass the screenplay beats per shot.
     - Always pass the character-identity marker (8-15 words) and the resolved video-style entry.
   - The Agent returns ONE JSON object `{"shots":[{"index":N,"prompt":"...","kwargs":{...}}]}` — all N shots in a single call. Per-shot subagent calls break identity consistency, just like in the carousel chain.
   - Append each `shots[i].prompt` + `shots[i].kwargs` to `plan.json` (single canonical path, overwrite — don't proliferate `plan-v1.json`).

   The SYSTEM_PROMPT encodes the full discipline: i2v 11 rules (2-sentence cap, 80-word cap, single motion verb, identity front-loading, global lock sentence verbatim, no rhetorical adjectives, no punitive labels, contact-motion subject-anchored not target-anchored, etc.) and the t2v cinematic template. The human-readable rationale + worked before/after examples live in the sibling `video-prompt` skill's i2v-prompting reference document (at `../video-prompt/references/`). When the two files conflict, the SYSTEM_PROMPT wins — that doc is the rationale, not the authority.

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

## FILM MODE

A voiced film, ≤30 s in one Seedance 2.5 generation (no seams) or longer in segments cut in speech pauses. Full pipeline, rationale and a worked rewrite of a real prompt in [references/film-mode.md](references/film-mode.md).

1. **Voice** — `python3 -m common.runners.cli.reel_voice --script-file vo.txt --voice-id <id> --output-dir <out> [--max-seconds 30|15] [--lead 0.8] [--tail 1.5]`. ElevenLabs TTS with timestamps (forced alignment as fallback, or `--voice-file` for an existing take) → `voice/master.wav` on the film clock, per-segment lip-sync slices, `timing.json`.
2. **Direction** — ONE Agent with [`film-system-prompt.md`](../../common/video-prompt-library/film-system-prompt.md). It sets the dramaturgy first: the controlling image, counterpoint rather than illustration, a colour arc, a quiet turn, hits pinned to word timings. It then writes 6–10 shots per 30 s, cut on action, with the camera and the subject moving in every shot, plus one keyframe prompt per shot. By default each shot is its own Seedance generation, 4–6 s long with head and tail handles, and the film is cut afterwards. Lip-sync shots get their own stretch of the master as `@Audio1`; voice-over shots open on their keyframe with the mouth closed. One generation for the whole film, in BytePlus's official 2.5 multi-shot format, is the alternative. Lines are verbatim in `{}`, either on camera or `(V.O.)` with the lips closed. The result is `plan.json` with `board`, `voiceover`, `trim_seconds` and `sound`.
3. **Storyboard** — `python3 -m common.runners.cli.reel_board --plan-file <out>/plan.json`. Nano Banana Pro renders one keyframe per shot through OpenRouter. A Gemini critic scores each against its shot (framing, light, identity, idea, craft), and frames below 8/10 are re-rolled with the critic's fix, about $0.14 a frame. The approved frames become the shot's ordered keyframe references. Look at `board/contact.jpg` before paying for video.
3b. **Previs** — `python3 -m common.runners.cli.reel_previs --plan-file <out>/plan.json`. Blender, headless and free, renders a clay blocking clip for each shot from the chain's `previs` spec: sets, camera keys including orbits and dolly zooms, hand-held shake, the hero's moves, and the moments lights fire. The clips go to Seedance as `@Video1`, which follows a previs's camera, speed and timing far more faithfully than any sentence. Watch `previs/contact.jpg` and the clips before paying for video. Blender is found through `$BLENDER`, `blender` on PATH, or `/Applications/Blender.app`.
4. **Sound** — `python3 -m common.runners.cli.reel_sound --plan-file <out>/plan.json`. The chain's `sound` block becomes Eleven Music cues plus ElevenLabs effects and beds, placed on the film clock (kills, dips and "distant" re-use are edits, not generations), ducked under the voice and mastered to −14 LUFS. The result is `soundtrack.wav`, which you can hear before paying for the picture. Seedance's own audio is never used.
5. **Render** — `python3 -m common.runners.cli.reel --plan-file <out>/plan.json`. Chained segments run in order, and each opens on the frame the previous one was cut on. The join is frame-exact, effects marked `snap` move onto the frames where the flashes really are, and the soundtrack is muxed over. If the lips drift from the take, run `python3 -m common.runners.cli.reel_conform --plan-file <out>/plan.json --picture <shot>` and then `reel --resume`.

Providers: `seedance-2-5` / `seedance-2-0` (BytePlus ModelArk, `ARK_API_KEY`), `openrouter-seedance-2-5` (`OPENROUTER_API_KEY`, BytePlus price, audio references honoured), `fal-seedance-2-5` (`FAL_KEY`). The user's brief stays theirs — the chain restructures it, it does not replace the idea.

## DRAMA MODE

A series of dialogue films: episodes of 8-12 minutes cut from 15-second Seedance 2.5 scenes, several characters speaking in the series' language, voiced by Seedance itself. The cast, places and director carry over from episode to episode. Full sequence, costs and the language check are in [references/drama-mode.md](references/drama-mode.md).

1. **Series**: ONE Agent with SERIES from [`drama-system-prompt.md`](../../common/video-prompt-library/drama-system-prompt.md) produces `<series>/bible.json` (language, look, cast with portrait prompts, places per weather and time, episode outlines). Research what gets views first with `research-brief` when the user asks for a hit in a given market.
2. **Director**: ONE Agent with DIRECTOR plus [`directors/base.md`](../../common/video-prompt-library/directors/base.md) writes `<series>/director.md`, rules that extend the base by number.
3. **Episode**: ONE Agent with EPISODE plus the merged rules (`drama.director(path)`) writes `<series>/epNN/plan.json`. Every scene carries its cast, location, dialogue in the series language, and a shot list.
4. **Cast**: `python3 -m common.runners.cli.reel_cast --plan-file <series>/ep01/plan.json` renders and judges each face and place once per series. It then gives every scene its references and composes the prompt.
5. **Render**: `python3 -m common.runners.cli.reel --plan-file <series>/ep01/plan.json` (first `--cost-only`, then one scene with `--redo sc01`). Scenes keep their own dialogue. A `music` block is ducked under it.
6. **Check**: `python3 -m common.runners.cli.reel_check --plan-file <series>/ep01/plan.json` compares each scene's transcribed speech with its script, letter by letter. It also checks faces against the portraits and catches doubles or subtitles, then prints the `--redo` line for what failed.

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

- `--video-provider auto|veo-3-1|veo-3-1-fast|veo-3-1-lite|kling-3|runway-gen-4-5|fal-video|seedance-2-5|seedance-2-0|openrouter-seedance-2-5|fal-seedance-2-5` — video API (Seedance = film mode)
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
| [references/film-mode.md](references/film-mode.md) | Voiced film — voice phase, dramaturgy rules and why, Seedance routes, seams, worked example |
| [references/drama-mode.md](references/drama-mode.md) | Series of dialogue films — bible, director, episode, cast, speech check, costs |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: 3-shot vertical reel from a topic with Suno music (Veo 3.1 + Suno v5.5), 1-shot atmospheric reel with Stable Audio (Sora 2 + Stable Audio), 4-shot product reel from research brief with Kling 3.0 + Lyria 3 Pro.

## CONSTRAINTS

- **One video provider for all shots.** Mixing Veo / Sora / Kling across shots breaks the look. Lock per-reel.

- **One music track per reel.** Not one per shot. The music plays under the whole sequence.

- **Music duration ≥ total video duration.** ffmpeg `-shortest` clips music to video length, so generate music a bit longer than reel. Default: reel_duration + 2s of music.

- **Voice means film mode.** A narrated reel is built against its take: voice phase first, prompts from `timing.json`, never prompts first and voice after.

- **In film mode the master take is the only voice.** Seedance's own audio is dropped at stitch; music, if any, is ducked under the take.

- **Hard cuts only at seams.** ffmpeg joins without dissolves; a transition the film needs is staged inside a generation (smoke whiteout, occlusion) and, when it can, placed on a seam.

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
- "make a film / series / episode", "next episode", "characters talk in Thai", "a director who shoots like …" → drama mode

RU triggers:
- «рил про X», «короткое видео про Y»
- «TikTok / Reels / Shorts про Z»
- «15-секундное видео», «30-секундный рил»
- «озвученный ролик», «ролик с озвучкой ElevenLabs», «Seedance с липсинком», «персонаж говорит в кадре» → film mode
- «вертикальное видео про Q»
- «сними кино / сериал / фильм на 10 минут», «новая серия», «на тайском / японском», «персонажи разговаривают», «режиссёр в стиле …»: это drama mode

Defaults: `--shots 3 --shot-duration 5 --aspect vertical --captions on --video-provider auto --music-provider auto --video-instrumental on`. Without `--execute`, returns plan + prompts; with `--execute`, generates the MP4.

This skill is downstream of `research-brief` and is the most expensive in the collection — always recommend `--prompts-only` for first iteration. If the user only needs ONE shot (not a stitched reel), suggest `video-prompt --execute` instead — saves the orchestration overhead.
