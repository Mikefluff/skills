# Open-weights / self-host models

Models you can run on your own hardware. Trade quality and convenience for control, privacy, and per-clip cost approaching zero. LTX-2 audio + 4K is covered in `audio-tier.md`; this file focuses on self-host operation.

---

# LTX-2 / LTX-2 Distilled (Lightricks)

**Strengths**: first open-weights with native 4K + synchronized audio, 20s clips at 50fps.
**Weaknesses**: heavyweight VRAM for full tier; Distilled trades fidelity for consumer GPU support.

## Hardware

- LTX-2 full: data-center GPU (A100 / H100 80GB class). Direct 4K@50fps is only feasible in short bursts on consumer-class cards even at 24GB — OOM and time costs spike fast.
- LTX-2 Distilled: **practical floor ~12GB VRAM** (RTX 3060 12GB / 4070 — short 512-640px clips), **24GB sweet spot** (RTX 3090 / 4090 / 5090 — 720p comfortable, ~90s for a short clip on a 4090, ~7 min on a 3060 12GB). Distilled saves ~30-40% VRAM vs full at same resolution/frame count. Use fp16/bf16 half precision + attention tiling for sub-24GB cards. Sources: [docs.ltx.video system requirements](https://docs.ltx.video/open-source-model/getting-started/system-requirements), [crepal.ai VRAM guide](https://crepal.ai/blog/aivideo/blog-ltx-2-vram-requirements/), [wavespeed reality check](https://wavespeed.ai/blog/posts/blog-ltx-2-vram-requirements/).

## Format

See `audio-tier.md` for the full Dialogue / SFX / Ambient block. Self-host workflow:

```
Beat 1 [0-7s]: {action with body-part detail}
Beat 2 [7-14s]: {escalation}
Beat 3 [14-20s]: {resolution}

Dialogue / SFX / Ambient blocks.

Lighting / Camera blocks.
```

## Example (LTX-2 Distilled, self-host)

```
Beat 1 [0-7s]: She raises the wine glass slowly across the candle-lit table, fingers tightening on the stem, gaze locking on him.
Beat 2 [7-14s]: She begins speaking — mouth shaping words continuously, jaw moving; he holds still, throat working in one swallow, fingers compressing the napkin.
Beat 3 [14-20s]: She sets the glass down with a soft clink, hand stays on the stem; his hand stays clenched on the napkin.

Dialogue:
  Her: "You knew."
  Him: "It wasn't like that."
SFX: glass clink end of Beat 3; quiet fork tap mid-Beat 1.
Ambient: low restaurant murmur, distant piano.

Lighting: warm candle from below, dim pendant overhead, condensation on the glass.
Camera: slow dolly push-in across the table, focus on her hand.
```

## Notes

- Open-weights — safe for on-prem / regulated workflows.
- 50fps output conforms cleanly to slow motion without retiming.
- For identity stability past 20s: chain clips and feed the last frame as reference into the next.

---

# HunyuanVideo 1.5 (Tencent)

**Strengths**: high-quality open-weights T2V/I2V; community ecosystem (ComfyUI nodes, LoRA support).
**Weaknesses**: no native audio; identity drift past ~5s without reference conditioning.

## Hardware

**HunyuanVideo 1.5 VRAM floor: 16GB minimum with FP8 quantization (24GB recommended)**. With model offloading, can squeeze down to ~13.6GB for 720p / 121-frame output. Step-distilled 480p model runs end-to-end in ~75s on a single RTX 4090. Optimal run on A100/H100 80GB. Source: [Tencent-Hunyuan/HunyuanVideo-1.5 GitHub](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5), [spheron VRAM guide](https://www.spheron.network/blog/gpu-cloud-video-ai-2026/).

## Format

```
Beat 1: {action — body parts, repeated}
Beat 2: {escalation}
Beat 3: {resolution}

Lighting: {named sources}
Camera: {one term}
```

## Example (HunyuanVideo 1.5)

```
Beat 1: She raises the wine glass slowly, fingers tightening on the stem, gaze locking on him across the candle-lit table.
Beat 2: She begins speaking — mouth shaping words continuously, jaw moving; he holds still, throat working in a swallow.
Beat 3: She sets the glass down with a soft clink, hand stays on the stem; his hand stays gripped on the napkin.

Lighting: warm candle from below, dim pendant overhead, condensation on the glass.
Camera: slow dolly push-in across the table, focus on her hand.
```

## Notes

- Strong LoRA ecosystem — style and identity LoRAs slot cleanly.
- For audio: render silent, post-sync separately. No first-party audio extension as of May 2026; community Hunyuan-Audio forks exist but are experimental — for native audio + open weights use LTX-2 instead.

---

# HunyuanCustom (Tencent)

**Strengths**: subject-consistent generation conditioned on image / audio / video / text inputs — multi-modal identity lock.
**Weaknesses**: complexity ceiling per call; conditioning conflict if inputs disagree.

## Hardware

Inherits HunyuanVideo's footprint — **24GB VRAM minimum for the full model**, FP8 quantized builds run on 16GB; same 8GB floor as base Hunyuan exists with temporal tiling (ComfyUI ≥v0.3.10). Official VRAM table for HunyuanCustom specifically is not yet published — figures inferred from HunyuanVideo base. Source: [Tencent-Hunyuan/HunyuanCustom GitHub](https://github.com/Tencent-Hunyuan/HunyuanCustom), [spheron VRAM guide](https://www.spheron.network/blog/gpu-cloud-video-ai-2026/).

## Format

```
Identity sources:
  image: {reference image label}
  audio: {voice/performance audio if used}
  video: {motion reference if used}
  text: {character description}

Beat 1: {action}
Beat 2: {escalation}
Beat 3: {resolution}

Lighting / Camera blocks.
```

## Example (HunyuanCustom)

```
Identity sources:
  image: woman_ref_01.png (the woman, dark hair, thirties).
  text: woman in her thirties, dark hair, candle-lit dinner setting.

Beat 1: She raises the wine glass slowly, fingers tightening on the stem, gaze locking on him.
Beat 2: She begins speaking — mouth shaping words continuously, jaw moving; he holds still, throat working in a swallow.
Beat 3: She sets the glass down with a soft clink, hand stays on the stem.

Lighting: warm candle from below, dim pendant overhead.
Camera: slow dolly push-in, focus on her hand.
```

## Notes

- Audio conditioning gives lip-sync without rendering native audio — the model uses audio to drive mouth motion only.
- When image + text conflict, image wins.
- Source: github.com/Tencent-Hunyuan/HunyuanCustom.

---

# Wan 2.2 / Wan 2.7 (Alibaba)

**Strengths**: Mixture-of-Experts architecture, first-frame control, 15s clips. Wan 2.7 adds partial multi-shot.
**Weaknesses**: **no native 4K** — Wan 2.2 ceiling is 720p (480p + 720p T2V/I2V); 1080p / 4K only via upscaler (Real-ESRGAN etc.). Wan 2.7 (Apr 2026) lifts the ceiling slightly with sharper controls and adds "Thinking Mode", but native generation still tops out at 1080p — true 4K is an upscaler step. Ecosystem narrower than Hunyuan.

## Hardware

**Wan 2.2 VRAM floor: ~80GB recommended for the full A14B model** at 720p; **5B distilled variant runs 720p on as little as 8GB**. RTX 4090 (24GB) renders 81 frames @ 640×480 in ~7s/frame; 720p ~18s/frame. Wan 2.7 VRAM footprint is comparable — Alibaba has not published a dedicated table; community ComfyUI builds report similar bands. MoE routing means a single forward pass touches a subset of experts — VRAM peak is lower than parameter count suggests. Sources: [Wan-Video/Wan2.2 GitHub](https://github.com/Wan-Video/Wan2.2), [novita Wan 2.2 VRAM guide](https://blogs.novita.ai/wan-2-2-vram-find-the-best-gpu-setup-for-deployment/).

## Format

```
First frame: {reference image, optional}
Beat 1: {action with body-part detail}
Beat 2: {escalation}
Beat 3: {resolution}

Lighting / Camera blocks.
```

## Example (Wan 2.2)

```
First frame: woman_at_table.png (woman seated across from man at candle-lit dinner table, wine glass in front of her).

Beat 1: She raises the wine glass slowly, fingers tightening on the stem, gaze locking on him.
Beat 2: She begins speaking — mouth shaping words continuously, jaw moving; he holds still, throat working in a swallow.
Beat 3: She sets the glass down with a soft clink, hand stays on the stem; his hand stays gripped on the napkin.

Lighting: warm candle from below, dim pendant overhead, condensation on the glass.
Camera: slow dolly push-in across the table, focus on her hand.
```

## Notes

- First-frame control: cleanest way to fix opening composition.
- Wan 2.7 multi-shot: partial, behaves more like scene-extend than true cut.
- Source: wan22.io/.

---

# Mochi 1 (Genmo) — legacy

**Strengths**: 10B params, fully open-weights, decent motion for an early model.
**Weaknesses**: 5.4s @ 30fps, 480p ceiling, ageing — superseded by Hunyuan / Wan / LTX-2.

## Hardware

Runs on a single H100; community 24GB consumer-GPU builds exist with quality loss.

## Format

```
{One paragraph: character action, body-part detail, beats embedded as prose.}

Lighting / Camera: {short blocks}
```

## Example (Mochi 1)

```
A woman raises a wine glass slowly at a candle-lit dinner table, fingers tightening on the stem, her gaze locked on a man across from her. She begins speaking, mouth shaping words, jaw moving; he holds still, throat working in a swallow. She sets the glass down softly, hand staying on the stem.

Lighting: warm candle from below, dim pendant overhead.
Camera: slow dolly push-in.
```

## Notes

- Legacy callout — keep prompts simple, expect 480p output.
- Migrate to HunyuanVideo 1.5 or LTX-2 Distilled for new work.

---

## Universal self-host anti-patterns

- Treating self-host like a closed API — these models need warm-up, LoRA selection, and sampler tuning. The prompt is half the work.
- Over-long prompts on Mochi 1 — its attention is short. Cut to 3-4 sentences.
- Ignoring first-frame control on Wan when the opening composition matters — set it explicitly.
- Audio-driven workflows on Hunyuan/Wan without acknowledging there's no native audio — render silent, sync separately. Only LTX-2 has native audio in this cluster.
