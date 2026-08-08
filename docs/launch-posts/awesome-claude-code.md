# awesome-claude-code submission

<!-- lint-role: catalogue -->
<!-- Launch copy quotes the patterns it describes, so linting it for slop measures the examples. -->

Target: <https://github.com/hesreallyhim/awesome-claude-code>

> [!IMPORTANT]
> **Submissions go through the issue form, not a PR.** The repo's CONTRIBUTING.md
> says: "Do not open a PR. Just fill out the form." Submitting via PR — or via
> `gh` CLI — risks a temporary or permanent ban. Recommendations must be created
> by a human via the web UI.

## How to submit

1. Open the issue form: <https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml>
2. Fill in the fields below.
3. Submit. A bot will validate the entry; if anything needs adjustment, follow the bot's comments.
4. After maintainer review, the bot opens a PR automatically and merges it.

## Form fields

| Field | Value |
| --- | --- |
| Display Name | `Mikefluff/skills` |
| Primary Link | `https://github.com/Mikefluff/skills` |
| Secondary Link (optional) | `https://github.com/Mikefluff/skills/blob/main/docs/USER-GUIDE.md` |
| Category | `Agent Skills` |
| Sub-Category | `General` |
| Author Name | `Mikefluff` |
| Author Link | `https://github.com/Mikefluff` |
| License | `MIT` |

## Description (copy-paste)

```
44 Claude Code skills for writing and AI media generation. The base is an offline Python regex linter over 25 catalogued categories of LLM-prose tells (RU + EN) with severity tags, code-fence-aware scanning, and a separate class for chatbot copy-paste artifacts (oaicite, turn-markers, utm_source=chatgpt.com) where a single hit is conclusive. 21 wrappers compose on it: viral-text, prose-edit (fiction), essay-write, tone-shifter, cold-email, landing-copy, release-notes, rfc-writer, microcopy, plus prompt skills for 14 image / 20 video / 10 music model families with an optional execute layer across 32 providers. 13 orchestrators chain them end to end — research to carousel, research to vertical reel, price list to branded HTML proposal. 3 read-only linters: style-check (pre-commit gate), translation-sync (RU/EN/PT-BR parity), canon-check (story-bible consistency). Install via curl, npm (`@mikefluff/skills`), Homebrew (`mikefluff/tap/skills`), or Docker (`ghcr.io/mikefluff/skills`).
```

## What the bot validates

Per the repo's CONTRIBUTING.md, the automation checks:

- All required fields are filled
- URLs are valid and accessible
- No duplicate resources exist
- License information (when available)
- Description length and quality

If something fails, the bot leaves a comment with the fix. Edit your submission and the bot revalidates.

## After submission

Watch the issue for bot feedback. After maintainer approval, the bot creates and merges the PR automatically — you don't need to do anything manual on the PR.

Once merged, the new entry is live at <https://github.com/hesreallyhim/awesome-claude-code> in the Agent Skills section.

## Why this isn't an automated step

Two of the repo's hard rules block automation here:

1. "Resource recommendations must be created by human beings."
2. "It is not possible to submit a resource recommendation using the `gh` CLI."

Combined with the explicit warning against PR submissions, the path is a manual web-UI issue form. The text above is everything needed — paste-ready.
