# Hacker News

**Title** (Show HN):

```
Show HN: Mikefluff/skills – 17 Claude Code skills for editing prose without LLM-tells
```

**URL**:

```
https://github.com/Mikefluff/skills
```

**Body** (first comment from submitter):

```
Hi HN — I've been writing with LLMs for the last couple of years and noticed everyone's output started to converge on the same handful of tells: "It's important to note that...", "delve into the rich tapestry of...", "in today's fast-paced world...", "we're excited to announce...", balance hedges, intensifier ladders, em-dash overuse.

This is 17 Claude Code skills built around an offline Python regex linter that catches 28 categories of those tells. EN + RU, ~50ms on a 5K-word file. The latest set adds marketing-specific patterns (revolutionary / world-class / industry-leading / click here / learn more / save time / boost productivity / we're excited to announce) since those bypass the older "prose" rules and land hardest on landing pages and release notes.

The base linter is standalone and useful on its own (run via Docker or curl-pipe). Twelve wrappers compose on top — viral-text, prose-edit (fiction), essay-write (non-fic), tone-shifter (register changes), pelevin-digression, cold-email (5-block / ≤120 words), landing-copy (Julian Shapiro hero formula + char-limits per platform), release-notes (Keep-a-Changelog), rfc-writer (RFCs / ADRs / Tech Specs with RFC 2119), microcopy, image-prompt (MJ/DALL-E/Flux), video-prompt (Kling/Veo/Sora). Three read-only linters — style-check (pre-commit), translation-sync (RU↔EN↔PT-BR parity), canon-check (story-bible consistency).

Linter has severity tags (blocker/caution/nit) and is code-fence-aware (skips ```fenced``` blocks so it doesn't false-positive on code examples).

MIT. No external deps. CI/CD with conventional commits → auto-release. Skills compose by chaining (see docs/COMPOSING.md for 14 recipes).

The interesting bit (to me): every skill has a sharp `description:` field that Claude Code matches against user requests. Overlapping descriptions hurt discovery, so the boundary between skills is intentional, not aesthetic. There's also a `skills.json` manifest with tags (`fiction`, `marketing`, `outreach`, `tech-docs`, `ux-copy`, `visual`, …) and an auto-generated skill index by tag + language.

Happy to answer questions on the linter design, the regex categories, the skill-discovery contract, or how the wrappers compose.

Repo: https://github.com/Mikefluff/skills
```
