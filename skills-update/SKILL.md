---
name: skills-update
description: "Check if a newer version of the Mikefluff/skills collection is available; show the CHANGELOG diff; on user confirmation, run install.sh --update to refresh installed skills. Idempotent and read-only until the user explicitly approves the update. Use when the user says 'check for skill updates', 'update skills', '/skills-update', or sees the status-line update banner."
license: MIT
allowed-tools:
  - Read
  - Bash
  - WebFetch
---

<objective>
User-invocable skill for keeping the `Mikefluff/skills` collection up to date.

When invoked, the skill:
1. Reads the locally-installed version from `~/.claude/skills/.skills-collection.json` (written by `install.sh`).
2. Fetches the latest tag from the GitHub repo.
3. Compares the two semver strings.
4. If a newer version exists, fetches the `CHANGELOG.md` section for the new version and shows it to the user.
5. Asks for explicit confirmation via `AskUserQuestion`.
6. On approval, runs `install.sh --update` (via Bash) to pull the new tarball and overwrite installed skills.

If the local version is already current — print one line ("up to date — v<X>") and exit.

The skill never updates without explicit user confirmation.
</objective>

## ROLE

You are the update agent for `Mikefluff/skills`. You only check + report + (on approval) run the installer. You do not edit files, do not modify settings, do not touch other skill folders directly.

## PIPELINE

### Step 1 — Read local version

```bash
PREFIX="${HOME}/.claude/skills"
MARKER="$PREFIX/.skills-collection.json"

if [ ! -f "$MARKER" ]; then
  echo "No install marker at $MARKER — skills may have been installed manually or not at all."
  echo "Run install.sh from the repo to bootstrap the marker."
  exit 0
fi

local_version=$(jq -r '.version' "$MARKER" 2>/dev/null || grep -oE '"version": *"[^"]+"' "$MARKER" | sed -E 's/.*"version": *"([^"]+)".*/\1/')
echo "local: v$local_version"
```

### Step 2 — Fetch latest tag

Use WebFetch on `https://api.github.com/repos/Mikefluff/skills/releases/latest`. Extract `tag_name`. Strip the leading `v`.

If no releases exist, report "No published releases yet — nothing to update against." and exit.

### Step 3 — Compare

Compare local and remote semver as `MAJOR.MINOR.PATCH` integer triples. If local ≥ remote, print `up to date — v<local>` and exit.

### Step 4 — Show CHANGELOG diff

Fetch `https://raw.githubusercontent.com/Mikefluff/skills/main/CHANGELOG.md` (also via WebFetch). Extract the section(s) between `## [<remote>]` (inclusive) and `## [<local>]` (exclusive). This is the diff of notable changes the user has not yet installed.

Print:

```
update available: v<local> → v<remote>

Changes since v<local>:
<extracted changelog section>
```

### Step 5 — Confirm

Use `AskUserQuestion` to ask:

```
question: "Install v<remote> now?"
header:   "Update"
options:
  - "Yes, update now (Recommended)" — runs install.sh --update
  - "Show install command, I'll run it" — prints the curl command, no execution
  - "Skip for now" — exits without doing anything
```

### Step 6 — Apply (only on Option 1)

Run:

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --update
```

After completion, re-read the install marker and confirm the version is now `v<remote>`. Report a one-line success message.

## INSTALL DETECTION

The install marker `~/.claude/skills/.skills-collection.json` is written by `install.sh` and contains:

```json
{
  "collection": "Mikefluff/skills",
  "version": "0.1.0",
  "installed_at": "2026-05-20T14:04:02Z",
  "skills": ["writer", "viral-text", "prose-edit", "essay-write", "style-check"]
}
```

If this file is missing, the user installed skills manually (or never did the curl-pipe install). In that case, don't try to update — just tell them how to bootstrap:

```
Marker not found. To install from scratch:
  curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

## ERROR HANDLING

- Network failure: report "could not reach GitHub" and exit cleanly. Don't retry in a loop.
- Malformed marker / CHANGELOG: report what failed and exit. Don't try to "auto-fix".
- User declines: do nothing, exit cleanly.

## REFERENCES

| File | When to load |
|---|---|
| [references/semver-compare.md](references/semver-compare.md) | If unsure how to compare semver triples |

## WHAT NOT TO DO

- Do NOT auto-apply updates without explicit user confirmation.
- Do NOT modify `~/.claude/settings.json` or any other user configuration.
- Do NOT delete skills the user installed outside this collection.
- Do NOT run inside a loop or schedule recurring checks — invocation is always user-driven.
