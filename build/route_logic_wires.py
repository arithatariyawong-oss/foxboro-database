# -*- coding: utf-8 -*-
"""Same bug as signal-map.html's block-wiring diagram, in the gate sheet
this time (see build/route_wires_no_overlap.py, unify_entry_lanes.py,
clamp_lanes_to_gap.py on that file for the full history).

`layout()` gives a node a column = 1 + its DEEPEST input's column, so an
`AND` combining a raw BI pin (column 0) with an already-computed
intermediate (column 4) sits at column 5 -- and the wire from that BI pin
used to run straight across at its own height all the way to column 5,
through whatever gate happened to occupy columns 1-4 at that row. This is
a common shape here, not a rare one: a program very often combines a fresh
field input with a value several steps deep.

Unlike signal-map.html this sheet is a DAG (a stack program can't feed
back into an earlier instruction), so there is no feedback case to route --
only "column-adjacent" (draw straight across the gap, which is always
empty) and "skip" (route above the whole sheet, one row per wire, the one
place no gate ever stands). Both kinds still converge on the same target
column through the same narrow gap, so they share one entry-lane counter
per target COLUMN rather than two that don't know about each other, and
every lane budget is a fixed share of the gap (COLGAP - 34) rather than a
fixed step per wire, so a crowded column can't reserve more width than the
gap has.

A first version of this fix anchored each lane to the individual target/
source BOX's own x. That is wrong here in a way it never was on
signal-map.html: a column here can mix a wide IO box with a narrower gate
box centred inside the same reserved width, so a box's own x is not
always clear of its neighbours -- another box already sitting further out
in the same column can be in the way. Fixed by anchoring every lane to the
column's shared edges (the widest box's x / x+w) instead of any one box's
own.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "logic-view.html"

s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


OLD = """function render(L){
  const { nodes, outs, box } = L;
  const parts = [], wires = [];
  const anchorOut = k => { const b = box.get(k); return [b.x + b.w, b.y + b.h / 2]; };

  /* wires first so the boxes sit on top */
  let wi = 0;
  const legY = (b, i, n) => b.y + b.h * (i + 1) / (n + 1);
  for (const id of L.used){
    const n = nodes[id], b = box.get('n' + id);
    n.ins.forEach((src, i) => {
      const [sx, sy] = anchorOut('n' + src);
      const dy = legY(b, i, n.ins.length), dx = b.x;
      wires.push({ i: wi++, sx, sy, dx, dy });
    });
  }
  outs.forEach((o, k) => {
    if (o.src == null) return;
    const [sx, sy] = anchorOut('n' + o.src);
    const b = box.get('o' + k);
    wires.push({ i: wi++, sx, sy, dx: b.x, dy: b.y + b.h / 2 });
  });
  for (const w of wires){
    const mx = w.dx - 26;
    const d = `M${w.sx} ${w.sy} H${Math.max(mx, w.sx + 10)} V${w.dy} H${w.dx}`;
    parts.push(`<path class="lg-wire" d="${d}"></path>`);
    parts.push(`<path class="lg-arrow" d="M${w.dx} ${w.dy} l-7 -3.6 v7.2 z"></path>`);
  }"""

NEW = """function render(L){
  const { nodes, outs, box } = L;
  const parts = [];
  const anchorOut = k => { const b = box.get(k); return [b.x + b.w, b.y + b.h / 2]; };
  const legY = (b, i, n) => b.y + b.h * (i + 1) / (n + 1);

  /* ---- wires first, so boxes sit on top ----
     A column-adjacent wire (target column === source column + 1) crosses
     only the empty gap between the two, so it is drawn straight across.
     Everything else -- a shallow input reaching a gate several columns
     deeper -- is routed above the whole sheet instead, one row per wire
     (no two ever share a row, so no two of these can coincide), the one
     stretch of the sheet no gate ever occupies regardless of how many
     columns it skips. This is a DAG (a stack program cannot feed back
     into an earlier step), so unlike signal-map.html there is no
     feedback case to handle.

     Both kinds still land on the target column through the same narrow
     gap in front of it, so they share ONE entry-lane counter per target
     COLUMN -- an adjacent wire and a skip wire converging on the same
     column no longer get handed the same x by two counters that do not
     know about each other. Every lane budget is a fixed share of the gap
     (`COLGAP - 34`, split by how many wires actually use it) rather than
     a fixed step per wire, so a crowded column can never reserve more
     width than the gap actually has. */
  const raw = [];
  let wi = 0;
  for (const id of L.used){
    const n = nodes[id], tk = 'n' + id, b = box.get(tk);
    n.ins.forEach((src, i) => {
      const sk = 'n' + src, sb = box.get(sk);
      const [sx, sy] = anchorOut(sk);
      raw.push({ i: wi++, sx, sy, dx: b.x, dy: legY(b, i, n.ins.length), sd: sb.d, td: b.d });
    });
  }
  outs.forEach((o, k) => {
    if (o.src == null) return;
    const sk = 'n' + o.src, sb = box.get(sk), tk = 'o' + k, b = box.get(tk);
    const [sx, sy] = anchorOut(sk);
    raw.push({ i: wi++, sx, sy, dx: b.x, dy: b.y + b.h / 2, sd: sb.d, td: b.d });
  });

  const through = new Set(), byTargetCol = new Map();
  for (const w of raw){
    if (w.td !== w.sd + 1) through.add(w.i);
    if (!byTargetCol.has(w.td)) byTargetCol.set(w.td, []);
    byTargetCol.get(w.td).push(w.i);
  }

  /* a column can mix a wide IO box with a narrower gate box, centred
     inside the same reserved width -- so a box's OWN x is not always a
     safe lane anchor, another box already sitting further out in the
     same column can be in the way. Anchor every lane to the column's
     shared edges instead: the widest box in a column has no centring
     offset, so the minimum x at a given depth is that column's true
     left edge, and x+w's maximum is its true right edge. */
  const colLeft = new Map(), colRight = new Map();
  for (const b of box.values()){
    colLeft.set(b.d, Math.min(colLeft.has(b.d) ? colLeft.get(b.d) : Infinity, b.x));
    colRight.set(b.d, Math.max(colRight.has(b.d) ? colRight.get(b.d) : -Infinity, b.x + b.w));
  }

  const BUDGET = COLGAP - 34;
  const globalTop = Math.min(...[...box.values()].map(b => b.y));
  const bandOf = new Map();
  for (const i of through) bandOf.set(i, bandOf.size);
  const exitCount = new Map();
  for (const i of through) exitCount.set(raw[i].sd, (exitCount.get(raw[i].sd) || 0) + 1);
  const exitRank = new Map();
  const rankOf = (m, key) => { const r = m.get(key) || 0; m.set(key, r + 1); return r; };

  const wires = [];
  for (const [td, list] of byTargetCol){
    /* rank by the row each wire actually runs at, so lanes fan out in
       travel order instead of crossing right at the gap's mouth */
    list.sort((ia, ib) => (raw[ia].sy + raw[ia].dy) - (raw[ib].sy + raw[ib].dy));
    const lane = Math.min(10, BUDGET / list.length);
    list.forEach((i, rank) => {
      const w = raw[i];
      const enterX = colLeft.get(td) - 14 - rank * lane;
      let d;
      if (!through.has(i)){
        d = `M${w.sx} ${w.sy} H${enterX} V${w.dy} H${w.dx}`;
      } else {
        const ry = globalTop - 18 - bandOf.get(i) * 10;          // its own row, never reused
        const exLane = Math.min(5, BUDGET / exitCount.get(w.sd));
        const ex = colRight.get(w.sd) + 10 + rankOf(exitRank, w.sd) * exLane;
        d = `M${w.sx} ${w.sy} H${ex} V${ry} H${enterX} V${w.dy} H${w.dx}`;
      }
      wires.push({ i, d, dx: w.dx, dy: w.dy });
    });
  }
  wires.sort((a, b) => a.i - b.i);
  for (const w of wires){
    parts.push(`<path class="lg-wire" d="${w.d}"></path>`);
    parts.push(`<path class="lg-arrow" d="M${w.dx} ${w.dy} l-7 -3.6 v7.2 z"></path>`);
  }"""

sub(OLD, NEW, "logic-view render(): block-safe, collision-free wire routing")

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("logic-view.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
