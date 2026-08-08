"""Submission packets for directories, registries and curated lists.

Sibling of `syndication.py`. That module syndicates one *article*; this one
places the *project* — the same repo, submitted once per directory, with a
tagline and a category rather than a body.

What this is not: a backlink farm. The "1000+ free dofollow sites" lists are the
thing Google's 2025 spam updates were aimed at, and links from directories with
no editorial review are ignored at best. Every entry below is a place this
project genuinely belongs, where the link is a by-product of being listed rather
than the reason for showing up.

Project facts are read from package.json and skills.json so a packet cannot
quietly describe a version that shipped two releases ago — which is exactly how
the npm listing ended up advertising 1.9.0 while the repo was on 2.23.0.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

LinkType = str  # "dofollow" | "nofollow" | "unknown"


@dataclass(frozen=True)
class DirectorySpec:
    slug: str
    label: str
    url: str
    why: str
    route: str  # how a submission is made
    link: LinkType
    needs: tuple[str, ...]
    steps: tuple[str, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)


# Routes verified 2026-08-05. Where a submission URL could not be confirmed, the
# spec says so instead of guessing one — a wrong form URL wastes more time than
# an honest "check the CONTRIBUTING".
SPECS: dict[str, DirectorySpec] = {
    "npm": DirectorySpec(
        slug="npm",
        label="npm registry",
        url="https://www.npmjs.com/package/@mikefluff/skills",
        why="Highest-authority listing available to this project, and it already exists.",
        route="`make publish-npm` (or `npm publish --access public`)",
        link="dofollow",
        needs=("package.json homepage + repository fields", "npm login"),
        steps=(
            "npm login",
            "make publish-npm",
            "Check the rendered README on the package page — npm renders it as the landing copy.",
        ),
        notes=(
            "The published version drifted 14 minors behind the repo because nothing "
            "tied `npm publish` to the release. `make release` now calls it.",
        ),
    ),
    "claude-community": DirectorySpec(
        slug="claude-community",
        label="Anthropic community plugin directory",
        url="https://github.com/anthropics/claude-plugins-community",
        why=(
            "Official directory. Installs become one command: "
            "`claude plugin marketplace add anthropics/claude-plugins-community`."
        ),
        route="Submission form at https://clau.de/plugin-directory-submission",
        link="dofollow",
        needs=(".claude-plugin/marketplace.json in the repo root", "public repository"),
        steps=(
            "Confirm `/plugin marketplace add Mikefluff/skills` works from a clean checkout.",
            "Submit the repo through clau.de/plugin-directory-submission.",
            "Wait for the automated security scan and manual review.",
        ),
        notes=(
            "Pull requests against that repo are closed automatically — the form is the "
            "only route. The list syncs nightly from Anthropic's internal pipeline.",
            "This became possible only once the plugin manifest shipped in v2.23.0.",
        ),
    ),
    "awesome-claude-code": DirectorySpec(
        slug="awesome-claude-code",
        label="awesome-claude-code",
        url="https://github.com/hesreallyhim/awesome-claude-code",
        why="The most-linked curated list in the Claude Code ecosystem.",
        route="Issue form in the repo — NOT a pull request",
        link="dofollow",
        needs=("one-line description", "repo URL"),
        steps=(
            "Open the repo's issue form in a browser.",
            "Fill it in by hand and submit.",
        ),
        notes=(
            "Their CONTRIBUTING is explicit: do not open a PR and do not submit via the "
            "`gh` CLI. Submissions must be created by a human through the web UI, or you "
            "risk a ban. Copy for this one already exists in docs/launch-posts/.",
        ),
    ),
    "awesome-claude-skills": DirectorySpec(
        slug="awesome-claude-skills",
        label="travisvn/awesome-claude-skills",
        url="https://github.com/travisvn/awesome-claude-skills",
        why="Skills-focused list rather than a general Claude Code one — closer fit.",
        route="Pull request — read the repo's CONTRIBUTING first",
        link="dofollow",
        needs=("one-line description", "category placement"),
        steps=(
            "Read CONTRIBUTING.md — awesome lists differ on PR vs issue.",
            "Add one alphabetically-placed line in the right section.",
            "Keep the description to a single clause; these lists reject marketing copy.",
        ),
    ),
    "claudemarketplaces": DirectorySpec(
        slug="claudemarketplaces",
        label="claudemarketplaces.com",
        url="https://claudemarketplaces.com/",
        why="Web directory of plugin marketplaces; indexes by marketplace, not by plugin.",
        route="Submission form on the site",
        link="unknown",
        needs=(".claude-plugin/marketplace.json", "marketplace name"),
        steps=("Find the submit link on the site and register the marketplace name `mikefluff`.",),
    ),
    "aitmpl": DirectorySpec(
        slug="aitmpl",
        label="aitmpl.com",
        url="https://www.aitmpl.com/plugins/",
        why="Plugin and marketplace directory with browsing by category.",
        route="Submission form on the site",
        link="unknown",
        needs=("repo URL", "category"),
        steps=("Submit through the site's own form.",),
    ),
    "alternativeto": DirectorySpec(
        slug="alternativeto",
        label="AlternativeTo",
        url="https://alternativeto.net/",
        why="Editorially moderated, high authority, real traffic from people comparing tools.",
        route="Add-software form; requires an account",
        link="dofollow",
        needs=("tagline", "category", "screenshots", "licence", "platforms"),
        steps=(
            "Create an account and use Add Software.",
            "List it as an alternative to comparable tooling — that is how people arrive.",
            "Expect moderation; thin entries are rejected.",
        ),
    ),
    "sourceforge": DirectorySpec(
        slug="sourceforge",
        label="SourceForge",
        url="https://sourceforge.net/",
        why="High authority; mirrors open-source projects and ranks well on tool queries.",
        route="Create a project, point it at the GitHub repo",
        link="dofollow",
        needs=("project description", "licence", "category"),
        steps=("Register the project and enable the GitHub mirror rather than uploading files.",),
    ),
    "producthunt": DirectorySpec(
        slug="producthunt",
        label="Product Hunt",
        url="https://www.producthunt.com/",
        why="A launch-day traffic spike rather than a durable listing.",
        route="Scheduled launch; needs assets ready in advance",
        link="nofollow",
        needs=("tagline (60 chars)", "gallery images", "first comment", "launch date"),
        steps=(
            "Prepare the gallery and the maker's first comment before scheduling.",
            "Launch early in the day, US time.",
        ),
        notes=("Links are nofollow — this one is for traffic and signups, not for ranking.",),
    ),
}

DEFAULT_ORDER = (
    "npm",
    "claude-community",
    "awesome-claude-code",
    "awesome-claude-skills",
    "claudemarketplaces",
    "aitmpl",
    "alternativeto",
    "sourceforge",
    "producthunt",
)


@dataclass
class ProjectFacts:
    """What every packet needs to say about the project, read from the repo."""

    name: str
    version: str
    description: str
    repo: str
    homepage: str
    license: str
    keywords: tuple[str, ...]
    skill_count: int

    @classmethod
    def load(cls, root: Path) -> "ProjectFacts":
        pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
        repo = pkg.get("repository") or {}
        url = repo.get("url", "") if isinstance(repo, dict) else str(repo)
        skills = len(list((root / "skills").glob("*/SKILL.md")))
        return cls(
            name=pkg.get("name", ""),
            version=(root / "VERSION").read_text(encoding="utf-8").strip(),
            description=pkg.get("description", ""),
            repo=url.removeprefix("git+").removesuffix(".git"),
            homepage=pkg.get("homepage", ""),
            license=pkg.get("license", ""),
            keywords=tuple(pkg.get("keywords", [])),
            skill_count=skills,
        )


def _packet(spec: DirectorySpec, facts: ProjectFacts) -> str:
    lines = [
        f"# {spec.label} — submission packet",
        "",
        f"**Where**: {spec.url}",
        f"**Route**: {spec.route}",
        f"**Link type**: {spec.link}",
        "",
        f"**Why bother**: {spec.why}",
        "",
        "## Project facts",
        "",
        f"- **Name**: {facts.name}",
        f"- **Version**: {facts.version}",
        f"- **Repo**: {facts.repo}",
        f"- **Homepage**: {facts.homepage}",
        f"- **Licence**: {facts.license}",
        f"- **Skills**: {facts.skill_count}",
        f"- **Keywords**: {', '.join(facts.keywords) if facts.keywords else '(none)'}",
        "",
        "## Description",
        "",
        facts.description,
        "",
        "## What this directory wants",
        "",
    ]
    lines += [f"- {n}" for n in spec.needs]
    lines += ["", "## Steps", ""]
    lines += [f"{i}. {s}" for i, s in enumerate(spec.steps, 1)]

    if spec.notes:
        lines += ["", "## Notes", ""]
        lines += [f"- {n}" for n in spec.notes]

    if spec.link == "nofollow":
        lines += [
            "",
            "> Links here are nofollow: no ranking signal passes. Worth doing for the "
            "audience, not for SEO.",
        ]
    lines.append("")
    return "\n".join(lines)


def write_packets(
    root: Path,
    out_dir: Path,
    *,
    directories: tuple[str, ...] = DEFAULT_ORDER,
) -> list[Path]:
    """Render one packet per directory. Returns the paths written."""
    unknown = [d for d in directories if d not in SPECS]
    if unknown:
        raise KeyError(f"unknown directory: {', '.join(unknown)}. Known: {', '.join(SPECS)}")

    facts = ProjectFacts.load(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for slug in directories:
        path = out_dir / f"submit-{slug}.md"
        path.write_text(_packet(SPECS[slug], facts), encoding="utf-8")
        written.append(path)
    return written
