# FAQ

The questions that get asked first.

If your question isn't here, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue with the bug-report template.

---

## What is this collection for, in one line?

Editing prose (Russian or English) inside Claude Code without your output reading like LLM output. Plus a few related tools: viral-post generator, fiction/non-fiction wrappers, story-bible auditor, multilingual translation parity checker.

---

## Do I need to install all 9 skills?

No. Install a subset:

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --skills writer,viral-text
```

The wrappers (`viral-text`, `prose-edit`, `essay-write`, `pelevin-digression`) **do** need `writer` installed — they invoke it as their final pass. Linters (`style-check`, `translation-sync`, `canon-check`) are standalone. `skills-update` is standalone.

If you skip a wrapper's dep, the wrapper will fail at runtime with a clear "missing dependency: writer" message. Easier to just install all 9 and ignore what you don't use — they're plain markdown, near-zero cost on disk.

---

## Can I use this without speaking Russian?

Yes — the base linter (`writer`) covers EN as well as RU, with most rules being language-neutral. The structural-synthesis rules (staccato, double-negation, comma-stitching, etc.) and AI-style patterns (intensifiers, pseudo-causal bridges, balance hedges) apply equally to English prose.

The wrappers (`prose-edit`, `essay-write`) and `viral-text` are mostly English-capable but were calibrated against Russian fiction / non-fiction. Output quality in EN is fine; the *examples* in their `references/` are mostly Russian.

`translation-sync` is by design multilingual (RU / EN / PT-BR). If you only edit one language, use `style-check` instead.

---

## Does this leak my prose to any third party?

The skills run **entirely inside Claude Code on your machine**. Your text goes to Anthropic's API (because that's how Claude Code works in general — no special channel for these skills), and the standard Anthropic data-use policy applies. No third-party services.

Two skills make outbound network calls *to GitHub only*, and only when you invoke them:

1. `skills-update` — fetches the latest release tag and CHANGELOG to compare against your local marker
2. `hooks/skills-update-banner.js` (only if you opted in via `bash scripts/install-hook.sh`) — fetches the latest release tag every 24 hours and caches the result locally

If you want to disable the banner's network call entirely, just don't install it (`scripts/install-hook.sh` is opt-in; default install doesn't touch your `~/.claude/settings.json`).

`viral-text` and `essay-write` use Claude Code's `WebSearch` tool — same network constraints as Claude Code itself.

---

## How do I uninstall?

```bash
bash install.sh --uninstall              # interactive with [y/N]
bash install.sh --uninstall --yes        # scriptable
```

Or by hand:

```bash
rm -rf ~/.claude/skills/{writer,viral-text,prose-edit,essay-write,style-check,translation-sync,canon-check,pelevin-digression,skills-update}
rm -f  ~/.claude/skills/.skills-collection.json
```

If you installed the status-line banner, also: `bash scripts/install-hook.sh --uninstall`.

---

## Why so many skills instead of one big one?

Two reasons.

**Discovery.** Claude Code matches a skill to a user request via the skill's `description:` field. A single "edit prose" skill would match almost any text task, even when the user wanted something narrow ("make this viral" or "verify the translation parity"). Splitting lets each skill have a sharp, discriminating description.

**Composition.** Different tasks need different rule layers. Viral posts need hooks + 41 viral rules; fiction needs voice rules + canon check; non-fiction needs sources + V/H/P markers. Stacking them as wrappers around a shared base (`writer`) keeps each one focused while sharing the heavy regex / typography pass.

If you have a use case that none of the 9 fits, the right answer is usually a new skill, not bloating an existing one. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Can I use a wrapper without the `writer` final pass?

Not by design. The contract of every wrapper is "output is ready to ship" — that means the `writer` pass has run. If you want pre-cleanup raw output, you probably want `writer clean` directly with your text, then layer voice rules manually.

---

## What if the linter false-positives on legitimate prose?

The 23-category regex linter is high-recall by design — it's a pre-check, not the final word. False positives mostly come from:

1. **Idioms** (`"ни рыба ни мясо"` triggers DOUBLE_NEG_REGEX) — there's an explicit exception list in `writer/references/structural-prose.md` for these. If you find more, open a PR adding them.
2. **Technical terms** (`"нерв"` in anatomical context) — the cat 22 NEURAL_METAPHOR rules document the literal-vs-metaphorical distinction. Pass through context to Claude when in doubt.
3. **Anaphora / lestnichny accord / mantra** — `essay-write/references/structural-synthesis-keepers.md` lists the 7 patterns where parallelism is a device, not nyeyroslop. The structural detector should skip these.

If the linter still fires on something that's clearly fine, file a bug with the exact fragment — the regex needs tightening.

---

## How do I add my own rules / calques / banned constructions?

Two paths:

**A. Local override.** Edit the relevant file in `~/.claude/skills/<skill>/references/` after install. Your changes survive until the next `--update`, which overwrites them. Not durable.

**B. Upstream contribution.** Fork the repo, add your rules to the right `references/*.md` file, open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md). This is the right answer if your rule benefits other users.

Local-only project rules (e.g. project-specific terminology canon for `translation-sync`) usually go in option A — they're yours alone.

---

## What happens if the GitHub API is rate-limited?

`skills-update` and the banner hook silently fall back: banner shows nothing, `skills-update` prints "could not reach GitHub — try again later". Both fail open — your normal Claude Code session is unaffected.

If you hit GitHub's unauthenticated 60-req/hr limit (rare for personal use), wait an hour, or check via `bash install.sh --check` (which uses the same endpoint).

---

## Is it safe to pipe the installer from curl?

Yes — but verify if you're paranoid:

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh -o /tmp/install.sh
less /tmp/install.sh                    # read it
bash /tmp/install.sh
```

The installer is pure bash, ~280 lines, well-commented, and does only: enumerate skills from `skills.json`, `cp -R` each skill into `~/.claude/skills/`, write a marker JSON. No `sudo`, no system writes outside `~/.claude/skills/`, no third-party downloads (only the GitHub release tarball).

The same script lives at `install.sh` in the repo — pin a specific version if you want reproducibility: `bash install.sh --version 1.0.1`.

---

## Status-line banner doesn't show. Am I doing something wrong?

Likely one of:

1. **Banner needs Node.js installed locally** — the hook is a `.js` script invoked via `node`. Run `node --version`; if missing, install from nodejs.org or your package manager.
2. **Marker file missing** — `~/.claude/skills/.skills-collection.json` is written by `install.sh`. If you installed by hand (symlinking or copying without the installer), there's no marker, and the banner stays silent. Run `bash install.sh --copy-from <repo> --update` to write the marker.
3. **You're on the latest version** — the banner only appears when a newer release exists. Run `bash install.sh --check`; if it says "up to date", that's why.
4. **Network unreachable** — banner fails open after 1.5-second HTTP timeout. Behaves exactly like "no update".

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

---

## How do I run a skill from outside Claude Code?

Mostly you don't — they're designed for the Claude Code matcher. But two pieces are CLI-callable:

- `writer/scripts/lint.py` — offline regex linter, runs on any text file
- `scripts/install-hook.sh` / `scripts/validate.sh` / `scripts/smoke.sh` / `scripts/coverage.py` — repo maintenance

Everything else (the rule application, voice editing, viral generation, multilingual parity) needs Claude Code as the inference layer.

---

## What's the difference between `writer`, `prose-edit`, and `style-check`?

- **`writer`** *writes / cleans*. Takes raw text → outputs cleaner text. Mutates content.
- **`prose-edit`** *rewrites with a voice*. Wraps `writer`, adds fiction voice rules. Also mutates content.
- **`style-check`** *only reports*. Wraps writer + prose-edit + essay-write *rules* (not the skills themselves) and produces a structured report. Never mutates anything.

Use `style-check` as a pre-commit gate; use `writer` / `prose-edit` / `essay-write` to actually edit.

---

## How is the release cadence?

Tag-driven from `main`. Every push to `main` triggers `.github/workflows/release.yml`, which parses commit messages since the last tag:

- `feat:` → minor bump
- `fix:` / `perf:` / `refactor:` → patch bump
- `!` after type or `BREAKING CHANGE:` in body → major bump
- `docs:` / `chore:` / `style:` / `ci:` / `test:` → no release

So expect a release ~as often as there are real changes, with no scheduled cadence. The status-line banner caches the latest tag for 24 h, so the banner reflects yesterday's-or-newer state.

---

## Where do I report issues / ask design questions?

- **Bug** (a skill misbehaves, installer breaks): [open an issue](https://github.com/Mikefluff/skills/issues/new/choose) with the bug-report template
- **New skill proposal**: same — new-skill-proposal template
- **Design / open-ended question**: [Discussions](https://github.com/Mikefluff/skills/discussions)
- **Security**: see [SECURITY.md](../SECURITY.md) for the responsible-disclosure flow
