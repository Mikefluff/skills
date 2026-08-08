"""Submission packets for article platforms that have no publishing API.

Half the places worth syndicating to cannot be posted to programmatically:
Medium closed its API to new integrations in March 2023, HackerNoon runs every
submission past human editors, and Habr, VC.ru and Dzen have never published a
write API at all. Driving a headless browser at them would be against their
terms and brittle besides.

So this module does the part that *can* be automated: it works out the order of
operations, writes the per-platform constraints and the canonical instruction
into a checklist, and leaves a file the author pastes from. The text adaptation
itself is not here — a single body reposted verbatim to five platforms is what
those platforms pessimise. That is a job for `tone-shifter`, driven by the
SKILL, and the packet says so per platform.

Nothing in this file performs I/O against a vendor. It renders markdown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .publishers.base import Post


@dataclass(frozen=True)
class PlatformSpec:
    """What a human needs to know to submit one article by hand."""

    slug: str
    label: str
    why: str
    canonical: str
    steps: tuple[str, ...]
    adapt: str
    caveats: tuple[str, ...] = field(default_factory=tuple)


# Verified 2026-08-05. Deliberately free of invented character limits — the
# submission flow and the canonical mechanism are what these platforms document,
# and a made-up "max 120 chars" would be worse than no number at all.
SPECS: dict[str, PlatformSpec] = {
    "medium": PlatformSpec(
        slug="medium",
        label="Medium",
        why=(
            "Large general audience. Outbound links are nofollow, so the value is "
            "reach, not ranking signal."
        ),
        canonical=(
            "Set automatically. Importing a story makes Medium point its canonical "
            "at the source URL for you — do not paste the text by hand, or you lose that."
        ),
        steps=(
            "Publish to dev.to first and copy the resulting URL.",
            "Open medium.com/p/import (Profile → Stories → Import a story).",
            "Paste the dev.to URL and let Medium fetch it.",
            "Check the canonical notice appears under the title before publishing.",
            "Add up to 5 topic tags, then publish.",
        ),
        adapt=(
            "Little adaptation needed — Medium's audience overlaps dev.to's. Retitle "
            "only if the dev.to headline leans on developer jargon."
        ),
        caveats=(
            "The Medium API has been closed to new integrations since March 2023; "
            "existing tokens still work but no new ones are issued. The import route "
            "is the supported path, not a workaround.",
        ),
    ),
    "hackernoon": PlatformSpec(
        slug="hackernoon",
        label="HackerNoon",
        why="Tech-editorial audience, strong distribution when accepted.",
        canonical="Set the canonical field in story settings before submitting.",
        steps=(
            "Draft the story in the HackerNoon editor.",
            "Fill the canonical URL field in story settings.",
            "Pick tags, add a cover image, submit for review.",
            "Wait — the editorial queue runs about 3-5 business days.",
        ),
        adapt=(
            "Tighten the opening. HackerNoon editors reject posts that read as "
            "company blog content; lead with the finding, not the context."
        ),
        caveats=("Human editorial review; acceptance is not guaranteed.",),
    ),
    "habr": PlatformSpec(
        slug="habr",
        label="Habr",
        why=(
            "The one that actually matters for Yandex. Technical, and unforgiving of "
            "anything that reads like marketing."
        ),
        canonical="Mark the post as a translation/repost and link the original in the first paragraph.",
        steps=(
            "Choose the right hub — the wrong hub is the usual reason a good post sinks.",
            "Paste the adapted body; Habr's editor takes markdown.",
            "Link the original explicitly near the top.",
            "Publish into a hub you have karma for, or it lands in a sandbox.",
        ),
        adapt=(
            "Rewrite, do not repost. Habr wants depth, concrete numbers and reproducible "
            "detail; promotional framing gets downvoted fast. Run the body through "
            "`tone-shifter --to technical` and cut every claim you cannot source."
        ),
        caveats=(
            "No public publishing API.",
            "New accounts post into a sandbox until they earn karma.",
        ),
    ),
    "vc": PlatformSpec(
        slug="vc",
        label="VC.ru",
        why="Business and startup audience in Russian; good referral traffic.",
        canonical="No canonical field — link the original in the body.",
        steps=(
            "Pick the subsite (Маркетинг, Разработка, …) that matches the topic.",
            "Paste the adapted body and add a cover.",
            "Link the original in the first or last paragraph.",
        ),
        adapt=(
            "Lead with the business outcome, not the method. VC readers reward "
            "numbers, postmortems and opinion; they scroll past tutorials."
        ),
        caveats=("No official public API.",),
    ),
    "dzen": PlatformSpec(
        slug="dzen",
        label="Dzen",
        why="Broadest Russian reach, weakest technical audience.",
        canonical="No canonical field — link the original in the body.",
        steps=(
            "Create the article in Dzen Studio.",
            "Add a cover — Dzen's feed is thumbnail-driven more than any other here.",
            "Publish and watch the first-hour CTR; Dzen decides reach on it.",
        ),
        adapt=(
            "Simplify hard. Short paragraphs, no jargon, a concrete hook in the first "
            "two sentences. This is the one platform where the technical version will fail."
        ),
        caveats=(
            "No public API.",
            "Reach is decided by early click-through, so the title and cover matter "
            "more than the body.",
        ),
    ),
}

MANUAL_ORDER = ("medium", "hackernoon", "habr", "vc", "dzen")


def _packet(spec: PlatformSpec, post: Post, devto_url: str | None) -> str:
    lines = [
        f"# {spec.label} — submission packet",
        "",
        f"**Why this platform**: {spec.why}",
        "",
        f"**Canonical**: {spec.canonical}",
        "",
        "## Content",
        "",
        f"- **Title**: {post.title or '(none — write one)'}",
        f"- **Description**: {post.description or '(none)'}",
        f"- **Tags**: {', '.join(post.hashtags) if post.hashtags else '(none)'}",
        f"- **Canonical URL**: {post.canonical_url or '(none — this is a problem, see below)'}",
    ]
    if spec.slug == "medium":
        lines.append(f"- **Import from**: {devto_url or '(publish to dev.to first)'}")
    lines += ["", "## Adapt before posting", "", spec.adapt, "", "## Steps", ""]
    lines += [f"{i}. {step}" for i, step in enumerate(spec.steps, 1)]

    if spec.caveats:
        lines += ["", "## Caveats", ""]
        lines += [f"- {c}" for c in spec.caveats]

    if not post.canonical_url:
        lines += [
            "",
            "> **No canonical URL was set.** Posting the same text to several "
            "platforms without one splits the ranking signal between them, and the "
            "platform with the bigger domain wins — with your words. Publish the "
            "original somewhere you own first, then syndicate.",
        ]

    lines += ["", "## Body", "", post.text.rstrip(), ""]
    return "\n".join(lines)


def write_packets(
    post: Post,
    out_dir: Path,
    *,
    platforms: tuple[str, ...] = MANUAL_ORDER,
    devto_url: str | None = None,
) -> list[Path]:
    """Render one markdown packet per manual platform. Returns the paths written."""
    unknown = [p for p in platforms if p not in SPECS]
    if unknown:
        raise KeyError(f"unknown platform(s): {', '.join(unknown)}. Known: {', '.join(SPECS)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for slug in platforms:
        path = out_dir / f"packet-{slug}.md"
        path.write_text(_packet(SPECS[slug], post, devto_url), encoding="utf-8")
        written.append(path)
    return written


def plan(post: Post, *, has_own_blog: bool = True) -> list[str]:
    """The order the platforms should be hit in, as human-readable steps.

    Order is not cosmetic. Medium's import needs a dev.to URL to exist, and the
    canonical target has to be live before anything points at it.
    """
    steps: list[str] = []
    if has_own_blog and post.canonical_url:
        steps.append(f"1. Original is live at {post.canonical_url} — everything points here.")
    else:
        steps.append(
            "1. No canonical target. Write the original first — "
            "`python3 -m common.runners.cli.origin` renders it into a static blog and "
            "prints the URL it will have. Without one, syndication gives your text away "
            "rather than promoting it."
        )
    steps += [
        "2. dev.to — the only platform here with dofollow outbound links. Publish with "
        "canonical set; this URL is also what Medium imports from.",
        "3. Medium — import the dev.to URL. Canonical is set for you.",
        "4. hashnode — needs Hashnode Pro for API writes.",
        "5. micropub — one endpoint, whatever your site advertises (Micro.blog, "
        "WordPress with the plugin).",
        "6. tumblr / telegraph — reach, not ranking. Neither has a canonical field, so "
        "the link home sits in the body.",
        "7. qiita — Japanese only. Skip unless the body has been translated.",
        "8. Manual packets — HackerNoon, then Habr / VC.ru / Dzen with the body rewritten "
        "per platform rather than reposted.",
    ]
    return steps
