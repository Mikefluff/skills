# Particle systems

Thousands of moving points: fields, morphs, starfields, assembly. Always
`THREE.Points` with a `BufferGeometry` + a `ShaderMaterial` — never many meshes.

## Baseline points

```js
const N = 40000
const positions = new Float32Array(N * 3)
for (let i = 0; i < N; i++) {
  // fill from a sphere / box / sampled surface
}
const geo = new THREE.BufferGeometry()
geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))

const mat = new THREE.ShaderMaterial({
  uniforms: { uTime: { value: 0 }, uSize: { value: 18 }, uColor: { value: new THREE.Color('#88ccff') } },
  vertexShader, fragmentShader,
  transparent: true, depthWrite: false,
  blending: THREE.AdditiveBlending,   // glow; use NormalBlending for solid points
})
const points = new THREE.Points(geo, mat)
```

Vertex shader sizes points by distance (so they shrink with depth) and can displace:

```glsl
uniform float uTime, uSize;
void main() {
  vec3 p = position;
  // optional: curl/sine drift here
  vec4 mv = modelViewMatrix * vec4(p, 1.0);
  gl_PointSize = uSize * (1.0 / -mv.z);   // perspective sizing
  gl_Position = projectionMatrix * mv;
}
```

Fragment shader makes each point a soft disc, not a square:

```glsl
uniform vec3 uColor;
void main() {
  float d = length(gl_PointCoord - 0.5);
  if (d > 0.5) discard;                 // round
  float a = smoothstep(0.5, 0.0, d);    // soft edge
  gl_FragColor = vec4(uColor, a);
}
```

Budget: 20k–80k points hold 60fps on desktop; drop to 8k–15k on mobile
(craft-floor.md). `AdditiveBlending` + `depthWrite:false` avoids sort artifacts.

## Shape morph & assembly (the `particle-self` core)

Carry two (or more) position buffers as attributes and blend in the vertex shader:

```js
geo.setAttribute('aScatter', new THREE.BufferAttribute(scatter, 3)) // random
geo.setAttribute('aTarget',  new THREE.BufferAttribute(target, 3))  // the shape
geo.setAttribute('aDelay',   new THREE.BufferAttribute(delay, 1))   // 0..1 per point
```
```glsl
uniform float uAssemble;   // 0 scattered → 1 formed (scroll- or time-driven)
attribute vec3 aScatter, aTarget;
attribute float aDelay;
// ...
float t = clamp((uAssemble - aDelay * 0.3) / 0.7, 0.0, 1.0);
t = t * t * (3.0 - 2.0 * t);            // smoothstep ease
vec3 p = mix(aScatter, aTarget, t);
```

Sampling the target points:
- **from a 3D model:** `MeshSurfaceSampler` (three/addons) over a glTF mesh.
- **from text/logo:** render text or an SVG to an offscreen canvas, read pixels,
  emit a point where alpha/luma passes a threshold (subsample to N).
- **from a sphere/box:** cheap procedural targets for abstract hero fields.

## Motion: curl noise & cursor

- **Drift:** add a small curl-noise or layered-sine offset in the vertex shader
  keyed on `uTime` so a formed shape breathes instead of freezing.
- **Cursor repulsion:** pass `uMouse` (world or NDC) + `uRepel`; push points within
  a radius along the away-vector, ease back. Keep the radius soft (`smoothstep`).
- **Velocity trails:** feed scroll velocity (`lenis` exposes it, or diff progress)
  into point size or speed for a reactive feel.

## GPGPU / FBO (only when you need real simulation)

For flocking, fluid-like particle motion, or N large enough that per-frame JS
position updates stall: simulate positions in a texture with ping-pong render
targets (`GPUComputationRenderer` in three/addons), then read the texture in the
render vertex shader. This keeps positions on the GPU.

Reach for it only when attribute-blend + shader drift cannot express the motion —
it is more code, more teardown (dispose both render targets), and more mobile risk.
For assembly, drift, and repulsion, the attribute approach above is enough.

## Starfield / warp

Points in a long box; move `positions.z` toward the camera each frame, wrap when
past; scale speed by scroll/hover. Streak by stretching `gl_PointSize` or drawing
short lines (`THREE.LineSegments`) along the velocity for a hyperspace look.
