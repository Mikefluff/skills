---
name: style-suggest
description: "Visual style generator — turn a text description and/or reference image into a structured style entry for the prompt-library. Duplicate-detect then emit v2.15.0 schema (background, accents, mood, typography, composition_signature). Use when: 'make a new style', 'add a style based on this image', 'добавь стиль', 'предложи стиль'."

license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Visual-style generator. Input: a text description, optionally a reference image. Output: a structured `<slug>.md` style file conforming to the v2.15.0 schema in `common/visual-prompt-library/styles/_schema.md` — ready to drop into the library and immediately usable by every visual-output skill (carousel-builder / cover-maker / quote-card-maker / meme-card-maker / banner-maker / logo-maker) via the shared chain.

This skill does NOT:
- Add the new style file to disk without user confirmation (default behavior: print the proposed entry and ask)
- Edit existing styles (use a manual Edit on the `<slug>.md` file for that)
- Generate images using the new style (that's what the downstream visual skills do)
- Replace user vocabulary with generic synonyms — the user's terms are preserved verbatim wherever they're tight enough to use directly
</objective>

## ROLE

Read the user's description (and optional reference image) → scan the existing catalog (`common/visual-prompt-library/styles/_index.md` + each `<slug>.md` frontmatter) → decide DUPLICATE (similarity ≥ 0.72 to an existing style) or NEW → if NEW, draft a full v2.15.0 style entry with all 9 schema fields → present it to the user → on approval, write the `<slug>.md` file + add a row to `_index.md` + optionally add a row to `_auto-pick.md`.

## PIPELINE

1. **Read the catalog** — load `common/visual-prompt-library/styles/_index.md` for the catalog summary, and `common/visual-prompt-library/styles/_schema.md` for the required schema fields. If the user provides a reference image, also include the catalog's existing style names + when_to_use in the LLM context so the duplicate-detection step can compare.

2. **Compose the LLM call** — load [`references/system-prompt.md`](references/system-prompt.md) as `system` and assemble a user message:
   ```
   User description: "<verbatim user text>"
   [If image attached:]
   Reference image: <base64-encoded data: URI OR a local path that the model can read>
   Existing styles catalog (slug → when_to_use):
     <one line per style — pulled from the catalog>
   Slugs already taken (cannot re-use): <comma-separated list>

   Analyze: does this match an existing style (similarity ≥ 0.72) — if so, return {action: "duplicate", matchId, similarity, reasoning}. Otherwise return {action: "new", suggestion: {...}} with the full v2.15.0 schema fields.
   ```
   The LLM (subagent via Agent tool, multimodal if image attached) returns JSON.

3. **Validate the output**:
   - If `action == "duplicate"` — tell the user the existing style covers their request; suggest using `--style <slug>` directly. Optionally allow `--force-new` to override and create anyway.
   - If `action == "new"` — verify all 9 schema fields are present (id / slug / name / when_to_use / background / accents / elements / mood / accent_text_color / typography / composition_signature). Reject any with literal layout-label words (HEADLINE / BODY / etc.) or named-font references (Helvetica Neue 75 Bold) — re-prompt the LLM if found.

4. **Present the entry** — print the full proposed `<slug>.md` content (frontmatter + body) to stdout. Show the user:
   - The proposed file path: `common/visual-prompt-library/styles/<slug>.md`
   - The new row that will go into `_index.md`
   - Whether an `_auto-pick.md` row is suggested (only if the topic-signal mapping is clear)

5. **Save on confirmation** — when the user passes `--save` (or types yes to the prompt):
   - Write `common/visual-prompt-library/styles/<slug>.md` (refuse if file already exists; use `--force` to overwrite).
   - Append the new row to `_index.md` (alphabetical or thematic — preserve existing structure).
   - Optionally append a row to `_auto-pick.md` if the LLM suggested topic signals.
   - Echo the saved paths to stdout.

6. **Provide a usage hint** — print a one-liner showing how to invoke a downstream visual skill with the new style:
   ```
   ./scripts/run.py --style <slug>   # in any visual skill (carousel-builder / cover-maker / etc.)
   ```

## MODES

### Input

- `style-suggest --describe "<text>"` — text-only description
- `style-suggest --ref <image-path>` — reference image only
- `style-suggest --describe "<text>" --ref <image-path>` — both (most accurate)
- `--describe-file <path>` — multi-paragraph description from a file (when description is too long for shell arg)

### Output control

- `--save` — write the file + update `_index.md` without asking (default: ask first)
- `--force` — overwrite existing `<slug>.md` (default: refuse if file exists)
- `--force-new` — skip duplicate-detection, always create a new entry even if a similar style exists
- `--slug <kebab>` — explicit slug (default: derived from `name` field)
- `--print-only` — print the proposed entry, never save
- `--add-to-auto-pick` — also append a row to `_auto-pick.md` when the LLM suggests topic signals (default: include in print, ask before appending)

### Discovery

- `--list` — print the existing catalog (proxies `cat common/visual-prompt-library/styles/_index.md`)
- `--show <slug>` — print a specific existing style's entry (proxies `cat <slug>.md`)

### Model

- `--model anthropic|openai|gemini` — LLM provider for the analysis step. Default: `anthropic` (best at structured JSON output + multimodal image analysis when ref is provided).

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/system-prompt.md](references/system-prompt.md) | Step 2 — the SYSTEM_PROMPT for the LLM analysis step (verbatim) + user-message shape |
| [`../common/visual-prompt-library/styles/_schema.md`](../common/visual-prompt-library/styles/_schema.md) | Step 1, 3 — the required frontmatter fields for any new style file |
| [`../common/visual-prompt-library/styles/_index.md`](../common/visual-prompt-library/styles/_index.md) | Step 1 — the existing catalog (for duplicate detection + alphabetical placement) |
| [`../common/visual-prompt-library/styles/_auto-pick.md`](../common/visual-prompt-library/styles/_auto-pick.md) | Step 5 — auto-pick matrix (if the new style should auto-resolve on certain topic signals) |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: (1) text-only "nordic minimalism" generates a new entry; (2) reference image of a Wes Anderson film still generates a "wes-anderson" entry; (3) description "deep academia, leather and ivy" detected as duplicate of existing SCIENTIFIC / ACADEMIC (similarity 0.78) — points the user to use `--style scientific` instead.

## CONSTRAINTS

- **Always show before saving (unless `--save`).** This is a destructive-ish operation (creates files in the shared library). Default to dry-run + confirm. The cost of pausing is low; the cost of polluting the library is high.

- **Duplicate-detection threshold = 0.72.** Per figma's StyleSuggestAgent. If similarity is below this, treat as new. If above, point the user to the existing style (`--style <existing-slug>`) unless they pass `--force-new`.

- **Schema fields are MANDATORY for new entries.** All 9 fields (id / slug / name / when_to_use / background / accents / elements / mood / accent_text_color / typography / composition_signature) must be filled. Re-prompt the LLM if any is empty.

- **No forbidden literals in the entry body or frontmatter.** No layout labels (HEADLINE / BODY TEXT / CTA), no hex codes (#FF0000), no platform names (Instagram / 1080x1350), no named-font references (Helvetica Neue 75 Bold — describe by genre instead). Same forbidden-literal rules as the main SYSTEM_PROMPT in `common/visual-prompt-library/system-prompt.md`.

- **Slug is kebab-case, ≤24 chars.** Examples: `cyber-noir`, `art-deco`, `nordic-minimal`. Reject slugs with underscores / camelCase / spaces.

- **One reference image per request.** Multi-ref blending would require a different LLM treatment — out of scope for v1.

- **Image reference is read locally, never uploaded to a third party.** When `--ref <path>` is provided, the file is read into memory + base64-encoded + passed to the LLM via the Anthropic / OpenAI multimodal API. The user's anthropic / openai API key handles auth — no upload to other services.

- **Never commit `<slug>.md` to git automatically.** The skill writes the file; the user runs `git add` + commit explicitly. This avoids accidentally committing style entries before they've been reviewed.

- **Never print API keys.** Mask in errors.

- **Cost is small but non-zero.** One LLM call per request, no image generation. Typically <$0.02 per call. No cost-confirmation prompt needed at this level.

## INVOCATION HINTS

When the user says any of:

- "make a new style / add a new style based on X"
- "generate a style description from this image"
- "опиши стиль / сделай новый стиль / добавь стиль в библиотеку"
- "на основе этой картинки сделай стиль"
- "предложи стиль для X"
- "найди какой стиль подходит для X" (use `--list` + recommend)
- "is there already a style for X" (use duplicate-detection workflow)

If the user provides a screenshot of a website / poster / film still — they probably mean "extract a style from this image". Use `--ref <path>`.

If the user provides only text like "make a vaporwave-but-darker style" — use `--describe` and let the duplicate-detection step decide if it's a variant of an existing entry or a new one worth creating.

Defaults: `--model anthropic`. Without `--save`, prints the proposed entry and waits for confirmation. Suggests `_auto-pick.md` row only if topic signals are clear.

This skill is the WRITE side of the style library. The READ side (consume styles in downstream image-gen) lives in `common/visual-prompt-library/system-prompt.md` and is invoked by `carousel-builder` / `cover-maker` / etc.
