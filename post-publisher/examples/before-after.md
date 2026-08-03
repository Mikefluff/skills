# Calibration runs

Three runs showing what the skill prints and where it stops. All three begin
in dry-run, because that is the default.

---

## 1. An 8-slide carousel to Instagram, as a draft

**Input** — a finished `carousel-builder` directory:

```
./generated/carousel/pochemu-avtoposting-lomaetsya/
  slide-1.png … slide-8.png
  captions.md
  manifest.json
```

**Command**

```bash
post-publisher ./generated/carousel/pochemu-avtoposting-lomaetsya/ \
  --platform instagram --draft \
  --hashtags "smm,автопостинг,контент" \
  --alt "Обложка: заголовок на тёмном фоне" --alt "График срывов публикаций"
```

**Output**

```
DRY RUN — nothing will be sent. Add --yes to publish for real.

    warn  alt_texts: 2 alt texts for 8 files — files 3-8 will go without
  → DRAFT to instagram
    kind:  carousel
    text (312 chars):
      Автопостинг ломается не на генерации, а на последней миле.
      Разобрали восемь мест, где это происходит.
      
      #smm #автопостинг #контент
    media: slide-1.png  1.2 MB  alt="Обложка: заголовок на тёмном фоне"
    media: slide-2.png  1.1 MB  alt="График срывов публикаций"
    media: slide-3.png  1.3 MB  (no alt)
    …
    media: slide-8.png  1.2 MB  (no alt)

Dry run complete — 1 of 1 platform(s) would proceed (0 skipped, 0 blocked). Add --yes to publish.
```

Two things to read here. The caption came from `captions.md` — check it, because
that file is written by an agent and its shape is a convention. And the alt-text
warning is real: eight slides, two alts.

**Then, for real:**

```bash
post-publisher ./generated/carousel/pochemu-avtoposting-lomaetsya/ \
  --platform instagram --draft --yes ...
```

```
Create draft on instagram? [y/N] y
✓ instagram: draft (id 17920...)
  container staged and processed, NOT posted. It expires in 24h.
  Publish it with: --platform instagram --publish-container 17920...

Published: 0 · skipped: 0 · failed: 0
Receipt: ./generated/carousel/pochemu-avtoposting-lomaetsya/posted.json
```

The container is real: the media has been fetched and processed, so a broken
file would have failed here rather than at publish time. Nothing is public yet.

---

## 2. A reel to TikTok's inbox

**Command**

```bash
post-publisher ./generated/reel/kak-my-slomali-ochered/ --platform tiktok --draft --yes
```

**Output**

```
  → DRAFT to tiktok
    kind:  video
    text (88 chars):
      Три недели чинили очередь публикаций. Рассказываем, что было не так.
    media: final.mp4  24.3 MB  (no alt)

Create draft on tiktok? [y/N] y
✓ tiktok: draft (id v_pub_url~v2...)
  landed in the TikTok app inbox — open the app to caption and publish it
```

Without `--draft` the same command adds a warning first:

```
    warn  audit: direct publishing requires an audited TikTok app. Unaudited apps have
          every post forced to SELF_ONLY — it looks published and nobody sees it.
          Use --draft to land it in the app inbox instead, which always works.
```

That warning is the reason the inbox is the recommended path. The direct-post
call *succeeds* on an unaudited app — it simply produces a post only you can
see, and the API says nothing about it.

---

## 3. One text post to three platforms at once

This is the recurring real failure: a post drafted for Telegram's 4096
characters, then fanned out unchanged.

**Command**

```bash
post-publisher --kind text --text-file ./generated/posts/ocheredi.md \
  --platform telegram,threads,x --yes
```

**Output**

```
  → PUBLISH to telegram
    kind:  text
    text (1180 chars):
      Три недели мы чинили очередь публикаций, и в итоге выяснилось, что
      проблема была не в очереди.
      …

PUBLISH to telegram? [y/N] y
✓ telegram: published → https://t.me/mikefluff_channel/412

    BLOCK text: 1180 chars exceeds the 500-char limit (over by 680)
✗ threads: 1 blocking issue(s) — not sent

    BLOCK text: 1180 chars exceeds the 280-char limit (over by 900)
✗ x: 1 blocking issue(s) — not sent

Published: 1 · skipped: 0 · failed: 2
Receipt: ./generated/posts/posted.json
```

Four things this run demonstrates:

- **Each platform is confirmed separately.** One "yes" does not fan out to the
  rest.
- **A block on one platform does not stop the others.** Telegram went out;
  Threads and X were refused locally and never received a request.
- **Nothing partial was posted to the blocked platforms** — the check is local,
  so no truncated version leaked out.
- **Exit code is 1** because something failed, even though one post succeeded.

The fix is upstream, not here: ask `viral-text` for a per-platform variant
([`viral-text/references/platforms.md`](../../viral-text/references/platforms.md)
carries the budgets), then publish each with its own `--text-file`. Writing one
caption and hoping it fits all seven networks does not work, and this skill will
not silently truncate to make it look like it did.
