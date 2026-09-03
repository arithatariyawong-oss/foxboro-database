# -*- coding: utf-8 -*-
"""route_wires_no_overlap.py gave column-adjacent edges one lane-numbering
scheme for their approach into a target block (`adjacent`, offset from
`dx - 24`) and skip/feedback edges a second, independent one (`through`,
offset from `dx - 18`). Both schemes carve their lanes out of the same
physical gap in front of the target column, and neither knew the other
existed -- so an adjacent edge and a skip edge landing in the same column
could still be handed the same x, and one wire's short approach ended up
sitting inside another's long one for however far they both ran at that x.

Checked with the same script this file's build/route_wires_no_overlap.py
used to find the original bug: a 150-node, 207-edge map still turned up
~4,780 overlapping segment pairs after that fix and self_loop_stack, almost
all of them this. The fix is to stop running two counters and run one: every
edge landing in a given target column, adjacent or not, draws its final
approach from a single shared rank sequence for that column.
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


OLD = """  /* ---- wires first, so blocks sit on top ----
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
  const loopRank = new Map();
  for (const i of selfLoops){
    /* a block wired to its own parameter (PIDE RSP <- its own SPT, and
       often OUT -> FBK on the same block too): a tight loop over the top
       of the box, the way ICC draws it. A second loop on the same block
       is stepped out a bit further on both legs and a bit higher, so it
       clears the first loop instead of retracing it exactly. */
    const [s, sp, t, tp, qual] = L.edges[i];
    const bs = L.box.get(s), bt = L.box.get(t);
    const sx = bs.x + bs.w, sy = pinY(s, 'out', sp, L);
    const dx = bt.x, dy = pinY(t, 'in', tp, L);
    const rank = loopRank.get(s) || 0; loopRank.set(s, rank + 1);
    const leg = 16 + rank * 6, top = bs.y - 12 - rank * 6;
    const d = `M${sx} ${sy} H${sx + leg} V${top} H${dx - leg} V${dy} H${dx}`;
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
    const ex = sx + 18 + Math.min(rankOf(exitRank, bs.col), 20) * 6;
    const en = dx - 18 - Math.min(rankOf(enterRank, bt.col), 20) * 6;
    const d = `M${sx} ${sy} H${ex} V${ry} H${en} V${dy} H${dx}`;
    wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
  });
"""

NEW = """  /* ---- wires first, so blocks sit on top ----
     Two kinds of overlap are possible here: a wire cutting through a
     block that is none of its business, and two different wires ending
     up on the exact same track.

     A column-adjacent edge only ever crosses the empty gap between two
     columns, so it can never hit a block -- that gap holds nothing.
     Anything else (a skip over a column, or a feedback edge running
     backwards) is routed up over the whole diagram instead, each on its
     own row, the other stretch of canvas no block ever stands in, no
     matter how many columns the edge skips.

     Both kinds still land on the target block through the same narrow
     gap in front of it, so their final approach shares ONE lane
     assignment per target column -- an adjacent edge and a skip edge
     converging on the same column no longer get handed the same x by
     two counters that do not know about each other. */
  const selfLoops = [], through = new Set(), byTargetCol = new Map();
  L.edges.forEach((e, i) => {
    const [s, , t] = e;
    if (s === t){ selfLoops.push(i); return; }
    const bs = L.box.get(s), bt = L.box.get(t);
    if (bt.col !== bs.col + 1) through.add(i);
    if (!byTargetCol.has(bt.col)) byTargetCol.set(bt.col, []);
    byTargetCol.get(bt.col).push(i);
  });

  const wires = [];
  const loopRank = new Map();
  for (const i of selfLoops){
    /* a block wired to its own parameter (PIDE RSP <- its own SPT, and
       often OUT -> FBK on the same block too): a tight loop over the top
       of the box, the way ICC draws it. A second loop on the same block
       is stepped out a bit further on both legs and a bit higher, so it
       clears the first loop instead of retracing it exactly. */
    const [s, sp, t, tp, qual] = L.edges[i];
    const bs = L.box.get(s), bt = L.box.get(t);
    const sx = bs.x + bs.w, sy = pinY(s, 'out', sp, L);
    const dx = bt.x, dy = pinY(t, 'in', tp, L);
    const rank = loopRank.get(s) || 0; loopRank.set(s, rank + 1);
    const leg = 16 + rank * 6, top = bs.y - 12 - rank * 6;
    const d = `M${sx} ${sy} H${sx + leg} V${top} H${dx - leg} V${dy} H${dx}`;
    wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
  }

  const globalTop = Math.min(...[...L.box.values()].map(b => b.y));
  const exitRank = new Map();
  const rankOf = (m, key) => { const r = m.get(key) || 0; m.set(key, r + 1); return r; };
  const bandOf = new Map();
  for (const i of through) bandOf.set(i, bandOf.size);

  for (const [, list] of byTargetCol){
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
      const enterX = dx - 24 - rank * lane;
      let d;
      if (!through.has(i)){
        d = `M${sx} ${sy} H${enterX} V${dy} H${dx}`;
      } else {
        const ry = globalTop - 30 - bandOf.get(i) * LANE;      // its own row, never reused
        const ex = sx + 18 + Math.min(rankOf(exitRank, bs.col), 20) * 6;
        d = `M${sx} ${sy} H${ex} V${ry} H${enterX} V${dy} H${dx}`;
      }
      wires.push({ i, d, s, t, sp, tp, dx, dy, qual });
    });
  }
"""

sub(OLD, NEW, "adjacent + through share one entry-lane counter per target column")

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
