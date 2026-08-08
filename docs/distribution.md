# Distribution

Where this project is listed, where it should be, and what each listing is
actually worth. Generate the submission material with:

```bash
python3 -m common.runners.cli.distribute --list          # the map
python3 -m common.runners.cli.distribute                 # write packets
```

Packets land in `./generated/distribution/`. Nothing is submitted automatically —
several of these directories require a human to fill the form, and
awesome-claude-code bans automated submissions outright.

---

## What is worth doing, and what is not

The tempting version of this page is a list of a hundred "free dofollow backlink
sites". That is the exact pattern Google's June 2025 and October 2025 spam
updates were built to catch: links from directories with no editorial review are
ignored, and at volume they attract manual actions rather than rankings.

Every entry below is somewhere this project genuinely belongs. The link is a
by-product of being listed; the listing is the point. Where a link is nofollow it
says so, because "worth doing for the audience" and "worth doing for search" are
different reasons and should not be confused.

---

## The map

Last reviewed: 2026-08-08. `tests/unit/test_distribution.py` fails 90 days after
that date — the point is to re-check the statuses against the actual listings,
not to move the line.

Status is one of `listed`, `submitted`, `drafted`, `not submitted`. Anything else
fails the same test, because a free-text column is how the npm row came to say
"published" through a release that never uploaded.

| Directory | Link | Route | Status |
|---|---|---|---|
| npm registry | dofollow | `make publish-npm` | listed |
| Anthropic community plugin directory | dofollow | form at clau.de | not submitted |
| awesome-claude-code | dofollow | issue form, by hand | drafted |
| travisvn/awesome-claude-skills | dofollow | pull request | not submitted |
| claudemarketplaces.com | unknown | site form | not submitted |
| aitmpl.com | unknown | site form | not submitted |
| AlternativeTo | dofollow | add-software form | not submitted |
| SourceForge | dofollow | project + GitHub mirror | not submitted |
| Product Hunt | nofollow | scheduled launch | not submitted |

`listed` for npm means the package is on the registry, not that it is current:
the upload runs at release time and skips itself when `npm login` has expired,
which is what left v2.24.0 on disk and 2.23.0 on the registry.

---

## Highest value first

### npm — the one that was already earned

npm carries more authority than anything else on this list, the package exists,
and its page links to the repo dofollow. It had drifted to **1.9.0 while the repo
was on 2.23.0**, because nothing tied `npm publish` to cutting a release.

Fixed two ways: `make release` now calls `make publish-npm`, and the target is
idempotent, so re-running it after a failed login is safe.

Also fixed on the way through: the tarball was shipping `__pycache__/*.pyc`.
`.npmignore` did not apply because `package.json` sets a `files` allow-list,
which takes precedence. Negation patterns in `files` were the fix — 656 files
down to 552.

### Anthropic community plugin directory — newly possible

This one could not be submitted before v2.23.0, because a submission needs
`.claude-plugin/marketplace.json` in the repo root and there was none. Now there
is.

The payoff is the install path: a listed plugin installs with
`claude plugin marketplace add anthropics/claude-plugins-community` followed by
the plugin name, instead of the user having to know this repo exists.

Submissions go through **clau.de/plugin-directory-submission**. Pull requests
against the mirror repo are closed automatically. Expect an automated security
scan and a manual review.

### The awesome lists

Highest relevance per unit of effort, and the ecosystem's main discovery path.
`awesome-claude-code` copy is already written in
[`launch-posts/awesome-claude-code.md`](launch-posts/awesome-claude-code.md) —
note the warning there: their CONTRIBUTING forbids PRs and CLI submissions, and
says recommendations must be created by a human through the web UI.

---

## What is deliberately not here

**PyPI.** The Python runners are not a standalone library — they are the
execution layer of a skill collection and are useless installed on their own.
Publishing a package purely to hold a link is the behaviour this page argues
against.

**Docker Hub.** There is a `Dockerfile`, so the option is real, but an
unmaintained image is worse than no image: it goes stale silently and people
file bugs against a build from months ago. Worth doing only alongside a CI job
that rebuilds it per release.

**Generic SEO directories.** See the first section.

---

## Keeping it honest

The status column above is maintained by hand, and it rotted exactly as this
section predicted: the npm row read "published" while the registry sat a release
behind, because the row was written when the target was fixed rather than when an
upload succeeded.

So it now carries the same guard as the model ids — a dated marker and a test.
`tests/unit/test_distribution.py` checks three things offline: the review date is
under 90 days old, every status comes from the four-word vocabulary, and every
`make` route named in the table is a target that still exists. What it cannot
check is whether a listing is real; that is what the 90-day prompt is for.
