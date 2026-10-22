# 3D models, characters & liquid glass

Loading real geometry, lighting it so it reads as premium, and the transmission
("liquid glass") look.

## Loading glTF (+ Draco)

glTF/GLB is the web 3D format. Compress with Draco (geometry) / KTX2 (textures) and
load with the matching decoders:

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'
const draco = new DRACOLoader().setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/libs/draco/')
const loader = new GLTFLoader().setDRACOLoader(draco)
loader.load(url, (gltf) => scene.add(gltf.scene))
```

R3F: `useGLTF(url)` from drei (it wires Draco/Meshopt); preload with
`useGLTF.preload(url)`. Wrap the model in `<Suspense>` with a fallback.

Assets the user must supply: the `.glb` itself, and any HDRI. Wire a labeled
placeholder (a primitive with a note) and list it in the handover — never a broken
import. Keep models low-poly for web; decimate heavy scans.

## Lighting that looks expensive

Image-based lighting beats point lights for product/metal/glass. Use an HDRI
environment:

```jsx
import { Environment, Lightformer } from '@react-three/drei'
// <Environment preset="studio" />  — or files={hdrUrl}, or custom <Lightformer>s
```

- `meshStandardMaterial` / `meshPhysicalMaterial` react to the environment —
  metalness + roughness + a good HDRI is 80% of "premium".
- Add one soft key `directionalLight` for a defined highlight; keep ambient low.
- `ContactShadows` / `AccumulativeShadows` (drei) ground the object cheaply.
- Tone mapping: `ACESFilmicToneMapping` on the renderer; set `renderer.outputColorSpace`
  / let three default to sRGB. Correct color space is what separates "flat" from "lit".

## Liquid glass / transmission

The refractive glass panel/blob. `MeshTransmissionMaterial` (drei) or
`meshPhysicalMaterial` with `transmission`:

```jsx
<mesh>
  <roundedBoxGeometry args={[2, 1.2, 0.3, 8, 0.2]} />
  <MeshTransmissionMaterial
    thickness={0.5} roughness={0.08} transmission={1} ior={1.3}
    chromaticAberration={0.04} anisotropy={0.3} distortion={0.3}
    distortionScale={0.4} temporalDistortion={0.1} backside />
</mesh>
```

Cost notes:
- Transmission re-renders the scene behind the object into a buffer — it is
  expensive. One or two transmissive objects, not a field of them.
- It needs something behind it to refract (content, a gradient, other 3D). Over a
  flat color it looks like nothing.
- Pair with subtle bloom + chromatic aberration (postprocessing.md) for the sheen.
- Mobile: drop `backside`, lower `samples`/resolution, or fall back to a CSS
  `backdrop-filter: blur()` glass card (craft-floor.md).

## 3D product viewer

- `OrbitControls` (drei `<OrbitControls enablePan={false} enableZoom={…} autoRotate autoRotateSpeed={0.6} />`)
  with damping on; constrain polar angle so users can't look under the floor.
- Auto-spin until first interaction, then hand control over.
- Frame the model: center it (`Box3().setFromObject`), set camera distance from its
  bounding sphere so it fills the frame on any aspect.
- Give a non-3D equivalent for keyboard/reduced-motion: a static hero render.

## 3D character

- Idle: play the glTF's bundled animation clip with `AnimationMixer` (or drei
  `useAnimations`). Advance the mixer in the one rAF loop.
- Scroll-posed: blend between clips or drive a bone/morph target by scroll progress
  (scroll-3d.md). Keep rigs light; full skinned characters are the heaviest web 3D —
  budget hard and give mobile a static pose.
