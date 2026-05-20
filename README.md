# skills

[![ci](https://github.com/Mikefluff/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/ci.yml)
[![release](https://github.com/Mikefluff/skills/actions/workflows/release.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/release.yml)
[![version](https://img.shields.io/github/v/release/Mikefluff/skills?label=version)](https://github.com/Mikefluff/skills/releases/latest)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Collection of [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) skills focused on prose editing in Russian and English: an antinyeyroslop base editor (`writer`) plus four layered wrappers/linters on top of it.

---

## Install (5 seconds)

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

This pulls the latest GitHub release tarball, copies each skill into `~/.claude/skills/`, and writes a marker so the auto-update flow knows what's there.

Useful flags:

```bash
# install only specific skills
curl -fsSL .../install.sh | bash -s -- --skills writer,viral-text

# install to a custom prefix
curl -fsSL .../install.sh | bash -s -- --prefix /tmp/skills

# pin a specific version
curl -fsSL .../install.sh | bash -s -- --version 0.1.0

# re-install (overwrite existing skills)
curl -fsSL .../install.sh | bash -s -- --update
```

After install, every skill is auto-discovered by Claude Code via its frontmatter `name:` and `description:`. No `~/.claude/settings.json` edits required.

---

## Update

Three ways, increasing in eagerness:

1. **On demand from inside Claude Code.** Invoke `/skills-update` (the `skills-update` skill is shipped as part of this collection). It checks the latest tag, shows the CHANGELOG diff for what you'd be installing, asks for confirmation, then runs `install.sh --update`.

2. **Ambient banner via status-line hook** *(opt-in)*. The repo ships `hooks/skills-update-banner.js` — a Node script that fits into Claude Code's `statusLine` slot and tacks ` · skills v0.3.0→0.4.0 +2 skills (translation-sync description)` onto your status line when an update is available. It caches the remote tag for 24 h and fails silently if the network is down.

   To install:
   ```bash
   bash scripts/install-hook.sh
   # or: make install-hook
   ```

   The script idempotently merges the `statusLine` block into `~/.claude/settings.json`. If you already have a `statusLine` set to a different command, it asks before overwriting; with `--yes` it defaults to cancel (safer).

   To remove: `bash scripts/install-hook.sh --uninstall`.

3. **From the command line.** Just re-run the install command with `--update`.

The banner never prompts and never installs — it only nudges. The installer never runs without your explicit invocation. The `/skills-update` skill never updates without your explicit `AskUserQuestion` confirmation.

---

## Quick start

After install, open Claude Code and try:

| You want to … | Invoke |
|---|---|
| Write a viral Telegram post about morning routines | `/viral-text утренние ритуалы` |
| Clean a draft pasted in chat | `/writer clean` (then paste) |
| Rewrite a fiction chapter fragment | `/prose-edit rewrite books/god-academy/ru/chapters/ch05.tex 142:198` |
| Draft a non-fiction chapter on quantum coherence | `/essay-write chapter` (then describe topic) |
| Insert a Pelevin-style digression at a specific line | `/pelevin-digression at ch07.tex:201 "брендовая социология"` |
| Lint staged changes before commit | `/style-check staged` |
| Verify a translation matches across RU/EN/PT-BR | `/translation-sync chapter god-academy ch05` |
| Check a chapter against the story bible | `/canon-check chapter era-arkhitektorov ch12` |
| See if there's a new version of the collection | `/skills-update` |

See [docs/COMPOSING.md](docs/COMPOSING.md) for the full dependency graph and "when to invoke which" decision tree.

---

## What's in the box

Skills are organized by layer: one base editor + wrappers/linter on top.

| Skill | Layer | Purpose |
|---|---|---|
| [`writer`](writer/) | base | Base clean-prose editor. Antinyeyroslop (23 categories), typography, structural synthetics (staccato / double negation / chunks / inversions / repetitions), RU calque dictionary. Invoked by all other prose skills as their final pipeline step. Can also be called directly in `clean` / `lint` / `apply` modes. Ships with an offline regex linter (`writer/scripts/lint.py`). |
| [`viral-text`](viral-text/) | wrapper | Write viral social media content (RU/EN) — hooks, 5 numbered points, micro-conclusion with NLP question, CTA. 41 viral content rules, hook criteria, research via WebSearch, platform adaptation (Telegram / Threads / Instagram / Twitter / LinkedIn / Facebook), two-stage validation. Built on top of `writer`. |
| [`prose-edit`](prose-edit/) | wrapper | Fiction rewrite layer for the author's books (АБ / ЭА / НК). Voice (Pelevin/Manson), 10-item style drift checklist, canon check, no meta-refs / anglicisms in narrator voice, long artistic rewrite preferred over compression, AB ToV pattern, 5-trigger structural synthesis detector, Postirony depth-pass checklist, AI-aphorism trap. |
| [`essay-write`](essay-write/) | wrapper | Non-fiction layer (НК chapters, longreads, essays). Long subordinate sentences (Manson style), source-backed claims, philosophy through humor, biography through scenes, plain-Russian for complex content, sparing with metaphors, 7-case structural synthesis false-positive filter, V/H/P hypothesis markers. |
| [`style-check`](style-check/) | linter | Read-only pre-commit lint stacked on top of writer / prose-edit / essay-write. Auto-routes by file path (`books/god-academy/` → fiction; `books/heavenly-code/` → non-fic). BLOCKING / WARNING / INFO severity. Exit-code semantics for git hooks. Includes post-rewrite signature catalogue. |
| [`translation-sync`](translation-sync/) | linter | Pre-commit parity checker for multilingual book translations (RU ↔ EN ↔ PT-BR). Per-language typography, terminology canon, anchor-quote translations, names / patronymics / diminutives, cultural-realia footnote pattern, "do not smooth this number" guard. Read-only. |
| [`canon-check`](canon-check/) | linter | Story-bible consistency auditor for the author's book series (АБ / ЭА / НК). Greps entities in changed chapters, cross-references `story-bible.tex`, flags BLOCKING contradictions / WARNING gaps / INFO new details. Principle: trust the text, not memory. |
| [`pelevin-digression`](pelevin-digression/) | wrapper | Write a Pelevin-voice-vector digression for a fiction or non-fiction passage. 12 structural techniques (bracket-essay, brand-name sociology, anti-gradation list, forward-link, …) + 5 banned constructions. Invoked by request, composes with `prose-edit` (fiction) or `essay-write` (non-fic). |
| [`skills-update`](skills-update/) | meta | User-invocable update check + apply for this collection (see Update section above). |

---

## Project layout

```
skills/
├── README.md                # this file
├── LICENSE                  # MIT
├── VERSION                  # semver, single source of truth
├── CHANGELOG.md             # Keep-a-Changelog
├── skills.json              # machine-readable manifest used by install.sh
├── install.sh               # pure-bash installer, curl-pipeable
├── Makefile                 # local dev convenience: install, validate, smoke, bump, release
├── .github/workflows/
│   ├── ci.yml               # validate + smoke on every PR/push
│   └── release.yml          # conventional-commits-driven auto-release
├── docs/
│   ├── CONTRIBUTING.md      # how to add a skill
│   ├── VERSIONING.md        # semver policy + release flow
│   ├── COMPOSING.md         # which skill to invoke when; dependency graph + scenarios
│   └── LINTER-COVERAGE.md   # which of the 23 neuroslop categories lint.py detects via regex
├── scripts/
│   ├── validate.sh          # frontmatter + cross-link + description-quality check
│   ├── smoke.sh             # validate + writer linter regression + fixture snapshots
│   ├── bump.sh              # bump VERSION + promote [Unreleased] section
│   ├── new-skill.sh         # bootstrap a new skill folder
│   ├── decide-bump.sh       # parse conventional commits since last tag
│   ├── lint-description.py  # frontmatter description quality (advisory)
│   ├── coverage.py          # regenerate docs/LINTER-COVERAGE.md
│   └── install-hook.sh      # idempotent status-line banner installer
├── tests/
│   ├── README.md
│   ├── fixtures/            # short Russian fragments with known verdicts
│   ├── snapshots/           # frozen linter outputs per fixture
│   └── run.sh               # compare linter output to snapshot, fail on drift
├── hooks/
│   └── skills-update-banner.js  # opt-in status-line update banner
├── writer/                  # the 9 skills
├── viral-text/
├── prose-edit/
├── essay-write/
├── style-check/
├── translation-sync/
├── canon-check/
├── pelevin-digression/
└── skills-update/
```

Every skill follows the same SOTA progressive-disclosure layout — compact `SKILL.md` (≤ 250 lines) + heavy rules in `references/` + calibration in `examples/`. See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the contract.

---

## Local development

```bash
make help                  # list all targets

make install               # install from this checkout into ~/.claude/skills
make uninstall             # remove all installed skills + marker (interactive)
make check                 # compare installed version to latest release
make list                  # list installed skills under PREFIX
make install-hook          # opt in to the status-line update banner
make validate              # frontmatter + cross-link + description-quality check
make smoke                 # validate + writer linter regression + fixture snapshots
make test                  # snapshot tests only
make coverage              # regex coverage report (which of 23 categories lint.py detects)
make lint                  # run writer/scripts/lint.py over every skill's examples/
make new-skill NAME=foo-bar DESC="..."   # scaffold a new skill

make bump-patch            # 0.1.0 → 0.1.1 (+ promoted CHANGELOG section)
make bump-minor            # 0.1.0 → 0.2.0
make bump-major            # 0.1.0 → 1.0.0
make release               # tag + push current VERSION (CI builds release)
```

CI runs `validate` + `smoke` on every push and PR. Releases are automated from `main`: see [docs/VERSIONING.md](docs/VERSIONING.md).

---

## Uninstall

```bash
rm -rf ~/.claude/skills/{writer,viral-text,prose-edit,essay-write,style-check,translation-sync,canon-check,pelevin-digression,skills-update}
rm -f  ~/.claude/skills/.skills-collection.json
```

If you installed the status-line hook, also remove the `statusLine` block from `~/.claude/settings.json`.

---

## License

MIT — see [LICENSE](LICENSE).
