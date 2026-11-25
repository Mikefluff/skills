# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Chrome or Chromium not found` | The graphics are rendered by a headless browser | Install Chrome, or set `$CHROME` to a Chromium binary |
| A graphic is missing or blank | Chrome exited before writing the PNG, and an empty file was cached | Delete `work/png/` and rebuild |
| Captions render as boxes | The text font lacks the script | Point `brand.fonts.text` at a font that covers it |
| Captions are thin | The font is static, so `caption_weight` has nothing to move | Use a variable font, or a bold static cut |
| The tail shows a frozen speaker and no cutaway | The cutaway asset is missing, or shorter than 0.6 s | Run `check`; it names the missing file |
| A caption sits on the face | `face` is wrong for this clip | Read the face position off a frame again; adjust the preset's `face_y` |
| The punch-in crops the head | `close` zoom too high for a speaker near the camera | A preset for that location with a lower zoom |
| The opener trim clips a word | `start` is inside a word with no pause before it | Move `start` earlier, to the previous pause |
| A removed pause sounds abrupt | Two cuts landed close together | Remove one from `cuts`; the automatic tightening keeps air on both sides |
| The cover frame has closed eyes | `cover.t` landed on a blink | Try half a second either side, then `covers --only N` |
| The first build is slow | Every graphic is rendered once and cached by its content | Later builds reuse `work/png/`; only changed graphics are redrawn |
| Music is three seconds long | The provider's duration flag is in seconds | Generate 60 s; the builder loops and trims it |
| `transcribe --words` returns no `words` | The format is not `verbose_json` | `--format verbose_json --words` |
| Source folder has unreadable (mojibake) names | A messenger exported them | Copy the clips to `src/` under simple names first |
