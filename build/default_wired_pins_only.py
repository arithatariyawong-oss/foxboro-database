# -*- coding: utf-8 -*-
"""Go back to drawing only the pins that carry a wire.

`show_all_block_pins.py` made the box list every connectable pin B0193AX
gives the type. On the plant's real blocks that is a lot of empty rail --
PIDE is 47 inputs against 5 wired, CALCA 29 against 2 -- and the map got
harder to read, not easier.

What the missing detail actually was is now known: it was never the pin
list, it was `export_graph.py` dropping 14,626 bit-qualified references, so
P3973:P3973ILK genuinely had four fewer wires than ICC showed. That is
fixed in the export, and with the wires back the free pins are just noise.

So the default flips to wired-only, which is what the map drew before
today. The ☰ button still switches the full set on for anyone who wants to
see what a type could carry -- the machinery is already built and tested,
and it is one button -- it simply is no longer what you get by default.
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
    "let ALL_PINS = true;\n",
    "let ALL_PINS = false;      /* wired pins only; ☰ turns the full set on */\n",
    "default to wired-only",
)

# the stored preference has to flip with it, or a browser that never touched
# the button would keep reading the old '0' default as "not the default"
sub(
    "try { if (localStorage.getItem('fox-map-allpins') === '0') ALL_PINS = false; } catch (e) {}\n",
    "try { if (localStorage.getItem('fox-map-allpins') === '1') ALL_PINS = true; } catch (e) {}\n",
    "stored preference reads the other way",
)

# and the comment above the toggle still claimed the full set was the default
sub(
    """/* Every pin the block has, or only the wired ones. Both are worth having and
   which one you want depends on the job — tracing a signal wants the wires
   alone, checking what is still free wants the whole set — so it is a toggle,
   remembered per browser rather than reset on every visit. */
""",
    """/* Only the wired pins by default: that is the diagram you want when you are
   tracing a signal, and on a PIDE it is 5 pins rather than 47. ☰ brings in
   every pin the type could carry, for when the question is what is still
   free instead of what is connected. Remembered per browser. */
""",
    "comment matches the new default",
)

# the legend note only makes sense while the free pins are on screen, and
# they now are not unless you ask for them
sub(
    '      <span style="opacity:.62">ชื่อขาสีจาง = ขาที่บล็อกมีแต่ยังไม่ได้ต่อสาย</span>\n',
    '      <span style="opacity:.62">☰ = แสดงทุกขาที่บล็อกมี (ขาว่างเป็นสีจาง)</span>\n',
    "legend note",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
