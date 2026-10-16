# Drama mode — a series of dialogue films, from an idea to a checked episode

Drama mode makes long narrative video: episodes of 8-12 minutes, built from 15-second Seedance 2.5 scenes in which several characters speak in the series' language and Seedance voices them. Episodes of one series share a cast, places and a director, so the second episode costs one sentence of direction.

Everything runs in this repo. The agent that runs the skill writes the story and the prompts, Nano Banana Pro draws the faces and places, Seedance renders the scenes, and ElevenLabs Scribe with a Gemini critic checks the result. No web interface, no image service in a browser, no downloads by hand.

```
<series>/
  bible.json          SERIES call: language, look, cast, locations, episode outlines
  director.md         DIRECTOR call: rules that extend directors/base.md
  cast/<id>.png       reel_cast: one judged portrait per character
  cast/<id>.mp3       reel_cast: a 7 s voice per speaking character (ElevenLabs voice design)
  locations/<id>.png  reel_cast: one judged plate per place and state
  cast.json           what was rendered from which description (reuse across episodes)
  ep01/
    plan.json         EPISODE call, then reel_cast composes each scene's prompt
    shots/            reel: one clip per scene
    final.mp4         reel: the episode with its own dialogue (+ score, if planned)
    check.json        reel_check: speech and faces per scene
```

## The sequence

| Step | Run | Look at before going on | Cost |
|---|---|---|---|
| 0. Research (optional) | `research-brief` on what gets views in this genre and language: titles, hooks, lengths | the brief | — |
| 1. Series | ONE Agent with SERIES from [`drama-system-prompt.md`](../../../common/video-prompt-library/drama-system-prompt.md) → `bible.json` | cast, wants, episode events | — |
| 2. Director | ONE Agent with DIRECTOR + `directors/base.md` → `director.md` | 5-15 rules, each checkable on a shot | — |
| 3. Episode | ONE Agent with EPISODE + `drama.director("<series>/director.md")` → `ep01/plan.json` | beats, every line in its shot | — |
| 4. Cast | `python3 -m common.runners.cli.reel_cast --plan-file <series>/ep01/plan.json` | `cast/`, `locations/`: faces right, weather right for its scenes | ≈ $0.14 per asset, up to 3 tries |
| 5. Price | `python3 -m common.runners.cli.reel --plan-file <series>/ep01/plan.json --cost-only` | the total | — |
| 6. One scene | `reel --plan-file <series>/ep01/plan.json --redo sc01 --yes` then `reel_check --only sc01` | the scene, and whether its speech passed | one scene |
| 7. Episode | `python3 -m common.runners.cli.reel --plan-file <series>/ep01/plan.json --resume --yes` | `final.mp4` | see below |
| 8. Check | `python3 -m common.runners.cli.reel_check --plan-file <series>/ep01/plan.json` | `check.json`; it prints the `--redo` line | ≈ $0.01 per scene |
| 9. Re-render | the printed `reel ... --redo sc03,sc07`, then `reel_check --only sc03,sc07` | until it prints nothing to redo | per scene |

Step 6 is the director's test: render one scene, watch it, and change the director's rules before 40 scenes are paid for. A rule changed after step 3 needs the EPISODE call again; a scene changed by hand needs only `reel_cast` (it re-composes prompts and renders nothing new).

The next episode: run EPISODE with the next outline and the previous episode's last two scenes, into `ep02/plan.json`, then steps 4-9. `reel_cast` reuses every face and place whose description has not changed.

## What it costs

Seedance 2.5 bills tokens: seconds × width × height × 24 / 1024, $10.70 per million on BytePlus and OpenRouter. One 15-second 16:9 scene is about $1.54 at 480p and $3.47 at 720p. A 10-minute episode, 40 scenes, is about $62 at 480p and $139 at 720p, before re-renders. Every scene `reel_check` sends back costs the same again. Run `--cost-only` for the exact figure; it reads each scene's own length and resolution.

## Speech: what is known, what is measured

What the sources say, as of 2026-10-15:

- **Languages.** BytePlus says only "10+ languages" ([product page](https://www.byteplus.com/en/product/modelark)), and its docs pages render no text for a fetcher. The eleven most often listed are Chinese, English, Spanish, Indonesian, Malay, Thai, Arabic, Portuguese, Vietnamese, Japanese and Korean ([OrcaRouter](https://www.orcarouter.ai/blog/seedance-2-5), which gives no source).
- **Per-language scores exist only for 2.0.** The [Seedance 2.0 report](https://arxiv.org/abs/2604.14148), Table 20, rates image-to-video on a 1-5 scale. Audio prompt following, meaning the model says the words it was asked for, scored English 4.20, Indonesian 4.14, Spanish 4.00, Portuguese 3.63, Korean 3.38 and Japanese 3.13. Thai, Arabic, Vietnamese and Malay were not scored. The report names "lip-sync errors in multi-speaker scenes" and audio distortion as open problems.
- **2.5 says the words far more accurately but holds a voice less closely.** In an independent benchmark ([ORAV](https://arxiv.org/html/2609.34843v1), Table 3), 2.5 has 5.5 % word and character error rate against 16-19 % for 2.0. Its cosine similarity to a reference voice is 0.45, against 0.48 for 2.0 and 0.59 for MiniMax-H3. No language list or lip-sync score for 2.5 is published.
- **Voice references carry identity; they are not a copy.** In a two-speaker test, giving each speaker their own `@Audio` voice, about 7 s each so the total stayed under 15 s, mapped the voices correctly to two named speakers. Without an instruction, the sample's room and microphone carried into the scene ([Genflick](https://genflick.com/blog/seedance-voice-consistency-audio-reference-2026-05-03)).
- **Two speakers in one shot** sometimes get each other's lines ([videoai.me](https://videoai.me/blog/seedance-2-0-dialogue-prompts)), so base rule 9 gives each line its own shot.

What the pipeline does with it:

- **A voice per character, once per series.** For a character with `voice_text`, ElevenLabs designs a voice from its `voice` description, and the sample is cut to 7 s (`cast/<id>.mp3`). Every scene the character speaks in carries it as `@Audio`, with the line "use it only for timbre, accent and pace; do not copy its room". Given 2.5's weaker voice matching, this narrows the drift between scenes but does not remove it.
- **The 2.5 dialogue syntax.** `Dialogue language: Thai.` comes before the lines, then `Malai says (…): {…}` per line, sound effects in `<>`, and "No music".
- **The words are measured, not trusted.** `reel_check` transcribes the part of each scene the edit uses with ElevenLabs Scribe, in the bible's language, and compares it with the script letter by letter, because Thai, Japanese and Chinese write no spaces. A scene where less than 0.8 of the script is heard is re-rendered.
- **When the same scene fails twice, the line is the problem.** Shorten it (base rule 9), give it its own close-up, or move the second speaker's line to the next scene.
- **A language that fails on most scenes** is one Seedance does not voice well. Pick another language for the series, or voice it outside the scene with film mode: an ElevenLabs take, with Seedance lip-syncing to it.

On the OpenRouter route, voice references need a public URL. Either set `"media_host": "litterbox"` in the plan to allow uploading them for an hour, or render on `seedance-2-5` (BytePlus), which takes the files inline.

## Faces

- A scene sends its speakers' portraits and its place as references, and the runner writes the line that says which Image is whom. The chain never counts images.
- Seedance rejects a reference or keyframe with a photoreal face it takes for a real person (`InputImageSensitiveContentDetected.PrivacyInformation`), and the whole scene fails. A generated face is not exempt: a Nano Banana keyframe tripped it in the first film-mode trial. When a scene fails with it, re-roll that portrait with `reel_cast --only <id>`; a look with a light painterly or animated rendering avoids the gate entirely. Extras never show sharp faces (base rule 16).
- `reel_check` scores identity against the portraits and flags a character doubled in one frame or subtitles burnt in. Both are common Seedance failures.

## Score and sound

The scene's own sound is the dialogue and diegetic noise; base rule 13 keeps music out of it, so the score can be laid over without fighting a second one. A `music` block in the plan (as in an ordinary reel, `--music-provider eleven-music` for an instrumental) is mixed under the dialogue and ducked whenever someone speaks. With no music block the episode keeps exactly the sound Seedance made.

## Directors

`common/video-prompt-library/directors/base.md` holds 24 rules for long narrative YouTube film. A series director extends it and states only what changes: `extends: base`, one sentence of style, then rules. A base number replaces that rule, 101 and up add new ones. A director can be reused across series by copying it into `directors/<id>.md` and extending it by id.

Why rules and not a style adjective: "shoot it like a thriller" gives the model nothing it can execute, while "average shot 2 s, hand-held on 24 mm, hard cut on every line" does. The DIRECTOR prompt rejects any rule a camera cannot carry out.
