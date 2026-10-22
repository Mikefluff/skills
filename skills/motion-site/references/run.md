# Preview & handover

How to let the user see it move, how to run the React target, and the two-line
handover every build ends with.

## Output location

- Default: `./generated/motion-site/<slug>/` — `<slug>` from the brief
  (`particle-hero`, `fluid-landing`). HTML target → `index.html` (+ any `assets/`).
  React target → component file(s) named for the project's conventions.
- `--variants N` → `variant-1/`, `variant-2/`, … each self-contained.
- Writing into the user's existing project (React target) happens only after you
  confirm the destination path with them.

## Preview — HTML target

The self-contained file opens anywhere. Offer the cheapest path the session has:

1. **Serve locally** (works everywhere, no tools needed):
   ```bash
   cd generated/motion-site/<slug> && python3 -m http.server 8000
   ```
   Then open `http://localhost:8000`. A static file server is needed (not `file://`)
   because ES module import maps and CORS for CDN fetches don't work from `file://`.
2. **Publish as an artifact** — if the running session has an Artifact tool, a
   single-file CDN HTML page is exactly what it renders: the user gets a live,
   interactive, shareable preview on claude.ai. Good for "покажи / preview / let me
   see it move". (Don't claim this if the tool isn't available.)
3. **`--preview`** means: actually do one of the above, don't just describe it.

Browser-driving (Chrome tools) can screenshot it for a static check, but motion
needs a live view to judge — prefer serve/artifact over a screenshot for sign-off.

## Preview — React target

Run the project's own dev server; don't invent one:

```bash
npm install   # if deps (three, @react-three/fiber, gsap, lenis…) were added
npm run dev    # or pnpm/yarn/bun per the lockfile
```

List any dependencies you added so the user can install them; don't silently assume
they're present.

## The handover (every build ends with this)

Two lines, no wall of text:

```
Built: <archetype> · <scope> · tier <webgl|light> · target <html|react>
Libs:  three@<v>, gsap@<v>, lenis@<v> (pinned). Open: <serve cmd | artifact link | npm run dev>
You supply: <real logo / glTF model / HDRI / licensed font — or "nothing, it's complete">
```

Then one sentence on the alternative direction you didn't take, if relevant — not a
menu. If anything was left as a labeled placeholder, it is named in "You supply".

## `audit` handover

For `motion-site audit <path>`, output only the report block from craft-floor.md
(fps risk, rAF loops, DPR, teardown, reduced-motion, mobile, a11y, LCP, versions) +
ranked fixes. Change nothing on disk.
