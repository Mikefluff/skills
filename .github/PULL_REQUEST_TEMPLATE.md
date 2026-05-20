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

- [ ] `bash scripts/validate.sh` passes locally
- [ ] `bash scripts/smoke.sh` passes locally
- [ ] If a skill is added: row appended to `skills.json` AND `README.md` table
- [ ] If frontmatter changed: `name`, `description`, `license`, `allowed-tools` all present
- [ ] If `references/` files added: linked from the skill's `SKILL.md` and from any other reference that references them
- [ ] Commit message uses conventional-commit prefix (`feat:` / `fix:` / `docs:` / `chore:` …)
- [ ] No real / sensitive content in `examples/` — calibration samples only

## Notes for the reviewer

<!-- Optional: anything load-bearing about voice, language, or composition that the reviewer should not "fix" without context. -->
