# -*- coding: utf-8 -*-
"""Stop signal-map.html's wires crossing blocks, and stop them stacking on
each other.

Two bugs lived in the same few lines of render():

1. Any edge that skipped more than one column (bs.col to bt.col > 1 --
   common once the layering has more than one path into a node, since a
   node's column is the LONGEST path to it) was drawn as one straight
   horizontal run at the source pin's own height, all the way to the
   target's column. That height has no reason to be clear over the
   columns in between, so the run went straight through whatever block
   happened to sit at that row a column or two along.

2. The lane a wire got inside a column gap was `lane % 9` -- fine for the
   first 9 wires sharing a gap, then the 10th reused lane 0's x and drew
   directly on top of the 1st. Feedback edges had the same wraparound
   one column over (`% 10` / `% 7`).

The fix: only a truly column-adjacent edge (bt.col === bs.col + 1) gets
the direct in-gap route, because that gap is the one stretch of canvas
guaranteed to hold no block -- and its lane count is now sized to the
wires actually in that gap instead of wrapping. Everything else (a
column skip, or a feedback edge running backwards) is routed up over the
whole diagram, one row per edge, which is the other stretch guaranteed
clear of every block regardless of how many columns it spans.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "signal-map.html"

s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


OLD = """  /* ---- wires first, so blocks sit on top ---- */
  const gapLane = new Map();          // vertical lanes between columns
  let ringUp = 0;                     // horizontal lanes for feedback paths
  const wires = [];
  L.edges.forEach((e, i) => {
    const [s, sp, t, tp, qual] = e;
    const bs = L.box.get(s), bt = L.box.get(t);
    const sx = bs.x + bs.w, sy = pinY(s, 'out', sp, L);
    const dx = bt.x, dy = pinY(t, 'in', tp, L);
    let d;
    if (s === t){
      /* a block wired to its own parameter (PIDE RSP <- its own SPT):
         a tight loop over the top of the box, the way ICC draws it */
      const top = bs.y - 12;
      d = `M${sx} ${sy} H${sx + 16} V${top} H${dx - 16} V${dy} H${dx}`;
    } else if (bt.col > bs.col){
      const key = bt.col;
      const lane = (gapLane.get(key) || 0) + 1; gapLane.set(key, lane);
      const mx = bt.x - 24 - (lane % 9) * LANE;
      d = `M${sx} ${sy} H${mx} V${dy} H${dx}`;
    } else {
      /* feedback: out to the right, up over everything, back to the left */
      ringUp += 1;
      const ry = -30 - (ringUp % 10) * LANE;
      d = `M${sx} ${sy} H${sx + 22} V${ry} H${dx - 26 - (ringUp % 7) * LANE} V${dy} H${dx}`;
    }
    wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
  });
"""

NEW = """  /* ---- wires first, so blocks sit on top ----
     A column-adjacent edge only ever crosses the empty gap between two
     columns, so it just needs its own lane inside that gap -- sized to
     the gap, not wrapped with modulo, which used to hand the 10th wire
     through a gap the same x as the 1st and draw one on top of the
     other. Anything that is NOT column-adjacent (a skip over a column,
     or a feedback edge running backwards) cannot be drawn straight at
     the source's own height: that height is very likely to cross a
     block sitting in one of the columns in between. Those are routed up
     over the whole diagram instead, each on its own row -- the one
     stretch of the canvas no block ever stands in, no matter how many
     columns the edge skips. */
  const selfLoops = [], adjacent = new Map(), through = [];
  L.edges.forEach((e, i) => {
    const [s, , t] = e;
    if (s === t){ selfLoops.push(i); return; }
    const bs = L.box.get(s), bt = L.box.get(t);
    if (bt.col === bs.col + 1){
      if (!adjacent.has(bt.col)) adjacent.set(bt.col, []);
      adjacent.get(bt.col).push(i);
    } else through.push(i);
  });

  const wires = [];
  for (const i of selfLoops){
    /* a block wired to its own parameter (PIDE RSP <- its own SPT): a
       tight loop over the top of the box, the way ICC draws it */
    const [s, sp, t, tp, qual] = L.edges[i];
    const bs = L.box.get(s), bt = L.box.get(t);
    const sx = bs.x + bs.w, sy = pinY(s, 'out', sp, L);
    const dx = bt.x, dy = pinY(t, 'in', tp, L);
    const top = bs.y - 12;
    const d = `M${sx} ${sy} H${sx + 16} V${top} H${dx - 16} V${dy} H${dx}`;
    wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
  }

  for (const [, list] of adjacent){
    /* rank by the row each wire actually runs at, so the lanes fan out
       in travel order instead of crossing right at the gap's mouth */
    list.sort((ia, ib) => {
      const a = L.edges[ia], b = L.edges[ib];
      return (pinY(a[0], 'out', a[1], L) + pinY(a[2], 'in', a[3], L))
           - (pinY(b[0], 'out', b[1], L) + pinY(b[2], 'in', b[3], L));
    });
    const lane = Math.min(LANE, Math.max(4, (COL_GAP - 40) / list.length));
    list.forEach((i, rank) => {
      const [s, sp, t, tp, qual] = L.edges[i];
      const bs = L.box.get(s), bt = L.box.get(t);
      const sx = bs.x + bs.w, sy = pinY(s, 'out', sp, L);
      const dx = bt.x, dy = pinY(t, 'in', tp, L);
      const mx = dx - 24 - rank * lane;
      const d = `M${sx} ${sy} H${mx} V${dy} H${dx}`;
      wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
    });
  }

  const globalTop = Math.min(...[...L.box.values()].map(b => b.y));
  const exitRank = new Map(), enterRank = new Map();
  const rankOf = (m, key) => { const r = m.get(key) || 0; m.set(key, r + 1); return r; };
  through.forEach((i, band) => {
    const [s, sp, t, tp, qual] = L.edges[i];
    const bs = L.box.get(s), bt = L.box.get(t);
    const sx = bs.x + bs.w, sy = pinY(s, 'out', sp, L);
    const dx = bt.x, dy = pinY(t, 'in', tp, L);
    const ry = globalTop - 30 - band * LANE;                 // its own row, never reused
    const ex = sx + 18 + Math.min(rankOf(exitRank, s), 20) * 6;
    const en = dx - 18 - Math.min(rankOf(enterRank, t), 20) * 6;
    const d = `M${sx} ${sy} H${ex} V${ry} H${en} V${dy} H${dx}`;
    wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
  });
"""

sub(OLD, NEW, "orthogonal wire routing -> block-safe, collision-free lanes")

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
