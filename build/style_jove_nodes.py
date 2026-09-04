# -*- coding: utf-8 -*-
"""Draw the Jove objects on the signal map, and give them a Properties panel
that does not pretend to be a Foxboro block.

build/add_jove_to_graph.py put 18,502 Jove objects into graph.js as nodes with
TYPE 'JOVE'. Three things follow from a Jove node being a different kind of
thing from every node already there:

  * It needs its own colour. ECB (the FBM hardware end) is already amber, so
    Jove gets a violet head -- the map now says at a glance which side of a
    block is field I/O and which is the historian/API host.
  * It has NO data.js row: field 7 is -1, because a Jove object is not a
    Foxboro block and has no parameter record. openProps() fed that straight
    into rowValues(-1), which walks 1,202 sparse columns looking for row -1
    and quietly returns nothing -- a Properties panel that sits on
    "กำลังอ่านค่า…" forever after loading 2.4 MB for no reason. A Jove node
    now shows what it actually has (host, attribute, description, and the
    Foxboro parameter it is bound to) without touching data.js at all.
  * Direction is the whole point. 5,985 of the 20,434 connections are Jove
    WRITING into the DCS, and the panel says which way this one runs, because
    "the historian can move this valve" is not a detail to leave implicit.
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


# ---- tokens, light and dark -------------------------------------------
sub(
    "  --ecb-head:#f0dcb6; --ecb-edge:#c2a161; --ecb-ink:#4a3610;\n",
    "  --ecb-head:#f0dcb6; --ecb-edge:#c2a161; --ecb-ink:#4a3610;\n"
    "  --jove-head:#ded7f2; --jove-edge:#9b8ac9; --jove-ink:#2f2452;\n",
    "light tokens for a Jove node",
)
sub(
    "  --ecb-head:#5a4a24; --ecb-edge:#a08745; --ecb-ink:#f4e6c6;\n",
    "  --ecb-head:#5a4a24; --ecb-edge:#a08745; --ecb-ink:#f4e6c6;\n"
    "  --jove-head:#3c3260; --jove-edge:#8878b8; --jove-ink:#e4dcf7;\n",
    "dark tokens for a Jove node",
)

sub(
    ".blk.ecb .blk-name,.blk.ecb .blk-desc,.blk.ecb .blk-type{fill:var(--ecb-ink)}\n",
    ".blk.ecb .blk-name,.blk.ecb .blk-desc,.blk.ecb .blk-type{fill:var(--ecb-ink)}\n"
    ".blk.jove .blk-head{fill:var(--jove-head); stroke:var(--jove-edge)}\n"
    ".blk.jove .blk-face{stroke:var(--jove-edge)}\n"
    ".blk.jove .blk-name,.blk.jove .blk-desc,.blk.jove .blk-type{fill:var(--jove-ink)}\n",
    "CSS for a Jove node",
)
sub(
    ".blk.ecb{--flash-base:var(--ecb-edge)}\n",
    ".blk.ecb{--flash-base:var(--ecb-edge)}\n"
    ".blk.jove{--flash-base:var(--jove-edge)}\n",
    "the ?tag= flash reads the Jove edge colour too",
)

# ---- the legend --------------------------------------------------------
sub(
    '      <span><i style="background:var(--ecb-head);border-color:var(--ecb-edge)"></i>'
    "ECB (โมดูล FBM)</span>\n",
    '      <span><i style="background:var(--ecb-head);border-color:var(--ecb-edge)"></i>'
    "ECB (โมดูล FBM)</span>\n"
    '      <span><i style="background:var(--jove-head);border-color:var(--jove-edge)"></i>'
    "Jove (OPC / historian)</span>\n",
    "legend entry",
)

# ---- draw it as its own kind ------------------------------------------
sub(
    "    const isEcb = TYPE(n).startsWith('ECB');\n",
    "    const isEcb = TYPE(n).startsWith('ECB'), isJove = TYPE(n) === 'JOVE';\n",
    "isJove alongside isEcb",
)
sub(
    "    let g = `<g class=\"blk${isRoot ? ' root' : ''}${isEcb ? ' ecb' : ''}\" data-n=\"${n}\"` +\n",
    "    let g = `<g class=\"blk${isRoot ? ' root' : ''}${isEcb ? ' ecb' : ''}`\n"
    "          + `${isJove ? ' jove' : ''}\" data-n=\"${n}\"` +\n",
    "the .jove class on the box",
)

# ---- Properties, without a data.js row --------------------------------
sub(
    "  try { await loadData(); } catch (err){\n"
    "    el.querySelector('.props-body').innerHTML = `<p class=\"props-note\">${esc(err.message)}</p>`;\n"
    "    return;\n"
    "  }\n"
    "  if (propsEl !== el) return;                     // closed while loading\n"
    "  propsRows = rowValues(NODES[n][7]);\n",
    "  /* A Jove object has no parameter record — field 7 is -1. Reading it out\n"
    "     of data.js would download 2.4 MB to walk 1,202 sparse columns looking\n"
    "     for a row that does not exist and come back empty. Everything a Jove\n"
    "     object has is already on the node and its edges. */\n"
    "  if (NODES[n][7] < 0){\n"
    "    const link = [];\n"
    "    for (const e of EDGES){\n"
    "      if (e[0] === n) link.push(['เขียนไปที่', NAME(e[2]) + '.' + e[3]]);\n"
    "      else if (e[2] === n) link.push(['อ่านจาก', NAME(e[0]) + '.' + e[1]]);\n"
    "    }\n"
    "    el.querySelector('.props-body').innerHTML =\n"
    "      `<div class=\"props-sec\">Jove object</div>` +\n"
    "      [['ชื่อ object', NAME(n)], ['attribute', PNT(n)],\n"
    "       ['API host', CP(n)], ['คำอธิบาย', DESC(n) || '—']]\n"
    "        .map(([k, v]) => `<div class=\"prow\"><div class=\"k\">${esc(k)}</div>` +\n"
    "                         `<div class=\"v\">${esc(v)}</div></div>`).join('') +\n"
    "      `<div class=\"props-sec\">ผูกกับพารามิเตอร์</div>` +\n"
    "      (link.length\n"
    "        ? link.map(([k, v]) => `<div class=\"prow\"><div class=\"k\">${esc(k)}</div>` +\n"
    "            `<div class=\"v ref\" data-go=\"${esc(v.split('.')[0])}\">${esc(v)}</div></div>`).join('')\n"
    "        : `<p class=\"props-note\">ไม่ได้ผูกกับบล็อกไหน</p>`);\n"
    "    return;\n"
    "  }\n"
    "\n"
    "  try { await loadData(); } catch (err){\n"
    "    el.querySelector('.props-body').innerHTML = `<p class=\"props-note\">${esc(err.message)}</p>`;\n"
    "    return;\n"
    "  }\n"
    "  if (propsEl !== el) return;                     // closed while loading\n"
    "  propsRows = rowValues(NODES[n][7]);\n",
    "Properties for a Jove object reads the node, not data.js",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
