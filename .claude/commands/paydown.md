---
description: Pay down the frozen code-quality baseline and run a full QA sweep
---

# Paydown + QA sweep

Clear structural debt from `scripts/code-quality-baseline.json` and fix whatever
else the sweep turns up. Argument (optional): a cluster name from the table
below, or a file path. With no argument, work the table top-down.

```
$ARGUMENTS
```

## Read first

```bash
python3 scripts/check-code-quality.py --report | grep -v '^!' | head -40
python3 scripts/check-code-quality.py            # must be green before you start
git log --oneline -8
```

`CONTRIBUTING.md` §2b describes the gate. The short version: thresholds are
module ≤400 lines, function ≤50, branch complexity ≤12, parameters ≤5. Known
violations are frozen; anything **new** is a hard failure. The baseline may only
shrink — `--freeze` refuses to grow it.

## The state as of the last session

114 frozen violations across 48 files. Zero in the publishing layer — that one
was refactored to zero and is the worked example of what "done" looks like
(`publishers/rules.py`, `publishers/_oauth.py`, `postsource.py`,
`cli/_publish_view.py`, `cli/_reel_stitch.py`).

| # | Cluster | Count | The move |
|---|---|---|---|
| A | `-maker` CLI `main()` × 9 (carousel, cover, flyer, banner, thumbnail, meme, quote, logo, avatar) | ~25 | **Start here.** They are near-identical: parse → resolve style → build plan → estimate → confirm → batch → print. Extract one skeleton into `cli/_maker.py` and let each module declare its differences. Nine separate edits would be the wrong answer. |
| B | Other CLI (`gif`, `styles`, `stylize`, `proposal`, `transcribe`, `upscale`, `subtitle`, `bg`, `mix`, `_shared`) | ~20 | Case by case. `cli/styles.py` (537 lines) and `cli/proposal.py` (`main()` at complexity 41) are the big two. |
| C | `providers/*.py` — `generate()` / `poll()` | 17 | Shared shape: build body → POST → handle error → poll → download. `kling`, `suno`, `google_video` are the worst. A `providers/_polling.py` helper likely collapses most of it. |
| D | `proposal_*.py` (`kit`, `parse`, `render`, `brand`) | 15 | `parse()` and `render_html()` both run >100 lines at complexity ~30-40. Real decomposition, no shared skeleton to lean on. |
| E | `writer/scripts/lint.py` (988 lines) | 6 | **Highest risk, do last.** It is the base linter every skill depends on, and 31 fixture snapshots pin its behaviour. Split by concern (catalogue / structural / rhythm / report) and lean on `bash tests/run.sh` after every step. |
| F | `runners` core (`ffmpeg` 7, `typography` 5, `styles` 5, `batch` 3, misc 4) | ~24 | Mostly `parameters` findings — signatures that grew into bags. A frozen dataclass per call is usually the fix, as `PostOverrides` was. |
| G | `scripts/*.py` | 7 | Small and safe. Good warm-up. |

## Rules for this work

- **Behaviour must not change.** Every one of these is a refactor. If you find a
  bug on the way, fix it in a separate commit with its own test.
- **Verify each cluster before moving on.** `make validate && make smoke &&
  make test-unit && make check-docs`, plus a real invocation of whatever you
  touched. Gate 14 (CLI surface) catches import-time breakage; it does not catch
  a changed exit code, so check those by hand the way the reel refactor did.
- **Shrink the baseline as you go**: `python3 scripts/check-code-quality.py
  --freeze` after each cluster, in the same commit. The count in the commit
  message is the point of the exercise.
- **Never raise a threshold to make something pass.** If a threshold is genuinely
  wrong, say so and change it deliberately, in its own commit, with the reason.
- **Do not touch `writer/scripts/lint.py` until the rest is done.**

## Also sweep for

Things known to be loose, beyond the baseline:

1. **Unverified platform limits.** `post-publisher/references/platform-limits.md`
   marks rows `~` where the number came from a vendor parameter table that could
   not be machine-read (Telegram's per-method limits, X's file sizes, YouTube's,
   LinkedIn's, Threads' video size). Verify against live docs, move `~` to `✅`,
   update the constant *and* the table together, and add a test pinning it —
   `TestVerifiedPlatformNumbers` in `tests/unit/test_publish.py` is the pattern.
   Four numbers were already wrong once; assume more are.
2. **`shellcheck` SC2015 in `scripts/smoke.sh`** (lines ~76, ~92) — pre-existing
   `A && B || C`, informational, but it is noise on every run.
3. **No unit tests for `common/runners/cli/`.** Gate 14 only proves they import.
   Characterisation tests for exit codes would make cluster A and B far safer;
   consider writing them *first* if you are touching those.
4. **`scripts/gen-skill-index.py:38`** — `LAYER_ORDER` omits `"orchestrator"`
   while `LAYER_HEADINGS` defines it, so all 14 orchestrators are missing from
   the "By layer" section of `docs/SKILL-INDEX.md`. One-line fix, needs
   `make gen-index` after.
5. **Dead imports.** Several modules import names they no longer use. A naive
   AST check gives false positives on `__future__`, `TYPE_CHECKING` and the
   self-registering provider/publisher imports in `config.py`, so it was not
   made a gate — check by hand while you are in a file.

## Finish

Report as a table: cluster, violations before → after, what was extracted, how it
was verified. State plainly what you did not get to and why. Then:

```bash
python3 scripts/check-code-quality.py       # confirm the new, smaller count
make validate && make smoke && make test-unit && make check-docs
```

Do not cut a release unless asked. If you do, remember that tagging `v*.*.*`
publishes the Docker image, and gate 7 of `check-docs-consistency.sh` checks
that the image and the npm package still ship every registered skill.
