# skills-update — example update flow

## Local marker (written by `install.sh`)

`~/.claude/skills/.skills-collection.json` after a fresh install:

```json
{
  "collection": "Mikefluff/skills",
  "version": "1.6.0",
  "installed_at": "2026-05-15T10:23:14Z",
  "skills": [
    "writer",
    "viral-text",
    "prose-edit",
    "essay-write",
    "style-check",
    "translation-sync",
    "canon-check",
    "pelevin-digression",
    "skills-update",
    "tone-shifter",
    "cold-email",
    "image-prompt",
    "video-prompt",
    "microcopy",
    "release-notes",
    "rfc-writer",
    "landing-copy"
  ]
}
```

## Update flow

User: `/skills-update`

Skill:
1. Reads `~/.claude/skills/.skills-collection.json` → local version `1.6.0`
2. Fetches latest release tag via GitHub API → remote `1.7.0`
3. Fetches CHANGELOG.md section for v1.7.0
4. Renders diff summary:

```
Current: v1.6.0 (installed 2026-05-15)
Available: v1.7.0 (released 2026-05-20)

What's new in v1.7.0:
- 9 per-skill snapshot fixtures added (test parity for all 17 skills)
- 8 dedicated walkthroughs (tone-shift, cold-email-pitch, image-prompt-cover,
  video-prompt-reel, microcopy-error-states, release-notes-saas,
  rfc-architecture, landing-launch)
- RU паритет for 7 EN-only skills (cold-email, image-prompt, video-prompt,
  microcopy, release-notes, rfc-writer, landing-copy)
- COMPOSING.md rewritten as 14 named workflow recipes
- skills-update gets examples/

Apply v1.7.0? [Y/n]
```

5. On `Y` (or empty): runs `bash install.sh --update`
6. On `n`: prints "Skipped — re-run /skills-update when ready."
7. On `q` / `Ctrl-C`: graceful abort, no changes

## Failure modes

| Cause | Skill behavior |
|---|---|
| Network unreachable | Print "Could not reach api.github.com — try again later"; no changes |
| GitHub rate-limited (60/hr unauth) | Print "Rate-limited; wait an hour or use `bash install.sh --check`"; no changes |
| Local marker missing | Print "Not installed via install.sh. Run `bash install.sh --copy-from <repo>` first"; no changes |
| Already at latest | Print "Up to date at v1.7.0"; no changes |
| Update fails mid-install | install.sh handles atomicity; skills-update reports the install.sh exit code |

## Cache behavior

skills-update does NOT cache anything (each invocation re-checks via API). The optional status-line banner (separate from this skill, see `scripts/install-hook.sh`) DOES cache the remote tag for 24h to avoid hammering the API.
