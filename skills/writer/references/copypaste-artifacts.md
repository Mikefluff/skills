# Class A — chatbot copy-paste artifacts

Service markers that reach a text only one way: someone copied out of a chat UI and pasted in. No editor, no autocorrect, no CMS produces them.

That makes them categorically different from every other signal in this skill. Soft markers («ключевой», a rule of three, a balance paragraph) are probabilistic — they need a cluster before they mean anything. A class A artifact needs nothing. **One hit is the verdict.**

The linter reports them as `COPYPASTE_ARTIFACT` with `blocker` severity, which fails the gate regardless of how clean the prose reads otherwise.

---

## The registry

| Source | Marker |
|---|---|
| ChatGPT footnotes | `:contentReference[oaicite:N]{index=N}`, `oai_citation:N‡`, bare `oaicite:N` |
| ChatGPT web search | `turn0search3`, `turn1news2`, `turn0file0`, `citeturn…` |
| ChatGPT / Copilot links | `utm_source=chatgpt.com`, `utm_source=copilot.com` |
| Grok | `referrer=grok.com`, `grok_card://`, `grok_render_citation_card_json`, `<grok-card …>` |
| Gemini | `vertexaisearch…/grounding-api-redirect/…`, `[cite_start]`, `[cite: 8]`, `[span_12]` |
| Internal footnotes | `【12†source】`, `](sandbox:/mnt/data/…)` |
| Reasoning leftovers | `<think>`, `</think>` |
| Perplexity | `ppl-ai-file-upload` |
| Unfilled placeholders | `INSERT_SOURCE_URL`, `PASTE_X_URL_HERE`, `URL_HERE`, `20XX-XX-XX` |
| Private-use-area glyphs | `U+E200`–`U+E2FF` range markers |

---

## Two deliberate exemptions

**Backticked spans do not count.** Quoting an artifact in documentation — as this very file does throughout — is a citation, not a paste. The linter blanks inline code and fenced blocks before the class A pass. If you need to discuss `turn0search0` in prose, put it in backticks.

**URLs are scanned, not stripped.** This is the one pass where URLs must survive, because `utm_source=chatgpt.com` lives inside them. Every other pass strips URLs first.

---

## Class B — zero-width characters

`U+200B` (zero-width space), `U+200C`, `U+200D` (ZWJ), `U+2060`, `U+FEFF`.

Reported as `ZERO_WIDTH` at `caution`, not blocker. Newsletters, CMSs and copy-paste through rich-text editors inject these too, so they warrant a look at the source rather than an automatic verdict.

One exception is coded in: ZWJ inside an emoji sequence (👨‍👩‍👧) is legitimate and does not fire. Only a bare zero-width character outside emoji does.

---

## Treatment

Always the same: delete the artifact entirely.

If it stood where a citation belonged, restore the real source or drop the claim. A paste marker where a source should be usually means the claim was never verified — deleting the marker while keeping the claim launders an unverified statement into a confident one.

---

Registry ported from [smixs/humanizer-ru](https://github.com/smixs/humanizer-ru) (MIT), which credits [Vladimir-Human/humanizer-ru](https://github.com/Vladimir-Human/humanizer-ru) and [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (both MIT).
