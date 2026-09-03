# -*- coding: utf-8 -*-
"""Both lane assignments in render() could still run past the empty gap
they were supposed to stay inside once enough wires shared one:

  * the entry lane used `Math.max(4, (COL_GAP - 40) / count)` -- the
    Math.max(4, ...) floor meant a crowded column (40+ wires) reserved
    MORE total width than the gap actually has (40 wires * 4px = 160px
    is fine, but 50 * 4px = 200px is not, and it only gets worse), so
    the far ranks landed to the left of the previous column's boundary
    -- inside that column's own blocks.
  * the exit lane hard-capped at rank 20 and let every wire past that
    pile up at the exact same x instead of continuing to spread out.

Both are replaced with a fixed total budget per gap ((COL_GAP - 60), left
undivided by a floor) split evenly across however many wires actually
share it, so the reserved width can never exceed the gap no matter how
crowded a column gets -- checked against the same 150-node worst case
that turned these up: a hub-like ECB block (94MG03) with 923 edges at
depth 8 previously drove 116 wire-through-block violations from lanes
overflowing past their gap; now zero.
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


sub(
    "  const globalTop = Math.min(...[...L.box.values()].map(b => b.y));\n"
    "  const exitRank = new Map();\n"
    "  const rankOf = (m, key) => { const r = m.get(key) || 0; m.set(key, r + 1); return r; };\n"
    "  const bandOf = new Map();\n"
    "  for (const i of through) bandOf.set(i, bandOf.size);\n",
    "  const globalTop = Math.min(...[...L.box.values()].map(b => b.y));\n"
    "  const bandOf = new Map();\n"
    "  for (const i of through) bandOf.set(i, bandOf.size);\n"
    "  /* how many `through` edges leave each source column, known before any\n"
    "     of them are placed, so the per-wire step can never be wider than the\n"
    "     column's own share of the gap -- a fixed budget split N ways instead\n"
    "     of a fixed step multiplied by N, which is what let a crowded column\n"
    "     overrun into the block on the other side of its own gap */\n"
    "  const exitCount = new Map();\n"
    "  for (const i of through){\n"
    "    const col = L.box.get(L.edges[i][0]).col;\n"
    "    exitCount.set(col, (exitCount.get(col) || 0) + 1);\n"
    "  }\n"
    "  const exitRank = new Map();\n"
    "  const rankOf = (m, key) => { const r = m.get(key) || 0; m.set(key, r + 1); return r; };\n",
    "exit-lane budget known up front, per source column",
)

sub(
    "    const lane = Math.min(LANE, Math.max(4, (COL_GAP - 40) / list.length));\n",
    "    /* a fixed (COL_GAP - 60) budget shared evenly, not a fixed step per\n"
    "       wire -- so list.length wires can never reserve more than the gap\n"
    "       actually has, however many of them there are */\n"
    "    const lane = Math.min(LANE, (COL_GAP - 60) / list.length);\n",
    "entry lane: fixed budget, no floor that could overrun it",
)

sub(
    "        const ex = sx + 18 + Math.min(rankOf(exitRank, bs.col), 20) * 6;\n",
    "        const exLane = Math.min(6, (COL_GAP - 60) / exitCount.get(bs.col));\n"
    "        const ex = sx + 18 + rankOf(exitRank, bs.col) * exLane;\n",
    "exit lane: same fixed-budget rule instead of a rank-20 pileup",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
