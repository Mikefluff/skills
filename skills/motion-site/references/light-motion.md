# Light tier — motion without WebGL

CSS / SVG / GSAP / Framer Motion. Reach here first; most "motion sites" are mostly
this, with WebGL only where it earns the GPU (tier-picker.md). All of it is
reduced-motion-trivial: wrap in the guard and it degrades to static.

```js
const ok = !matchMedia('(prefers-reduced-motion: reduce)').matches
if (ok) { /* run GSAP / Lenis here */ }
```

## Scroll reveals & stagger (GSAP ScrollTrigger)

```js
gsap.registerPlugin(ScrollTrigger)
gsap.from('.reveal', {
  y: 40, opacity: 0, duration: 0.8, stagger: 0.08, ease: 'power3.out',
  scrollTrigger: { trigger: '.section', start: 'top 80%' },  // once by default
})
```

Prefer `batch()` for long lists so items reveal as they enter:
`ScrollTrigger.batch('.card', { onEnter: b => gsap.from(b, {y:30,opacity:0,stagger:0.1}) })`.
Set initial hidden state in CSS too, so a JS failure doesn't flash all content.

## Kinetic type (GSAP SplitText — now free)

```js
const split = new SplitText('.headline', { type: 'lines,chars' })
gsap.from(split.chars, { yPercent: 120, opacity: 0, stagger: 0.02, ease: 'back.out(1.6)',
  scrollTrigger: { trigger: '.headline', start: 'top 85%' } })
```

Mask reveal: wrap lines in `overflow:hidden`, animate `yPercent` from 100 → 0. For
no-SplitText environments, split by word in markup or CSS. Revert on teardown:
`split.revert()`.

## Parallax

```js
gsap.to('.bg', { yPercent: -20, ease: 'none',
  scrollTrigger: { trigger: '.section', start: 'top bottom', end: 'bottom top', scrub: true } })
```

Or pure CSS with scroll-driven animations (progressive enhancement, no JS):

```css
@supports (animation-timeline: scroll()) {
  .bg { animation: rise linear both; animation-timeline: scroll(root); }
  @keyframes rise { to { translate: 0 -20%; } }
}
```

## Marquee (seamless, velocity-reactive)

Duplicate the strip, translate `-50%` on a loop (`gsap.to(x, {xPercent:-50, repeat:-1, duration, ease:'none'})`).
Nudge `timeScale` by scroll velocity (`lenis` gives it) for the reactive-speed look;
ease back to 1.

## Magnetic buttons

On `pointermove` within the button, translate it a fraction toward the cursor; on
leave, GSAP elastic back to 0:

```js
el.addEventListener('pointermove', e => {
  const r = el.getBoundingClientRect()
  gsap.to(el, { x: (e.clientX - (r.left+r.width/2)) * 0.3, y: (e.clientY - (r.top+r.height/2)) * 0.3, duration: 0.4 })
})
el.addEventListener('pointerleave', () => gsap.to(el, { x: 0, y: 0, ease: 'elastic.out(1,0.3)', duration: 0.8 }))
```

Pointer-fine only — guard with `matchMedia('(pointer:fine)')` so touch isn't janky.

## Sticky / horizontal scroll gallery

Pin a section, translate a track horizontally across its scroll budget:

```js
const track = document.querySelector('.track')
gsap.to(track, { x: () => -(track.scrollWidth - innerWidth), ease: 'none',
  scrollTrigger: { trigger: '.gallery', pin: true, scrub: 1,
    end: () => '+=' + (track.scrollWidth - innerWidth), invalidateOnRefresh: true } })
```

## SVG draw & morph

- **Draw:** `stroke-dasharray`/`dashoffset` animated 0 (GSAP `drawSVG`, now free, or
  raw dashoffset). Good for signatures, underlines, connectors.
- **Morph:** GSAP `MorphSVG` (free) tweens one path's `d` into another. Keep point
  counts comparable for clean morphs.

## Framer Motion (React target)

```jsx
import { motion } from 'motion/react'
<motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-15%' }} transition={{ duration: 0.6, ease: [0.22,1,0.36,1] }} />
```

- `whileInView` for reveals, `whileHover`/`whileTap` for micro-interactions,
  `layout` for shared-layout transitions, `useScroll` + `useTransform` for parallax.
- `<AnimatePresence>` for enter/exit (modals, route changes).
- Framer Motion respects `prefers-reduced-motion` via `useReducedMotion()` — honor it.

## View Transitions (page/element transitions)

`document.startViewTransition(() => updateDOM())` cross-fades or morphs between
states (nav, filter, route) with almost no code. Progressive enhancement — feature-
detect and fall back to an instant swap. In React frameworks, prefer their built-in
view-transition integration where present.

## Discipline

- Set the hidden/initial state in CSS so content isn't lost if JS fails — **but**
  when that hidden state is a `transform` (e.g. `translateY(110%)` on split chars)
  and you then animate it with GSAP `yPercent`/`xPercent`, clear the stray pixel
  offset GSAP reads from the CSS matrix: start the tween with
  `.fromTo(els, {yPercent:110, y:0, x:0}, {yPercent:0, …})`, or `gsap.set(els,
  {yPercent:110, y:0})` before `.to({yPercent:0})`. Otherwise GSAP parses the CSS
  `translateY(110%)` into `y` (px), adds the percent on top, and `yPercent:0` only
  zeroes the percent — the px lingers and the element stays hidden (a real bug this
  skill shipped once: a split headline that never rose into view).
- `ease: 'none'` for scrubbed scroll, expressive eases for triggered one-shots.
- Kill ScrollTriggers and revert SplitText on unmount (craft-floor.md).
- Everything degrades to a clean static layout under reduced-motion. Test it.
