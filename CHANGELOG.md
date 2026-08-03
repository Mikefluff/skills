# Changelog

All notable changes to this skill collection are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases are cut manually. Commit messages use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for clarity but no longer drive an automatic version bump — the previous `release.yml` GitHub Actions workflow was removed (was auto-tagging the wrong major bumps on additive commits).

## [Unreleased]

### Added — structural gates, and the publishing layer refactored to pass them

Two new smoke gates. `check-code-quality.py` enforces module ≤400 lines, function
≤50, branch complexity ≤12, parameters ≤5, plus two invariants: every registered
`Publisher` honours its ABC, and lower layers never import upper ones. The CLI
surface gate confirms all 26 CLI modules import and build a parser — those paths
have no unit tests, so it is the only thing between a refactor and a runner that
dies on invocation.

19k lines of Python predate the thresholds, so the gate runs against a frozen
baseline, the same shape `check-launch-copy.py` already uses here. Anything new
fails hard; the baseline may only shrink, and `--freeze` refuses to grow it. A
gate that fails the whole repo on day one gets disabled on day two.

The contract and layering checks have no baseline. They are invariants, not debt.

**The publishing layer now has zero violations**, which took four extractions,
each of which was worth doing on its own:

- `preflight()` was a 102-line method checking ten unrelated things. It is now
  `publishers/rules.py` — one function per rule, same signature, composed in a
  list. A rule can be tested against a stub instead of a whole publisher.
- Five publishers repeated the same forty lines of OAuth plumbing, and it had
  already drifted — the "is there a refresh token?" guard existed in three of
  them and not the other two. `publishers/_oauth.py` holds the shape; subclasses
  declare the endpoint and the payload.
- `cli/publish.py` was a 423-line module whose `main()` ran to 127 lines at
  complexity 36. Working out what a directory contains moved to `postsource.py`
  (domain logic, no argparse), rendering moved to `cli/_publish_view.py`, and the
  per-platform decision sequence became one readable function — that order *is*
  the safety contract, and it was hard to audit inside the loop.
- `build_post()` had grown to seven parameters that always travel together;
  they became a `PostOverrides` dataclass.

Outside the publishing layer, the worst function in the repository is gone:
`cli/reel.py:main()` ran 260 lines at complexity 60. It was already a pipeline —
the code had comments labelling "Stage 1/2/3" — so it became one: `load_plan`,
`prepare`, `estimate`, `run_shots`, `run_music`, and an ffmpeg stage in
`cli/_reel_stitch.py`. Verified by re-running `--cost-only`, the stdin path, and
every plan-error case against the original exit codes.

The gate found three violations in itself on first run, which is the correct
outcome for a tool with any authority, and two bugs worth recording: `--freeze`
refused to create the initial baseline because "0 → 116" reads as growth, and a
failure printed all 116 findings, which is a wall nobody reads.

114 known violations remain, all pre-existing, all frozen and visible. The
largest cluster is the twenty `-maker` CLI `main()` functions, which share a
shape and want a common skeleton rather than twenty separate edits.

## [2.21.1] — 2026-08-03

### Fixed — four platform constants were written from memory and were wrong

v2.21.0 shipped with a note in `platform-limits.md` reading "last verified: not
yet". Verifying it against the vendors' live documentation found four numbers
wrong, each in the direction that hurts:

- **Instagram's publishing cap is 100 posts per 24h, not 25.** Preflight would
  have blocked three quarters of a legitimate posting day, and the block was
  phrased as certainty.
- **Instagram Reels cap at 300 MB, not 1 GB.** A 700 MB reel would have passed
  preflight, been staged to S3, been fetched by Meta, and only then failed.
- **YouTube gives 100 `videos.insert` calls per day on their own allocation**,
  not 1600 units out of a shared 10,000/day pool. The old model is why the
  warning said "~6 uploads/day" — off by a factor of sixteen, in the direction
  that makes people ration something they have plenty of.
- **LinkedIn's pinned API version, 202401, had already aged out.** LinkedIn
  rejects versions older than roughly a year; the current moniker is 202607.

Also corrected: Telegram photos are held to sendPhoto's 10 MB rather than the
general 50 MB upload ceiling, and X's docstring no longer asserts a "17 posts
per 24h free tier" that appears nowhere in X's documentation — the verifiable
ceilings are 10,000/24h per app and 100/15min per user, and X has moved to
pay-per-usage pricing.

What was verified and found **correct**: every endpoint path and request shape
across all seven platforms; TikTok's chunking rules including the 5–64 MB range,
the floor-division chunk count and the single-chunk-equals-file-size rule;
X's `POST /2/media/upload` with INIT/APPEND/FINALIZE/STATUS on a Bearer token;
LinkedIn's `content.multiImage.images[]` shape with `id` + `altText`, its
`x-restli-id` response header and both required version headers; Threads'
container flow, 500-character limit, 2–20 carousel and 250/day cap; Instagram's
2200-character caption, 30 hashtags, 8 MB images, 10-item carousel and
`status_code` polling field.

Thirteen tests now pin the verified constants, because a plausible-looking wrong
number is invisible in review. `platform-limits.md` marks every row with whether
it was read off live documentation or carried from a parameter table, lists the
document behind each platform, and each corrected constant carries a comment
naming its source and date.

## [2.21.0] — 2026-08-03

### Added — new skills

- **`post-publisher`** (orchestrator). Publishes finished assets to Instagram, Threads, TikTok, X, YouTube, Telegram and LinkedIn through the official APIs. Composes with `carousel-builder` / `reel-builder` — it takes their output directory, reads `captions.md`, and sends it.

### Added — the collection can finally publish what it makes

Every skill here stopped at `./generated/`. Three separate places said so on purpose: `carousel-builder/SKILL.md` ("output is files you upload via the platform's UI / API"), `reel-builder/SKILL.md`, and `docs/walkthroughs/research-to-carousel-reel.md` ("that's a deliberate boundary — each platform's API has different OAuth flows"). The boundary was defensible when it was drawn and had simply stopped being: the OAuth flows differ, but they differ in ways one adapter layer absorbs.

`common/runners/publishers/` is a sibling of `providers/`, not a subclass of it. A provider turns a prompt into bytes, costs money, and can be retried for free; a publisher takes bytes that exist and does something irreversible with them. Shoehorning the second into `generate(prompt, **kwargs) -> bytes` plus `estimate_cost()` would have inherited the wrong invariants. So there is no cost estimation in the publishing layer, and in its place there is `preflight()` — which every caller runs before `publish()`, and which is a concrete method rather than an abstract one precisely so a subclass cannot forget to call `super()` and skip the file-exists check.

**Dry-run is the default and `--yes` is what leaves it.** That inverts the convention everywhere else in this repo, where `--yes` means "skip the cost prompt". The asymmetry is the point: a wasted generation costs cents, a wasted publish costs an audience. Even with `--yes`, each platform confirms separately — approving an Instagram post is not approval to also post to X.

`posted.json` receipts sit next to the assets, keyed on (platform, content hash). Re-running the identical command is refused; editing the caption makes it new content and it goes through. The hash fingerprints media by name and size rather than bytes, because hashing a 1 GB video on every dry run would be absurd and the case worth catching is "ran the same command twice".

State matters in that check, and a first pass that ignored it broke the workflow drafts exist for: staging a container, reviewing it, then publishing is the documented path for Meta and TikTok, and treating the draft as "already done" turned the second half into a `--force`. A publication is blocked only by a previous publication; a draft is blocked by either, since re-staging something already staged or already live has no purpose.

Four platform-specific decisions worth recording:

- **TikTok defaults to the inbox, not to publishing.** Direct posting requires passing TikTok's app audit; an unaudited app has every post silently forced to SELF_ONLY — the API returns success and nobody can see the post. That is the one failure mode in the set that reports itself as a success, so `--draft` routes to `/inbox/video/init/`, which needs no audit, and preflight warns loudly on the direct path.
- **Instagram uses Instagram Login, not Facebook Login for Business.** The older route additionally requires a linked Facebook Page, which most people publishing their own content neither want nor need. Business/Creator is still mandatory — there is no API path to a personal account, and `references/browser-fallback.md` says so rather than implying one exists.
- **The browser fallback is instructions, not code.** A Playwright robot holding social-network session cookies would be a worse thing to own than the problem it solves, and selectors rot on every redesign. It drives Claude in Chrome against the user's already-logged-in browser, stores nothing, and requires explicit consent per post.
- **Meta drafts became genuinely two-step.** A staged container is only useful if you can publish it later, so `--publish-container <id>` exists. Without it `--draft` on Instagram would have been decorative.

`common/runners/tokens.py` is a second credential store rather than an extension of `keysfile.py`. App credentials are long-lived and pasted by hand; user tokens expire in hours and arrive from an OAuth flow. Merging them would have meant sixteen generation providers carrying expired social tokens in `os.environ` at every runner startup. Tokens are never loaded into the environment — they are read on demand, refreshed transparently inside a 300-second skew window, and masked everywhere they are printed. `common/runners/atomicfile.py` now holds the secure-write helper both stores use.

Also: `scripts/validate.sh` only resolved `references/*.md` links inside the same skill, so any cross-skill reference was reported broken. It now matches `../other-skill/references/*.md` too.

144 new unit tests, none of which touch the network. Five of them exist because a review pass found the bugs they now pin: an explicit `--title` silently discarded on YouTube whenever the caption was empty (operator precedence — `(title or first_line) if text else "Untitled"`); a TikTok chunk plan that declared a 20 MB chunk for a 6 MB file, which TikTok rejects; Threads permanently unrefreshable because `tokens.py` hardcoded `"instagram"` as the one platform allowed to renew without a refresh token; a one-shot OAuth listener that a browser's `/favicon.ico` request could consume instead of the callback; and a partial-alt-text warning that the documentation described and the code did not implement.

### Fixed — the npm package and the Docker image shipped a 17-skill subset

Caught while deciding whether the release was safe to cut. Tagging `v*.*.*` triggers the Docker build, and the image would have gone out without `post-publisher` — along with 24 other skills.

`Dockerfile` and `package.json` both listed the same seventeen directories: exactly the v1.x prose set, frozen since around v2.3 while twenty-five skills were added around them. `skills.json` advertised all forty-two, so `install.sh` running inside the container warned about twenty-five missing skills — inside the artifact meant to contain them. The Dockerfile's own header claimed it ships "all skill markdown", which had quietly stopped being true.

The cost was never size. These are markdown directories; the rebuilt image is 117 MB and the skills contribute almost nothing to that. The subset was drift, not a decision.

Both lists regenerated from `skills.json`, and `check-docs-consistency.sh` gained gate 7 to compare them against it. That gate is the actual fix — the lists drifted for eighteen releases precisely because nothing compared them to anything. Verified it fails by removing a skill from each and watching it name both.

### Fixed — nothing was checking the launch copy

Caught by the user asking whether the rewritten posts had been run through the skills. They had not, and two layers of blindness met — both self-inflicted.

`lint.py` masks fenced code blocks by default, and the launch copy *is* the fenced block, so linting those files measured the surrounding notes. On top of that the files were marked `lint-role: catalogue`, which makes the pre-commit hook skip them entirely — correct for the hook, fatal as the only defence. The result: promotional copy for an anti-slop toolkit, written by a model, that nothing ever read back. The same structural blindness `check-after-samples.py` exists to fix, in a place the lesson was not applied.

Linted properly, the prose held up: every hit but two was a quoted example, since these posts legitimately print "revolutionary" and "delve into" as the things the linter catches. The two real ones were a closing line left over from the old draft ("highest-leverage 30 seconds you'll spend this week") and heavy bold density in the long-form pieces.

`scripts/check-launch-copy.py` added as gate 11/12. It scans fenced blocks and compares against a frozen baseline of reviewed (category, matched-text) pairs, so known quotes pass and anything new fails. Adding a genuinely new example means re-freezing the baseline on purpose, which is the review moment worth having. Verified it catches real slop by injecting some.

### Fixed — launch copy described a version that no longer exists

`docs/launch-posts/` still pitched v1.x: "17 skills", "12 wrappers", "28 categories", and DALL-E among the image models. The AI-media half and all 13 orchestrators — most of what the collection now is — went unmentioned. The Hacker News draft advertised "CI/CD with conventional commits → auto-release" for a pipeline removed several versions ago, and `docs/COMPOSING.md` was credited with 14 recipes against 5.

Two claims were measurably wrong. The linter was billed at "~50ms on a 5K-word file"; it is ~80ms in-process on 4K words and ~135ms through the CLI. And the X thread claimed "all tweets ≤280 chars (verified)" beside a verification one-liner that no longer parsed the file — two tweets were over.

All six drafts rewritten around what the project actually is now, leading with the two design decisions worth defending (copy-paste artifacts as a conclusive class; density and gate as separate outputs) rather than a feature list. `scripts/check-tweet-length.py` added and wired into smoke as gate 10/11, so the "verified" claim is now true. Launch files carry `lint-role: catalogue` — they quote the patterns they describe.

`README.md` also called `docs/LAUNCH-POST.md` "frozen v1.9 launch copy". It is the index of those drafts, and it was not frozen.

### Fixed — the gate was not actually orthogonal to the verdict

Two defects in this release's own work, both surfaced by the pre-commit hook during the docs audit.

**Hard bans counted toward the density verdict.** They were given `blocker` severity, and `verdict()` counted every non-nit hit. So `docs/walkthroughs/canon-check-audit.md` — one real slop marker, forty-eight ordinary Russian em-dashes — read as "neuroslop suspected". Before this release it read clean. Density now counts `caution` hits only. A typography choice is a house-rule violation, not evidence that a model wrote the text.

**Exit code 3 masked exit code 2.** `main()` returned `3 if hard_bans else code`, so a file that was both slop-dense *and* carried a hard ban returned 3 — and the pre-commit hook, which blocks on 2, let it through. Hard bans made the hook weaker. The hook now reads `verdict` and `gate` from `--json` as separate signals: it blocks on a `neuroslop suspected` verdict and reports a failed gate without blocking, because the gate targets prose deliverables and this repo's own Russian documentation legitimately uses em-dashes.

`--quiet` also stopped being quiet, printing the full report whenever a hard ban existed. Every commit was buried under hundreds of lines. It now honours its documented contract — emit only when the density verdict is not clean — and callers use the exit code.

### Fixed — documentation audit before going public

Counts that had drifted, phantom references, and rotted paths a link checker could not see.

**Stale numbers**, in README and four docs pages: "22 skills" against 41, "31 providers" against 32 (the audio tier grew to 3), "50 bundled styles" where 24 + 12 + 12 is 48, "28 categories" against the current 25. The README repo-layout block placed `SECURITY.md` under `.github/` when it sits at the root, and omitted `CODE_OF_CONDUCT.md`, `tests/unit/` and `tests/evals/`.

**Phantom tooling in `CONTRIBUTING.md`.** It credited commit parsing to `scripts/decide-bump.sh`, deleted alongside `release.yml` long ago — the same class of rot as the missing `bump.sh` this release already fixed. Its `smoke` section still described three checks against the current ten, and `check-docs` "five sub-checks" against six.

**Nine rotted backtick references.** `docs/walkthroughs/` pointed at `microcopy/references/banned.md` (is `banned-words.md`), `release-notes/references/banned.md` (is `banned-patterns.md`), `tone-shifter/references/markers.md` (is `transformation-rules.md`), `video-prompt/references/character-first.md` (is `identity-references.md`), and five more. Markdown-link checking never saw them because they are inline code, not links.

`scripts/check-links.py` now resolves backticked `<skill>/references/<file>.md` too — 1287 links, up from 1195. Scoped deliberately: broad path matching also hits user-project examples (`your-book/ru/chapters/ch07.md`), runtime outputs (`plan.json`, `script.md`) and `/tmp` paths, none of which exist in the repo. `CHANGELOG.md` is exempt, since a log names files that were later renamed.

**`docs/LINTER-COVERAGE.md` was stale and self-contradicting** — generated, but nothing compared it to its sources, so the new categories never appeared and a note claimed `SUPERLATIVE_OVERLOAD` was uncovered while the table showed five patterns. Another note called the em-dash "LLM territory" after it had become a hard ban. `scripts/coverage.py` gained `--write` / `--check`, wired into smoke as gate 9/10, and the doc now states which detector families it deliberately does not score: hard bans are pass/fail rather than density, and structural detectors are computed per document rather than matched per line.

One more private-path leak reached `common/runners/README.md` after the earlier sweep; genericized.

## [2.20.0] — 2026-07-31

### Added — `proposal-maker`: raw offer → brand-faithful HTML proposal

Takes a telegram-style offer (client, line items with catalogue links, total) and produces a self-contained `proposal.html` whose visual style is copied from a brand's website.

Default flow is LLM-authored: a Python step assembles the brand kit (site screenshot, logo, accent and font tokens, per-item catalogue photos, `BRIEF.md`), then the skill writes bespoke HTML mirroring that brand. Line items missing a photo get an on-brand generated image. Prices and links stay exact — nothing about the commercial terms is generated. Prints to a link-preserving, Ghostscript-compressed PDF.

`--quick` skips the brand scrape entirely and renders one of three deterministic themes (editorial / invoice / dark), for offline use or clients with no site. Saved brand profiles live in `proposal-maker/brands/` and are reusable across proposals for the same client.

### Added — `style-suggest`: description or reference image → visual-style entry

Authors a new entry for the shared visual-prompt style library that every image-producing skill reads (`carousel-builder`, `cover-maker`, `flyer-maker`, `quote-card-maker`, `banner-maker`, `logo-maker`, `thumbnail-maker`, `avatar-maker`, `meme-card-maker`).

Takes free-form text, a reference image, or both. Checks the catalogue for a near-duplicate first (similarity ≥ 0.72) and says so rather than growing the library with variations of the same look. Otherwise emits a complete v2.15.0 entry — background, accents, elements, mood, accent_text_color, typography, composition_signature, when_to_use — into `common/visual-prompt-library/styles/`, usable immediately.

Distinct from `skills-styles`, which manages the carousel / video / music library by hand. This one writes the entry for you.

---

Detection and discipline pass over the prose stack, adapted from [smixs/humanizer-ru](https://github.com/smixs/humanizer-ru) (MIT), which in turn credits [Vladimir-Human/humanizer-ru](https://github.com/Vladimir-Human/humanizer-ru) and [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (both MIT).

### Added — class A copy-paste artifacts: one hit is the verdict

`writer/scripts/lint.py` now catches the service markers that reach a text only by copying out of a chat UI: `:contentReference[oaicite:N]`, `turn0search3`, `utm_source=chatgpt.com`, `referrer=grok.com`, Gemini's `[cite: 8]` and `grounding-api-redirect`, `【12†source】`, `sandbox:/mnt/data/`, `</think>`, `ppl-ai-file-upload`, unfilled placeholders, PUA glyphs.

No editor and no CMS produces these, so they need no corroborating cluster — a single hit settles the question. Reported as `COPYPASTE_ARTIFACT` at `blocker` severity. Two deliberate exemptions: URLs are scanned rather than stripped (that is where `utm_source` lives), and backticked spans never count, because quoting an artifact in documentation is not pasting one. Zero-width characters are class B (`ZERO_WIDTH`, caution) — newsletters inject them too — with ZWJ inside emoji sequences explicitly allowed. Registry: `writer/references/copypaste-artifacts.md`.

### Added — a gate that is orthogonal to the density verdict

The linter now emits two independent results. `verdict` is unchanged (clean / borderline / neuroslop suspected) and stays a judgement call about slop density. `gate` is pass/fail on hard bans and is not a judgement call. A text can read clean and still fail the gate on one pasted `turn0search3`.

Hard bans wired as `blocker`: RU em-dash, math and code signs in prose (`= → > < ≈ vs`), completed negative parallelism («не только X, но и Y», «это не просто…»), chopped drama («Без X. Без Y.»), and class A artifacts. The `blocker` severity tier existed in the JSON schema but had no category assigned to it — it was dead code until now. New exit code `3` for a failed gate. New JSON fields `gate` and `hard_bans`.

`--fiction` demotes the em-dash ban to an advisory nit, matching the exception `writer/references/typography.md` already granted to book typesetting — without it every line of dialogue would fail.

### Added — structural detectors regex cannot express

Five document-level checks, none of which are phrase lookups:

- **`RHYTHM_MONOTONE` / `RHYTHM_NO_SHORT`** — mean difference between adjacent sentence lengths under 4 words, or no sentence under 9 words across 10+. Uniform sentence width is the LLM tell no word list catches.
- **`VERB_ECHO`** — the same verb stem in adjacent sentences. The repetition penalty makes models vary nouns (hence synonym cycling) while *duplicating* verbs into parallel constructions: «Сбербанк предлагает… Тинькофф предлагает…».
- **`BOLD_DENSITY`** — more than roughly one bold span per 200 words: formatting standing in for content.
- **`HEADING_ECHO`** — a short line after a heading that restates it. Stem-based, so it survives Russian inflection.
- **`HEDGE_CASCADE`** — three or more softeners in one sentence. One or two are ordinary careful speech and do not fire.

### Added — three new categories, two of them regex-backed

`THERAPEUTIC` («и это нормально», «вы не одиноки», "and that's okay") — fake care, distinct from `SELFHELP`'s fake drive. `CALQUE_COLLOCATION` («адресовать проблему», «доставить ценность») — every word Russian, the pairing English; distinct from the direct borrowings already in `ru-calques.md`. `DANGLING_GERUND` («используя метод, результаты улучшаются») — deliberately narrowed to a closed list of gerunds plus a required impersonal head, because a suffix guess would also match ordinary adjectives. `FALSE_RANGE` is documented but intentionally has no regex: legitimate ranges outnumber the slop.

Catalogue is now 25 RU categories + 18 EN signatures.

### Added — forbidden substitutions: slop replaced by kindred slop is still slop

New `writer/references/forbidden-substitutions.md`. The failure mode it guards against is mechanical: a repetition penalty pushes the model toward synonym substitution instead of deletion, so «ключевой» becomes «важнейший» and «не только X, но и Y» becomes «как X, так и Y» — same cadence, new packaging, cleaning pass scored as a success.

Contains the treatment hierarchy (delete → replace with a fact from the original → rewrite simpler; a synonym is level zero and does not count), the substitution table, three rules for how a replacement knits into surrounding text, and the "do not touch" list.

### Added — delete the water, not the function

The default treatment for slop is deletion, which is dangerous for text that has a job to do. A CTA, offer, price, deadline, link, contact, recovery step or upgrade command is a working part, not water — treat by replacement or simplification, then verify each survived.

Wired into `landing-copy`, `cold-email`, `microcopy`, `viral-text`, `release-notes`, and made a standing requirement for every sub-skill in `writer/references/integration.md`.

### Added — phase discipline and a stop rule in `writer`

Audit → edit → verify, and the phases do not mix. Editing while reading overwrites detection: a model that has started rewriting goes on to repeat its own phrasing and misses half the patterns, because it is reading its draft over the text rather than the text.

Phase 1 builds a findings table and edits nothing. **If there are no findings, stop and return the text unchanged** — re-editing clean text degrades it, and dry text with no catalogued patterns is just dry text, not AI. Phase 3 adds a blind verification pass: hand a fresh subagent only the final text and the category catalogue, with no original and no edit history, because an editor recognizes their own phrasing and grades it leniently.

### Added — `detect` mode in `style-check`

Answers "was this written by AI?" without touching the text. Scores findings by *family* (лексика / структура / коммуникация) rather than raw count: hits confined to one family are an author's style, hits spread across two or more are a model. Any class A artifact settles it alone.

Includes an explicit limit: flawless grammar, dryness and a wide vocabulary prove nothing, so report markers with quotes and let the reader conclude. Missing a machine-written text is cheaper than accusing a living author. See `style-check/references/detect-mode.md`.

### Added — prompt-injection guard

Text handed to `writer` is data, not instructions. Directives inside it («забудь правила», «выполни», «отправь») are edited as ordinary sentences, never executed; a noticed attempt is reported in the summary. Matters because these skills routinely process text pasted from clients, email and websites.

### Added — behavioural evals, a layer the repo did not have

`tests/evals/writer.json` — 9 scenarios, 49 checks. Snapshot tests lock the linter; these lock the skill. A snapshot proves `lint.py` still flags «представляет собой»; it cannot tell whether the model invented a statistic while removing it, deleted the CTA along with the water, or swapped «ключевой» for «важнейший» and stopped.

Seven of the nine are `guard` traps, and that ratio is the point: clean text that must come back untouched, slop that must not be replaced by kindred slop, functional elements that must survive, facts that must not be invented, a prompt injection that must not execute, fiction that must not be business-edited. A skill scoring well on the happy path and failing these produces confident, clean-reading damage.

Not wired into CI — they need a model in the loop, and a test that needs a model is not a smoke test.

### Fixed — the calibration samples the linter could never see

`scripts/check-after-samples.py`, wired into `smoke.sh` as step 4/5.

The hole it closes: calibration samples live inside fenced code blocks, and `lint.py` masks fenced blocks by default. So the one thing a model copies verbatim — the "После" sample — was the one thing never checked. Six real violations were sitting in them, including an em-dash in `landing-copy`'s hero sample and in `microcopy`'s empty-state body, both of which the skills would have reproduced.

Fixed in `landing-copy`, `microcopy`, `release-notes`, `rfc-writer`. Scope is deliberately narrow: only `EM_DASH_RU`, `NEG_PARALLEL` and `CHOPPED_DRAMA` are checked. `MATH_SIGN_PROSE` is excluded because inside samples the signs are usually legitimate — RFC specs (`p95 ≤ 5 с`), UI paths (Настройки → Тема), parity-report output — and flagging those would teach people to ignore the check.

Files whose samples are not ordinary prose declare it inline: `<!-- after-samples: fiction -->` for dialogue dashes and lyrics (`writer`, `music-prompt`), `<!-- after-samples: none -->` for tool output (`translation-sync`).

### Fixed — docs consistency

`docs/USER-GUIDE.md` claimed thirty-nine skills against forty-one on disk, carried two duplicate **Meta** bullets, and never mentioned `proposal-maker` or `style-suggest`. Census corrected, duplicate merged, both skills given working sections. `README.md` table and `docs/SKILL-INDEX.md` regenerated.

Check 5 in `check-docs-consistency.sh` scanned only `[Unreleased]` for new-skill entries. This repo writes version sections directly and cuts tags manually — the last tag is `v2.12.3` while the changelog is seven minors ahead — so a skill shipping in an untagged 2.20.0 could never satisfy it. The window now spans every section above the last tagged version. Verified it still fails when an entry is genuinely absent.

### Fixed — link rot that no check could see

`scripts/check-links.py`, wired into `smoke.sh` as step 5/6. Resolves all 1180 relative markdown links across 460 files.

`validate.sh` greps for `references/<file>.md` and resolves it inside the *owning* skill, so three whole classes of link were never checked, and all three had rotted: cross-skill links from `docs/walkthroughs/` into `../../<skill>/references/`, docs-to-docs links, and repo-root links from `.github/` templates. Seven were broken, every one of them in public-facing documentation — `image-prompt/references/formula.md` (is `prompt-formula.md`), `landing-copy/references/julian-shapiro-hero.md` (is `hero-formula.md`), `release-notes/references/keep-a-changelog.md` (is `sections.md`), `rfc-writer/references/adr-template.md` (is `templates.md`), `video-prompt/references/kling.md` (is `models/i2v-tier.md`), a wrong relative depth in `canon-check`, and a malformed `../blob/main/` path in the PR template.

Placeholders are skipped rather than reported: a target containing angle brackets, `...` or a bare curly slot documents a format, it is not a link.

### Fixed — markdownlint ran only in CI, so it failed only after push

The generated pricing table ended on a double blank line (MD012). Local smoke had no markdownlint step, so the first CI run on this release failed on a one-character problem that could not be seen before pushing.

Smoke now runs it as step 8/9, pinned to `markdownlint-cli2@0.13.0` — the version `markdownlint-cli2-action@v16` uses. A newer local version reports rules CI does not have (MD060 fires across 157 files) and would have made the step permanently red. Tracked files only, since `generated/` is ignored.

### Fixed — HEADING_ECHO flagged ordinary documentation

Caught by the pre-commit hook refusing this very release, which is what the hook is for.

The first cut counted *shared* stems between a heading and the line under it. That also matches a section's opening sentence, which naturally reuses the section's topic: `## Where the canon may live` → "Non-fiction projects split canon across two sources:" shares three stems and is not an echo. It also matched cross-references — `### Artifact / physical invariant` → "In `Physical invariants`:".

The discriminator is *restates vs. adds*, not overlap. An echo introduces almost nothing beyond the heading; a real opening sentence introduces several new stems. Now fires only when the line adds two content stems or fewer, and backticked spans are stripped first so an identifier reference is not read as prose.

### Changed — `<!-- lint-role: catalogue -->`

Several `SKILL.md` files list the phrases they exist to strip ("world-class", "Click here", "revolutionary"), and walkthroughs demonstrate slop being cleaned. Linting those for slop measures the examples, not the prose — they were failing the pre-commit hook before this release too, on pre-existing categories.

The hook already exempted `banned-patterns*.md` by path. A file now declares its own role instead, so that list stops growing every time a skill documents what it bans. Applied to `landing-copy`, `release-notes` and the EN viral-post walkthrough.

### Added — unit tests for the layer that spends money

`tests/unit/` — 80 tests over `common/runners`, wired into `smoke.sh` and CI. Plain stdlib `unittest`, no pytest: the README promises no required dependencies and this keeps that true.

Chosen by risk, not by coverage percentage. `cost.py` decides what the user gets billed and whether to prompt at all — a wrong multiplier there does not fail loudly, it silently overcharges. `keysfile.py` writes secrets to disk, loads them into the environment, and prints them back to a terminal; the tests pin file mode `0600`, that `mask()` never shows the middle of a key, that a shell export escapes quotes and backslashes (an unescaped quote in `eval "$(...)"` becomes executable words), and that a deliberate shell export still beats a file entry. `proposal_parse.py` reads the prices that reach a client, where `5,154` misread as a decimal is an error of three orders of magnitude. `poll.py` runs with a stubbed clock, so the suite finishes in 0.07 s and still proves backoff grows, stays capped, and never sleeps past the caller's timeout.

This is the highest-risk surface, not full coverage of 13 500 lines. The rest of the runner layer remains untested.

### Added — pricing generated from the code that bills

`scripts/gen-pricing.py` renders `common/references/model-pricing.md` from `cost.PRICE_TABLE`, with `--check` failing CI on drift (step 7/8 in smoke, `make gen-pricing` to regenerate).

Per-unit prices were hand-written into ten `model-picker.md` files. They happened to agree, but nothing enforced it, and none of them were tied to the table that actually estimates the bill. A documented price that disagrees with the charged price is worse than no price. All ten now point at the generated table as canonical and keep their own figures as batch illustrations.

### Fixed — the release process was broken end to end

`scripts/bump.sh` did not exist, yet `make bump-patch|bump-minor|bump-major` called it and `docs/VERSIONING.md` documented it. Every path to cutting a release failed with `No such file or directory`, so `VERSION` was edited by hand and tagging quietly stopped. The last tag sat eight versions behind the changelog — and because `install.sh` defaults to `--version latest`, resolved from the newest published GitHub *release*, the `curl | bash` command in the README was serving v2.12.3.

- **`scripts/bump.sh` written** — bumps `VERSION`, opens a CHANGELOG section, refuses to reuse an existing tag, supports `--dry-run`. It deliberately does not commit, tag, or push.
- **`make release` hardened** — now verifies the tag is free, that `CHANGELOG.md` has a section for the current `VERSION`, and that `smoke.sh` passes, before tagging. It no longer claims "release workflow will fire"; it prints the reminder that a tag without a published release leaves installs on the previous version.
- **`docs/VERSIONING.md`, `CONTRIBUTING.md` and `docs/FAQ.md` corrected.** All three described the auto-bump pipeline as live. `CONTRIBUTING.md` instructed contributors "do not manually tag releases — the pipeline does it", which was exactly backwards.

### Fixed — pre-publication hygiene

- **Private paths.** Five live files referenced an absolute path into the author's private project (`/Users/mikefluff/Documents/figma/...`) as the origin of a ported pattern. Genericized in `common/runners/config.py`, `poll.py`, `storage/s3.py`, `common/visual-prompt-library/system-prompt.md` and `styles/_index.md`, and in `style-suggest`. The CHANGELOG keeps its historical entries — a log records what was true when written.
- **Stale counts.** `README.md` said thirty-nine skills against forty-one, with eleven orchestrators against thirteen. `scripts/coverage.py` still documented 23 categories.
- **A promise in the docs.** `carousel-builder/references/troubleshoot.md` told users to run `--list-styles (TODO: implement)`. Replaced with the two things that do work.
- **`CODE_OF_CONDUCT.md`** added — deliberately short, since a long one on a project this size reads as process theatre.
- **Client brand profiles are no longer published.** A saved `proposal-maker` profile carries a named client's brand tokens, their logo, and the authored structure of their real commercial offer. `.gitignore` now excludes `brands/*/` with an exception for the author's own brand, which stays as a worked example of the format. The Double D Project profile was untracked; the files remain on disk and keep working.

### Changed — test fixtures

Five new fixtures: `hard_bans`, `copypaste_artifacts`, `structural_signals`, `rhythm_monotone`, `fiction_dialogue`. `tests/run.sh` now passes `--fiction` for fixtures named `fiction_*`. `clean_prose.md` lost its two em-dashes — they violated `typography.md`, and the linter simply never checked before. All 30 snapshots re-baselined for the new `gate` / `hard_bans` JSON fields.

## [2.19.0] — 2026-07-11

### Added — `carousel-builder --animate`: one-command carousel → animated reel

The carousel → animation pipeline no longer requires manual reel-plan assembly. With `--animate`, after the static deck renders, the skill spawns ONE Agent with the canonical video SYSTEM_PROMPT (`common/video-prompt-library/system-prompt.md`), passes each slide PNG + a one-line overlay-text summary + the character-identity marker, receives all N motion prompts in a single JSON, mechanically builds `reel-plan.json`, and runs the reel CLI. Flags: `--animate-duration 4|8` · `--animate-provider veo-3-1-fast|veo-3-1|kling-3-0|runway-gen-4` · `--animate-stitch on|off`. Labels are validated to start with `shot-` (the reel CLI's filter).

### Added — provider parity for text-stability kwargs (Kling + Runway)

`lock_first_last` / `last_frame` now work across all three i2v providers with one kwarg contract:

- **`kling.py`**: `lock_first_last=True` → Kling's native `image_tail` bookend (start == end). Local paths are base64-encoded for both `image` and `image_tail` (Kling accepts URL or base64).
- **`runway.py`**: `lock_first_last=True` → Runway's First/Last-Image mode (`promptImage` as `[{uri, position: "first"}, {uri, position: "last"}]`). Local paths become data URIs. Runway has no `negative_prompt` parameter — the kwarg is intentionally ignored there.
- **`google_video.py`** (since v2.18.0): `last_frame` + `negative_prompt`, with graceful fallback when a preview model rejects `last_frame`.

### Added — orientation lock + wardrobe continuity in the image SYSTEM_PROMPT

Two field-tested rules added to `common/visual-prompt-library/system-prompt.md`:

- **Orientation lock**: every prompt must OPEN with an orientation cue ("Vertical portrait composition, taller than wide —"); "wide / panoramic / cinematic POV" openers are banned on portrait/square because image models let prompt language override the size kwarg (two slides rendered landscape in production because a prompt opened with "wide cinematic POV").
- **Wardrobe continuity**: when a character ref is present, every slide's prompt carries a generic wardrobe-continuity clause ("the same 3D-cartoon figure in the same hat, glasses, and outfit as on every slide") — naming accessory CATEGORIES generically keeps them present across slides without overriding their look (fixes hats/glasses vanishing on individual slides).

Both SYSTEM_PROMPTs now cross-link each other (image chain ↔ video chain).

### Added — brand-profile registry for proposal-maker (documents v2.18.1+ work)

The 4 previously-unversioned commits (Double D Project + INITE brand profiles) are now first-class: `proposal-maker/brands/_index.md` registry + a "Saved brand profiles" section in SKILL.md. Each `brands/<slug>/` holds a corrected `brand.json`, an authored `template.html` to clone, cached assets, and reuse README. Prefer `--brand-file brands/<slug>/brand.json` over a fresh scrape — profiles encode manual corrections (dark Tilda sites scrape as light; white SVG logos vanish on light surfaces).

### Changed — reel output dedup

`reel.py` no longer copies the stitched video into `final.mp4` when no transformation remains — it renames instead. A music-less, caption-less reel dir now holds ONE multi-MB video (final.mp4), not two identical ones (concat.mp4 + final.mp4).

### Docs

- README: style-library section now lists BOTH libraries (legacy per-modality `common/style-library/` + extensible `common/visual-prompt-library/styles/`, 23 entries), links both LLM prompt chains, and the brand-profile registry.
- USER-GUIDE: new "commercial proposal (КП)" scenario section; carousel section gained the `--animate` block.

## [2.18.1] — 2026-06-20

### Fixed — skill descriptions tightened for Claude ingest

27 SKILL.md `description:` fields were over 350 chars (`proposal-maker` was 1066, over Claude Cowork's 1024-char hard limit). Rewrote each to ≤350 chars while preserving every trigger phrase (EN + RU) — only implementation detail and feature lists were cut. Output: skills now register cleanly in Claude Cowork / claude.ai / Anthropic Skill ingest pipelines, and the matching signal is sharper (the writer-linter's preferred sweet spot is 120-300; most landed at 300-340).

Skills touched: audio-mix-maker, avatar-maker, banner-maker, bg-remover, carousel-builder, cover-maker, flyer-maker, gif-maker, image-prompt, logo-maker, meme-card-maker, music-prompt, proposal-maker, quote-card-maker, reel-builder, research-brief, rfc-writer, skills-keys, skills-styles, style-suggest, style-transfer, subtitle-burner, thumbnail-maker, transcribe-maker, upscaler, video-prompt, voiceover-maker.

## [2.18.0] — 2026-06-20

### Added — canonical video-prompt SYSTEM_PROMPT chain (rules-driven, not hand-written)

New `common/video-prompt-library/system-prompt.md` — sibling to the existing `visual-prompt-library/system-prompt.md`. Encodes 12 rules for overlay-heavy i2v on Veo 3.1 / Veo 3.1 Fast / Kling / Sora / Runway: 2-sentence cap, 80-word cap, one motion verb per shot, identity front-loaded in 8-15 words, verbatim global lock sentence (`Keep everything else still. Maintain the style of the image.`), no rhetorical adjectives, no punitive labels (avoid Veo's safety filter), no negation of locked props, contact-motion described as subject-anchored not target-anchored ("the hand lowers 3 cm in place", not "taps onto the paper"), text-overlay preservation via `last_frame == image` bookend + `negative_prompt` text-stability payload.

`reel-builder/SKILL.md` step 6 now spawns ONE Agent with this SYSTEM_PROMPT and gets all N shot prompts in a single JSON response — the same pattern the carousel chain has used since v2.13.0. Per-shot subagent calls break identity consistency across the reel.

### Added — Veo 3.1 text-overlay preservation (provider level)

`common/runners/providers/google_video.py` now accepts:

- `kwargs["lock_first_last"] = True` — passes the source frame as both `image` AND `last_frame` to the Veo API. Per Google's docs, `last_frame` is "the only documented mechanism for constraining drift" in i2v — when start == end, typography drift collapses. This is the single highest-ROI lever for text wobble on dense overlays.
- `kwargs["negative_prompt"] = "<phrases>"` — Veo's `negative_prompt` config field. Expects comma-separated PHRASES not negations. Default text-stability payload (set by SYSTEM_PROMPT rule 12): `"text warping, glyph distortion, melting letters, flickering text, re-rendered text, subtitle, caption overlay, watermark change, blurred text, deformed letters, no subtitles"`.
- Graceful fallback: some preview model IDs (notably `veo-3.1-fast-generate-preview`) reject `last_frame` with a 400 "use case not supported". Provider catches the error and retries once without `last_frame` (other levers stay active); surfaces a stderr `⚠` note so callers know the drift-lock didn't activate. For full text preservation on overlay-heavy reels, opt into `veo-3-1` (non-Fast) at ~4× cost.

### Added — 4 new visual styles (23 total in the library)

- **`servers-not-staff`** (FAKE AI-WORKFORCE EXPOSÉ) — Apple-showroom Mac Mini stack with employee-badge cards defaced by "NOT AN EMPLOYEE" stamps, fake org-chart, HR-audit form with 10 accountability questions stamped UNDEFINED, architecture-blueprint comparison side. For "AI workforce" / "цифровые сотрудники" grift critiques.
- **`ownership-ledger`** (TAKEN-BY DOCTRINE) — executive ledger paper + brass desk-lamp + wax-seal aesthetic. "TAKEN BY" signed lines vs "ADVISED ONLY · NO SIGNATURE" stamps. For ownership / skin-in-the-game / responsibility-as-income essays.
- **`rough-and-cut`** (DIAMOND DOCTRINE) — gemmologist's bench, dusty pile of rough stones with handwritten paper-tag grievances vs single cut diamond on black velvet with brass plaque verdict. For emotional-maturity / "люди как алмазы" / grievance-as-inclusion psychology pieces.
- **`mission-control`** (CONTROL-LOOP DOCTRINE) — NASA Apollo-era dispatcher's pit, wall of red EXECUTOR ALERT lamps vs one steady green OWNER · DELIVERED CRT, corkboard red-yarn schematic, brass desk-mike. For executor-vs-owner / "исполнительность ≠ ответственность" / AI-era execution-cheapening essays.

All four follow the per-file extensible-library schema (frontmatter + body) introduced in v2.15.0. Indexed in `styles/_index.md`, auto-pick rows added to `styles/_auto-pick.md` so they resolve via `--style auto`.

### Fixed — reel concat order respects plan index, not file-finish time

`common/runners/cli/reel.py:281` previously sorted concat inputs by filename (which begins with finish timestamp) — when shots run in parallel or get retried via `--resume`, finish order ≠ plan order, and final.mp4 played shots out of sequence (e.g. `1,3,2,5,4` for a parallel run). Now sorts `shots_result.succeeded` by `item.index` from the plan. Concat order is now strictly 1→2→3→…→N regardless of how shots finished.

### Internal — i2v discipline docs synchronized

`video-prompt/references/i2v-prompting.md` is the human-facing rationale; `common/video-prompt-library/system-prompt.md` is the LLM-facing rule list. The references file now mirrors the SYSTEM_PROMPT's rules 1-12 with worked before/after examples. Memory `feedback_reel_chain.md` codifies "rules not hardcode" as a recurring lesson.

## [2.17.0] — 2026-06-03

### Added — `proposal-maker` skill (brand-copying commercial proposal generator)

New top-level skill `proposal-maker/` — a new **document** modality (HTML/PDF) distinct from the visual-generation skills. Turns a raw, telegram-style commercial offer (client block + itemised order with catalogue links + total) into a beautiful, self-contained `proposal.html` whose visual style is **copied from a website**. Built and verified against the Double D Project event offer (`www.doubledproject.com`).

Why a document, not an image deck: a proposal carries **exact prices** and **clickable product links** — AI image generation garbles both. The renderer emits real HTML text; only `requests` (already a dependency) is required.

**Default flow is LLM-authored, screenshot-driven.** A `proposal_kit.py` step builds a *brand kit* — a headless-Chrome **screenshot** of the brand site, the downloaded logo, resolved tokens, the enriched offer, and a `BRIEF.md` — then the orchestrator *looks at the screenshot* and *authors bespoke HTML* mirroring the brand (dark/light mood, type, accent, logo treatment), rather than filling a fixed template. This fixes two real defects of a pure deterministic renderer: dark sites (Tilda/Webflow serve white-heavy CSS) were misread as light, and white/monochrome logo SVGs vanished on a light theme. The deterministic 3-theme renderer remains as `--quick` (offline / no-LLM).

### Skill files

- **`proposal-maker/SKILL.md`** — orchestrator: capture offer → resolve brand (auto-detect site from offer footer, `--brand-url`, `--brand-file`, or manual overrides) → enrich items → render → surface data-quality warnings → deliver.
- **`proposal-maker/scripts/run.py`** — venv bootstrap delegating to `common/runners/cli/proposal.py` (same pattern as flyer/cover).
- **`proposal-maker/references/`** — `offer-format.md` (parse contract), `brand-extraction.md`, `templates.md`, `troubleshoot.md`.
- **`proposal-maker/examples/before-after.md`** — the Double D offer rendered in all three themes + outlier handling.

### Execute layer (`common/runners/`)

- **`proposal_parse.py`** — pure-stdlib offer parser. RU/EN header aliases, item-line grammar `Name (url) qty — price CUR` (currency symbol may lead or trail; space/comma/European decimals), recomputed subtotal, `total_mismatch` flag, and `price_outliers` (a single line ≥60% of total — flags the seed offer's erroneous `5 000 000` logistics line; never auto-corrects). Emits `skills.proposal.plan.v1`.
- **`proposal_brand.py`** — `requests` + regex brand extractor: accent/secondary colour (frequency-ranked, saturation/luminance filtered), heading/body fonts + Google Fonts link, logo (og:image / `img[logo]` / favicon), name + tagline. `enrich_items()` thread-pooled per-item `og:image`/`og:description` fetch (failure-tolerant). Calibrated on doubledproject → `#99cc66` + Ubuntu.
- **`proposal_render.py`** — pure-Python HTML assembly, brand tokens as CSS custom properties, three themes (editorial / invoice / dark), per-item photo cards, `@media print` rules, RU/EN labels, currency formatting, `--embed-images` base64 inlining, and best-effort `to_pdf()` (Playwright → WeasyPrint).
- **`proposal_kit.py`** — brand-kit collector: cross-platform headless-browser screenshot (`find_browser()` / `capture_screenshot()`), logo download, `write_brief()` (tokens + item table + authoring rules incl. the print-colophon recipe), and `print_pdf()` (system-browser print-to-PDF — no Python deps, preserves links + dark full-bleed; Playwright/WeasyPrint fallback) followed by a Ghostscript image-shrink pass (`find_ghostscript()` / `_gs_shrink()`, `/ebook` @ 144 dpi → ~15 MB to ~0.5 MB, links intact). Exposed via `--pdf-from <html>` / `--pdf`, with `--no-compress` and `--pdf-dpi`.
- **Print colophons.** The authoring recipe specifies `@page{margin:0}` (no white margins, full-bleed) + running header/footer via the table `<thead>`/`<tfoot>` pattern with gap padding on the head/foot `<td>` — uniform per-page spacing that `position:fixed` bands can't achieve (they reserve space only on the first/last page). `break-after:avoid` keeps category headers from orphaning.
- **Missing-photo pickup.** `proposal_kit.generate_photo()` / `fill_missing_photos()` — any service the offer left without a catalogue link gets an on-brand, photoreal image generated via the runner's image layer (gpt-image-2 / Imagen / Nano Banana, keys from `~/.skills.env`), saved to `<out>/img/` and wired into the item. `--no-gen-photos` opts out; graceful when no key is set.
- **Category grouping + density.** Authoring rules (BRIEF + SKILL) now require items grouped into 4–7 categories with per-category subtotals, and a mixed layout — big photo cards for showpieces, compact 2-column rows for utility/low-cost items — instead of one uniform pile.
- **`cli/proposal.py`** — orchestration; default = build kit and stop for LLM authoring, `--quick` = deterministic template. Flags (`--offer`, `--brand-url|--brand-file|--no-brand`, `--accent/--font/--logo/--brand-name`, `--quick`, `--template`, `--lang`, `--no-thumbnails`, `--embed-images`, `--currency`, `--pdf`, `--parse-only`, `--check`).

### Registration

- `skills.json` — added `proposal-maker` entry; version bumped to `2.17.0`.
- `VERSION` → `2.17.0`.

## [2.16.0] — 2026-05-22

### Added — `style-suggest` skill (visual-style generator)

New top-level skill `style-suggest/` adapted from figma's `app/lib/agents/StyleSuggestAgent.js`. Takes a user description (text and/or reference image), checks the existing catalog for duplicates (similarity ≥ 0.72), and either points the user to the existing style OR produces a full v2.15.0-schema entry ready to drop into `common/visual-prompt-library/styles/`.

### Skill files

- **`style-suggest/SKILL.md`** — orchestration instructions: read catalog → compose LLM call → validate output → present proposed entry → save on confirmation.
- **`style-suggest/references/system-prompt.md`** — the SYSTEM_PROMPT for the LLM analysis step (verbatim, adapted from figma StyleSuggestAgent). Includes:
  - The duplicate-detection contract (`action=duplicate` vs `action=new`).
  - The full v2.15.0 schema fields the LLM must fill for new entries (9 fields + optional body_notes + optional auto_pick_signal).
  - Forbidden literals list (no layout labels / hex codes / platform names / named fonts / copyrighted brand names in structured fields).
  - Vocabulary-preservation rule (don't replace user terms like "oxblood leather" with generic synonyms).
- **`style-suggest/examples/before-after.md`** — 3 calibration runs (text-only new style / reference-image new style / duplicate-detected with reasoning).

### Invocation modes

- `--describe "<text>"` — text-only
- `--ref <image-path>` — image reference only
- `--describe "<text>" --ref <image-path>` — both (most accurate)
- `--save` — write file + update `_index.md` without asking
- `--print-only` — never save (preview mode)
- `--force-new` — skip duplicate-detection, always create
- `--add-to-auto-pick` — also append a row to `_auto-pick.md` when topic signals are clear
- `--model anthropic|openai|gemini` — LLM provider (default: anthropic)

### Validated

Live-tested with a text-only description ("Nordic minimalism — snow-white background, single pop of vermillion red, geometric sans-serif on Helsinki magazine layouts, generous negative space, restrained mood, premium B2B / Scandinavian brand"). The agent correctly identified this as NEW (no existing style covers the territory), preserved user vocabulary verbatim ("Helsinki magazine" / "Marimekko-era" / "vermillion red" / "expensive-quiet"), filled all 9 schema fields with 2 typography descriptors + 6 composition signatures + 12 elements + body_notes (when-NOT-to-use + variation hints) + auto_pick_signal mapping. The proposed entry was saved as:

- **`common/visual-prompt-library/styles/nordic-minimal.md`** — the 14th style in the library (first non-figma-ported entry)
- **`_index.md`** — new row added
- **`_auto-pick.md`** — new row added for "Premium B2B / Scandinavian brand / mindful tech" topic signals

### Notes

- 40 skills total (was 39).
- This is the WRITE side of the style library. The READ side (consume styles in downstream image-gen) is the existing shared chain in `common/visual-prompt-library/system-prompt.md` invoked by `carousel-builder` / `cover-maker` / `quote-card-maker` / `meme-card-maker` / `banner-maker` / `logo-maker`.
- The skill never auto-commits to git. After saving a new style, the user runs `git add common/visual-prompt-library/styles/<slug>.md _index.md _auto-pick.md` + commits explicitly. Avoids accidentally polluting the library with unreviewed entries.
- Cost per invocation is small (~$0.02 — one LLM call with optional multimodal image input). No image generation in this skill — that happens downstream when a visual skill picks up the new style.

## [2.15.1] — 2026-05-22

### Added — image-to-video on Veo 3.1 + Sora 2 (Kling 3 + Runway Gen-4 already had it)

Previously the video providers were a mixed bag: Kling 3 and Runway Gen-4 already accepted `image_url` (in fact REQUIRED it for their image-to-video-primary models), but Veo 3.1 was text-to-video only and Sora 2 didn't support image input at all. v2.15.1 ships cross-provider parity so any video provider in the collection takes an optional `image_url` / `input_image` kwarg as the first-frame seed.

**`common/runners/providers/google_video.py`** — `_VeoProvider.generate()` now reads `image_url` / `input_image` (cross-provider aliases), loads bytes via the shared `_read_image_bytes_and_mime` helper, and passes `types.Image(image_bytes=..., mime_type=...)` to `client.models.generate_videos(image=...)`. When absent, Veo stays in text-to-video mode (backwards compatible).

**`common/runners/providers/openai_video.py`** — `_SoraBase.generate()` now reads the same kwargs and includes `input_reference` in the POST body. Note: Sora 2 API is still gated (`OPENAI_SORA_API_ENABLED=1`); the field name follows the public-docs convention but may need a multipart/form-data upgrade depending on your account's API contract. The gate restricts who hits this code path.

**Kling 3 + Runway Gen-4** — already accepted `image_url` (they REQUIRE it for image-to-video-primary models). Unchanged.

### Added — carousel-builder optional animation step (docs)

`carousel-builder/SKILL.md` got a new `## Optional: animate the slides` section documenting the image-to-video chain:

1. After static carousel image gen, build a `skills.reel.plan.v1` with one shot per slide.
2. Each shot's `kwargs.image_url` points to the slide PNG; `kwargs.aspect_ratio: "9:16"`; `kwargs.duration_seconds: 4–8`.
3. Animation prompts respect the static layout — specify what MOVES (character action, atmospheric pulses, light ripples) and what STAYS STILL (headlines + plates + chrome in double quotes).
4. Run reel CLI with `--skip-stitch` for 3 independent slide-as-reels, OR omit to ffmpeg-concat into one continuous promo reel.

Cost guidance (Veo 3.1 fast, $0.15/s):
- 3 slides × 4s = $1.80
- 3 slides × 8s = $3.60
- 5 slides × 4s = $3.00

### Validated

Live-tested with the v2.15.0 AI Media Workshop deck (3 cyber-noir slides at /tmp/cover-test/generated/carousel/ai-media-workshop-v215/). Per-shot 4s animations via veo-3-1-fast preserved the static text + character identity while animating subtle motion (head turn → nod → terminal-tap on slide 1; arm extend + data-stream trail on slide 2; rise + welcome gesture + CLASSIFIED stamp pulses on slide 3). $1.80 total. ffmpeg concat into one 11.95s promo reel succeeded.

### Notes

- 39 skills unchanged.
- No new skills added — the chain is `carousel-builder` (static deck) → existing `reel-builder` CLI (animation + optional stitch) → ffmpeg. Composable, not monolithic.
- Sora 2 image-to-video support is best-effort given the gated API; first user to enable the gate will discover whether the multipart upgrade is needed.

## [2.15.0] — 2026-05-22

### Refactored — style library split into extensible per-file directory

v2.14.x bundled all 13 styles into one monolithic `common/visual-prompt-library/style-library.md` + a hardcoded quick-reference table inside the SYSTEM_PROMPT. v2.15.0 splits it into an extensible directory — drop a new `<slug>.md` file and every visual skill picks it up automatically, no code changes anywhere.

### New layout

```
common/visual-prompt-library/
  system-prompt.md       (library-agnostic — references the directory, no hardcoded style names)
  style-library.md       (now a redirect pointer to styles/)
  styles/
    _schema.md           (required frontmatter fields when adding a new style)
    _index.md            (catalog — one row per available style with `when_to_use` summary)
    _auto-pick.md        (topic-signal → style-slug resolution matrix)
    biotech.md
    cyber-noir.md
    brutalist.md
    vaporwave.md
    military.md
    scientific.md
    streetwear.md
    art-deco.md
    blueprint.md
    grunge.md
    glamour.md
    nature.md
    adventure.md
```

Each style file has YAML frontmatter with all 9 structured fields (id / slug / name / when_to_use / background / accents / elements / mood / accent_text_color / typography / composition_signature) plus optional body for extended notes / when-NOT-to-use / variation hints.

### Changed — SYSTEM_PROMPT is library-agnostic

The shared SYSTEM_PROMPT no longer enumerates the 13 styles. Instead it instructs the LLM to consult the `Style entry:` block in the user message — which the orchestrating skill resolves and inlines from the chosen `styles/<slug>.md` frontmatter. Adding a new style means adding a file in `styles/`, NOT editing the SYSTEM_PROMPT.

### Updated — buildUserMessage(opts) shape

The `Visual style:` field now carries a slug + structured `Style entry:` block (Background / Accents / Elements / Mood / Accent text color / Typography / Composition signature). For `--style custom`, replace with `Style entry (custom): "<verbatim desc>"`. For library + modifier, add `Style modifier: "<override>"`.

### Updated — per-skill cross-references

All 6 visual skills (`carousel-builder` / `cover-maker` / `quote-card-maker` / `meme-card-maker` / `banner-maker` / `logo-maker`) + their local style-presets refs now point at `common/visual-prompt-library/styles/_index.md` instead of the old `style-library.md`.

### How to add a new style

1. Write `styles/<your-slug>.md` with the frontmatter schema in `styles/_schema.md`.
2. Add a one-line row to `styles/_index.md`.
3. Optional: add a topic-signal row to `styles/_auto-pick.md` if the style should auto-resolve.
4. No code changes. Every visual skill picks it up immediately.

### Notes

- 39 skills unchanged.
- Old monolithic `style-library.md` kept as a 30-line pointer document for migration / discoverability — links to the new structure.
- Behavioral output is identical to v2.14.2 — the same 13 styles with the same fields, just stored extensibly.

## [2.14.2] — 2026-05-22

### Enriched — shared style library with Typography + Composition signatures

After v2.14.1 added rich typographic templating to the shared SYSTEM_PROMPT, the LLM still had to invent typography and composition patterns from scratch for each style — the 13-style library entries only listed background / accents / elements / mood / accent text color, with no typography genre or composition signature. This left the LLM picking generic typography (often defaulting to "bold sans-serif" everywhere) regardless of which style was active.

### Added to each of 13 styles in `common/visual-prompt-library/style-library.md`

- **Typography** — genre-level font descriptors specific to the style (image models don't have font libraries; they approximate by genre). Examples:
  - CYBER-NOIR → heavy stencil display + monospace terminal + condensed grotesque sans
  - ART DECO → stepped geometric deco display + thin engraved sans + copperplate script
  - GRUNGE → condensed newspaper serif + typewriter mono + ransom-note collage
  - GLAMOUR → modern high-contrast serif (Didot/Bodoni) + refined humanist sans + copperplate script
- **Composition signature** — layout patterns the style is famous for, so the LLM can pick a DIFFERENT signature per slide while staying on-style. Examples:
  - BRUTALIST → aggressive asymmetric grids, full-bleed headline, oversized numerals, thick black/yellow rules
  - VAPORWAVE → centered subject over horizon grid + sunset, chrome bevel reflections, kana floating in corners
  - SCIENTIFIC → journal-page asymmetry, sidebar pull-quote, figure + caption pyramids, marginalia
  - MILITARY → dossier-folder framing, target reticles centered, topographic map underlays, ammo-box frames

### Expanded element vocabulary

Each style entry's element list is now 2× richer (e.g. CYBER-NOIR: + blinking cursors / target reticles / CRT vignettes / ASCII frames; ART DECO: + deco arch silhouettes / lily pads / peacock feathers / crystal facets / octagonal medallions). Gives the LLM more variety to pick from per slide, avoiding the "same motif on every slide" failure mode.

### Updated SYSTEM_PROMPT to consult the new fields

`common/visual-prompt-library/system-prompt.md` STYLE FIELDS section now explicitly instructs the LLM to pull Typography + Composition signature + Elements from the chosen style's library entry, and to vary the composition signature + elements across slides when N>1. Added a 13-row quick-reference table so the LLM has the highlights in-prompt without needing to re-load the full library.

### Cross-referenced per-skill local presets

Added explicit cross-reference notes at the top of:
- `quote-card-maker/references/style-presets.md`
- `banner-maker/references/style-presets.md`
- `logo-maker/references/style-presets.md`
- `cover-maker/references/imprints.md`

Each notes that the local skill-specific presets complement the shared 13-style library — users can pick by name from the shared library for broad stylistic coverage, or use the local presets for medium-specific shortcuts.

### Notes

- 39 skills unchanged.
- The richer library entries cost zero runtime — they're text the LLM reads once per request. Same provider calls, same prices.
- Validated by re-running the AI Media Workshop carousel + spot-checking a cover-maker book cover generation.

## [2.14.1] — 2026-05-22

### Fixed — rich typography + composition variety in shared SYSTEM_PROMPT

v2.14.0 shipped the unified visual-prompt chain but the SYSTEM_PROMPT's per-prompt instructions over-simplified to "headline + caption + chrome", producing monotone slides — same plate-at-top + same fonts + same character position repeated across the deck. The user pointed out the figma SEEDREAM_SYSTEM_PROMPT has a far richer typographic template + composition guidance that v2.14.0 lost in translation.

### Added to `common/visual-prompt-library/system-prompt.md`

- **RICH TYPOGRAPHIC TEMPLATE** — explicit table of 15+ typographic roles the LLM can choose from per slide: main headline, second headline line, subhead / kicker, highlighted plate / call-out, body paragraph, accent phrase (in style-accent color), numbered list with large display numerals, bullet list, two-column comparison, table / checklist, big stat badge, italic pull quote, code / monospace block, footer / caption, date / number stamp, brand / logo zone. Each role with its own natural-language descriptor pattern.
- **COMPOSITION VARIETY** — explicit rule that N>1 decks MUST use DIFFERENT compositions per slide. Forbidden: every slide = plate-at-top + character + chrome repeated. Required: vary dominant-element position (top-left / center / right-third / asymmetric split), layout type (full-bleed / two-column / list / badge-centered / pull-quote / table), character position (left edge / right edge / behind type / interacting with one element).
- **TYPOGRAPHIC VARIETY WITHIN A SLIDE** — at least 2 typeface treatments per slide; biggest element 5–10× the smallest; apply style's accent color to ==marked== accent phrases and key numbers.
- **STYLE ACCENT COLORS** — explicit instruction to pull accent text colors from the chosen style's `Accent text color` line in `style-library.md` (BIOTECH → cyan/mint; CYBER-NOIR → matrix green/signal red; BRUTALIST → industrial yellow/rust red; ART DECO → gold/champagne; GLAMOUR → gold/champagne/rose gold; etc.).

### Validation

Live-tested with the AI Media Workshop 3-slide carousel + 4 `==accent==` markers + character ref. Result: three radically different compositions:
- Slide 1 (hook) — asymmetric layout with stencil-display headline + monospace kicker + angled signal-red plate + Mac-window terminal caption + character right-edge.
- Slide 2 (framework) — vertical navy left panel + 4 giant matrix-green numerals + 4 code-block terminal windows + character profile-left gesturing.
- Slide 3 (cta) — centered medallion with concentric dashed rings + giant signal-red countdown numeral + arched stencil headline + signal-red CTA plate + matrix-green overlapping pill + classified-stamp + character lower-right.

Each slide has 5+ distinct typographic treatments. Style accent colors applied throughout. Character identity preserved across all 3 via nano-banana-pro ref.

### Notes

- 39 skills unchanged.
- SYSTEM_PROMPT is the only file modified. The shared chain architecture from v2.14.0 stays. The other skills (cover-maker / quote-card / meme-card / banner / logo) automatically inherit the typography + composition improvements since they all load the same shared SYSTEM_PROMPT.

## [2.14.0] — 2026-05-21

### Added — shared visual-prompt-library + unified chain across all visual skills

After multiple iterations on carousel-builder (Python templates v2.12, image-prompt subagent chain v2.13, text-first → SEEDREAM v2.13.1, then user pointed to the canonical figma `promptCarousel/` flow), the user requested ONE unified prompt-chain approach across every visual-output skill (carousels + covers + flyers + quote / meme / banner / logo cards). v2.14.0 ships exactly that.

### New shared library

- **`common/visual-prompt-library/system-prompt.md`** — the canonical SYSTEM_PROMPT used by every visual skill. Mirrors `figma/app/lib/carousel/promptCarousel/prompts.js` with improvements ported from `slidePrompts/systemPrompt.js` (SEEDREAM):
  - **Single LLM call** returning JSON `{slides:[{number, prompt}]}` — no per-slide subagents (breaks visual consistency).
  - **Per-prompt discipline**: 1–3 sentences, text-in-quotes for what should render, natural-language layout ("at top" / "centered" / "right edge"), no meta-labels (no literal `HEADLINE:` / `BODY:` / `SUBHEADLINE:` — they render as visible text on the image).
  - **Infographic vocabulary** for middle carousel slides (numbered list / comparison / badge / quote / steps / framework / myth-vs-truth) — keeps middle slides informative, not atmospheric.
  - **Deck structure** for N>1 (hook → info-dense middle → CTA verbatim).
  - **Single-image structure** for N=1 (title-dominant + secondary attribution zone + optional subtitle).
  - **Carousel chrome** (page indicator + swipe / end marker) appended automatically when N>1, skipped when N=1.
  - **Character reference language** — when user supplies a character photo, the LLM is instructed NOT to re-describe face / hair / build / accessories (image-side ref locks identity); only pose / action / position.
  - **Brand & style reference** — supplied colors become the dominant palette; supplied style images get matched.
  - **Accent markup** — `==word==` in input text → accent-color callouts on the relevant image.
  - **Finished-post preservation** — direct quotes + cuts only, never paraphrase.
  - **Forbidden literals** banned from prompt body (layout labels, hex codes, platform names, dimensions, emojis).
  - **Retry policy** — up to 2 LLM retries with stricter reminder on malformed JSON / missing slides / forbidden literals.

- **`common/visual-prompt-library/style-library.md`** — the 13-style library ported from figma's SEEDREAM_SYSTEM_PROMPT (BIOTECH / CYBER-NOIR / BRUTALIST / VAPORWAVE / MILITARY / SCIENTIFIC / STREETWEAR / ART-DECO / BLUEPRINT / GRUNGE / GLAMOUR / NATURE / ADVENTURE). Each entry: when-to-use + background + accents + elements + mood + accent text color. Auto-pick matrix at the bottom maps topic / tone signals → dominant style. Custom-style override supported.

### Changed — every visual-output skill switched to the unified chain

- **`carousel-builder`** — PIPELINE step 4 now reads "Compose ONE LLM call, load shared SYSTEM_PROMPT + buildUserMessage(Mode=carousel)". REFERENCES table points at the shared library. Constraints rewritten: ONE LLM call (not per-slide), 1–3 sentence prompts (not 250-word spec-dumps), style = vocabulary + treatment (not a recurring scene). `references/slide-roles.md` demoted from primary to optional content-brief aid.

- **`cover-maker`** — PIPELINE step 5 switched to shared chain with `Mode=cover`. The two-pass Pillow typography composer (v2.11.0) is kept as an opt-in `--typeset overlay` fallback for users who need pixel-perfect typography (publisher imprint precision, multilingual). Default for all mediums is now `--typeset ai` (LLM-prompt → image model renders title + creator in the image).

- **`quote-card-maker`** — PIPELINE step 5 switched to shared chain with `Mode=quote-card`, N = aspect count.

- **`meme-card-maker`** — PIPELINE step 5 switched to shared chain with `Mode=meme-card`, N = variants. Template-specific composition + Impact-style typography cues passed via user message.

- **`banner-maker`** — PIPELINE step 5 switched to shared chain with `Mode=banner`, N = presets count. Per-preset composition zones (leaderboard/medium-rectangle/skyscraper layout asymmetry) passed via user message.

- **`logo-maker`** — PIPELINE step 5 switched to shared chain with `Mode=logo`, N = variants. Brand + tagline + style preset + palette passed via user message.

### Migration notes

- Existing `plan.json` files with `prompt` items continue to work — the CLIs are unchanged (v2.13.0 simplification still applies).
- The legacy `common/style-library/carousel/` (24 hand-rolled styles) is still on disk for back-compat. New decks should use the 13-style library at `common/visual-prompt-library/style-library.md` instead. The two co-exist; eventually the old library can be deleted in a future cleanup pass.
- `carousel-builder/references/slide-roles.md` and `references/slide-split.md` are now optional content-brief aids; the SYSTEM_PROMPT's infographic-vocabulary section supersedes them.
- The Pillow two-pass typography composer in `common/runners/typography.py` (v2.11.0) is retained for `cover-maker --typeset overlay` — kept as opt-in fallback, not the default.

### Notes

- 39 skills total (unchanged).
- Validated by regenerating the AI Media Workshop 3-slide promo carousel — clean, designerly, character identity preserved across slides via nano-banana-pro image ref.
- The earlier v8 `common/runners/carousel_composer.py` (Konva-style Pillow text overlay for carousels) was deleted before v2.14.0 was finalized — that approach mirrored `canvas-new` not `promptCarousel`, and the user rejected it as the wrong figma feature to mirror.

## [2.13.0] — 2026-05-21

### Removed — Python carousel prompt builder

`common/runners/carousel_prompt_builder.py` (~564 lines, 9 role-specific dataclasses + 9 layout functions + scene policy + anti-AI-tells) is **deleted**. Live testing kept producing magazine-with-text-overlay output regardless of how much the templates were refined. The root cause was structural, not stylistic: prompt writing is a designer task, not a string-template task. The figma reference (`figma/app/lib/carousel/...`) uses the LLM itself (Claude with SEEDREAM_SYSTEM_PROMPT) to compose ~100-word natural-language prompts per slide. Python templates produced prompts that read like spec-sheets ("HEADLINE: ... / SUBTITLE: ... / FRAMEWORK: ...") which the image model rendered literally as labels-on-image.

### Replaced with — `image-prompt` skill chained per slide

The carousel-builder now invokes the existing `image-prompt` skill once per slide:

1. Skill side assembles a STRUCTURED BRIEF per slide: style anchor (verbatim) + role + content (real titles / boxes / data points / quote+attribution) + composition guidance from `references/slide-roles.md` + universal rules from `_universal-rules.md` + slide marker + swipe arrow / end marker + aspect + character-ref hint if constant across deck.
2. `image-prompt` returns a single dense natural-language designer prompt (~80-150 words, no meta-labels).
3. The returned prompt becomes `plan.items[i].prompt` directly.
4. Carousel CLI is a thin batch runner — fully written prompts in, batched generation out.

### Plan-schema simplification (`skills.carousel.plan.v1`)

The structured `role` + `content` item shape (added in v2.12.1) is removed. Plan items now have ONE shape:

```
{"index": N, "label": "slide-NN-role", "prompt": "<full natural-language prompt>", "kwargs": {...}}
```

If an item lacks `prompt`, the CLI errors with: "write prompts via image-prompt skill, then assemble plan items as `{index, label, prompt, kwargs}`. Structured role+content items were removed in v2.13.0."

### Docs rewritten

- **`carousel-builder/SKILL.md`** — step 5 rewrites the pipeline as "brief image-prompt per slide, place returned text into plan items". REFERENCES table now lists `image-prompt` as a chained skill.
- **`carousel-builder/references/slide-roles.md`** — keeps the 9-role taxonomy + per-role content brief contracts + composition guidance, but reframes the role file as a SPEC FOR BRIEFING image-prompt rather than a SPEC FOR A PYTHON BUILDER. Added "How to brief image-prompt per slide" section at the top.
- **`common/style-library/carousel/_universal-rules.md`** — reframed §10 (loading order) as "brief assembly order" and dropped Python-builder language from §0, §11, and the intro. Rules still apply; they're now LLM-author guidelines, not template engine injection points.

### Migration

Existing plans with `role` + `content` items are NOT auto-converted. Re-generate via the new chain: brief image-prompt per slide → drop returned text into `items[i].prompt`. For one-off legacy needs, the v2.12.3 builder can be re-extracted from git history.

### Notes

- 39 skills (unchanged).
- Validated against the hand-written-prompts AI Media Workshop test (3-slide deck) — that test bypassed the Python builder entirely and produced clean designer output. v2.13.0 normalizes that bypass as THE path.
- Skill counts in scenarios / examples / quickstart unchanged.

## [2.12.3] — 2026-05-21

### Fixed — figma-rigor composition for hook + framework + cta layouts; optional character override

Live testing of character-driven promo carousels (course invitation deck) showed two composition failures:

1. **Generic typography hierarchy** — hook layout produced "title + subtitle on one plate" with no scale contrast, no separate subtitle pill, no decorative element. Output read as "text in a rectangle", not as designed promo poster.
2. **Framework excluded character** — the per-role scene policy from v2.12.2 (correctly) said "no literal scene" on framework slides for info-density carousels, but this blocked character-driven decks where the character is the constant unifier across all slides.

### Upgraded layout templates (carousel_prompt_builder.py)

**`_hook_layout`** — rewrote with figma-style explicit hierarchy: PRIMARY HEADLINE (upper area, bold, 12-18% of frame height, 2-3 lines with balanced wrap, sentence case, on style-appropriate plate) → SUBTITLE / TAGLINE on a SEPARATE smaller secondary element (pill / chip / italic ribbon, visually distinct from headline plate, 3-5% of frame height, accent color) → MAIN SUBJECT fills lower 50-65% of canvas and visually interacts with the type (looks at / gestures toward / framed by). Explicit design discipline: 3-5× scale contrast headline-to-subtitle, generous negative space, "type and subject feel COMPOSED together not stacked".

**`_framework_layout`** — rewrote with per-card internal hierarchy: SECTION LABEL at top (small all-caps eyebrow + thin accent underline) → LAYOUT spec with explicit fill region (cards fill middle 65-75% of frame, equal-sized cells, consistent gutters, drop shadow, rounded corners, low-opacity tinted fill, 1px stroke border in accent color) → EACH CARD has bold accent-colored eyebrow/number/label + neutral body text beneath with explicit sizing (3-4% / 2-3% of frame height respectively). Explicit design discipline: visual weight equality, eyebrow in style accent / body in neutral.

### Optional `visual_hint` on FrameworkContent + CtaContent

Both dataclasses gained an optional `visual_hint: str | None` field. When set, the layout template injects "MAIN SUBJECT (overrides background policy)" describing how the subject co-exists with the cards / CTA plate. Used for character-driven decks where one character is the constant unifier across all slides. Scene-policy "no literal scene" is correctly overridden via content (not via global config), so info-density carousels still get clean framework slides by default.

### Notes

- 39 skills total (unchanged).
- Validated with the AI Media Workshop 3-slide course-invitation deck (hook → framework with character → cta with character). All 3 slides feature the same 3D-cartoon character identity (via nano-banana-pro photo-ref) and consistent typographic design language. Framework slide reads as a real designed infographic (4 cards with eyebrow + body each), not as 4 floating word-chips.
- Other 6 layout templates (point / data / steps / comparison / quote / myth-vs-truth) NOT yet upgraded to this figma-rigor depth — incremental v2.13 task. They work but produce less designed output.

## [2.12.2] — 2026-05-21

### Fixed — style anchor "same scene on every slide" anti-pattern

Live testing revealed that a scene-y style anchor (e.g., "Library reading room at dusk with leather books, brass lamp, ink wells") caused EVERY slide to render the same library setting — framework became "4 cards in a library", quote became "single page in a library", killing the carousel as an information sequence. The fix had to happen at two layers:

- **`common/runners/carousel_prompt_builder.py`** — added per-role `_SCENE_POLICY` directive injected between the style anchor and the role layout block. Hook slides keep literal scenes (the establishing shot is valid). `framework` / `data` / `steps` / `comparison` / `myth-vs-truth` / `point` get "clean style-appropriate textured field, no literal recurring scene — content dominates". `quote` and `cta` get "clean field with AT MOST ONE small decorative element". This works as a safety net even when the user passes a scene-y anchor — the policy strips scene leakage per role.
- **`common/style-library/carousel/_universal-rules.md`** — added §0 (style anchor = vocabulary, not scene) at the top and §11 (per-role scene policy table) at the bottom, documenting both the principle and the builder's enforcement.
- **`common/style-library/carousel/dark-academia.md`** — rewrote both anchors (carousel + text-in-image) as vocabulary + treatment + element-list, dropping the "private library reading room at dusk" scene baking. Now reads as the model example of vocabulary-style anchor.
- **`carousel-builder/SKILL.md`** — explicit anti-pattern constraint added to CONSTRAINTS list referencing §0 and §11.

### Notes

- 39 skills total (unchanged). Pure architectural fix.
- The remaining 23 carousel style files have NOT been swept for scene-y anchors yet — but the per-role scene policy in the builder is the safety net so they'll still produce informative decks even with imperfect anchors. Incremental cleanup is a future v2.13 task.
- Verified end-to-end with the book promo 5-slide deck: hook gets the literal scene (book + lamp), framework renders as 4 distinct parchment cards on textured field (no library), myth-vs-truth as two plates with accent divider (no library), quote as single big aged-parchment plate (no library), cta as plate + minimal corner decoration (no library). Style consistency held via palette + typography + plate vocabulary.

## [2.12.1] — 2026-05-21

### Added — structured plans + stdin support across all 9 plan-driven CLIs

Live testing of v2.12.0 surfaced two UX problems:

1. Per-test Python "build script" overhead — to use `carousel_prompt_builder`, the skill side had to write a Python script that imported the builder and dumped a plan.json. Bloat: intermediate disposable file per test.
2. Disposable plan.json files — every iteration created `plan-v2.json` / `plan-v3.json` / `lattice-plan.json` etc., a graveyard of one-off artifacts.

Both fixed by extending the carousel CLI's plan format AND adding stdin support across all plan-driven CLIs.

### Structured-content items (carousel-builder)

`skills.carousel.plan.v1` plan items now accept TWO shapes:

- Legacy: `{"index": N, "label": "...", "prompt": "<full prompt>", "kwargs": {...}}` (back-compat)
- New: `{"index": N, "label": "...", "role": "framework", "content": {framework_name: ..., boxes: [...]}, "kwargs": {...}}`

When a plan item has `role` + `content`, the CLI internally invokes `carousel_prompt_builder.build_slide_prompt()` at execution time. The plan also accepts top-level `lang` and `slide_marker_style` fields applied uniformly across slides. No Python script needed in user-land — structured content goes straight in the JSON.

Routing implemented for all 9 supported roles: `hook` / `point` / `framework` / `data` / `steps` / `comparison` / `quote` / `myth-vs-truth` / `cta`. Each role wires through to its matching dataclass via `_CONTENT_FACTORIES` in `cli/carousel.py`.

### `--plan-file -` reads from stdin across all 9 plan-driven CLIs

`carousel`, `cover`, `flyer`, `avatar`, `thumbnail`, `banner`, `meme`, `logo`, `quote`, `reel` now all support `--plan-file -` to read the plan from stdin. Pattern:

```bash
cat <<EOF | carousel-builder --plan-file - --yes
{...}
EOF
```

No intermediate file needed for one-off tests / iterations. Production workflows can still use file-based plans.

### Notes

- 39 skills total (unchanged). Pure UX patch.
- Combined with v2.12.0's structured-content support in carousel-builder, the full skill workflow is now: Claude assembles structured plan in conversation → heredoc → stdin → CLI builder → batch generates. Zero disposable artifacts.
- Other plan-driven skills (cover-maker, flyer-maker, avatar-maker, etc.) get stdin support but DON'T yet have structured-content mode — they still need full per-item prompts. Adding structured shape to them is a future enhancement.

## [2.12.0] — 2026-05-21

### Added — figma-rigor prompt builder for carousel-builder

Live-testing revealed that carousels produced "atmospheric image with floating text overlay", not actual informative carousels. Root cause: per-slide prompts were assembled ad-hoc by the skill side without infographic discipline, no static carousel UI elements (page indicators / swipe arrows / end markers), and no role-driven information density. Middle slides were just hooks-with-pretty-backgrounds — the user-facing complaint was "информативности слабовато".

Imported the rigor from the upstream figma/carousel-new pipeline (`SEEDREAM_SYSTEM_PROMPT` pattern) and codified it as a reusable builder.

- **`common/runners/carousel_prompt_builder.py`** — Python prompt builder that assembles figma-rigor image prompts. `build_slide_prompt(style_anchor, role, slide_number, total_slides, content, lang, is_last, slide_marker_style)` returns a single dense paragraph (~800-1500 chars) combining:
  1. Style anchor (from the chosen style's text-in-image mode block)
  2. Role-specific composition template (one of 9 roles)
  3. Filled content slots (all text in double-quotes for image-model literal rendering)
  4. Static carousel UI (page indicator, swipe arrow or end marker, slide marker)
  5. Anti-AI-tells closing modifiers (sharp text, no melted glyphs, no extra elements)
- **Per-role dataclasses**: `HookContent`, `PointContent`, `FrameworkContent` (with `Box`), `DataContent` (with `DataPoint`), `StepsContent` (with `Step`), `ComparisonContent` (with `ComparisonSide`), `QuoteContent` (with `QuoteAttribution`), `MythTruthContent`, `CtaContent`. Each enforces info-density expectations per role.
- **`carousel-builder/references/slide-roles.md`** — 9-role taxonomy with composition templates, content-slot contracts, info-density targets, default deck shapes per slidesCount (3/5/6/7/8/10), per-domain bias recommendations, anti-patterns. Replaces the implicit hook/point/cta tripartite default.
- **`common/style-library/carousel/_universal-rules.md`** — universal carousel conventions injected into every prompt by the builder: page indicators (RU `"N из total"` / EN `"N of total"`), swipe arrows (`листай →` / `swipe →`), end markers (`конец` / `end`), slide markers (arabic / roman / bracketed), infographic grammar patterns (numbered lists, comparison tables, data badges, quote blocks, steps sequences, myth-vs-truth contrasts, framework grids), forbidden patterns (HEADLINE/BODY literals, hex codes, aspect ratio mentions), anti-AI-tells closing modifiers. Applies uniformly across all 24 carousel styles — no per-style duplication.
- **`carousel-builder/SKILL.md`** — updated pipeline to STRONGLY PREFER the builder over manual prompt assembly. Explicit info-density discipline guidance: middle slides MUST use `framework` / `data` / `steps` / `comparison` / `quote` / `myth-vs-truth` roles, not just `point`.

### Notes

- 39 skills total (unchanged). Additive infrastructure for `carousel-builder`.
- Existing 24 carousel style files are unchanged. The builder reads their existing "Style anchor (text-in-image mode)" block and combines with universal rules + role template. Eventual per-style `infographic_grammar` blocks may be added later for style-specific deviations from the universal patterns.
- The builder is also useful for `reel-builder`'s shot prompts (one frame = one slide for the role taxonomy) — future v2.13.0 wiring.
- Pattern referenced from the figma project (`/Users/mikefluff/Documents/figma/app/lib/carousel/slidePrompts/systemPrompt.js`, `app/lib/carousel/contentGenerator/orchestrator.js`).
- Validated end-to-end with a 5-slide book promo deck (hook + framework + myth-vs-truth + quote + cta) — Framework slide rendered as actual 2×2 box infographic with 4 distinct components, Myth-vs-Truth as proper vertical split with accent divider, Quote with attribution. This is the information density that was missing in the prior implementation.

## [2.11.0] — 2026-05-21

### Added — two-pass typography for book covers

This release fixes the fundamental "AI image with floating title" failure mode that every other AI cover generator suffers from. We now separate **background art** (what AI is good at) from **typography** (what AI is bad at), and do typesetting externally with real bundled OFL fonts.

- **`common/runners/typography.py`** — Pillow-based typography composer. `compose_book_cover(image_bytes, layout)` overlays title / author / subtitle / decorations on an AI-generated background using bundled OFL fonts. Supports variable fonts (auto-picks weight axis), per-block sizing as fraction of cover height, tracking in ems, multi-line wrap with max-line cap, optional title legibility bands, optional thin-rule / dot decorations, per-block anchor positioning.
- **`common/runners/cover_imprints.py`** — five publisher design-system presets encoding real-world layouts:
  - `nyrb-classics` — painterly background + crimson title plate + Inter Bold caps (NYRB Classics aesthetic)
  - `penguin-marber-grid` — 1963 Marber tri-band (title 27% / illustration 50% / author 23%, cream + ink + accent)
  - `mit-essential-knowledge` — top 55% typography (large) + bottom 45% abstract diagram
  - `picador-modern` — Playfair Display title + EB Garamond italic author + flat-color visual accent
  - `faber-modernist` — solid color field + Cinzel display caps (typography-as-image, no illustration)
- **`cover-maker/fonts/`** — bundled OFL 1.1-licensed typefaces (EB Garamond, Cormorant, Playfair Display, Inter, Bebas Neue, Cinzel; ~2.8 MB total). Cross-platform consistent output. Variable-font support; weight is set per-block.
- **`cover-maker/references/imprints.md`** — full design-system documentation per imprint.
- **`cover-maker` CLI extensions** (additive — no breaking changes):
  - `--imprint <slug>` — pick one of 5 presets
  - `--genre <slug>` — auto-map to default imprint (literary-fiction→nyrb, thriller→marber, academic→mit, memoir→picador, poetry→faber)
  - `--typeset overlay|ai` — `overlay` runs the two-pass composer (default for `--medium book` when `--imprint` or `--genre` set); `ai` legacy mode lets the image model render text itself
- **Plan-file schema additions** (`skills.cover.plan.v1`): `imprint`, `genre`, `typeset` fields. Backwards compatible — older plans without these fields still work in legacy `ai`-typeset mode.

### Fixed (bundled patches from session)

- **`openai_image.py` removed deprecated `response_format` param** — OpenAI dropped it from `/v1/images/generations`; v2.10.0/v2.10.1 calls would 400 with `Unknown parameter: 'response_format'`. Now omitted; gpt-image-2 always returns b64_json which we decode regardless.
- **`openai_image.py` timeout bumped 120 → 300 seconds** — `quality=high` requests can take 90-180s, the old timeout fired during normal generation.

### Changed

- **`common/runners/requirements.txt`** — added `Pillow>=10.4,<12` for the typography composer.
- **`cover-maker/SKILL.md`** — documents new modes (`--imprint`, `--genre`, `--typeset`) under a Visual subsection.
- **`VERSION` + `skills.json:version`** → `2.11.0`.

### Notes

- 39 skills total (unchanged). This release is purely additive infrastructure for `cover-maker`.
- The two-pass pattern is the de-facto standard among pro AI-cover designers (BeYourCover, Inkfluence, Reedsy) as of 2026. Background-only + Pillow overlay produces dramatically better results than letting AI render typography directly.
- Imprint presets ship with both a `TypeLayout` (for the composer) AND a `prompt_fragment` (for the image-gen prompt) — the prompt asks for "calmer upper third for plate overlay" etc., so the AI generates art that harmonizes with the planned typography zone.
- The 5 starter imprints cover the 80% case. Custom imprints can be added by editing `cover_imprints.py`; a JSON `--layout-file` flag is planned for v2.12.0.
- Variable-font weight selection requires Pillow 10.4+ — older versions silently ignore weight axis.

## [2.10.1] — 2026-05-21

### Fixed

- **`style-transfer` default model didn't work in v2.10.0.** The CLI passed `image_url` as the kwarg, but BFL's flux-kontext provider expects `input_image` — every call failed with "flux-kontext requires input_image". Now fixed at two layers:
  - `bfl.py`: accepts either `input_image` (native) or `image_url` (cross-provider alias).
  - `cli/stylize.py`: routes the right kwarg per provider explicitly.

### Added (multi-provider support for `style-transfer`)

- **`nano-banana-pro` image-to-image** is now wired. The `google_image.py` `NanoBananaProProvider` accepts `image_url` or `input_image` (path / URL / bytes), reads + base64-encodes the reference, and sends it as a multimodal `types.Part` alongside the prompt via the Gemini SDK. This unlocks identity-priority style transfer (best for portraits) and also benefits any plan-driven skill that passes `--photo` to nano-banana-pro (cover-maker / avatar-maker / thumbnail-maker / flyer-maker had been silently dropping the reference image for this provider).
- **`replicate-image`** is now routable from `style-transfer` via `--model replicate-image --replicate-model <user>/<model>` — passes `image` as the input field (most Replicate style-transfer models read this).

### Changed

- **`style-transfer` CLI errors out cleanly for `gpt-image-2`** with a message pointing to flux-kontext / nano-banana-pro alternatives. gpt-image-2 image-to-image edits would need OpenAI's `/v1/images/edits` endpoint (different from the current `/v1/images/generations` wrapper) — tracked as a future enhancement, not in this patch.
- **`style-transfer/references/providers.md`** — added explicit provider-status matrix.
- **`style-transfer/references/troubleshoot.md`** — added entries for the flux-kontext bug, gpt-image-2 limitation, and nano-banana-pro re-roll guidance.
- **`VERSION` + `skills.json:version`** → `2.10.1`.

### Notes

- This is a patch release — no new skills, no breaking changes, no schema changes.
- The bfl.py alias affects ALL skills that pass `image_url` to flux-kontext (not just style-transfer) — cover-maker, flyer-maker, avatar-maker etc. will now correctly send reference images to Flux Kontext when the user picks `--model flux-kontext`.

## [2.10.0] — 2026-05-21

### Added

- **`audio-mix-maker` wrapper skill** — mix a music / audio track onto an existing video via ffmpeg. Three modes: `replace` (drop original audio), `overlay` (mix both audible), `duck` (sidechain compressor lowers music when speech detected). Volume + fade-in + fade-out + duck-amount controls. No API calls — pure ffmpeg. Closes the "I have video + music separately, just need a final" workflow gap.

- **`style-transfer` wrapper skill** — apply an artistic style to an existing image. Default provider Flux Kontext (best for natural-language style transfer). 12 curated style presets: `watercolor`, `oil-painting`, `sketch`, `line-art`, `ink-wash`, `cyberpunk`, `studio-ghibli`, `pixar-3d`, `manga`, `art-deco`, `low-poly`, `vaporwave`, plus `custom` mode with `--prompt-mod`. Single image in, stylized output. ~$0.05 per image.

- **`transcribe-maker` wrapper skill** — speech-to-text via OpenAI Whisper. Audio / video → SRT, WebVTT, JSON, plain text, or verbose_json (word-level timestamps). Auto-detects language or accepts `--lang` hint (ISO-639-1). ~$0.006/min. Closes the loop with `subtitle-burner`: transcribe → burn captions. Whisper API limit 25 MB per call (see references/preprocessing.md for splitting).

- **`common/runners/ffmpeg.py:mix_audio_with_modes()`** — extended ffmpeg helper covering replace / overlay / duck modes. Duck mode uses `sidechaincompress` filter (the original audio drives compression of the music — speech detected → music dims).

- **`common/runners/providers/openai_transcribe.py`** — new Whisper provider. Multipart upload via `requests`, supports all Whisper response formats, enforces 25 MB API limit at the client side.

- **`common/runners/cli/{mix,stylize,transcribe}.py`** — three new CLI modules. `mix` is argparse-driven (pure ffmpeg). `stylize` wraps Flux Kontext / Nano Banana Pro with style preset → prompt mapping. `transcribe` wraps the Whisper provider with format selection.

### Changed

- **`skills.json`** — 39 entries (was 36). Three new skills registered.
- **`docs/USER-GUIDE.md`** — added "I want to mix music onto a video", "I want to style-transfer an image", "I want to transcribe audio / video to subtitles" sections.
- **`docs/COMPOSING.md`** — added 3 new orchestrator recipes: auto-caption a tutorial (transcribe + burn), voiceover-driven explainer with music bed, style-transfer brand identity variants.
- **`docs/ROADMAP.md`** — marks `audio-mix-maker`, `style-transfer`, `transcribe-maker` as SHIPPED. ACTIVE ROADMAP IS NOW EMPTY — only deferred-heavy items remain (`deck-maker`, `print-ready-export`).
- **`common/runners/cost.py`** — added `whisper-1` to price table ($0.006/min).
- **`common/runners/config.py`** — registers the new `openai_transcribe` provider on import.
- **`VERSION` + `skills.json:version`** → `2.10.0`.

### Notes

- 39 skills total (was 36). All three new skills are additive — no breaking changes.
- ACTIVE ROADMAP CLOSED. Single-image siblings of `flyer-maker` complete (cover / thumbnail / avatar / logo / quote-card / banner / meme). Image utilities complete (bg-remover / upscaler / style-transfer). Audio utilities complete (voiceover-maker / subtitle-burner / audio-mix-maker / transcribe-maker). Animation utility shipped (gif-maker).
- The 4 deferred items remain: `deck-maker` (3-5 day effort), `print-ready-export` (DTP territory), `event-discovery` (TOS issues), `whisper-transcription` (NOW SHIPPED as `transcribe-maker`).
- Skill counts by layer: 1 base + 21 wrappers + 3 linters + 11 orchestrators + 3 meta.

## [2.9.0] — 2026-05-21

### Added

- **`banner-maker` orchestrator skill** — banner-ad / display-creative generator with standard-size presets. Headline + CTA + brand composition for OG (1200×630), LinkedIn ad (1200×627), Facebook ad (1200×628), Twitter card (1500×500), Google Display (leaderboard 1456×180, medium-rectangle 600×500, mobile-banner 640×200, wide-skyscraper 320×1200). All output at @2x retina for high-DPI displays. Default model `ideogram-3-quality` for clean embedded text. Style presets biased toward ad-friendly anchors (`swiss-grid-poster` / `gradient-mesh-modern` / `brutalist-grid` / `editorial-magazine` / `neon-cyberpunk`). Plan schema `skills.banner.plan.v1`.

- **`meme-card-maker` orchestrator skill** — Impact-style meme generator. Top text + bottom text + optional centerpiece. 5 supported templates as composition hints: `drake` (2-panel rejection/approval), `distracted-boyfriend` (3-character), `expanding-brain` (4-panel ascending), `two-buttons` (decision), `change-my-mind` (sign), plus `custom` (default — model interprets freely). Optional `--base-photo` for user-image centerpiece. Default model `gpt-image-2` (best illustration + integrated text). Captions auto-uppercase for English; mixed-case for Cyrillic (`--lang ru`). Plan schema `skills.meme.plan.v1`.

- **`upscaler` wrapper skill** — image super-resolution utility. Single image in → 2× / 4× / 8× output via Replicate-hosted models. Default `nightmareai/real-esrgan` (general-purpose). Alternatives: `tencentarc/gfpgan` (face-focused), `jingyunliang/swinir` (texture-preserving), `philz1337x/clarity-upscaler` (max fidelity). Optional `--face-enhance` flag enables face restoration in Real-ESRGAN. ~$0.005-0.02 per image.

- **`common/runners/cli/{banner,meme,upscale}.py`** — three new CLI modules. Banner & meme are plan-driven (cover.py / flyer.py shape); upscale is argparse-driven single-image (bg.py shape).

### Changed

- **`skills.json`** — 36 entries (was 33). Three new skills registered.
- **`docs/USER-GUIDE.md`** — added "I want a banner ad", "I want a meme", "I want to upscale / enhance an image" sections.
- **`docs/COMPOSING.md`** — added 4 new orchestrator recipes: full launch campaign visuals (banner + cover + thumbnail), brand identity + ad creatives (logo + banner ads), meme + carousel content, restore + repurpose old assets (upscale + cover).
- **`docs/ROADMAP.md`** — marks `banner-maker`, `meme-card-maker`, `upscaler` as SHIPPED.
- **`VERSION` + `skills.json:version`** → `2.9.0`.

### Notes

- 36 skills total (was 33). All three new skills are additive — no breaking changes. Existing orchestrators / wrappers unchanged.
- `banner-maker` & `meme-card-maker` reuse the carousel style library + batch executor infrastructure.
- `upscaler` reuses the Replicate provider router from `bg-remover` (no new vendor abstractions).
- Single-image siblings of `flyer-maker` family now complete: cover-maker / thumbnail-maker / avatar-maker / logo-maker / quote-card-maker / banner-maker / meme-card-maker. `deck-maker` remains deferred (heavier — multi-slide).
- Image-utility family now has 3 wrappers: `bg-remover` (segmentation), `upscaler` (super-resolution), with `style-transfer` next on ROADMAP.

## [2.8.0] — 2026-05-21

### Added

- **`logo-maker` orchestrator skill** — brand mark / wordmark / logo generator. Defaults to `ideogram-3-quality` for cleanest embedded text. Six style presets: `wordmark` (default) / `minimal` / `illustrated` / `typographic` / `geometric` / `emblem`. Single-image output with N stochastic variants per call (default `--variants 4`). Optional palette hint via natural language or hex codes. Outputs `./generated/logo/<slug>/logo-v<N>.png` + `manifest.json` + `prompts.md`. Plan schema `skills.logo.plan.v1`.

- **`quote-card-maker` orchestrator skill** — typography-dominant quote / aphorism graphics where the text IS the image. Six style presets biased toward text-friendly carousel anchors: `minimal-serif` (literary), `swiss-grid-poster` (marketing), `monochrome-bold` (manifesto), `editorial-magazine` (long-form), `gradient-mesh-modern` (SaaS), `russian-constructivist` (RU heritage). Multi-aspect (square / portrait / story / landscape). Constraint: ≤20 words per quote — longer text goes to `carousel-builder`. Plan schema `skills.quote.plan.v1`.

- **`gif-maker` wrapper skill** — short looping GIF utility with two modes. Mode A: convert an existing MP4 → optimized GIF via ffmpeg 2-pass palette generation (palettegen + paletteuse with bayer dithering). Mode B: generate a 1-3s clip via a video provider (`veo-3-1-fast` default; also `kling-3` / `fal-video` / `sora-2`) then convert. Aspect crop presets: `1:1` / `9:16` / `16:9` / `4:5` / `2:1` / `1:2`. Trim controls (`--start` / `--duration`), fps + width tuning. Outputs `./generated/gif/<name>.gif`. ffmpeg required.

- **`common/runners/cli/{logo,quote,gif}.py`** — three new CLI modules. `logo.py` and `quote.py` follow the cover.py / flyer.py plan-driven pattern (skill assembles `plan.json` with per-variant prompts; CLI runs batch via `common.runners.batch`). `gif.py` is argparse-driven with two-mode dispatch (Mode A converts directly; Mode B generates via a video provider then converts).

- **`common/runners/ffmpeg.py:mp4_to_gif()`** — high-quality MP4→GIF conversion helper. Two-pass: palettegen (256-color, `stats_mode=diff`) then paletteuse (bayer dithering at `bayer_scale=5` for best size/quality tradeoff). Supports trim window (start/duration), fps + width controls, loop count.

### Changed

- **`skills.json`** — 33 entries (was 30). Three new skills registered.
- **`docs/USER-GUIDE.md`** — added "I want to design a logo", "I want a quote card", "I want a short looping GIF" sections in the AI media group.
- **`docs/COMPOSING.md`** — added 3 new orchestrator recipes: brand identity pack (logo + cover + quote card), quote card series for content marketing, animated reaction / hero loop.
- **`docs/ROADMAP.md`** — marks `logo-maker`, `quote-card-maker`, `gif-maker` as SHIPPED.
- **`VERSION` + `skills.json:version`** → `2.8.0`.

### Notes

- 33 skills total (was 30). All three new skills are additive — no breaking changes. Existing orchestrators / wrappers unchanged.
- `logo-maker` & `quote-card-maker` reuse the carousel style library + batch executor infrastructure (no new dependencies).
- `gif-maker` Mode B reuses the video provider abstraction from `video-prompt --execute`.
- `gif-maker` is the first wrapper skill in v2.x with TWO operational modes (existing-input vs generation). Mode dispatch is via mutually exclusive arg groups.
- Brand identity pack recipe (logo + cover + quote card) chains 3 skills into a $0.50-1.50 brand starter kit.

## [2.7.0] — 2026-05-21

### Added

- **`cover-maker` orchestrator skill** — title + creator + medium → cover at the medium's native aspect. Mediums: `album` (1:1 3000²), `book` (2:3 portrait), `podcast` (1:1), `magazine` (2:3), `report` (A4 portrait), `deck-cover` (16:9), `linkedin-doc` (1:1). Optional `--photo` reference. Reuses the 24-style carousel library. Plan schema `skills.cover.plan.v1`.

- **`thumbnail-maker` orchestrator skill** — 16:9 thumbnails with face-placement variants (left / right / center). Type presets: `youtube` (1920×1080), `blog` (1200×630 OG), `podcast-episode` (1920×1080). Face + bold-title aesthetic with model auto-pick (nano-banana-pro for identity-preserve, ideogram-3-quality for text-heavy). Plan schema `skills.thumbnail.plan.v1`.

- **`bg-remover` wrapper skill** — background removal utility. Default model `851-labs/background-remover` (~$0.001-0.005/image via Replicate). Alternative `pollinations/modnet` for portrait hair edges. Transparent PNG output. Single image per call; loop for batch.

- **`common/runners/cli/{cover,thumbnail,bg}.py`** — three new CLI modules. Cover & thumbnail are plan-driven (same shape as flyer.py); bg is argparse-driven (single transform).

### Notes

- 30 skills total (was 27). All three additive — no breaking changes.

## [2.6.0] — 2026-05-21

### Added

- **`avatar-maker` orchestrator skill** — turn a user photo into N profile-pic / headshot / avatar variants in a consistent style. Identity-preserve is the differentiator — defaults to `nano-banana-pro`. Multi-aspect output (square 1:1, square-tight, cover 4:5, story 9:16, wide 16:9). Reuses the carousel style library, filtered to photoreal-friendly anchors via `--style auto`. Plan schema `skills.avatar.plan.v1`.

- **`voiceover-maker` wrapper skill** — text-to-speech. Wraps ElevenLabs `eleven-tts` (multilingual, brand-voice via `voice_id`) + OpenAI `gpt-4o-mini-tts` (cheap English-strong). Supports voice picker, multilingual TTS, speed control, long-form scripts. Auto-picks provider based on language + script length + brand-voice needs.

- **`subtitle-burner` wrapper skill** — burn captions onto an existing MP4 / MOV / WebM via ffmpeg. Supports SRT, WebVTT, plain text (evenly distributed). Style presets: `modern` (white on black backplate), `minimal` (no backplate), `bold` (yellow + dense backplate). Subcommands: `burn` / `preview`. No API calls — pure ffmpeg.

- **`common/runners/ffmpeg.py:burn_captions()`** + **`common/runners/subtitles.py`** — SRT/VTT/plain-text parser + ffmpeg drawtext caption helper.

- **`common/runners/cli/_shared.py`** — extended with `--voice-id` / `--speed` / `--lang` args for TTS.

### Notes

- 27 skills total (was 24). All three additive — no breaking changes.

## [2.5.0] — 2026-05-21

### Added

- **`flyer-maker` orchestrator skill** — single-image batch generator for event posters / flyers / social event graphics. Takes structured event details (`--title / --date / --location / --cta`) + optional `--photo <path>` reference + optional `--style <library-id>`. Picks a text-friendly + multi-ref-capable model automatically (gpt-image-2 / ideogram-3-quality / nano-banana-pro). Outputs multi-aspect renders (default: portrait 1080×1350 + square 1080×1080 + story 1080×1920; also supports landscape, a4, tabloid). Reuses the carousel style library (24 visual styles) + the runner's batch executor.
- **`common/runners/cli/flyer.py`** — plan-driven CLI (schema `skills.flyer.plan.v1`). Same shape as carousel/reel: skill assembles the plan with per-aspect prompts incl. composition zones; CLI runs batch + manifest + `--resume`.
- **`docs/ROADMAP.md`** — enumerates identified gaps (other single-image use cases like cover-maker / avatar-maker / thumbnail-maker / banner-maker; audio gaps like voiceover-maker / subtitle-burner; utility gaps like upscaler / bg-remover / style-transfer). Marks priorities + non-goals.

### Notes

- 24 skills total (was 23). New skill is layer=orchestrator, sibling to `carousel-builder` and `reel-builder`.
- No breaking changes — additive. Style library / runners unchanged.
- Composition zones (headline / visual / details) are encoded in the per-aspect prompt template, not in code. To customize a layout, edit the prompt-assembly logic in the skill's SKILL.md pipeline.
- v1 limitations (documented): no QR codes, no print-ready CMYK / 300DPI output, no auto-translation for bilingual variants (run twice with different `--lang`), single composition mode per aspect (`--composition` flag is reserved but only `top-headline` / `side-headline` for landscape are implemented).

## [2.4.0] — 2026-05-21

### Added

- **`skills-styles` meta-skill** — CRUD on the local style library + upstream-PR helper. Subcommands: `list / show / path / add [--from <existing>] / edit / remove / validate / diff / submit`. Skill operates ONLY on `~/.claude/style-library/<modality>/<id>.md` (user dir) — bundled styles stay read-only. The submit subcommand builds a self-contained `./style-submission-<ts>-<modality>-<id>/` package with the style file at the correct repo path + `PR-DESCRIPTION.md` template + `README.md` with step-by-step manual PR instructions. No auto-`gh pr create` (intentionally; v1 trusts user to do git ops).

- **`common/runners/styles.py` extensions**:
  - `REQUIRED_FRONTMATTER` + `REQUIRED_BODY_FIELDS` schemas per modality
  - `validate_style(style) -> list[str]` returning issue messages
  - `copy_template(modality, new_id)` — create user-override from `<modality>/_template.md`
  - `copy_existing(source_id, new_id, modality)` — copy a bundled style as a starting point
  - `resolution_status(id, modality)` — returns `bundled | user-only | override | missing`
  - `resolved_path(id, modality)` — actual file the loader picks

- **`common/runners/cli/styles.py`** — argparse subcommands for the keys CLI plumbing.

- **Per-modality templates** at `common/style-library/<modality>/_template.md` (carousel + video + music). Each includes the full schema as placeholders + an inline `<!-- conventions -->` block reminding the user of the validator's rules + reviewer expectations.

### Notes

- 23 skills total (was 22). New skill is layer=meta, sibling to `skills-update` and `skills-keys`.
- No breaking changes — additive. `carousel-builder`, `reel-builder`, `music-prompt` unchanged.
- Style library loader (`load_style`, `list_styles`, `find_by_tags`) is unchanged — orchestrators consume it the same way.
- v1 submit doesn't run `git` — it prepares a portable submission package + prints instructions. Future v2 may add `--auto` with `gh` CLI gating.

## [2.3.1] — 2026-05-21

### Added

- **`skills-keys` meta-skill** — CRUD on `~/.skills.env` (chmod 600) so users don't have to hand-edit dotfiles. Subcommands: `list / add / update / remove / enable / disable / verify / export / path`. Interactive (silent) input via `getpass` when no value is passed on the CLI — keys never enter shell history or conversation transcript.

- **`common/runners/keysfile.py`** — atomic CRUD over `~/.skills.env` with chmod 600 enforcement + `mask()` helper + `load_into_env(override=False)` that merges file entries into `os.environ` without overriding explicit shell exports. Precedence is documented: shell `export` > file > unset.

- **`common/runners/verify.py`** — lightweight HTTP probe (no SDK deps) for 9 providers: OpenAI, Gemini, Anthropic, BFL, Ideogram, Replicate, FAL, Runway, ElevenLabs. Returns `valid | invalid | unknown | unsupported | unset`. Suno + Kling don't expose verify-friendly endpoints — they show `unsupported` (test via real generation).

- **`common/runners/cli/keys.py`** — argparse-driven CLI with subcommands. Gate flag shortcuts (`enable / disable` for `SUNO_API_ENABLED`, `LYRIA_API_ENABLED`, `OPENAI_SORA_API_ENABLED`). `export` produces eval-ready lines for shell-level apply.

- **`SKILLS_KEYS_FILE` env override** — relocate the file (useful for CI, multi-profile setups, dotfile syncing).

### Changed

- **`config.load_all_providers()`** now calls `keysfile.load_into_env(override=False)` before importing providers. Existing shell exports still win — this is purely additive: keys stored in `~/.skills.env` become visible to runners without the user having to `source` it.

### Notes

- Plaintext at rest + `chmod 600` is the v1 security posture. macOS Keychain / Linux Secret Service / encrypted vault deferred to keep cross-platform parity.
- v1 verify covers 9 of the ~12 supported provider keys. Adding new probes is a 20-line PR in `common/runners/verify.py`.
- This skill is a meta-skill (sibling to `skills-update`) — it operates on the user's machine state, not on prose.
- 22 skills total (was 21).

## [2.3.0] — 2026-05-21

### Added

- **`research-brief` skill** — produces a structured research brief on any topic: TL;DR, key facts with citations, notable quotes, suggested narrative angles, open questions, out-of-reach flags. Supports `--depth quick|standard|deep` (3 / 7 / 15 queries), multi-source (WebSearch + WebFetch + optional Firecrawl / Exa MCP), per-format output (`--format brief|outline|article-ready`), per-language output (`--lang en|ru|mixed`), and angle bias (`--for carousel|reel|post|essay|landing`). Saves to `./generated/research/<topic-slug>-<date>.md` for downstream `--research <path>` ingestion.

- **`carousel-builder` skill** — orchestrator that turns a topic or research brief into an N-slide carousel (3-12 slides; default 8) with consistent visual style. Picks a style from the bundled library (24 carousel styles) OR matches a user-provided reference image. Wraps `essay-write` / `viral-text` (content) + `image-prompt --execute` (slides) + new `common/runners/batch.py` (parallel execution). Outputs `./generated/carousel/<slug>/slide-{1..N}.png` + `captions.md` + `manifest.json` + `style-used.md` + `prompts.md`. Supports `--platform instagram|linkedin|tiktok`, `--text-mode embedded|overlay|none`, `--style auto|<library-id>|--style-ref <image>`, `--resume`, `--prompts-only` (safe dry-run).

- **`reel-builder` skill** — orchestrator that produces a vertical reel (1-4 shots × 5-8s each + matched music + optional burned-in captions). Wraps `viral-text` (script) + `video-prompt --execute` (shots) + `music-prompt --execute` (track) + `common/runners/ffmpeg.py` (concat + audio mix + caption burn). Picks from 12 directorial video styles + 12 music genre presets. Outputs `./generated/reel/<slug>/final.mp4` + `shots/` + `music.mp3` + `script.md` + `manifest.json`. Supports `--shots 1-5`, `--shot-duration <s>`, `--aspect vertical|square|horizontal`, `--captions on|off`, `--style auto|<id>`, `--music-style auto|<id>`, video provider auto-pick across Veo 3.1 / Sora 2 / Kling 3.0 / Runway Gen-4, music provider auto-pick across Suno v5.5 / Lyria 3 Pro / ElevenLabs Music / Stable Audio 2.5.

- **Style library at `common/style-library/`** — 50 bundled styles + user-override path at `~/.claude/style-library/<modality>/<id>.md`. Three subdirs:
  - `carousel/` — 24 visual styles (kinfolk-minimal, swiss-grid-poster, art-deco-gold, memphis-90s, neon-cyberpunk, brutalist-poster, gradient-mesh-modern, dark-academia, y2k-chrome, holographic-iridescent, polaroid-faded, risograph-2color, voxel-3d-cube, bauhaus-primary, sketch-bw-line, sticker-mascot, flat-vector-illustration, photo-editorial-bw, paper-cutout-craft, retro-magazine-70s, isometric-3d-soft, watercolor-soft, hand-drawn-pastel, low-poly-3d).
  - `video/` — 12 directorial styles (wes-anderson-symmetric, fincher-cold-lowkey, wong-kar-wai-neon-dream, nolan-imax-handheld, chazelle-musical-glow, refn-neon-static, tarkovsky-slow-meditative, villeneuve-monumental, soderbergh-natural-light, edgar-wright-snap-cuts, david-lynch-dream-static, inarritu-long-take-handheld). Director names appear ONLY in display/metadata; never reach the model.
  - `music/` — 12 genre recipes ported from `music-prompt/references/genre-recipes.md` (afrobeats, ambient-drone, cinematic-orchestral, country-modern, drill-uk, gospel-modern, hardcore-punk, hyperpop, jazz-fusion, k-pop, lofi-hiphop-chill, synthwave). Includes paste-ready Suno Style box + meta-tag stacks + Udio prompt + Lyria field-driven block + ElevenLabs prompt per genre.

  Each style file has a `_index.md` (table view) and a per-modality `README.md`.

- **`common/runners/styles.py`** — style loader (frontmatter parser, anchor extraction, user-override priority, find-by-tags).

- **`common/runners/batch.py`** — batch executor with parallelism (ThreadPoolExecutor), manifest.json after every state change, `--resume` semantics, single aggregate cost confirm before first call.

- **`common/runners/ffmpeg.py`** — pure-subprocess wrappers for concat / audio-mix / caption-burn-in. `detect_ffmpeg()` probe. Graceful fallback when ffmpeg is absent.

- **`common/runners/cost.py` extended** — `confirm_batch()` and `batch_budget()`. Per-modality defaults: `carousel: $1.50`, `reel: $4.00`, `research: $0.00`. Env overrides: `SKILLS_CAROUSEL_BUDGET`, `SKILLS_REEL_BUDGET`, `SKILLS_RESEARCH_BUDGET`.

- **`common/runners/cli/carousel.py`** + **`common/runners/cli/reel.py`** — new CLI entries for plan-driven batch execution. Per-skill `scripts/run.py` thin entries follow the same auto-venv re-exec pattern as image/video/music.

- **`install.sh` enhancements** — `install_style_library()` copies the bundled library to the install prefix. `install_ffmpeg()` detects ffmpeg, offers to `brew install ffmpeg` (Mac) / `apt-get install -y ffmpeg` (Linux), with `SKILLS_SKIP_FFMPEG=1` opt-out.

### Notes

- The 3 new skills are LAYER `orchestrator` — they coordinate other skills + the execute runner. `research-brief` is the upstream feeder for both `carousel-builder` and `reel-builder` via `--research <path>`.
- `reel-builder` is the most expensive skill in the collection (default ~$2-5 per reel). Always run `--prompts-only` first to inspect script + per-shot prompts.
- ffmpeg dependency is OPTIONAL — without it, `reel-builder` still generates shots + music separately and prints the manual stitch command.
- User-overridable style library: drop a `<id>.md` file under `~/.claude/style-library/<modality>/` to override or extend the bundled library.
- No breaking changes — additive release. `image-prompt`, `video-prompt`, `music-prompt` unchanged.

## [2.2.1] — 2026-05-21

### Changed

- **`install.sh` auto-installs runner deps.** Removes the separate `pip install -r common/runners/requirements.txt` step that v2.2.0 required. The installer now creates a dedicated venv at `$PREFIX/.runners-venv`, upgrades pip, and installs `requests` + `openai` + `google-genai` + `boto3` automatically. Per-skill `scripts/run.py` re-execs through that venv interpreter, so the user gets `--execute` working out of the box.
- Honours `SKILLS_SKIP_VENV=1` env flag to opt out of the auto-venv (useful for CI / minimal installs).
- Honours `--update` to refresh the venv from scratch on subsequent runs.
- Graceful fallback: if python3 is missing, < 3.10, venv module unavailable, or pip install fails, the installer prints a warning + manual instructions instead of failing. Skills still ship; only `--execute` degrades to prompt-only with an actionable error.

### Updated docs

- README "Optional API execution" section drops the manual `pip install` step.
- `image-prompt/references/execute.md`, `video-prompt/references/execute.md`, `music-prompt/references/execute.md` updated.
- `docs/walkthroughs/execute-end-to-end.md` updated.
- `common/runners/README.md` updated.
- `.env.example` mentions auto-install.

## [2.2.0] — 2026-05-21

### Added — optional execution layer for image-prompt / video-prompt / music-prompt

If the relevant API key is set in env, the three prompt skills can now actually
call the vendor and save a real PNG / MP4 / MP3 — not just produce prompt text.
If keys are missing the skills stay PROMPT-ONLY, exactly as in v2.1.

- **`common/runners/`** — new Python package shipped alongside the skills.
  Provider abstraction (ABC) + 31 registered providers across 14 modules
  covering 10 vendors: OpenAI (gpt-image-2, Sora 2 / Sora 2 Pro, gpt-4o-mini-tts),
  Google (Imagen 4 / Ultra / Fast, Nano Banana Pro, Veo 3.1 / Fast, Lyria 3 Pro),
  Black Forest Labs (Flux 1.1 Pro, Flux 2 Pro, Flux Kontext, Flux Schnell),
  Runway (Gen-4, Gen-4 Turbo, Aleph), Kuaishou (Kling 3.0 with HS256 JWT signing),
  Ideogram (3 Turbo / Default / Quality), ElevenLabs (Music + TTS), Suno (v5.5),
  fal.ai router (image + video + music — covers Flux/Recraft/Seedream/Kling
  mirrors/Hunyuan/LTX-2/Wan), Replicate router (image + video + music — covers
  SD 3.5/MusicGen/Stable Audio/many open-source models). Architecture ported
  (and trimmed) from `/Users/mikefluff/Documents/figma/` — provider abstraction,
  poll-with-timeout, and S3-compatible object_storage_adapter — without the
  Temporal / SurrealDB / multi-tenancy weight.
- **`common/runners/cli/`** — three modality CLIs (`image`, `video`, `music`)
  with consistent flags: `--model`, `--prompt` / `--prompt-file`, `--output`,
  `--variants`, `--yes`, `--check`, `--list-providers`, `--cost-only`,
  `--timeout`, plus modality-specific `--duration`, `--lyrics-file`,
  `--instrumental`, `--image-url`, `--video-url`, `--size`, `--quality`,
  `--voice`, `--fal-model`, `--replicate-model`.
- **Per-skill entry scripts**: `image-prompt/scripts/run.py`,
  `video-prompt/scripts/run.py`, `music-prompt/scripts/run.py` — thin
  delegates to the shared CLI; auto-discover `common/runners/` regardless of
  install location.
- **Storage**: local FS (`./generated/<modality>/<timestamp>-<slug>.<ext>`)
  always; optional S3 / DigitalOcean Spaces / Cloudflare R2 / MinIO upload
  when `S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY` (and optional `S3_ENDPOINT
  / S3_REGION / S3_PATH_PREFIX`) are set. URL printed alongside local path.
- **Cost preview + confirmation**: static price table per provider; estimates
  >$0.10 USD prompt for Y/N on stdin (bypass with `--yes`). Cost-only
  inspection via `--cost-only`.
- **Fall-back behaviour**: missing key / API failure / timeout always saves
  the prompt to `./generated/<modality>/<timestamp>-prompt-only.txt` with a
  one-line reason. Skill stays useful end-to-end.
- **Gated providers**: Sora 2 / Sora 2 Pro behind `OPENAI_SORA_API_ENABLED=1`,
  Lyria 3 Pro behind `LYRIA_API_ENABLED=1`, Suno v5.5 behind
  `SUNO_API_ENABLED=1` — protects against accidental spend until the user
  confirms account access.
- **New reference files**: `image-prompt/references/execute.md`,
  `video-prompt/references/execute.md`, `music-prompt/references/execute.md`
  — full provider matrix + env vars + cost preview + troubleshooting + fall-
  back behaviour per skill.
- **Walkthrough**: `docs/walkthroughs/execute-end-to-end.md` — three worked
  examples (gpt-image-2 image / Veo 3.1 Fast video / Suno v5.5 music) plus
  multi-cloud output, pre-flight check, and troubleshooting.
- **`.env.example`** at repo root — full env-var matrix with per-provider
  comments and storage options.
- **SKILL.md updates** in all three prompt skills: new `--execute` /
  `--check` / `--list-providers` / `--yes` / `--output` / `--timeout` modes;
  pipeline step "Optional Execute"; new constraints (never print keys,
  confirm cost, fall back gracefully, default output dir); EN+RU invocation
  hints (`execute the prompt`, «выполни промпт», «вызови модель»).
- **Model matrix updates** — 55 new `**Execute via**:` lines across 19 model
  files mark which models execute via a native API, which route through fal/
  Replicate, and which stay prompt-only (no public API).
- **install.sh** — new `install_runners()` step copies `common/runners/`
  alongside the skills.
- **smoke gate** — new step imports every provider module and asserts the
  registry has ≥25 providers.
- **CI** — `pip install -r common/runners/requirements.txt` step added so
  the smoke import works on a fresh runner.

### Changed

- `skills.json` `version` → `2.2.0`. (`VERSION` likewise.)
- README adds an "Optional API execution" section listing setup + provider
  coverage + output behaviour.
- `docs/USER-GUIDE.md` extends the three prompt-skill sections with
  `--execute` examples.

### Notes

- Skills stay 100% backward-compatible. v2.1 prompt-only workflow is the
  default; `--execute` is opt-in.
- Runtime deps: `requests` always; `openai` + `google-genai` recommended for
  the most-used vendors; `boto3` only if you opt into S3 upload. Other
  vendors are reached via plain `requests` so no provider requires its own
  SDK.
- The runner does NOT implement Temporal / queues / multi-tenancy / a UI —
  it's a single-user CLI with simple sync polling. For production multi-
  tenant gen infrastructure, see the figma project this design borrows from.

## [2.1.0] — 2026-05-21

### Removed — release.yml CI auto-bump workflow

- `.github/workflows/release.yml` deleted along with `scripts/decide-bump.sh`
  and `scripts/bump.sh` — the conventional-commit-driven auto-bumper was
  misfiring (cut a phantom v3.0.0 off the v2.0.0 commit). Releases are now
  manual; this entry is the proper semver-minor follow-up to v2.0.0.

### Added — new `music-prompt` skill

Parallel to `image-prompt` and `video-prompt`, completing the visual+audio
prompt-skill trio for AI generation.

- **10+ frontier music models** covered: Suno v5.5 (chirp-crow, March 2026 GA;
  Voices clone, Custom Models, Studio DAW, 12-stem export, Replace Section,
  Remaster, Cover); Udio v4 (~10-min coherent songs, Stem Separation 2.0,
  Developer Platform API); Google Lyria 3 Pro (March 25 2026; 3 min, 48 kHz,
  watermarked, EN/ES/FR/JP); ElevenLabs Music (August 2025; exclude-styles +
  cleanest licensing); Stable Audio 2.5 (September 2025; ARC 8-step + sound
  design + audio-to-audio); Meta MusicGen / AudioCraft (open-source, melody
  conditioning); Tencent SongGeneration / LeVo (open-source 3B, EN+ZH);
  Sonauto v2 Beta (stems + word-level alignment); Riffusion v5 (free webapp);
  Mubert API 3.0 (parameter-driven background music).
- **2026 canonical 8-category meta-tag taxonomy** in `references/meta-tags.md`
  — Structure / Vocal delivery / Vocal effects / Instrumental /
  Mix-production / Energy-dynamics / Era-genre / FX cues. 200+ community-
  validated tags. Stacking rules with `|` separator inside one bracket, max
  4-8 tags, ordering: core genre → era → mood → instrument → mix/FX → vocal
  direction.
- **Deep-dive references**: `vocal-tags.md` (voice character / register /
  style / effects + mini-recipes); `instrumental-tags.md` (drums / bass /
  guitars / keys / strings / brass / world + per-genre quick-picks);
  `mix-production-tags.md` (era / stereo width / reverb / delay / compression
  / mastering); `song-structure.md` (5-block universal structure, length
  budgets per model, genre templates); `lyrics-conventions.md` (lyrics-box
  vs style-box rule on Suno, ad-libs in parens, repetition by duplication,
  language switch at section boundary).
- **12 paste-ready genre recipes** in `references/genre-recipes.md`:
  hyperpop, UK drill, modern country, lo-fi hip-hop, ambient cinematic,
  orchestral film score, K-Pop 4th gen, Afrobeats 2024, jazz fusion,
  hardcore punk, 80s synthwave, contemporary gospel. Each with target
  models, BPM, key signal, Style box + Lyrics box, variations.
- **Decision tree** in `references/model-picker.md` — intent → model
  mapping + capability matrix (rows: models; columns: Vocals / Stems /
  Max length / Brackets / Stacking / Voice clone / Cover/Remix / API /
  Open weights / Languages).
- **SKILL.md modes**: `--model` (14 model keys), `--genre` (12 recipe
  keys + free-form), `--instrumental`, `--lyrics file:<path>`, `--exclude`
  (exclude-styles), `--cover`, `--extend`, `--variants N`, `--improve`.
- **6 before-after calibration pairs** in `examples/before-after.md`:
  anthemic modern pop (Suno), drill verse (Suno), long-form jazz fusion
  (Udio), label-safe orchestral cue (Lyria 3 Pro), indie folk with
  exclude-styles (ElevenLabs), RU pop ballad with language switch at
  section boundary (Suno).

### Changed

- `skills.json` — 17 → 18 skills.
- `README.md` — added music-prompt scenario row and skills-table entry.

### Notes

- `music-prompt` reuses the same skill philosophy as image-prompt /
  video-prompt: declarative SKILL.md, load-on-demand references, EN+RU
  parity (lyrics support multilingual on Suno + ElevenLabs; Lyria limited
  to EN/ES/FR/JP), MIT, zero external deps.
- Some agent-flagged TODO markers remain in a few model files (Riffusion
  API GA status, etc.) — they're explicit placeholders for next-pass
  verification, not blockers.

## [2.0.0] — 2026-05-20

### BREAKING — major restructure of `image-prompt` + `video-prompt`

Both prompt skills now cover the 2025-2026 frontier across all major modes:
text-to-image edit / multi-reference / text-in-image for image; T2V / I2V /
V2V / extend / multi-shot / native-audio for video. The single
`references/model-specifics.md` file is replaced by per-vendor / per-tier files
under `references/models/`. Direct references to the old path will break — load
via SKILL.md's REFERENCES table, not by hardcoded path.

### Added — image-prompt (v2)

- **14+ frontier image models**: Midjourney v7 (incl. `--sref`, `--oref`, `--raw`),
  Flux 2 Pro / Flux 2 Dev / Flux 1.1 Pro Ultra (Raw) / Flux Kontext (edit) /
  Flux Schnell / FLUX.1 Krea [dev], Imagen 4 / Imagen 4 Ultra / Imagen 4 Fast,
  Nano Banana Pro (Gemini 3 Pro Image — 4K, 5-person consistency, 14 refs,
  thinking mode), gpt-image-2 (~99% char accuracy, 16 refs; DALL-E 3 retired
  2026-05-12), Ideogram 3 (Turbo / Default / Quality — text-in-image leader),
  Recraft V3 (SVG vector), Seedream 4.5 / 5.0 (weighted multi-ref), Qwen-Image
  2.0 + 2512 (Apache-2.0, CJK + multilingual typography), HiDream-O1-Image
  (MIT, pixel-native), Krea-1 ("no AI look"), SD 3.5 Large + Turbo + Medium
  (with weight-syntax no-op caveat).
- **New modality references**: `references/editing-prompting.md` (i2i,
  character/identity locks, multi-ref weighting, preserve/change grammar);
  `references/text-in-image.md` (per-model text rendering rules + multilingual);
  `references/model-picker.md` (intent → model decision tree + capability
  matrix).
- **New SKILL.md modes**: `--edit`, `--reference <path@role:weight>` (repeatable),
  expanded `--model` enum to 14+ keys, pipeline step 2.5 (mode select),
  intent-based default-model logic.
- **Updated `prompt-formula.md`**: 7th conditional block "References / multi-ref"
  with weighted-role syntax + Kontext deviation note.
- **+4 new before-after pairs** in `examples/before-after.md`: text-in-image
  (Ideogram 3 Quality), edit + character consistency (Flux Kontext), multi-ref
  composite (Seedream 4.5), open-weights multilingual (Qwen-Image 2.0).

### Added — video-prompt (v2)

- **20+ frontier video models**: Veo 3.1 / 3.1 Fast (native synced audio, 4K,
  ~120ms lip-sync, scene-extend), Sora 2 / Sora 2 Pro (audio + cameos +
  multi-shot), Kling 3.0 / Kling 2.6 Elements (4 refs per scene) / Kling Master,
  Runway Gen-4 / Gen-4 Turbo / Aleph (V2V — add / remove / replace / relight /
  re-angle / restyle / extend) / Act-One (performance transposition),
  Luma Ray 3 / Ray 3 Modify (Start+End keyframes + Character Ref swap),
  Pika 2.2 (Pikaframes / Pikadditions / Pikaswaps), MiniMax Hailuo 02 /
  Hailuo 02 Pro (best physics), Higgsfield Cinema Studio (70+ named camera
  presets, Soul ID, Start+End frames — wraps Sora 2 / Veo 3.1 / Kling /
  Seedance / Wan), LTX-2 / LTX-2 Distilled (Lightricks open-source 4K + audio),
  HunyuanVideo 1.5 / HunyuanCustom (Tencent open-source), Wan 2.2 / 2.7
  (Alibaba MoE), Seedance 1.0 Pro (ByteDance multi-shot), Mochi 1 (Genmo
  legacy).
- **New modality references**: `references/audio-prompting.md` (Dialogue /
  SFX / Ambient grammar, prosody adverbs, lip-sync rules, talking-head
  template, 5-layer cap); `references/i2v-prompting.md` (motion-over-still
  law, never-re-describe-frame, physical tethers); `references/v2v-editing.md`
  (action-verb-first grammar, single-change-per-pass, per-model duration
  caps); `references/multi-shot.md` (Shot 1/2/3 blocks, style anchors,
  transitions: `new shot:` / `cut to:` / `match cut on`); `references/
  identity-references.md` (Sora Cameos / Kling Elements / Runway Act-One /
  Higgsfield Soul ID / HunyuanCustom — "name the ref, don't re-describe").
- **New SKILL.md modes**: `--mode t2v|i2v|v2v|extend`, `--audio`, `--dialogue
  "..."`, `--end-frame "..."`, `--shots N`, `--ref name=path,...`, `--cluster
  audio|i2v|v2v|open|aggregator`. Expanded `--model` enum to 22+ keys, with
  deprecated aliases (`kling-1-6`, `pika-1-5`, `gen-3`, `luma-dream`).
- **Updated `camera-vocabulary.md`**: + Higgsfield aggregator presets section
  (Bullet Time / Crash Zoom / Vertigo / FPV / Robo-arm / Speed Ramp), + Sora 2
  multi-shot transitions, + Cinema Studio lens/body vocab.
- **Updated `pacing-modes.md`**: + dialogue-scene mode, + music-video mode
  (beat-synced).
- **Updated `beat-structure.md`**: appended "Beat structure with native
  dialogue" — dialogue obeys beat budget, one speaker per beat, prosody before
  the quote.
- **+5 new before-after pairs** in `examples/before-after.md`: dialogue with
  audio (Veo 3.1), I2V (Kling 3.0), V2V single-verb passes (Runway Aleph),
  multi-shot mini-scene (Sora 2), RU audio (Veo 3.1 with verbatim RU
  dialogue line).

### Removed

- `image-prompt/references/model-specifics.md` — content migrated to
  `image-prompt/references/models/` (one file per vendor family) and
  `image-prompt/references/model-picker.md`.
- `video-prompt/references/model-specifics.md` — content migrated to
  `video-prompt/references/models/` (one file per capability tier) and
  `video-prompt/references/models/_index.md`.
- DALL-E 3 — retired 2026-05-12 by OpenAI; replaced by gpt-image-2.
  Reference retained as a brief retirement note in
  `image-prompt/references/models/openai.md`.

### Migration notes

- Anything that loaded `references/model-specifics.md` directly should now
  load via the SKILL.md REFERENCES table or via the per-vendor / per-tier
  files under `references/models/`.
- The deprecated model keys (`kling-1-6`, `pika-1-5`, `gen-3`, `luma-dream`
  for video; old DALL-E references for image) still resolve with a
  deprecation warning — schedule migration to the current keys.
- Skill philosophy unchanged: declarative SKILL.md, load-on-demand
  references, RU+EN parity, MIT, zero external deps.

## [1.9.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v1.9.1)

## [1.9.0] — 2026-05-20

### Added — sprint v1.9 distribution + visibility

- **Refreshed launch-post drafts** — `docs/LAUNCH-POST.md` rewritten as an
  index pointing to per-platform files under `docs/launch-posts/`:
  `x-thread.md` (single tweet + 9-tweet thread), `linkedin.md` (long post),
  `hacker-news.md` (Show HN + body), `reddit.md` (r/ClaudeAI, r/programming,
  r/copywriting variants), `substack.md` (long-form blog post),
  `awesome-claude-code.md` (one-line entry + paragraph + PR body). All
  drafts reflect current state (17 skills, 28 linter categories, all
  wrappers) instead of the stale "11 / 23" numbers.

- **npm packaging** — new `package.json` + `bin/skills.js` wrapper script.
  Installable as `npm install -g @mikefluff/skills`; the `skills` binary
  delegates every subcommand (`install` / `update` / `uninstall` / `check`
  / `list` / `version` / `help`) to the bundled `install.sh`. `npm pack`
  produces a 430 kB tarball with 142 files.

- **Homebrew formula** — `Formula/skills.rb` for a future
  `mikefluff/homebrew-tap`. Bundles the repo under `libexec/` and exposes
  a `skills` binary; `skills install` copies into `~/.claude/skills/`.
  SHA256 to be filled at release time.

- **`docs/INSTALL.md`** — consolidated install reference covering curl,
  npm, Homebrew, Docker, and manual paths, plus updates / uninstall /
  troubleshooting sections.

### Changed

- README install section now shows curl + npm + Homebrew + Docker in one
  block instead of just curl + Docker. Links to `docs/INSTALL.md` for the
  complete reference.

## [1.8.1] — 2026-05-20

### Fixed

- **Finish Track E from v1.8** — v1.8.0 created `common/references/` and added
  cross-link headers to the three skill `banned-patterns.md` files but kept the
  duplicated content in place. Now actually deduplicated: 26 anti-pattern
  entries that were listed in 2-3 places live in exactly one place under
  `common/`. Affected files: `cold-email`, `landing-copy`, `release-notes`
  `banned-patterns.md`; `common/references/banned-patterns-preambles.md` (added
  email-greeting variants).
- **Pre-commit hook skip list** extended to cover anti-pattern catalogues
  (`*/references/banned-patterns*.md`, `common/references/banned-patterns*.md`)
  and `CHANGELOG.md` — these files exist specifically to quote the patterns
  they document, so the linter would always flag them otherwise.

## [1.8.0] — 2026-05-20

### Added — sprint v1.8 linter v2 + DRY + DX + index

- **Linter v2** (`writer/scripts/lint.py`): five new categories —
  `MARKETING_HYPE` (revolutionary / game-changing / world-class / industry-leading /
  cutting-edge / best-in-class / groundbreaking / next-generation / state-of-the-art /
  unparalleled / unmatched + RU equivalents); `EMPTY_CTA` (click here / tap here /
  learn more / get started without object + RU); `WEAK_OPENER` (we're excited to /
  thrilled to / proud to + RU); `VAGUE_BENEFIT` (save time / boost productivity /
  get more done + RU); `WRONG_TENSE_RELEASE` (will support/enable/etc. in
  release-notes context, severity `nit`). Total: 28 categories.

- **Code-fence skip** in linter: lines inside fenced ``` / ~~~ blocks are no longer
  scanned. Previously `skill_skills-update_input` had 74 lines of false-positive
  hits matching marketing words inside JSON examples; now clean.

- **Severity tags** (`blocker` / `caution` / `nit`) per hit + aggregate
  `by_severity` in JSON output. Nit-level hits don't escalate the overall
  verdict. New CLI flags: `--scan-code-blocks` (opt-in for calibration files),
  `--quiet` (used by `make lint-all`).

- **7 new `before-after.md` calibration files**: `canon-check`, `essay-write`,
  `skills-update`, `style-check`, `translation-sync`, `viral-text`, `cold-email`.
  Every skill (17/17) now has a calibration file showing the concrete
  transformation it produces.

- **3 expanded walkthroughs**: `viral-post.md` (129→234), `tone-shift.md` (162→276),
  `image-prompt-cover.md` (165→351). Added RU port scenarios, A/B variants,
  multi-stage shifts, cross-model comparisons, refinement decision trees,
  and per-walkthrough troubleshooting sections.

- **Skill tags** in `skills.json`: closed-dictionary `tags: []` array per skill
  (domain: fiction / non-fiction / marketing / social / product / tech-docs /
  ux-copy / visual / outreach; function: editing / generation / audit /
  translation / ops). `scripts/validate.sh` validates the dictionary.

- **`docs/SKILL-INDEX.md`** — auto-generated by `scripts/gen-skill-index.py`
  (`make gen-index`). Groups all 17 skills by layer, by domain, and by
  language. `scripts/check-docs-consistency.sh` gains a 6th sub-check
  verifying SKILL-INDEX freshness.

- **`common/references/`** — shared cross-skill anti-pattern catalogues:
  `banned-patterns-hype.md`, `banned-patterns-preambles.md`,
  `banned-patterns-empty-cta.md`. `install.sh` gains `install_shared_refs()`
  to copy them to `$PREFIX/common/references/`. `cold-email`,
  `landing-copy`, and `release-notes` `banned-patterns.md` now cross-link
  to the shared files instead of duplicating their content.

- **DX**: `make lint-all` (writer linter across every reference, example, and doc
  file — advisory); `scripts/install-precommit-hook.sh` (installs local
  `.git/hooks/pre-commit` that runs the linter on staged .md + smoke gate, skips
  calibration files); `.github/PULL_REQUEST_TEMPLATE.md` checklist extended to
  all 5 CI gates + tag-dictionary + gen-readme/gen-index + common/references
  consideration.

### Changed

- `writer` description: "23 categories" → "28 categories" (reflects linter v2).
- `viral-text`, `release-notes`, `rfc-writer` SKILL.md descriptions: explicit
  "Wraps `writer`" mention (consistency with other wrappers — moved from v1.7
  prep into shipped commit on this branch).
- `cold-email/references/banned-patterns.md`, `landing-copy/references/banned-patterns.md`,
  `release-notes/references/banned-patterns.md`: lead with cross-link to
  `common/references/` shared catalogues.
- `scripts/smoke.sh`: writer linter self-test now passes `--scan-code-blocks`
  so calibration BEFORE samples inside ``` fences still trigger neuroslop verdict.

## [1.7.0] — 2026-05-20

### Added — sprint v1.7 polish + RU паритет

Coverage parity across all 17 skills + RU support for 7 previously EN-only skills.

- **9 new per-skill snapshot fixtures** for skills lacking baseline tests:
  `skills-update`, `tone-shifter`, `cold-email`, `image-prompt`, `video-prompt`,
  `microcopy`, `release-notes`, `rfc-writer`, `landing-copy`. Total fixtures: 23.

- **8 new dedicated walkthroughs** in `docs/walkthroughs/`:
  `tone-shift.md`, `cold-email-pitch.md`, `image-prompt-cover.md`,
  `video-prompt-reel.md`, `microcopy-error-states.md`, `release-notes-saas.md`,
  `rfc-architecture.md`, `landing-launch.md`. Walkthrough count: 17.

- **RU паритет for 7 EN-only skills** (`cold-email`, `image-prompt`,
  `video-prompt`, `microcopy`, `release-notes`, `rfc-writer`, `landing-copy`):
  `languages: ["en", "ru"]` in `skills.json`; RU invocation hints in each
  `SKILL.md`; RU sections appended to references (RU→EN vocabulary tables,
  RU-specific tone notes, RU template variants); RU calibration pairs added to
  `examples/before-after.md`. EN+RU support: 14/17 skills (was 7/17).

- **`skills-update/examples/manifest-example.md`** — local marker JSON example,
  update flow walkthrough, failure modes table, cache behavior notes.

### Changed

- **`docs/COMPOSING.md`** — full rewrite as 14 named workflow recipes
  ("Ship a SaaS product launch", "Write a fiction chapter", "Pitch a startup",
  "Document an architecture decision", etc.). Layered architecture diagram
  (meta / linters / wrappers / base), skill-to-skill data flow table,
  anti-patterns section.

- **`cold-email`** — added missing `deps: ["writer"]` in skills.json
  (description always said "Wraps writer", but the deps array was empty).

## [1.6.0] — 2026-05-20

### Added — 3 new skills (tech docs + marketing)

Collection now has **17 skills** (was 14). Closes the remaining direction from the
earlier roadmap: release-notes / RFC writing / marketing copy.

- **`release-notes`** (wrapper, EN). User-facing release notes + changelogs.
  Keep-a-Changelog format (Security / Breaking / Added / Changed / Deprecated /
  Removed / Fixed). Per-audience tone (end-user / developer / ops). Per-channel
  templates (changelog page / GitHub release / email / in-app modal / push /
  quarterly recap). Anti-marketing-fluff bans ("revolutionary", "we're thrilled
  to announce", etc.). References:
  - `sections.md` — Keep-a-Changelog 6 sections + decision rules
  - `audience-tone.md` — user / dev / ops voice differences + mixed-audience patterns
  - `structure.md` — version headers, length budgets per output format
  - `banned-patterns.md` — strip list (marketing hype, vague improvements,
    feelings preambles, future-tense for shipped work)
  - 5 calibration before/after pairs (SaaS / API / mobile / major release / recap)

- **`rfc-writer`** (wrapper, EN). Engineer-facing design documents — RFCs, ADRs,
  Tech Specs, Design Docs. Per-type structure (context / problem / proposal /
  alternatives / consequences / decision / open questions). RFC 2119 keywords
  (MUST / SHOULD / MAY) with capitalization rules. Forces at-least-2-alternatives
  plus "do nothing" baseline. References:
  - `document-types.md` — when to use RFC vs ADR vs Tech Spec vs Design doc
  - `templates.md` — full section templates per type
  - `rfc-2119.md` — keyword semantics + usage patterns
  - `alternatives.md` — how to list fairly, "Why not X?" pattern, comparison tables
  - `review-checklist.md` — common gaps and weak signals to flag
  - 4 calibration before/after pairs (ADR / RFC / Tech Spec / Design doc)

- **`landing-copy`** (wrapper, EN). Marketing copy — landing page sections (hero
  / features / pricing / FAQ / footer), SEO meta (title + description + Open
  Graph + Twitter cards), paid ad copy (Google Ads RSA / Facebook / LinkedIn /
  X / Reddit / TikTok). Julian Shapiro 5-step hero formula + 5 alternatives
  (outcome-led / old-vs-new / quantified / category+qualifier / direct-address
  / negation-led). Strict char limits per platform with i18n expansion factors.
  References:
  - `surfaces.md` — full taxonomy of marketing-copy surfaces + audience-tone mapping
  - `hero-formula.md` — Julian Shapiro 5-step + 6 alternative formulas + headline/
    subheadline/CTA rules
  - `feature-blocks.md` — 3-block / 6-block / detailed-feature patterns + how-it-works
  - `seo-meta.md` — title + description + OG + Twitter + per-page-type templates
  - `ad-copy.md` — per-platform templates (Google RSA / FB / LinkedIn / X / Reddit /
    TikTok) with variant strategy
  - `char-limits.md` — quick-reference table for every surface
  - `banned-patterns.md` — marketing hype, vague claims, generic CTAs, fake urgency
  - 8 calibration before/after pairs (hero / feature / SEO / Google Ad / FB / LinkedIn
    / Twitter / FAQ)

### Changed

- `skills.json` — +3 new entries (release-notes, rfc-writer, landing-copy)
- `README.md` — "Seventeen skills, one base linter + twelve wrappers + three
  linters + one meta-skill"
- `docs/USER-GUIDE.md` — added 3 use-case sections + scenario picker entries
- Repo layout in README updated to "17 skills, one folder each"

## [1.5.0] — 2026-05-20

### Added — 3 new skills (visual + UX)

Imported high-value content from `/Users/mikefluff/Documents/figma/` deep-scan + added microcopy from best-practices. Collection now has **14 skills** (was 11).

- **`image-prompt`** (wrapper, EN). Write prompts for AI image generators (Midjourney v6, DALL-E 3, Flux Pro, Nano Banana, SDXL). 6-part formula: `{subject} + {setting} + {style} + {lighting} + {camera} + {texture}`. References:
  - `prompt-formula.md` — 6-part structure + templates (portrait / product / scene / abstract / illustration)
  - `lighting-vocabulary.md` — portrait / scene / quality-of-light dictionaries (figma-derived)
  - `camera-vocabulary.md` — lens / aperture / format / quality-tag cheatsheet
  - `model-specifics.md` — per-model deltas (MJ params, DALL-E natural language, Flux negatives, SD weights)
  - `examples/before-after.md` — 5 calibration pairs (4-6 weak words → 40-80 strong)

- **`video-prompt`** (wrapper, EN). Write prompts for AI video generators (Kling 3.0, Veo 3, Sora, Runway Gen-3, Pika, Hailuo, Luma). CHARACTER FIRST law, Beat 1/2/3 structure, exact camera vocabulary. References (figma-derived from cinematographer/narrative.js):
  - `camera-vocabulary.md` — full DOLLY / PAN / TRACKING / CRANE / ORBIT / AERIAL / SPECIALTY dictionary with translation table
  - `beat-structure.md` — CHARACTER FIRST law, repeated-action patterns, body-detail layers, forbidden phrases that cause frozen-pose output
  - `model-specifics.md` — Kling temporal markers required, Sora narrative paragraph, Runway short prompts, Pika minimal, Luma atmospheric
  - `pacing-modes.md` — narrative / action / comedy / documentary / timelapse rules
  - `examples/before-after.md` — 5 pairs (hook / tension / breathing / POV / timelapse)

- **`microcopy`** (wrapper, EN). Write UX strings — error messages, empty states, tooltips, button labels, helper text, modals, 404/500/offline pages, onboarding cards, toasts, inline alerts. Plain language, action-oriented, never blame user. References:
  - `element-types.md` — full taxonomy with length budgets and templates per UI element
  - `length-budgets.md` — exact word/char limits, i18n expansion factors
  - `rules.md` — 10 universal rules (plain language, action verbs, no blame, no jargon, etc.) + 3 cardinal sins
  - `voice-by-product-type.md` — adjustments for SaaS / dev tool / fintech / e-commerce / consumer / B2B
  - `banned-words.md` — strip list (jargon, hedge words, robot-speak)
  - `examples/before-after.md` — 10 calibration pairs

### Added — bonus from figma deep-scan

- **`prose-edit/references/patch-refining.md`** — surgical search/replace patch strategy (from figma PatchRefinerAgent.js). Alternative to full rewrite when 90%+ of original should survive. Programmatic apply; signals fallback if patches fail >50%.
- **`style-check/references/validation-taxonomy.md`** — structured JSON output schema for machine-readable validation. Includes:
  - `scoreReasons` closed-enum (length / lack_of_specificity / promise_without_fact / generic_fear / clickbait_no_payoff / filler_banality / synthetic_template / grammar_agreement)
  - `hookAnalysis` (27 hook criteria) + `contentAnalysis` (issues by severity)
  - `metrics` per-dimension (cta / grammar / length / style)
  - `formattingRecommended` signal for downstream tooling
  - Cross-link to patch-refining as consumer

### Changed

- `skills.json` — +3 new entries (image-prompt, video-prompt, microcopy)
- `README.md` — "Fourteen skills, one base linter + nine wrappers + three linters + one meta-skill"
- `docs/USER-GUIDE.md` — added 3 use-case sections + scenario picker entries
- Repo layout in README updated to "14 skills, one folder each"

## [1.4.0] — 2026-05-20

### Added — from godacademy/figma archive mining

Imported high-value content from `/Users/mikefluff/Documents/figma/` (the author's inite.digital project — production-tuned prompts and rules).

- **`writer/references/synthetic-constructions.md`** — fake AI authenticity catalogue (7 sections):
  - Name-dropping templates (city + profession + transfer verb formulas)
  - CTA stamps ("пишите ДА", "tag someone who needs this", etc.)
  - Formula metaphors ("works like a radar")
  - Red/Green flags list templates
  - Uniform paragraph rhythm detection (LLM signature)
  - Synthetic-depth constructions ("за этим стоит", "которую стоит разобрать")
  - Pseudo-vulnerability / faux-confession patterns
- **`writer/scripts/lint.py` — new SYNTHETIC category.** 22 regex patterns covering literal phrases for name-drop templates (RU+EN), CTA stamps, formula metaphors, coaching jargon ("осознанное"), faux-confession ("я тоже через это прошёл"). Linter now has 24 categories (was 23).
- **`writer/references/ru-grammar.md`** — name declension + gender agreement for RU named entities:
  - Male names ending in -а/-я (Никита, Илья) — decline as feminine paradigm, agree as masculine
  - Foreign names -о/-е/-и/-у (Пикассо, Феллини, Гюго) — indeclinable
  - Foreign female names ending in consonant (Элизабет, Маргарет) — indeclinable
  - Patronymics, diminutives, surname patterns (-ин/-ов/-ев/-ский, -их/-ых)
  - Quick-reference table; LLM gender-agreement check protocol
- **`viral-text/references/hook-taxonomy.md`** — controllable hook generation:
  - Intent axis (5): anger / surprise / ground / give_action / sell_idea
  - Angle axis (5): numbers / conflict / new_standard / threat_to_professions / instruction_what_to_do
  - 5 × 5 matrix of 25 viable hook styles
  - 3 modes: topic-based / text-driven / improve-hook
  - Generation prompt templates for each mode
  - Calibration example with 5 hooks across distinct intent + angle pairs
- **`tone-shifter/references/brand-voice-profile.md`** — custom brand-voice JSON profile:
  - Schema: name / tone (5 enum) / styles (6 enum, 1-3) / vocabulary / avoidWords / hooks / ctaPhrases / register
  - 3 modes added to SKILL.md: `--profile`, `--infer-profile`, `--verify-profile`
  - Discriminator: registers = abstract categorical, brand-voice = concrete custom
  - Multilingual notes (brand-language fields, English taxonomy labels)

### Changed

- `writer/SKILL.md` REFERENCES table — added synthetic-constructions.md and ru-grammar.md entries.
- `viral-text/SKILL.md` REFERENCES table — added hook-taxonomy.md entry.
- `tone-shifter/SKILL.md` MODES — added 3 new modes; REFERENCES — added brand-voice-profile.md.

### Notes

- Existing `viral-text/references/viral-rules.md` and `hook-criteria.md` were already imported from figma in earlier work — no changes needed there.
- StyleSuggestAgent.js (visual-style-generator) from figma was NOT imported — out of scope (visual style detection, not prose editing).
- AGENTS.md (n8n) and .cursorrules from figma were NOT imported — non-portable project-specific.

## [1.3.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v1.3.1)

## [1.3.0] — 2026-05-20

### Added — Docker image

- **`Dockerfile`** + **`.github/workflows/docker.yml`** — multi-arch (linux/amd64 + linux/arm64) Docker image published to `ghcr.io/mikefluff/skills` on push to main and on tag. Image ships `writer/scripts/lint.py` + all 11 skills' markdown. Entrypoint commands: `lint FILE`, `lint-all DIR`, `coverage`, `validate`, `list`, `version`, `help`.
- Use cases: CI integration without `curl | bash`, containerized pre-commit, isolated lint in untrusted environments.
- README quick-link added; docs/USER-GUIDE.md "Use the Docker image" section.

### Added — Launch material

- **`docs/LAUNCH-POST.md`** — copy-pasteable drafts for X (single tweet + 7-tweet thread), LinkedIn, Substack longform, Hacker News, Reddit, awesome-claude-code PR. Plus anticipated FAQ. All drafts intentionally cite AI-slop phrases (so the linter trips on them — expected meta-evidence).

### Added — Architecture audit

- **`docs/audits/references-duplicates.md`** — documented finding that no `core/` shared-base refactor is needed. Filename-clashes (two `banned-constructions.md`) cover disjoint scopes; structural concepts (staccato, double-neg) defined once in `writer/references/`, cross-linked from wrappers.

### Changed — EN linter coverage

- **`writer/scripts/lint.py`** — 9 additional EN regex category sets added: PSEUDO_SMART, BUREAU_INV, CORPORATE, NE_X_A_Y, SELF_REF, PSEUDO_SCI, VAGUE_PERSON, NOMINALIZATION, SUPERLATIVE_OVERLOAD, plus expanded AI_QA. Synthetic EN-neuroslop fixture now triggers **18 categories / 54 hits** (was 7 / 23). EN clean-prose fixture stays clean (0 hits). All RU fixtures unaffected (new patterns are EN-only by structure).

## [1.2.0] — 2026-05-20

### Added — new skills

- **`tone-shifter`** (wrapper, RU+EN). Rewrite text in a different register without changing meaning. 6 named registers — `casual`, `friendly-professional`, `business-formal`, `academic`, `technical`, `plain-explainer` — plus a transformation-deltas matrix for each source→target pair. Wraps `writer` as final cleanup.
- **`cold-email`** (wrapper, EN). Write or rewrite cold outreach (first-touch, follow-up, intro request, re-engage, forwardable). 5-block structure, ≤120-word budget, banned ceremony patterns, anti-template subject lines. Wraps `writer` as final cleanup.

### Added — EN paritет

- **`writer/scripts/lint.py` — EN regex patterns.** Added EN coverage to FILLER_INTRO, GPT_FILLER, AI_BRIDGE, STOCK_METAPHOR, AI_INTENSIFIER, AI_HEDGE, SELFHELP, PSEUDO_CAUSAL, plus new AI_TRIPLETS category. Synthetic EN-neuroslop fixture now triggers 7 categories / 23 hits → verdict "neuroslop suspected".
- **EN sections in 5 reference files** (mirror RU rules):
  - `writer/references/structural-prose.md` — `## EN structural patterns` (staccato, em-dash abuse, comma-splice, double-negation, intensifier ladder, balance hedges, pseudo-causal bridges, nominalization, sentence-opener monotony)
  - `writer/references/neuroslop-categories.md` — `## EN AI-style signatures` (18 EN buckets EN-1..EN-18)
  - `viral-text/references/viral-rules.md` — `## EN viral hook patterns`
  - `essay-write/references/banned-constructions.md` — `## EN banned constructions for non-fiction`
  - `prose-edit/references/voice.md` — `## EN voice patterns`
- **EN test fixtures** — `tests/fixtures/en_neuroslop_full_pass.md` + `tests/fixtures/en_clean_prose.md` with snapshots.
- **EN walkthrough** — `docs/walkthroughs/en-viral-post.md` (EN content marketer persona for LinkedIn / X).

### Added — per-skill test coverage

- **8 per-skill input fixtures** in `tests/fixtures/skill_*_input.md`. Each fixture is a representative input for that skill (viral-text, prose-edit, essay-write, style-check, translation-sync, canon-check, pelevin-digression) so any future linter regression on real-world skill inputs is caught. Combined fixture count: 14 (up from 5).

### Added — dedicated walkthroughs

- **`docs/walkthroughs/canon-check-audit.md`** — story-bible audit for a fresh chapter, standalone.
- **`docs/walkthroughs/digression-insertion.md`** — Pelevin-vector digression in non-fiction essay, standalone.
- **`docs/walkthroughs/style-check-gate.md`** — manual quality gate without auto-edits, standalone.

### Added — contributor infrastructure

- **`CONTRIBUTING.md`** (root) — comprehensive contributor guide. Project structure, how-to-add-a-skill checklist, editing existing skills, bug reporting, local dev workflow, CI gate explanations, conventional-commits reference, PR checklist. Fixes broken FAQ links.
- **`.github/ISSUE_TEMPLATE/false_positive.yml`** — new template for linter / wrapper false-positive reports.
- **`bug_report.yml` + `new_skill_proposal.yml`** updated to include `tone-shifter` and `cold-email` in dropdowns.
- **`.github/workflows-template/skills-lint.yml.template`** — copy-pasteable GitHub Action that pins to a specific `Mikefluff/skills` release and runs `writer/scripts/lint.py` on the user's prose files in CI. Configurable `LINT_PATHS` and `FAIL_THRESHOLD`. Documented in USER-GUIDE under new "Use in your CI" section.

### Changed — descriptions tightened

- 6 SKILL.md descriptions shortened to ≤350 chars (canon-check 493→334, pelevin-digression 457→315, translation-sync 451→325, essay-write 443→345, prose-edit 419→312, skills-update 369→295). Improves Claude Code skill-matching discrimination.

### Fixed — shellcheck warnings

- **`install.sh:90`** — replaced `eval "$@"` (SC2294) with safe `"$@"` direct expansion. All `run` callers refactored to plain-arg style (no string-quoted shell expressions). Removes potential security risk.
- **`install.sh:254-274`** — removed unused `a1/a2/a3/b1/b2/b3` vars (SC2034); refactored `semver_cmp` to use `cut -d. -f<i>` directly.
- **`install.sh:431`** — added missing `"$INSTALL_SKILLS"` quoting (SC2086).
- **`scripts/validate.sh:61`** + **`scripts/check-docs-consistency.sh:109`** — missing quotes fixed.
- **`scripts/check-docs-consistency.sh`** — removed unused `yellow()` helper (SC2329).

### Removed

- **`docs/CONTRIBUTING.md`** — consolidated into root `CONTRIBUTING.md` (GitHub standard location). All references updated.

## [1.1.0] — 2026-05-20

### Added — user-facing documentation

- **`docs/USER-GUIDE.md`** — landing page for users. Scenario-based navigation, two-minute orientation per use case, configuration pointers, update flow summary, link to FAQ / TROUBLESHOOTING.
- **`docs/walkthroughs/`** — 5 detailed step-by-step flows, one per persona:
  - `viral-post.md` (viral-text, writer) — content marketer / SMM
  - `fiction-chapter.md` (prose-edit, writer, canon-check, pelevin-digression) — novelist
  - `non-fiction.md` (essay-write, writer, pelevin-digression) — essayist / popular-science writer
  - `translation-parity.md` (translation-sync) — translator / localization editor
  - `pre-commit-hook.md` (style-check, writer) — author who wants automatic linting
  - Each walkthrough has `title:` / `persona:` / `time:` / `skills:` frontmatter; the `skills:` list is verified against `skills.json` by CI.
- **`docs/FAQ.md`** — the questions that get asked first. Covers: which skills are required, RU vs EN coverage, data flow / privacy, uninstall, why-so-many-skills, false-positive policy, custom rules, network-failure fallback, curl-pipe safety, etc.
- **`docs/TROUBLESHOOTING.md`** — symptom → diagnosis → fix for: install/update, status-line banner, `skills-update`, linter false-positives, CI failures in forks, pre-commit hook gotchas, cross-skill issues.

### Added — CI gates for doc consistency

- **`scripts/gen-skills-table.py`** — generates the "What's in the box" markdown table from `skills.json`. Supports `--write` (update README in place) and `--check` (CI gate: fail if README out of date).
- **`scripts/check-docs-consistency.sh`** — five-step gate:
  1. README skills table matches `skills.json` (delegates to gen-skills-table.py --check)
  2. Every skill folder on disk is in `skills.json`
  3. Every walkthrough's `skills:` frontmatter list references only real skills
  4. Every skill is mentioned somewhere in `docs/USER-GUIDE.md`
  5. New skill folders since the last `v*` tag must be mentioned in `CHANGELOG.md [Unreleased]`
- **`.github/workflows/ci.yml`** — runs `check-docs-consistency.sh` on every PR/push.
- **`Makefile`** — new targets: `check-docs`, `gen-readme`.
- **`.markdownlint.json`** — disabled MD025 (single-h1) since walkthroughs have both frontmatter `title:` and an h1 by design.

### Changed — README rewritten as a slim landing

Replaced the long technical README with a 1-page landing that points users into `docs/USER-GUIDE.md` for the deep dive. The "What's in the box" table is now auto-generated from `skills.json` between `<!-- BEGIN skills-table -->` / `<!-- END skills-table -->` markers. Repo-internal sections (full project layout, Makefile targets, release flow) moved to a "Local development" section at the bottom of README + linked deep-dive docs.

## [1.0.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v1.0.1)

## [1.0.0] — 2026-05-20

### Changed — decoupled from author's specific LaTeX book project

The collection no longer assumes any specific book repository, LaTeX build, or character canon. Skills now work on any text file (`.md` / `.tex` / `.txt` / etc.) and any prose project — the editorial rules, voice principles, regex catalogues, and structural patterns stay intact; only the bindings to one author's particular setup are gone.

- **`prose-edit`**: removed `books/{god-academy,era-arkhitektorov,heavenly-code}/` paths, removed АБ/ЭА/НК naming, removed assumed `.tex` extension. Renamed AB-specific ToV section to generic "ToV pattern". `references/canon-check.md` reduced to meta-references + anglicisms rules; story-bible consistency moved entirely to the standalone `canon-check` skill.
- **`essay-write`**: removed НК naming, generic non-fiction framing. `references/structure.md` describes hypothesis chapters in general (V/H/P markers still useful for any non-fic with mixed-confidence claims). `references/biography.md` no longer references specific places or the author's memory directory — generic protocol for verifying biographical facts.
- **`style-check`**: routing table now illustrative + configurable, no hardcoded book paths.
- **`translation-sync`**: terminology / anchor-quote tables generalized to placeholder rows; transliteration table marked as illustrative pattern rather than the author's character canon.
- **`canon-check`**: SKILL.md framed as "for any book series with a story bible". `references/known-incidents.md` restructured from 6 author-specific past incidents into 5 generic detection categories.
- **`pelevin-digression`**: removed assumption that fiction context = a specific series; routing now uses frontmatter / extension / explicit user signal.
- **`writer`**: cleaned references in SKILL.md objective and `references/integration.md` to remove project-specific naming.
- **`skills.json`** + **`README.md`** + **`docs/COMPOSING.md`** — all descriptions, Quick Start examples, decision-tree text now generic.

Historical CHANGELOG entries below (v0.3.0 — v0.4.1) are preserved as-is — they describe what was done at release time, including the author-specific framing the project then had. Going forward, descriptions stay generic.

## [0.4.1] — 2026-05-20

### Changed
- (no notable changes captured in Unreleased — see commit log for v0.4.1)

## [0.4.0] — 2026-05-20

### Added — installer
- **`install.sh --list`** — print available skills + descriptions and exit.
- **`install.sh --check`** — compare local install marker to latest release, report status.
- **`install.sh --uninstall`** — remove all installed skills + marker (interactive with `[y/N]`, scriptable with `--yes`).
- **`install.sh --prune`** — used with `--update`; remove installed skills that are no longer in the upstream manifest.
- **`scripts/install-hook.sh`** — idempotent installer for the status-line banner. Detects existing `statusLine` block, asks before overwriting, supports `--uninstall`.

### Added — quality gates
- **`scripts/lint-description.py`** — advisory linter for `description:` field quality (length, prefix smell, invocation hint, internal-path bleed). Wired into `validate.sh` — emits ⚠ / · lines per skill plus a `description quality: N PASS · M INFO · K WARN` summary.
- **GitHub Actions** — `shellcheck` job (action-shellcheck, error severity only) and `markdownlint` job (markdownlint-cli2-action) added to CI.
- **`.markdownlint.json`** + **`.markdownlintignore`** — permissive base config (MD013/MD024/MD033/MD036/MD041 off, MD001/MD009/MD012/MD022/MD025/MD040 on); examples/ excluded as calibration fixtures.
- **CI install-flow coverage** — ci.yml now also exercises `--list` and `--uninstall` end-to-end.

### Added — testing
- **`tests/`** with 5 Russian-language fixtures (`neuroslop_full_pass`, `clean_prose`, `borderline`, `staccato`, `ru_calques`) and frozen snapshots of `python3 writer/scripts/lint.py --json` output. `tests/run.sh` compares actual vs snapshot; `--update` re-baselines.
- **`smoke.sh`** now runs the fixture snapshots as Stage 3.
- **`scripts/coverage.py`** — generates `docs/LINTER-COVERAGE.md` showing which of the 23 neuroslop categories `lint.py` regex-detects (currently 18 covered / 3 partial / 2 intentionally LLM-only).

### Added — community
- **`.github/ISSUE_TEMPLATE/`** with bug-report and new-skill-proposal forms, plus `config.yml` linking to Discussions.
- **`.github/PULL_REQUEST_TEMPLATE.md`** with conventional-commits reminder + pre-merge checklist.
- **`SECURITY.md`** — responsible-disclosure policy, scope, contact.
- **GitHub Discussions** enabled, repo topics set (`claude-code`, `claude-skills`, `prose-editing`, `russian-language`, `anti-llm-detection`, `neuroslop`, `writing-tools`).

### Added — docs
- **`docs/COMPOSING.md`** — dependency graph (ASCII), "when to invoke which" decision tree, common composition patterns, anti-patterns.
- **README** — Quick Start block with typical invocations; updated project layout; Makefile targets section refreshed.

### Improved
- **`hooks/skills-update-banner.js`** v2 — now shows `skills vX→vY +N skills (release topline)` instead of bare version delta. Fetches `skills.json` from remote release to compute skill-count delta. Extracts first bullet from release body for topline. Caches both for 24h.
- **`Makefile`** — new targets: `uninstall`, `check`, `install-hook`, `test`, `coverage`.

## [0.3.0] — 2026-05-20

### Added — new skills
- **`translation-sync`** (linter). Pre-commit parity checker for multilingual book translations (RU ↔ EN ↔ PT-BR). 15-point pre-commit checklist + per-language typography rules + terminology canon table + anchor-quote canonical translations + names / patronymics / diminutives rules + cultural-realia footnote pattern + "do not smooth this number" guard. Read-only — produces a structured parity report.
- **`canon-check`** (linter). Story-bible consistency auditor for the author's book series (АБ / ЭА / НК). Greps entities in changed chapters, cross-references `story-bible.tex`, flags BLOCKING contradictions / WARNING gaps / INFO new details. Core principle: trust the text, not memory. Ships with the documented incident catalogue (хват Ирэн, яйцо-Квинта, рыжая ведьма, число смехов Вэй Лина, возраст Лии, возраст отца Дана).
- **`pelevin-digression`** (wrapper). Write a Pelevin-voice-vector digression for a fiction or non-fiction passage. 12 structural techniques (bracket-essay, brand-name sociology, anti-gradation list, forward-link, …) + 5 banned constructions (aphoristic closer, X-превращается-в-Y, дефис-афоризм, двойной пафос, «не X, а Y»). Composes with `prose-edit` (fiction) or `essay-write` (non-fic) as the wrapped final pass.

### Improved — existing skills (godacademy edit-pattern mining)
- **`writer`**: extended cat 22 NEURAL_METAPHOR with the «держать» abstract-metaphor cluster (держит роль / связка нас держит / держит веер / etc.) and explicit "even in literal sense" ban for «шёпот / прошептал». New section in `ru-calques.md` for окказионализмы и псевдоакадемические новоделы (зряче, заимка, похвала к, следствию не подлежит, заявочное рамкирование). New section in `structural-prose.md` for N+Gen → Gen+N word-order inversion («инженера сын»). Added 4 NEURAL_METAPHOR patterns and a new `DOUBLE_NEG_REGEX` category to `writer/scripts/lint.py` (linter now flags 13 hits on the calibration fixture, up from 10).
- **`prose-edit`**: new `references/depth-pass.md` — 10-point Postirony depth-pass checklist (bleed-instead-of-wrap / recursive-accusation / body-over-mind / cruelty-surprised-by-itself / …) plus the IT-blog test ("could this edit exist in an IT blog?"). New section in `rewrite-principles.md`: comma-stitching recidivism + темпо-правила (≤ 3 staccato fixes consecutively; rewrite MUST be longer than the original; subordinate-clause or concrete-image obligatory). New section in `pitfalls.md`: AI-aphorism trap (ChatGPT aphorisms ↔ chopped beats — both nyeyroslop from opposite poles). Sharpened `cleanness-checklist.md` items with concrete examples.
- **`essay-write`**: new `references/structural-synthesis-keepers.md` — 7-pattern false-positive filter for when parallelism is a device, not nyeyroslop (anaphora, opening catalog, staircase, block-diagram, mantra, virtual opponents, dash-definitions). New section in `voice-long-sentences.md`: two-three-tier structure of long subordinate periods (main claim → : / — → expansion via metaphor or concretion → ironic coda). New section in `structure.md`: НК-specific V/H/P hypothesis markers + mandatory "what would falsify this" block.
- **`style-check`**: appended post-rewrite signature catalogue to `references/severity.md` — concrete regex patterns the author has flagged in their own past Claude rewrites (duplicate punch lines on `\n` boundaries, calque «не X, а Y» at line start, dangling adverb-stumps, N+Gen inversion).

## [0.2.0] — 2026-05-20

### Added
- **Distribution pipeline.** `install.sh` (pure bash, curl-pipeable, tarball-based by default; flags: `--skills`, `--copy-from`, `--update`, `--version`, `--prefix`, `--dry-run`). Writes `~/.claude/skills/.skills-collection.json` marker for the update flow.
- **Local dev tooling.** `Makefile` (install / validate / smoke / lint / new-skill / bump-{patch,minor,major} / release). `scripts/validate.sh` (frontmatter + cross-link check), `scripts/smoke.sh` (validate + writer-linter regression), `scripts/bump.sh` (VERSION + CHANGELOG + skills.json), `scripts/new-skill.sh` (scaffold), `scripts/decide-bump.sh` (parse conventional commits).
- **CI / release.** `.github/workflows/ci.yml` runs validate + smoke + install-dry-run on every PR/push. `.github/workflows/release.yml` parses conventional commits since the last `v*` tag, decides bump level, bumps VERSION + CHANGELOG + skills.json, commits, tags `v<new>`, pushes, publishes GitHub Release. Manual override via `workflow_dispatch.level`.
- **Update notification (both A and B).**
  - `skills-update` skill: user-invocable (`/skills-update`) — reads the local marker, fetches latest tag via WebFetch, shows the CHANGELOG diff, confirms via `AskUserQuestion`, runs `install.sh --update`. Never updates without confirmation.
  - `hooks/skills-update-banner.js`: opt-in Node status-line hook — checks remote tag with a 24-hour cache and appends a quiet `· skills v0.1.0→0.2.0 (run /skills-update)` banner. Fails open on any error.
- **Docs.** `docs/CONTRIBUTING.md` (SOTA layout contract + commit conventions + CI gates + release flow). `docs/VERSIONING.md` (semver policy, bump rules, tag format, yanking).
- **README** rewritten with badges, 5-second install, update flow, project layout, and local dev section.

### Improved
- `scripts/bump.sh` now promotes the accumulated `[Unreleased]` section into the new version instead of inserting an empty placeholder. Future releases will have populated GitHub Release notes automatically.

## [0.1.0] — 2026-05-20

### Added
- Initial release with 5 skills: `writer`, `viral-text`, `prose-edit`, `essay-write`, `style-check`.
- SOTA progressive-disclosure layout: compact `SKILL.md` (≤ 200 lines) + `references/` + `examples/`.
- `writer` ships with an offline regex linter (`writer/scripts/lint.py`) — 23 neuroslop categories, exit-code verdict.
- Cross-skill dependency: `viral-text`, `prose-edit`, `essay-write` invoke `writer` as their final pipeline step; `style-check` routes by file path to the right rule set.

[Unreleased]: https://github.com/Mikefluff/skills/compare/v2.2.1...HEAD
[2.0.0]: https://github.com/Mikefluff/skills/releases/tag/v2.0.0
[2.1.0]: https://github.com/Mikefluff/skills/releases/tag/v2.1.0
[2.2.0]: https://github.com/Mikefluff/skills/releases/tag/v2.2.0
[2.2.1]: https://github.com/Mikefluff/skills/releases/tag/v2.2.1
[0.2.0]: https://github.com/Mikefluff/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/Mikefluff/skills/releases/tag/v0.1.0
[0.3.0]: https://github.com/Mikefluff/skills/releases/tag/v0.3.0
[0.4.0]: https://github.com/Mikefluff/skills/releases/tag/v0.4.0
[0.4.1]: https://github.com/Mikefluff/skills/releases/tag/v0.4.1
[1.0.0]: https://github.com/Mikefluff/skills/releases/tag/v1.0.0
[1.0.1]: https://github.com/Mikefluff/skills/releases/tag/v1.0.1
[1.1.0]: https://github.com/Mikefluff/skills/releases/tag/v1.1.0
[1.2.0]: https://github.com/Mikefluff/skills/releases/tag/v1.2.0
[1.3.0]: https://github.com/Mikefluff/skills/releases/tag/v1.3.0
[1.3.1]: https://github.com/Mikefluff/skills/releases/tag/v1.3.1
[1.4.0]: https://github.com/Mikefluff/skills/releases/tag/v1.4.0
[1.5.0]: https://github.com/Mikefluff/skills/releases/tag/v1.5.0
[1.6.0]: https://github.com/Mikefluff/skills/releases/tag/v1.6.0
[1.7.0]: https://github.com/Mikefluff/skills/releases/tag/v1.7.0
[1.8.0]: https://github.com/Mikefluff/skills/releases/tag/v1.8.0
[1.8.1]: https://github.com/Mikefluff/skills/releases/tag/v1.8.1
[1.9.0]: https://github.com/Mikefluff/skills/releases/tag/v1.9.0
[1.9.1]: https://github.com/Mikefluff/skills/releases/tag/v1.9.1
