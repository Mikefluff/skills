# Behavioural evals for the prose skills

`tests/run.sh` locks the **linter**. These lock the **skill**.

Different layer, different failure mode. A snapshot test proves `lint.py` still flags «представляет собой»; it says nothing about whether `writer` invented a statistic while removing it, or deleted the CTA along with the water, or swapped «ключевой` for «важнейший» and called it a day. Those are model behaviours, and regex cannot see them.

## Not run by CI

These require a model in the loop. There is no assertion harness here and no exit code — running an eval means giving a model the `prompt`, letting it apply the named skill, and checking the result against `expectations` (by hand or with an LLM judge).

Do not wire them into `smoke.sh`. A test that needs a model is not a smoke test.

## Categories

- **core** — ordinary cleaning. Does the skill do the obvious job?
- **saturated** — heavy slop across many categories at once. Does it catch everything, or stop at the first three?
- **guard** — the traps. Clean text that must come back untouched, slop that must not be swapped for kindred slop, functional elements that must survive, facts that must not be invented. **These are the ones that matter.** A skill that scores well on `core` and fails `guard` is worse than useless: it produces confident, clean-reading damage.

## Running one by hand

1. Paste the `prompt` into a session with the skill installed.
2. Take the output.
3. Walk the `expectations` list. Every item is a yes/no question with no room for interpretation — that is deliberate.
4. A failed expectation is a bug in the SKILL.md, not in the eval. Fix the instruction, then re-run.

## Adding one

Write the trap first, then the prompt that springs it. An eval that only confirms the happy path teaches nothing — every scenario here exists because there is a specific way for the skill to look successful while being wrong.

Expectations must be checkable without reading the original. «Итог короче» is checkable; «текст стал живее» is not.
