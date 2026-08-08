"""Everything `proposal-maker` needs to turn a telegram-style offer into HTML.

These six modules were `proposal_parse.py`, `proposal_render.py` and their four
siblings, sitting flat in `common/runners/` beside `cost.py` and `errors.py`.
Together they are 1,747 lines — one skill's implementation occupying a fifth of
the top level, so that reading the runner's layout told you more about
proposal-maker than about the runner.

Nothing here changed except the address. The pipeline still reads in order:

    parse  → the offer text becomes a plan (money, in every locale it arrives in)
    brand  → the client's site becomes tokens (palette, fonts, logo)
    kit    → screenshot, logo download, PDF, missing-item photos
    brief  → the authoring brief the orchestrator reads before writing HTML
    render → the deterministic `--quick` path, when no model is in the loop
    css    → render's stylesheet, split off when render outgrew the size gate
"""
