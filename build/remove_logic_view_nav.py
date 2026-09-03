# -*- coding: utf-8 -*-
"""Take LOGIC VIEW back out of the shared nav bar (undoes
add_logic_view_nav.py on the five pages it touched).

Logic View is no longer a page you navigate to -- it is a popup off a
block's own menu (see add_logic_popup.py on signal-map.html), offered only
where a block actually has one to show. Advertising it as a seventh -- er,
sixth -- pill in the shared bar suggested it was a page like the other
five; it never was one to get to that way, and now nothing in the bar
claims otherwise. logic-view.html itself is untouched here: its own copy
of the bar is already hidden unconditionally (hide_logic_chrome.py), and
the page is still reachable by the deep link the popup opens
(`logic-view.html?tag=...`).
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent

LINK = '    <a href="logic-view.html"><b>LOGIC VIEW</b><i>ผังลอจิกจาก step</i></a>\n'

targets = ["index.html", "signal-map.html", "system-manager.html",
           "system-monitor.html", "modbus.html"]

for name in targets:
    path = WEB / name
    s = io.open(path, encoding="utf8").read()
    n_before = len(s)
    if s.count(LINK) != 1:
        sys.exit("ABORT: %s -- nav anchor found %d times, expected 1"
                  % (name, s.count(LINK)))
    s = s.replace(LINK, "", 1)
    io.open(path, "w", encoding="utf8", newline="").write(s)
    print("  ok  %-22s LOGIC VIEW removed from nav (%d -> %d chars)"
          % (name, n_before, len(s)))

print("done")
