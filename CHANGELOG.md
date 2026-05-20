# Changelog

All notable changes to this skill collection are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Commit format follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — CI parses messages to decide the next bump:

- `feat:` / `feat(scope):` → minor bump
- `fix:` / `perf:` / `refactor:` → patch bump
- `BREAKING CHANGE:` in body OR `!` after type → major bump
- `docs:` / `chore:` / `style:` / `ci:` / `test:` → no release

## [Unreleased]

### Added — new skills
- **`translation-sync`** (linter). Pre-commit parity checker for multilingual book translations (RU ↔ EN ↔ PT-BR). 15-point pre-commit checklist + per-language typography rules + terminology canon table + anchor-quote canonical translations + names / patronymics / diminutives rules + cultural-realia footnote pattern + "do not smooth this number" guard. Read-only — produces a structured parity report.
- **`canon-check`** (linter). Story-bible consistency auditor for the author's book series (АБ / ЭА / НК). Greps entities in changed chapters, cross-references `story-bible.tex`, flags BLOCKING contradictions / WARNING gaps / INFO new details. Core principle: trust the text, not memory. Ships with the documented incident catalogue (хват Ирэн, яйцо-Квинта, рыжая ведьма, число смехов Вэй Лина, возраст Лии, возраст отца Дана).
- **`pelevin-digression`** (wrapper). Write a Pelevin-voice-vector digression for a fiction or non-fiction passage. 12 structural techniques (bracket-essay, brand-name sociology, anti-gradation list, forward-link, …) + 5 banned constructions (aphoristic closer, X-превращается-в-Y, дефис-афоризм, двойной пафос, «не X, а Y»). Composes with `prose-edit` (fiction) or `essay-write` (non-fic) as the wrapped final pass.

### Improved — existing skills (godacademy edit-pattern mining)
- **`writer`**: extended cat 22 NEURAL_METAPHOR with the «держать» abstract-metaphor cluster (держит роль / связка нас держит / держит веер / etc.) and explicit "even in literal sense" ban for «шёпот / прошептал». New section in `ru-calques.md` for окказионализмы и псевдоакадемические новоделы (зряче, заимка, похвала к, следствию не подлежит, заявочное рамкирование). New section in `structural-prose.md` for N+Gen → Gen+N word-order inversion («инженера сын»). Added 4 NEURAL_METAPHOR patterns and a new `DOUBLE_NEG_REGEX` category to `writer/scripts/lint.py` (linter now flags 13 hits on the calibration fixture, up from 10).
- **`prose-edit`**: new `references/depth-pass.md` — 10-point Postirony depth-pass checklist (bleed-instead-of-wrap / recursive-accusation / body-over-mind / cruelty-surprised-by-itself / …) plus the IT-blog test ("could this edit exist in an IT blog?"). New section in `rewrite-principles.md`: comma-stitching recidivism + темпо-правила (≤ 3 staccato fixes consecutively; rewrite MUST be longer than the original; subordinate-clause or concrete-image obligatory). New section in `pitfalls.md`: AI-aphorism trap (ChatGPT aphorisms ↔ chopped beats — both nyeyroslop from opposite poles). Sharpened `cleanness-checklist.md` items with concrete examples.
- **`essay-write`**: new `references/structural-synthesis-keepers.md` — 7-pattern false-positive filter for when parallelism is a device, not nyeyroslop (anaphora, opening catalog, staircase, block-diagram, mantra, virtual opponents, dash-definitions). New section in `voice-long-sentences.md`: two-three-tier structure of long subordinate periods (main claim → : / — → expansion via metaphor or concretion → ironic coda). New section in `structure.md`: НК-specific V/H/P hypothesis markers + mandatory "what would falsify this" block.
- **`style-check`**: appended post-rewrite signature catalogue to `references/severity.md` — concrete regex patterns the author has flagged in their own past Claude rewrites (duplicate punch lines on `\n` boundaries, calque «не X, а Y» at line start, dangling adverb-stumps, N+Gen inversion).

## [0.2.0] — 2026-05-20

### Added
- **Distribution pipeline.** `install.sh` (pure bash, curl-pipeable, tarball-based by default; flags: `--skills`, `--copy-from`, `--update`, `--version`, `--prefix`, `--dry-run`). Writes `~/.claude/skills/.skills-collection.json` marker for the update flow.
- **Local dev tooling.** `Makefile` (install / validate / smoke / lint / new-skill / bump-{patch,minor,major} / release). `scripts/validate.sh` (frontmatter + cross-link check), `scripts/smoke.sh` (validate + writer-linter regression), `scripts/bump.sh` (VERSION + CHANGELOG + skills.json), `scripts/new-skill.sh` (scaffold), `scripts/decide-bump.sh` (parse conventional commits).
- **CI / release.** `.github/workflows/ci.yml` runs validate + smoke + install-dry-run on every PR/push. `.github/workflows/release.yml` parses conventional commits since the last `v*` tag, decides bump level, bumps VERSION + CHANGELOG + skills.json, commits, tags `v<new>`, pushes, publishes GitHub Release. Manual override via `workflow_dispatch.level`.
- **Update notification (both A and B).**
  - `skills-update` skill: user-invocable (`/skills-update`) — reads the local marker, fetches latest tag via WebFetch, shows the CHANGELOG diff, confirms via `AskUserQuestion`, runs `install.sh --update`. Never updates without confirmation.
  - `hooks/skills-update-banner.js`: opt-in Node status-line hook — checks remote tag with a 24-hour cache and appends a quiet `· skills v0.1.0→0.2.0 (run /skills-update)` banner. Fails open on any error.
- **Docs.** `docs/CONTRIBUTING.md` (SOTA layout contract + commit conventions + CI gates + release flow). `docs/VERSIONING.md` (semver policy, bump rules, tag format, yanking).
- **README** rewritten with badges, 5-second install, update flow, project layout, and local dev section.

### Improved
- `scripts/bump.sh` now promotes the accumulated `[Unreleased]` section into the new version instead of inserting an empty placeholder. Future releases will have populated GitHub Release notes automatically.

## [0.1.0] — 2026-05-20

### Added
- Initial release with 5 skills: `writer`, `viral-text`, `prose-edit`, `essay-write`, `style-check`.
- SOTA progressive-disclosure layout: compact `SKILL.md` (≤ 200 lines) + `references/` + `examples/`.
- `writer` ships with an offline regex linter (`writer/scripts/lint.py`) — 23 neuroslop categories, exit-code verdict.
- Cross-skill dependency: `viral-text`, `prose-edit`, `essay-write` invoke `writer` as their final pipeline step; `style-check` routes by file path to the right rule set.

[Unreleased]: https://github.com/Mikefluff/skills/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Mikefluff/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/Mikefluff/skills/releases/tag/v0.1.0
