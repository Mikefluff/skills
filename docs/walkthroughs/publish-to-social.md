---
title: "Generate → publish (the last mile)"
persona: "Solo creator who already has the content and needs it posted"
time: "20 minutes first time, 2 minutes after"
skills:
  - post-publisher
  - carousel-builder
  - viral-text
---

# Generate → publish

Everything else in this collection ends at `./generated/`. This is the part that
sends it.

Two rules shape the whole workflow, and both exist because publishing cannot be
undone:

- **Dry-run is the default.** Without `--yes` nothing leaves your machine.
- **Consent does not fan out.** Even with `--yes`, each platform asks separately.

---

## Step 0 — connect one account (once)

Do this with Telegram first. It is the only platform with no OAuth, no app
review and no account-type requirement, which makes it the one place you can
prove the pipeline works before fighting anyone's developer portal.

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
2. Add the bot to your channel **as an administrator** with "Post messages" on.

```bash
skills-keys add TELEGRAM_BOT_TOKEN 123456:AA...
skills-keys add TELEGRAM_CHAT_ID @your_channel

post-publisher --list-platforms
```

```
Platforms:
  instagram    missing env: INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET [carousel, image, video · draft]
  linkedin     missing env: LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET [carousel, image, text, video]
  telegram     ready                                     [carousel, image, text, video]
  threads      missing env: THREADS_APP_ID, THREADS_APP_SECRET [carousel, image, text, video · draft]
  ...
```

A bot that is a member but not an admin is the commonest failure here, and it
shows up as `not enough rights` at publish time rather than in this list.

---

## Step 1 — a text post, end to end

```bash
post-publisher --kind text --text "Проверка связи." --platform telegram
```

```
DRY RUN — nothing will be sent. Add --yes to publish for real.

  → PUBLISH to telegram
    kind:  text
    text (15 chars):
      Проверка связи.

Dry run complete — 1 of 1 platform(s) would proceed (0 skipped, 0 blocked). Add --yes to publish.
```

Nothing happened. Add `--yes`:

```bash
post-publisher --kind text --text "Проверка связи." --platform telegram --yes
```

```
PUBLISH to telegram? [y/N] y
✓ telegram: published → https://t.me/your_channel/1
```

That is the whole contract. Everything below is the same three steps with more
platforms attached.

---

## Step 2 — a real carousel

```bash
/carousel-builder --topic "почему автопостинг ломается на последней миле" \
  --slides 8 --platform instagram --execute
```

Then hand the output directory over:

```bash
post-publisher ./generated/carousel/pochemu-avtoposting-lomaetsya/ \
  --platform telegram \
  --hashtags "smm,автопостинг" \
  --alt "Обложка" --alt "График срывов"
```

The caption comes from `captions.md` automatically. **Read what it extracted**
in the preview — that file is written by an agent, so its structure is a
convention rather than a guarantee. Override with `--text-file` if the parse is
wrong.

Preflight runs before anything is sent, and it knows the difference between a
Telegram text post (4096 chars) and a Telegram caption on media (1024):

```
    warn  alt_texts: 2 alt texts for 8 files — files 3-8 will go without
  → PUBLISH to telegram
    kind:  carousel
    media: slide-1.png  1.2 MB  alt="Обложка"
    ...
```

---

## Step 3 — add Instagram

Instagram needs three things Telegram did not: a Business or Creator account, a
registered app, and an S3 bucket. The bucket is not optional — Instagram fetches
media from a URL and never accepts uploaded bytes.

```bash
skills-keys add INSTAGRAM_APP_ID <app-id>
skills-keys add INSTAGRAM_APP_SECRET <app-secret>
skills-keys add S3_BUCKET my-bucket
skills-keys add S3_ACCESS_KEY ...
skills-keys add S3_SECRET_KEY ...

python3 -m common.runners.cli.auth --platform instagram
```

Full setup, per platform, including which scopes and which account type:
[`post-publisher/references/oauth-setup.md`](../../post-publisher/references/oauth-setup.md).

Then stage it rather than publishing it:

```bash
post-publisher ./generated/carousel/<slug>/ --platform instagram --draft --yes
```

```
✓ instagram: draft (id 17920...)
  container staged and processed, NOT posted. It expires in 24h.
  Publish it with: --platform instagram --publish-container 17920...
```

The container is real — the media has been uploaded, fetched and processed, so a
broken file fails here rather than at publish time. Nothing is public yet.

```bash
post-publisher --platform instagram --publish-container 17920... --yes
```

---

## Step 4 — fan out, and what happens when it does not fit

```bash
post-publisher ./generated/posts/ --platform telegram,threads,x --yes
```

```
✓ telegram: published → https://t.me/your_channel/412

    BLOCK text: 1180 chars exceeds the 500-char limit (over by 680)
✗ threads: 1 blocking issue(s) — not sent

    BLOCK text: 1180 chars exceeds the 280-char limit (over by 900)
✗ x: 1 blocking issue(s) — not sent

Published: 1 · skipped: 0 · failed: 2
```

This is the normal outcome of writing one caption for seven networks, and the
fix belongs upstream. Ask `viral-text` for a per-platform variant — the budgets
live in [`viral-text/references/platforms.md`](../../viral-text/references/platforms.md)
— and publish each with its own `--text-file`. The skill will not truncate to
make a bad fit look like a good one.

---

## Step 5 — re-running is safe

```bash
post-publisher ./generated/carousel/<slug>/ --platform telegram --yes
```

```
— telegram: skipped, identical content already published at 2026-08-01T09:14:00+00:00
  (https://t.me/your_channel/412). Use --force.
```

`posted.json` in the source directory records every success, keyed on platform
plus a hash of the content. Fix a typo in the caption and it counts as a new
post and goes through; re-run the same command and it does not.

---

## The platform that behaves differently

TikTok. Direct publishing requires passing TikTok's app audit, and until that
happens every direct post is forced to SELF_ONLY — **the API reports success and
nobody can see the post.** There is no error to catch.

So the recommended path is the inbox:

```bash
post-publisher ./generated/reel/<slug>/ --platform tiktok --draft --yes
```

```
✓ tiktok: draft (id v_pub_url~v2...)
  landed in the TikTok app inbox — open the app to caption and publish it
```

Without `--draft`, preflight says so before you commit to it.

---

## When the API cannot do it

An unaudited TikTok app, a personal Instagram account, a LinkedIn company page —
these are closed to the API, not merely inconvenient.
[`browser-fallback.md`](../../post-publisher/references/browser-fallback.md)
covers posting those by hand while keeping the receipt trail intact, so a later
API run does not double-post. Run the dry-run first even then: character limits
and file sizes do not stop mattering because the transport changed.

---

## Summary

| Step | Time | Result |
|---|---|---|
| Connect Telegram | 5 min | Whole pipeline provable, no OAuth |
| Text post | 1 min | Dry-run → `--yes` → live |
| Carousel from `./generated/` | 1 min | Caption auto-read, preflight enforced |
| Connect Instagram + S3 | 15 min | Business account, app, bucket |
| Everything after | ~30 s | One command per post |

Troubleshooting any platform error:
[`post-publisher/references/troubleshoot.md`](../../post-publisher/references/troubleshoot.md).
