---
name: skills-styles
description: "Manage the local style library — bundled (24 carousel + 12 video director + 12 music genre) plus user overrides at ~/.claude/style-library/. CRUD + submit (upstream-PR packages) + schema validation. Use when: 'add a custom carousel style', 'create a directorial style', 'genre preset for k-pop', 'list available styles', 'submit my style upstream'."

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
Provide a thin CLI on top of `~/.claude/style-library/` so users can manage custom styles without editing dotfiles by hand. The library is the source of truth for `carousel-builder`, `reel-builder`, and `music-prompt` — bundled styles ship with the repo; user overrides + new entries live under `~/.claude/style-library/<modality>/<id>.md` and take priority when the loader resolves a style id.

This skill does NOT:
- Modify bundled styles (under `<repo>/common/style-library/`) — only user overrides.
- Run the auto-PR creation flow end-to-end (no `gh pr create`). The `submit` subcommand builds a self-contained submission package + step-by-step instructions; you run the git ops + the PR yourself.
- Generate the style content for you. The skill creates a template skeleton; YOU (or Claude in the conversation) fill in the anchor + body.
- Manage API keys (that's `skills-keys`) or skill updates (that's `skills-update`).
</objective>

## ROLE

Read the user's intent (list / show / add / edit / remove / validate / diff / path / submit) → call the matching `common/runners/cli/styles.py` subcommand → relay the result. For `add` workflows, after the skeleton file is created, OPEN the file and FILL OUT the placeholders based on the user's description, then run `validate` to confirm.

## PIPELINE

1. **Parse intent**: which subcommand + modality (carousel|video|music) + style id.
2. **Run** `python3 scripts/run.py <subcommand> [args]`.
3. **For add workflows**: after the skeleton is created, READ the new file, FILL the placeholders (frontmatter + body anchors) using the user's description, then run `validate` to confirm.
4. **Relay the output** — masked / structured by the CLI.
5. **Suggest next step**: edit / validate / submit as appropriate.

## MODES

### Inspection

- `skills-styles list [modality]` — show all styles with status (bundled / user-only / override)
- `skills-styles list [modality] --user-only` — only user-overrides
- `skills-styles list [modality] --bundled-only` — only bundled
- `skills-styles show <modality> <id>` — print the resolved file (user wins over bundled)
- `skills-styles path [modality] [id]` — print resolved path

### Creation + edit

- `skills-styles add <modality> <id>` — create a new user style from the bundled template
- `skills-styles add <modality> <id> --from <existing-id>` — start as a copy of an existing style
- `skills-styles add <modality> <id> --force` — overwrite if it already exists
- `skills-styles edit <modality> <id>` — open the user-override in `$EDITOR`
- `skills-styles remove <modality> <id> --force` — delete the user-override (reverts to bundled if any)

### Validation

- `skills-styles validate <modality> <id>` — frontmatter + body schema check per modality
- `skills-styles diff <modality> <id>` — diff user-override vs bundled (useful when customizing a bundled style)

### Upstream PR

- `skills-styles submit <modality> <id>` — validate, then build `./style-submission-<ts>-<modality>-<id>/` with the file at the correct repo path + a PR description template + a step-by-step instructions README. You do the git ops + `gh pr create` manually.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/usage.md](references/usage.md) | Detailed UX for each subcommand — exit codes, edge cases, examples |
| [references/templates.md](references/templates.md) | Per-modality frontmatter schema + required body fields + validation rules + conventions reviewers enforce on PRs |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 4 example sessions: create a carousel style from scratch via template, create a video style as a copy of `fincher-cold-lowkey`, validate + submit a music genre to upstream, customize a bundled style (override → edit → diff → submit).

## CONSTRAINTS

- **Bundled styles are read-only.** This skill operates ONLY on `~/.claude/style-library/`. To modify a bundled style, use `add --from <id>` to copy it, then edit the user override.

- **User wins on resolution.** When both a bundled `<id>.md` and a user `<id>.md` exist, the loader picks user. `skills-styles list` shows the `override` status so you know.

- **Add doesn't auto-fill the content.** It creates a skeleton with `<placeholders>`. After `add`, YOU (or Claude in the chat) fill the file based on user intent, then run `validate`.

- **Validation is strict on schema, soft on content.** It checks frontmatter shape + required body fields + anchor length. It does NOT enforce style guidelines (no copyrighted artist names, no real-brand mimicry, no clichés) — those are reviewer checks during PR. The skill prints reviewer-checklist reminders in the submission package.

- **Submit doesn't run git.** v1 prepares a submission package + prints exact instructions. Users do `git clone fork → cp → commit → push → gh pr create` themselves. Auto-PR is intentionally deferred — fork detection + multi-step gh interaction is brittle.

- **Submit validates first.** If the style has schema issues, submit refuses unless `--force` is passed. Don't submit broken styles upstream.

- **No copyrighted living-artist names in anchor text.** The `video/_template.md` warning + the PR checklist enforce this. Bundled video styles store the director's name in `display:` and `Inspired by:` ONLY — those fields are user-facing, not model-facing.

- **No real-brand mimicry in anchor text.** "Apple's WWDC look" / "Stripe's hero" are banned. Use era + cultural movement instead ("developer-platform brand aesthetic of the 2022-2025 era").

- **No emoji.** Anywhere in any style file. Reviewer rejects.

- **id must be kebab-case** (`^[a-z][a-z0-9-]{1,40}$`). The validator enforces.

- **Style anchor minimum 40 chars.** The validator enforces. Shorter anchors lose to the per-slide content prompt.

- **Use the bundled templates** (`common/style-library/<modality>/_template.md`) as the schema reference. They contain inline conventions + the validator targets exactly that shape.

- **For Claude to fill content**: after `add`, read the new file at the path printed by stdout, edit each `<placeholder>` based on the user's description, then run `validate` to confirm the result is parseable. Don't skip the validate step.

## INVOCATION HINTS

When the user says any of:

- "add a custom style for X", "create a carousel style called Y"
- "make a video style inspired by [director]", "build a music genre preset"
- "list available styles", "show what's in [style-id]"
- "edit the [style-id] style", "tweak the [style-id]"
- "remove my [style-id] style"
- "validate my style", "check if [style-id] is valid"
- "submit my style upstream", "send [style-id] to the repo", "PR my carousel style"
- "diff my override against bundled"

RU triggers:
- «добавь свой стиль для X», «создай carousel стиль <name>»
- «сделай директорский стиль в духе X», «сделай music-пресет жанра Y»
- «покажи доступные стили», «что внутри [style-id]»
- «отредактируй стиль [style-id]», «правка [style-id]»
- «удали мой стиль [style-id]»
- «провалидируй стиль», «проверь корректность [style-id]»
- «отправь стиль наверх / в апстрим», «PR мой carousel стиль»
- «дифф моего override и bundled»

Defaults when intent is ambiguous: `list` (safe — read-only, shows what's available).

This is a meta-skill, sibling to `skills-keys` and `skills-update`. All three wrap `common/runners/cli/...` plumbing. Their outputs are tool outputs to be relayed honestly — don't paraphrase the validation results, just show them.

When the user creates a new style and gives a brief description, the recommended flow is:

1. `skills-styles add <modality> <id>` — create skeleton
2. Read the newly created file
3. Fill the frontmatter + body anchors based on the user's description
4. `skills-styles validate <modality> <id>` — confirm schema
5. Optionally: `skills-styles submit <modality> <id>` — prepare PR package

For modifying a bundled style:

1. `skills-styles add <modality> <id> --from <id>` — copy bundled as starting point
2. Edit the user-override file (the file the user is allowed to change)
3. `skills-styles diff <modality> <id>` — review what changed
4. `skills-styles validate <modality> <id>`
5. Optionally submit upstream
