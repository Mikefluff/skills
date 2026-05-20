# tests/

Snapshot tests for `writer/scripts/lint.py`. They lock the linter's behaviour against a curated set of fixtures so a regex tweak that silently weakens detection (or over-fires on clean prose) fails CI instead of slipping into production.

## Layout

```
tests/
├── fixtures/                 # short Russian fragments designed to land in known verdict buckets
│   ├── neuroslop_full_pass.md   # 8+ categories — must be "neuroslop suspected"
│   ├── clean_prose.md           # natural prose — must be "clean" or borderline
│   ├── borderline.md            # 2-3 organic hits — must be "borderline"
│   ├── staccato.md              # Layer 2 territory — linter currently catches little here
│   └── ru_calques.md            # dev calques — terminology-heavy
└── snapshots/
    └── *.json                # frozen `python3 writer/scripts/lint.py <fixture> --json` output
```

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
   python3 writer/scripts/lint.py tests/fixtures/<name>.md --json > tests/snapshots/<name>.json
   ```
3. Commit both files. CI from now on will fail if the verdict drifts.

## What fixtures cover

- **neuroslop_full_pass**: regression against accidentally weakening 8+ categories at once
- **clean_prose**: regression against false-positives creeping into clean Russian
- **borderline**: regression on the 2-4 hit verdict boundary (changing thresholds in lint.py would break this)
- **staccato**: documents what we DON'T catch with regex (Layer 2 is LLM territory)
- **ru_calques**: regression against dev-calque category drift
