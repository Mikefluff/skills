# Audio-tier models

Models with native synchronized audio (dialogue + SFX + ambient) generated in one pass — no separate audio post. Beat 1/2/3 still applies. Audio-bearing examples (Veo 3.1, Sora 2, LTX-2, Kling 3.0 Omni) include a Dialogue / SFX / Ambient block. Seedance 2.0 lives in this file because it's the visual-multi-shot peer in this tier; its audio support is unconfirmed and its example omits the audio block by design.

---

# Veo 3.1 (Google)

**Strengths**: native synchronized audio (dialogue + SFX + ambience) in a single pass, 4K, ~120ms lip-sync accuracy, scene-extend, reference-image conditioning, T2V + I2V.
**Weaknesses**: shorter base clip than open-source rivals; premium pricing on full tier.
**Execute via**: `--execute --model veo-3-1` / `veo-3-1-fast` (env: `GEMINI_API_KEY`) — Gemini / Vertex AI API.

Released Oct 2025. 4K rolled out Jan 2026. Pricing (May 2026, Vertex / Gemini API): Veo 3.1 Standard ~$0.40/sec, Veo 3.1 Fast ~$0.15/sec, Veo 3.1 Light ~$0.05/sec. Max native clip = **8s** (4s / 6s / 8s options); Scene Extend chains in 7-second hops, up to 20 hops, total ≤148s. Sources: [veo3gen pricing](https://www.veo3gen.app/blog/veo-3-1-pricing-plans), [aifreeapi extend guide](https://www.aifreeapi.com/en/posts/veo-3-extend-video-length).

## Format rules (mandatory)

- Beat 1/2/3 inside the visual block.
- Audio split into THREE labelled lines: `Dialogue:`, `SFX:`, `Ambient:`. Lip-sync targets the Dialogue line.
- One camera direction line.
- Scene-extend: write the next 8s as a fresh Beat 1/2/3, reference the prior clip explicitly.

## Veo 3.1 template

```
Beat 1: {character A action — body parts, repeated motion}
Beat 2: {character B reaction + escalation, mouth shaping if speaking}
Beat 3: {resolution — final pose, breath, micro-gesture}

Dialogue:
  Character A: "{exact line}"
  Character B: "{exact line}"
SFX: {1-3 named sounds with timing}
Ambient: {room tone / location bed}

Lighting: {named sources with direction}
Camera: {one exact term}
```

## Example (Veo 3.1)

```
Beat 1: She raises a wine glass slowly across the candle-lit dinner table, fingers tightening around the stem, gaze locking on him; he sets his fork down, jaw clenching.
Beat 2: She begins speaking — mouth shaping words continuously, lips moving on each syllable, eyes narrowing; he holds still, throat working in one visible swallow, fingers pressing into his napkin.
Beat 3: She sets the glass down with a soft clink, hand staying on the stem; his hand stays gripping the napkin, knuckles white, breath held.

Dialogue:
  Her: "You knew. You knew the whole time."
  Him: "It wasn't like that."
SFX: glass clink at end of Beat 3; quiet fork-on-plate tap mid-Beat 1.
Ambient: low restaurant murmur, distant piano, faint cutlery clatter from neighbouring tables.

Lighting: warm tungsten table-candle from below illuminating both faces, dim pendant overhead, condensation glinting on the wine glass.
Camera: slow dolly push-in across the table, focus locked on her hand on the stem.
```

## Notes

- Veo 3.1 Fast: same parser, less detail, ~$0.15/sec — use for iteration, switch to full tier for final.
- Dialogue lines longer than ~6 seconds drift in lip-sync; split across Beat 2 + Beat 3.
- Reference images: attach as `subject_reference` for identity, `style_reference` for look.
- Scene-extend chains in 7-second hops up to 20 times — total ≤148s, all from a Veo-generated source, 720p only, 9:16 or 16:9.
- **Timestamp prompting** (official Veo 3.1 recipe for multi-shot inside one 8s clip): assign actions to `[00:00-00:02]`, `[00:02-00:04]`, `[00:04-00:06]`, `[00:06-00:08]` blocks. Each block can carry its own framing + SFX + emotion line. Source: [Google Cloud Veo 3.1 prompting guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1).
- **First-and-Last-Frame workflow**: generate both frames with Gemini 2.5 Flash Image, then describe the transition in the Veo prompt. Better than asking Veo to invent endpoints.
- **Ingredients-to-Video**: attach character + setting reference images, then write the prompt as a director's note referring to them ("Using the provided images for the detective...").
- **Negative-prompt anti-pattern (official)**: avoid blanket negations like "no man-made structures". Restate positively — "a desolate landscape with no buildings or roads" works better.

---

# Sora 2 / Sora 2 Pro (OpenAI)

**Strengths**: synchronized audio + dialogue, multi-shot inside one prompt, Cameos (consented identity insertion), strong physics.
**Weaknesses**: less granular camera control than Kling; default toward "cinematic" unless specified.
**Execute via**: `--execute --model sora-2` / `sora-2-pro` (env: `OPENAI_API_KEY` + `OPENAI_SORA_API_ENABLED=1`) — OpenAI Sora API.

Pricing (May 2026): **Sora 2 base ~$0.10/sec @ 720p**; **Sora 2 Pro ~$0.30/sec @ 720p, ~$0.50/sec @ 1024p** (note: earlier ~$0.75/sec figure was a launch ceiling that has dropped). Max native clip: **Sora 2 base = 4s / 8s / 12s** options; **Sora 2 Pro = 10s / 15s / 25s** options (25s is the current ceiling). Resolution caps at **1080p** — no native 4K. Sources: [aifreeapi Sora 2 pricing](https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas), [yingtu 4K guide](https://yingtu.ai/en/blog/can-sora-2-generate-4k-videos), [help.apiyi.com Pro vs standard](https://help.apiyi.com/en/sora-2-pro-vs-standard-comparison-en.html).

## Format rules

- Natural-language paragraph as a director's note — Sora 2 parses prose.
- Audio block follows the same Dialogue / SFX / Ambient split.
- Multi-shot uses explicit cues: `new shot:` or `cut to:` — Sora 2 is one of the few that renders this correctly.
- Cameos: reference the consented identity by registered label.

## Sora 2 template

```
{One paragraph: characters, location, beat 1 → beat 2 → beat 3 embedded as continuous prose with body-part detail.}

[new shot: {transition + next beat block if multi-shot}]

Dialogue:
  Character A: "{line}"
  Character B: "{line}"
SFX: {sounds + timing}
Ambient: {bed}

Lighting: {named sources}
Camera: {term or movement}
```

## Example (Sora 2)

```
A woman in her thirties sits across from a man at a candle-lit dinner table. She raises a wine glass slowly, fingers tightening around the stem, her gaze locked on his face as she leans forward. She begins speaking — mouth shaping words continuously, jaw tense, eyes narrowing — while he holds still, throat working in a single visible swallow, his fingers tightening on his napkin. As her words land, she sets the glass down with a soft clink, hand staying on the stem; his hand stays gripping the napkin, knuckles white.

Dialogue:
  Her: "You knew. You knew the whole time."
  Him: "It wasn't like that."
SFX: glass clink at the end; faint cutlery tap mid-scene.
Ambient: low restaurant murmur, distant piano, neighbouring-table cutlery.

Lighting: warm tungsten candle from below illuminating both faces; a single pendant lamp casts dim ambient from above; condensation glints on the wine glass.
Camera: slow dolly push-in across the table, subtle handheld vibration, sharp focus on her hand on the stem.
```

## Notes

- Sora 2 is the only major closed model that reliably handles `new shot:` inside a single prompt — use for short scenes that would otherwise need editing.
- Cameos require pre-registered consent; do not invoke unregistered identities.
- For best physics: name the contact (`glass meets table`, `napkin compresses under fingers`) — Sora 2 picks up tactile prose.
- Sora 2 Pro: same parser, higher resolution + longer attention.
- **Stitch two 4s shots, don't generate one 8s** — official cookbook advice. Shorter clips have measurably higher physics + identity fidelity.
- **One camera move + one subject action per shot.** Stacking ("she walks AND turns AND speaks") is the #1 failure mode per the cookbook.
- **Treat prompts as a wish list, not a contract** — identical prompts intentionally yield different results across runs; iterate, don't fight the seed.
- **Official structured template** (from the OpenAI Cookbook): split prose, cinematography, actions, dialogue:
  ```
  [Prose scene description]

  Cinematography:
    Camera shot: {framing + angle}
    Mood: {tone}

  Actions:
    - {action 1: specific beat}
    - {action 2: distinct beat}

  Dialogue:
    {brief natural lines}
  ```
- **Character API**: upload 2-4s reference videos (720p-1080p, 16:9 or 9:16) to register a character. Reference by name in the prompt; ≤2 characters per generation.
- **API params are NOT in prose** — set `model` (`sora-2` / `sora-2-pro`), `size`, `seconds` ("4" / "8" / "12" / "16" / "20"), `characters` explicitly via API. Don't ask for them in the prompt body.
- **Style anchoring early** ("1970s film, 16mm black-and-white") frames all downstream choices — put aesthetic in the first sentence.
- Source: [OpenAI Cookbook — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide).

---

# LTX-2 / LTX-2 Distilled (Lightricks — open-source)

**Strengths**: first open-weights model with native 4K + synchronized audio, 20s clips at 50fps. Distilled variant: **practical floor ~12GB VRAM** (RTX 3060 12GB / 4070 — short clips at 512-640px), **24GB sweet spot** (RTX 3090 / 4090 — 720p comfortable, ~90s render per clip on a 4090), **8GB absolute minimum** with reduced resolution + frame count. Sources: [crepal.ai VRAM guide](https://crepal.ai/blog/aivideo/blog-ltx-2-vram-requirements/), [wavespeed VRAM reality check](https://wavespeed.ai/blog/posts/blog-ltx-2-vram-requirements/).
**Weaknesses**: newer ecosystem, fewer tutorials; identity drift on longer clips.
**Execute via**: prompt-only — open weights, self-host. Workaround: `--execute --model fal-video --fal-model fal-ai/ltx-2` (env: `FAL_KEY`).

## Format rules

- Natural-language paragraph + explicit audio block.
- Audio: `Dialogue:`, `SFX:`, `Ambient:` lines accepted same as Veo/Sora.
- 20s clips: structure as Beat 1 (0-7s) / Beat 2 (7-14s) / Beat 3 (14-20s).

## LTX-2 template

```
Beat 1 [0-7s]: {character action — body parts, repeated}
Beat 2 [7-14s]: {escalation + reaction}
Beat 3 [14-20s]: {resolution}

Dialogue:
  Character A: "{line}"
  Character B: "{line}"
SFX: {named sounds with timing}
Ambient: {bed}

Lighting: {named sources}
Camera: {one term}
```

## Example (LTX-2)

```
Beat 1 [0-7s]: She raises a wine glass slowly across the candle-lit dinner table, fingers tightening around the stem, gaze locking on him; he sets his fork down, jaw clenching once.
Beat 2 [7-14s]: She begins speaking — mouth shaping words continuously, jaw moving on each syllable, eyes narrowing; he holds still, throat working in one swallow, his hand gripping the napkin, knuckles whitening.
Beat 3 [14-20s]: She sets the glass down with a soft clink, hand staying on the stem; his hand stays clenched, breath held, candle flame flickering between them.

Dialogue:
  Her: "You knew. You knew the whole time."
  Him: "It wasn't like that."
SFX: glass clink at the end of Beat 3; quiet fork tap mid-Beat 1.
Ambient: low restaurant murmur, distant piano, faint cutlery from neighbouring tables.

Lighting: warm tungsten candle from below illuminating both faces, dim pendant overhead, condensation glinting on the glass.
Camera: slow dolly push-in across the table, focus locked on her hand on the stem.
```

## Notes

- LTX-2 Distilled: same prompt format, lower fidelity, runs on a single consumer GPU. Use for iteration.
- Open-weights — safe for on-prem / regulated workflows.
- 50fps output: native slow-motion conform without retiming.
- For identity stability past 20s: chain two clips and use a still from the last frame as reference.

---

# Kling 3.0 Omni (Kuaishou)

**Strengths**: native synchronized audio (added in 3.0 Omni), 4K @ 60fps, up to 15s clips, AI Director multi-shot (up to 6 shots in one 15s generation), multi-speaker dialogue via `<<<voice_1>>>` syntax, EN / CN / JP / KR / ES dialogue, cheapest premium tier (~$0.10/sec).
**Weaknesses**: temporal flow REQUIRED (no flexibility on time markers); rejects vague camera direction. See full I2V grammar in [`i2v-tier.md`](i2v-tier.md) — this section covers ONLY the audio + multi-shot additions.
**Execute via**: `--execute --model kling-3` (env: `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET`) — Kuaishou Kling API.

## Format rules (audio)

- Temporal flow: `First [0-2s]: ... Then [2-5s]: ... Finally [5-Xs]: ...` — see [`i2v-tier.md`](i2v-tier.md).
- Multi-speaker dialogue uses `<<<voice_1>>>` / `<<<voice_2>>>` tags: `Character <<<voice_1>>> said, "{line}"`.
- Single-speaker dialogue: same `Character: "{line}"` form as Veo / Sora.
- SFX + Ambient blocks accepted same as Veo / Sora.
- Director mode (Auto vs Custom) — Auto plans shots, Custom takes per-shot duration + framing + content blocks.

## Kling 3.0 Omni audio template

```
First [0-2s]: {character physical setup — body, breath, gaze}
Then [2-5s]: {character delivers line}
  Character <<<voice_1>>>: "{line}"
  Ambient: {one bed, low}
Finally [5-Xs]: {reaction or second speaker}
  Character <<<voice_2>>>: "{reaction line}"
  SFX: {one cue}

Lighting: {named sources}
Camera: {one named term}
```

## Example (Kling 3.0 Omni — two-speaker)

```
First [0-2s]: She raises a wine glass slowly across the candle-lit table, fingers tightening around the stem, gaze locking on him; her shoulders settle, breath in.
Then [2-6s]: She delivers the line, jaw moving evenly, no hesitation.
  Character <<<voice_1>>>: "I'm not coming home tonight. Or any night after."
  Ambient: low restaurant murmur, distant clink of cutlery.
Finally [6-10s]: He freezes for one beat, lips parting; throat works in one swallow; his hand reaches halfway across the table and stops.
  Character <<<voice_2>>>: "You don't mean that."
  SFX: muted glass clink from a neighboring table at the end.

Lighting: warm tungsten candle from below, dim ambient pendant overhead, condensation glinting on the wine glass.
Camera: static medium two-shot held throughout, subtle handheld vibration, focus on the gap between their faces.
```

## Notes / Pitfalls

- `<<<voice_1>>>` and `<<<voice_2>>>` map to whichever speakers Kling detects on the visible face track — order matters; first detected face = voice_1.
- Director Custom-mode multi-shot: each shot block can carry its own Dialogue + SFX + Ambient. Combined shot total stays ≤15s.
- Source: [kling.ai blog — Omni native lip-sync + audio guide](https://kling.ai/blog/kling-video-3-omni-native-lip-sync-audio-guide).

---

# Seedance 2.0 (ByteDance)

**Strengths**: multi-shot narrative in a single prompt (up to 6 shots, 30s total); 1080p in ~41s on hosted endpoints; real-time interactive variant (Seaweed APT2); strong character consistency across shots in one generation; available via Higgsfield Cinema Studio as a backend.
**Weaknesses**: <!-- TODO: confirm Seedance 2.0 native audio status — community reports unclear --> audio support beyond ambient is inconsistent; English documentation thinner than Sora 2 / Kling.
**Execute via**: prompt-only — no native ByteDance video adapter in v2.2. Workaround: `--execute --model fal-video --fal-model fal-ai/bytedance/seedance-1-0-pro` (env: `FAL_KEY`) if mirror available.

## Format rules

- Multi-shot block format: `Shot 1 (Xs, <framing>): <action> / Shot 2 (Ys, <framing>): <action>` — see [`multi-shot.md`](../multi-shot.md).
- Style anchor sentence at the END applies across all shots — lighting, grade, identity.
- Identity labels (`[ref:Name]`) for consistent characters across shots.
- Audio: where supported, follow Veo / Sora syntax — `Character: "{line}"`, `SFX:`, `Ambient:`.

## Seedance 2.0 template

```
Shot 1 ({duration}, {framing}): {action beat, body specific}
Shot 2 ({duration}, {framing}): {action beat}
Shot 3 ({duration}, {framing}): {resolution}

Style anchor: {one shared sentence — lighting, grade, identity binding}
Camera: {one named term applied across}
```

## Example (Seedance 2.0 — three-shot scene)

```
Shot 1 (4s, wide establishing): A candle-lit dinner table seen from across the room; the warm pendant lamp above casting a pool of light on the scene; both figures visible — [ref:Sarah] sits camera-left, [ref:Marcus] camera-right; the room around them in soft darkness.
Shot 2 (5s, extreme close-up on hands): [ref:Sarah]'s right hand wraps slowly around the stem of a wine glass; her thumb traces the curve once; [ref:Marcus]'s hand enters frame from the right, fingers tightening on his napkin.
Shot 3 (4s, medium two-shot): [ref:Sarah] lifts the wine glass to chest height, gaze locking on [ref:Marcus]; [ref:Marcus] holds eye contact, throat working in one slow swallow, jaw clenching once.

Style anchor: warm tungsten candle from below, dim ambient pendant overhead, editorial cinematic grade with shallow depth of field across all three shots.
Camera: locked compositions per shot, subtle handheld vibration only.
```

## Notes / Pitfalls

- Multi-shot total stays ≤30s in one generation; longer scenes via chained generations with style-anchor continuity.
- Style anchor is mandatory for cross-shot lighting / grade / identity consistency — without it, every shot reads as a separate scene.
- For audio-led scenes, prefer Sora 2 or Veo 3.1 until Seedance 2.0 audio support is confirmed; use Seedance 2.0 when visual multi-shot continuity is the priority.

---

## Universal audio-tier anti-patterns

- Mixing dialogue inside the visual paragraph — split it into the labelled block, lip-sync targets that line.
- Stacking >3 SFX events — model picks 1-2 and drops the rest.
- Vague ambient (`some background noise`) — name the location bed.
- Dialogue longer than ~6s in one beat — drift accumulates; split.
