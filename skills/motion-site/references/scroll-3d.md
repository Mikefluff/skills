# Scroll-driven 3D

Tie a 3D scene to scroll position: camera dolly, object rotation, pinned reveals,
staged timelines. The genre motionsites.ai calls "Scroll-Driven 3D".

## The spine

Scroll → Lenis → GSAP ticker → ScrollTrigger (stack.md). Then drive the scene from
a **scroll progress value**, not from raw scroll pixels, so it is resolution- and
device-independent.

Two ways to link scene to scroll:

**A. ScrollTrigger `scrub` timeline** — best for choreographed, reversible motion.

```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#hero',
    start: 'top top',
    end: '+=2000',      // scroll distance the animation spans
    scrub: 1,           // 1s catch-up; ties playhead to scroll
    pin: true,          // hold the section while it plays
  }
})
tl.to(camera.position, { z: 2, ease: 'none' }, 0)
  .to(model.rotation, { y: Math.PI, ease: 'none' }, 0)
  .to(model.position, { y: 0.5 }, 0.3)
```

Animate plain objects (`camera.position`, `mesh.rotation`); the render loop reads
their current values each frame. Don't `renderer.render()` inside the tween — your
one rAF loop already does.

**B. A progress uniform / ref** — best for continuous, shader-linked motion.

```js
let progress = 0
ScrollTrigger.create({
  trigger: '#hero', start: 'top top', end: '+=2000', scrub: true,
  onUpdate: (self) => { progress = self.progress },  // 0 → 1
})
// in the rAF loop: uniforms.uProgress.value = progress  (or lerp toward it)
```

In R3F, read scroll with drei's `<ScrollControls>` + `useScroll()` (`scroll.offset`,
`scroll.range(start, len)`, `scroll.visible(...)`) and apply in `useFrame`.

## Camera rigs

- **Dolly:** move `camera.position.z`; keep `lookAt` on a target. Gives "fly in".
- **Orbit by scroll:** place camera on a circle, `angle = progress * Math.PI`,
  `camera.position.set(Math.sin(a)*r, y, Math.cos(a)*r); camera.lookAt(target)`.
- **Path:** sample a `CatmullRomCurve3` at `progress` for cinematic sweeps:
  `camera.position.copy(curve.getPointAt(progress))`.
- Smooth the input: lerp the driven value toward the scroll target each frame
  (`cur += (target - cur) * 0.08`) so fast scroll flicks don't snap.

## Pinning & section staging

- `pin: true` holds the section in place while its timeline scrubs — the scroll
  "budget" (`end: '+=N'`) is how long it stays pinned. Keep `pin-spacing` on so
  layout below doesn't jump.
- Stage multiple beats on one pinned section by placing tweens at timeline labels
  (`0`, `0.3`, `0.6`). One pin, several reveals.
- Add `invalidateOnRefresh: true` and call `ScrollTrigger.refresh()` after fonts /
  images load and on resize so start/end recompute.

## The `particle-self` scroll pattern

Points start as noise, assemble into the target shape across the first pinned
screen, then drift / react to cursor while the headline holds. Combine with
particles.md:

- precompute two position buffers: `scattered` (random in a sphere) and `target`
  (sampled from a glTF surface, text, or logo SVG)
- in the vertex shader, `mix(scattered, target, uAssemble)` where `uAssemble` is the
  scroll progress eased with `smoothstep`
- add a per-point delay (`aDelay` attribute) so assembly ripples instead of snapping
- after assembly, a small curl-noise drift keeps it alive; cursor adds local repulsion

## Pitfalls

- Pin without `scrub` feels broken — the section sticks but nothing moves. Pair them.
- Tweening `renderer.render` calls or re-creating geometry per frame tanks fps —
  animate values, render once per frame in the shared loop.
- Forgetting `ScrollTrigger.refresh()` after late-loading assets leaves triggers
  measuring the wrong height → effect fires at the wrong scroll point.
- Kill triggers on unmount (craft-floor.md) or they leak and double-fire on re-mount.
