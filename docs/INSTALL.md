# Install

Pick the install method that fits your environment. All paths land at the same destination: skills copied into `~/.claude/skills/` where Claude Code auto-discovers them on next session start.

## Curl (recommended for most users)

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

What it does:

1. Downloads the latest release tarball from GitHub
2. Verifies the `skills.json` manifest
3. Copies every skill folder into `~/.claude/skills/<skill>/`
4. Copies `common/references/` into `~/.claude/skills/common/references/`
5. Writes `~/.claude/skills/.skills-collection.json` (install marker)
6. Prints next-steps banner

No external dependencies. Works on macOS + Linux. `bash` and `python3` (for the writer linter) only.

### Custom prefix

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --prefix /opt/skills
```

### Subset install

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --skills writer,viral-text,landing-copy
```

## npm

```bash
npm install -g @mikefluff/skills
skills install                 # copies skills into ~/.claude/skills
skills update                  # later, to refresh
skills uninstall               # removes everything
```

The `skills` binary is a thin wrapper around the same `install.sh`. The package bundles the full collection, so npm install does NOT touch `~/.claude/skills/` automatically — you opt in with `skills install`.

## Homebrew

```bash
brew tap mikefluff/tap https://github.com/Mikefluff/homebrew-tap
brew install mikefluff/tap/skills
skills install                 # copies skills into ~/.claude/skills
```

The formula bundles the repo under `$(brew --prefix)/Cellar/skills/.../libexec/` and exposes a `skills` binary. Run `skills install` to populate `~/.claude/skills/`. To update Homebrew after a new release:

```bash
brew upgrade mikefluff/tap/skills
skills update
```

## Docker (for CI / one-off lint)

```bash
docker pull ghcr.io/mikefluff/skills:latest

# Lint a single file
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work/draft.md

# Lint everything under examples/
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint-all /work

# Validate the manifest (useful in collection-development workflows)
docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills validate
```

Image tags:

- `:latest` — most recent release
- `:1.8.1`, `:1.8`, `:1` — specific version pins
- `:main` — head of main branch (avoid in production CI)

Multi-arch image is built for both `linux/amd64` and `linux/arm64`.

## Manual

```bash
git clone https://github.com/Mikefluff/skills.git
cd skills
bash install.sh --copy-from .
```

Useful when you want to:

- Run from a local checkout for development
- Modify references/ files locally before installing
- Audit what's being copied before any system change

## Verification

After any install method, verify:

```bash
ls ~/.claude/skills                          # should list 44 skill folders + common/
cat ~/.claude/skills/.skills-collection.json # marker with version + skill list
```

In Claude Code, ask `what skills are available?` — the 44 skills appear in the response.

## Updates

```bash
# Via curl
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --update

# Via npm
skills update

# Via Homebrew
brew upgrade mikefluff/tap/skills && skills update

# Inside Claude Code
/skills-update                # checks GitHub for new release, asks before applying
```

## Uninstall

```bash
# Via curl
bash install.sh --uninstall

# Via npm
skills uninstall && npm uninstall -g @mikefluff/skills

# Via Homebrew
skills uninstall && brew uninstall mikefluff/tap/skills

# Manual
rm -rf ~/.claude/skills
```

## Troubleshooting

**Claude Code doesn't see the skills after install.**

Restart the Claude Code session. Skill discovery happens on session start.

**`python3` not found when running the writer linter.**

The linter needs Python 3.10+. Install via `brew install python@3.12` (macOS) or your distro's package manager (Linux). The wrappers don't need a local Python — they run inside Claude Code.

**Permission denied writing to `~/.claude/skills/`.**

```bash
mkdir -p ~/.claude/skills && chown -R "$USER" ~/.claude
```

**`install.sh` fails with `jq: command not found`.**

`jq` is preferred but optional — install.sh falls back to `grep`-based parsing. If you see the error, your install.sh is older than v1.2.0; pull latest.

**Docker image fails with `permission denied` on the volume mount.**

Common on Linux SELinux systems. Add `:Z` to the volume flag:

```bash
docker run --rm -v "$PWD:/work:Z" ghcr.io/mikefluff/skills lint /work/draft.md
```

**Want the optional status-line update banner (announces new releases inside Claude Code)?**

```bash
bash scripts/install-hook.sh
```

Idempotent. Caches the remote tag for 24h.

**Want a local pre-commit hook for the writer linter?**

```bash
bash scripts/install-precommit-hook.sh
# Or: make install-precommit-hook
```

Installs `.git/hooks/pre-commit` that lints staged `.md` files and runs `make smoke` before each commit. Bypass once with `git commit --no-verify`. Calibration files (`*/examples/before-after.md`, anti-pattern catalogues, `CHANGELOG.md`) are skipped because they intentionally quote banned patterns.
