# llms.txt — the honest state of it

Read this before telling anyone it will help.

## What it is

A markdown file at `/llms.txt` that describes a site for language models: a
title, a one-line summary, and curated links with notes. Proposed in 2024, and
by 2026 it is a familiar convention across documentation sites.

## What it is not

**It is not a standard.** No W3C, no IETF, no RFC. A formal standardisation
effort has been discussed and has not materialised. The spec is community-managed.

**It is not part of any documented citation pipeline.** As of 2026, no major AI
company — OpenAI, Google, Anthropic, Meta, Mistral — has publicly committed to
reading or acting on `llms.txt` in production systems. Google said through John
Mueller that Search does not use it.

The position is genuinely split. Anthropic is the convention's most prominent
advocate and recommends it in its own guidance for writing for agents; OpenAI
maintains llms.txt files for some of its own products without committing to
consuming anyone else's. Advocacy from a vendor is not the same as that vendor's
retrieval stack reading the file.

## So why generate one at all

Because it costs nothing and does no harm. A tidy, accurate map of a site is
defensible on its own terms — the same way a good sitemap is — and if any engine
does start honouring it, the file is already there and already correct.

What it will not do is lift citation rates on its own. If a page is not
extractable, an llms.txt pointing at it changes nothing. Structure first
(`writer --aeo`), schema second, this last.

## Generating one

```bash
python3 -m common.runners.cli.schema --llms-txt \
  --site-name "Your Site" \
  --site-summary "What it is, in one sentence." \
  --url "https://you.dev"
```

The generated file carries a note saying the convention is unratified, so nobody
reading the repository later mistakes it for a ranking mechanism.

## Keeping it honest

An llms.txt that lists pages which have moved is worse than none — it is a map
to nothing, and it is exactly the kind of file that rots silently because
nothing renders it. Regenerate it when the site's structure changes, or do not
ship one.
