# LinkedIn — long post

```
We just open-sourced Mikefluff/skills — a collection of 17 Claude Code skills for editing prose, marketing copy, release notes, RFCs, cold outreach, and AI image/video prompts without the LLM-tells.

What's in the box:

→ writer — a pure-Python regex linter that catches 28 categories of AI-prose tells (EN + RU). Patterns like "It's important to note that...", "delve into the rich tapestry of...", intensifier ladders ("truly remarkable", "deeply important"), balance hedges, comma-splices, em-dash abuse — plus the new marketing-specific set: revolutionary / game-changing / industry-leading / we're excited to announce / click here / learn more / save time. Runs offline in ~50ms.

→ Twelve wrappers that compose on the linter. Prose: viral-text, prose-edit (fiction), essay-write (non-fic), pelevin-digression, tone-shifter (register changes). Product: landing-copy (hero + features + pricing + SEO + ads, with platform char-limits), release-notes (Keep-a-Changelog format, per-audience tone), rfc-writer (RFCs/ADRs/Tech Specs with RFC 2119), microcopy (error states, empty states, buttons, 404s). Outreach: cold-email (5-block / ≤120 words). Visual: image-prompt (MJ/DALL-E/Flux), video-prompt (Kling/Veo/Sora/Runway).

→ Three read-only linters: style-check (pre-commit prose gate), translation-sync (multilingual parity for RU/EN/PT-BR books), canon-check (story-bible consistency for fiction).

Why we built it:

LLMs make writing easier but the output reads identical across users. The collection encodes the specific patterns that make LLM prose recognizable, then strips them. The base linter is high-recall by design — it'll false-positive on legitimate prose sometimes, accepted as the cost of catching what matters at scale.

Five-second install:

curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash

Or pull the Docker image for CI integration:

docker run --rm -v "$PWD:/work" ghcr.io/mikefluff/skills lint /work

MIT license. No external deps. Works inside Claude Code via skill discovery (each skill has a sharp `description:` field that Claude matches against user requests).

GitHub: github.com/Mikefluff/skills

If you've shipped enough LLM-assisted writing that your output is starting to sound like Claude — try the offline linter on your last draft. Best signal-to-noise gain for the time invested this year.
```
