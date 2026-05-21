---
title: Execute end-to-end — prompt → API → asset
covers: [image-prompt, video-prompt, music-prompt]
skills:
  - image-prompt
  - video-prompt
  - music-prompt
---

# Execute end-to-end

Three worked examples that take the prompt the skill produces and run it through a real API to land a PNG / MP4 / MP3. Requires v2.2.0+ and the relevant env var(s).

## Setup (one-time)

`install.sh` already created `~/.claude/skills/.runners-venv` and installed the runner deps for you. Just configure keys:

```bash
cp .env.example ~/.skills.env
${EDITOR:-vi} ~/.skills.env       # add the keys you have
set -a; source ~/.skills.env; set +a
```

If you used `SKILLS_SKIP_VENV=1` or want to reinstall deps manually:

```bash
python3 -m venv ~/.claude/skills/.runners-venv
~/.claude/skills/.runners-venv/bin/pip install -r ~/.claude/skills/common/runners/requirements.txt
```

Check what's reachable:

```bash
python3 ~/.claude/skills/image-prompt/scripts/run.py --list-providers
python3 ~/.claude/skills/video-prompt/scripts/run.py --list-providers
python3 ~/.claude/skills/music-prompt/scripts/run.py --list-providers
```

---

## Image — gpt-image-2 (OpenAI)

**Setup**: `export OPENAI_API_KEY=sk-...`

**Step 1: produce the prompt** (skill in Claude Code):

```
/image-prompt a confident woman in her thirties leaning on a polished marble countertop in a sunlit Brooklyn loft kitchen at golden hour, editorial photo, 85mm f/1.8
```

The skill returns a paste-ready prompt block. Save it:

```
echo "...<the prompt from above>..." > /tmp/scene.txt
```

**Step 2: execute**:

```bash
python3 ~/.claude/skills/image-prompt/scripts/run.py \
  --model gpt-image-2 \
  --prompt-file /tmp/scene.txt \
  --quality medium \
  --yes
```

Expected output: `./generated/image/20260521-130000-gpt-image-2.png`

If `S3_BUCKET` etc. are set: `./generated/image/...png  (also at https://...)`

Cost: ~$0.05.

**Variations**:
- High quality: `--quality high` (~$0.10, will prompt for confirmation without `--yes`).
- Multiple variants: `--variants 3` (saves first; vendor returns N).
- Custom output dir: `--output /tmp/imgs/`.
- Estimated cost only: `--cost-only`.

**Fall-back** (no key): saves prompt to `./generated/image/...-prompt-only.txt` with reason "missing env: OPENAI_API_KEY".

---

## Video — Veo 3.1 Fast (Google)

**Setup**: `export GEMINI_API_KEY=...`

**Step 1: produce the prompt** (Claude Code):

```
/video-prompt animate this still: two characters at a candle-lit dinner table, she raises a wine glass, says "I'm not coming home tonight" --model veo-3-1
```

The skill outputs a beat-structured prompt with Dialogue / SFX / Ambient blocks. Save to `/tmp/scene.txt`.

**Step 2: execute** (long-running, polls):

```bash
python3 ~/.claude/skills/video-prompt/scripts/run.py \
  --model veo-3-1-fast \
  --prompt-file /tmp/scene.txt \
  --duration 8 \
  --yes
```

```
Calling veo-3-1-fast (est cost $1.2000)...
  job operations/... queued, polling.......... done (47.3s)
./generated/video/20260521-130200-veo-3-1-fast.mp4
```

Cost: 8s × $0.15 ≈ $1.20 (Fast tier; Standard is $0.40/sec).

**Long-poll behaviour**: dots printed to stderr while waiting. Default timeout 600s; override `--timeout 1200` for the full tier.

**Notes**:
- For I2V (with a start frame): `--image-url https://...` or local path.
- For Aleph V2V: `--model aleph --video-url https://existing.mp4 --prompt "Add snowfall and relight to dusk."`
- For Sora 2 (once gated): `--model sora-2` (requires `OPENAI_SORA_API_ENABLED=1`).

---

## Music — Suno v5.5

**Setup**: `export SUNO_API_KEY=... && export SUNO_API_ENABLED=1`

**Step 1: produce the prompt** (Claude Code):

```
/music-prompt anthemic modern pop chorus about leaving home --model suno-v5-5
```

The skill outputs TWO boxes — Style of Music + Lyrics. Save them separately:

```bash
cat > /tmp/style.txt <<'EOF'
Modern pop, anthemic, female lead, polished production, 110 BPM
EOF

cat > /tmp/lyrics.txt <<'EOF'
[Intro | building energy]

[Verse 1 | soft indie whisper | minimal drums]
Walking down the street tonight
The neon signs are humming bright

[Chorus | anthemic chorus | stacked harmonies | wide stereo]
We light it up like fire
We light it up like fire
(yeah)

[Outro | fade out]
EOF
```

**Step 2: execute**:

```bash
python3 ~/.claude/skills/music-prompt/scripts/run.py \
  --model suno-v5-5 \
  --prompt-file /tmp/style.txt \
  --lyrics-file /tmp/lyrics.txt \
  --yes
```

```
Calling suno-v5-5 (est cost $0.1000)...
  job <id> queued, polling.................. done (94.2s)
./generated/music/20260521-130400-suno-v5-5.mp3
```

Cost: $0.10 / song.

**Instrumental variant**:

```bash
... --instrumental --yes
```

(Lyrics field ignored; Style of Music + the genre recipe drive the gen.)

---

## Multi-cloud output

If you also set `S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY` (plus optional `S3_ENDPOINT` for MinIO / DO Spaces / R2):

```
./generated/image/20260521-130000-gpt-image-2.png  (also at https://<bucket>.s3.<region>.amazonaws.com/skills-generated/image/20260521-130000-gpt-image-2.png)
```

Local copy is always written first. The S3 upload is best-effort — failure prints a warning but doesn't abort the run.

---

## Pre-flight check

To validate connectivity to a specific provider without spending credit:

```bash
python3 ~/.claude/skills/image-prompt/scripts/run.py --check --model gpt-image-2
# OK: gpt-image-2 configured (env set). Run without --check to generate.
```

To see only estimated cost:

```bash
python3 ~/.claude/skills/video-prompt/scripts/run.py --cost-only --model veo-3-1 --duration 8
# estimated cost: $3.2000
```

---

## Troubleshooting

- `missing env: ...` → export the named env var in this shell.
- `[provider 429] ...` → vendor quota. Wait.
- `[provider 401] ...` → key wrong.
- `Sora 2 API access is currently gated` → set `OPENAI_SORA_API_ENABLED=1`.
- `Lyria 3 Pro API is in limited preview` → set `LYRIA_API_ENABLED=1`.
- `Suno API access is currently gated` → set `SUNO_API_ENABLED=1`.
- `cannot locate common/runners` → re-run `install.sh`.
- `ModuleNotFoundError: No module named 'openai'` (or `google.genai` / `boto3`) → `pip install -r common/runners/requirements.txt`.

Provider-specific tips: `*/references/execute.md` for each skill.
