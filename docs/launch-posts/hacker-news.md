# Hacker News

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

**Title** (Show HN):

```
Show HN: 41 Claude Code skills for writing and AI media, with an offline slop linter
```

**URL**:

```
https://github.com/Mikefluff/skills
```

**Body** (first comment from submitter):

```
I write a lot with LLMs and got tired of every draft converging on the same handful of tells: "it's important to note that", "delve into the rich tapestry of", "we're excited to announce", the two-sided balance paragraph that commits to nothing, intensifier ladders, em-dash clusters.

So the base of this is `writer`: a pure-Python regex linter over 25 catalogued categories of those tells, RU and EN. No dependencies, ~80ms on a 4K-word file in-process, ~135ms through the CLI including Python startup. It runs standalone via Docker or curl-pipe, and every prose skill in the collection calls it as a final pass.

Two things in it I think are worth more than the word lists.

Copy-paste artifacts. Markers that reach a text only by copying out of a chat UI: `:contentReference[oaicite:0]`, `turn0search3`, `utm_source=chatgpt.com`, Gemini's `[cite: 8]`, a stray `</think>`. No editor produces those, so they need no corroborating signal — one hit settles it. Everything else in the catalogue is probabilistic and only means something in clusters.

The verdict and the gate are separate outputs. Density (clean / borderline / slop-suspected) answers "does this read like a model wrote it". The gate is pass/fail on house rules. I had them mixed at first, and a Russian document with forty-eight ordinary em-dashes and one actual slop marker came out as "slop suspected" — a typography choice masquerading as evidence of machine authorship. Keeping them apart fixed it.

The other half of the collection is AI media. Prompt skills for image, video and music (14, 20 and 10 model families), then an optional --execute layer that calls the vendor API and saves real files. 32 providers behind one interface. Orchestrators chain the two halves: research a topic with citations, turn it into an 8-slide carousel with a consistent visual style, or into a vertical reel with matched music and ffmpeg stitching.

Structure: 1 base + 21 wrappers + 3 read-only linters + 13 orchestrators + 3 meta. Skills are discovered by Claude Code through a `description:` field, so the boundary between them is a discovery contract rather than taste — overlapping descriptions make the wrong skill fire.

MIT. Releases are cut by hand; an auto-bump workflow used to do it and kept choosing the wrong major on additive commits, so I removed it.

Happy to talk about the linter design, why some categories are deliberately regex-free, or how the --execute layer handles cost confirmation.

Repo: https://github.com/Mikefluff/skills
```

## Notes before posting

- Show HN wants the submitter's first comment to explain what it is and what is interesting about it. The two design points (artifacts, verdict-vs-gate) carry that weight; the feature list alone will not.
- Expect pushback on regex-for-prose. The honest answer: the catalogue is high-recall by design, false positives are the accepted cost, and anything needing semantics is documented as deliberately uncovered in `docs/LINTER-COVERAGE.md`.
- Do not claim the linter detects AI authorship. It detects patterns. `style-check` has a detect mode with an explicit limit on what soft signals can prove.
