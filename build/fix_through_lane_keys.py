# -*- coding: utf-8 -*-
"""route_wires_no_overlap.py keyed each "through" edge's exit/entry step-off
by the source/target NODE, so two edges leaving different blocks that
happen to sit in the same column both got rank 0 -- same x, and with their
own bands close together in y, the vertical stubs actually overlapped.

All that offset is for is keeping wires from the same column's exit (or
the same column's entry) apart, so the key only needs to be the column,
not the node inside it.
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
    "    const ex = sx + 18 + Math.min(rankOf(exitRank, s), 20) * 6;\n"
    "    const en = dx - 18 - Math.min(rankOf(enterRank, t), 20) * 6;\n",
    "    const ex = sx + 18 + Math.min(rankOf(exitRank, bs.col), 20) * 6;\n"
    "    const en = dx - 18 - Math.min(rankOf(enterRank, bt.col), 20) * 6;\n",
    "exit/entry lanes keyed by column, not by node",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
