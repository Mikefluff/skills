---
name: motion-site
description: "Build motion-rich websites and sections as running code: WebGL hero, particles, scroll-driven 3D, GLSL shader backgrounds, liquid glass (Three.js/R3F + GSAP + Lenis), plus a light CSS/Framer-Motion tier. Section or full page. The motion builder impeccable isn't. Use when: 'animated landing', 'particle hero', 'шейдерный фон', 'лендинг с анимацией'."
version: 1.0.0
user-invocable: true
argument-hint: "[brief] [--scope section|page] [--tier webgl|light|auto] [--target html|react|auto] [--effect <archetype>] [--ref <path|url>] [--variants N] [--preview] | audit <path>"
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Build the motion-heavy web genre that `impeccable` does not reach — WebGL hero
sections, particle fields that morph, scroll-driven 3D, GLSL shader backgrounds,
liquid glass, kinetic type — and ship it as **running code**, not a prompt and
not a spec. Output: real files (a self-contained HTML page, or React / R3F
component files for an existing project) that open and move, with the mandatory
reduced-motion and mobile fallbacks already wired.

Two tiers, chosen per effect:
- **webgl** — Three.js / React-Three-Fiber + GLSL + GSAP ScrollTrigger + Lenis.
  Particles, shaders, scroll-linked 3D cameras, transmission/glass, postprocessing.
- **light** — CSS / SVG / GSAP / Framer Motion. Scroll reveals, parallax, text
  kinetics, marquees, magnetic buttons, gradient-mesh backgrounds. No GPU scene.

Two scopes: a single **section** (hero / CTA / background / 3D viewer), or a full
**page** composed of motion sections over one smooth-scroll spine.

This skill does NOT:
- own layout, typography, information architecture, UX copy, or design systems —
  that is `impeccable`. motion-site drops the moving layer into a page impeccable
  shaped, or builds the motion page and hands typographic polish back to impeccable.
- render video files — that is `reel-builder` / `video-prompt` (those are not
  interactive and not web). motion-site output is live in a browser.
- call any paid API. It writes code and runs locally; there is nothing to bill.
</objective>

## ROLE

Read the brief → fix **scope** (section vs page), **tier** (webgl vs light),
**target** (html vs react), and the **effect archetype** → load the matching
technique reference plus the craft floor → build it bespoke → verify in one
bounded pass by eye → hand over running files and how to open them.

You are a creative WebGL/motion engineer, not a template vendor. The archetype
catalog is a vocabulary to pick a direction fast, then build for *this* brief —
never paste a canned demo.

## PIPELINE

1. **Read the brief.** Extract: scope, the effect(s) wanted, the vibe / brand /
   palette, the real content (copy, logo, product), and hard constraints —
   performance target, must-work-on-mobile, reduced-motion, existing stack.

2. **Detect the target.** Scan cwd: a `package.json` with `react` / `next` / a
   Vite React setup → `target: react`, and write components into that project's
   conventions. Otherwise → `target: html`, one self-contained file with CDN
   import maps. State the pick; `--target` overrides. See [references/stack.md](references/stack.md).

3. **Pick the tier.** Per effect, from [references/tier-picker.md](references/tier-picker.md). Use **webgl**
   only where it earns the GPU: particle fields, shader/fluid backgrounds, 3D
   models or characters, scroll-driven cameras, displacement, transmission glass.
   Use **light** for reveals, parallax, kinetic type, marquees, magnetic hovers,
   gradient mesh. State which tier and why; `--tier` overrides, `--no-3d` forces light.

4. **Pick the direction + load references.** Choose an archetype from the catalog
   in tier-picker.md, load its technique reference(s), and **always** load
   [references/craft-floor.md](references/craft-floor.md) and [references/stack.md](references/stack.md) before writing code.

5. **Build bespoke.** Wire the stack once (one renderer, one `requestAnimationFrame`
   loop), implement the effect for this brief, and wire the non-negotiables in the
   same pass: `prefers-reduced-motion` fallback, a low-end / mobile fallback,
   `dispose()` on unmount, DPR capped ≤ 2, offscreen canvas paused. The craft
   floor is not a later audit — it is built in now.

6. **Compose (page scope only).** Per [references/compose-page.md](references/compose-page.md): one smooth-scroll
   spine (Lenis), section rhythm (not every section is a canvas — quiet sections
   carry the loud ones), a single shared WebGL canvas behind the page where
   possible, and a loader that gates heavy assets without blocking first paint.

7. **Verify once, by eye.** Open / serve it. Watch for jank, layout shift, a
   stuck loader; confirm the reduced-motion path renders a real static state and
   the mobile fallback holds. Fix everything found in **one** batch, re-check at
   most once, then stop. No open-ended re-roll loop — name the frame to redo and
   redo that one. (See CONSTRAINTS.)

8. **Hand over.** Write to `./generated/motion-site/<slug>/` (or into the detected
   project after confirming). Report in two lines: tier · target · libraries with
   pinned versions · how to open it · what the user must still supply (real logo,
   glTF model, HDRI, fonts). See [references/run.md](references/run.md).

## MODES

- `motion-site <brief>` — build. Scope/tier/target inferred, stated, overridable.
- `motion-site <brief> --scope section|page` — one section, or a composed page.
- `motion-site <brief> --tier webgl|light|auto` — force the tier (`auto` default).
- `motion-site <brief> --target html|react|auto` — force the output format.
- `motion-site <brief> --effect <archetype>` — force a direction. Catalog:
  `particle-self` · `scroll-3d` · `fluid-gradient` · `aurora` · `liquid-glass` ·
  `metaball` · `noise-field` · `starfield` · `kinetic-type` · `marquee` ·
  `magnetic` · `sticky-gallery` · `image-distortion` · `3d-viewer` · `3d-character`.
- `motion-site <brief> --ref <path|url>` — match the vibe of a reference image or site.
- `motion-site <brief> --no-3d` — force the light tier.
- `motion-site <brief> --variants N` — N distinct directions of the same section (N ≤ 3).
- `motion-site <brief> --preview` — also open / serve it (or publish as an artifact) so you can see it move.
- `motion-site audit <path>` — read-only craft-floor check of existing motion / WebGL code (perf, dispose, DPR, reduced-motion, a11y). Produces a report, changes nothing. See [references/craft-floor.md](references/craft-floor.md).

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/stack.md](references/stack.md) | Always at build — stack wiring for both targets, CDN import maps, Lenis↔GSAP↔ScrollTrigger sync, version pinning |
| [references/tier-picker.md](references/tier-picker.md) | Always at step 3 — webgl-vs-light rules + the archetype catalog (direction → tier → which reference) |
| [references/craft-floor.md](references/craft-floor.md) | Always before writing code, and for `audit` — perf budget, dispose, DPR, reduced-motion, mobile, a11y, the absolute bans |
| [references/scroll-3d.md](references/scroll-3d.md) | Scroll-driven 3D — camera rigs, section pinning, scroll-linked timelines, the `particle-self` scroll pattern |
| [references/particles.md](references/particles.md) | Particle systems — instanced points, GPGPU/FBO simulation, shape-morph, mouse repulsion, point shaders |
| [references/shaders.md](references/shaders.md) | GLSL — fragment-shader backgrounds (gradient flow, noise, fluid, metaballs), vertex displacement, fresnel, uniforms, `shaderMaterial` wiring |
| [references/materials-3d.md](references/materials-3d.md) | 3D models / characters / liquid glass — glTF + draco, HDRI env, `MeshTransmissionMaterial`, distortion, model perf |
| [references/postprocessing.md](references/postprocessing.md) | Bloom · chromatic aberration · DOF · grain · god rays — EffectComposer / @react-three/postprocessing budgets |
| [references/light-motion.md](references/light-motion.md) | The light tier — GSAP reveals, SplitText kinetics, parallax, marquee, magnetic, sticky gallery, SVG draw/morph, gradient mesh, Framer Motion, CSS scroll-driven animations, View Transitions |
| [references/compose-page.md](references/compose-page.md) | Scope `page` — smooth-scroll spine, section rhythm, one shared canvas, loader/preload, scroll performance |
| [references/run.md](references/run.md) | Preview / handover — serve the HTML or publish as an artifact, run the React dev server, the audit report shape |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — calibration pairs: a vague "animated hero"
brief resolved into a tiered build decision, a particle-self morph, a scroll-3D
section, a fluid-gradient background, a light-tier kinetic-type hero, and an
`audit` finding list.

## CONSTRAINTS

- **The craft floor is built in, not bolted on.** Every build ships, in the first
  pass: a real `prefers-reduced-motion` static state (not a frozen first frame — a
  composed still), a mobile / low-end fallback (heavy WebGL downgrades to a poster
  or the light tier on small screens and `Save-Data`), `dispose()` of geometries /
  materials / textures / renderer on unmount, DPR capped at `min(devicePixelRatio, 2)`,
  one shared `requestAnimationFrame` loop, and the canvas paused when offscreen
  (`IntersectionObserver`). No seizure-risk flashing (> 3 Hz high-contrast). See
  [references/craft-floor.md](references/craft-floor.md).
- **Verify in bounded passes, not a loop.** Build fully, inspect once by eye, fix
  everything that pass shows in one batch, confirm with at most one more look, then
  stop. Open-ended self-QA burns time doing worse what one honest look does. When a
  specific frame or section is wrong, redo that one — do not re-roll the whole build.
- **Motion serves the brief.** Pick the quietest technique that lands the effect.
  A CSS gradient and a blur can beat a GPGPU fluid sim; reach for the GPU only when
  the effect needs it. Don't make every section a canvas.
- **Don't duplicate impeccable.** No design-system extraction, critique scoring, or
  typographic playbooks here — that is impeccable's. motion-site owns the moving
  layer and the motion-page composition. If the brief is really a layout / copy /
  IA request with no motion genre in it, say so and route to impeccable.
- **Pin versions; load from allowed CDNs only.** HTML target loads from cdnjs,
  jsdelivr, or unpkg at an exact pinned version (≥ 2 weeks old). Never a bare
  `three` or `three@0`. See [references/stack.md](references/stack.md).
- **Real content, honest placeholders.** Use the user's copy / logo / product when
  given. For assets they must supply (glTF, HDRI, licensed fonts), wire a labeled
  placeholder and list it in the handover — never ship a broken import.
- **Output stays in one place.** `./generated/motion-site/<slug>/` by default; write
  into the user's project only after confirming. No scattered one-off helper scripts.

## INVOCATION HINTS

Use this skill when the user says any of:
- "animated / motion landing page", "make the site move", "awwwards-style site"
- "particle hero", "particles that form a logo / shape", "particle background"
- "scroll-driven 3D", "3D that moves as you scroll", "pin the section and animate"
- "shader background", "fluid / gradient / noise / aurora background", "metaballs"
- "liquid glass", "glassmorphism that refracts", "transmission material"
- "3D product viewer", "spin the model", "glTF on the page", "3D character"
- "kinetic typography", "text that animates / splits / reveals on scroll"
- "smooth scroll", "Lenis", "GSAP ScrollTrigger site", "sticky scroll gallery"
- "magnetic buttons", "marquee", "image distortion gallery", "WebGL hero"
- "audit this WebGL / Three.js / motion code for performance"

RU triggers (use the skill when the user writes any of):
- «анимированный лендинг», «оживи сайт», «сайт как на awwwards», «лендинг с анимацией»
- «партикловый hero», «частицы собираются в логотип / фигуру», «фон из частиц»
- «скролл-3D», «3D крутится при скролле», «запинь секцию и анимируй»
- «шейдерный фон», «флюид / градиентный / нойз / aurora фон», «метаболлы»
- «жидкое стекло», «стекло которое преломляет», «transmission материал»
- «3D-вьювер товара», «покрути модель», «glTF на странице», «3D-персонаж»
- «кинетическая типографика», «текст анимируется / разбивается при скролле»
- «плавный скролл», «Lenis», «сайт на GSAP ScrollTrigger», «липкая галерея»
- «магнитные кнопки», «бегущая строка», «галерея с искажением», «WebGL hero»
- «проверь этот WebGL / Three.js код на производительность»

For a layout, copy, IA, or static-design request with no motion genre — use
`impeccable`. For a video file — use `reel-builder`. motion-site is for code that
moves in the browser.
