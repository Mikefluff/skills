---
name: video-prompt
description: "Write prompts for AI video generators (Kling, Veo, Sora, Runway, Pika, Hailuo, Luma). Character-first beat structure, exact camera vocabulary (dolly/pan/tracking/orbit/drone), pacing modes, per-model deltas. Use when the user says 'video prompt', 'animate this image', 'motion prompt for Kling', 'short-form video shot'."
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
Write a tight, model-aware motion prompt for AI video generation. Output: one structured prompt string (3-6 sentences, beat-structured), optionally + endFrameDescription. This skill does NOT call the video model — it produces the text you paste into Kling / Veo / Sora / Runway / Pika / Hailuo / Luma.

Use when the user wants a 4-10s clip from a still image (image-to-video) or from text (text-to-video). The skill applies the **CHARACTER FIRST, CAMERA SECOND** law, beat-structures the motion, picks vocabulary the target model parses cleanly, and avoids the language that produces frozen-pose output.

This skill does NOT:
- generate the video itself (that's the model)
- generate the still image (use `image-prompt`)
- write a full storyboard / multi-shot sequence (use a storyboarding tool / separate skill)
- write traditional film screenplays (use `essay-write` or `prose-edit`)
</objective>

## ROLE

Read request → identify subject + action + emotional beat → pick target model → apply CHARACTER FIRST law (action before camera) → beat-structure the motion → add camera move from exact vocabulary → return motion prompt + optional endFrame.

## PIPELINE

1. **Clarify the shot.** Need to know:
   - What is the still image (if image-to-video)? Brief description: who/what is in frame, posture, setting.
   - What action happens in the 4-10 seconds? (the model can't extrapolate "and then he leaves and comes back")
   - Emotional beat: `hook` (peak tension from frame 0), `tension`, `climax`, `breathing`, `resolution`, `setup`
   - Target model (Kling, Veo, Sora, Runway, Pika, Hailuo, Luma)
   - POV or third-person?

2. **Apply CHARACTER FIRST.** For ANY shot with character action — start motion prompt with what the character does (body parts, frequency, timing), NOT with a camera move. See `references/beat-structure.md`.

3. **Beat-structure the motion** (mandatory for action shots):
   - Beat 1 (0% → 30%): initiating action
   - Beat 2 (30% → 70%): escalation
   - Beat 3 (70% → 100%): resolution / final pose
   See `references/beat-structure.md` for templates per emotional beat.

4. **Pick camera move from exact vocabulary.** Use the named terms (`slow dolly push-in`, `orbit 180`, `whip pan`) — NOT vague "camera moves forward". See `references/camera-vocabulary.md`.

5. **Add per-model rules.**
   - Kling 3.0: temporal flow REQUIRED ("First [0-2s]: ..., then [2-4s]: ..."); name specific cinematic verbs; no transition language
   - Veo3: less rigid temporal structure, accepts natural description
   - Runway: shorter, action-focused prompts; less camera-vocabulary, more body description
   - Sora: handles narrative direction well; can describe physics
   - Pika / Hailuo / Luma: similar to Runway in structure
   See `references/model-specifics.md`.

6. **Apply pacing mode** — narrative / action / comedy / documentary / timelapse. Each has its own camera-energy rules. See `references/pacing-modes.md`.

7. **Strip forbidden phrases** that cause frozen-pose output. Replace with body-part-specific, timed, repeated actions. See `references/beat-structure.md` § Forbidden phrases.

8. **Output.**
   - The motion prompt as one fence-block (paste-ready)
   - `endFrameDescription` only if the shot ends in a DIFFERENT composition from the start (otherwise empty)
   - 1-line note: which model conventions were applied, which pacing mode

## MODES

- `video-prompt <action-description> --model kling` — generate Kling-formatted motion prompt
- `video-prompt <action> --model veo` — Veo format
- `video-prompt <action> --model runway|sora|pika|hailuo|luma` — other providers
- `video-prompt <action> --pacing action|narrative|comedy|documentary|timelapse` — apply pacing mode
- `video-prompt <action> --beat hook|tension|climax|breathing|resolution|setup` — emotional beat
- `video-prompt <action> --pov` — first-person POV variant
- `video-prompt <action> --variants 3` — 3 alternative cuts with different camera moves

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/camera-vocabulary.md](references/camera-vocabulary.md) | When picking the camera move — full DOLLY / PAN / TRACKING / CRANE / ORBIT / AERIAL / SPECIALTY dictionary with examples |
| [references/beat-structure.md](references/beat-structure.md) | Always — Beat 1/2/3 structure, CHARACTER FIRST law, repeated-action patterns, body-detail layers for emotion shots, forbidden phrases that cause frozen output |
| [references/model-specifics.md](references/model-specifics.md) | When the user names a model — per-model template, what they parse well, what they don't |
| [references/pacing-modes.md](references/pacing-modes.md) | When user specifies pacing — narrative / action / comedy / documentary / timelapse rules |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 5 calibration pairs covering hook, tension, breathing, POV, and timelapse shots.

## CONSTRAINTS

- **CHARACTER FIRST, CAMERA SECOND.** Never start a motion prompt with a camera move when characters are in action. Camera is one supporting sentence at the end.
- **Beat structure mandatory.** Every shot with action gets Beat 1 / Beat 2 / Beat 3 timing. This is the single biggest defense against the "model freezes one pose" failure mode.
- **Repeated, not single.** "He extends his arm" produces a frozen statue. "He delivers 3-4 sharp jabbing motions, arm never fully returning to rest" produces video.
- **Two characters → describe both separately.** "They look at each other" → synchronised statues. Describe character A AND character B's reactions in EACH beat.
- **Use exact camera vocabulary.** "Slow dolly push-in" not "camera moves forward". "Orbit 180" not "camera goes around". The model is trained on the specific terms.
- **No transition language.** "Cut to", "fade to", "reveal" are EDIT terms, not motion terms. The model can't render them inside one shot.
- **Physical realism.** If the still shows a kiteboard, describe kite-line tension and edge angles, not generic "rides the wave". Match motion physics to the equipment.
- **Props stay.** A laptop on the desk doesn't teleport. Specify "laptop screen glow continuous", "cup stays in hand", etc.
- **No naming text overlays.** If the still has a title card, the model already sees it — just say "title overlay fades in", don't quote the text.

## INVOCATION HINTS

When the user says any of:
- "video prompt for {model}", "Kling / Veo / Sora / Runway / Pika prompt"
- "motion prompt for this image"
- "animate this still"
- "image-to-video prompt"
- "4-second clip of {action}"
- "shot for TikTok / Reels / Shorts"

RU triggers (use the skill when the user writes any of):
- «промпт для Kling / Veo / Sora / Runway / Pika / Hailuo / Luma»
- «оживи картинку / оживи это фото»
- «motion-промпт для Reels / Shorts / TikTok»
- «image-to-video промпт»
- «4 секунды клипа с {действие}»
- «сделай видео из этой картинки»

Sam prompt body is still best written in English (the video models parse EN much better than RU). The RU → EN camera-vocabulary mapping lives in [`references/camera-vocabulary.md`](references/camera-vocabulary.md) (section `RU термины`).

Use this skill. For static image — `image-prompt`. For full storyboard — neither (use a dedicated tool).
