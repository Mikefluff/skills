# Versioning policy

This collection is versioned as a whole — one `VERSION` file at the repo root, one tag per release, one CHANGELOG entry per version. Per-skill versioning would let any single skill drift, which we don't want: cross-skill references (`viral-text → writer`, `style-check → prose-edit + essay-write`) need a single coherent snapshot to remain consistent.

## Semver in this context

- **MAJOR**: a breaking change to a skill's contract — frontmatter rename, removed mode, removed reference file that downstream skills depended on. Anything that requires the user to re-learn how to invoke or compose the skills.
- **MINOR**: a new skill, a new mode, a new category of rules, a new reference file. Backwards-compatible additions.
- **PATCH**: a rule clarification, a typo, a regex tweak that's strictly more precise (no new false positives), an internal refactor, doc-only changes.

If a change is ambiguous, prefer bumping higher rather than lower. The cost of a too-conservative bump is zero; the cost of a too-permissive bump is a user with a broken workflow.

## How bumps are decided

CI (`.github/workflows/release.yml`) parses commit subjects since the last `v*` tag and picks the highest-severity bump found:

| Commit prefix / marker | Bump |
|---|---|
| `BREAKING CHANGE:` in body, **or** `!` after type (e.g. `feat!:`) | major |
| `feat:` / `feat(scope):` | minor |
| `fix:` / `perf:` / `refactor:` | patch |
| `docs:` / `chore:` / `style:` / `ci:` / `test:` | (none) |

Other prefixes are ignored. A push with only `docs:` and `chore:` commits will produce no release.

You can also force a level from the GitHub UI: `Actions → release → Run workflow → level: patch/minor/major`.

## Tag format

Tags are `vMAJOR.MINOR.PATCH` (e.g. `v0.2.0`). The `VERSION` file holds the same string without the `v` (e.g. `0.2.0`). The two are kept in sync by `scripts/bump.sh` and the release workflow.

## CHANGELOG

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Each release gets a section like:

```
## [0.2.0] — 2026-06-01

### Added
- ...
### Changed
- ...
### Fixed
- ...
### Removed
- ...
```

`scripts/bump.sh` inserts the section header automatically; you fill in the bullets before pushing the release commit (or rely on the CI workflow's autogeneration, which uses commit subjects as fallback content).

## Pre-releases

The pipeline does **not** emit pre-release suffixes (`-rc.1`, `-canary.0`, etc.). If you need to test changes against another machine before tagging:

```bash
# install from a specific branch / commit
make install      # from local checkout — no tag needed
# or, on the consumer machine:
git clone https://github.com/Mikefluff/skills /tmp/skills-preview
bash /tmp/skills-preview/install.sh --copy-from /tmp/skills-preview --update
```

## What's NOT versioned

- The status-line hook (`hooks/skills-update-banner.js`) is shipped with the collection but not under semver discipline of its own — it's tied to the repo and changes when the install marker schema changes.
- The `install.sh` script is part of the repo; users who pipe it directly via `curl` always get HEAD from `main`. Old installer + new tarball is supported (the installer reads `skills.json` from the tarball, not from itself).

## Yanking a bad release

If a release goes out broken:

1. `git tag -d v0.X.Y && git push --delete origin v0.X.Y` (delete the bad tag)
2. Use the GitHub UI to delete the GitHub Release entry too.
3. Push a fix commit (`fix: ...`) — CI will compute the next patch from the last good tag, so the bad version just disappears from history.

Don't `git push --force` to rewrite main — keep the bad-release commit visible, just nuke its tag.
