---
name: skills-keys
description: "Manage API keys for the runner's --execute layer. CRUD on ~/.skills.env (chmod 600): list / add / update / remove / enable / disable gate flags / verify (ping vendor APIs) / export (eval-ready). Single source of truth for OPENAI_API_KEY, GEMINI_API_KEY, BFL_API_KEY, FAL_KEY, REPLICATE_API_TOKEN, RUNWAY_API_KEY, KLING_ACCESS_KEY_ID/SECRET, SUNO_API_KEY, ELEVENLABS_API_KEY, IDEOGRAM_API_KEY, ANTHROPIC_API_KEY, S3_* + gate flags (LYRIA_API_ENABLED, SUNO_API_ENABLED, OPENAI_SORA_API_ENABLED). Explicit shell exports always win over file entries. Use when the user says 'add my OpenAI key', 'rotate the Suno key', 'check which keys are set', 'verify my Gemini key works', 'where do I put my keys'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Provide a thin CLI on top of `~/.skills.env` (the runner's key store) so users can manage keys WITHOUT editing dotfiles by hand. Values are stored plaintext but chmod 600. Each runner reads the file at startup, merging entries into `os.environ` without overriding explicit shell exports.

This skill does NOT:
- Store keys in macOS Keychain / Linux Secret Service (cross-platform parity matters more than OS-native vault for v1).
- Encrypt the file at rest (chmod 600 is the v1 posture).
- Manage non-runner keys (database creds, SSH keys, etc.).
- Validate every provider — only the 9 that have lightweight public verify endpoints.

Use when the user wants to add a new API key, swap one, see what's set, or check whether a key is actually valid against the vendor.
</objective>

## ROLE

Read the user's intent (add/update/remove/list/verify/enable/disable/path/export) → call the matching `common/runners/cli/keys.py` subcommand → relay the result. Mask values when displaying. Prompt for value silently if not provided on the command line. Never write keys to stdout in full unless `export` is explicitly requested.

## PIPELINE

1. **Parse intent**: which subcommand and which arg(s).
2. **Run** `python3 scripts/run.py <subcommand> [args]`.
3. **Relay the output** — already masked / colorized by the CLI.
4. **Optional follow-up**: if user added a new key, suggest running `skills-keys verify <KEY>` to confirm it works.

## MODES

### Inspection

- `skills-keys list` — show all keys with masked values + gate-flag indicator
- `skills-keys path` — print the keys-file path (default `~/.skills.env`; override via `SKILLS_KEYS_FILE` env var)
- `skills-keys verify` — ping every supported provider's endpoint, report valid/invalid/unknown/unsupported per key
- `skills-keys verify OPENAI_API_KEY GEMINI_API_KEY` — verify specific keys only

### Mutation

- `skills-keys add OPENAI_API_KEY sk-proj-...` — add or update
- `skills-keys add OPENAI_API_KEY` — interactive (silent stdin read; not echoed)
- `skills-keys update OPENAI_API_KEY sk-new-...` — alias for `add`
- `skills-keys remove OPENAI_API_KEY` — delete the entry

### Gate flags

Three keys are NOT API tokens but on/off gates for paid premium endpoints:

- `OPENAI_SORA_API_ENABLED` — required to call Sora 2 (anti-accidental-spend gate)
- `LYRIA_API_ENABLED` — required to call Lyria 3 Pro
- `SUNO_API_ENABLED` — required to call Suno

Shortcut commands:
- `skills-keys enable SUNO_API_ENABLED` — equivalent to `add SUNO_API_ENABLED 1`
- `skills-keys disable SUNO_API_ENABLED` — equivalent to `remove SUNO_API_ENABLED`

### Export

- `skills-keys export` — print eval-ready lines:
  ```
  export OPENAI_API_KEY="sk-..."
  export GEMINI_API_KEY="..."
  ```
  Use to apply file changes to the CURRENT shell: `eval "$(skills-keys export)"`. Plaintext output — only pipe to eval, don't share.

- `skills-keys export --mask` — same shape but values masked, for inspection.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/usage.md](references/usage.md) | Detailed UX reference — what each subcommand prints, exit codes, interactive prompts, file format, precedence rules |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 4 example sessions covering: first-time setup of OpenAI + Gemini, rotating a leaked Suno key, verifying a freshly-pasted key, enabling Lyria gate.

## CONSTRAINTS

- **Values are masked in every output EXCEPT `export` without `--mask`.** Logs / list / add confirmation print `sk-pr…WXYZ` style only.
- **The file is chmod 600.** Skill enforces after every write.
- **Explicit shell exports win.** If the user has `export OPENAI_API_KEY=...` in their `.zshrc`, the file entry is ignored — by design.
- **Interactive `add` reads via `getpass`** — value not echoed to terminal or shell history.
- **Don't print full key in error messages.** Errors reference env var NAMES, not values.
- **`verify` uses lightweight HTTP probes** — costs $0, no generation. Only 9 providers covered (OpenAI, Gemini, Anthropic, BFL, Ideogram, Replicate, FAL, Runway, ElevenLabs). Suno / Kling / Lyria gate flags / S3 / SKILLS_* don't have verify — they show `unsupported`.
- **Network errors in verify** show as `unknown` — not a key problem.
- **Don't auto-purge invalid keys.** If verify reports invalid, the skill flags it but doesn't delete — the user might have just rotated the key in the vendor dashboard.
- **gate flags are NOT API keys.** Use `enable / disable` for them, not `add / remove`. The skill warns when you try to misuse.
- **`~/.skills.env` location is overrideable** via `SKILLS_KEYS_FILE=/custom/path`. Useful for CI (where home dir might be ephemeral) or multi-profile setups.
- **Never commit `~/.skills.env` to git.** The home-dir location avoids accidental commits. If someone wants the file elsewhere (project root), they MUST add it to `.gitignore`.
- **For CI / GitHub Actions: don't use this skill.** Use the platform's native secret management (`secrets.OPENAI_API_KEY`) which propagates to env vars. This skill is for local dev.

## INVOCATION HINTS

When the user says any of:
- "add my <provider> key", "store my OpenAI key", "save the Gemini key"
- "rotate the <provider> key", "update / change / swap the X key"
- "remove / delete the X key", "I leaked my Suno key, take it out"
- "list keys", "what keys do I have set", "which providers are configured"
- "verify my <provider> key", "test the OpenAI key", "is my key still valid"
- "enable Suno", "turn on Lyria", "disable Sora"
- "where do I put my keys", "where is the keys file"

RU triggers:
- «добавь ключ OpenAI», «сохрани Gemini-ключ»
- «обнови / поменяй / ротируй ключ X»
- «удали ключ X», «утёк Suno-ключ, убери»
- «покажи ключи», «какие ключи у меня заданы»
- «проверь ключ X», «работает ли OpenAI-ключ»
- «включи Suno», «выключи Lyria»
- «где хранятся ключи», «куда вставлять ключи»

Default subcommand if intent is ambiguous: `list` (safe — masks everything).

This is a meta-skill, sibling to `skills-update`. Both wrap `common/runners/cli/...` plumbing. Their outputs are not Claude-produced text — they're tool outputs to be relayed honestly.
