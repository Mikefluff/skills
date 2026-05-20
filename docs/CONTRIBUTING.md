# Contributing

Thanks for considering a contribution. This repo is small on purpose — its goal is a tight set of Claude Code skills with a consistent shape. Everything that ships here must follow the SOTA layout below and pass `scripts/validate.sh`.

---

## Skill layout (SOTA progressive-disclosure)

```
<skill-name>/
├── SKILL.md              # entrypoint — frontmatter + concise router. ≤ 250 lines.
├── references/           # progressive disclosure — loaded only when needed.
│   └── *.md
├── scripts/              # optional — offline deterministic helpers (Python / shell).
│   └── *.py
└── examples/             # canonical inputs/outputs for calibration.
    └── *.md
```

Rules of thumb:

- **SKILL.md** is the router. It states the contract and links to heavy content. Don't paste 500-line catalogues directly here.
- **references/** holds the things you'd otherwise put in an appendix: regex tables, exhaustive enumerations, "everything we ban" lists, large checklists.
- **scripts/** is where deterministic logic lives. Use it when a regex or simple state machine is cheaper, faster, and more reliable than an LLM pass.
- **examples/** is for calibration. Each example should fail or succeed in a *predictable* way — that's what the smoke test relies on.

Bootstrap a new skill:

```bash
make new-skill NAME=foo-bar DESC="One-line description"
# or
bash scripts/new-skill.sh foo-bar --description "..." --layer wrapper --deps writer
```

This scaffolds the right directories and a SKILL.md template with the required frontmatter.

---

## Required frontmatter

Every `SKILL.md` must start with:

```markdown
---
name: <kebab-case-name>
description: "<one-line description, used by Claude Code for skill discovery>"
license: MIT
allowed-tools:
  - Read
  - Write
  ...
---
```

The `validate.sh` script will reject any SKILL.md missing one of these.

---

## Manifest entry (`skills.json`)

When you add a skill, register it in `skills.json`:

```json
{
  "name": "foo-bar",
  "dir": "foo-bar",
  "layer": "wrapper",
  "description": "...",
  "languages": ["ru", "en"],
  "deps": ["writer"]
}
```

- `layer`: one of `base`, `wrapper`, `linter`.
- `deps`: other skills in this collection that must be installed alongside.

Also add a row to the table in the top-level `README.md`.

---

## Commit messages — Conventional Commits

CI parses commit messages to decide the next semver bump. Use:

| Prefix | Bump |
|---|---|
| `feat:` or `feat(scope):` | minor |
| `fix:`, `perf:`, `refactor:` | patch |
| `BREAKING CHANGE:` in body **or** `!` after type (e.g. `feat!:`) | major |
| `docs:`, `chore:`, `style:`, `ci:`, `test:` | no release |

Examples:

```
feat(viral-text): add ru-only "ёлочки" enforcement to validation Layer B
fix(writer): NEURAL_METAPHOR regex over-matched literal "трещина в стене"
feat!: rename style-check `staged` mode to `cached`
chore(release): v0.2.0
```

---

## CI gates

Every PR runs `bash scripts/validate.sh` and `bash scripts/smoke.sh`. Both must pass.

Locally:

```bash
make validate    # frontmatter + cross-link check
make smoke       # validate + writer linter regression
make lint        # writer offline linter over every skill's examples/
```

---

## Release flow

You generally don't release manually. On push to `main`, `.github/workflows/release.yml`:

1. Looks at commits since the last `v*` tag.
2. Decides bump level via `scripts/decide-bump.sh`.
3. Runs `scripts/bump.sh <level>` to update VERSION + CHANGELOG + skills.json.
4. Commits as `chore(release): v<new>`.
5. Tags `v<new>` and pushes.
6. Creates a GitHub Release with the relevant CHANGELOG section as the body.

To release manually (from a clean local checkout):

```bash
make bump-minor          # or bump-patch / bump-major
# edit CHANGELOG if needed
git add VERSION CHANGELOG.md skills.json
git commit -m "chore(release): v$(cat VERSION)"
make release             # tags + pushes; CI takes it from there
```

To trigger from GitHub UI: `Actions → release → Run workflow` with the bump level you want (or leave blank to let the workflow decide).

---

## Local install during development

```bash
make install                              # copy this checkout to ~/.claude/skills/
PREFIX=/tmp/skills-dev make install       # to a sandbox prefix
make update                               # re-copy with --update
```

Both `install` and `update` use `install.sh --copy-from .` so you don't need a published release to test.

---

## What I'd reject in review

- A new skill without `examples/` (no calibration → no regression coverage).
- A SKILL.md longer than ~250 lines (didn't use progressive disclosure).
- New deps the rest of the collection doesn't justify (npm package, MCP server, language-specific frameworks).
- Frontmatter without `license` (the whole repo is MIT — be explicit per skill).
- Examples that are *real publishable content* — these are calibration fixtures, not finished work.
- Cross-skill imports via filesystem paths. Skills reference each other by name (the Claude Code matcher resolves), not by `../writer/SKILL.md`.
