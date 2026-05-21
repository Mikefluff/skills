# skills-keys — detailed usage reference

What each subcommand does, exit codes, precedence rules.

---

## The file

- Default location: `~/.skills.env`
- Override: set `SKILLS_KEYS_FILE=/custom/path` in your shell BEFORE running
- Format: plain `KEY=VALUE` lines, one per line; blank lines + `# comments` ignored
- Permissions: chmod 600 (rw for user only). Skill enforces after every write.
- Atomicity: writes go through a temp file + rename. No partial-write state.

Example file:
```
OPENAI_API_KEY=sk-proj-...redacted...
GEMINI_API_KEY=AIza...redacted...
BFL_API_KEY=ec123...redacted...
SUNO_API_KEY=sk-1q...redacted...
SUNO_API_ENABLED=1

# Storage (optional)
S3_BUCKET=skills-generated
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
```

---

## Precedence

When a runner CLI starts, this happens in order:

1. Skill imports `keysfile.load_into_env(override=False)`.
2. For each entry in `~/.skills.env`:
   - If `os.environ[name]` is already set → SKIP (shell export wins).
   - Else → set `os.environ[name] = value`.
3. Providers check `os.environ` as usual.

**Implication**: an explicit `export OPENAI_API_KEY=...` in your `.zshrc` ALWAYS wins. The file is for keys you want managed independently of shell config. To force the file's value, edit your `.zshrc` to remove the export.

---

## `list`

```
skills-keys list
```

Output:
```
# /Users/.../.skills.env  (4 key(s))

  OPENAI_API_KEY            sk-p…WXYZ
  GEMINI_API_KEY            AIza…3def
  SUNO_API_KEY              sk-1…3def
  SUNO_API_ENABLED          1               [gate flag]

Use 'skills-keys verify' to ping providers.
```

Exit: 0 always.

---

## `add` / `update`

```
skills-keys add OPENAI_API_KEY sk-proj-...
skills-keys add OPENAI_API_KEY                   # interactive
```

Interactive prompt:
```
  value for OPENAI_API_KEY (not echoed):
```

Reads via `getpass` (TTY) or stdin line (when piped). Empty value → exit 2.

Output:
```
  ✓ Added OPENAI_API_KEY in /Users/.../.skills.env
    masked: sk-p…WXYZ
    Active in new Claude Code sessions, or run: source /Users/.../.skills.env
```

Exit: 0 on success, 2 on validation error (invalid env var name).

`update` is an alias for `add` — same behavior. Use whichever reads better in context.

### Gate flag shortcut

If the env var name is a known gate flag (`SUNO_API_ENABLED` / `LYRIA_API_ENABLED` / `OPENAI_SORA_API_ENABLED`) and no value is given, `add` defaults to `1`:

```
skills-keys add SUNO_API_ENABLED
# equivalent to: skills-keys add SUNO_API_ENABLED 1
```

---

## `remove`

```
skills-keys remove OPENAI_API_KEY
```

Output (key was present):
```
  ✓ Removed OPENAI_API_KEY from /Users/.../.skills.env
```

Output (key wasn't there):
```
  · OPENAI_API_KEY was not set — nothing to remove
```

Exit: 0 always (idempotent).

---

## `enable` / `disable`

Only operate on gate flags. Refuse to act on regular keys.

```
skills-keys enable SUNO_API_ENABLED
# ✓ Enabled SUNO_API_ENABLED=1 in ~/.skills.env

skills-keys disable LYRIA_API_ENABLED
# ✓ Disabled LYRIA_API_ENABLED (removed)
```

Known gate flags:
- `OPENAI_SORA_API_ENABLED`
- `LYRIA_API_ENABLED`
- `SUNO_API_ENABLED`

Trying to enable a non-gate var:
```
skills-keys enable OPENAI_API_KEY
# ! 'OPENAI_API_KEY' isn't a known gate flag. Use 'add' for general keys.
#   Known gate flags: LYRIA_API_ENABLED, OPENAI_SORA_API_ENABLED, SUNO_API_ENABLED
# exit 2
```

---

## `verify`

```
skills-keys verify                           # all supported providers
skills-keys verify OPENAI_API_KEY GEMINI_API_KEY  # specific
```

Output:
```
  ✓ OPENAI_API_KEY      valid        models endpoint OK
  ✓ GEMINI_API_KEY      valid        models endpoint OK
  ✗ BFL_API_KEY         invalid      HTTP 401
  ? RUNWAY_API_KEY      unknown      network error / timeout
  · SUNO_API_KEY        unsupported  no verify endpoint configured
  – ELEVENLABS_API_KEY  unset        no value
```

Status legend:
- `valid` — vendor endpoint returned 200 with the key
- `invalid` — vendor returned 401/403 (key is bad)
- `unknown` — network error / timeout / unexpected HTTP status — re-run later
- `unsupported` — no public verify endpoint configured for this provider
- `unset` — env var not set anywhere

Exit: 0 if no invalid found, 1 if any key returned `invalid`.

### Supported providers (v1)

| Env var | Probe endpoint |
|---|---|
| OPENAI_API_KEY | `GET https://api.openai.com/v1/models` |
| GEMINI_API_KEY | `GET https://generativelanguage.googleapis.com/v1/models?key=...` |
| ANTHROPIC_API_KEY | `GET https://api.anthropic.com/v1/models` |
| BFL_API_KEY | `GET https://api.bfl.ai/v1/get_result?id=test` |
| IDEOGRAM_API_KEY | `GET https://api.ideogram.ai/api/v1/styles` |
| REPLICATE_API_TOKEN | `GET https://api.replicate.com/v1/account` |
| FAL_KEY | `GET https://fal.run/health` |
| RUNWAY_API_KEY | `GET https://api.dev.runwayml.com/v1/tasks?limit=1` |
| ELEVENLABS_API_KEY | `GET https://api.elevenlabs.io/v1/user` |

Not yet supported (return `unsupported`):
- `SUNO_API_KEY` — no public verify endpoint
- `KLING_ACCESS_KEY_ID` + `KLING_ACCESS_KEY_SECRET` — requires JWT signing flow
- All `S3_*` keys
- All gate flags + `SKILLS_*` env vars

---

## `path`

```
skills-keys path
# /Users/.../.skills.env
```

Just prints the file path. Useful for scripting:

```bash
$(skills-keys path)        # → /Users/.../.skills.env
cat "$(skills-keys path)"  # inspect raw file (you'll see plaintext keys)
```

Exit: 0.

---

## `export`

```
skills-keys export
```

Output:
```
export OPENAI_API_KEY="sk-proj-..."
export GEMINI_API_KEY="..."
export SUNO_API_KEY="sk-..."
export SUNO_API_ENABLED="1"
```

Use to apply file changes to the current shell:

```bash
eval "$(skills-keys export)"
```

PLAINTEXT OUTPUT — only pipe to `eval`, don't share or commit.

### `--mask`

```
skills-keys export --mask
```

Same shape, values masked. For inspection / docs / sharing — NOT eval-able.

Output:
```
# Values masked — for inspection only. Use without --mask for eval.
export OPENAI_API_KEY="sk-p…WXYZ"
export GEMINI_API_KEY="AIza…3def"
```

---

## Programmatic API (`common.runners.keysfile`)

For scripts that want to integrate without going through the CLI:

```python
from common.runners import keysfile

# Read
entries = keysfile.read_all()                   # list[KeyEntry]
value = keysfile.get("OPENAI_API_KEY")           # str | None

# Write
keysfile.upsert("OPENAI_API_KEY", "sk-...")     # True if new, False if updated
keysfile.remove("OPENAI_API_KEY")                # True if removed, False if absent

# Load into env
n_loaded = keysfile.load_into_env()              # int; doesn't override existing
keysfile.load_into_env(override=True)            # forces file values

# Display helpers
keysfile.mask("sk-proj-abc...xyz")               # "sk-p…axyz"
keysfile.export_lines(mask_values=False)         # list[str] eval-ready
```

---

## Security posture

- **Plaintext at rest**: file is plain text. Anyone with read access to your home dir can read your keys. `chmod 600` protects from other users on a multi-user system.
- **No encryption**: trade-off vs. cross-platform simplicity. If you need encryption, use a real secret manager (1Password CLI, Bitwarden CLI, AWS Secrets Manager) and `export` from there into your shell.
- **No audit log**: skill doesn't track who edited the file when. If you need that, use a real secret manager.
- **Backups**: if your dotfiles are backed up to cloud storage (iCloud / Dropbox / etc), `~/.skills.env` goes with them. To exclude, move via `SKILLS_KEYS_FILE` env var.
- **CI**: don't use this skill in CI. Use the platform's native secret management.

---

## Common workflows

### First-time setup (3 keys)

```
skills-keys add OPENAI_API_KEY sk-proj-...
skills-keys add GEMINI_API_KEY AIza...
skills-keys add BFL_API_KEY ec...
skills-keys verify          # confirm all 3 work
```

### Rotate a leaked key

```
# In the vendor dashboard: revoke the old key, generate a new one.
skills-keys update OPENAI_API_KEY sk-proj-new...
skills-keys verify OPENAI_API_KEY  # confirm new key works
# Restart Claude Code so new key loads into the session.
```

### Enable a paid premium provider

```
skills-keys add SUNO_API_KEY sk-suno-...
skills-keys enable SUNO_API_ENABLED       # required to actually call Suno
skills-keys verify SUNO_API_KEY            # returns 'unsupported' — Suno has no verify endpoint
```

### Apply changes without restarting Claude Code

```
eval "$(skills-keys export)"
# All keys loaded into current shell. Next Claude Code session inherits.
```

### Audit what's set

```
skills-keys list             # masked overview
skills-keys verify           # validation status for each
skills-keys export --mask    # inspection-ready summary
```
