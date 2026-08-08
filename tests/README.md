# tests/

Three test layers, each locking a different thing: the linter, the runner, and the skill.

## Layout

```
tests/
├── fixtures/                 # short Russian fragments designed to land in known verdict buckets
│   ├── neuroslop_full_pass.md   # 8+ categories — must be "neuroslop suspected"
│   ├── clean_prose.md           # natural prose — must be "clean", zero hits
│   ├── borderline.md            # 2-3 organic hits — must be "borderline"
│   ├── staccato.md              # Layer 2 territory — linter currently catches little here
│   ├── ru_calques.md            # dev calques — terminology-heavy
│   ├── hard_bans.md             # every blocker category — gate must fail
│   ├── copypaste_artifacts.md   # class A markers + backticked ones that must NOT count
│   ├── structural_signals.md    # verb echo, heading echo, hedge cascade, colon reveal, gerund
│   ├── rhythm_monotone.md       # uniform sentence length — RHYTHM_MONOTONE only
│   └── fiction_dialogue.md      # em-dash dialogue — must pass under --fiction
├── snapshots/
│   └── *.json                # frozen `python3 skills/writer/scripts/lint.py <fixture> --json` output
├── unit/                     # stdlib unittest over common/runners — 80 tests, runs in CI
│   ├── test_cost.py             # the module that guards user money
│   ├── test_keysfile.py         # secret storage, masking, shell-export escaping
│   ├── test_poll.py             # async-vendor wait loop, time stubbed
│   ├── test_config.py           # provider registry + env resolution
│   └── test_proposal_parse.py   # money-amount parsing across locales
└── evals/                    # behavioural evals — need a model in the loop, NOT run by CI
    ├── README.md
    └── writer.json           # 9 scenarios / 49 checks, 7 of them guard traps
```

## Three layers, three failure modes

- **`fixtures/` + `snapshots/`** lock the *linter*: a regex tweak that silently weakens detection fails here.
- **`unit/`** locks the *runner*: the executable layer that spends the user's API budget. Chosen by risk, not by coverage percentage — `cost.py` decides what you get billed, `keysfile.py` handles secrets, `proposal/parse.py` reads the prices that reach a client. Plain `unittest`, no pytest, because the README promises no required dependencies.
- **`evals/`** locks the *skill*: whether the model invented a statistic or deleted the CTA. Needs a model, so it is not in CI.

Run the unit layer alone with `make test-unit`; see [evals/README.md](evals/README.md) for the model-in-the-loop layer.

Fixtures named `fiction_*` are linted with `--fiction`, which demotes the RU em-dash ban from blocker to nit. That mirrors `skills/writer/references/typography.md`, which bans the em-dash in prose but leaves book typesetting alone — without the flag, every dialogue line would fail the gate.

## Running

```bash
bash tests/run.sh              # compare each fixture to its snapshot, fail on drift
bash tests/run.sh --update     # re-baseline (only when you intentionally change the linter)
```

Smoke (`bash scripts/smoke.sh`) and CI both call `tests/run.sh` after the linter self-test.

## Updating snapshots

If you intentionally extend / refine the linter:

```bash
bash tests/run.sh --update
git diff tests/snapshots/      # inspect the deltas
git add tests/snapshots/
git commit -m "fix(writer): tighten DOUBLE_NEG_REGEX to skip idioms"
```

Snapshot drift WITHOUT a corresponding intentional change is the signal we care about — that's what CI catches.

## Adding a new fixture

1. Drop the new Russian fragment in `fixtures/<name>.md`.
2. Generate the initial snapshot:
   ```bash
   python3 skills/writer/scripts/lint.py tests/fixtures/<name>.md --json > tests/snapshots/<name>.json
   ```
3. Commit both files. CI from now on will fail if the verdict drifts.

## What fixtures cover

- **neuroslop_full_pass**: regression against accidentally weakening 8+ categories at once
- **clean_prose**: regression against false-positives creeping into clean Russian
- **borderline**: regression on the 2-4 hit verdict boundary (changing thresholds in lint.py would break this)
- **staccato**: documents what we DON'T catch with regex (Layer 2 is LLM territory)
- **ru_calques**: regression against dev-calque category drift
- **hard_bans**: every blocker fires and the gate reports `fail` — the gate is orthogonal to the density verdict, so this is the only fixture that locks it
- **copypaste_artifacts**: class A markers are caught inside URLs, and the same markers wrapped in backticks are NOT (quoting an artifact is not pasting one)
- **structural_signals**: the document-level detectors that regex-per-line cannot express
- **rhythm_monotone**: uniform sentence length alone must trip RHYTHM_MONOTONE without dragging in unrelated categories
- **fiction_dialogue**: the `--fiction` exception — dialogue em-dashes stay nits, gate passes
