# LinkedIn — long post

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

```
I open-sourced Mikefluff/skills — 41 Claude Code skills for writing and AI media generation.

The problem it started from: LLMs make writing faster, and the output converges. Everyone's drafts pick up the same tells — "it's important to note that", "we're excited to announce", the balance paragraph that argues both sides and commits to neither. Readers who have seen a thousand of those recognize the shape and discount the whole text.

What's in it:

→ writer — an offline regex linter over 25 catalogued categories of AI-prose tells, Russian and English. Pure Python, no dependencies, ~80ms on a 4K-word file. Every prose skill runs it as a final pass. It also catches copy-paste artifacts from chat UIs — the turn0search3 and utm_source=chatgpt.com markers that no editor produces, where a single hit is conclusive rather than suggestive.

→ 21 wrappers on top. Prose: viral-text, prose-edit for fiction, essay-write for non-fiction, tone-shifter for register changes. Product: landing-copy with per-platform character limits, release-notes in Keep-a-Changelog format, rfc-writer with RFC 2119 keywords, microcopy for error states and empty states. Outreach: cold-email, five blocks and a 120-word budget.

→ Prompt skills for AI media — 14 image models, 20 video, 10 music — with an optional execute layer that calls the vendor API and saves real files. 32 providers behind one interface, with cost confirmation before anything bills.

→ 13 orchestrators that chain the halves. Research a topic with citations, turn it into an eight-slide carousel with a consistent visual style, or into a vertical reel with matched music and ffmpeg stitching. proposal-maker turns a raw price list into an HTML commercial proposal styled from the client's own website.

→ 3 read-only linters that report and never edit: style-check as a pre-commit gate, translation-sync for RU/EN/PT-BR book parity, canon-check for story-bible consistency.

One design note I would defend anywhere: the linter reports two independent things. Density answers "does this read like a model wrote it". A separate gate answers "does this break a house rule". I had them mixed at first, and a document with forty-eight ordinary em-dashes and one real slop marker scored as machine-written — a typography preference wearing the costume of evidence. They have been separate ever since.

Install takes five seconds:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

Or pull the image for CI:

docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work

MIT. No required dependencies. Russian-first, English throughout.

github.com/Mikefluff/skills

If your LLM-assisted drafts have started to sound like everyone else's, run the offline linter over your last one. It takes a second and the result is specific enough to argue with.
```

## Notes before posting

- LinkedIn truncates around 200 characters before "see more". The first two lines carry the click.
- First person singular throughout. This is one author's project, and "we" on a solo repository reads as posturing.
- No hashtag block. It signals broadcast, and this audience is technical enough to find the post without it.
