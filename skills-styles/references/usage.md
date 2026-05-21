# skills-styles — detailed usage reference

What each subcommand does, exit codes, edge cases.

---

## The library

Two roots:

| Root | Path | Modifiable by user? |
|---|---|---|
| Bundled | `<repo>/common/style-library/<modality>/<id>.md` | No (read-only from this skill) |
| User    | `~/.claude/style-library/<modality>/<id>.md`     | Yes |

Loader precedence: **user wins** — a user file shadows a bundled file with the same id.

Override location is fixed at `~/.claude/style-library/` by design. If you want a different path, fork the loader (`common/runners/styles.py:_USER_DIR`).

---

## `list`

```
skills-styles list [carousel|video|music] [--user-only|--bundled-only]
```

Shows ids with one-character status indicators:

| Symbol | Meaning |
|---|---|
| `·` | bundled (only in repo, no user override) |
| `+` | user-only (no bundled counterpart) |
| `*` | override (both exist, user wins) |

Example output:

```
# carousel  (26 style(s))

  ·  bundled    art-deco-gold                    Art Deco gold
  ·  bundled    bauhaus-primary                  Bauhaus primary
  +  user-only  retro-soviet-poster              Retro Soviet poster (custom)
  *  override   kinfolk-minimal                  Kinfolk minimal (warmer)
  ...
```

Without args: all three modalities. Exit: 0 always.

---

## `show`

```
skills-styles show <modality> <id>
```

Prints the file the loader resolves to (user override if present, else bundled). Header line includes the path + status.

Exit: 0 if found, 2 if not found.

---

## `path`

```
skills-styles path                       # both roots
skills-styles path <modality>            # both roots, scoped
skills-styles path <modality> <id>       # resolved file
```

Useful for scripts: `cat $(skills-styles path carousel kinfolk-minimal)`.

Exit: 0 always (or 2 if `<id>` given but not found).

---

## `add`

```
skills-styles add <modality> <id>
skills-styles add <modality> <id> --from <existing-id>
skills-styles add <modality> <id> --force
```

Two modes:

- **From template** (default): copies `<modality>/_template.md` (bundled), replaces `<ID>` and `<MODALITY>` placeholders, writes to user dir.
- **From existing** (`--from <id>`): copies the resolved bundled file, rewrites `id:` and appends "(custom)" to `display:`.

Refuses to overwrite an existing file without `--force`.

Refuses an `<id>` that doesn't match `^[a-z][a-z0-9-]{1,40}$` (kebab-case, lowercase, no spaces, no underscores).

After creation:

```
  ✓ Created carousel/retro-soviet-poster.md  (from template)
    Path: /Users/.../.claude/style-library/carousel/retro-soviet-poster.md
    Next: skills-styles edit carousel retro-soviet-poster
    Then: skills-styles validate carousel retro-soviet-poster
```

Exit: 0 on success, 2 on conflict / invalid id / missing template.

### What "from template" creates

A skeleton with all required frontmatter fields + all required body sections, populated with `<placeholder>` text. The conventions block at the bottom is inside a `<!-- comment -->` so it doesn't render but stays in the file as a reminder.

### What "from existing" creates

The bundled file copied verbatim, except:
- `id:` rewritten to the new id
- `display:` gets " (custom)" appended

You'll need to update the rest (palette / typography / anchor text / etc) to match the new intent.

---

## `edit`

```
skills-styles edit <modality> <id>
```

Opens the **user-override** file in `$EDITOR` (or `$VISUAL`).

If the id exists only as a bundled style (no user override), prints an error and suggests `skills-styles add <modality> <id> --from <id>` to create an override.

If `$EDITOR` is unset, just prints the file path so you can open it manually.

Exit: 0 on clean editor close, 1 if editor exits non-zero.

---

## `remove`

```
skills-styles remove <modality> <id>           # safety check, no-op
skills-styles remove <modality> <id> --force   # actually deletes
```

Deletes ONLY the user-override file. The bundled file (if any) is untouched.

Without `--force`, the skill prints a preview of what will happen + asks you to add `--force`. This is intentional friction — deletion is irreversible.

If the style is `user-only` (no bundled fallback), the warning is louder.

Exit: 0 on delete success or no-op, 2 if file doesn't exist.

---

## `validate`

```
skills-styles validate <modality> <id>
```

Resolves the style (user > bundled), then runs the schema check.

Checks:

- All required frontmatter keys present (see [templates.md](templates.md))
- `id` matches `^[a-z][a-z0-9-]{1,40}$` AND equals the filename stem
- `modality` field equals the directory it lives in
- `mood` + `tags` are lists of strings
- Per-modality fields have valid values:
  - `pacing` ∈ {slow, medium, snap, kinetic}
  - `energy` ∈ {calm, warm, driving, aggressive}
  - `bpm_range` matches `^\d{2,3}-\d{2,3}$`
  - booleans are actual booleans, not strings
- All required body fields are present (markers like `**Vibe**:`, `**Style anchor (carousel)**:`)
- The main style anchor is ≥40 characters

Does NOT check:

- Style content quality (subjective)
- Whether anchor text contains copyrighted names / brand mimicry (reviewer judgment)
- Whether the style is duplicative of an existing one

Exit: 0 if valid, 1 if any issue found, 2 if file not found.

Output:

```
# carousel/retro-soviet-poster  [user-only]  (/Users/.../.claude/style-library/carousel/retro-soviet-poster.md)

  ✓ valid — passes all schema checks
```

Or:

```
# carousel/retro-soviet-poster  [user-only]  (...)

  ✗ 3 issue(s):
    - frontmatter missing required field(s): photoreal, text_friendly
    - 'mood' must be a list (got str)
    - body missing field: 'Style anchor (text-in-image mode)' (expected line starting with '**Style anchor (text-in-image mode)**:')
```

---

## `diff`

```
skills-styles diff <modality> <id>
```

Standard unified diff between bundled and user-override. Useful when you've customized a bundled style and want to see what's changed before submitting upstream.

Cases:

- No user override → "nothing to diff" (exit 0)
- No bundled counterpart → "this is a user-only style" (exit 0)
- Both exist → diff output (exit 0)

---

## `submit`

```
skills-styles submit <modality> <id>
skills-styles submit <modality> <id> --force
```

Validates the style. If issues, refuses unless `--force` is passed (don't submit broken styles upstream).

Builds a submission package at `./style-submission-<ts>-<modality>-<id>/`:

```
style-submission-<ts>-<modality>-<id>/
├── common/
│   └── style-library/
│       └── <modality>/
│           └── <id>.md          # the style file at the exact repo path
├── PR-DESCRIPTION.md            # PR body template
└── README.md                    # step-by-step manual PR instructions
```

The package is self-contained. You don't need this skills repo cloned to submit.

The skill prints the next steps to stdout (fork → clone → branch → cp → commit → push → `gh pr create`).

**Why not auto-PR?** Because fork detection, branch creation, push behind a remote, and `gh pr create` together are 6-8 things that can fail. v1 prepares the package and trusts you to do the git ops. Future v2 may add auto-PR behind a `--auto` flag with `gh` CLI gating.

Exit: 0 on package built, 2 on validation failure (without `--force`).

---

## Common errors

### `style 'X' not found for modality 'carousel'`

The id doesn't match any bundled or user file. Run `list carousel` to see what exists.

### `id 'X' must match ^[a-z][a-z0-9-]{1,40}$`

Use kebab-case, lowercase only, no spaces, no underscores. Examples:
- ✓ `retro-soviet-poster`
- ✓ `kinfolk-minimal-warmer`
- ✗ `RetroSovietPoster` (capitals)
- ✗ `retro_soviet_poster` (underscores)
- ✗ `retro-soviet` + 40-char-of-padding-just-to-test-limits-here (>40 chars after slug)

### `style already exists at /path/...md (use --force to overwrite)`

`add` is non-destructive by default. Either pick a different id or pass `--force`.

### `style has N validation issue(s)` (from submit)

Fix the issues first (`skills-styles edit ... && skills-styles validate ...`). The validator output tells you which fields are missing or malformed.

---

## Programmatic API

For scripts that want to bypass the CLI:

```python
from common.runners import styles as styles_mod

# Read
style = styles_mod.load_style("kinfolk-minimal", "carousel")
all_carousel = styles_mod.list_styles("carousel")
status = styles_mod.resolution_status("kinfolk-minimal", "carousel")  # 'bundled' | 'user-only' | 'override' | 'missing'

# Create
path = styles_mod.copy_template("carousel", "my-new-style")
path = styles_mod.copy_existing("kinfolk-minimal", "my-new-style", "carousel")

# Validate
issues = styles_mod.validate_style(style)
if issues:
    for i in issues:
        print(i)
```
