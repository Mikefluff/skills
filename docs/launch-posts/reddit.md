# Reddit

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

Suitable subreddits: r/ClaudeAI, r/LocalLLaMA, r/programming, r/copywriting (for the landing-copy and release-notes wrappers).

**Title** (r/ClaudeAI, r/programming):

```
I open-sourced 44 Claude Code skills, built around an offline linter for LLM-prose tells
```

**Body**:

```
I write a lot with LLMs and got tired of every draft reading the same way — "it's important to note that", "delve into", "we're excited to announce", the balance paragraph that argues both sides and lands nowhere.

So the base of this is `writer`: a pure-Python regex linter over 25 catalogued categories of those tells, RU and EN. No LLM call, no dependencies, ~80ms on a 4K-word file in-process. Every prose skill in the collection runs it as a final pass, and it works standalone.

Two parts of it I'd defend over the word lists.

**Copy-paste artifacts are a separate class.** Markers that reach a text only by copying out of a chat UI: `:contentReference[oaicite:0]`, `turn0search3`, `utm_source=chatgpt.com`, Gemini's `[cite: 8]`, a leftover `</think>`. No editor and no CMS produces those, so they need no corroborating signal — one hit settles it. Everything else in the catalogue is probabilistic and only means something in clusters. One "however" is nothing; "however" plus a rule of three plus a Conclusion section is a confession.

**Density and gate are separate outputs.** Density asks "does this read like a model wrote it". The gate is pass/fail on house rules. I had them mixed at first and a Russian document with forty-eight ordinary em-dashes and one real slop marker came out as machine-written — a typography preference wearing the costume of evidence.

The other half of the collection is AI media. Prompt skills for image, video and music (14, 20 and 10 model families), plus an optional `--execute` layer that calls the vendor API and saves real files — 32 providers behind one interface, with cost confirmation before anything bills. Then 13 orchestrators chain the halves: research a topic with citations, turn it into an eight-slide carousel with one consistent visual style, or into a vertical reel with matched music and ffmpeg stitching.

Structure: 1 base + 21 wrappers + 3 read-only linters + 13 orchestrators + 3 meta.

Install:
curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

Or Docker:
docker pull ghcr.io/mikefluff/skills

MIT. Open to feedback and contributions — especially on the linter categories, which are where the arguments are.

Repo: github.com/Mikefluff/skills
Docs: github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md
Skill index: github.com/Mikefluff/skills/blob/main/docs/SKILL-INDEX.md
```

---

**Variant for r/copywriting** (focus on the marketing-copy skills):

**Title**:

```
Open-sourced a set of writing tools that strip the "AI-generated" feel from copy
```

**Body**:

```
44 Claude Code skills built on an offline regex linter that catches the patterns marking copy as LLM-generated. No API call for the linter — it is pure regex and runs in under a tenth of a second.

25 catalogued categories, including the marketing-specific set: revolutionary, world-class, game-changing, industry-leading, cutting-edge, "click here", "learn more", bare "get started", "we're excited to announce", "save time", "boost productivity", and future tense for already-shipped features. English and Russian.

Wrappers most relevant here:

- landing-copy — hero (Julian Shapiro's formula plus alternatives), features, pricing, FAQ, SEO meta including Open Graph and Twitter cards, ad copy for Google RSA / Facebook / LinkedIn / X with exact character limits per platform
- release-notes — Keep-a-Changelog format with per-audience tone (end-user / dev / ops)
- microcopy — errors, empty states, tooltips, buttons, modals, 404 and 500 pages, onboarding. Buttons capped at 8 words, and the copy never blames the user
- cold-email — five blocks, a 120-word budget, banned ceremony patterns
- viral-text — hooks, numbered points, closing question, CTA

One rule worth stealing even if you never install this: **delete the water, not the function.** A cleaning pass will happily remove your CTA, your offer, your deadline and your price along with the filler, and the result scores beautifully on every slop metric while no longer doing its job. Those elements get rewritten, never deleted.

Each wrapper ships a `references/banned-patterns.md` for its domain and a `before-after.md` calibration file showing real transformations.

MIT. Free.

GitHub: github.com/Mikefluff/skills
```

## Notes before posting

- r/ClaudeAI and r/programming tolerate self-promotion when the post carries a technical argument. The two design points are that argument; the feature list alone reads as an ad.
- The r/copywriting variant leads with a rule the reader can use immediately, which survives even if they never install anything.
- Do not cross-post the same body. Reddit surfaces duplicates and the reception drops.
