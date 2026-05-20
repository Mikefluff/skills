<!--
Title format: conventional-commits prefix + scope.
  feat(viral-text): …
  fix(writer): …
  docs: …
  chore(release): …

CI parses commit messages to decide the next semver bump — see docs/VERSIONING.md.
-->

## Summary

<!-- 1-3 sentences. What changes, why now. -->

## Scope

- [ ] New skill (followed [CONTRIBUTING.md](../blob/main/CONTRIBUTING.md) SOTA layout)
- [ ] Extension to an existing skill (specify which: ____________________)
- [ ] Infrastructure (installer / CI / scripts / docs)
- [ ] Bug fix

## Pre-merge checklist

- [ ] `bash scripts/validate.sh` passes locally (frontmatter, cross-links, tag dictionary)
- [ ] `bash scripts/smoke.sh` passes locally (validate + linter regression + snapshots)
- [ ] `bash scripts/check-docs-consistency.sh` passes locally (6/6 sub-checks)
- [ ] `shellcheck install.sh scripts/*.sh` clean
- [ ] `npx -y markdownlint-cli2@0.13.0 "**/*.md" "#node_modules/**" "#.git/**"` clean
- [ ] If `skills.json` changed: `make gen-readme` + `make gen-index` run
- [ ] If a skill is added: row appended to `skills.json` with `tags: []` from the closed dictionary
- [ ] If frontmatter changed: `name`, `description`, `license`, `allowed-tools` all present
- [ ] If `references/` files added: linked from the skill's `SKILL.md`; if shared across ≥2 skills, consider `common/references/`
- [ ] Commit message uses conventional-commit prefix (`feat:` / `fix:` / `docs:` / `chore:` …)
- [ ] CHANGELOG `[Unreleased]` updated for any `feat:` or `fix:`
- [ ] No real / sensitive content in `examples/` — calibration samples only

## Notes for the reviewer

<!-- Optional: anything load-bearing about voice, language, or composition that the reviewer should not "fix" without context. -->
