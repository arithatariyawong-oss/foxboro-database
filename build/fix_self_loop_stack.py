# -*- coding: utf-8 -*-
"""A block with two self-referencing pins (PIDE's OUT -> FBK and SPT -> RSP
both feed back into the same block, and plenty of PIDEs wire both) had both
loops drawn at the exact same height (`bs.y - 12`) over the exact same two
vertical legs (`sx + 16` / `dx - 16`, fixed offsets off the block's own
edges) -- so the two loops sat exactly on top of each other rather than
reading as two separate feedback paths. An automated check on a 150-node,
207-edge map (build/route_wires_no_overlap.py's own test) turned up ~4,800
overlapping segment pairs, nearly all of them this.

Each loop off the same block now gets its own height AND its own pair of
legs, so a second loop clears the first in both dimensions instead of
retracing it.
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


OLD = """  for (const i of selfLoops){
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
"""

NEW = """  const loopRank = new Map();
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
"""

sub(OLD, NEW, "self-loops stack instead of coinciding")

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
