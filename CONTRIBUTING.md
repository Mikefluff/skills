# Contributing to Mikefluff/skills

Thanks for considering a contribution. This repo is a collection of editing-prose skills for Claude Code, with sharp boundaries and strong CI gates. The friction is intentional — it keeps the collection coherent rather than letting drift accumulate.

If you've already decided what to contribute, jump to the relevant section. Otherwise read top-to-bottom.

---

## Quick links

- [How the repo is structured](#how-the-repo-is-structured)
- [Adding a new skill](#adding-a-new-skill)
- [Editing an existing skill](#editing-an-existing-skill)
- [Reporting a bug or false-positive](#reporting-a-bug-or-false-positive)
- [Local development workflow](#local-development-workflow)
- [CI gates explained](#ci-gates-explained)
- [Commit message convention](#commit-message-convention)
- [PR checklist](#pr-checklist)

---

## How the repo is structured

```
skills/
  <skill-name>/              ← one skill per directory
    SKILL.md                 ← required: frontmatter + objective + pipeline
    references/              ← optional: heavy rule tables, checklists
      *.md
    examples/                ← optional: BEFORE/AFTER calibration pairs
    scripts/                 ← optional: skill-specific tooling (e.g. skills/writer/scripts/lint.py)
  docs/
    USER-GUIDE.md            ← scenario-based landing
    FAQ.md
    TROUBLESHOOTING.md
    walkthroughs/            ← step-by-step user flows
  scripts/                   ← repo-level tooling (validate, bump, gen-readme, etc.)
  tests/
    fixtures/                ← input markdown files
    snapshots/               ← expected linter JSON outputs
    run.sh                   ← test runner
  install.sh                 ← user-facing installer
  skills.json                ← machine-readable skill manifest
  CHANGELOG.md
  README.md
  Makefile
```

Each skill must have `SKILL.md` with valid frontmatter (`name`, `description`, `license`, `allowed-tools`). The `description:` field is what Claude Code matches user requests against — keep it specific and ≤350 characters.

---

## Adding a new skill

### Before you scaffold

1. **Confirm it doesn't overlap an existing skill.** Read `docs/USER-GUIDE.md` and the SKILL.md of each existing skill. If your idea is "write better X" and `writer`/`prose-edit`/`essay-write` could do it, extend one of them instead of adding a new skill.

2. **Verify the discriminator.** Can a user clearly decide *when to use yours vs the alternative*? If not, the skill won't get matched — Claude Code uses the `description:` field for fuzzy matching, and overlapping descriptions hurt discovery.

3. **Decide the layer:** `base` (rules used by other skills), `wrapper` (calls a base skill as final cleanup), or `linter` (read-only, produces reports).

4. **A separate skill, or a flag on an existing one?** Split when the two would
   need different `description:` triggers; add a flag when they differ only in
   defaults. Claude routes on `description:` alone, so one skill covering eight
   jobs needs a description vague enough to match all eight — which is a
   description that matches none of them well.

   This was measured rather than assumed. The eight single-image makers
   (`flyer` / `cover` / `thumbnail` / `avatar` / `logo` / `quote-card` /
   `banner` / `meme-card`) look like one skill wearing eight hats, and merging
   them was on the roadmap twice. Their same-named reference files turn out to
   share 4–19% of their text, and 656 bytes of prose is duplicated verbatim
   across three or more of them. They are not copies; they are eight different
   grammars — thumbnails have eyeline rules, logos have palette-count limits,
   memes have caption conventions — over one shared pipeline that already lives
   in `common/runners/cli/_maker.py`, where each `run.py` is a 25-line shim.

   What *was* duplicated is the part that has since been automated: the price
   tables that had to be edited together on every vendor refresh, now checked by
   gate 8. Extract shared *data* into `common/`; keep the routing surface split.

### Scaffold

```bash
make new-skill NAME=your-skill DESC="one line, ≤350 chars"
# or
bash scripts/new-skill.sh your-skill --description "..." --layer wrapper --deps writer
```

This creates:

```
your-skill/
  SKILL.md           ← TODO placeholders
  references/
  examples/
```

### Fill in

1. **Frontmatter.** Update `SKILL.md` frontmatter:
   - `name:` — kebab-case, matches the directory name
   - `description:` — ≤350 chars (CI WARNs >350). Include task + invocation hint + discriminator vs other skills.
   - `allowed-tools:` — minimal set (Read, Bash, Grep, Glob for read-only; add Write/Edit only if mutating).

2. **`<objective>`** — what this skill is for, when to invoke, what the output contract is.

3. **`## PIPELINE`** — the deterministic steps the skill follows. Wrappers must specify "Final step: apply `writer`/SKILL.md cleanup pass."

4. **`## REFERENCES`** — table of `references/*.md` files with "When to load" column.

5. **`references/*.md`** — heavy content the skill needs but shouldn't bloat SKILL.md. Each reference file is loaded on demand. Aim for SKILL.md ≤250 lines; spillover goes here.

6. **`examples/*.md`** — at least one calibration pair (input + expected output / patterns).

### Register

7. **Add to `skills.json`** — see the existing entries. Required fields: `name`, `dir`, `layer`, `description`, `languages`, `deps`.

8. **Regenerate README table:** `make gen-readme` (auto-updates `<!-- BEGIN skills-table -->`).

9. **Add to `docs/USER-GUIDE.md`** — at minimum, a row in the "Pick your starting point" table and a short use-case section. CI fails if a registered skill isn't mentioned anywhere in USER-GUIDE.md.

10. **Add a walkthrough** (optional but encouraged) — `docs/walkthroughs/your-skill.md` with frontmatter:
    ```yaml
    ---
    title: "..."
    persona: "..."
    time: "..."
    skills:
      - your-skill
    ---
    ```
    CI parses the `skills:` list and fails if any referenced skill is unknown.

11. **Add at least one fixture** — `tests/fixtures/skill_your-skill_input.md` + run `bash tests/run.sh --update` to seed the snapshot.

12. **Add to `CHANGELOG.md` `[Unreleased]`** — under `### Added — new skills`, one bullet:
    ```markdown
    - **`your-skill`** (wrapper). One-line description. Composes with X / Y.
    ```
    CI fails if a new skill folder is detected without a CHANGELOG entry.

### Verify locally

```bash
make validate         # frontmatter + cross-link + description-length + tag dict
make smoke            # all 14 gates (see below)
make test-unit        # runner unit tests alone
make check-docs       # README/USER-GUIDE/walkthroughs/CHANGELOG/SKILL-INDEX consistency
make lint-all         # writer linter across every reference/example/doc file (advisory)
shellcheck install.sh scripts/*.sh
```

All four required gates must be green before opening a PR (`lint-all` is advisory but recommended).

### Optional: local pre-commit hook

```bash
make install-precommit-hook
```

Installs `.git/hooks/pre-commit` that runs the writer linter on staged `.md` files and re-runs `make smoke` before each commit. Bypass once with `git commit --no-verify`. Uninstall: `rm .git/hooks/pre-commit`.

---

## Editing an existing skill

The bar is lower than adding a new skill but the gates are the same.

1. Make your edit.
2. Run the verification block above.
3. If you changed the `description:` field, make sure it's still ≤350 chars.
4. If you added or removed a reference file, make sure all SKILL.md cross-links still resolve (`validate.sh` checks this).
5. If you changed regex patterns in `skills/writer/scripts/lint.py`, snapshots will drift — re-run `bash tests/run.sh --update` and commit the new snapshots **along with the explanation** of why the linter changed in the PR description.

---

## Reporting a bug or false-positive

Use the issue templates at `.github/ISSUE_TEMPLATE/`:

- **bug-report** — installer broken, skill misbehaves, banner doesn't fire
- **false-positive** — the linter or a wrapper flagged something legitimate
- **new-skill-proposal** — propose a new skill before scaffolding it

Include:

- Output of `bash install.sh --check`
- Output of `bash scripts/validate.sh`
- The exact prompt + the unexpected output
- Your OS + Claude Code version

---

## Local development workflow

```bash
# clone
git clone https://github.com/Mikefluff/skills
cd skills

# install locally (uses ./ as source, not the upstream tarball)
bash install.sh --copy-from . --update

# edit a skill, then re-install
bash install.sh --copy-from . --update

# run all local CI gates
make validate
make smoke
make check-docs
shellcheck install.sh scripts/*.sh
npx -y markdownlint-cli2@0.13.0 "**/*.md" "#node_modules/**" "#.git/**"

# regen README skills table
make gen-readme

# add a new fixture + snapshot
echo "..." > tests/fixtures/new_fixture.md
bash tests/run.sh --update

# bump version + write release notes
make bump-minor   # or bump-patch / bump-major
git commit -am "chore: bump to vX.Y.Z"
```

---

## CI gates explained

The GitHub Actions pipeline runs four gates on every push:

### 1. `validate` (`bash scripts/validate.sh`)

For each skill:
- Frontmatter present and well-formed (`name`, `description`, `license`, `allowed-tools`)
- All `references/<file>` links in SKILL.md actually resolve to existing files
- `description:` is 120-350 chars (WARN >350; this WARN now fails the build at our policy)
- At least one example or reference file exists

### 2. `smoke` (`bash scripts/smoke.sh`)

Twelve gates, all must pass:

1. **validate** — all `validate.sh` checks
2. **linter regression** — `skills/writer/examples/before-after.md` must still read as neuroslop
3. **fixture snapshots** — `lint.py --json` on every `tests/fixtures/*.md`, byte-equal to `tests/snapshots/*.json`. On intentional drift, re-baseline with `bash tests/run.sh --update`
4. **AFTER calibration samples** — hard bans inside the "После" blocks of `examples/before-after.md`. These live in fenced blocks, which the linter masks, so they need their own pass
5. **relative links** — all ~1200 of them; `validate.sh` only resolves same-skill `references/`
6. **runner unit tests** — `tests/unit/`, stdlib `unittest`
7. **pricing doc ↔ `cost.PRICE_TABLE`** — the published prices are generated from the code that bills
8. **markdownlint** — pinned to the version CI uses, tracked files only
9. **linter coverage doc** — `docs/LINTER-COVERAGE.md` is generated from the category catalogue plus `lint.py`; it went stale silently once
10. **launch-thread tweet lengths** — every tweet in `docs/launch-posts/x-thread.md` fits 280 characters
11. **launch copy** — the drafts in `docs/launch-posts/` linted with fenced blocks scanned, against a baseline of reviewed quoted examples
12. **runners import** — every provider module imports and registers

### 2b. Code quality (`python3 scripts/check-code-quality.py`, gate 13/14)

Structural limits on the Python layer: module ≤400 lines (tests ≤900), function
≤50 lines, branch complexity ≤12, parameters ≤5. Plus two invariants:

- **contract** — every registered `Publisher` implements `publish()`, declares
  the attributes the CLI reads, and does not override `preflight()` (extend via
  `_extra_preflight()`, or the generic checks get skipped).
- **layering** — `publishers/`, `providers/` and `storage/` must not import
  `cli.`, and lower layers must not import upper ones.

19k lines predate these thresholds, so the gate runs against a frozen baseline
in `scripts/code-quality-baseline.json`. Anything **new** is a hard failure;
known violations are ignored until someone pays them down. The baseline may only
shrink — `--freeze` refuses to grow it, so adding debt takes a visible,
deliberate diff.

```bash
python3 scripts/check-code-quality.py            # gate — new violations only
python3 scripts/check-code-quality.py --report   # everything, baseline included
python3 scripts/check-code-quality.py --freeze   # after paying some down
```

The contract and layering checks have no baseline. They are invariants, not
debt — a publisher that skips its ABC is broken now, not gradually.

### 2c. CLI surface (gate 14/14)

Every module in `common/runners/cli/` must import and build its parser. The CLI
paths have no unit tests of their own, so this is what stands between a refactor
and a runner that dies on invocation.

### 3. `check-docs-consistency` (`bash scripts/check-docs-consistency.sh`)

Ten sub-checks, all must pass:

1. README table ↔ `skills.json` (auto-generated; if drift, run `make gen-readme`)
2. Skill folders on disk ↔ `skills.json` (new folder without manifest entry → fail)
3. Walkthrough `skills:` frontmatter list ↔ `skills.json` (unknown skill referenced → fail)
4. Every skill in `skills.json` is mentioned somewhere in `docs/USER-GUIDE.md`
5. New skill folders since the last `v*` tag are documented in `CHANGELOG.md` — in any section above the tagged version, not only `[Unreleased]`, because this repo writes version sections directly
6. `docs/SKILL-INDEX.md` ↔ `skills.json` (auto-generated; if drift, run `make gen-index`)
7. `Dockerfile` + `package.json` ship `skills/` and `common/`
8. Every price quoted in a doc is derivable from `cost.PRICE_TABLE` (`make check-prices`) — batch totals need a `<!-- prices: batch=N -->` declaration in the file
9. Every `skills.json` blurb was written against the current `SKILL.md` description (`make check-descriptions`; accept a change with `make freeze-descriptions`)
10. Every literal `python3 -m common.runners.cli.X --flag` in the docs uses flags that parser accepts (`make check-cli-docs`)

Checks 2 and 5 assert their scan found something before reporting green. They
both spent two years passing while matching nothing, because they searched the
pre-`skills/` layout — a gate that scans nothing looks exactly like a gate that
scans everything. Any new check that walks the tree should assert a floor too.

### 4. Shellcheck + Markdownlint

- `shellcheck install.sh scripts/*.sh` — 0 warnings
- `markdownlint-cli2` on `**/*.md` — the repo disables ~14 cosmetic rules in `.markdownlint.json`; what's left must pass

---

## Commit message convention

Conventional Commits, read by humans. Nothing parses them — the workflow that used to (`release.yml`, with `scripts/decide-bump.sh`) was removed for picking the wrong major bump on additive commits. The prefix tells the maintainer which `make bump-*` to run:

| Prefix | Triggers | Notes |
|---|---|---|
| `feat:` | minor bump | new feature, new skill, new walkthrough |
| `fix:` | patch bump | bug fix |
| `perf:` | patch bump | performance fix |
| `refactor:` | patch bump | non-behavioural refactor |
| `feat!:` or any `!:` | major bump | breaking change |
| `BREAKING CHANGE:` in body | major bump | breaking change |
| `docs:` | no release | documentation-only |
| `chore:` | no release | tooling, CI, scaffolding |
| `style:` | no release | formatting only |
| `test:` | no release | test-only |
| `ci:` | no release | CI config only |

These prefixes are a convention for readable history, not an automation trigger. Nothing parses them: the `release.yml` workflow that used to do so was removed for choosing the wrong major bump on additive commits.

Releases are cut by the maintainer:

1. `make bump-{patch,minor,major}` — writes `VERSION`, opens a CHANGELOG section
2. Fill in the CHANGELOG bullets
3. `make smoke && make check-docs`
4. `git commit -am "chore(release): vX.Y.Z"`
5. `make release` — verifies, tags, pushes
6. Publish the GitHub release, or `curl | bash` installs stay on the previous version

So: **as a contributor, do not tag releases** — but understand that no pipeline does it either. Full process: [`docs/VERSIONING.md`](docs/VERSIONING.md).

---

## PR checklist

When opening a PR, confirm:

- [ ] `make validate` passes (no WARN)
- [ ] `make smoke` passes (12/12)
- [ ] `make check-docs` passes (6/6 sub-checks)
- [ ] `python3 scripts/check-links.py` passes (or just run `make smoke`, which includes it)
- [ ] `shellcheck install.sh scripts/*.sh` exits 0
- [ ] `markdownlint-cli2` reports no errors
- [ ] If you added a skill: `skills.json` updated, README table regenerated, USER-GUIDE mentions it, CHANGELOG `[Unreleased]` has an entry, ≥1 fixture exists
- [ ] If you changed `skills/writer/scripts/lint.py`: regenerated all snapshots and explained the change in the PR description
- [ ] Commit messages follow Conventional Commits

The CI will run the same gates. If anything fails, the PR cannot merge.

---

## Code of conduct

Be specific. Be direct. No flame. If you disagree with a maintainer decision, open a Discussions thread with a concrete alternative and a reason — not a complaint.

---

## Questions

Open a [Discussions](https://github.com/Mikefluff/skills/discussions) thread for design questions or anything that isn't a bug / new-skill proposal.
