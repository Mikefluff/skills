# Reddit

Suitable subreddits: r/ClaudeAI, r/MachineLearning, r/programming, r/copywriting (for landing-copy + release-notes wrappers).

**Title** (r/ClaudeAI, r/programming):

```
I built 17 Claude Code skills to make LLM-assisted writing stop sounding like LLM output
```

**Body**:

```
I've been writing with LLMs and got tired of every output reading the same way — "It's important to note that...", "delve into...", "in today's fast-paced world...", "we're excited to announce...", balance hedges everywhere.

So I built a collection of skills around an offline Python regex linter. The linter catches 28 categories of AI-prose tells in 50ms on a 5K-word file. No LLM call required for the linter — it's pure regex (writer/scripts/lint.py).

Twelve wrappers compose on top:
- viral, fiction (prose-edit), non-fiction (essay-write)
- register shifts (tone-shifter)
- voice digressions (pelevin-digression)
- cold email (5-block / ≤120 words)
- landing copy (Julian Shapiro hero formula + char-limits per platform)
- release notes (Keep-a-Changelog, per-audience tone)
- RFCs / ADRs / Tech Specs (RFC 2119 keywords)
- microcopy (errors, empty states, buttons, 404s)
- image / video prompts (MJ, DALL-E, Flux, Kling, Veo, Sora, Runway)

Three read-only linters: pre-commit gate, multilingual translation parity (RU/EN/PT-BR), story-bible consistency for fiction.

Install:
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

Or Docker:
docker pull ghcr.io/mikefluff/skills

MIT. Open to feedback / contributions.

Repo: github.com/Mikefluff/skills
Docs: github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md
Skill index by tag: github.com/Mikefluff/skills/blob/main/docs/SKILL-INDEX.md
```

---

**Variant for r/copywriting** (focus on marketing-copy skills):

**Title**:

```
Open-sourced a collection of writing tools that strip the "AI-generated" feel from copy
```

**Body**:

```
17 Claude Code skills + an offline regex linter that catches the patterns that mark copy as LLM-generated.

The linter catches 28 categories — including the marketing-specific set: revolutionary, world-class, game-changing, industry-leading, cutting-edge, "click here", "learn more", "get started" (alone), "we're excited to announce", "save time", "boost productivity", "will support" (future-tense for shipped features). EN + RU.

Wrappers most relevant to copywriters:
- landing-copy — hero (Julian Shapiro 5-step formula + 5 alternatives), features, pricing, FAQ, SEO meta (title + description + Open Graph + Twitter), ad copy (Google RSA / Facebook / LinkedIn / X / Reddit / TikTok with exact char limits per platform)
- release-notes — Keep-a-Changelog format with per-audience tone (end-user / dev / ops)
- microcopy — error messages, empty states, tooltips, buttons, modals, 404/500 pages, onboarding (≤8 words for buttons, never blames user)
- cold-email — 5-block structure, ≤120-word budget, banned ceremony patterns
- viral-text — hooks + numbered points + NLP question + CTA, EN viral patterns

Each wrapper has a `references/banned-patterns.md` with the domain-specific anti-patterns, plus a `before-after.md` calibration file showing the transformation.

MIT license. Free.

GitHub: github.com/Mikefluff/skills
```
