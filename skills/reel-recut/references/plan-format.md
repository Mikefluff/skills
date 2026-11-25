# plan.json

One file describes a whole series. Paths are relative to the plan file. Every time is a second on the ORIGINAL clip; the builder trims and then moves the times itself.

## Top level

```json
{
  "series": "Legalisation in Brazil",
  "out": "final",
  "work": "work",
  "brand": {
    "wordmark": ["floripa", ".info"],
    "colors": {"accent": "#ff6544", "second": "#19c2b8", "ink": "#0a1413"},
    "fonts": {"display": "brand/Unbounded.ttf", "text": "brand/Onest.ttf"},
    "caption_weight": 850
  },
  "end": {
    "art": "brand/sunset.svg",
    "tagline": ["A guide for people who live here", "Every entry has a source and a date"],
    "buttons": [{"text": "floripa.info"}, {"text": "t.me/floripa_ru", "icon": "tg"}],
    "seconds": 2.8
  },
  "music": {"file": "music/bed.mp3", "level": 0.2},
  "framing": {
    "steps": {"wide": [1.0, null], "close": [1.45, 660], "stack": [1.55, 440]}
  },
  "episodes": []
}
```

| Field | Meaning |
|---|---|
| `series` | Label on every cover, next to the episode number |
| `brand.wordmark` | Two parts; the second is drawn in the `second` colour |
| `brand.colors` | `accent` for warnings, highlights and the spoken word; `second` for confirmations; `ink` for dark plates and the panel |
| `brand.fonts` | TTF files, variable weight preferred. Omitted: the bundled Inter. Check that the font has the script the captions are in |
| `end` | The closing card. `art` is optional. The first button is drawn in `accent`. `icon` is `tg`, `link` or absent |
| `music` | Optional. `level` is the bed's gain under speech; it is ducked further by the voice and rises under the end card |
| `framing` | Named presets. Each mode is `[zoom, face_y]`: how far to punch in and the canvas row (px from the top) the face is held at. `null` keeps the source position. Unnamed modes fall back to `wide 1.0`, `close 1.35 @ 680`, `stack 1.45 @ 440` |

A preset per location is worth the minute it takes: a speaker who sits far from the camera needs `close` at 1.5-1.6, one who fills the frame already needs 1.2.

## Episode

```json
{
  "n": 4,
  "src": "src/v06.mp4",
  "words": "words/v06.json",
  "slug": "04-residence-is-not-citizenship",
  "framing": "steps",
  "face": [0.53, 0.40],
  "start": 3.1,
  "cuts": [[11.55, 14.95]],
  "word_fix": [[18.9, "CRNM"], [19.4, ""]],
  "cover": {"lines": ["Residence", "*≠*", "citizenship"], "t": 6.9},
  "hook": ["RESIDENCE ≠ CITIZENSHIP", "people mix them up"],
  "items": [],
  "tail": null
}
```

| Field | Meaning |
|---|---|
| `face` | Where the speaker's face is in the source frame, as fractions of width and height. Read it off a frame; every punch-in is centred on it |
| `start` | Trim everything before this second. It snaps into the nearest pause, so the second a word starts is close enough |
| `cuts` | Spans to remove, for a restart or a line said twice |
| `word_fix` | `[second, "text"]` replaces the word that starts at that second; an empty text drops it |
| `cover.lines` | Up to three lines; a line wrapped in `*` is drawn on an accent plate |
| `cover.t` | The second of the source the cover frame is taken from. Pick one with open eyes and a closed or smiling mouth |
| `hook` | Two lines shown for the first three seconds: the topic, then the tension |

## Items

Every item has `kind` and `at: [start, end]`.

| Kind | Fields | What appears |
|---|---|---|
| `chip` | `text`, `style` | One pill with an icon. Styles: `plain`, `ok`, `warn`, `ask`, `quote`, `loc`, `save`, `comment` |
| `big` | `text`, `sub`, `style` | A large number or amount, then its caption. Styles: `plain`, `ok`, `warn` |
| `vs` | `text: [top, bottom]`, `style: [top, bottom]`, `second` | Two pills stacked; the bottom one arrives at `second` |
| `tags` | `tags: [[t, text], ...]` | A row of white pills, each arriving at its own second |
| `url` | `text`, `sub` | An address bar with a padlock, then a caption |
| `broll` | `asset` | A cutaway over the speaker: a video is slowed to fill the span, a still gets a slow push |
| `panel` | `title`, `rows: [[t, text], ...]`, `style` | The screen splits: speaker above, a list below, each row arriving when it is said. Styles: `num`, `check`, `cross`, `flag` |

```json
{"kind": "big", "at": [2.5, 4.8], "text": "$3 000", "sub": "for paperwork", "style": "warn"},
{"kind": "vs", "at": [5.5, 10.2], "second": 7.2, "text": ["Official fees", "The agent's price"], "style": ["ok", "warn"]},
{"kind": "broll", "at": [13.9, 17.0], "asset": "assets/counter.mp4"},
{"kind": "panel", "at": [33.6, 37.8], "title": "Ask before you pay",
 "rows": [[34.9, "A contract"], [35.7, "An estimate"], [36.2, "The list of official fees"]], "style": "check"}
```

A cutaway whose span lies inside a panel fills only the top half, above the list. A panel with five rows, or with long ones, is set smaller automatically.

## Tail

For a clip that ends before its thought does. The picture goes to a cutaway and a panel with no speech under it, then the end card.

```json
"tail": {
  "seconds": 4.6,
  "title": "What the parents do",
  "rows": [[0.4, "Apply for their own residence"], [1.5, "On the grounds of family reunion"]],
  "style": "check",
  "asset": "assets/family.png"
}
```

Row times here are offsets from the start of the tail. The tail states something the speaker did not finish saying, so its wording is the user's to confirm.
