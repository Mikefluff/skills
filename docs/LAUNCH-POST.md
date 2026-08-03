# Launch posts

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

Per-platform copy-paste drafts, current as of v2.20.0 — 41 skills, 25 linter categories, the AI-media half and the orchestrators.

Pick the file that matches the audience and edit before posting. Every draft quotes the patterns it describes, so linting one for slop measures the examples rather than the copy; the files are marked accordingly. Tweet lengths are verified by `scripts/check-tweet-length.py`.

## Drafts

| Platform | File | Length |
| --- | --- | --- |
| X / Twitter — single tweet | [`launch-posts/x-thread.md`](launch-posts/x-thread.md) | 264 chars |
| X / Twitter — 10-tweet thread | [`launch-posts/x-thread.md`](launch-posts/x-thread.md) | all ≤280, verified |
| LinkedIn — long post | [`launch-posts/linkedin.md`](launch-posts/linkedin.md) | ~1500 chars |
| Hacker News — Show HN + body | [`launch-posts/hacker-news.md`](launch-posts/hacker-news.md) | ~2200 chars |
| Reddit (r/ClaudeAI, r/programming, r/copywriting) | [`launch-posts/reddit.md`](launch-posts/reddit.md) | per-sub variants |
| Substack / personal blog | [`launch-posts/substack.md`](launch-posts/substack.md) | long form |
| awesome-claude-code PR | [`launch-posts/awesome-claude-code.md`](launch-posts/awesome-claude-code.md) | one-line + paragraph + PR body |

## Suggested order

1. **Substack / blog post first** — sets the canonical narrative, gives X/LinkedIn/HN something to link to.
2. **HN Show HN** — needs an existing repo + ideally an existing post to link. Submit Tuesday-Thursday morning Pacific.
3. **X thread + LinkedIn long post** — same day as HN, ride the discussion if HN ranks.
4. **Reddit** — separate day, target the right sub for the angle (ClaudeAI for tech, copywriting for the marketing wrappers).
5. **awesome-claude-code PR** — anytime; not time-sensitive.

## Common questions to anticipate

When the post lands, expect these:

**Q: How is this different from Grammarly / LanguageTool / Hemingway?**

Grammarly catches grammar. LanguageTool catches typos and basic style. Hemingway catches sentence length and adverbs. None of them catch the specific patterns LLMs produce — "navigate the complexities", "rich tapestry", balance hedges, AI-style triplets ("smart, capable, and intelligent"), marketing hype ("revolutionary", "world-class"), excitement preambles ("we're excited to announce"). This is purpose-built for the LLM-output problem, which is a different shape than human-error catching.

**Q: Why a regex linter? Won't an LLM judge better?**

For pre-commit and CI gating, regex wins: ~80ms against five to ten seconds, no API cost, deterministic, no network. For nuanced rewriting the wrappers do use the model, because that is where context matters. The linter is the floor; the wrappers are the ceiling.

There is also a class regex handles better than a judge would: chatbot copy-paste artifacts. A model asked "was this pasted from ChatGPT" reasons about it. A regex either finds `turn0search3` or does not.

**Q: Why so many skills instead of one big one?**

Discovery. Claude Code matches user requests against the `description:` field. A single mega-skill would match too broadly and hurt precision. Splitting lets each skill carry a sharp discriminator, so the boundary is a discovery contract rather than taste. See `docs/COMPOSING.md` for the named recipes showing how the 41 skills chain into workflows.

**Q: Russian-first sounds limiting. What about English?**

English is first-class. The catalogue carries 25 RU categories plus 18 EN-specific signatures, and the marketing set is EN-led. Most skills support both languages; the RU-only ones are language-specific by nature — prose-edit for Russian fiction, essay-write for Russian non-fiction structure, pelevin-digression.

**Q: How do I add my own rules?**

Two paths: (a) local override of `references/*.md` files (survives until `--update`), (b) PR to the repo. Both documented in `CONTRIBUTING.md`. For domain-specific banned terms, the local-override path is the right answer. For widely-applicable patterns, send a PR.

**Q: Can I run this without Claude Code?**

The linter, yes. `python3 skills/writer/scripts/lint.py file.md` works standalone. The wrappers require Claude Code (they're LLM-driven by design). Docker image (`ghcr.io/mikefluff/skills`) exposes the linter for CI without any Python install.

**Q: Why MIT?**

Because anti-AI-slop tooling should not have a gatekeeper. Fork it, embed it, monetize it — don't care. Just keep the repo link in the README so people can find the upstream.
