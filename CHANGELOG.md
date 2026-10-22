# Changelog

All notable changes to this skill collection are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases are cut manually. Commit messages use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for clarity but no longer drive an automatic version bump — the previous `release.yml` GitHub Actions workflow was removed (was auto-tagging the wrong major bumps on additive commits).

## [Unreleased]

### Added

- **`motion-site`** (wrapper). Builds the motion-heavy web genre `impeccable` doesn't reach — WebGL hero, particle fields that morph, scroll-driven 3D, GLSL shader backgrounds, liquid glass — as running code, not a prompt. Two tiers chosen per effect (`webgl`: Three.js / R3F + GSAP ScrollTrigger + Lenis + GLSL; `light`: CSS / SVG / Framer Motion), two scopes (`section`, `page`), two targets (`html` self-contained via CDN import maps, `react` / R3F component files). Every build ships the `prefers-reduced-motion` and mobile fallbacks in the first pass. `motion-site audit <path>` is a read-only craft-floor check (fps, DPR, teardown, reduced-motion, a11y). No paid API. Composes with `impeccable` (which owns layout / typography / copy); distinct from `reel-builder` (video files, not interactive web).
- **reel-builder short films from one picture.** The SHORT prompt in `drama-system-prompt.md` writes a whole animated short to its end from an outline, in the trailer's plan shape, with story rules (the protagonist's own thread, a clock, plants and payoffs, couples' arcs, a continuity list, group blocking) and a dense sound design.
  - The bible's `master` picture is the source of every portrait, plate and group frame. A location's `refs` photos put the film in a real place.
  - Images through OpenAI `gpt-image-2.5-sunburst` with reference edits, with `fallback_provider` for frames a vendor's moderation refuses.
  - Seedance 2.5 on Atlas Cloud (`atlas-seedance-2-5`). References go inline, and portraits are registered as assets so the privacy filter passes the cast. A pinned first and last frame goes to image-to-video: generated transitions between shots (`bridge`, also from or to a still). `extend` continues a rendered shot. `extra_refs`, `no_keyframe`, `no_location_ref` and `no_previs` are per-shot answers to the vendor's copyright and video-edit filters.
  - Ensemble previs: every person in frame is a troll-proportioned figure with height, colour, hair and poses. Props move on `anim` keys. Rendered in Workbench with shadows, cavity and outlines.
  - The cut:
    - the clip's own voice is removed by contour with Mel-Band RoFormer (`audio-separator`), not ducked in time;
    - parts are whole frames of the film clock, so the picture never drifts from the sound;
    - `dip` and `iris` transitions, a per-shot `into`, a card's own `into`, and the film's `ending`;
    - the `candy` grade;
    - `reel_upscale` (Real-ESRGAN animevideov3, local) and `"hd"` cuts at 1080p;
    - a film that ends on its picture keeps its sound to the last card;
    - `--audio-only` lays a rebuilt sound on the picture already cut, refused (naming the shots) when the plan no longer makes it; parts are encoded once into `parts/` and joined by stream copy;
    - nothing kept is bought, priced or redone: the score survives a retime (keyed without section lengths, each section stretched in the mix), the confirmation prices only exchanges, vocals and sources not on disk, line takes are keyed by language too, split lines, shot sound and lengths are cached, the separator's model is in its file name, and the dialogue is mixed once per run even when the lines tighten the cut.
  - `_trailer_retime.insert` / `shift` put a shot into a cut and move the clock, the cards, the sound and the storyboard indices with it.
- **reel-builder: what the first short film taught, built in.**
  - `reel_insert --from inserts.json` puts shots into a cut, before, after or in place of another, including hand-cut pieces of a take. Frames, previs, vocals and continuity come along, the plan is validated, and the next commands are printed.
  - Before every paid confirmation, `reel`, `reel_board` and `reel_cast` list what they will buy and why: asked, missing, changed, failed last time. `--redo` warns when it would also render missing shots. `reel_board --mark-current` re-stamps drawn frames, and a frame's cache key is only what it looks like.
  - The previs checks its own framing: a cast head off the frame, cut by the edge in a close shot, or too small for the shot size is flagged in `previs/framing.json`, and `--auto-skip` lets the storyboard frame lead those shots.
  - `drama.preflight` turns off generated audio where a child speaks or someone sings, before Seedance's copyright filter refuses it.
  - The story check (`story-check-prompt.md`, `drama.screenplay_text`): a reader sees only the screenplay and names every object, rule or plan the story turns on without a setup, before anything is drawn. SHORT story rule 13, and `coverage` for an exchange shot as a wide plus close-ups.
  - `reel_listen` transcribes every line in the finished cut with a local Whisper and flags the ones that cannot be made out.
  - With `"hd"`, `reel` upscales each clip as it lands.
  - A cast member's `"voice_pitch"` (semitones) lifts their lines and vocals in the mix: a library child voice that comes out adult in a dialogue take sounds its age without a new voice slot.
  - `"voice_formant"` moves a voice's throat apart from its pitch, with a child EQ: an adult library "kid" voice becomes a child's timbre, not a higher-pitched adult (the first short's toddlers went from a hoarse man to 440-610 Hz children).
  - A line never leaves its shot: it starts on the mouth, and a take too long to end with its shot starts earlier rather than run onto the next face. The voice-performance prompt counts non-verbal reactions as seconds. In the first short 34 of 38 lines sit within 0.25 s of the mouth.
  - `reel_animatic --audio-only` remixes the sound onto the existing picture, and the picture is cut from cached parts: a change of one shot re-encodes that shot. The score is no longer bought again when a retime moves its sections, and only cache misses are priced.
  - `reel_insert` moves a shot's own sounds with it, drops them with a removed shot, and lays a new shot's `sounds` (with new `sources`) on the clock.
  - Every stage keeps its intermediate state: previs clips, board jpgs, bridge frames, upscaled copies, transcripts, vocals (keyed by voice and model) and refused vocals.
