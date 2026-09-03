# -*- coding: utf-8 -*-
"""Drop logic-view.html's topbar (title + search box + fit/theme buttons)
and page-nav bar for good, not just in the `?embed=1` popup case
(add_logic_embed_mode.py) -- the user asked for the standalone page itself
to be nothing but the diagram and the step listing.

The page is still reached the same ways it always was (a deep link's
`?tag=`, or Back) -- it just no longer carries the search box or the
six-page nav row while doing it.

The override has to be the LAST rule in the sheet: .topbar and .pagenav
already have their own `display:flex` further up, and CSS resolves two
rules of equal specificity by source order, not by which one "sounds like"
an override -- put a `display:none` for the same selector ABOVE that and
the later `display:flex` still wins. (First version of this script made
exactly that mistake, appending right after the top of the sheet instead
of the end; fixed here.)
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
    ".badge.ok{background:var(--mint); border-color:var(--mint-deep); color:#17352b}\n</style>",
    ".badge.ok{background:var(--mint); border-color:var(--mint-deep); color:#17352b}\n"
    "\n"
    "/* no topbar, no page-nav row -- just the diagram and the step listing. A\n"
    "   popup iframe has no room for a page's own chrome (see add_logic_popup.py\n"
    "   on signal-map.html), and the standalone page does not want it either: it\n"
    "   is reached by a deep link's `?tag=`, same as before. Last in the sheet\n"
    "   on purpose -- .topbar and .pagenav are defined further up with their own\n"
    "   `display:flex`, which would otherwise win the cascade over an earlier\n"
    "   `display:none`. */\n"
    "body{padding:10px}\n"
    ".topbar, .pagenav{display:none}\n"
    ".app{height:calc(100vh - 20px)}\n"
    "</style>",
    "CSS: topbar + pagenav hidden unconditionally, last in the sheet",
)

sub(
    "\"use strict\";\nconst $ = s => document.querySelector(s);\n"
    "if (new URLSearchParams(location.search).get('embed') === '1')\n"
    "  document.body.classList.add('embed');\n",
    "\"use strict\";\nconst $ = s => document.querySelector(s);\n",
    "JS: drop the now-unused embed query-string toggle",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("logic-view.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
