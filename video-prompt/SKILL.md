---
name: video-prompt
description: "Write prompts for 20+ frontier AI video generators (Veo 3.1 + native audio, Sora 2 + cameos, Kling 3.0 / Elements, Runway Gen-4 / Aleph V2V / Act-One, Luma Ray 3 / Modify, Pika 2.2 / Pikaframes, Hailuo 02, Higgsfield, LTX-2, HunyuanCustom, Wan 2.2, Seedance). Modes: T2V / I2V / V2V / extend / multi-shot / dialogue+audio. CHARACTER FIRST law, beat structure, exact camera vocabulary, identity-reference grammar, pacing modes. Use when the user says 'video prompt', 'animate this image', 'Kling/Veo/Sora/Runway prompt', 'dialogue scene with audio', 'edit this clip', 'character consistency across shots'."
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
Write a tight, model-aware motion prompt for AI video generation. Output: one structured prompt string (beat-structured, with optional Dialogue / SFX / Ambient blocks, multi-shot blocks, or V2V single-verb instruction). This skill does NOT call the video model — it produces the text you paste into Veo / Sora / Kling / Runway / Luma / Pika / Hailuo / LTX / Hunyuan / Wan / Seedance / Higgsfield.

Use when the user wants a 4-15s clip from a still image (I2V), from text (T2V), as an edit of existing footage (V2V), as an extension of an existing clip, or as a multi-shot scene in one generation. Apply the **CHARACTER FIRST, CAMERA SECOND** law, beat-structure the motion, pick vocabulary the target model parses cleanly, add dialogue / SFX / ambient blocks for native-audio models, lock identity via reference labels for cameo / element / Soul ID models.

This skill does NOT:
- generate the video itself (that's the model)
- generate the still image (use `image-prompt`)
- write a full multi-scene storyboard (use a storyboarding tool / separate skill)
- write traditional film screenplays (use `essay-write` or `prose-edit`)
</objective>

## ROLE

Read request → identify subject + action + emotional beat → pick mode (T2V / I2V / V2V / extend / multi-shot) → pick target model from `references/models/_index.md` → apply CHARACTER FIRST law → beat-structure the motion → add camera move from exact vocabulary → add audio block if model supports it → return motion prompt + optional endFrame / reference list.

## PIPELINE

1. **Clarify the shot.** Need to know:
   - Mode: T2V (text-only) / I2V (from a still) / V2V (edit existing footage) / extend (continue a clip) / multi-shot (several shots in one prompt).
   - What action happens in the 4-15 seconds? (the model can't extrapolate offscreen).
   - Emotional beat: `hook` / `tension` / `climax` / `breathing` / `resolution` / `setup`.
   - Target model (default by mode — see `references/models/_index.md`).
   - Dialogue or sound design? (only if model supports native audio: Veo 3.1, Sora 2, LTX-2).
   - POV or third-person?
   - Identity references attached? (cameos / elements / Soul ID).

2. **Apply CHARACTER FIRST.** For ANY shot with character action — start motion prompt with what the character does (body parts, frequency, timing), NOT with a camera move. See `references/beat-structure.md`.

3. **Beat-structure the motion** (mandatory for action shots):
   - Beat 1 (0% → 30%): initiating action / setup
   - Beat 2 (30% → 70%): escalation / dialogue delivery
   - Beat 3 (70% → 100%): resolution / reaction / final pose
   See `references/beat-structure.md` for templates per emotional beat AND per dialogue-bearing model.

4. **Pick camera move from exact vocabulary.** Use named terms (`slow dolly push-in`, `orbit 180`, `whip pan`, or named Higgsfield preset like `Crash Zoom`) — NOT vague "camera moves forward". See `references/camera-vocabulary.md`.

5. **Mode-specific rules.**
   - **T2V**: 6-part build with full scene description.
   - **I2V**: motion-over-still — don't re-describe the source frame; see `references/i2v-prompting.md`.
   - **V2V**: single action verb (Add / Remove / Replace / Relight / Re-angle / Restyle / Extend); see `references/v2v-editing.md`.
   - **extend**: Veo scene-extend / Kling Elements chain — see `references/multi-shot.md`.
   - **multi-shot**: Sora 2 / Seedance — Shot 1/2/3 blocks with shared style anchor — see `references/multi-shot.md`.

6. **Add audio block** if model supports native audio (Veo 3.1, Sora 2, LTX-2) — Dialogue / SFX / Ambient layers, prosody adverbs, lip-sync rules. See `references/audio-prompting.md`. ≤5 total audio elements per 8s clip.

7. **Add per-model rules** from `references/models/<tier>.md`:
   - Kling 3.0 / Elements: temporal flow required, 4 refs for Elements
   - Veo 3.1: more flexible structure; audio + lip-sync triggered by `Character: "line"` syntax
   - Sora 2: NL paragraph + audio + multi-shot transitions (`new shot:`, `cut to:`, `match cut on`)
   - Runway Gen-4 / Aleph: short clips; Aleph = single-verb V2V edit, 5s cap
   - Higgsfield: named camera presets, max 3 stacked; Soul ID for character lock

8. **Identity references** (if cameos / elements / Soul ID / HunyuanCustom):
   - Name the reference: `[ref:Sarah]`, `[ref:Marcus]`
   - Do NOT re-describe locked physical traits (hair, face, body)
   - See `references/identity-references.md`.

9. **Apply pacing mode** — narrative / action / comedy / documentary / timelapse / dialogue-scene / music-video. See `references/pacing-modes.md`.

10. **Strip forbidden phrases** that cause frozen-pose output. Replace with body-part-specific, timed, repeated actions. See `references/beat-structure.md` § Forbidden phrases.

11. **Output.**
    - The motion prompt as one fence-block (paste-ready), with Dialogue / SFX / Ambient blocks inline if audio mode
    - `endFrameDescription` only if shot ends in a DIFFERENT composition from start
    - For multi-shot: each shot block fenced separately or in one block
    - For V2V: just the single-verb instruction
    - 1-line note: model + mode + key conventions + pacing mode

## MODES

- `video-prompt <action> --model <name>` — generate model-specific prompt. Valid: `veo-3-1`, `veo-3-1-fast`, `sora-2`, `sora-2-pro`, `kling-3`, `kling-master`, `kling-elements`, `runway-gen-4`, `runway-gen-4-turbo`, `runway-aleph`, `runway-act-one`, `hailuo-02`, `hailuo-02-pro`, `pika-2-2`, `ray-3`, `ray-3-modify`, `ltx-2`, `hunyuan-1-5`, `hunyuan-custom`, `wan-2-2`, `seedance-1-pro`, `higgsfield`
- `video-prompt <action> --mode t2v|i2v|v2v|extend` — pick mode explicitly; routes to the right reference
- `video-prompt <action> --audio` — append Dialogue / SFX / Ambient blocks (default ON for Veo 3.1 / Sora 2 / LTX-2)
- `video-prompt <action> --dialogue "<line>"` or `--dialogue file:<path>` — explicit dialogue input; auto-formats with `Character: "..."` syntax
- `video-prompt <action> --end-frame "<description>"` — keyframe block for Kling tail / Pikaframes / Ray3 Start+End / Higgsfield
- `video-prompt <action> --shots N` — multi-shot Sora 2 / Seedance layout
- `video-prompt <action> --ref <name>=<path>[,<name>=<path>...]` — identity reference labels
- `video-prompt <action> --cluster audio|i2v|v2v|open|aggregator` — pick by capability when no model named
- `video-prompt <action> --pacing narrative|action|comedy|documentary|timelapse|dialogue-scene|music-video`
- `video-prompt <action> --beat hook|tension|climax|breathing|resolution|setup`
- `video-prompt <action> --pov` — first-person POV variant
- `video-prompt <action> --variants 3` — 3 alternatives with different camera moves or pacing

Deprecated aliases (accepted with warning): `kling-1-6`, `kling-2`, `pika-1-5`, `pika-2-0`, `gen-3`, `gen-3-turbo`, `veo-3`, `sora`, `luma-dream`.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/models/_index.md](references/models/_index.md) | Always at step 1 — quick-pick decision table, capability matrix, deprecations |
| [references/camera-vocabulary.md](references/camera-vocabulary.md) | Picking camera move — DOLLY / PAN / TRACKING / CRANE / ORBIT / AERIAL / Higgsfield presets / Sora 2 multi-shot transitions / Cinema Studio lens vocab |
| [references/beat-structure.md](references/beat-structure.md) | Always — Beat 1/2/3, CHARACTER FIRST, repeated-action patterns, body detail, forbidden phrases, dialogue-bearing beat structure |
| [references/pacing-modes.md](references/pacing-modes.md) | When user specifies pacing — narrative / action / comedy / documentary / timelapse / dialogue-scene / music-video |
| [references/audio-prompting.md](references/audio-prompting.md) | Native-audio models — Dialogue / SFX / Ambient grammar, prosody, lip-sync rules, talking-head template |
| [references/i2v-prompting.md](references/i2v-prompting.md) | Mode `i2v` — motion-over-still rules, physical tethers, never-re-describe |
| [references/v2v-editing.md](references/v2v-editing.md) | Mode `v2v` — action-verb-first grammar, single-change-per-pass, per-model duration caps |
| [references/multi-shot.md](references/multi-shot.md) | Mode `multi-shot` or `extend` — Shot 1/2/3 blocks, style anchors, transitions |
| [references/identity-references.md](references/identity-references.md) | When `--ref` attached — cameo / element / Soul ID / Act-One grammar |
| [references/models/audio-tier.md](references/models/audio-tier.md) | Veo 3.1 / Sora 2 / LTX-2 — per-model audio templates |
| [references/models/i2v-tier.md](references/models/i2v-tier.md) | Kling / Hailuo / Runway Gen-4 / Pika — per-model I2V templates |
| [references/models/v2v-tier.md](references/models/v2v-tier.md) | Aleph / Act-One / Ray 3 Modify / Pika swaps-additions-frames |
| [references/models/open-source.md](references/models/open-source.md) | LTX-2 / Hunyuan 1.5 + Custom / Wan 2.2 / Mochi 1 |
| [references/models/aggregators.md](references/models/aggregators.md) | Higgsfield — Cinema Studio presets, Soul ID, Start+End frames |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — calibration pairs covering hook / tension / breathing / POV / timelapse + dialogue (Veo 3.1) / I2V (Kling) / V2V (Aleph) / multi-shot (Sora 2) / RU audio.

## CONSTRAINTS

- **CHARACTER FIRST, CAMERA SECOND.** Never start a motion prompt with a camera move when characters are in action. Camera is one supporting sentence at the end.
- **Beat structure mandatory.** Every shot with action gets Beat 1 / Beat 2 / Beat 3 timing. Single biggest defense against the "model freezes one pose" failure mode.
- **Repeated, not single.** "He extends his arm" → frozen statue. "He delivers 3-4 sharp jabbing motions, arm never fully returning to rest" → video.
- **Two characters → describe both separately** within each beat. "They look at each other" → synchronised statues.
- **Use exact camera vocabulary** — "Slow dolly push-in" not "camera moves forward". Or named Higgsfield preset (`Crash Zoom`, `Bullet Time`).
- **No transition language inside one shot.** "Cut to", "fade to", "reveal" are EDIT terms. Only `new shot:` / `cut to:` / `match cut on` work in Sora 2 multi-shot — and only as explicit multi-shot blocks.
- **Dialogue obeys beat budget.** ≤8s speech per 8s clip. One speaker per beat. Prosody adverbs BEFORE the quote, not inside (no ellipsis-acting).
- **No competing SFX during dialogue.** Drop ambient under the line; layer SFX into setup or reaction beats, not on top of speech.
- **Face must be visible for lip-sync.** Cutting away during a line breaks sync.
- **V2V: one action verb per generation.** Stack edits by chaining multiple passes. Single-pass multi-edit produces unstable results.
- **I2V: don't re-describe the source frame.** The model already sees it. Describe only motion + tethers.
- **Identity refs: don't re-describe locked traits.** Wardrobe / action / expression / environment change; hair / face / body type are locked by the ref.
- **Physical realism.** A kiteboard → describe kite-line tension and edge angles, not generic "rides the wave".
- **Props stay.** Objects in frame don't teleport. Specify "cup stays in hand", "laptop screen glow continuous".

## INVOCATION HINTS

When the user says any of:
- "video prompt for {model}", "Veo / Sora / Kling / Runway / Pika / Hailuo / Luma / LTX / Hunyuan / Wan / Seedance / Higgsfield prompt"
- "motion prompt for this image", "animate this still", "image-to-video"
- "edit this clip", "V2V", "Aleph prompt", "Ray3 Modify", "Pikaswaps"
- "dialogue scene", "talking-head", "two characters arguing", "lip-sync"
- "multi-shot in one prompt", "Sora 2 multi-shot", "extend this scene"
- "character consistency across shots", "cameo", "Soul ID", "Act-One performance"
- "4-15 second clip of {action}"
- "shot for TikTok / Reels / Shorts"
- "music video shot", "beat-synced"

RU triggers:
- «промпт для Veo / Sora / Kling / Runway / Pika / Hailuo / Luma / LTX / Hunyuan / Wan / Seedance / Higgsfield»
- «оживи картинку / оживи это фото», «motion-промпт»
- «отредактируй клип», «V2V», «измени освещение на закат на этом видео»
- «диалоговая сцена», «говорящая голова», «двое спорят», «lip-sync»
- «multi-shot за один промпт», «3 кадра подряд», «расширь сцену»
- «единый персонаж на всех клипах», «cameo», «Soul ID»
- «motion-промпт для Reels / Shorts / TikTok»
- «4 секунды клипа с {действие}»
- «клип под музыку», «beat-synced»

Prompt body is usually written in English (video models parse EN much better than RU). RU dialogue lines can pass verbatim inside `Character: "..."` quotes (Veo 3.1 handles multilingual speech). RU → EN camera-vocabulary mapping lives in [`references/camera-vocabulary.md`](references/camera-vocabulary.md) (section `RU термины`).

Use this skill. For static image — `image-prompt`. For full storyboard — neither (use a dedicated tool).
