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

## [1.3.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v1.3.1)

## [1.3.0] — 2026-05-20

### Added — Docker image

- **`Dockerfile`** + **`.github/workflows/docker.yml`** — multi-arch (linux/amd64 + linux/arm64) Docker image published to `ghcr.io/mikefluff/skills` on push to main and on tag. Image ships `writer/scripts/lint.py` + all 11 skills' markdown. Entrypoint commands: `lint FILE`, `lint-all DIR`, `coverage`, `validate`, `list`, `version`, `help`.
- Use cases: CI integration without `curl | bash`, containerized pre-commit, isolated lint in untrusted environments.
- README quick-link added; docs/USER-GUIDE.md "Use the Docker image" section.

### Added — Launch material

- **`docs/LAUNCH-POST.md`** — copy-pasteable drafts for X (single tweet + 7-tweet thread), LinkedIn, Substack longform, Hacker News, Reddit, awesome-claude-code PR. Plus anticipated FAQ. All drafts intentionally cite AI-slop phrases (so the linter trips on them — expected meta-evidence).

### Added — Architecture audit

- **`docs/audits/references-duplicates.md`** — documented finding that no `core/` shared-base refactor is needed. Filename-clashes (two `banned-constructions.md`) cover disjoint scopes; structural concepts (staccato, double-neg) defined once in `writer/references/`, cross-linked from wrappers.

### Changed — EN linter coverage

- **`writer/scripts/lint.py`** — 9 additional EN regex category sets added: PSEUDO_SMART, BUREAU_INV, CORPORATE, NE_X_A_Y, SELF_REF, PSEUDO_SCI, VAGUE_PERSON, NOMINALIZATION, SUPERLATIVE_OVERLOAD, plus expanded AI_QA. Synthetic EN-neuroslop fixture now triggers **18 categories / 54 hits** (was 7 / 23). EN clean-prose fixture stays clean (0 hits). All RU fixtures unaffected (new patterns are EN-only by structure).

## [1.2.0] — 2026-05-20

### Added — new skills

- **`tone-shifter`** (wrapper, RU+EN). Rewrite text in a different register without changing meaning. 6 named registers — `casual`, `friendly-professional`, `business-formal`, `academic`, `technical`, `plain-explainer` — plus a transformation-deltas matrix for each source→target pair. Wraps `writer` as final cleanup.
- **`cold-email`** (wrapper, EN). Write or rewrite cold outreach (first-touch, follow-up, intro request, re-engage, forwardable). 5-block structure, ≤120-word budget, banned ceremony patterns, anti-template subject lines. Wraps `writer` as final cleanup.

### Added — EN paritет

- **`writer/scripts/lint.py` — EN regex patterns.** Added EN coverage to FILLER_INTRO, GPT_FILLER, AI_BRIDGE, STOCK_METAPHOR, AI_INTENSIFIER, AI_HEDGE, SELFHELP, PSEUDO_CAUSAL, plus new AI_TRIPLETS category. Synthetic EN-neuroslop fixture now triggers 7 categories / 23 hits → verdict "neuroslop suspected".
- **EN sections in 5 reference files** (mirror RU rules):
  - `writer/references/structural-prose.md` — `## EN structural patterns` (staccato, em-dash abuse, comma-splice, double-negation, intensifier ladder, balance hedges, pseudo-causal bridges, nominalization, sentence-opener monotony)
  - `writer/references/neuroslop-categories.md` — `## EN AI-style signatures` (18 EN buckets EN-1..EN-18)
  - `viral-text/references/viral-rules.md` — `## EN viral hook patterns`
  - `essay-write/references/banned-constructions.md` — `## EN banned constructions for non-fiction`
  - `prose-edit/references/voice.md` — `## EN voice patterns`
- **EN test fixtures** — `tests/fixtures/en_neuroslop_full_pass.md` + `tests/fixtures/en_clean_prose.md` with snapshots.
- **EN walkthrough** — `docs/walkthroughs/en-viral-post.md` (EN content marketer persona for LinkedIn / X).

### Added — per-skill test coverage

- **8 per-skill input fixtures** in `tests/fixtures/skill_*_input.md`. Each fixture is a representative input for that skill (viral-text, prose-edit, essay-write, style-check, translation-sync, canon-check, pelevin-digression) so any future linter regression on real-world skill inputs is caught. Combined fixture count: 14 (up from 5).

### Added — dedicated walkthroughs

- **`docs/walkthroughs/canon-check-audit.md`** — story-bible audit for a fresh chapter, standalone.
- **`docs/walkthroughs/digression-insertion.md`** — Pelevin-vector digression in non-fiction essay, standalone.
- **`docs/walkthroughs/style-check-gate.md`** — manual quality gate without auto-edits, standalone.

### Added — contributor infrastructure

- **`CONTRIBUTING.md`** (root) — comprehensive contributor guide. Project structure, how-to-add-a-skill checklist, editing existing skills, bug reporting, local dev workflow, CI gate explanations, conventional-commits reference, PR checklist. Fixes broken FAQ links.
- **`.github/ISSUE_TEMPLATE/false_positive.yml`** — new template for linter / wrapper false-positive reports.
- **`bug_report.yml` + `new_skill_proposal.yml`** updated to include `tone-shifter` and `cold-email` in dropdowns.
- **`.github/workflows-template/skills-lint.yml.template`** — copy-pasteable GitHub Action that pins to a specific `Mikefluff/skills` release and runs `writer/scripts/lint.py` on the user's prose files in CI. Configurable `LINT_PATHS` and `FAIL_THRESHOLD`. Documented in USER-GUIDE under new "Use in your CI" section.

### Changed — descriptions tightened

- 6 SKILL.md descriptions shortened to ≤350 chars (canon-check 493→334, pelevin-digression 457→315, translation-sync 451→325, essay-write 443→345, prose-edit 419→312, skills-update 369→295). Improves Claude Code skill-matching discrimination.

### Fixed — shellcheck warnings

- **`install.sh:90`** — replaced `eval "$@"` (SC2294) with safe `"$@"` direct expansion. All `run` callers refactored to plain-arg style (no string-quoted shell expressions). Removes potential security risk.
- **`install.sh:254-274`** — removed unused `a1/a2/a3/b1/b2/b3` vars (SC2034); refactored `semver_cmp` to use `cut -d. -f<i>` directly.
- **`install.sh:431`** — added missing `"$INSTALL_SKILLS"` quoting (SC2086).
- **`scripts/validate.sh:61`** + **`scripts/check-docs-consistency.sh:109`** — missing quotes fixed.
- **`scripts/check-docs-consistency.sh`** — removed unused `yellow()` helper (SC2329).

### Removed

- **`docs/CONTRIBUTING.md`** — consolidated into root `CONTRIBUTING.md` (GitHub standard location). All references updated.

## [1.1.0] — 2026-05-20

### Added — user-facing documentation

- **`docs/USER-GUIDE.md`** — landing page for users. Scenario-based navigation, two-minute orientation per use case, configuration pointers, update flow summary, link to FAQ / TROUBLESHOOTING.
- **`docs/walkthroughs/`** — 5 detailed step-by-step flows, one per persona:
  - `viral-post.md` (viral-text, writer) — content marketer / SMM
  - `fiction-chapter.md` (prose-edit, writer, canon-check, pelevin-digression) — novelist
  - `non-fiction.md` (essay-write, writer, pelevin-digression) — essayist / popular-science writer
  - `translation-parity.md` (translation-sync) — translator / localization editor
  - `pre-commit-hook.md` (style-check, writer) — author who wants automatic linting
  - Each walkthrough has `title:` / `persona:` / `time:` / `skills:` frontmatter; the `skills:` list is verified against `skills.json` by CI.
- **`docs/FAQ.md`** — the questions that get asked first. Covers: which skills are required, RU vs EN coverage, data flow / privacy, uninstall, why-so-many-skills, false-positive policy, custom rules, network-failure fallback, curl-pipe safety, etc.
- **`docs/TROUBLESHOOTING.md`** — symptom → diagnosis → fix for: install/update, status-line banner, `skills-update`, linter false-positives, CI failures in forks, pre-commit hook gotchas, cross-skill issues.

### Added — CI gates for doc consistency

- **`scripts/gen-skills-table.py`** — generates the "What's in the box" markdown table from `skills.json`. Supports `--write` (update README in place) and `--check` (CI gate: fail if README out of date).
- **`scripts/check-docs-consistency.sh`** — five-step gate:
  1. README skills table matches `skills.json` (delegates to gen-skills-table.py --check)
  2. Every skill folder on disk is in `skills.json`
  3. Every walkthrough's `skills:` frontmatter list references only real skills
  4. Every skill is mentioned somewhere in `docs/USER-GUIDE.md`
  5. New skill folders since the last `v*` tag must be mentioned in `CHANGELOG.md [Unreleased]`
- **`.github/workflows/ci.yml`** — runs `check-docs-consistency.sh` on every PR/push.
- **`Makefile`** — new targets: `check-docs`, `gen-readme`.
- **`.markdownlint.json`** — disabled MD025 (single-h1) since walkthroughs have both frontmatter `title:` and an h1 by design.

### Changed — README rewritten as a slim landing

Replaced the long technical README with a 1-page landing that points users into `docs/USER-GUIDE.md` for the deep dive. The "What's in the box" table is now auto-generated from `skills.json` between `<!-- BEGIN skills-table -->` / `<!-- END skills-table -->` markers. Repo-internal sections (full project layout, Makefile targets, release flow) moved to a "Local development" section at the bottom of README + linked deep-dive docs.

## [1.0.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v1.0.1)

## [1.0.0] — 2026-05-20

### Changed — decoupled from author's specific LaTeX book project

The collection no longer assumes any specific book repository, LaTeX build, or character canon. Skills now work on any text file (`.md` / `.tex` / `.txt` / etc.) and any prose project — the editorial rules, voice principles, regex catalogues, and structural patterns stay intact; only the bindings to one author's particular setup are gone.

- **`prose-edit`**: removed `books/{god-academy,era-arkhitektorov,heavenly-code}/` paths, removed АБ/ЭА/НК naming, removed assumed `.tex` extension. Renamed AB-specific ToV section to generic "ToV pattern". `references/canon-check.md` reduced to meta-references + anglicisms rules; story-bible consistency moved entirely to the standalone `canon-check` skill.
- **`essay-write`**: removed НК naming, generic non-fiction framing. `references/structure.md` describes hypothesis chapters in general (V/H/P markers still useful for any non-fic with mixed-confidence claims). `references/biography.md` no longer references specific places or the author's memory directory — generic protocol for verifying biographical facts.
- **`style-check`**: routing table now illustrative + configurable, no hardcoded book paths.
- **`translation-sync`**: terminology / anchor-quote tables generalized to placeholder rows; transliteration table marked as illustrative pattern rather than the author's character canon.
- **`canon-check`**: SKILL.md framed as "for any book series with a story bible". `references/known-incidents.md` restructured from 6 author-specific past incidents into 5 generic detection categories.
- **`pelevin-digression`**: removed assumption that fiction context = a specific series; routing now uses frontmatter / extension / explicit user signal.
- **`writer`**: cleaned references in SKILL.md objective and `references/integration.md` to remove project-specific naming.
- **`skills.json`** + **`README.md`** + **`docs/COMPOSING.md`** — all descriptions, Quick Start examples, decision-tree text now generic.

Historical CHANGELOG entries below (v0.3.0 — v0.4.1) are preserved as-is — they describe what was done at release time, including the author-specific framing the project then had. Going forward, descriptions stay generic.

## [0.4.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v0.4.1)

## [0.4.0] — 2026-05-20

### Added — installer
- **`install.sh --list`** — print available skills + descriptions and exit.
- **`install.sh --check`** — compare local install marker to latest release, report status.
- **`install.sh --uninstall`** — remove all installed skills + marker (interactive with `[y/N]`, scriptable with `--yes`).
- **`install.sh --prune`** — used with `--update`; remove installed skills that are no longer in the upstream manifest.
- **`scripts/install-hook.sh`** — idempotent installer for the status-line banner. Detects existing `statusLine` block, asks before overwriting, supports `--uninstall`.

### Added — quality gates
- **`scripts/lint-description.py`** — advisory linter for `description:` field quality (length, prefix smell, invocation hint, internal-path bleed). Wired into `validate.sh` — emits ⚠ / · lines per skill plus a `description quality: N PASS · M INFO · K WARN` summary.
- **GitHub Actions** — `shellcheck` job (action-shellcheck, error severity only) and `markdownlint` job (markdownlint-cli2-action) added to CI.
- **`.markdownlint.json`** + **`.markdownlintignore`** — permissive base config (MD013/MD024/MD033/MD036/MD041 off, MD001/MD009/MD012/MD022/MD025/MD040 on); examples/ excluded as calibration fixtures.
- **CI install-flow coverage** — ci.yml now also exercises `--list` and `--uninstall` end-to-end.

### Added — testing
- **`tests/`** with 5 Russian-language fixtures (`neuroslop_full_pass`, `clean_prose`, `borderline`, `staccato`, `ru_calques`) and frozen snapshots of `python3 writer/scripts/lint.py --json` output. `tests/run.sh` compares actual vs snapshot; `--update` re-baselines.
- **`smoke.sh`** now runs the fixture snapshots as Stage 3.
- **`scripts/coverage.py`** — generates `docs/LINTER-COVERAGE.md` showing which of the 23 neuroslop categories `lint.py` regex-detects (currently 18 covered / 3 partial / 2 intentionally LLM-only).

### Added — community
- **`.github/ISSUE_TEMPLATE/`** with bug-report and new-skill-proposal forms, plus `config.yml` linking to Discussions.
- **`.github/PULL_REQUEST_TEMPLATE.md`** with conventional-commits reminder + pre-merge checklist.
- **`SECURITY.md`** — responsible-disclosure policy, scope, contact.
- **GitHub Discussions** enabled, repo topics set (`claude-code`, `claude-skills`, `prose-editing`, `russian-language`, `anti-llm-detection`, `neuroslop`, `writing-tools`).

### Added — docs
- **`docs/COMPOSING.md`** — dependency graph (ASCII), "when to invoke which" decision tree, common composition patterns, anti-patterns.
- **README** — Quick Start block with typical invocations; updated project layout; Makefile targets section refreshed.

### Improved
- **`hooks/skills-update-banner.js`** v2 — now shows `skills vX→vY +N skills (release topline)` instead of bare version delta. Fetches `skills.json` from remote release to compute skill-count delta. Extracts first bullet from release body for topline. Caches both for 24h.
- **`Makefile`** — new targets: `uninstall`, `check`, `install-hook`, `test`, `coverage`.

## [0.3.0] — 2026-05-20

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

[Unreleased]: https://github.com/Mikefluff/skills/compare/v1.3.1...HEAD
[0.2.0]: https://github.com/Mikefluff/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/Mikefluff/skills/releases/tag/v0.1.0
[0.3.0]: https://github.com/Mikefluff/skills/releases/tag/v0.3.0
[0.4.0]: https://github.com/Mikefluff/skills/releases/tag/v0.4.0
[0.4.1]: https://github.com/Mikefluff/skills/releases/tag/v0.4.1
[1.0.0]: https://github.com/Mikefluff/skills/releases/tag/v1.0.0
[1.0.1]: https://github.com/Mikefluff/skills/releases/tag/v1.0.1
[1.1.0]: https://github.com/Mikefluff/skills/releases/tag/v1.1.0
[1.2.0]: https://github.com/Mikefluff/skills/releases/tag/v1.2.0
[1.3.0]: https://github.com/Mikefluff/skills/releases/tag/v1.3.0
[1.3.1]: https://github.com/Mikefluff/skills/releases/tag/v1.3.1
