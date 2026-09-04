# -*- coding: utf-8 -*-
"""Start both map pages quiet, so the first screen is a question and not an
answer to a question nobody asked.

SIGNAL MAP — the chain-length slider defaulted to 4. On a well-connected block
that is a wall: four hops out of a PID reaches the whole loop plus its
neighbours, and the first thing you have to do is drag the slider back down to
find the block you came for. Starts at 1 now: the root and what touches it
directly. Turning it up is one drag; untangling 150 boxes to find your bearings
is not.

SYSTEM MANAGER — boot ran `pickCp(0)`, which filled all six block panes with
whatever station happened to sort first. That is 300 rows of Block List, a full
type histogram and a Block Properties table about a station the user never
asked for, and on ALL NETWORK the same panes are computed over 77,010 rows.
The six panes now stay empty until an equipment is actually picked from the
rail. Foxboro Network and the rail itself still draw at boot -- they ARE the
picker -- and Block Mapping already had its own "pick a block" empty state.

A deep link still lands exactly where it did: `?tag=` and `?cp=` both count as
a pick, because the user chose the block by following the link.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent


def edit(path, jobs):
    s = io.open(path, encoding="utf8").read()
    n0 = len(s)
    for old, new, what in jobs:
        if s.count(old) != 1:
            sys.exit("ABORT: %s -- anchor found %d times, expected 1"
                     % (what, s.count(old)))
        s = s.replace(old, new, 1)
        print("  ok  %s" % what)
    io.open(path, "w", encoding="utf8", newline="").write(s)
    print("%s %d -> %d chars (%+d)" % (path.name, n0, len(s), len(s) - n0))


# ---- 1. SIGNAL MAP: open one hop out ------------------------------------
edit(WEB / "signal-map.html", [
    (
        '        <input type="range" id="depth" min="1" max="8" value="4">\n'
        '        <b id="depthN">4</b>\n',
        '        <input type="range" id="depth" min="1" max="8" value="1">\n'
        '        <b id="depthN">1</b>\n',
        "signal-map: chain length starts at 1",
    ),
])

# ---- 2. SYSTEM MANAGER: the block panes wait to be asked -----------------
edit(WEB / "system-manager.html", [
    (
        "let selMod = -1, MODROWS = null;\n",
        "let selMod = -1, MODROWS = null;\n"
        "/* Nothing is picked until the user picks it. The six block panes are\n"
        "   blank while this is false — see render(). It is NOT the same as\n"
        "   selCp === -1, which is the real, deliberate ALL NETWORK scope and\n"
        "   still fills them. */\n"
        "let picked = false;\n",
        "system-manager: the `picked` flag",
    ),
    (
        "function render(){\n"
        "  drawTree(); drawNet(); drawCrumb(); drawParam(); drawClist(); drawCprops();\n"
        "  drawTypes(); drawBlist(); drawBprops(); drawMap();\n"
        "}\n",
        "const PICK_ME = '<p class=\"empty\">เลือกอุปกรณ์จากผังทางซ้าย '\n"
        "  + '(station · FBM · ช่องสัญญาณ) เพื่อดูข้อมูลส่วนนี้</p>';\n"
        "function render(){\n"
        "  drawTree(); drawNet(); drawCrumb();\n"
        "  if (!picked){\n"
        "    /* Skipped, not hidden: on ALL NETWORK these three walk 77,010 rows\n"
        "       to build a compound list, a type histogram and a block table that\n"
        "       nobody has asked for yet. */\n"
        "    for (const id of ['param', 'clist', 'cprops', 'types', 'blist', 'bprops'])\n"
        "      $('#' + id).innerHTML = PICK_ME;\n"
        "    for (const id of ['nPar', 'nCmp', 'nBlk']) $('#' + id).textContent = '';\n"
        "    drawMap();\n"
        "    return;\n"
        "  }\n"
        "  drawParam(); drawClist(); drawCprops();\n"
        "  drawTypes(); drawBlist(); drawBprops(); drawMap();\n"
        "}\n",
        "system-manager: render() leaves the six panes blank until a pick",
    ),
])

# every route into a selection counts as the pick
s = io.open(WEB / "system-manager.html", encoding="utf8").read()
n0 = len(s)
n = 0
for fn in ("function pickCp(", "function pickMod(", "function pickComp(",
           "function gotoRow("):
    i = s.find(fn)
    if i < 0:
        sys.exit("ABORT: %s not found" % fn)
    j = s.index("\n", s.index("{", i)) + 1
    s = s[:j] + "  picked = true;\n" + s[j:]
    n += 1
    print("  ok  %s marks the selection as picked" % fn.split("(")[0][9:])
io.open(WEB / "system-manager.html", "w", encoding="utf8", newline="").write(s)
print("system-manager.html %d -> %d chars (%+d)" % (n0, len(s), len(s) - n0))

# ---- boot: do not pick the first station for the user --------------------
edit(WEB / "system-manager.html", [
    (
        "    if (!done && cp && CPN.has(cp)){ pickCp(CPN.get(cp)); done = true; }\n"
        "    if (!done) pickCp(CPS.length ? 0 : -1);\n",
        "    if (!done && cp && CPN.has(cp)){ pickCp(CPN.get(cp)); done = true; }\n"
        "    /* No deep link means no choice has been made yet. Draw the rail and\n"
        "       the network — the two panes you choose FROM — and leave the rest\n"
        "       blank rather than answering for a station picked alphabetically. */\n"
        "    if (!done) render();\n",
        "system-manager: boot no longer picks station 0",
    ),
])
