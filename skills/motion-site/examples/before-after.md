# Calibration pairs

How a brief resolves into a tier/target/direction decision and what the build ships.
These calibrate judgment — they are not templates to paste.

---

## 1. Vague brief → explicit build decision

**Brief:** "make my landing hero animated, it's an AI note-taking app."

**Resolution (state this before building):**
- scope: `section` (hero only — they said hero)
- target: `html` (no React project in cwd detected) → one self-contained file
- tier: `webgl` — "AI" + hero wants a GPU moment; direction `particle-self`: points
  drift, assemble into the app's glyph on load, repel from the cursor
- fallback wired in pass one: reduced-motion → points pre-assembled, still; mobile →
  15k points instead of 50k, no postprocessing
- handover names what they supply: the logo/glyph outline (SVG) to sample points from

One direction offered and built, not a four-option menu. Alternative noted in one
line: "a fluid-gradient background would be the quieter take."

---

## 2. `particle-self` morph (webgl / section)

**Brief:** "particles that form our logo, then float, react to mouse."

**Build shape:**
- `THREE.Points`, 50k, attributes `aScatter` (random sphere) + `aTarget` (sampled
  from the logo SVG rasterized to a canvas) + `aDelay`
- vertex shader: `mix(aScatter, aTarget, smoothstep(assemble))` with per-point delay
  so it ripples in; curl-noise drift after assembly; `uMouse` repulsion radius
- `uAssemble` eased 0→1 on load (GSAP), or scroll-linked if the brief said "on scroll"
- additive blending, round soft points, DPR ≤ 2
- reduced-motion: render the assembled shape once, no loop
**Ship:** `index.html`, `python3 -m http.server`, "you supply: logo.svg (I wired a
placeholder wordmark)."

---

## 3. `scroll-3d` section (webgl / section)

**Brief:** "the product model should rotate and zoom as you scroll."

**Build shape:**
- Lenis → GSAP ticker → ScrollTrigger (one spine)
- pinned `#hero`, `scrub: 1`, `end: '+=2000'`
- timeline tweens `camera.position.z` and `model.rotation.y` at labels 0 / 0.4 / 0.8
- values smoothed (lerp toward target in the loop); one rAF renders
- HDRI `Environment` for lighting; `ACESFilmicToneMapping`
- `invalidateOnRefresh` + `ScrollTrigger.refresh()` after model load
- reduced-motion: static hero render at the opening pose; mobile: static render
**Ship:** "you supply: product.glb (placeholder primitive wired)."

---

## 4. `fluid-gradient` background (webgl / section)

**Brief:** "a premium animated gradient behind the hero text."

**Build shape:**
- fullscreen plane, `ShaderMaterial`, domain-warped FBM (≤ 5 octaves), two brand
  colors mixed by `smoothstep`, gentle `uMouse` bias
- rendered to a ½-resolution target, upscaled — cheap
- text is HTML in front (LCP not blocked); canvas is `position:fixed` behind
- reduced-motion: freeze at a chosen `uTime`; this is cheap enough to keep on mobile
  at lower resolution
**Ship:** complete, nothing to supply.

---

## 5. Light-tier `kinetic-type` hero (light / section)

**Brief:** "editorial agency, headline that reveals dramatically on load." No 3D in it.

**Resolution:** tier `light` — a shader here would be overkill; `SplitText` + mask
reveal lands it. No canvas, no teardown cost, reduced-motion trivial.

**Build shape:**
- `SplitText` into lines+chars, lines wrapped in `overflow:hidden`
- chars `yPercent: 120 → 0`, stagger 0.02, `back.out(1.6)` on load; lines mask-reveal
- a magnetic CTA (pointer-fine guard) + a velocity-reactive marquee strip below
- CSS holds the initial hidden state so a JS failure doesn't lose the headline
- reduced-motion: everything renders in place, no animation
**Ship:** complete. Note: "impeccable owns the type scale/spacing; I matched it."

---

## 6. `audit` finding list (read-only)

**Brief:** "audit this Three.js hero for performance" → `motion-site audit hero.js`

**Output (changes nothing):**
```
motion-site audit — hero.js
  fps risk:        90k points + UnrealBloom at DPR 3 — over budget on mobile
  rAF loops:       2 found (Lenis has its own rAF AND gsap.ticker drives it) → scroll double-steps
  DPR cap:         uncapped (renderer.setPixelRatio(devicePixelRatio))
  offscreen pause: no
  teardown:        renderer.dispose present; render target + ScrollTriggers leak on unmount
  reduced-motion:  MISSING
  mobile fallback: MISSING
  a11y:            ok — content is HTML in front
  LCP:             text-first ok
  versions:        three pinned; gsap loaded as "gsap@3" (major-only)
Ranked fixes:
  1) Remove the second Lenis rAF — drive it only from gsap.ticker.
  2) Cap DPR at min(dpr,2); drop points to 20k and gate bloom off < 768px.
  3) Add a prefers-reduced-motion static poster; dispose the render target + kill ScrollTriggers on unmount.
  4) Pin gsap to an exact patch.
```
