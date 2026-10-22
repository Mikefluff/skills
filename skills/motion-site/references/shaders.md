# GLSL playbook

Fragment-shader backgrounds and vertex displacement — the fluid gradients, noise
fields, metaballs, and distortion that define the genre.

## Full-screen fragment background

A plane (or fullscreen triangle) with a `ShaderMaterial`. Standard uniforms:

```js
const uniforms = {
  uTime:       { value: 0 },
  uResolution: { value: new THREE.Vector2() },  // set on resize, * pixelRatio-capped
  uMouse:      { value: new THREE.Vector2(0.5, 0.5) },
  uColorA:     { value: new THREE.Color('#3a1c71') },
  uColorB:     { value: new THREE.Color('#00d2ff') },
}
```

Simplest rig: an `OrthographicCamera` + a plane that fills the frustum, or a single
oversized triangle. Keep the fragment cheap; this runs for every pixel every frame.

## Value / FBM noise (paste-ready, no texture)

```glsl
vec2 hash2(vec2 p){ p = vec2(dot(p,vec2(127.1,311.7)), dot(p,vec2(269.5,183.3)));
  return -1.0 + 2.0*fract(sin(p)*43758.5453123); }
float noise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f*f*(3.0-2.0*f);
  return mix(mix(dot(hash2(i+vec2(0,0)), f-vec2(0,0)),
                 dot(hash2(i+vec2(1,0)), f-vec2(1,0)), u.x),
             mix(dot(hash2(i+vec2(0,1)), f-vec2(0,1)),
                 dot(hash2(i+vec2(1,1)), f-vec2(1,1)), u.x), u.y);
}
float fbm(vec2 p){
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++){ v += a*noise(p); p *= 2.0; a *= 0.5; } // ≤5 octaves
  return v;
}
```

## Fluid / flowing gradient

Domain-warp the noise with itself (cheap "fluid" look, no sim):

```glsl
void main(){
  vec2 uv = gl_FragCoord.xy / uResolution.xy;
  float t = uTime * 0.08;
  vec2 q = vec2(fbm(uv*3.0 + t), fbm(uv*3.0 - t + 5.0));
  float n = fbm(uv*3.0 + q*1.5 + t);        // warp
  vec3 col = mix(uColorA, uColorB, smoothstep(0.2, 0.8, n));
  col += 0.05 * sin(uv.yxy * 6.0 + uTime);  // subtle shimmer
  gl_FragColor = vec4(col, 1.0);
}
```

Mouse reactivity: bias the warp or color toward `uMouse` with a soft radial falloff.

## Metaballs (2D SDF)

Sum inverse-distance fields, threshold for the merge look:

```glsl
float field(vec2 uv, vec2 c, float r){ return r / length(uv - c); }
// field(uv,a,.08) + field(uv,b,.09) + ... then smoothstep(1.0, 1.1, sum)
```

Move the ball centers with `sin(uTime*...)` or toward `uMouse`. For 3D blobs that
merge in space, raymarch a sum of sphere SDFs with a smooth-min (`smin`).

## Vertex displacement

Push mesh vertices along their normal by noise for breathing blobs / terrain:

```glsl
uniform float uTime, uAmp;
varying float vD;
// noise3 omitted — use a 3D simplex/curl noise
void main(){
  float d = fbm3(normal * 1.5 + uTime * 0.2);
  vec3 p = position + normal * d * uAmp;
  vD = d;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}
```

Pass `vD` to the fragment shader to tint by displacement. An `IcosahedronGeometry`
with detail 4–6 gives smooth blobs cheaply.

## Fresnel (rim glow / "energy" look)

```glsl
varying vec3 vN, vView;      // normal, view dir in view space
float fres = pow(1.0 - max(dot(normalize(vN), normalize(vView)), 0.0), 3.0);
gl_FragColor = vec4(mix(base, rim, fres), 1.0);
```

## Image distortion (hover / scroll)

Image as a texture on a plane; displace UVs in the fragment shader by a hover
factor and a noise/displacement map:

```glsl
uniform sampler2D uTex, uDisp; uniform float uHover;
vec2 d = (texture2D(uDisp, uv).rg - 0.5) * uHover * 0.2;
vec3 c; c.r = texture2D(uTex, uv + d*1.0).r;   // RGB split
c.g = texture2D(uTex, uv + d*0.8).g;
c.b = texture2D(uTex, uv + d*0.6).b;
```

Animate `uHover` 0→1 with GSAP on pointer enter/leave.

## R3F wiring

Use drei's `shaderMaterial` to make a typed material with named uniforms, extend it,
and drive uniforms in `useFrame`:

```jsx
const FluidMat = shaderMaterial({ uTime: 0, uColorA: new THREE.Color(), /*…*/ }, vert, frag)
extend({ FluidMat })
// <mesh><planeGeometry args={[2,2]} /><fluidMat ref={r} /></mesh>
// useFrame((_,dt)=>{ r.current.uTime += dt })
```

## Discipline

- `≤ 5` FBM octaves for a background. Profile; drop octaves before anything else.
- Full-screen sims render to a **reduced-resolution** target (½ or ⅓) upscaled on
  draw — the eye won't miss it, the GPU will thank you.
- Keep `uResolution` in capped device pixels (craft-floor.md), not raw CSS pixels.
- Everything here needs a reduced-motion still: render one chosen `uTime` frame.
