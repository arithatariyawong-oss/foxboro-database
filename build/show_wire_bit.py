# -*- coding: utf-8 -*-
"""Print the bit / boolean qualifier a wire carries, next to the pin it lands on.

`export_graph.py` used to require a reference to be exactly
COMPOUND:BLOCK.PARAM, so every value with a third dot-separated token was
dropped on the floor -- 14,626 wires, a QUARTER of the plant's parameter
wiring. P3973:P3973ILK is the block that showed it: ICC lists seven input
references (11.png) and the map drew three, missing exactly the four written
`...ALMSTA.B15` style.

The export now keeps that tail as a fifth field on the edge, and this puts it
on the diagram, because a bit reference without its bit number is not the same
wire -- V3973:39LISA223.ALMSTA drives BI02, BI03 and BI04 from three DIFFERENT
bits of one status word, and drawn bare those three are indistinguishable.

The label goes just before the arrow head rather than at the source pin: a
destination pin takes exactly one wire, so there is nothing for it to collide
with, whereas one PAKCIN pin fans out to as many as 32 bits at the source and
they would all stack on the same y.
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


# ---- 1. CSS -------------------------------------------------------------
sub(
    ".pin-io{font-size:9.5px; fill:var(--text-faint)}\n",
    ".pin-io{font-size:9.5px; fill:var(--text-faint)}\n"
    "/* the bit a wire picks out of a packed word, e.g. ALMSTA .B15 */\n"
    ".qual{font-size:9px; font-weight:800; fill:var(--text-dim); paint-order:stroke;\n"
    "  stroke:var(--canvas); stroke-width:2.6; stroke-linejoin:round}\n"
    ".qual.hot{fill:var(--wire-hot)}\n",
    "CSS .qual",
)

# ---- 2. the edge comment, so the 5th field is documented where it is read
sub(
    """   nodes: [name, type, descrp, cp, area, iom, pnt]
   edges: [srcNode, srcParam, dstNode, dstParam]
""",
    """   nodes: [name, type, descrp, cp, area, iom, pnt]
   edges: [srcNode, srcParam, dstNode, dstParam, qualifier?]
          the 5th is present only when the reference carried one: the bit of
          a packed word (`ALMSTA.B15`, `PAKCIN.B3`) or the boolean form's
          trailing digit (`MA.1`). 24% of edges have one; the rest are 4 long.
""",
    "edge shape comment",
)

# ---- 3. carry it through the wire build ---------------------------------
sub(
    """    const [s, sp, t, tp] = e;
""",
    """    const [s, sp, t, tp, qual] = e;
""",
    "destructure the qualifier",
)

sub(
    "    wires.push({ i, d, s, t, sp, tp, dx, dy });\n",
    "    wires.push({ i, d, s, t, sp, tp, dx, dy, qual });\n",
    "carry it on the wire record",
)

# ---- 4. draw it ---------------------------------------------------------
sub(
    """    parts.push(`<path class="arrow" id="a${w.i}" d="M${w.dx} ${w.dy} l-7 -3.6 v7.2 z"></path>`);
""",
    """    parts.push(`<path class="arrow" id="a${w.i}" d="M${w.dx} ${w.dy} l-7 -3.6 v7.2 z"></path>`);
    if (w.qual)
      parts.push(`<text class="qual" id="q${w.i}" x="${w.dx - 10}" y="${w.dy - 3.5}"` +
                 ` text-anchor="end">${esc(w.qual)}</text>`);
""",
    "draw the qualifier",
)

# ---- 5. light it with the rest of the wire on hover ----------------------
sub(
    """  world.querySelectorAll('.wire, .arrow').forEach(el => el.classList.remove('hot'));
  if (idx === null) { world.querySelectorAll('.blk').forEach(el => el.classList.remove('dim')); return; }
  const w = document.getElementById('w' + idx), a = document.getElementById('a' + idx);
  if (w) w.classList.add('hot'); if (a) a.classList.add('hot');
""",
    """  world.querySelectorAll('.wire, .arrow, .qual').forEach(el => el.classList.remove('hot'));
  if (idx === null) { world.querySelectorAll('.blk').forEach(el => el.classList.remove('dim')); return; }
  const w = document.getElementById('w' + idx), a = document.getElementById('a' + idx);
  const q = document.getElementById('q' + idx);
  if (w) w.classList.add('hot'); if (a) a.classList.add('hot'); if (q) q.classList.add('hot');
""",
    "hover lights the qualifier",
)

# ---- 6. and spell the whole reference out in the tooltip, the way ICC's
#         Input References pane prints it -------------------------------
sub(
    """  tip.innerHTML = `<b>${esc(NAME(w[0]))}.${esc(w[1])} → ${esc(NAME(w[2]))}.${esc(w[3])}</b>` +
""",
    """  tip.innerHTML = `<b>${esc(NAME(w[0]))}.${esc(w[1])}${w[4] ? '.' + esc(w[4]) : ''}` +
    ` → ${esc(NAME(w[2]))}.${esc(w[3])}</b>` +
""",
    "tooltip prints the full reference",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (+%d)" % (n_before, len(s), len(s) - n_before))
