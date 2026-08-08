# Article syndication

Cross-posting one article to several platforms. Different shape from the social
path: the unit is a markdown body plus a headline, and the thing that decides
whether the whole exercise helps or hurts is one field — `--canonical`.

---

## Read this before deciding it is worth doing

**Backlinks from these platforms are mostly worthless.** Medium, Hashnode,
HackerNoon, Habr, VC.ru and Dzen all mark outbound links `nofollow` or
`rel=ugc`, which passes no ranking signal. **dev.to is the single exception in
this set — its outbound links are dofollow.**

**The mechanism that does work is canonical, not links.** Publish the original
on a domain you own, syndicate with `canonical_url` pointing home, and search
engines consolidate the ranking signal onto your page. What you gain is reach
and referral traffic; what you protect is your own ranking.

**Without a canonical you are worse off than not syndicating.** The same text
on several domains makes search engines pick one winner, and a platform with a
larger domain will outrank your page for your own words. `preflight` warns when
`--canonical` is missing. Take the warning seriously.

**If the goal is Yandex specifically**: Medium and HackerNoon are close to
irrelevant. Habr, VC.ru and Dzen are what move the needle, and none of the three
has a publishing API — that half of the work is manual by necessity, not by
choice. (Also worth knowing: ТИЦ was retired in August 2018 and replaced by ИКС,
and Yandex shifted weight from citation counts to behavioural factors and site
quality at the same time. Chasing link volume for it is chasing a dead metric.)

---

## What has an API

| Platform | API | Canonical field | Links |
|---|---|---|---|
| `devto` | REST | `canonical_url` | **dofollow** |
| `micropub` | IndieWeb standard — one adapter, many endpoints | `u-syndication` | depends on the endpoint |
| `tumblr` | API v2, OAuth2 bearer, Neue Post Format | none | nofollow |
| `qiita` | API v2, `write_qiita` scope | none (guidelines ask for a link) | nofollow |
| `telegraph` | REST, no auth needed | none | — |
| `hashnode` | GraphQL, **Hashnode Pro required** | `originalArticleURL` | nofollow |
| Medium | closed to new integrations since 2023-03 | set automatically on import | nofollow |
| HackerNoon | none; human review, 3-5 business days | manual field | nofollow |
| Habr / VC.ru / Dzen | none | none | nofollow |
| Substack | no official API | — | nofollow |
| Zenn | no API — GitHub integration with frontmatter | — | nofollow |

**Substack is worth a warning.** A third-party service sells a "Substack posting
API" for $9/month, but it authenticates with **your browser session cookie**.
That hands a live session to someone else's server and runs against Substack's
terms. Not wired here, and not recommended.

`micropub` is the interesting one: it is a protocol rather than a vendor, so a
single publisher reaches Micro.blog, WordPress with the Micropub plugin, and
anything else implementing the spec. Point `MICROPUB_ENDPOINT` at whatever your
site advertises as `rel="micropub"`.

Hashnode retired free API access in May 2026. Read operations still work;
`publishPost` checks that the publication is on a paid plan.

---

## Order of operations

The order is load-bearing, not cosmetic — Medium's import needs the dev.to URL
to exist first.

1. **Original goes live on your own domain.** Everything else points here. On a
   static site there is no API for this, so `cli.origin` writes the markdown
   with frontmatter and — the useful part — prints the URL the post *will* have
   once the site rebuilds. That URL is what every later `--canonical` needs.

   ```bash
   python3 -m common.runners.cli.origin \
     --title "..." --text-file ./post.md --tags "python,api" \
     --blog-dir ~/blog/content/posts \
     --url-pattern "https://you.dev/posts/{slug}/"
   ```

   It writes the file and stops — committing and deploying stay yours. Cyrillic
   titles are transliterated into readable slugs. Jekyll's dated filenames come
   from `--filename-pattern "{year}-{month}-{day}-{slug}.md"`.
2. **dev.to**, with `--canonical` set. The only dofollow link home, and the URL
   Medium will import from.
3. **Medium**, via Import a Story using the dev.to URL. Medium sets its own
   canonical back to the source — do not paste the text by hand, or you lose
   that and create a duplicate instead.
4. **telegraph**, optionally. No SEO value; it renders natively inside Telegram,
   which matters if any distribution runs through a channel.
5. **hashnode**, if the publication is on Pro.
6. **micropub**, if your site or Micro.blog exposes an endpoint.
7. **tumblr**, for reach. No canonical field, so the link home goes in the body.
8. **qiita**, Japanese only — an English post there reaches nobody, and preflight
   says so.
9. **Manual packets** — HackerNoon, then Habr / VC.ru / Dzen.

---

## Usage

```bash
# dry run first — this is the default
python3 -m common.runners.cli.publish \
  --kind article \
  --text-file ./post.md \
  --title "Five model ids had stopped resolving" \
  --description "What vendor drift looks like in a skill collection." \
  --hashtags "python,api,webdev" \
  --canonical "https://yourdomain.com/model-drift" \
  --platform devto

# then for real
... --platform devto --yes
```

`--draft` works on dev.to (it creates a real unpublished draft) and is refused
by Hashnode and Telegraph, which have no draft concept on this path.

### Packets for the manual platforms

```bash
python3 -m common.runners.cli.publish \
  --kind article --text-file ./post.md --title "..." \
  --canonical "https://yourdomain.com/model-drift" \
  --link "https://dev.to/you/the-post" \
  --packets ./generated/syndication
```

Writes `packet-medium.md`, `packet-hackernoon.md`, `packet-habr.md`,
`packet-vc.md`, `packet-dzen.md`, each carrying the content slots, the canonical
instruction for that platform, the submission steps and the caveats. Pass the
dev.to URL as `--link` so the Medium packet names what to import.

---

## Adapt per platform — do not repost verbatim

One body sent unchanged to five platforms is exactly what those platforms
pessimise, and on Habr it will be actively downvoted. The packets say what each
audience wants; the rewriting is a job for the text skills:

| Platform | Adaptation |
|---|---|
| Habr | Depth, reproducible detail, sourced numbers. Strip every promotional line. `tone-shifter --to technical` |
| VC.ru | Lead with the business outcome. Postmortems and opinion travel; tutorials do not |
| Dzen | Simplify hard. Short paragraphs, concrete hook in the first two sentences. Reach is decided by first-hour click-through, so title and cover matter more than the body |
| HackerNoon | Lead with the finding, not the context. Editors reject anything reading as company-blog content |
| Medium | Little adaptation — the audience overlaps dev.to's |

---

## Credentials

```bash
DEVTO_API_KEY=...              # dev.to → Settings → Extensions → DEV Community API Keys
HASHNODE_TOKEN=...             # Hashnode → Account Settings → Developer → API tokens
HASHNODE_PUBLICATION_ID=...    # from your publication's dashboard URL
TELEGRAPH_ACCESS_TOKEN=...     # optional; one is minted on first use and printed
TUMBLR_ACCESS_TOKEN=...        # OAuth2 token from tumblr.com/oauth/apps
TUMBLR_BLOG_ID=...             # hostname, e.g. myblog.tumblr.com
QIITA_TOKEN=...                # Qiita → Settings → Applications, scope write_qiita
MICROPUB_ENDPOINT=...          # whatever your site publishes as rel="micropub"
MICROPUB_TOKEN=...             # from your IndieAuth token endpoint

# The static-blog source step
BLOG_CONTENT_DIR=...           # e.g. ~/blog/content/posts
BLOG_URL_PATTERN=...           # e.g. https://you.dev/posts/{slug}/
BLOG_FILENAME_PATTERN=...      # default {slug}.md; Jekyll needs the date
```

Telegraph is the only publisher in the collection that needs no credential at
all. When none is set it creates a throwaway account and prints the token — save
it, or the page stays live but becomes uneditable from this machine.
