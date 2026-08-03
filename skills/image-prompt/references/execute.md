# Execute mode — image-prompt

Optional layer that calls the vendor API and returns a real PNG / WEBP instead of just the prompt text. Activated by `--execute` on the skill or by running `image-prompt/scripts/run.py` directly. Falls back to prompt-only output when API keys are missing or the API call fails.

---

## When this fires

`image-prompt <scene> --execute` (or `--execute --model <slug>`) — if env keys for the chosen model are present, the skill writes the prompt AND calls the API AND saves the result to `./generated/image/<timestamp>-<slug>.png`.

If keys are missing → prompt is still produced, saved to `./generated/image/<timestamp>-prompt-only.txt`, plus a hint about which env var to set.

---

## Setup

1. Runner deps are installed automatically by `install.sh` into `~/.claude/skills/.runners-venv` (Python ≥ 3.10). To skip auto-venv: `SKILLS_SKIP_VENV=1 bash install.sh ...`. Manual reinstall: `~/.claude/skills/.runners-venv/bin/pip install -r ~/.claude/skills/common/runners/requirements.txt`.

2. Export the keys you actually have. Pick any subset; unset providers stay prompt-only.

```
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
export BFL_API_KEY=...
export FAL_KEY=...
export REPLICATE_API_TOKEN=...
export IDEOGRAM_API_KEY=...
```

Or copy `.env.example` from the repo root, fill in, then `set -a; source ~/.skills.env; set +a`.

3. Verify what's currently available:

```
python3 ~/.claude/skills/image-prompt/scripts/run.py --list-providers
```

---

## Provider matrix

| Slug | Vendor | Env var(s) | Modality | Est cost/image | Notes |
|---|---|---|---|---|---|
| `gpt-image-2` | OpenAI | `OPENAI_API_KEY` | sync | $0.02 - $0.10 | Quality tiers: low / medium / high. ~99% character accuracy across Latin/CJK/Hindi/Bengali. 16 reference images. |
| `nano-banana-pro` | Google | `GEMINI_API_KEY` | sync | $0.134 ($0.24 4K) | Multi-person consistency up to 5. 14 reference images. Best for slides / diagrams / infographics. |
| `nano-banana-2` | Google | `GEMINI_API_KEY` | sync | $0.101 ($0.151 4K) | The default Google tier. 4K, reliable text, strong multi-ref. |
| `nano-banana-2-lite` | Google | `GEMINI_API_KEY` | sync | $0.034 | Cheapest Google tier. Moodboarding and iteration. |
| `flux-1-1-pro` | BFL | `BFL_API_KEY` | async (poll) | $0.04 | Photorealism leader. |
| `flux-2-pro` | BFL | `BFL_API_KEY` | async (poll) | $0.06 | 32K context, 4MP, multi-ref ≤ 10, ~60% complex typography. |
| `flux-kontext` | BFL | `BFL_API_KEY` | async (poll) | $0.05 | Edit mode — needs `--image-url <path-or-url>`. Preserve/change grammar. |
| `flux-schnell` | BFL | `BFL_API_KEY` | async (poll) | $0.003 | Fast iteration. |
| `ideogram-3-flash` | Ideogram | `IDEOGRAM_API_KEY` | sync | ≤$0.02 | Fastest text-in-image tier. |
| `ideogram-3-turbo` | Ideogram | `IDEOGRAM_API_KEY` | sync | $0.02 | Cheap text-in-image. |
| `ideogram-3` | Ideogram | `IDEOGRAM_API_KEY` | sync | $0.04 | Default tier. |
| `ideogram-3-quality` | Ideogram | `IDEOGRAM_API_KEY` | sync | $0.08 | Best in class for legible multi-line text. |
| `fal-image` | fal.ai | `FAL_KEY` | async (poll) | ~$0.05 | Router. Override hosted model via `--fal-model <id>`. Hosts Flux / Recraft / Seedream / many mirrors. |
| `replicate-image` | Replicate | `REPLICATE_API_TOKEN` | async (poll) | ~$0.03 | Router. Override via `--replicate-model <owner>/<name>`. Hosts SD 3.5 / open-source frontier. |

**Prompt-only (no public API)**: Midjourney V8.1 (no first-party API; community gateways exist but quality varies — use fal-image with a Midjourney-style model alias if needed), Krea-1, Qwen-Image 2.0 (open weights — self-host), HiDream-O1 (open weights — self-host), Ideogram 4.0 (open weights on Hugging Face; the hosted API still exposes only the v3 generate endpoint, so `ideogram-3-*` remains what we call), Seedream 5.0 (use fal-image override), Recraft V3 (use fal-image with `--fal-model fal-ai/recraft-v3`), FLUX 3 (early access, no API yet), Meta Muse Image (no public API).

### Retired slugs

`imagen-4`, `imagen-4-ultra` and `imagen-4-fast` still resolve, print a warning,
and route to `nano-banana-2`, `nano-banana-pro` and `nano-banana-2-lite`
respectively. Google shut the Imagen endpoints down on 2026-06-30.

---

## Cost preview

Generations estimated above $0.10 prompt for confirmation on stdin. Bypass with `--yes`:

```
python3 ~/.claude/skills/image-prompt/scripts/run.py \
  --model nano-banana-pro \
  --prompt-file ./my-prompt.txt \
  --yes
```

Show cost without generating:

```
... --cost-only
```

---

## Output handling

Default: `./generated/image/<YYYYMMDD-HHMMSS>-<model-slug>.png`. Override:

```
--output /tmp/my-image-dir/
```

If S3 env vars are set (`S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, optional `S3_ENDPOINT` / `S3_REGION` / `S3_PATH_PREFIX`), the same file is also uploaded and the URL is printed alongside the local path. Supports AWS S3 / DigitalOcean Spaces / MinIO / Cloudflare R2.

---

## Troubleshooting

- `missing env: OPENAI_API_KEY` → export the key in this shell (or `source` the .env file).
- `[provider 429] ...` → vendor quota / rate limit. Wait and retry.
- `[provider 401] ...` → key is wrong. Re-check.
- `[gpt-image-2 500] ...` → vendor outage. Try a different model or fal-image.
- `cannot locate common/runners` → re-run `install.sh` from the repo root.
- `ModuleNotFoundError: No module named 'openai'` → venv may not have been set up. Reinstall: `~/.claude/skills/.runners-venv/bin/pip install -r ~/.claude/skills/common/runners/requirements.txt`. Or re-run `install.sh`.

---

## Fall-back behaviour

When `--execute` is requested but:
- env key missing → prompt is saved to `./generated/image/<timestamp>-prompt-only.txt` with a one-line reason at top.
- API call fails / quota / timeout → same fallback. Skill stays useful.

In all cases the printed line on stdout is the path to the file (local or `<local> (also at <s3-url>)`).
