# -*- coding: utf-8 -*-
"""Give logic-view.html a `?embed=1` mode: no topbar, no six-page nav bar,
just the diagram and the step listing filling the frame.

Built for `add_logic_popup.py`, which opens this page inside an iframe from
signal-map.html's block menu -- a modal popup has no use for a page's own
search box or the row of links back to itself and five other pages it is
already floating on top of.
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


sub(
    ".app{width:100%; margin:0 auto; display:flex; flex-direction:column; gap:16px; height:calc(100vh - 48px)}\n",
    ".app{width:100%; margin:0 auto; display:flex; flex-direction:column; gap:16px; height:calc(100vh - 48px)}\n"
    "/* a popup iframe has no room, and no use, for this page's own chrome --\n"
    "   see add_logic_popup.py on signal-map.html */\n"
    "body.embed{padding:10px}\n"
    "body.embed .topbar, body.embed .pagenav{display:none}\n"
    "body.embed .app{height:calc(100vh - 20px)}\n",
    "embed CSS: hide topbar + pagenav, tighten body padding",
)

sub(
    '"use strict";\nconst $ = s => document.querySelector(s);\n',
    '"use strict";\nconst $ = s => document.querySelector(s);\n'
    "if (new URLSearchParams(location.search).get('embed') === '1')\n"
    "  document.body.classList.add('embed');\n",
    "embed JS: flip the class from the query string",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("logic-view.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
