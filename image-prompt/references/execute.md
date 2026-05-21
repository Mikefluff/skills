# Execute mode — image-prompt

Optional layer that calls the vendor API and returns a real PNG / WEBP instead of just the prompt text. Activated by `--execute` on the skill or by running `image-prompt/scripts/run.py` directly. Falls back to prompt-only output when API keys are missing or the API call fails.

---

## When this fires

`image-prompt <scene> --execute` (or `--execute --model <slug>`) — if env keys for the chosen model are present, the skill writes the prompt AND calls the API AND saves the result to `./generated/image/<timestamp>-<slug>.png`.

If keys are missing → prompt is still produced, saved to `./generated/image/<timestamp>-prompt-only.txt`, plus a hint about which env var to set.

---

## Setup

1. Install runner deps (one-time):

```
pip install -r ~/.claude/skills/common/runners/requirements.txt
```

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
| `imagen-4` | Google | `GEMINI_API_KEY` | sync | $0.04 | Strict prompt adherence; no flags; ratio via API param. |
| `imagen-4-ultra` | Google | `GEMINI_API_KEY` | sync | $0.06 | 2K output. Best in Imagen family for text rendering. |
| `imagen-4-fast` | Google | `GEMINI_API_KEY` | sync | $0.02 | Iteration tier. |
| `nano-banana-pro` | Google | `GEMINI_API_KEY` | sync | $0.05 | 4K. Multi-person consistency up to 5. 14 reference images. Best for slides / diagrams / infographics. |
| `flux-1-1-pro` | BFL | `BFL_API_KEY` | async (poll) | $0.04 | Photorealism leader. |
| `flux-2-pro` | BFL | `BFL_API_KEY` | async (poll) | $0.06 | 32K context, 4MP, multi-ref ≤ 10, ~60% complex typography. |
| `flux-kontext` | BFL | `BFL_API_KEY` | async (poll) | $0.05 | Edit mode — needs `--image-url <path-or-url>`. Preserve/change grammar. |
| `flux-schnell` | BFL | `BFL_API_KEY` | async (poll) | $0.003 | Fast iteration. |
| `ideogram-3-turbo` | Ideogram | `IDEOGRAM_API_KEY` | sync | $0.02 | Cheap text-in-image. |
| `ideogram-3` | Ideogram | `IDEOGRAM_API_KEY` | sync | $0.04 | Default tier. |
| `ideogram-3-quality` | Ideogram | `IDEOGRAM_API_KEY` | sync | $0.08 | Best in class for legible multi-line text. |
| `fal-image` | fal.ai | `FAL_KEY` | async (poll) | ~$0.05 | Router. Override hosted model via `--fal-model <id>`. Hosts Flux / Recraft / Seedream / many mirrors. |
| `replicate-image` | Replicate | `REPLICATE_API_TOKEN` | async (poll) | ~$0.03 | Router. Override via `--replicate-model <owner>/<name>`. Hosts SD 3.5 / open-source frontier. |

**Prompt-only (no public API)**: Midjourney v7 (no first-party API; community gateways exist but quality varies — use fal-image with a Midjourney-style model alias if needed), Krea-1, Qwen-Image 2.0 (open weights — self-host), HiDream-O1 (open weights — self-host), Seedream 4.5 (use fal-image override), Recraft V3 (use fal-image with `--fal-model fal-ai/recraft-v3`).

---

## Cost preview

Generations estimated above $0.10 prompt for confirmation on stdin. Bypass with `--yes`:

```
python3 ~/.claude/skills/image-prompt/scripts/run.py \
  --model imagen-4-ultra \
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
- `ModuleNotFoundError: No module named 'openai'` → `pip install -r common/runners/requirements.txt`.

---

## Fall-back behaviour

When `--execute` is requested but:
- env key missing → prompt is saved to `./generated/image/<timestamp>-prompt-only.txt` with a one-line reason at top.
- API call fails / quota / timeout → same fallback. Skill stays useful.

In all cases the printed line on stdout is the path to the file (local or `<local> (also at <s3-url>)`).
