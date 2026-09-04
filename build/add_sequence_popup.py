# -*- coding: utf-8 -*-
"""Add a "Sequence View" item to signal-map.html's block menu.

Offered on IND blocks and nowhere else. Unlike the Logic View item next to
it, this needs no background index to decide: a block has a sequence program
if and only if its TYPE is IND, and the map already knows every node's type.
sequence.js (0.48 MB) is therefore never fetched until someone actually opens
the popup, which is the iframe's own business.

The modal machinery is the one add_logic_popup.py already put in — same
backdrop, same shell, same Escape handling — so `openLogicPopup(n)` is
widened here into `openViewPopup(n, url)` and the two entry points become
thin wrappers. Widening rather than copying is the point: a second modal
with its own element handle is a second thing to forget to close.
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


# ---- the menu item -------------------------------------------------------
sub(
    "    (LOGIC_NAMES && LOGIC_NAMES.has(NAME(n))\n"
    "      ? `<button data-a=\"logic\">Logic View…<i>step program</i></button>` : '') +\n",
    "    (LOGIC_NAMES && LOGIC_NAMES.has(NAME(n))\n"
    "      ? `<button data-a=\"logic\">Logic View…<i>step program</i></button>` : '') +\n"
    "    /* TYPE is enough on its own here — every IND block has an HLBL source\n"
    "       and nothing else does, so there is no index to wait for. */\n"
    "    (TYPE(n) === 'IND'\n"
    "      ? `<button data-a=\"seq\">Sequence View…<i>โปรแกรม + reference</i></button>` : '') +\n",
    "menu: Sequence View item on IND blocks",
)

sub(
    "    else if (a.dataset.a === 'logic') openLogicPopup(n);\n",
    "    else if (a.dataset.a === 'logic') openLogicPopup(n);\n"
    "    else if (a.dataset.a === 'seq') openSeqPopup(n);\n",
    "menu click: seq -> openSeqPopup",
)

# ---- widen the popup, and hang both views off it -------------------------
sub(
    "let logicEl = null;\n"
    "function closeLogicPopup(){ if (logicEl){ logicEl.remove(); logicEl = null; } }\n"
    "function openLogicPopup(n){\n"
    "  closeLogicPopup();\n",
    "let logicEl = null;\n"
    "function closeLogicPopup(){ if (logicEl){ logicEl.remove(); logicEl = null; } }\n"
    "/* Both block views open the same way and into the same handle, so Escape\n"
    "   and the backdrop keep working without knowing which one is up. */\n"
    "function openLogicPopup(n){\n"
    "  openViewPopup(n, `logic-view.html?tag=${encodeURIComponent(NAME(n))}&embed=1`);\n"
    "}\n"
    "function openSeqPopup(n){\n"
    "  openViewPopup(n, `sequence-view.html?tag=${encodeURIComponent(NAME(n))}`);\n"
    "}\n"
    "function openViewPopup(n, url){\n"
    "  closeLogicPopup();\n",
    "widen openLogicPopup into openViewPopup(n, url)",
)

sub(
    "      `<iframe src=\"logic-view.html?tag=${encodeURIComponent(NAME(n))}&embed=1\"></iframe>` +\n",
    "      `<iframe src=\"${esc(url)}\"></iframe>` +\n",
    "the iframe takes the url it was given",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
