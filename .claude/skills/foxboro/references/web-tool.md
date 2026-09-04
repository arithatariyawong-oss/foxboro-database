# The web tool — `03 WEB/`

An offline, no-server replacement for a Power BI report. Opens from `file://`
(or `serve.cmd` on `127.0.0.1:8712` if policy blocks that). **`03 WEB` is the git
repo**, not `FOXBORO`.

## Pages

Five sit in the shared nav bar; two are popup-only and deliberately not
advertised as destinations.

| page | shown as | reads |
|---|---|---|
| `index.html` | TAG SEARCH | `data.js`, `params.js` |
| `signal-map.html` | SIGNAL MAP | `graph.js`, `params.js`, `data.js` (lazily, for Properties) |
| `system-manager.html` | SYSTEM MANAGER | `data.js`, `systems.js`, `params.js` |
| `system-monitor.html` | FBM (I/O) MODULE MANAGEMENT | `systems.js` |
| `modbus.html` | MODBUS COMMUNICATION | `modbus.js` |
| `logic-view.html` | *(popup only)* LOGIC VIEW | `logic.js` |
| `sequence-view.html` | *(popup only)* SEQUENCE VIEW | `sequence.js` |

`system-monitor.html` keeps its original filename on purpose — only the visible
label was renamed, so old links still work.

**Reaching the two popups.** Logic View: right-click a block in the signal map
(offered only on the 4,232 blocks with a step program). Sequence View: the tag
table's NAME menu on an IND row, or the signal map's block menu, or either of
its empty states. **The tag table is the dependable route** — a sequence block
usually has no box on the map to right-click, which is exactly the point.

## Data files

All gzip + base64 inside a `.js` global, inflated with `DecompressionStream`.
A page on `file://` cannot `fetch()` a `.json`; `<script src>` is the only
channel that works.

| file | size | contents |
|---|---|---|
| `data.js` | 2.4 MB | 77,010 rows × 1,202 cols, dictionary-encoded + sparse |
| `graph.js` | 1.9 MB | 82,897 nodes, 108,897 edges (58,129 parameter + 30,334 hardware + 20,434 Jove) |
| `systems.js` | 160 KB | 1,436 modules, 16,422 I/O points |
| `modbus.js` | 208 KB | 16,462 register points |
| `logic.js` | 0.43 MB | 4,232 step programs |
| `sequence.js` | 0.48 MB | 942 sequence blocks + all 779 sources |
| `params.js` | 40 KB | the slim shipping copy of `block_params.json` |

Minimum deliverable: `index.html` + `data.js` + `params.js`.

## The build-script convention — follow it

Every edit to a page is a **one-shot Python script in `build/`** that does exact
string replacement and `sys.exit`s if an anchor is not found exactly once. Read
them to see what changed or to reverse it. They are the change log.

```python
def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)
```

Because they assert, **re-running one on an already-patched file aborts** — that
is the intended safety. To iterate, restore the file from a backup first and
replay the whole chain.

Ordered chains that must run together:
- branching Logic View: `draw_branching_logic.py` → `layout_branching_logic.py` → `fix_branching_polish.py`
- signal-map wire routing: `route_wires_no_overlap.py` → `fix_self_loop_stack.py` → `unify_entry_lanes.py` → `fix_through_lane_keys.py` → `clamp_lanes_to_gap.py`

## Wire routing — the rule both diagram pages arrived at

**A wire may only run through a stretch of canvas that is guaranteed empty.**

- An edge between **column-adjacent** boxes (`target.col === source.col + 1`)
  draws straight across — that gap is always empty.
- Anything else (a column skip, or a feedback edge running backwards) routes
  **above the whole diagram on its own row**, one row per edge, **no modulo**.
  The old code used `lane % 9`, so a 10th wire in a gap silently drew on top of
  the 1st.
- Both kinds share **one entry-lane counter per target column**. Two independent
  counters hand out the same x.
- Lane width is a **fixed total budget per gap split by count**
  (`(COL_GAP-60)/count`), not a fixed step per wire — a floor-based step reserves
  more width than the gap has once a column gets crowded (40+ wires) and overruns
  into the next column's blocks.

In the CFG flowchart the equivalent empty stretches are the band between two rows
and the gutter to the right of every container.

Verified by an in-page geometry check: parse every wire's `d` into segments and
test against every block rect. Current: **0 crossings** on signal-map (7 diagrams
to the 150-node cap) and on the flowchart (2,027 edges across 130 diagrams).
A same-pin fan-out touch is expected and excluded.

## Defaults, chosen deliberately

- **Signal map opens at chain length 1.** Four hops is a wall of 150 boxes.
- **System Manager fills nothing until an equipment is picked** from the rail.
  The six block panes are *skipped*, not hidden — on ALL NETWORK they would walk
  77,010 rows for tables nobody asked for. `?tag=` and `?cp=` still land where
  they did; following a link is a choice. `picked` is a separate flag from
  `selCp === -1`, which stays a real, deliberate scope that does fill them.
- **Signal map draws only pins that carry a wire.** The ☰ button opts into every
  connectable pin B0193AX gives the type. Wired-only is the default on purpose —
  PIDE is 47 inputs against 5 wired, and the full rail was asked for and asked
  back off the same day. Build the full set only if asked again.

## Clear all filters

Every filtering page carries the same amber button top-right next to Export CSV:
TAG SEARCH, FBM MODULE MANAGEMENT, MODBUS, SYSTEM MANAGER, SEQUENCE VIEW.
**The tab a page is on is not a filter and is not cleared** — nor is the block
Sequence View has open. `signal-map.html` and `logic-view.html` have no such
button: their only control is a search box you navigate *with*, which hides
nothing.

## Still unbuilt

- CP loading by scan PERIOD (the FBM page shows the period histogram, not loading).
- Filling the 22 missing CPs in `02 AREA/CP AREA.xlsx` — the fix for the 13,781
  blank-AREA rows. Nothing in the pages needs to change.
- `export_logic.py` re-run so Logic View shows Jove destinations for CALC outputs
  (it reads `graph.js`, which now carries them).
