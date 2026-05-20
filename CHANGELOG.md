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

## [1.9.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v1.9.1)

## [1.9.0] — 2026-05-20

### Added — sprint v1.9 distribution + visibility

- **Refreshed launch-post drafts** — `docs/LAUNCH-POST.md` rewritten as an
  index pointing to per-platform files under `docs/launch-posts/`:
  `x-thread.md` (single tweet + 9-tweet thread), `linkedin.md` (long post),
  `hacker-news.md` (Show HN + body), `reddit.md` (r/ClaudeAI, r/programming,
  r/copywriting variants), `substack.md` (long-form blog post),
  `awesome-claude-code.md` (one-line entry + paragraph + PR body). All
  drafts reflect current state (17 skills, 28 linter categories, all
  wrappers) instead of the stale "11 / 23" numbers.

- **npm packaging** — new `package.json` + `bin/skills.js` wrapper script.
  Installable as `npm install -g @mikefluff/skills`; the `skills` binary
  delegates every subcommand (`install` / `update` / `uninstall` / `check`
  / `list` / `version` / `help`) to the bundled `install.sh`. `npm pack`
  produces a 430 kB tarball with 142 files.

- **Homebrew formula** — `Formula/skills.rb` for a future
  `mikefluff/homebrew-tap`. Bundles the repo under `libexec/` and exposes
  a `skills` binary; `skills install` copies into `~/.claude/skills/`.
  SHA256 to be filled at release time.

- **`docs/INSTALL.md`** — consolidated install reference covering curl,
  npm, Homebrew, Docker, and manual paths, plus updates / uninstall /
  troubleshooting sections.

### Changed

- README install section now shows curl + npm + Homebrew + Docker in one
  block instead of just curl + Docker. Links to `docs/INSTALL.md` for the
  complete reference.

## [1.8.1] — 2026-05-20

### Fixed

- **Finish Track E from v1.8** — v1.8.0 created `common/references/` and added
  cross-link headers to the three skill `banned-patterns.md` files but kept the
  duplicated content in place. Now actually deduplicated: 26 anti-pattern
  entries that were listed in 2-3 places live in exactly one place under
  `common/`. Affected files: `cold-email`, `landing-copy`, `release-notes`
  `banned-patterns.md`; `common/references/banned-patterns-preambles.md` (added
  email-greeting variants).
- **Pre-commit hook skip list** extended to cover anti-pattern catalogues
  (`*/references/banned-patterns*.md`, `common/references/banned-patterns*.md`)
  and `CHANGELOG.md` — these files exist specifically to quote the patterns
  they document, so the linter would always flag them otherwise.

## [1.8.0] — 2026-05-20

### Added — sprint v1.8 linter v2 + DRY + DX + index

- **Linter v2** (`writer/scripts/lint.py`): five new categories —
  `MARKETING_HYPE` (revolutionary / game-changing / world-class / industry-leading /
  cutting-edge / best-in-class / groundbreaking / next-generation / state-of-the-art /
  unparalleled / unmatched + RU equivalents); `EMPTY_CTA` (click here / tap here /
  learn more / get started without object + RU); `WEAK_OPENER` (we're excited to /
  thrilled to / proud to + RU); `VAGUE_BENEFIT` (save time / boost productivity /
  get more done + RU); `WRONG_TENSE_RELEASE` (will support/enable/etc. in
  release-notes context, severity `nit`). Total: 28 categories.

- **Code-fence skip** in linter: lines inside fenced ``` / ~~~ blocks are no longer
  scanned. Previously `skill_skills-update_input` had 74 lines of false-positive
  hits matching marketing words inside JSON examples; now clean.

- **Severity tags** (`blocker` / `caution` / `nit`) per hit + aggregate
  `by_severity` in JSON output. Nit-level hits don't escalate the overall
  verdict. New CLI flags: `--scan-code-blocks` (opt-in for calibration files),
  `--quiet` (used by `make lint-all`).

- **7 new `before-after.md` calibration files**: `canon-check`, `essay-write`,
  `skills-update`, `style-check`, `translation-sync`, `viral-text`, `cold-email`.
  Every skill (17/17) now has a calibration file showing the concrete
  transformation it produces.

- **3 expanded walkthroughs**: `viral-post.md` (129→234), `tone-shift.md` (162→276),
  `image-prompt-cover.md` (165→351). Added RU port scenarios, A/B variants,
  multi-stage shifts, cross-model comparisons, refinement decision trees,
  and per-walkthrough troubleshooting sections.

- **Skill tags** in `skills.json`: closed-dictionary `tags: []` array per skill
  (domain: fiction / non-fiction / marketing / social / product / tech-docs /
  ux-copy / visual / outreach; function: editing / generation / audit /
  translation / ops). `scripts/validate.sh` validates the dictionary.

- **`docs/SKILL-INDEX.md`** — auto-generated by `scripts/gen-skill-index.py`
  (`make gen-index`). Groups all 17 skills by layer, by domain, and by
  language. `scripts/check-docs-consistency.sh` gains a 6th sub-check
  verifying SKILL-INDEX freshness.

- **`common/references/`** — shared cross-skill anti-pattern catalogues:
  `banned-patterns-hype.md`, `banned-patterns-preambles.md`,
  `banned-patterns-empty-cta.md`. `install.sh` gains `install_shared_refs()`
  to copy them to `$PREFIX/common/references/`. `cold-email`,
  `landing-copy`, and `release-notes` `banned-patterns.md` now cross-link
  to the shared files instead of duplicating their content.

- **DX**: `make lint-all` (writer linter across every reference, example, and doc
  file — advisory); `scripts/install-precommit-hook.sh` (installs local
  `.git/hooks/pre-commit` that runs the linter on staged .md + smoke gate, skips
  calibration files); `.github/PULL_REQUEST_TEMPLATE.md` checklist extended to
  all 5 CI gates + tag-dictionary + gen-readme/gen-index + common/references
  consideration.

### Changed

- `writer` description: "23 categories" → "28 categories" (reflects linter v2).
- `viral-text`, `release-notes`, `rfc-writer` SKILL.md descriptions: explicit
  "Wraps `writer`" mention (consistency with other wrappers — moved from v1.7
  prep into shipped commit on this branch).
- `cold-email/references/banned-patterns.md`, `landing-copy/references/banned-patterns.md`,
  `release-notes/references/banned-patterns.md`: lead with cross-link to
  `common/references/` shared catalogues.
- `scripts/smoke.sh`: writer linter self-test now passes `--scan-code-blocks`
  so calibration BEFORE samples inside ``` fences still trigger neuroslop verdict.

## [1.7.0] — 2026-05-20

### Added — sprint v1.7 polish + RU паритет

Coverage parity across all 17 skills + RU support for 7 previously EN-only skills.

- **9 new per-skill snapshot fixtures** for skills lacking baseline tests:
  `skills-update`, `tone-shifter`, `cold-email`, `image-prompt`, `video-prompt`,
  `microcopy`, `release-notes`, `rfc-writer`, `landing-copy`. Total fixtures: 23.

- **8 new dedicated walkthroughs** in `docs/walkthroughs/`:
  `tone-shift.md`, `cold-email-pitch.md`, `image-prompt-cover.md`,
  `video-prompt-reel.md`, `microcopy-error-states.md`, `release-notes-saas.md`,
  `rfc-architecture.md`, `landing-launch.md`. Walkthrough count: 17.

- **RU паритет for 7 EN-only skills** (`cold-email`, `image-prompt`,
  `video-prompt`, `microcopy`, `release-notes`, `rfc-writer`, `landing-copy`):
  `languages: ["en", "ru"]` in `skills.json`; RU invocation hints in each
  `SKILL.md`; RU sections appended to references (RU→EN vocabulary tables,
  RU-specific tone notes, RU template variants); RU calibration pairs added to
  `examples/before-after.md`. EN+RU support: 14/17 skills (was 7/17).

- **`skills-update/examples/manifest-example.md`** — local marker JSON example,
  update flow walkthrough, failure modes table, cache behavior notes.

### Changed

- **`docs/COMPOSING.md`** — full rewrite as 14 named workflow recipes
  ("Ship a SaaS product launch", "Write a fiction chapter", "Pitch a startup",
  "Document an architecture decision", etc.). Layered architecture diagram
  (meta / linters / wrappers / base), skill-to-skill data flow table,
  anti-patterns section.

- **`cold-email`** — added missing `deps: ["writer"]` in skills.json
  (description always said "Wraps writer", but the deps array was empty).

## [1.6.0] — 2026-05-20

### Added — 3 new skills (tech docs + marketing)

Collection now has **17 skills** (was 14). Closes the remaining direction from the
earlier roadmap: release-notes / RFC writing / marketing copy.

- **`release-notes`** (wrapper, EN). User-facing release notes + changelogs.
  Keep-a-Changelog format (Security / Breaking / Added / Changed / Deprecated /
  Removed / Fixed). Per-audience tone (end-user / developer / ops). Per-channel
  templates (changelog page / GitHub release / email / in-app modal / push /
  quarterly recap). Anti-marketing-fluff bans ("revolutionary", "we're thrilled
  to announce", etc.). References:
  - `sections.md` — Keep-a-Changelog 6 sections + decision rules
  - `audience-tone.md` — user / dev / ops voice differences + mixed-audience patterns
  - `structure.md` — version headers, length budgets per output format
  - `banned-patterns.md` — strip list (marketing hype, vague improvements,
    feelings preambles, future-tense for shipped work)
  - 5 calibration before/after pairs (SaaS / API / mobile / major release / recap)

- **`rfc-writer`** (wrapper, EN). Engineer-facing design documents — RFCs, ADRs,
  Tech Specs, Design Docs. Per-type structure (context / problem / proposal /
  alternatives / consequences / decision / open questions). RFC 2119 keywords
  (MUST / SHOULD / MAY) with capitalization rules. Forces at-least-2-alternatives
  plus "do nothing" baseline. References:
  - `document-types.md` — when to use RFC vs ADR vs Tech Spec vs Design doc
  - `templates.md` — full section templates per type
  - `rfc-2119.md` — keyword semantics + usage patterns
  - `alternatives.md` — how to list fairly, "Why not X?" pattern, comparison tables
  - `review-checklist.md` — common gaps and weak signals to flag
  - 4 calibration before/after pairs (ADR / RFC / Tech Spec / Design doc)

- **`landing-copy`** (wrapper, EN). Marketing copy — landing page sections (hero
  / features / pricing / FAQ / footer), SEO meta (title + description + Open
  Graph + Twitter cards), paid ad copy (Google Ads RSA / Facebook / LinkedIn /
  X / Reddit / TikTok). Julian Shapiro 5-step hero formula + 5 alternatives
  (outcome-led / old-vs-new / quantified / category+qualifier / direct-address
  / negation-led). Strict char limits per platform with i18n expansion factors.
  References:
  - `surfaces.md` — full taxonomy of marketing-copy surfaces + audience-tone mapping
  - `hero-formula.md` — Julian Shapiro 5-step + 6 alternative formulas + headline/
    subheadline/CTA rules
  - `feature-blocks.md` — 3-block / 6-block / detailed-feature patterns + how-it-works
  - `seo-meta.md` — title + description + OG + Twitter + per-page-type templates
  - `ad-copy.md` — per-platform templates (Google RSA / FB / LinkedIn / X / Reddit /
    TikTok) with variant strategy
  - `char-limits.md` — quick-reference table for every surface
  - `banned-patterns.md` — marketing hype, vague claims, generic CTAs, fake urgency
  - 8 calibration before/after pairs (hero / feature / SEO / Google Ad / FB / LinkedIn
    / Twitter / FAQ)

### Changed

- `skills.json` — +3 new entries (release-notes, rfc-writer, landing-copy)
- `README.md` — "Seventeen skills, one base linter + twelve wrappers + three
  linters + one meta-skill"
- `docs/USER-GUIDE.md` — added 3 use-case sections + scenario picker entries
- Repo layout in README updated to "17 skills, one folder each"

## [1.5.0] — 2026-05-20

### Added — 3 new skills (visual + UX)

Imported high-value content from `/Users/mikefluff/Documents/figma/` deep-scan + added microcopy from best-practices. Collection now has **14 skills** (was 11).

- **`image-prompt`** (wrapper, EN). Write prompts for AI image generators (Midjourney v6, DALL-E 3, Flux Pro, Nano Banana, SDXL). 6-part formula: `{subject} + {setting} + {style} + {lighting} + {camera} + {texture}`. References:
  - `prompt-formula.md` — 6-part structure + templates (portrait / product / scene / abstract / illustration)
  - `lighting-vocabulary.md` — portrait / scene / quality-of-light dictionaries (figma-derived)
  - `camera-vocabulary.md` — lens / aperture / format / quality-tag cheatsheet
  - `model-specifics.md` — per-model deltas (MJ params, DALL-E natural language, Flux negatives, SD weights)
  - `examples/before-after.md` — 5 calibration pairs (4-6 weak words → 40-80 strong)

- **`video-prompt`** (wrapper, EN). Write prompts for AI video generators (Kling 3.0, Veo 3, Sora, Runway Gen-3, Pika, Hailuo, Luma). CHARACTER FIRST law, Beat 1/2/3 structure, exact camera vocabulary. References (figma-derived from cinematographer/narrative.js):
  - `camera-vocabulary.md` — full DOLLY / PAN / TRACKING / CRANE / ORBIT / AERIAL / SPECIALTY dictionary with translation table
  - `beat-structure.md` — CHARACTER FIRST law, repeated-action patterns, body-detail layers, forbidden phrases that cause frozen-pose output
  - `model-specifics.md` — Kling temporal markers required, Sora narrative paragraph, Runway short prompts, Pika minimal, Luma atmospheric
  - `pacing-modes.md` — narrative / action / comedy / documentary / timelapse rules
  - `examples/before-after.md` — 5 pairs (hook / tension / breathing / POV / timelapse)

- **`microcopy`** (wrapper, EN). Write UX strings — error messages, empty states, tooltips, button labels, helper text, modals, 404/500/offline pages, onboarding cards, toasts, inline alerts. Plain language, action-oriented, never blame user. References:
  - `element-types.md` — full taxonomy with length budgets and templates per UI element
  - `length-budgets.md` — exact word/char limits, i18n expansion factors
  - `rules.md` — 10 universal rules (plain language, action verbs, no blame, no jargon, etc.) + 3 cardinal sins
  - `voice-by-product-type.md` — adjustments for SaaS / dev tool / fintech / e-commerce / consumer / B2B
  - `banned-words.md` — strip list (jargon, hedge words, robot-speak)
  - `examples/before-after.md` — 10 calibration pairs

### Added — bonus from figma deep-scan

- **`prose-edit/references/patch-refining.md`** — surgical search/replace patch strategy (from figma PatchRefinerAgent.js). Alternative to full rewrite when 90%+ of original should survive. Programmatic apply; signals fallback if patches fail >50%.
- **`style-check/references/validation-taxonomy.md`** — structured JSON output schema for machine-readable validation. Includes:
  - `scoreReasons` closed-enum (length / lack_of_specificity / promise_without_fact / generic_fear / clickbait_no_payoff / filler_banality / synthetic_template / grammar_agreement)
  - `hookAnalysis` (27 hook criteria) + `contentAnalysis` (issues by severity)
  - `metrics` per-dimension (cta / grammar / length / style)
  - `formattingRecommended` signal for downstream tooling
  - Cross-link to patch-refining as consumer

### Changed

- `skills.json` — +3 new entries (image-prompt, video-prompt, microcopy)
- `README.md` — "Fourteen skills, one base linter + nine wrappers + three linters + one meta-skill"
- `docs/USER-GUIDE.md` — added 3 use-case sections + scenario picker entries
- Repo layout in README updated to "14 skills, one folder each"

## [1.4.0] — 2026-05-20

### Added — from godacademy/figma archive mining

Imported high-value content from `/Users/mikefluff/Documents/figma/` (the author's inite.digital project — production-tuned prompts and rules).

- **`writer/references/synthetic-constructions.md`** — fake AI authenticity catalogue (7 sections):
  - Name-dropping templates (city + profession + transfer verb formulas)
  - CTA stamps ("пишите ДА", "tag someone who needs this", etc.)
  - Formula metaphors ("works like a radar")
  - Red/Green flags list templates
  - Uniform paragraph rhythm detection (LLM signature)
  - Synthetic-depth constructions ("за этим стоит", "которую стоит разобрать")
  - Pseudo-vulnerability / faux-confession patterns
- **`writer/scripts/lint.py` — new SYNTHETIC category.** 22 regex patterns covering literal phrases for name-drop templates (RU+EN), CTA stamps, formula metaphors, coaching jargon ("осознанное"), faux-confession ("я тоже через это прошёл"). Linter now has 24 categories (was 23).
- **`writer/references/ru-grammar.md`** — name declension + gender agreement for RU named entities:
  - Male names ending in -а/-я (Никита, Илья) — decline as feminine paradigm, agree as masculine
  - Foreign names -о/-е/-и/-у (Пикассо, Феллини, Гюго) — indeclinable
  - Foreign female names ending in consonant (Элизабет, Маргарет) — indeclinable
  - Patronymics, diminutives, surname patterns (-ин/-ов/-ев/-ский, -их/-ых)
  - Quick-reference table; LLM gender-agreement check protocol
- **`viral-text/references/hook-taxonomy.md`** — controllable hook generation:
  - Intent axis (5): anger / surprise / ground / give_action / sell_idea
  - Angle axis (5): numbers / conflict / new_standard / threat_to_professions / instruction_what_to_do
  - 5 × 5 matrix of 25 viable hook styles
  - 3 modes: topic-based / text-driven / improve-hook
  - Generation prompt templates for each mode
  - Calibration example with 5 hooks across distinct intent + angle pairs
- **`tone-shifter/references/brand-voice-profile.md`** — custom brand-voice JSON profile:
  - Schema: name / tone (5 enum) / styles (6 enum, 1-3) / vocabulary / avoidWords / hooks / ctaPhrases / register
  - 3 modes added to SKILL.md: `--profile`, `--infer-profile`, `--verify-profile`
  - Discriminator: registers = abstract categorical, brand-voice = concrete custom
  - Multilingual notes (brand-language fields, English taxonomy labels)

### Changed

- `writer/SKILL.md` REFERENCES table — added synthetic-constructions.md and ru-grammar.md entries.
- `viral-text/SKILL.md` REFERENCES table — added hook-taxonomy.md entry.
- `tone-shifter/SKILL.md` MODES — added 3 new modes; REFERENCES — added brand-voice-profile.md.

### Notes

- Existing `viral-text/references/viral-rules.md` and `hook-criteria.md` were already imported from figma in earlier work — no changes needed there.
- StyleSuggestAgent.js (visual-style-generator) from figma was NOT imported — out of scope (visual style detection, not prose editing).
- AGENTS.md (n8n) and .cursorrules from figma were NOT imported — non-portable project-specific.

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

[Unreleased]: https://github.com/Mikefluff/skills/compare/v1.9.1...HEAD
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
[1.4.0]: https://github.com/Mikefluff/skills/releases/tag/v1.4.0
[1.5.0]: https://github.com/Mikefluff/skills/releases/tag/v1.5.0
[1.6.0]: https://github.com/Mikefluff/skills/releases/tag/v1.6.0
[1.7.0]: https://github.com/Mikefluff/skills/releases/tag/v1.7.0
[1.8.0]: https://github.com/Mikefluff/skills/releases/tag/v1.8.0
[1.8.1]: https://github.com/Mikefluff/skills/releases/tag/v1.8.1
[1.9.0]: https://github.com/Mikefluff/skills/releases/tag/v1.9.0
[1.9.1]: https://github.com/Mikefluff/skills/releases/tag/v1.9.1
