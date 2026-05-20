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

## [0.2.0] — 2026-05-20

## [0.1.0] — 2026-05-20

### Added
- Initial release with 5 skills: `writer`, `viral-text`, `prose-edit`, `essay-write`, `style-check`
- SOTA progressive-disclosure layout: compact `SKILL.md` (≤200 lines) + `references/` + `examples/`
- `writer` includes offline regex linter (`writer/scripts/lint.py`) — 23 neuroslop categories, exit-code verdict
- Cross-skill dependency: `viral-text`, `prose-edit`, `essay-write` invoke `writer` as their final pipeline step; `style-check` routes by file path to the right rule set
- Pipeline tooling: `install.sh` (tarball-based, curl-pipeable), `Makefile`, `scripts/` (validate, smoke, bump, new-skill), GitHub Actions for CI + conventional-commit-driven releases
- `skills-update` skill for user-triggered update checks
- Status-line hook (`hooks/skills-update-banner.js`) for ambient version notification
- `skills.json` machine-readable manifest

[Unreleased]: https://github.com/Mikefluff/skills/compare/v0.2.0...HEAD
[0.1.0]: https://github.com/Mikefluff/skills/releases/tag/v0.1.0
[0.2.0]: https://github.com/Mikefluff/skills/releases/tag/v0.2.0
