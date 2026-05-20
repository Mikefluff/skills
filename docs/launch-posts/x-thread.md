# X / Twitter

All tweets ≤280 chars (verified). To re-verify after edits:

```bash
python3 -c "import re,sys; [print(f'{len(b)} chars: '+b[:60]+'…') for b in re.findall(r'^\`\`\`\n(.*?)\n^\`\`\`', open('docs/launch-posts/x-thread.md').read(), re.MULTILINE|re.DOTALL)]"
```

## Single tweet (≤280 chars)

```
Open-sourced 17 Claude Code skills for editing prose without LLM-tells.

Offline regex linter catches 28 categories of AI-prose patterns (EN + RU). Wrappers for landing copy, release notes, RFCs, cold email, image/video prompts.

MIT.

github.com/Mikefluff/skills
```

## Thread (10 tweets)

```
1/ Open-sourced 17 Claude Code skills for editing prose without LLM-tells.

One base regex linter, 12 wrappers, 3 read-only linters, 1 meta. MIT.

github.com/Mikefluff/skills

Thread.
```

```
2/ The base is `writer` — pure Python regex, ~50ms on a 5K-word file.

Catches 28 categories: "it's important to note", "delve into the rich tapestry", "in today's fast-paced world", "we're excited to announce", balance hedges, intensifier ladders.

EN + RU side-by-side.
```

```
3/ Linter v2 adds five marketing categories:

— MARKETING_HYPE: revolutionary, world-class
— EMPTY_CTA: click here, learn more
— WEAK_OPENER: we're excited to announce
— VAGUE_BENEFIT: save time, boost productivity
— WRONG_TENSE_RELEASE: will support (for shipped features)
```

```
4/ Plus severity tags (blocker / caution / nit) per hit and code-fence-aware scanning.

The linter no longer false-positives on words quoted inside ``` blocks. It does still catch them in actual prose.
```

```
5/ Prose wrappers (compose on `writer`):

— viral-text: hooks + numbered points + NLP question
— prose-edit: fiction (Pelevin / Manson voice vectors)
— essay-write: non-fic longread (Manson coda, V/H/P markers)
— tone-shifter: register shifts
— pelevin-digression: voice inserts
```

```
6/ Product / tech wrappers:

— landing-copy: hero (Julian Shapiro), features, pricing, SEO, ad copy
— release-notes: Keep-a-Changelog, per-audience tone
— rfc-writer: RFCs / ADRs / Tech Specs (RFC 2119)
— microcopy: errors, empty states, buttons
— cold-email: 5-block / ≤120 words
```

```
7/ Visual prompt wrappers:

— image-prompt: MJ / DALL-E / Flux (6-part formula: subject + setting + style + lighting + camera + texture, per-model deltas)

— video-prompt: Kling / Veo / Sora / Runway (CHARACTER FIRST law, beat structure, pacing modes)
```

```
8/ Three read-only linters (reports, never mutate):

— style-check: pre-commit prose gate
— translation-sync: RU↔EN↔PT-BR parity (typography, terminology, anchor-quote drift)
— canon-check: story-bible consistency for fiction
```

```
9/ One-curl install. Also via npm, Homebrew, Docker:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

npm install -g @mikefluff/skills
brew install mikefluff/tap/skills
docker pull ghcr.io/mikefluff/skills
```

```
10/ Code: github.com/Mikefluff/skills
Docs: github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md
Index: github.com/Mikefluff/skills/blob/main/docs/SKILL-INDEX.md

If your LLM-output is starting to sound like Claude — run the linter on your last draft. Highest leverage 30s.
```
