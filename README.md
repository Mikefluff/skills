# skills

[![ci](https://github.com/Mikefluff/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/ci.yml)
[![release](https://github.com/Mikefluff/skills/actions/workflows/release.yml/badge.svg)](https://github.com/Mikefluff/skills/actions/workflows/release.yml)
[![version](https://img.shields.io/github/v/release/Mikefluff/skills?label=version)](https://github.com/Mikefluff/skills/releases/latest)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A small, opinionated collection of [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) skills for editing prose without producing text that reads like LLM output. Russian-first, English-capable.

**Eleven skills**, one base linter + six wrappers + three linters + one meta-skill. Plain markdown, MIT-licensed, no required external deps.

---

## Install (5 seconds)

```bash
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
```

Opens up after Claude Code session restart. Skills are auto-discovered by `name:` and `description:` in their frontmatter — no `~/.claude/settings.json` edits required.

---

## First time? Start here

**→ [User Guide](docs/USER-GUIDE.md)** — pick your scenario, walk through it end-to-end.

Quick scenario picker:

| You want to … | Walkthrough |
|---|---|
| Write a viral social-media post | [RU](docs/walkthroughs/viral-post.md) · [EN](docs/walkthroughs/en-viral-post.md) |
| Edit a fiction chapter | [fiction-chapter](docs/walkthroughs/fiction-chapter.md) |
| Draft a long-form essay | [non-fiction](docs/walkthroughs/non-fiction.md) |
| Verify a multilingual translation | [translation-parity](docs/walkthroughs/translation-parity.md) |
| Auto-lint every commit | [pre-commit-hook](docs/walkthroughs/pre-commit-hook.md) |
| Audit a chapter against your story bible | [canon-check-audit](docs/walkthroughs/canon-check-audit.md) |
| Insert a Pelevin-vector digression | [digression-insertion](docs/walkthroughs/digression-insertion.md) |
| Run a read-only quality gate | [style-check-gate](docs/walkthroughs/style-check-gate.md) |
| Rewrite text in a different register | [USER-GUIDE](docs/USER-GUIDE.md#tone-shifter--register-rewrites) |
| Draft a cold outreach email | [USER-GUIDE](docs/USER-GUIDE.md#i-want-to-write-a-cold-email) |

If something looks wrong: [FAQ](docs/FAQ.md) · [Troubleshooting](docs/TROUBLESHOOTING.md).

---

## What's in the box

<!-- BEGIN skills-table (auto-generated; run `make gen-readme`) -->

| Skill | Layer | Languages | Purpose |
| --- | --- | --- | --- |
| [`writer`](writer/) | base | ru/en | Base clean-prose editor — antinyeyroslop (23 categories), typography, structural synthetics, RU calques. Invoked by all other prose skills. |
| [`viral-text`](viral-text/) | wrapper | ru/en | Write viral social media content — hooks, numbered points, micro-conclusion with NLP question, CTA. 41 viral content rules + platform adaptation. |
| [`prose-edit`](prose-edit/) | wrapper | ru | Fiction rewrite layer — Pelevin/Manson voice vector, 10-item style drift checklist, no meta-refs / anglicisms in narrator voice, long artistic rewrite (no comma-stitching), ToV pattern, 5-trigger structural-synthesis detector, Postirony depth-pass. |
| [`essay-write`](essay-write/) | wrapper | ru | Non-fiction layer — long subordinate sentences (Manson style), source-backed claims, philosophy through humor, biography through scenes, plain-Russian for complex content. |
| [`style-check`](style-check/) | linter | ru/en | Read-only pre-commit lint that stacks writer + prose-edit + essay-write rules. Routes by configurable path patterns (fiction vs non-fic), BLOCKING/WARNING/INFO severity, exit-code semantics for git hook. |
| [`translation-sync`](translation-sync/) | linter | ru/en/pt-br | Read-only pre-commit parity checker for trilingual book translations (RU↔EN↔PT-BR) — typography per language, terminology canon, anchor-quote drift, names/patronymics/diminutives, cultural realia footnotes, no-smoothing of numbers/brands/dates. BLOCKING/WARNING/INFO severity with exit-code semantics for git hook. |
| [`canon-check`](canon-check/) | linter | ru/en | Story-bible consistency auditor for any book series. Greps entities (characters / artifacts / locations) in changed chapters, cross-references the project's story-bible document, flags BLOCKING contradictions / WARNING gaps / INFO new details. Read-only — trust the text, not memory. |
| [`pelevin-digression`](pelevin-digression/) | wrapper | ru | Write a Pelevin-style digression for a fiction or non-fiction passage — 12 structural techniques + 5 banned constructions. Wraps prose-edit (fiction) or essay-write (non-fic). Invoked by request, not auto-applied. |
| [`skills-update`](skills-update/) | meta | en/ru | User-invocable update check + apply for this collection. Compares local install marker with latest GitHub release, shows CHANGELOG diff, asks for confirmation, runs install.sh --update. |
| [`tone-shifter`](tone-shifter/) | wrapper | en/ru | Rewrite a passage in a different register (formal↔casual, business↔academic, technical↔friendly, plain-explainer) without changing meaning. 6 registers + named transformation deltas. Wraps writer as final cleanup. |
| [`cold-email`](cold-email/) | wrapper | en | Write or rewrite cold outreach emails (first-touch, follow-up, intro request, re-engage). 5-block structure, ≤120-word budget, banned ceremony patterns, anti-template subject lines. Wraps writer as final cleanup. |

<!-- END skills-table -->

Skills compose: wrappers call `writer` internally; linters reference the same rule files but don't mutate. See [docs/COMPOSING.md](docs/COMPOSING.md) for the dependency graph.

---

## Updates

Three ways, increasing in eagerness:

1. **On demand:** invoke `/skills-update` inside Claude Code.
2. **Ambient status-line banner** *(opt-in)*: `bash scripts/install-hook.sh`. Shows ` · skills v1.0.1→1.2.0 +1 skill` when an update exists.
3. **CLI:** `bash install.sh --check` / `bash install.sh --update [--prune]`.

The banner / `/skills-update` never updates without explicit user confirmation.

---

## Common install flags

```bash
# install a subset
curl -fsSL .../install.sh | bash -s -- --skills writer,viral-text

# install to a custom prefix
curl -fsSL .../install.sh | bash -s -- --prefix /tmp/skills

# pin a specific version
curl -fsSL .../install.sh | bash -s -- --version 1.0.1

# re-install (overwrite existing skills)
bash install.sh --update

# check what's installed vs what's available
bash install.sh --check

# uninstall everything
bash install.sh --uninstall
```

Full installer help: `bash install.sh --help`.

---

## Repo layout

```
skills/
├── README.md                # this file
├── VERSION                  # semver, single source of truth
├── CHANGELOG.md             # Keep-a-Changelog
├── skills.json              # machine-readable manifest used by installer
├── install.sh               # pure-bash installer, curl-pipeable
├── Makefile                 # local dev convenience
├── CONTRIBUTING.md          # how to add a skill / report a bug / propose new one
├── docs/
│   ├── USER-GUIDE.md        # ← start here as a user
│   ├── walkthroughs/        # detailed per-scenario flows
│   ├── FAQ.md
│   ├── TROUBLESHOOTING.md
│   ├── COMPOSING.md         # dependency graph + composition patterns
│   ├── VERSIONING.md        # semver policy + release flow
│   └── LINTER-COVERAGE.md   # auto-generated regex coverage
├── scripts/
│   ├── validate.sh          # frontmatter + cross-link + description-quality check
│   ├── check-docs-consistency.sh  # skills.json ↔ README ↔ USER-GUIDE ↔ walkthroughs
│   ├── gen-skills-table.py  # regenerate the README skills table from skills.json
│   ├── smoke.sh             # validate + writer linter regression + fixture snapshots
│   ├── coverage.py          # regenerate docs/LINTER-COVERAGE.md
│   ├── bump.sh              # bump VERSION + promote [Unreleased] CHANGELOG section
│   ├── new-skill.sh         # bootstrap a new skill folder
│   ├── decide-bump.sh       # parse conventional commits since last tag
│   ├── lint-description.py  # frontmatter description quality (advisory)
│   └── install-hook.sh      # idempotent status-line banner installer
├── hooks/
│   └── skills-update-banner.js
├── tests/                   # fixture snapshots for writer/scripts/lint.py
├── .github/                 # workflows + issue/PR templates + SECURITY.md
└── <skill-name>/            # the 11 skills, one folder each
```

---

## Local development

```bash
make help                       # list all targets
make install                    # install from this checkout to ~/.claude/skills/
make smoke                      # validate + linter regression + fixture snapshots
make check-docs                 # docs-consistency gate
make gen-readme                 # regenerate skills table
make new-skill NAME=foo-bar DESC="..."
```

Releases are automatic — push a conventional-commit message (`feat:`, `fix:`, `feat!:`, etc.) and `.github/workflows/release.yml` bumps + tags + publishes. See [docs/VERSIONING.md](docs/VERSIONING.md).

Want to contribute? Read [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

---

## License

MIT — see [LICENSE](LICENSE).
