# common/runners — optional execution layer

Lets the `image-prompt`, `video-prompt`, and `music-prompt` skills go beyond producing prompt text and actually call vendor APIs when keys are present. Without this layer, the skills stay prompt-only — exactly what they were in v2.1.

## Install

`install.sh` creates a dedicated venv at `~/.claude/skills/.runners-venv` and installs deps for you (Python ≥ 3.10 required). No separate step needed.

To install / refresh manually:

```bash
python3 -m venv ~/.claude/skills/.runners-venv
~/.claude/skills/.runners-venv/bin/pip install -r ~/.claude/skills/common/runners/requirements.txt
```

The `requests` dep is required for everything; `openai` and `google-genai` are recommended for the most-used vendors; `boto3` is needed only if you opt into S3 upload.

To skip auto-venv during `install.sh`: `SKILLS_SKIP_VENV=1 bash install.sh ...`.

## Configure

Copy `.env.example` from the repo root, fill in the keys you actually have, and source it:

```bash
cp .env.example ~/.skills.env
${EDITOR:-vi} ~/.skills.env
set -a ; source ~/.skills.env ; set +a
```

Or export inline:

```bash
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
export BFL_API_KEY=...
export FAL_KEY=...
```

Skills check `os.environ` at runtime. Unset keys = that provider stays prompt-only.

## Run

Each modality has its own CLI module:

```bash
# image
python3 -m common.runners.cli.image --list-providers
python3 -m common.runners.cli.image --check --model gpt-image-2
python3 -m common.runners.cli.image --model gpt-image-2 --prompt "..."

# video
python3 -m common.runners.cli.video --model veo-3-1 --prompt "..." --duration 8

# music
python3 -m common.runners.cli.music --model suno-v5-5 --prompt "..." --style "..." --lyrics ...
```

Or invoke the per-skill entry script (`image-prompt/scripts/run.py` etc.) — same interface, thin wrapper.

## Output

- Local: `./generated/<modality>/<timestamp>-<slug>.<ext>` always.
- S3 / DigitalOcean Spaces / MinIO / Cloudflare R2 (optional): if `S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY` are set, the file is also uploaded and the URL is printed alongside the local path.

## Fall-back behaviour

If `--execute` is requested but the relevant key is missing OR the API call fails, the runner writes the prompt to `./generated/<modality>/<timestamp>-prompt-only.txt` and prints the path + a one-line reason. The skill stays useful.

## Architecture

```
common/runners/
  config.py          # provider registry + env resolution
  poll.py            # poll-with-timeout for async vendors (video, music)
  cost.py            # static price table + interactive confirmation
  output.py          # save() — local + optional S3 mirror
  errors.py          # typed exceptions
  storage/
    local.py
    s3.py            # boto3 wrapper, supports custom endpoint
  providers/
    base.py          # Provider ABC
    <vendor>.py      # one file per vendor (openai_image, google_video, bfl, fal, ...)
  cli/
    image.py
    video.py
    music.py
```

Pattern adapted from the author's earlier provider abstraction and S3 sink — single-user CLI cut of those, without Temporal / SurrealDB / multi-tenancy.

## Cost confirmation

Generations estimated above `$0.10` USD prompt for confirmation on stdin. Bypass with `--yes`. The estimate is best-effort using the price table in `cost.py`; actual billing may differ slightly.
