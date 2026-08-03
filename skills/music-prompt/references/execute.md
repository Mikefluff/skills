# Execute mode — music-prompt

Optional layer that calls the vendor API and returns a real MP3 instead of just the Style+Lyrics prompt text. Activated by `--execute` on the skill or by running `music-prompt/scripts/run.py` directly. Falls back to prompt-only output when API keys are missing or the API call fails.

Music generations are async (~30s-3min). The runner polls vendor APIs and prints dots to stderr.

---

## When this fires

`music-prompt <brief> --execute` (or `--execute --model <slug>`) — if env keys are present, the skill produces the prompt AND calls the API AND saves an MP3 to `./generated/music/<timestamp>-<slug>.mp3`.

---

## Setup

1. Runner deps are installed automatically by `install.sh` into `~/.claude/skills/.runners-venv` (Python ≥ 3.10). To skip auto-venv: `SKILLS_SKIP_VENV=1 bash install.sh ...`. Manual reinstall: `~/.claude/skills/.runners-venv/bin/pip install -r ~/.claude/skills/common/runners/requirements.txt`.

2. Export keys for the providers you have:

```
export SUNO_API_KEY=...           # gateway token — Suno has no public API of its own
export SUNO_API_ENABLED=1         # gates Suno until you confirm your gateway
export SUNO_API_URL=https://<your-gateway>/v1   # REQUIRED — there is no official endpoint
export ELEVENLABS_API_KEY=...     # Eleven Music (music_v2)
export GEMINI_API_KEY=...         # Lyria 3 Pro / Clip (paid preview)
export LYRIA_API_ENABLED=1        # gates Lyria until access confirmed
export FAL_KEY=...                # fal-music router
export REPLICATE_API_TOKEN=...    # replicate-music router (MusicGen + many open-source)
```

3. Verify:

```
python3 ~/.claude/skills/music-prompt/scripts/run.py --list-providers
```

---

## Provider matrix

| Slug | Vendor | Env var(s) | Max length | Est cost/song | Notes |
|---|---|---|---|---|---|
| `suno-v5-5` | Suno (gateway) | `SUNO_API_KEY` + `SUNO_API_ENABLED=1` + `SUNO_API_URL` | ~4 min default, ~8 min Pro | $0.10 | **No official API** — needs a gateway URL. Pass Style box via `--prompt`, Lyrics box via `--lyrics` or `--lyrics-file`. Brackets in Lyrics box only. `--instrumental` flips lyrics-off. |
| `lyria-3-pro` | Google | `GEMINI_API_KEY` + `LYRIA_API_ENABLED=1` | 3 min hard cap | $0.30 per 3min ($0.10 per min) | Field-driven — NL prompt + optional `--lyrics` + `--duration` (minutes). 44.1 kHz stereo. No brackets. Watermarked. Label-safe. |
| `lyria-3-clip` | Google | `GEMINI_API_KEY` + `LYRIA_API_ENABLED=1` | 30 sec | $0.05 per clip | Speed tier for high-volume work — stings, loops, bumpers. Same grammar as Pro. |
| `eleven-music` | ElevenLabs | `ELEVENLABS_API_KEY` | 3 sec - 10 min via `--duration` | ~$0.20 per minute | Runs `music_v2`. Single prompt with bracketed style cues + timing markers; `--lyrics` is folded into the prompt (no separate field). `--instrumental` maps to `force_instrumental`. |
| `fal-music` | fal.ai | `FAL_KEY` | varies | ~$0.05 - $0.30 | Router. Default `fal-ai/cassetteai/music-generator`. Override via `--fal-model <id>`. Hosts MusicGen / open-source music models. |
| `replicate-music` | Replicate | `REPLICATE_API_TOKEN` | varies | ~$0.05 - $0.20 | Router. Default `meta/musicgen`. Override via `--replicate-model`. |

**Prompt-only**: Udio v4 (Developer Platform is Pro/Enterprise gated and key formats vary by tier — set `UDIO_API_KEY` and run via the user's own HTTP wrapper for now), Stable Audio 2.5 (Stability Direct API on Replicate — use `replicate-music --replicate-model stability-ai/stable-audio-2-5`), Tencent SongGeneration (open weights — self-host), Sonauto v2 (use Sonauto directly — set `SONAUTO_API_KEY` and use `requests` script), Riffusion (waitlist), Mubert (parameter-driven API, not yet covered — use direct HTTP).

---

## Cost preview

Suno + ElevenLabs + Lyria are all near or above the $0.10 threshold — confirmation will prompt. Bypass with `--yes`. Cost-only check via `--cost-only`.

---

## Long-poll behaviour

Same `poll_until` pattern as video. Default timeout 600s, override `--timeout`.

---

## Output

Default `./generated/music/<timestamp>-<slug>.mp3`. Override `--output`.

If S3 env vars set, also uploaded with `audio/mpeg` mime.

---

## Mode-specific notes

### Suno

The skill produces two boxes:
- Style of Music (≤1000 chars, NL only) → passed as `--prompt`
- Lyrics (≤3000 chars, brackets + lyrics) → passed via `--lyrics-file <generated-lyrics.txt>` or `--lyrics "..."`

For instrumental tracks: `--instrumental` (lyrics field is ignored).

### Lyria 3 Pro

Field-driven invocation:
- `--prompt` — natural-language scene
- `--lyrics` — optional (EN / ES / FR / JP only)
- `--duration` — minutes (max 3)

No bracket tags.

### ElevenLabs Music

Single prompt. Bracketed cues inside the prompt text:
- `[energetic guitar solo]` style hints
- `"130 BPM"`, `"in A minor"`, `"60 seconds"` timing
- Exclude-styles: include `"no abrupt ending"` in the prompt body

---

## Troubleshooting

- `[suno-v5-5 ...] Suno API access is currently gated` → set `SUNO_API_ENABLED=1`. If using a gateway, set `SUNO_API_URL` to the gateway base URL.
- `[lyria-3-pro ...] Lyria 3 is in paid preview` → set `LYRIA_API_ENABLED=1` once your project is allowlisted.
- `[suno-v5-5 ...] Suno has no public API` → set `SUNO_API_URL` to your gateway, or switch to `eleven-music` / `lyria-3-pro`.
- `[eleven-music 401] ...` → check `ELEVENLABS_API_KEY` is correct.
- `429` → vendor quota; wait or use a different provider.
- Mute / instrumental output when lyrics expected → for Suno, ensure brackets are in Lyrics box; for Eleven, include lyric text inside the prompt.

---

## Fall-back behaviour

Same as image / video: on missing env / API failure / timeout, the prompt + lyrics are saved as a text file under `./generated/music/` with a one-line reason. Useful for paste-into-Suno-manually workflow.
