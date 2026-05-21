# Documentation

Hub for everything in `/docs`. If you're browsing on GitHub, this is the page you land on when clicking the `docs/` folder. From here, jump to whichever doc matches your task.

For the project overview + install + the skills table, go back to the top-level [`README.md`](../README.md).

---

## Getting started

| Doc | What it's for | Length |
|---|---|---|
| [QUICKSTART.md](QUICKSTART.md) | Your first 5 minutes — install → first prose edit → first AI image → first end-to-end | ~140 lines |
| [INSTALL.md](INSTALL.md) | Every install method: curl, npm, Homebrew, Docker, local checkout, pinned version, custom prefix | ~180 lines |
| [USER-GUIDE.md](USER-GUIDE.md) | The scenarios index — pick what you want to do, get a per-skill walkthrough | ~520 lines |

---

## Reference

| Doc | What it's for | Length |
|---|---|---|
| [SKILL-INDEX.md](SKILL-INDEX.md) | Every skill indexed by layer / domain / language. Auto-generated from `skills.json` | ~75 lines |
| [COMPOSING.md](COMPOSING.md) | How the 22 skills compose — dependency graph + named workflows + data flow table + anti-patterns | ~290 lines |
| [walkthroughs/](walkthroughs/) | 19 step-by-step recipes with categorized [index](walkthroughs/README.md) | ~200 lines each |
| [LINTER-COVERAGE.md](LINTER-COVERAGE.md) | Auto-generated regex coverage table for the `writer` linter (28 categories) | ~50 lines |

---

## Operations

| Doc | What it's for | Length |
|---|---|---|
| [FAQ.md](FAQ.md) | Short Q&A for the questions people ask first | ~190 lines |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Known failure modes + fixes (install, runtime, key issues, ffmpeg, …) | ~335 lines |
| [VERSIONING.md](VERSIONING.md) | Semver policy + manual release flow (auto-bump was removed in v2.1) | ~75 lines |
| [ROADMAP.md](ROADMAP.md) | Identified gaps + planned skills (cover-maker, avatar-maker, voiceover-maker, …) + non-goals | ~200 lines |
| [LAUNCH-POST.md](LAUNCH-POST.md) | Frozen launch copy from v1.9 — kept for posterity, not maintained | ~55 lines |

---

## Outside `/docs`

The skills themselves are at the repo root. Each has its own SKILL.md + references/ + examples/:

- **Base + linters**: [`writer/`](../writer/) · [`style-check/`](../style-check/) · [`translation-sync/`](../translation-sync/) · [`canon-check/`](../canon-check/)
- **Prose wrappers**: [`viral-text/`](../viral-text/) · [`prose-edit/`](../prose-edit/) · [`essay-write/`](../essay-write/) · [`tone-shifter/`](../tone-shifter/) · [`cold-email/`](../cold-email/) · [`microcopy/`](../microcopy/) · [`release-notes/`](../release-notes/) · [`rfc-writer/`](../rfc-writer/) · [`landing-copy/`](../landing-copy/) · [`pelevin-digression/`](../pelevin-digression/)
- **Media-gen wrappers**: [`image-prompt/`](../image-prompt/) · [`video-prompt/`](../video-prompt/) · [`music-prompt/`](../music-prompt/)
- **Orchestrators**: [`research-brief/`](../research-brief/) · [`carousel-builder/`](../carousel-builder/) · [`reel-builder/`](../reel-builder/)
- **Meta**: [`skills-update/`](../skills-update/) · [`skills-keys/`](../skills-keys/)

Shared infrastructure:

- [`common/runners/`](../common/runners/) — optional Python execute layer (31 providers, batch executor, ffmpeg wrappers, keysfile)
- [`common/style-library/`](../common/style-library/) — 50 bundled styles (24 carousel + 12 video director + 12 music genre)
- [`common/references/`](../common/references/) — shared anti-pattern catalogues (hype words, preambles, empty CTAs)

Project files:

- [`CHANGELOG.md`](../CHANGELOG.md) — every release, Keep-a-Changelog format
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — how to add a skill / report a bug / propose new one
- [`SECURITY.md`](../SECURITY.md) — disclosure policy
- [`.env.example`](../.env.example) — template for `~/.skills.env` (manage via `/skills-keys`)

---

## By task

If you know what you want to do but don't know where to look:

| Task | Start here |
|---|---|
| Install the collection | [QUICKSTART](QUICKSTART.md) · [INSTALL](INSTALL.md) |
| Pick a skill for a scenario | [USER-GUIDE](USER-GUIDE.md) |
| Chain multiple skills | [COMPOSING](COMPOSING.md) |
| Walk through a real example | [walkthroughs/](walkthroughs/README.md) |
| Manage API keys | [`/skills-keys`](../skills-keys/SKILL.md) · [usage reference](../skills-keys/references/usage.md) |
| Run the execute layer (image/video/music) | [`execute-end-to-end`](walkthroughs/execute-end-to-end.md) |
| End-to-end content (research → carousel + reel) | [research-to-carousel-reel](walkthroughs/research-to-carousel-reel.md) |
| Add a new skill | [CONTRIBUTING](../CONTRIBUTING.md) |
| Lint your repo's prose | [pre-commit-hook](walkthroughs/pre-commit-hook.md) · [LINTER-COVERAGE](LINTER-COVERAGE.md) |
| Browse the style library | [carousel styles](../common/style-library/carousel/_index.md) · [video styles](../common/style-library/video/_index.md) · [music styles](../common/style-library/music/_index.md) |
| Update the collection | [`/skills-update`](../skills-update/SKILL.md) · `bash install.sh --update` |
| Something is broken | [FAQ](FAQ.md) · [TROUBLESHOOTING](TROUBLESHOOTING.md) |

---

## Conventions

- Every doc has a single H1 at the top + nested H2/H3 for sections.
- Internal links are relative (Markdown `[text](path)`), never absolute URLs to github.com.
- Code blocks are fenced with a language hint where it matters (` ```bash `, ` ```python `, ` ```markdown `).
- File paths in prose are wrapped in backticks: `~/.skills.env`.
- The auto-generated docs (SKILL-INDEX, LINTER-COVERAGE) have a "do not edit by hand" comment near the top — they're regenerated from `skills.json` / source.
