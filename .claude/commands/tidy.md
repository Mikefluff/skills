# Tidy — finish what the paydown left

The structural baseline is **empty**. `scripts/code-quality-baseline.json` has
no entries, so every gate is live: a new violation is now a hard failure with
nothing to hide behind. That is the regime this session works in.

What is left is not structure. It is four small defects, one unfinished
verification job, and the fact that several proofs from the paydown were run as
throwaway scripts instead of committed tests.

Argument (optional): a section letter from the table below. With no argument,
work the table top-down.

## Read first

```bash
python3 scripts/check-code-quality.py          # must print 0 known violations
make validate && make smoke && make test-unit && make check-docs
bash tests/run.sh                              # 31 writer snapshots
git log --oneline main..HEAD | head -25        # the paydown, if still unmerged
```

`CONTRIBUTING.md` §2b describes the gate. Thresholds: module ≤400 lines (≤900
for a module that declares only data — no `def`, no `class`), function ≤50,
branch complexity ≤12, parameters ≤5.

## The work

| # | Item | Size | Why it matters |
|---|------|------|----------------|
| A | Platform limits still marked `~` | 12 rows | **Start here.** The only sweep item from the paydown never touched. Four of these numbers were already wrong once. |
| B | Turn the equivalence probes into tests | 3 files | The paydown proved several refactors byte-identical with scripts that were then thrown away. The proof should live in the repo. |
| C | Four known defects | small | Each found by reading during the paydown, each deliberately left alone mid-refactor. |
| D | Remaining test gaps | ~5 modules | Ranked by what would actually catch something. |

## A — verify the platform limits

`skills/post-publisher/references/platform-limits.md` marks a row `~` when the number
came from a vendor parameter table that could not be machine-read. Twelve rows
carry it:

- **Telegram** — 4096 / 1024 caption split (line 31), 10 MB `sendPhoto` (58)
- **X** — 280 chars (35), 5 MB image / 512 MB video (62)
- **YouTube** — 100 title / 5000 description / ~500 tag chars (36), 256 GB / 12 h (63)
- **LinkedIn** — 3000 chars, 4086 altText (37), 10 MB / 500 MB (64)
- **Threads** — 1 GB video, explicitly "not stated in the docs read" (59)
- **TikTok** — 20 MB image (61)

For each: read the live vendor doc, then either move `~` → `✅` or correct the
number. **Update the constant and the table in the same commit** — they drift
apart otherwise, which is how the four wrong ones survived. Pin each verified
number with a test; `TestVerifiedPlatformNumbers` in `tests/unit/test_publish.py`
is the pattern. Record the date and the URL you read, as the existing header does.

Do not guess. A row you cannot verify stays `~` and says why.

## B — commit the equivalence proofs

Three refactors were verified against throwaway scripts in the scratchpad. The
harnesses were sound and the proofs are worth keeping:

1. **Cover typography** — `compose_book_cover` over all 5 imprints, sha256 of the
   PNG. Needs Pillow; skip cleanly when it is absent.
2. **Proposal HTML** — `render_html` across language × theme × brand
   (36 combinations in the paydown), sha256 of the document.
3. **Authoring brief** — `write_brief` across screenshot × logo × language
   (8 combinations), over an offer carrying both a total mismatch and a price
   outlier.

Golden-file or hash-pinned, either is fine. The point is that the next person to
touch `typography.py`, `proposal/render.py` or `proposal/brief.py` finds out from
a test rather than from a client.

## C — the four known defects

Each gets its own commit with a test that fails before the fix.

1. **`styles.anchor()` swallows an inline field.** `_starts_new_field` breaks on
   a line that starts with `**` *and ends with* `:`, so a field written as
   `**Best for**: weddings` directly under an anchor is absorbed into it. Every
   bundled style writes that field in block form, so nothing shipped is affected
   — but users are invited to author styles, and the anchor goes into every
   generated prompt. Pinned as current behaviour in
   `tests/unit/test_styles.py::Anchor::test_inline_field_does_not_terminate`;
   that test flips when you fix it.
2. **`cover_imprints.apply_text` mutates the shared preset.** It writes into
   `IMPRINTS[name].layout` in place, so a second `compose_book_cover` in the same
   process starts from the previous run's text — and `if layout.author is not None
   and author:` means an absent author leaves the previous one standing. One
   process per CLI invocation today, so it cannot bite; it will the moment
   anything batches covers.
3. **`cli/gif.py` has a `--yes` flag it never honours.** It advertises "skip cost
   confirmation (Mode B)" and no confirmation is ever asked — Mode B calls a video
   provider directly without a cost gate, unlike every other generating CLI.
   Either wire up `cost_mod.confirm` or drop the flag; do not leave it lying.
4. **`subtitle._cmd_burn` has an unreachable branch.** Its "provide --subtitle or
   --inline" error cannot fire: `build_parser` puts the two in a required
   mutually-exclusive group. Delete it; the parser's message is the real one.

## D — test gaps, ranked

Everything below has zero coverage. In descending order of what a test would
actually catch:

1. **`cli/proposal.py`** — the paydown's decomposition broke `_run_kit` with an
   unbound name and only an end-to-end run found it. Exit codes plus the two
   output modes' manifests.
2. **`proposal/brand.extract`** — the palette and font pickers are pure functions
   over HTML and were verified by diff, never by test.
3. **`cli/styles.py` + `_styles_submit.py`** — `submit` writes a package a human
   carries to GitHub; the `.format()` templates in it are one typo from shipping
   an unresolved `{placeholder}`.
4. **`batch.py` resume semantics** — exercised only indirectly through the maker
   CLIs.
5. **`reel.py` / `_reel_stitch.py`** — the stitch pipeline degrades rather than
   aborting at three separate points, and nothing checks that it still does.

## Rules

- **Behaviour does not change in a refactor.** A bug found on the way gets its
  own commit with its own test.
- **The baseline may not grow.** It is at zero. `--freeze` refuses to add, and
  there is nothing left to legitimately add.
- **Never raise a threshold to make something pass.** If one is genuinely wrong,
  change it deliberately, in its own commit, with the reason — the way the
  declaration-module cap was changed.
- **Run it, don't just import it.** Gate 14 proves a CLI imports. It does not
  execute one line of `main()`. Three of the paydown's five bugs were invisible
  to the whole test suite and turned up only when the command was actually run.
- **Verify a grep before trusting it.** One `| head` truncated a call-site search
  and shipped two `TypeError`s.

## Finish

Report as a table: item, before → after, what changed, how it was verified. Say
plainly what you did not get to and why.

```bash
python3 scripts/check-code-quality.py       # still 0
make validate && make smoke && make test-unit && make check-docs
bash tests/run.sh
```

Do not cut a release unless asked. If you do, tagging `v*.*.*` publishes the
Docker image, and gate 7 of `check-docs-consistency.sh` checks that the image
and the npm package still ship every registered skill.
