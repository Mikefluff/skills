# reel-recut — calibration

One real session.

## Example 1 — 22 raw clips to a 17-reel series

### User says

> There are promo clips in this folder but they are unfinished: no b-roll, no pop-up graphics, no subtitles, and a couple are repeats. Pick the best take, re-edit them properly so they can go on Instagram, with nice covers.

### Before

22 vertical clips, 1080x1920, a presenter talking to camera for 25-45 seconds each. One static framing per clip. Clips open with "next topic". Four of them are the same introduction.

### Take decisions

`reel_recut takes --words words/` and a read of the transcripts gave:

| Clips | Decision |
|---|---|
| Introduction, four takes | The one full take at 1080p. Two were fragments, one was 360p |
| Two takes of the "$3000" topic | The longer; the shorter was its first half |
| Two takes of "five red flags" | The longer, same reason |
| "Family reunion" | One take, but "let's go through the main points" said twice: cut 11.55-14.95 |
| "A child born here" | Ends mid-thought. Closed with a 4.6 s tail, wording flagged for the user |

17 reels.

### One episode of the plan

```json
{
  "n": 2, "src": "src/v04.mp4", "words": "words/v04.json", "slug": "02-what-the-3000-pays-for",
  "framing": "steps", "face": [0.50, 0.38],
  "cover": {"lines": ["What are you", "paying", "*$3000 for?*"], "t": 1.6},
  "hook": ["WHAT ARE YOU PAYING", "$3000 for?"],
  "items": [
    {"kind": "big", "at": [2.5, 4.8], "text": "$3 000", "sub": "for paperwork", "style": "warn"},
    {"kind": "vs", "at": [5.5, 10.2], "second": 7.2, "text": ["Official fees", "The agent's price"], "style": ["ok", "warn"]},
    {"kind": "broll", "at": [11.0, 13.7], "asset": "assets/calculator.png"},
    {"kind": "chip", "at": [11.2, 13.7], "text": "Where does the difference go?", "style": "ask"},
    {"kind": "broll", "at": [13.9, 17.0], "asset": "assets/counter.mp4"},
    {"kind": "panel", "at": [33.6, 37.8], "title": "Ask before you pay",
     "rows": [[34.9, "A contract"], [35.7, "An estimate"], [36.2, "The list of official fees"]], "style": "check"},
    {"kind": "chip", "at": [38.0, 43.0], "text": "Tell us in the comments what you paid", "style": "comment"}
  ]
}
```

### Commands

```bash
python3 -m common.runners.cli.reel_recut check --plan-file plan.json
python3 -m common.runners.cli.reel_recut build --plan-file plan.json --preview
python3 -m common.runners.cli.reel_recut sheet --plan-file plan.json
python3 -m common.runners.cli.reel_recut build --plan-file plan.json --only 4 14
python3 -m common.runners.cli.reel_recut build --plan-file plan.json
```

### What the review caught

Each of these rendered without an error and was found on a contact sheet:

- two stacked pills overlapping after the type was enlarged;
- a generated still with the flag of another country behind the subjects;
- a tail that showed a frozen speaker where its cutaway should have been;
- a cover frame taken on a blink.

### After

17 reels of 27-43 seconds: a two-line hook, alternating wide and close framing, word-by-word captions, 4-8 graphics and 2-3 cutaways each, an end card with the site and the channel, a music bed under the voice, and 17 numbered covers. Eight cutaways were video and 25 were stills with a push, because the video providers ran out of balance part-way; the report said so.
