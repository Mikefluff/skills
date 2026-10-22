# Craft floor & bans

The quality and safety floor. Built into the first pass, never bolted on later.
This is also the checklist `motion-site audit` runs against existing code.

## Performance budget

- **60 fps target, 30 fps floor.** If the effect can't hold 30 on a mid phone,
  cut particle count / resolution / postprocessing until it can, or drop to light.
- **One `requestAnimationFrame` loop.** One renderer, one tick. In R3F, `useFrame`
  is that loop — never spawn a second rAF. Lenis is driven by GSAP's ticker, not a
  second rAF (stack.md). Two loops = double work + scroll double-stepping.
- **Cap DPR at `min(window.devicePixelRatio, 2)`.** Retina at 3× quadruples fragment
  work for no visible gain. In R3F: `dpr={[1, 2]}`.
- **Pause when offscreen.** `IntersectionObserver` on the canvas → stop ticking when
  it leaves the viewport. In R3F use `frameloop="demand"` or toggle on intersection.
- **Resize is throttled**, and the renderer + camera aspect + composer update together.
- **Shaders:** keep fragment work cheap. FBM ≤ 4–5 octaves for a background. Avoid
  branching and `pow()` in hot loops where a cheaper curve does. Prefer a render
  target at reduced resolution for full-screen sims, upscaled on draw.
- **Geometry:** instance repeated meshes (`InstancedMesh`), merge static geometry,
  keep draw calls low. Points for particle fields, not thousands of meshes.
- **Textures:** power-of-two or let three mip; compress (KTX2/basis) for 3D models;
  cap texture size to what the screen shows.

## Teardown (the leak that kills SPAs)

On unmount / route change / variant swap, dispose everything the GPU holds:

```js
function dispose(root) {
  root.traverse((o) => {
    o.geometry?.dispose()
    const m = o.material
    if (Array.isArray(m)) m.forEach(disposeMat); else disposeMat(m)
  })
  renderer.dispose()
  renderer.forceContextLoss?.()
}
function disposeMat(m) {
  if (!m) return
  for (const k in m) { const v = m[k]; if (v && v.isTexture) v.dispose() }
  m.dispose()
}
```

R3F disposes scene objects on unmount automatically, but **you** must dispose
things you created outside the tree (render targets, FBOs, manually-made textures),
and remove GSAP/ScrollTrigger instances: `ScrollTrigger.getAll().forEach(t => t.kill())`
and `lenis.destroy()`.

## Accessibility & safety — non-negotiable

- **`prefers-reduced-motion: reduce` → a real static state.** Not a frozen first
  frame. Compose a deliberate still: final particle shape assembled, gradient at a
  chosen phase, 3D at a hero pose. Gate motion init behind the query:

  ```js
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce) { renderStaticPoster(); return } // no rAF, no scroll animation
  ```

- **Motion is never required to understand or use the page.** Content, nav, and CTAs
  work with JS/WebGL off or failed. WebGL context-loss and init failure fall back to
  the static poster, not a blank canvas. Check `canvas.getContext('webgl2')` exists.
- **No seizure risk.** No high-contrast full-screen flashing above ~3 Hz; no rapid
  red flashes. Keep luminance oscillation gentle.
- **Focus & input.** Pointer-driven effects must not trap keyboard users or hijack
  scroll (Lenis still allows native anchor jumps and reduced-motion). Interactive 3D
  controls get a visible focus path or a non-3D equivalent.
- **LCP is not a canvas.** The largest text / hero copy paints as HTML immediately;
  the canvas mounts behind or after it. Never block first contentful paint on three
  loading. Show text, then enhance.

## Mobile / low-end fallback

- Heavy webgl effects detect small screens and `Save-Data` / low memory and either
  (a) drop particle count & resolution hard, or (b) render the light-tier or static
  poster instead. Decide this at init, not mid-scroll.

  ```js
  const weak = matchMedia('(max-width: 768px)').matches
    || navigator.connection?.saveData
    || (navigator.deviceMemory && navigator.deviceMemory <= 4)
  ```

- Don't autoplay a GPGPU fluid sim on a phone. A pre-baked video poster or the CSS
  gradient is the honest fallback.

## Absolute bans

- No second rAF loop. No uncapped DPR. No effect without a reduced-motion state.
- No WebGL on the critical render path blocking LCP.
- No undisposed render targets / textures / ScrollTriggers on teardown.
- No bare / major-only CDN version (`three`, `three@0`); exact pinned patch only.
- No seizure-risk flashing. No motion required to read or operate the page.
- No scattered one-off helper scripts in the user's tree; output to one folder.

## `audit <path>` report shape

Read the file(s), check each item above, and report:

```
motion-site audit — <path>
  fps risk:        <particle count / shader cost / draw calls> — <ok | over budget: …>
  rAF loops:       <1 | N found → leak/jank>
  DPR cap:         <ok | uncapped>
  offscreen pause: <yes | no>
  teardown:        <disposes geo/mat/tex/targets + kills ScrollTrigger/Lenis | leaks: …>
  reduced-motion:  <static state present | MISSING>
  mobile fallback: <present | MISSING>
  a11y:            <content works without motion | motion required: …>
  LCP:             <text-first | blocked by canvas>
  versions:        <pinned | bare/major-only: …>
Ranked fixes: 1) … 2) … 3) …
```

Changes nothing — report only.
