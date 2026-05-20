# Launch posts

Per-platform copy-paste drafts (refreshed for v1.9 — 17 skills, 28 linter categories, all current wrappers).

Pick the file that matches the audience; edit before posting if needed. All drafts pass `writer/scripts/lint.py --scan-code-blocks` cleanly except for the deliberate examples that quote banned patterns.

## Drafts

| Platform | File | Length |
| --- | --- | --- |
| X / Twitter — single tweet | [`launch-posts/x-thread.md`](launch-posts/x-thread.md) | 279 chars |
| X / Twitter — 9-tweet thread | [`launch-posts/x-thread.md`](launch-posts/x-thread.md) | thread |
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

For pre-commit / CI gating, regex wins: 50ms vs 5-10s, no API cost, deterministic, no LLM dependence. For nuanced rewriting, the wrappers DO use the LLM (via Claude Code) — that's where context matters. The linter is the floor; the wrappers are the ceiling.

**Q: Why so many skills instead of one big one?**

Discovery. Claude Code matches user requests against the `description:` field. A single mega-skill would match too broadly and hurt precision. Splitting lets each skill have a sharp discriminator. The boundary is intentional, not aesthetic. See `docs/COMPOSING.md` for 14 named recipes showing how the 17 skills chain into workflows.

**Q: Russian-first sounds limiting. What about English?**

EN coverage is now first-class — all 28 linter categories have EN patterns (the marketing-specific set added in v1.8 is EN-led). On synthetic EN neuroslop, the linter fires 54 hits across 18 categories. 14 of 17 skills support both languages. The 3 RU-only skills are author-/language-specific (prose-edit for Russian fiction, essay-write for Russian non-fiction structure, pelevin-digression).

**Q: How do I add my own rules?**

Two paths: (a) local override of `references/*.md` files (survives until `--update`), (b) PR to the repo. Both documented in `CONTRIBUTING.md`. For domain-specific banned terms, the local-override path is the right answer. For widely-applicable patterns, send a PR.

**Q: Can I run this without Claude Code?**

The linter, yes. `python3 writer/scripts/lint.py file.md` works standalone. The wrappers require Claude Code (they're LLM-driven by design). Docker image (`ghcr.io/mikefluff/skills`) exposes the linter for CI without any Python install.

**Q: Why MIT?**

Because anti-AI-slop tooling should not have a gatekeeper. Fork it, embed it, monetize it — don't care. Just keep the repo link in the README so people can find the upstream.
