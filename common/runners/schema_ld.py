"""JSON-LD structured data, plus llms.txt.

Schema stopped being a click-through trick and became a citation one. Google
retired FAQ rich results on 2026-05-07 — the expandable SERP block is gone — but
the `FAQPage` type is still valid markup, and it is what AI Overviews, ChatGPT
browsing, Perplexity and Gemini parse first when deciding whose answer to quote.
Pages carrying FAQPage / HowTo / QAPage show up in AI summaries markedly more
often than pages without.

So the priority order here is citation-shaped, not SERP-shaped: FAQPage, HowTo,
Article, Organization, Person. JSON-LD only — it is the format Google recommends
and the one AI crawlers parse most consistently, and unlike microdata it does
not entangle itself with the page's markup.

Everything is generated and validated locally. No network, no vendor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

CONTEXT = "https://schema.org"

# The types that move citation rates, in the order worth implementing them.
TIER_1 = ("FAQPage", "HowTo", "Article", "Organization", "Person")


class SchemaError(ValueError):
    """A document that would be invalid or misleading if emitted."""


@dataclass
class Author:
    name: str
    url: str = ""
    job_title: str = ""
    # `knowsAbout` is the property that connects an author entity to a topic.
    # Author authority became a direct ranking input in the March 2026 update,
    # and this is where the topical alignment is declared.
    knows_about: tuple[str, ...] = ()
    same_as: tuple[str, ...] = ()  # profile URLs that corroborate the entity

    def to_ld(self) -> dict[str, Any]:
        node: dict[str, Any] = {"@type": "Person", "name": self.name}
        if self.url:
            node["url"] = self.url
        if self.job_title:
            node["jobTitle"] = self.job_title
        if self.knows_about:
            node["knowsAbout"] = list(self.knows_about)
        if self.same_as:
            node["sameAs"] = list(self.same_as)
        return node


@dataclass
class ArticleMeta:
    headline: str
    description: str = ""
    url: str = ""
    date_published: str = ""  # ISO 8601
    date_modified: str = ""
    author: Author | None = None
    publisher_name: str = ""
    publisher_url: str = ""
    image: str = ""
    keywords: tuple[str, ...] = ()


def _require(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise SchemaError(f"{field_name} is required and cannot be empty")
    return value.strip()


def article(meta: ArticleMeta) -> dict[str, Any]:
    """Article node with the E-E-A-T properties that carry weight.

    `dateModified` matters as much as `datePublished`: freshness is read from
    both, and an article that never declares a modification date reads as
    unmaintained no matter how recently it was edited.
    """
    node: dict[str, Any] = {
        "@context": CONTEXT,
        "@type": "Article",
        "headline": _require(meta.headline, "headline"),
    }
    if len(meta.headline) > 110:
        raise SchemaError(
            f"headline is {len(meta.headline)} chars; Google truncates Article "
            f"headlines past 110 and the type documents that limit"
        )

    for key, value in (
        ("description", meta.description),
        ("url", meta.url),
        ("datePublished", meta.date_published),
        ("dateModified", meta.date_modified or meta.date_published),
        ("image", meta.image),
    ):
        if value:
            node[key] = value
    if meta.keywords:
        node["keywords"] = list(meta.keywords)
    if meta.author:
        node["author"] = meta.author.to_ld()
    if meta.publisher_name:
        publisher: dict[str, Any] = {"@type": "Organization", "name": meta.publisher_name}
        if meta.publisher_url:
            publisher["url"] = meta.publisher_url
        node["publisher"] = publisher
    if meta.url:
        node["mainEntityOfPage"] = {"@type": "WebPage", "@id": meta.url}
    return node


def faq_page(pairs: list[tuple[str, str]]) -> dict[str, Any]:
    """FAQPage — the highest-leverage type, because Q&A pairs lift verbatim.

    Google's FAQ rich result is gone; the markup is not. Engines read these
    pairs directly, which is why a question that does not end in a question mark
    is rejected here: a statement heading defeats the whole point.
    """
    if not pairs:
        raise SchemaError("FAQPage needs at least one question/answer pair")

    entities = []
    for question, answer in pairs:
        q = _require(question, "question")
        a = _require(answer, "answer")
        if not q.rstrip().endswith("?"):
            raise SchemaError(f"FAQ question must be a question: {q!r}")
        entities.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    return {"@context": CONTEXT, "@type": "FAQPage", "mainEntity": entities}


def how_to(name: str, steps: list[tuple[str, str]], *, description: str = "") -> dict[str, Any]:
    """HowTo — process-intent pages. Steps carry a name and the text."""
    if not steps:
        raise SchemaError("HowTo needs at least one step")
    node: dict[str, Any] = {
        "@context": CONTEXT,
        "@type": "HowTo",
        "name": _require(name, "name"),
        "step": [
            {"@type": "HowToStep", "name": _require(s, "step name"), "text": _require(t, "step text")}
            for s, t in steps
        ],
    }
    if description:
        node["description"] = description
    return node


def organization(
    name: str, url: str, *, logo: str = "", same_as: tuple[str, ...] = ()
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "@context": CONTEXT,
        "@type": "Organization",
        "name": _require(name, "name"),
        "url": _require(url, "url"),
    }
    if logo:
        node["logo"] = logo
    if same_as:
        node["sameAs"] = list(same_as)
    return node


def person(author: Author) -> dict[str, Any]:
    node = author.to_ld()
    node["@context"] = CONTEXT
    return node


def render(nodes: list[dict[str, Any]], *, script_tag: bool = True) -> str:
    """One or more nodes as a pasteable block.

    Several nodes go into a @graph rather than several script tags — one graph
    lets a parser resolve references between them, and it is what the type
    documentation recommends.
    """
    if not nodes:
        raise SchemaError("nothing to render")
    if len(nodes) == 1:
        payload: dict[str, Any] = nodes[0]
    else:
        payload = {
            "@context": CONTEXT,
            "@graph": [{k: v for k, v in n.items() if k != "@context"} for n in nodes],
        }
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    if not script_tag:
        return body
    return f'<script type="application/ld+json">\n{body}\n</script>'


# ── llms.txt ────────────────────────────────────────────────────────────────


@dataclass
class LlmsSection:
    title: str
    links: list[tuple[str, str, str]] = field(default_factory=list)  # (name, url, note)


def llms_txt(
    *,
    name: str,
    summary: str,
    sections: list[LlmsSection],
    details: str = "",
) -> str:
    """Render an llms.txt file.

    Honest framing, because the docs should not oversell it: llms.txt is a
    community convention with no standards body behind it. Anthropic recommends
    it, Google has said Search does not use it, and as of 2026 no major vendor
    has committed to reading it in production. It is not part of any documented
    citation pipeline.

    It is cheap, it is well-formed, and it does no harm. Treat it as tidy
    infrastructure, not as a ranking lever.
    """
    out = [f"# {_require(name, 'name')}", "", f"> {_require(summary, 'summary')}", ""]
    if details:
        out += [details.strip(), ""]
    for section in sections:
        out.append(f"## {section.title}")
        out.append("")
        for link_name, url, note in section.links:
            suffix = f": {note}" if note else ""
            out.append(f"- [{link_name}]({url}){suffix}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"
