# House UI style, and the traps in offline single-file pages

## The visual system — use it, do not invent one

The user carries this across all their internal tools (TriconexDB, PT2 Analysis,
FOXBORO) and hands it over as reference images rather than describing it.
Matching it is what makes a new page look like part of the set.

- **Font:** SF Compact. Subsets at `03 WEB/assets/fonts/sf-compact-{400,700}.woff2`
  (originals in `Desktop/TriconexDB/scripts/assets/`). **Embed as base64 data
  URIs** — a `file://` page will not load an `@font-face` from a relative path.
  SF Compact has **no Thai glyphs**, so keep `"Noto Sans Thai","Leelawadee UI"`
  behind it for per-glyph fallback. The `.dmg` in their folders is a macOS
  installer and cannot be opened on Windows.
- **Palette (light):** `--bg #dee1d8` · `--surface #f7f5ee` · `--surface-2 #efece1`
  · `--border #dcd7c7` · `--text #2c332f` · `--text-dim #5a635d` ·
  `--accent #26505c` · mint `#a8d5bf` for selected states · `--amber #e8c98a`
  with `--amber-ink #6b4f16`. Dark is fully defined too.
- **Diagram ink:** `--blk-head #c9d8ef` for a block, `--blk-root #bfe3cd` for the
  selected one, `--ecb-head #f0dcb6` for FBM hardware, `--jove-head #ded7f2` for
  a Jove object.
- **Components:** pill buttons and chips, large radii (28 / 20 / 12),
  inset-pressed inputs, `lift` shadows with an `inset-hi` highlight.
- **Type noticeably larger than a dense dashboard** — body ~15.5px, table cells
  ~14px, KPI numerals ~34px. This was an explicit correction; do not shrink it.

The fastest way to keep a new page consistent is to **lift the whole `<style>`
block from an existing one** — `build/build_sequence_view_page.py` takes
`logic-view.html`'s verbatim and appends its own rules after it, so the two
cannot drift.

## Traps that each cost real debugging time

None is obvious from reading the code afterwards.

- **A `click` handler can miss when the page uses `setPointerCapture`.** Capturing
  the pointer for pan/drag lets the browser dispatch the compatibility `click` at
  the capture target instead of the element under the cursor, so
  `e.target.closest('.block')` comes back null and nothing happens. It is version-
  and device-dependent — it worked here and failed on the user's machine, and the
  cache got blamed twice before the real cause was found. Take the pick from
  `pointerdown` (its target resolves before capture is set) and act on `pointerup`
  when the pointer did not move.

- **`localeCompare` builds a fresh collator on every call.** Ranking DESCRP's
  33,387 distinct values that way took 3.3 s and froze the renderer on every
  keystroke. One shared `Intl.Collator` plus a cached rank per column: 136 ms
  once, then free.

- **A `file://` page cannot `fetch()` a `.json`, nor load an `@font-face` or a
  `background-image` from a relative path.** Ship data as a `.js` assigning a
  global (gzip + base64, inflated with `DecompressionStream`); inline fonts and
  images as `data:` URIs. `<script src>` is the only channel that works.

- **`<meta http-equiv="cache-control" content="no-store">` covers the HTML — NOT
  the `<script src>` data files.** After re-exporting `graph.js` the page loaded
  the *old* payload while the server held the new one, and a just-verified fix
  looked like it had done nothing. `location.reload(true)` is a no-op in modern
  Chrome. Two things that do work: compare `window.FOX_<X>_B64.length` against a
  `fetch(url, {cache:'reload'})` of the same file before believing any result,
  and **re-serve on a different port** — a new origin has an empty cache.
  (The browser extension cannot open `file://` at all, so a throwaway
  `python -m http.server` is how these pages get driven; give each verification
  round its own port.)

- **A CSS override placed early loses the cascade to a rule defined later at the
  same specificity.** `body.embed .topbar{display:none}` near the top of the sheet
  lost to `.topbar{display:flex}` further down. Append such overrides right before
  `</style>` and say why in a comment.

- **`getBBox()` right after building a subtree can be measured before the flex
  layout has settled**, giving a wrong `fit()` zoom on the first draw of a
  session — 0.77 for a chart that needed 0.32. Call `fit()` once synchronously
  and again on `requestAnimationFrame`.

- **Straighten an oblique 3D icon with a vertical shear, not a rotation.**
  `05.jpg`'s plate edges slope 12.5° but its slider stems are vertical to 0.01° —
  the signature of an oblique projection. Rotating tilts the stems; shearing
  `(x, y) → (x, y + s·x)` levels the edges and leaves verticals vertical.

## Verify in the browser, at scale

The standard this project holds itself to, and it has caught real bugs every
time: **render every case and assert, do not spot-check.** Recent sweeps —
942 sequence blocks, 4,232 step programs, 202 signal maps — each reported
0 errors and no case over its time budget, and the geometry checkers reported
0 wire/block crossings. Write the sweep as an async loop that yields every ~25
iterations so the tab stays responsive, stash the promise on `window`, and read
the result back in a later call.
