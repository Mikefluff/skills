# X / Twitter

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

All tweets ≤280 chars. To re-verify after editing:

```bash
python3 scripts/check-tweet-length.py
```

## Single tweet

```
Open-sourced 41 Claude Code skills for writing and AI media.

Base is an offline regex linter over 25 categories of LLM-prose tells, RU + EN, no deps. On top: prompt skills for image/video/music and orchestrators that chain them.

MIT.

github.com/Mikefluff/skills
```

## Thread (10 tweets)

```
1/ Open-sourced 41 Claude Code skills for writing and AI media generation.

1 base linter, 21 wrappers, 3 read-only linters, 13 orchestrators, 3 meta. MIT, no required deps.

github.com/Mikefluff/skills

Thread on the two design calls I'd defend.
```

```
2/ The base is `writer` — pure Python regex over 25 catalogued categories of LLM-prose tells.

"it's important to note", "delve into the rich tapestry", the balance paragraph that commits to nothing, intensifier ladders.

RU and EN. ~80ms on a 4K-word file.
```

```
3/ Design call one: copy-paste artifacts get their own class.

:contentReference[oaicite:0]
turn0search3
utm_source=chatgpt.com
[cite: 8]
</think>

No editor produces these. They reach a text one way. So one hit is the verdict — no cluster required.
```

```
4/ Everything else in the catalogue is probabilistic and only means something in clusters.

One "however" is nothing. "However" + a rule of three + a Conclusion section is a confession.

Treating those two classes the same is how detectors get things wrong.
```

```
5/ Design call two: density and gate are separate outputs.

Density: does this read like a model wrote it?
Gate: does this break a house rule?

I had them mixed. A doc with 48 ordinary em-dashes and one real slop marker scored as machine-written.

Typography isn't evidence.
```

```
6/ Prose wrappers compose on the linter:

— viral-text: hooks, numbered points, CTA
— prose-edit: fiction, voice vectors
— essay-write: non-fiction longread
— tone-shifter: register shifts
— cold-email: 5 blocks, 120 words
— microcopy, landing-copy, release-notes, rfc-writer
```

```
7/ Other half is AI media.

Prompt skills for 14 image models, 20 video, 10 music. Then an optional --execute layer that calls the vendor API and saves real files.

32 providers behind one interface, with cost confirmation before anything bills.
```

```
8/ 13 orchestrators chain the halves.

Research a topic with citations → 8-slide carousel with one visual style → or a vertical reel with matched music, ffmpeg-stitched.

proposal-maker turns a raw price list into an HTML proposal styled from the client's own site.
```

```
9/ Install:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

Also npm, Homebrew, Docker:

npm i -g @mikefluff/skills
brew install mikefluff/tap/skills
docker pull ghcr.io/mikefluff/skills
```

```
10/ Code: github.com/Mikefluff/skills
Guide: /blob/main/docs/USER-GUIDE.md

If your LLM-assisted drafts have started sounding like everyone else's, run the linter over the last one. Takes a second, and the output is specific enough to argue with.
```

## Notes before posting

- Tweet 3 quotes real artifact strings. That is the point — a reader can search their own drafts for them immediately.
- Tweets 3 and 5 carry the thread. If it needs shortening, cut 6 and 7 before those.
- Do not claim the linter detects AI authorship. It detects patterns.
