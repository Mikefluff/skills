# Troubleshooting

Known failure modes and how to fix them. Symptom → diagnosis → fix.

If your problem isn't listed, search [open issues](https://github.com/Mikefluff/skills/issues) before opening a new one — duplicates are common.

---

## Install / update

### Symptom: `curl ... | bash` fails with "could not resolve latest release tag"

**Diagnosis.** GitHub API is unreachable from your network, OR the repository has no published releases.

**Fix.** Check connectivity to `api.github.com`:

```bash
curl -fsSL https://api.github.com/repos/Mikefluff/skills/releases/latest
```

If that hangs or 404s, either your network is blocking GitHub or someone has deleted all releases (unlikely). Workaround: install from a local checkout:

```bash
git clone https://github.com/Mikefluff/skills /tmp/skills
bash /tmp/skills/install.sh --copy-from /tmp/skills
```

---

### Symptom: `install.sh` says "missing required command: jq"

**Diagnosis.** `jq` is preferred for parsing `skills.json` but the installer has a `grep`-based fallback. The error means `tar` or `curl` is missing — those are not optional.

**Fix.**

```bash
# macOS
brew install curl

# Debian/Ubuntu
sudo apt-get install -y curl tar
```

`jq` is nice-to-have but not strictly required — install if you want sharper error messages.

---

### Symptom: install succeeds but Claude Code doesn't see the skills

**Diagnosis.** Three likely causes.

1. **Wrong prefix.** Default is `~/.claude/skills/`. Verify:
   ```bash
   ls ~/.claude/skills/
   ```
   If the skills aren't there, you probably installed to a different prefix. Re-install without `--prefix`.

2. **Claude Code session predates install.** Skills are scanned at session start. Restart Claude Code.

3. **Frontmatter corrupted.** Run validation:
   ```bash
   cd path/to/skills/checkout && bash scripts/validate.sh
   ```
   If something's malformed, the skill won't load. Re-install with `--update`.

---

### Symptom: `--update` doesn't actually update

**Diagnosis.** Either you're already at the latest version, or the installer is being conservative (it does not overwrite a skill unless `--update` is explicitly passed).

**Fix.**

```bash
bash install.sh --check                                 # confirm there's a newer version
bash install.sh --update                                # actually update
bash install.sh --update --prune                        # also remove skills removed upstream
```

---

## Status-line banner

### Symptom: banner never appears even though I know an update exists

**Walk down this list:**

1. **Did you install the hook?** The default `install.sh` does NOT install the status-line hook (we don't touch `~/.claude/settings.json` without opt-in). Install it once:
   ```bash
   bash scripts/install-hook.sh
   ```

2. **Is Node.js installed?** The hook is a Node script. `node --version` should print 18+. If missing, install from your package manager or nodejs.org.

3. **Is `~/.claude/settings.json` valid JSON?** Catch silent errors:
   ```bash
   python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))"
   ```
   If it errors, fix the JSON, then re-run `bash scripts/install-hook.sh`.

4. **Is the marker file present?** The banner needs `~/.claude/skills/.skills-collection.json`. If you installed by symlink instead of by `install.sh`, the marker doesn't exist, and the banner silently passes through.
   ```bash
   cat ~/.claude/skills/.skills-collection.json
   ```
   If missing: `bash install.sh --copy-from /path/to/repo --update`.

5. **Is the cache stale?** The banner caches the remote tag for 24 hours.
   ```bash
   rm /tmp/skills-update-banner-cache.json
   ```
   The next status-line refresh will re-fetch.

6. **Did the network call time out?** The banner has a 1.5s timeout. On slow networks it silently fails open. Try again on a faster connection or remove the cache (above) and check `curl -m 5 https://api.github.com/repos/Mikefluff/skills/releases/latest`.

---

### Symptom: banner shows weird characters / overflows my status line

**Diagnosis.** The banner is capped at ~80 chars but your terminal may be narrower. Or your status line is already long.

**Fix.** Either widen the terminal or uninstall the banner and rely on `/skills-update` invocations:

```bash
bash scripts/install-hook.sh --uninstall
```

---

## `skills-update` skill

### Symptom: `/skills-update` says "not installed"

**Diagnosis.** No marker file at `~/.claude/skills/.skills-collection.json`. Means you installed by hand (symlink, manual copy), not via `install.sh`.

**Fix.**

```bash
# from your repo checkout:
bash install.sh --copy-from . --update          # writes the marker
```

After this, `/skills-update` will work normally.

---

### Symptom: `/skills-update` says "could not reach GitHub"

**Fix.** Same as for installer connectivity issues — verify `api.github.com` is reachable, retry later. Errors here are transient.

---

## Linter (`skills/writer/scripts/lint.py`) false positives

### Symptom: linter flags an idiom as DOUBLE_NEG_REGEX

**Diagnosis.** Some Russian negative idioms naturally trip the regex (`без сучка без задоринки`, `ни рыба ни мясо`, `не больше и не меньше`, `ни сном ни духом`).

**Fix.** These are documented exceptions in `skills/writer/references/structural-prose.md`. The regex catches them; the LLM pass should pass them through. If a wrapper (`prose-edit` etc.) is rewriting them anyway, that's a bug — file it with the exact fragment.

For the standalone linter (`python3 lint.py file.md`), false positives in this category are accepted as the cost of high recall. Don't try to make the regex case-by-case smart.

---

### Symptom: linter flags a literal physical "нерв" (anatomy) or "трещина" (physical crack) as NEURAL_METAPHOR

**Diagnosis.** Cat 22 (NEURAL_METAPHOR) covers метафорическое использование — literal physical use is intended to be allowed, but pure regex can't disambiguate.

**Fix.** When you invoke `prose-edit` or `essay-write`, the LLM pass should recognize the literal sense and skip. If the wrapper rewrites a legitimate literal use, file a bug with the fragment.

For standalone offline linter — accept the false positive (the linter is a pre-check, not the final word).

---

### Symptom: linter triggers on every fixture, even clean prose

**Diagnosis.** Probably you broke `lint.py` in a fork or local edit.

**Fix.** Regenerate from upstream:

```bash
bash install.sh --update                    # re-pull writer
bash tests/run.sh                           # confirm fixtures still match snapshots
```

If snapshots also drift, you've intentionally changed the linter — re-baseline with `bash tests/run.sh --update`.

---

## CI / shellcheck / markdownlint failures in your fork

### Symptom: my fork's CI fails on markdownlint right after I add a new doc

**Diagnosis.** New file probably has a markdownlint rule violation that the existing files don't. Check the failed CI logs.

**Fix.** Run the linter locally:

```bash
npx -y markdownlint-cli2@0.13.0 "**/*.md" "#node_modules/**" "#.git/**"
```

Fix what it reports. If the violation is genuinely fine for your style (e.g. you intentionally use underscored emphasis), disable that rule in `.markdownlint.json` (the repo already disables ~14 cosmetic rules — see what's there).

---

### Symptom: shellcheck fails on a script I added

**Diagnosis.** Real bug or false positive. Read the diagnostic — shellcheck's messages link to detailed rule explanations.

**Fix.** If real: fix the code. If false positive: add `# shellcheck disable=SCxxxx  # rationale: ...` annotation. Don't blanket-disable rules.

---

### Symptom: docs-consistency check fails ("skill X in skills.json not in README")

**Diagnosis.** You added a skill to `skills.json` but didn't regenerate the README table.

**Fix.**

```bash
python3 scripts/gen-skills-table.py --write
git add README.md
git commit --amend --no-edit                # if same PR
# or
git commit -m "docs: regen README skills table"
```

The CI gate exists specifically to catch this.

---

### Symptom: docs-consistency check fails ("new skill not mentioned in CHANGELOG [Unreleased]")

**Diagnosis.** You added a skill folder but didn't write a `[Unreleased]` entry.

**Fix.** Add a short bullet to the `[Unreleased]` section of `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added — new skills
- **`my-new-skill`** (wrapper). One-line description. Composes with X / Y.
```

The release workflow promotes whatever's in `[Unreleased]` into the new versioned section, so this is also what becomes your release notes.

---

## Pre-commit hook

### Symptom: hook runs but never blocks

**Diagnosis.** Either no BLOCKING-severity findings in the diff (good — that's the design), or the hook's exit-code logic is broken in your fork.

**Fix.** Test the hook manually:

```bash
bash .git/hooks/pre-commit; echo "exit=$?"
```

Exit codes: `0` = pass, `1` = WARNING (prompt or pass-with-warning depending on your hook script), `2` = BLOCKING (abort).

If you get `0` even when you expect `2`, your hook script isn't propagating the linter's exit code — see the [pre-commit walkthrough](walkthroughs/pre-commit-hook.md) for the canonical pattern.

---

### Symptom: hook is too slow

**Diagnosis.** You're invoking Claude Code from the hook, which has a multi-second cold-start.

**Fix.** Use the offline-only fallback variant from the [pre-commit walkthrough](walkthroughs/pre-commit-hook.md). It runs `python3 skills/writer/scripts/lint.py` on staged diff, which is <100ms.

You lose the wrapper rules (prose-edit / essay-write specifics) but keep the 23-category regex pass — which catches most issues anyway.

---

### Symptom: hook fails on macOS bash 3.2

**Diagnosis.** macOS ships bash 3.2.57; some hook templates from the wider internet use bash 4 features.

**Fix.** Use the pre-commit script from [pre-commit walkthrough](walkthroughs/pre-commit-hook.md) — it's tested on bash 3.2 (no `mapfile`, no `<<<` in pipes, no `${var,,}`).

If you wrote your own hook, replace bash-4-isms or change the shebang to `#!/usr/bin/env bash` and install bash 5: `brew install bash`.

---

## Cross-skill issues

### Symptom: `prose-edit` rewrites a fragment in a way I disagree with

**Diagnosis.** The skill is opinionated — it has explicit voice rules.

**Fix.** Three options:

1. **Reject the diff.** `prose-edit` returns a *proposed* diff for you to accept/reject. If a rewrite breaks your intent, reject it.
2. **Pass `--conservative`** (if available — see `skills/prose-edit/SKILL.md` MODES) to apply only structural-synthetics fixes, no voice-level edits.
3. **Override the rule.** If you consistently disagree with a rule, edit the corresponding `skills/prose-edit/references/<rule>.md` locally (survives until `--update`). For a durable change, open a PR.

---

### Symptom: `canon-check` flags everything as WARNING — no story bible yet

**Diagnosis.** The skill greps entities and looks them up in a story bible. If there's no bible, every entity is flagged as a new one (WARNING by design — author should add it).

**Fix.** Either populate `notes/story-bible.md` (or wherever your bible lives) with the existing characters / artifacts / locations, or use `/canon-check entity <book> <name>` to inspect a single entity without bible cross-reference.

---

### Symptom: `translation-sync` produces empty / nonsense parity report

**Diagnosis.** Most likely the path patterns in `skills/translation-sync/references/checklist.md` don't match your repo layout. Default examples are illustrative.

**Fix.** Edit your local `skills/translation-sync/references/checklist.md` to reference your actual paths (`<your-repo>/ru/ch07.md`, etc.). For a durable change, fork + PR.

---

## When all else fails

1. Re-install fresh:
   ```bash
   bash install.sh --uninstall --yes
   rm -f ~/.claude/skills/.skills-collection.json
   bash install.sh                                          # latest release
   ```

2. Compare with a known-good version:
   ```bash
   bash install.sh --version 1.0.1                          # specific tag
   ```

3. File a bug. Include:
   - Output of `bash install.sh --check`
   - Output of `bash scripts/validate.sh`
   - Output of `bash scripts/smoke.sh`
   - The exact command / prompt that misbehaved
   - The unexpected output (or screenshot if the issue is in Claude Code's UI)
