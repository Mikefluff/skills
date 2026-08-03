# Execute mode — video-prompt

Optional layer that calls the vendor API and returns a real MP4 instead of just the prompt text. Activated by `--execute` on the skill or by running `video-prompt/scripts/run.py` directly. Falls back to prompt-only output when API keys are missing or the API call fails.

Video generations are **long-running** (60s-5min). The runner polls vendor APIs and prints dots to stderr while waiting; results land on disk when ready. Cost prompts always trigger for video (any video is over the $0.10 threshold).

---

## When this fires

`video-prompt <action> --execute` (or `--execute --model <slug>`) — if env keys are present and the cost is confirmed, the skill produces the prompt AND calls the API AND saves the MP4 to `./generated/video/<timestamp>-<slug>.mp4`.

---

## Setup

1. Runner deps are installed automatically by `install.sh` into `~/.claude/skills/.runners-venv` (Python ≥ 3.10). To skip auto-venv: `SKILLS_SKIP_VENV=1 bash install.sh ...`. Manual reinstall: `~/.claude/skills/.runners-venv/bin/pip install -r ~/.claude/skills/common/runners/requirements.txt`.

2. Export keys:

```
export GEMINI_API_KEY=...           # Veo 3.1 / Veo 3.1 Fast
export OPENAI_API_KEY=sk-...        # Sora 2 (once API is enabled)
export OPENAI_SORA_API_ENABLED=1    # gates Sora 2 until you have access
export RUNWAY_API_KEY=...           # Gen-4 / Gen-4 Turbo / Aleph
export KLING_ACCESS_KEY_ID=...      # Kling 3 (needs both)
export KLING_ACCESS_KEY_SECRET=...
export FAL_KEY=...                  # fal-video router
export REPLICATE_API_TOKEN=...      # replicate-video router
```

3. Verify what's reachable:

```
python3 ~/.claude/skills/video-prompt/scripts/run.py --list-providers
```

---

## Provider matrix

| Slug | Vendor | Env var(s) | Max duration | Est cost/sec | Notes |
|---|---|---|---|---|---|
| `veo-3-1` | Google | `GEMINI_API_KEY` | 8s native | $0.40 ($0.60 4K) | Native audio + dialogue + lip-sync. 4K. Scene-extend to 148s via chained generations. |
| `veo-3-1-fast` | Google | `GEMINI_API_KEY` | 8s | $0.12 ($0.30 4K) | Cheaper tier; same audio capability. |
| `veo-3-1-lite` | Google | `GEMINI_API_KEY` | 8s | $0.08 | Cheapest tier with audio. 1080p ceiling. |
| `kling-3` | Kuaishou | `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET` | 15s | $0.12 | Cheapest premium tier. Native audio (Omni). AI Director multi-shot up to 6 shots. Multi-speaker via `<<<voice_1>>>`. |
| `gen-4` | Runway | `RUNWAY_API_KEY` | 10s native | $0.10 | I2V (needs `--image-url`). 4K via upscale. |
| `gen-4-turbo` | Runway | `RUNWAY_API_KEY` | 10s | $0.05 | Faster, cheaper, less detail. |
| `gen-4-5` | Runway | `RUNWAY_API_KEY` | 10s native | $0.12 | Sharper motion and prompt adherence than gen-4; extend to 60s. |
| `aleph` | Runway | `RUNWAY_API_KEY` | 5s | $0.18 | V2V (needs `--video-url`). One action verb per pass. |
| `sora-2` | OpenAI | `OPENAI_API_KEY` + `OPENAI_SORA_API_ENABLED=1` | 12s | $0.10 | **Retired 2026-09-24** — see below. |
| `sora-2-pro` | OpenAI | same | 25s | $0.50 | **Retired 2026-09-24** — see below. |
| `fal-video` | fal.ai | `FAL_KEY` | varies | ~$0.15 | Router. Default `fal-ai/kling-video/v1.6/pro/text-to-video`. Override via `--fal-model <id>`. Hosts most frontier video models. |
| `replicate-video` | Replicate | `REPLICATE_API_TOKEN` | varies | ~$0.10 | Router. Default `kwaivgi/kling-v1.6-pro`. Override via `--replicate-model`. |

### Sora 2 is being removed from the API

OpenAI announced on 2026-03-24 that the Videos API and every Sora 2 alias and
snapshot are deleted on **2026-09-24**, and named no successor model. The
providers stay callable until that date and print a countdown on every run.

Migrate by capability, not by price:

| What you used Sora for | Go to |
|---|---|
| Native audio + dialogue | `veo-3-1` (48 kHz synced dialogue) |
| Multi-shot in one prompt | `kling-3` (AI Director, up to 6 shots) |
| Cheapest clip with sound | `veo-3-1-lite` or `kling-3` |
| Cameo / identity lock | `kling-3` refs, or `gen-4-5` reference images |

**Prompt-only**: Hailuo 02 / 02 Pro (use fal-video with a Hailuo model alias), Pika 2.2 (use fal/replicate), Luma Ray 3 / Ray 3 Modify (Luma's API is in private beta — try fal-video), LTX-2 / HunyuanVideo 1.5 / Wan 2.2 (open weights — self-host or via Replicate), Seedance 2.0 (use fal-video with Seedance model), Higgsfield (no API — aggregator UI only), Pika 2.2 Pikaswaps / Ray 3 Modify (V2V — use Aleph as the closest API-accessible analog).

---

## Cost preview

ALWAYS prompted (any video is above $0.10 threshold). Bypass:

```
... --execute --yes
```

Cost-only check:

```
... --execute --cost-only --duration 8
```

---

## Long-poll behaviour

Async vendors (all of the above except where noted). The runner uses `poll_until` from `common/runners/poll.py`:

- Initial interval 3s, gentle backoff to 12s.
- Default timeout 600s (10 min). Override: `--timeout 1200`.
- Dots printed to stderr while waiting; final newline + elapsed time when done.
- Ctrl+C aborts the runner; the vendor job may still complete server-side — check the vendor's dashboard.

---

## Output handling

Default: `./generated/video/<YYYYMMDD-HHMMSS>-<model-slug>.mp4`. Override `--output`.

If S3 env vars are set, same file uploaded and URL printed. MP4 mime is `video/mp4`.

---

## Mode-specific flags

- I2V (Gen-4, Kling): `--image-url https://...` or local path (will be uploaded if vendor needs URL).
- V2V (Aleph): `--video-url https://...`.
- Audio-bearing (Veo 3.1, Sora 2, Kling 3 Omni): include dialogue / SFX / ambient blocks inside `--prompt`. See `references/audio-prompting.md`.
- Multi-shot (Sora 2, Seedance via fal): use `--shots N` and pass a multi-shot prompt body. See `references/multi-shot.md`.
- Identity refs (cameos, Soul ID): pass as `--ref name=path` on the prompt skill; the executor receives the prompt with `[ref:Name]` labels and the vendor that supports it consumes them.

---

## Troubleshooting

- `[veo-3-1 403] ...` → ensure your Google Cloud project has Veo access enabled in Vertex AI.
- `[sora-2 ...] Sora 2 API access is currently gated` → set `OPENAI_SORA_API_ENABLED=1` once your OpenAI account is approved.
- `[kling-3 401] ...` → JWT signing failed; double-check `KLING_ACCESS_KEY_ID` and `KLING_ACCESS_KEY_SECRET`.
- `provider 'aleph' ... missing --video-url` → V2V mode requires a source video URL.
- Timeout after 10 min on `veo-3-1` → vendor backlog; raise `--timeout 1800` or check dashboard.
- `cannot locate common/runners` → re-run `install.sh`.

---

## Fall-back behaviour

Same as image: on missing env / API failure / timeout, prompt is saved to `./generated/video/<timestamp>-prompt-only.txt` with a one-line reason. Skill stays useful.
