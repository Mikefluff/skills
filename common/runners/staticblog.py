"""The canonical source step, for a static site generator.

Everything else in the syndication chain points `canonical_url` at an original
that has to exist first. With Hugo, Astro, Jekyll and friends there is no API to
publish through — the post is a file in a git repository. So this module does
the two things that actually need doing:

  1. writes the markdown with the frontmatter the generator expects, and
  2. works out what the URL *will* be once the site rebuilds.

(2) is the useful half. Knowing the URL before the post is live is what lets a
single run publish the original and syndicate everything else with a correct
canonical, instead of publishing, waiting for a deploy, copying the URL by hand
and running a second command.

It deliberately does not commit or push. A generated file landing in someone's
blog repository is theirs to review; an automatic `git push` to a personal site
is not a decision this layer gets to make.
"""

from __future__ import annotations

import datetime as dt
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Cyrillic → Latin, so a Russian headline becomes a usable slug rather than a
# string of percent-escapes. Not a transliteration standard, just the mapping
# that produces readable URLs.
_CYRILLIC = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    """Title → URL slug. Transliterates Cyrillic, strips everything else."""
    lowered = title.strip().lower()
    out = []
    for ch in lowered:
        if ch in _CYRILLIC:
            out.append(_CYRILLIC[ch])
        else:
            # Decompose accented Latin (é → e) rather than dropping the letter.
            normalised = unicodedata.normalize("NFKD", ch)
            out.append("".join(c for c in normalised if not unicodedata.combining(c)))
    slug = _NON_SLUG.sub("-", "".join(out)).strip("-")
    return slug or "post"


def _yaml_scalar(value: Any) -> str:
    """Quote a frontmatter scalar. Enough YAML to be correct, not a YAML library."""
    text = str(value)
    if any(c in text for c in ':#"\'\n[]{}|>') or text != text.strip():
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def render_frontmatter(fields: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        # `not value` would also drop `draft: false`, which has to survive.
        if value is None or (not isinstance(value, bool) and not value):
            continue
        if isinstance(value, (list, tuple)):
            rendered = ", ".join(_yaml_scalar(v) for v in value)
            lines.append(f"{key}: [{rendered}]")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


@dataclass
class BlogConfig:
    """Where posts live and what their URLs look like.

    Patterns take {slug}, {year}, {month}, {day}. Jekyll wants the date in the
    filename; Hugo and Astro usually do not — hence two separate patterns rather
    than one convention baked in.
    """

    content_dir: Path
    url_pattern: str = "https://example.com/posts/{slug}/"
    filename_pattern: str = "{slug}.md"
    date_field: str = "date"
    draft_field: str | None = "draft"
    extra_frontmatter: dict[str, Any] | None = None

    def tokens(self, slug: str, when: dt.date) -> dict[str, str]:
        return {
            "slug": slug,
            "year": f"{when.year:04d}",
            "month": f"{when.month:02d}",
            "day": f"{when.day:02d}",
        }


@dataclass
class PostDraft:
    """The content half of a write. Travels together, so it travels as one thing.

    A dataclass rather than seven keyword arguments — the same call would
    otherwise be nine parameters wide and invite positional mistakes.
    """

    title: str
    body: str
    description: str = ""
    tags: tuple[str, ...] = ()
    when: dt.date | None = None
    slug: str | None = None
    draft: bool = False

    def resolved_date(self) -> dt.date:
        return self.when or dt.date.today()

    def resolved_slug(self) -> str:
        return self.slug or slugify(self.title)


@dataclass
class DraftedPost:
    path: Path
    url: str
    slug: str
    existed: bool


def write_post(config: BlogConfig, draft: PostDraft, *, overwrite: bool = False) -> DraftedPost:
    """Write the post file and return where it landed and what its URL will be.

    Refuses to clobber an existing file unless `overwrite` — the target is
    somebody's blog repository, and a silent overwrite there is unrecoverable
    if it has not been committed yet.
    """
    when = draft.resolved_date()
    slug = draft.resolved_slug()
    title, body, description, tags = draft.title, draft.body, draft.description, draft.tags
    tokens = config.tokens(slug, when)

    filename = config.filename_pattern.format(**tokens)
    path = config.content_dir / filename
    url = config.url_pattern.format(**tokens)

    existed = path.exists()
    if existed and not overwrite:
        raise FileExistsError(
            f"{path} already exists — pass overwrite=True to replace it, "
            f"or choose a different slug"
        )

    fields: dict[str, Any] = {
        "title": title,
        config.date_field: when.isoformat(),
        "description": description,
        "tags": list(tags),
    }
    if config.draft_field:
        fields[config.draft_field] = draft.draft
    if config.extra_frontmatter:
        fields.update(config.extra_frontmatter)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{render_frontmatter(fields)}\n\n{body.strip()}\n", encoding="utf-8")

    return DraftedPost(path=path, url=url, slug=slug, existed=existed)
