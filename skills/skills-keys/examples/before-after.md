# skills-keys — example sessions

4 realistic sessions showing how to use the skill end-to-end.

---

## Example 1 — First-time setup

### User says

> Add my OpenAI key. It's sk-proj-abc123def456.

### What happens

Claude invokes:
```
~/.claude/skills/skills-keys/scripts/run.py add OPENAI_API_KEY sk-proj-abc123def456
```

Output:
```
  ✓ Added OPENAI_API_KEY in /Users/.../.skills.env
    masked: sk-p…f456
    Active in new Claude Code sessions, or run: source /Users/.../.skills.env
```

### Follow-up

Claude offers: "Want me to verify the key works against OpenAI's API?"

> Yes

```
~/.claude/skills/skills-keys/scripts/run.py verify OPENAI_API_KEY
```

```
  ✓ OPENAI_API_KEY  valid  models endpoint OK
```

### What to notice

- The key value is masked in confirmation output.
- The full key never appears in conversation transcript after this point.
- Verify is offered automatically — first thing after adding.

---

## Example 2 — Rotate a leaked key

### User says

> I accidentally committed my Suno key to a public repo. Rotate it.

### What happens

Claude:
1. Suggests revoking the old key in Suno's dashboard FIRST. (This skill can't revoke remote keys.)
2. Once user has the new key, runs:
   ```
   ~/.claude/skills/skills-keys/scripts/run.py update SUNO_API_KEY
   ```
3. Prompts user interactively (silent stdin) so the new key doesn't go into shell history:
   ```
     value for SUNO_API_KEY (not echoed): _
   ```
4. User pastes new key, presses enter.
5. Output:
   ```
     ✓ Updated SUNO_API_KEY in /Users/.../.skills.env
       masked: sk-2…xyz9
       Active in new Claude Code sessions, or run: source /Users/.../.skills.env
   ```

### Verify offer

```
~/.claude/skills/skills-keys/scripts/run.py verify SUNO_API_KEY
```

```
  · SUNO_API_KEY  unsupported  no verify endpoint configured
```

Claude explains: "Suno doesn't expose a verify endpoint. The first generation call will tell you if the new key works. Try `music-prompt --execute --model suno-v5-5 --prompt 'test'` to confirm."

### What to notice

- Interactive (silent) input prevents key from leaking via terminal history.
- Some providers (Suno, Kling) don't have verify endpoints — skill is honest about it.
- The leaked-key remediation chain is: revoke remote → update local → confirm via a real call.

---

## Example 3 — Audit what's set

### User says

> Show me which keys I have set and whether they still work.

### What happens

Claude runs two commands:

```
~/.claude/skills/skills-keys/scripts/run.py list
```

```
# /Users/.../.skills.env  (8 key(s))

  OPENAI_API_KEY            sk-p…f456
  GEMINI_API_KEY            AIza…3def
  BFL_API_KEY               ec12…e89z
  REPLICATE_API_TOKEN       r8_a…2xyz
  RUNWAY_API_KEY            rw_x…9abc
  SUNO_API_KEY              sk-2…xyz9
  SUNO_API_ENABLED          1                [gate flag]
  S3_BUCKET                 skills-generated

Use 'skills-keys verify' to ping providers.
```

Then:

```
~/.claude/skills/skills-keys/scripts/run.py verify
```

```
  ✓ OPENAI_API_KEY      valid        models endpoint OK
  ✓ GEMINI_API_KEY      valid        models endpoint OK
  ✓ BFL_API_KEY         valid        HTTP 404 (key authenticated)
  ✓ REPLICATE_API_TOKEN valid        account endpoint OK
  ✗ RUNWAY_API_KEY      invalid      HTTP 401
  · SUNO_API_KEY        unsupported  no verify endpoint configured
  – IDEOGRAM_API_KEY    unset        no value
  – FAL_KEY             unset        no value
  – ANTHROPIC_API_KEY   unset        no value
  – ELEVENLABS_API_KEY  unset        no value
```

### Claude's summary

> 5 keys set + 1 gate flag.
> - **Working**: OpenAI, Gemini, BFL, Replicate.
> - **BROKEN**: Runway returned 401. The key may have been rotated or revoked — generate a new one in the Runway dashboard and run `skills-keys update RUNWAY_API_KEY <new>`.
> - **Unsupported**: Suno (no verify endpoint — test with a real call).
> - **Unset**: Ideogram, FAL, Anthropic, ElevenLabs (these aren't required for the providers you're using).

### What to notice

- One quick scan: what's set, what's working, what's broken.
- Invalid keys are highlighted but NOT auto-deleted (user might be mid-rotation).
- Unset != broken — just informational.

---

## Example 4 — Enable a paid gate

### User says

> I just signed up for Lyria 3 Pro. Enable it.

### What happens

Claude runs:

```
~/.claude/skills/skills-keys/scripts/run.py enable LYRIA_API_ENABLED
```

```
  ✓ Enabled LYRIA_API_ENABLED=1 in /Users/.../.skills.env
```

### Confirm setup

Claude checks the prerequisites:

```
~/.claude/skills/skills-keys/scripts/run.py verify GEMINI_API_KEY
```

```
  ✓ GEMINI_API_KEY  valid  models endpoint OK
```

> Lyria 3 Pro uses your Gemini API key for auth and the LYRIA_API_ENABLED gate to prevent accidental spend. Both are set now. You can call it via `reel-builder --music-provider lyria-3-pro --execute` or `music-prompt --execute --model lyria-3-pro`.

### What to notice

- Gate flags are distinct from API keys but managed via the same skill.
- Enable + verify the underlying API key together — the gate flag alone doesn't authenticate.
- Skill explains the WHY: paid premium, anti-accidental-spend.

---

## Anti-pattern (don't do this)

### Pasting a key in plaintext into the conversation

Don't:

> Set my OpenAI key to sk-proj-abc123def456ghi789.

(The key now lives in the conversation transcript forever.)

Better:

> Add my OpenAI key. I'll paste it when prompted.

Claude runs `skills-keys add OPENAI_API_KEY` (no value), which triggers the silent interactive prompt. The key never enters the conversation transcript.

### Using `export` output for logging

Don't:

> Run `skills-keys export` and save the output to keys-backup.txt.

(Now the unmasked keys are sitting in a file no one will remember to delete.)

Better:

> Run `skills-keys export --mask` for a snapshot. For backup of actual values, use a real secret manager (1Password / Bitwarden) and store there.
