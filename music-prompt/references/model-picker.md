# Model picker

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision tree — given user intent, pick the right music model and load the right model-file. Use this before writing any prompt.

---

## By intent → model

- **Pop / hip-hop / EDM / rock with vocals + lyrics** → Suno v5.5 → [`models/suno.md`](models/suno.md)
- **Longest coherent song (5-10 min)** → Udio v4 → [`models/udio.md`](models/udio.md)
- **Stems / multi-track export** → Suno (12 stems, Pro+) or Udio (Stem Separation 2.0) → [`models/suno.md`](models/suno.md) / [`models/udio.md`](models/udio.md)
- **Voice clone into music** → Suno Voices (Premier) → [`models/suno.md`](models/suno.md)
- **Cover song / remix existing track** → Suno Cover or Udio remix → [`models/suno.md`](models/suno.md) / [`models/udio.md`](models/udio.md)
- **Label-safe / strict licensing** → Google Lyria 3 Pro → [`models/google.md`](models/google.md)
- **Cinematic / film score / instrumental** → Stable Audio 2.5 or Lyria 3 Pro → [`models/stable-audio.md`](models/stable-audio.md) / [`models/google.md`](models/google.md)
- **Sound design / SFX-music hybrid** → Stable Audio 2.5 → [`models/stable-audio.md`](models/stable-audio.md)
- **Voice realism + exclude-styles control** → ElevenLabs Music → [`models/elevenlabs.md`](models/elevenlabs.md)
- **Multilingual (EN+CJK or Chinese-first)** → Tencent SongGeneration → [`models/open-source.md`](models/open-source.md) or Suno
- **Self-host / open-weights** → MusicGen / Stable Audio Open / Tencent SongGeneration → [`models/open-source.md`](models/open-source.md)
- **Background loops for apps / streaming / games** → Mubert API → [`models/api-tools.md`](models/api-tools.md)
- **Free unlimited iteration** → Riffusion → [`models/api-tools.md`](models/api-tools.md)

---

## By capability matrix

| Model | Vocals | Stems | Max length | Brackets | `\|` stacking | Voice clone | Cover/Remix | API | Open weights | Languages |
|---|---|---|---|---|---|---|---|---|---|---|
| Suno v5.5 | ✓ | ✓ (12, Pro+) | ~8 min | ✓ | ✓ | ✓ (Premier) | ✓ (Cover) | ✓ | no | 50+ |
| Udio v4 | ✓ | ✓ (2.0) | ~10-15 min | ✓ | partial | no | ✓ (remix) | partial | no | 30+ |
| Google Lyria 3 Pro | ✓ | partial | 3 min (hard cap) | no | no | no | no | ✓ (Vertex) | no | EN / ES / FR / JP |
| Stable Audio 2.5 | partial | no | ~4.5 min | partial | no | no | no | ✓ | partial (Open) | EN |
| ElevenLabs Music | ✓ | ✓ | ~5 min | ✓ | partial | ✓ | no | ✓ | no | 30+ |
| Tencent SongGeneration | ✓ | partial | ~4 min | ✓ | partial | no | no | partial | ✓ | CJK + EN |
| MusicGen | no | no | ~30 sec extendable | no | no | no | no | ✓ | ✓ (CC-BY-NC) | n/a |
| Mubert | no | no | streaming loop | no | no | no | no | ✓ | no | n/a |
| Riffusion | ✓ | partial | ~3 min | partial | no | no | partial | partial | partial | EN-first |

---

## Quick-pick cheat sheet

```
If you just want one model and a fallback:
  - Suno v5.5         → 90% of use cases (vocals + lyrics + genre)
  - Udio v4           → when you need 5+ min coherent
  - ElevenLabs Music  → clean licensing + vocal realism
  - Lyria 3 Pro       → strict label-safe / enterprise work
That covers ~95% of needs.
```
