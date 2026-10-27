# Stack & wiring

The canonical motion stack and how to wire it for each target. Load at every build.

## Libraries (pin an exact patch ≥ 2 weeks old)

| Role | Library | Import (npm) | CDN example (pin exact) |
|---|---|---|---|
| 3D engine | three | `three` | `three@0.171.0/build/three.module.js` |
| three addons | three/examples jsm | `three/addons/` | `three@0.171.0/examples/jsm/` |
| React renderer | @react-three/fiber | `@react-three/fiber` | — (project only) |
| R3F helpers | @react-three/drei | `@react-three/drei` | — |
| R3F postfx | @react-three/postprocessing | `@react-three/postprocessing` | — |
| Timeline / scroll | gsap + ScrollTrigger | `gsap`, `gsap/ScrollTrigger` | `gsap@3.13.0`, `.../ScrollTrigger.min.js` |
| Smooth scroll | lenis | `lenis` | `lenis@1.1.18/dist/lenis.min.js` |
| React motion | motion (Framer Motion) | `motion/react` | — |

Notes that bite:
- **Lenis was renamed** from `@studio-freight/lenis` to `lenis`. Use `lenis`.
- **GSAP is fully free**, all plugins included (SplitText, MorphSVG, ScrollTrigger,
  …). No club membership, no CDN gate. Register plugins: `gsap.registerPlugin(ScrollTrigger)`.
- **Framer Motion is now `motion`** — import from `motion/react` (React) or `motion`
  (vanilla mini). Old `framer-motion` still resolves but prefer `motion`.
- Version numbers above are *examples*. Pin whatever is current-stable at build time
  to an exact patch; the rule is exact + allowed CDN, not these literals.

## Target: `html` (self-contained, CDN import maps)

One file. Loads three from a CDN via an import map so `import ... from 'three'`
works in a plain `<script type="module">`. Allowed CDNs only: **cdnjs, jsdelivr,
unpkg**. GSAP/Lenis as UMD globals is simplest; three as ESM.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Motion</title>
<style>
  :root { color-scheme: dark; }
  html, body { margin: 0; height: 100%; background: #05060a; }
  canvas { display: block; }
  @media (prefers-reduced-motion: reduce) { .motion-only { display: none; } }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.18/dist/lenis.min.js"></script>
<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/"
}}
</script>
</head>
<body>
<script type="module">
  import * as THREE from 'three';
  // gsap, ScrollTrigger, Lenis are globals from the UMD tags above.
  gsap.registerPlugin(ScrollTrigger);
  // ... build here
</script>
</body>
</html>
```

If an effect must not run until `prefers-reduced-motion: no-preference`, gate the
whole module init behind `matchMedia`. See craft-floor.md.

## Target: `react` (existing project)

Match the project's conventions. Component sketch:

```jsx
import { Canvas } from '@react-three/fiber'
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function Scene() {
  const mesh = useRef()
  useFrame((_, dt) => { mesh.current.rotation.y += dt * 0.2 })
  return <mesh ref={mesh}><icosahedronGeometry args={[1, 4]} /><meshStandardMaterial /></mesh>
}

export default function Hero() {
  return (
    <Canvas dpr={[1, 2]} gl={{ antialias: true, powerPreference: 'high-performance' }}
            camera={{ fov: 45, position: [0, 0, 5] }}>
      <ambientLight intensity={0.6} />
      <directionalLight position={[3, 3, 3]} />
      <Scene />
    </Canvas>
  )
}
```

R3F handles the rAF loop, resize, and (with `frameloop="demand"` or unmount)
teardown for you — don't hand-roll a second loop. Cap DPR with `dpr={[1, 2]}`.

## The smooth-scroll + GSAP sync (both targets)

Lenis drives scroll; GSAP's ticker drives Lenis; ScrollTrigger reads from Lenis.
Wire it exactly once:

```js
const lenis = new Lenis({ lerp: 0.1, smoothWheel: true })
lenis.on('scroll', ScrollTrigger.update)
gsap.ticker.add((time) => lenis.raf(time * 1000)) // time is seconds → ms
gsap.ticker.lagSmoothing(0)
```

Do **not** also call `requestAnimationFrame(raf)` for Lenis if GSAP's ticker
drives it — that double-steps scroll. One driver only.

For the React target use the `lenis/react` `ReactLenis` provider, or the hook, and
sync in a `useEffect`; tear down on unmount.
