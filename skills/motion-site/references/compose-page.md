# Composing a full page

Scope `page`: several motion sections over one smooth-scroll spine, that stays at
60fps and doesn't exhaust the viewer. A page is not a stack of heroes.

## The spine

- **One Lenis instance** for the whole page, wired to GSAP's ticker once (stack.md).
  Not one per section.
- **One ScrollTrigger context.** Create triggers per section but refresh them
  together after assets load; `ScrollTrigger.refresh()` on resize and font load.
- **One WebGL canvas, shared.** Prefer a single fixed full-viewport `<canvas>` behind
  the page (or one R3F `<Canvas>`), and swap/show scenes per section by scroll —
  rather than mounting a new renderer per section. Multiple WebGL contexts compete
  for the GPU and browsers cap them (~8–16); you will hit the limit and contexts get
  dropped. If sections truly need isolated canvases, mount/unmount on enter/leave and
  dispose on leave.

## Section rhythm

- **Not every section is a canvas.** One or two loud WebGL moments per page; the
  rest carry with light-tier reveals, type, and imagery. Contrast is what makes the
  loud sections land. A page where everything moves reads as noise and melts phones.
- Alternate energy: loud hero → quiet readable section → medium interactive → quiet
  → loud finale. Give the eye rest.
- Keep a consistent motion language (same eases, same reveal distance, same timing
  family) so it feels like one site, not a demo reel. Pull the easing/spacing
  vocabulary from the page's design system — that part is impeccable's, not this
  skill's; motion-site matches it, doesn't invent a second one.

## Loader & preload

- Gate heavy assets (glTF, HDRI, large textures) behind a loader, but **never block
  first paint** on them. Text and layout paint immediately as HTML; the loader covers
  only the WebGL enhancement.
- Use `THREE.LoadingManager` (vanilla) or drei `useProgress` + `<Loader>` (R3F) for a
  real progress number, not a fake timed bar.
- Preload the next section's assets while the current one is on screen; lazy-init
  scenes that are far below the fold.
- First meaningful frame should appear in well under a loader's welcome; if the hero
  needs a 10MB model, show a static poster first and swap when ready.

## Performance across sections

- **Pause offscreen scenes.** `IntersectionObserver` per canvas/scene: tick only what
  is visible. A page with five scenes must never run five rAF-worth of work at once.
- Lower DPR / particle counts further on a page than on a standalone section — the
  budget is shared.
- Watch cumulative layout shift from pinned sections; keep `pin-spacing` and reserve
  space so content below doesn't jump.
- Test the whole scroll on a mid phone, not just the hero. Jank usually appears at
  section transitions, not within a section.

## Composing from sections you already built

If sections were built individually (`--scope section`), composing them means:
one Lenis, one shared canvas where possible, one refresh, consistent easing, and
cutting the particle/postfx budget per section so the sum fits. Re-verify the full
page by eye once (craft-floor.md) — section-perfect pieces can still jank together.
