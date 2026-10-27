# Postprocessing

Full-frame effects over a live scene: bloom, chromatic aberration, depth of field,
grain, vignette, god rays. The polish that makes WebGL read as "produced" — and the
first thing to cut when fps drops.

## R3F (preferred)

`@react-three/postprocessing` wraps the scene in an `EffectComposer`:

```jsx
import { EffectComposer, Bloom, ChromaticAberration, Vignette, Noise, DepthOfField } from '@react-three/postprocessing'

<EffectComposer multisampling={0}>
  <Bloom intensity={0.6} luminanceThreshold={0.8} luminanceSmoothing={0.3} mipmapBlur />
  <ChromaticAberration offset={[0.0008, 0.0008]} />
  <Vignette eskil={false} offset={0.2} darkness={0.7} />
  <Noise opacity={0.03} />
</EffectComposer>
```

Order matters (top → bottom = first → last applied). Bloom before CA before grain
before vignette reads well. `mipmapBlur` bloom is cheaper and softer than the old
kernel bloom.

## Vanilla three

```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass }      from 'three/addons/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'
import { OutputPass }      from 'three/addons/postprocessing/OutputPass.js'

const composer = new EffectComposer(renderer)
composer.addPass(new RenderPass(scene, camera))
composer.addPass(new UnrealBloomPass(new THREE.Vector2(w, h), 0.6, 0.4, 0.85))
composer.addPass(new OutputPass())
// in the loop: composer.render()  (NOT renderer.render)
// on resize: composer.setSize(w, h); and setPixelRatio capped ≤ 2
// on teardown: composer.dispose() and dispose each pass's render targets
```

`OutputPass` handles tone mapping + color space at the end — include it, or colors
shift.

## What each effect is for

- **Bloom** — makes emissive / bright areas glow. Raise `luminanceThreshold` so only
  the intended highlights bloom, not the whole frame (the "everything is foggy" bug).
  Mark glowing materials emissive or push their color > 1.
- **Chromatic aberration** — subtle RGB fringe at the edges; sells "lens"/glass.
  Keep offset tiny (`~0.0005–0.001`) or it looks broken.
- **Depth of field** — focus the hero, blur the rest. Expensive; desktop only, and
  only when there's real depth to blur.
- **Noise / film grain** — low opacity (`0.02–0.05`) kills banding on gradients and
  adds texture. Cheap, high value.
- **Vignette** — darkens edges, pulls the eye in. Cheap.
- **God rays / SSAO** — strong but costly; reserve for a hero moment, cut on mobile.

## Budget & bans

- Postprocessing is a per-pixel pass (sometimes several). It is the **first cut**
  when fps drops, and it is **off on mobile / low-end** by default (craft-floor.md).
- Keep `multisampling={0}` when using effect-level AA, or you pay twice.
- A full-screen DOF + bloom + god-rays stack on a phone is an instant jank; gate it.
- Never block LCP on the composer; the scene (and text in front of it) comes first.
