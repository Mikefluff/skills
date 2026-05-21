# Video models — index

Quick router from intent → capability cluster → file. The CHARACTER FIRST law and Beat 1/2/3 structure apply to every model — only syntax and audio/edit affordances change.

---

## By intent → cluster → file

| If you need… | Go to | Top picks |
|---|---|---|
| Native audio + dialogue + ambience in one pass | `audio-tier.md` | Veo 3.1, Sora 2, LTX-2 (open-source) |
| A still image → motion (I2V) | `i2v-tier.md` | Kling 3.0, Hailuo 02 Pro, Runway Gen-4, Pika 2.2 |
| Edit / transform existing footage (V2V) | `v2v-tier.md` | Runway Aleph, Luma Ray 3 Modify, Pikaswaps |
| Multi-shot scene in one prompt | `audio-tier.md` + `multi-shot.md` | Sora 2, Seedance 2.0 |
| Character consistency across clips | `identity-references.md` | Sora Cameos, Kling Elements, Act-One, Soul ID, HunyuanCustom |
| Open-weights / self-host | `open-source.md` | LTX-2, HunyuanVideo 1.5, Wan 2.2/2.7, Mochi 1 |
| Named camera presets (Bullet Time / Crash Zoom / FPV) | `aggregators.md` | Higgsfield AI Cinema Studio |
| Cheapest premium clip | `i2v-tier.md` | Kling 3.0 (~$0.10/sec) |
| Best physics (gymnastics, cloth, water) | `i2v-tier.md` + `audio-tier.md` | Hailuo 02, Sora 2 |

---

## Capability matrix

| Model | T2V | I2V | V2V | Native audio | Multi-shot | Character ref | Max duration | 4K | Open-weights | Price tier |
|---|---|---|---|---|---|---|---|---|---|---|
| Veo 3.1 | yes | yes | partial (extend) | yes | partial | yes (ref images) | 8s (scene-extend ladders) | yes | no | premium |
| Veo 3.1 Fast | yes | yes | partial | yes | partial | yes | 8s | yes | no | mid (~$0.15/sec) |
| Sora 2 | yes | yes | partial | yes | yes (in-prompt) | yes (Cameos) | 12s (4/8/12) | no (1080p ceiling) | no | premium (~$0.10/sec @ 720p) |
| Sora 2 Pro | yes | yes | partial | yes | yes | yes | 25s (10/15/25) | no (1080p ceiling) | no | premium (~$0.30/sec 720p, ~$0.50/sec 1024p) |
| LTX-2 | yes | yes | no | yes | no | partial | 20s @ 50fps | yes | yes | self-host |
| LTX-2 Distilled | yes | yes | no | yes | no | partial | 20s | yes | yes | self-host (consumer GPU) |
| Kling 3.0 | yes | yes | no | yes (native audio added in 3.0) | yes (Director, up to 6 shots) | yes (refs) | 15s | yes (native 4K @ 60fps) | no | cheap (~$0.10/sec) |
| Kling 2.6 Elements | yes | yes | no | no | no | yes (4 refs) | 10s | no | no | mid |
| Kling Master | yes | yes | no | no | no | no | 10s | no | no | mid |
| Hailuo 02 | yes | yes | no | no | no | no | 6-10s | 1080p | no | cheap (~$0.28/clip) |
| Hailuo 02 Pro | yes | yes | no | no | no | no | 6-10s | 1080p | no | mid |
| Runway Gen-4 | yes | yes | no | no | no | yes (refs) | 10s native (up to 60s w/ extend on Gen-4.5) | upscale only (4K export on Pro plan) | no | mid |
| Runway Gen-4 Turbo | yes | yes | no | no | no | yes | 10s | 1080p | no | cheap |
| Runway Aleph | no | no | yes | no | no | yes (refs) | 5s | 1080p | no | mid (~$0.18/sec) |
| Runway Act-One | no | partial | yes | no | no | yes (perf source) | 10s | 1080p | no | mid |
| Luma Ray 3 | yes | yes | no | no | no | yes | 10s native (up to 30s degrading); 5s @ 4K in Firefly | upscale to 4K HDR (Hi-Fi Diffusion) | no | mid |
| Luma Ray 3 Modify | no | no | yes | no | no | yes | 10s (5s / 10s) | no (1080p native) | no | mid |
| Pika 2.2 | yes | yes | yes (Pikaswaps/additions/frames) | no | no | partial | 10s | 1080p | no | cheap |
| HunyuanVideo 1.5 | yes | yes | no | no | no | partial | ~5s typical, distilled 480p in ~75s on 4090 | no (480p base, upscales to 1080p via DiT) | yes | self-host |
| HunyuanCustom | yes | yes | partial | partial (audio-driven) | no | yes (image/audio/video/text) | inherits Hunyuan base (~5s typical) | no | yes | self-host |
| Wan 2.2 | yes | yes | no | no | no | yes (first-frame) | 15s | no (480p / 720p native, upscale to 1080p / 4K) | yes | self-host |
| Wan 2.7 | yes | yes | no | no | partial | yes | 15s | yes | yes | self-host |
| Mochi 1 | yes | partial | no | no | no | no | 5.4s @ 30fps | 480p | yes | self-host (legacy) |
| Seedance 2.0 | yes | yes | no | partial (unconfirmed) | yes (up to 6 shots, 30s total) | yes (identity labels) | 30s multi-shot / ~41s render | 1080p | no | mid |
| Higgsfield (aggregator) | yes | yes | yes | passthrough | passthrough | yes (Soul ID) | depends on backend | depends | no | mid |

---

## Deprecations

Aliases still accepted with a deprecation warning. Route requests upward:

- Kling 1.6 → **Kling 3.0** (or **Kling Elements** if multi-element identity)
- Pika 1.5 → **Pika 2.2**
- Runway Gen-3 / Gen-3 Turbo → **Runway Gen-4** (T2V/I2V) or **Runway Aleph** (V2V)
- Luma Dream Machine 1.x → **Luma Ray 3** (T2V/I2V) or **Ray 3 Modify** (V2V)
- Veo 3 → **Veo 3.1** (gains scene-extend, reference images, native audio polish)
- Sora 1 → **Sora 2** (gains synced audio + multi-shot)

---

## Quick-pick cheat sheet

- Premium narrative + audio: **Veo 3.1**
- Cheap I2V with physics: **Kling 3.0**
- V2V edit on existing footage: **Runway Aleph**
- Named camera presets / Bullet Time / Crash Zoom: **Higgsfield**
- Self-host with audio + 4K: **LTX-2**

---

## Universal rules (all models)

- CHARACTER FIRST — body parts, repeated motion, beat structure before camera/lighting.
- Beat 1/2/3 structure is canon. Kling demands explicit time markers; others accept implicit beats.
- One camera move per shot. Two stacked only if absolutely needed.
- No transition language inside one shot (`cut to`, `fade to`, `dissolve`) — except where the model explicitly supports multi-shot prompts (Sora 2, Seedance, Higgsfield).
- For I2V: do NOT re-describe the source frame; describe motion only.
- For V2V: use ONE action verb per call — Add / Remove / Replace / Relight / Re-angle / Restyle / Extend.
