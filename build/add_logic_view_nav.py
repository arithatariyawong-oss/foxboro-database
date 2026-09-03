# -*- coding: utf-8 -*-
"""Put LOGIC VIEW into the shared nav bar on the five older pages.

logic-view.html already carries the full six-page bar (it is assembled with
one), so only the pages that predate it need the entry. It goes immediately
after SIGNAL MAP, which is where it belongs: signal map is the wiring
BETWEEN blocks, logic view is the logic INSIDE one, and a person tracing an
interlock moves from the first to the second.

signal-map.html marks its own entry with aria-current, so its anchor differs
from the other four and is handled separately.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent

LINK = ('<a href="logic-view.html"><b>LOGIC VIEW</b>'
        '<i>ผังลอจิกจาก step</i></a>')

PLAIN = '<a href="signal-map.html"><b>SIGNAL MAP</b><i>ผังการเดินสัญญาณ</i></a>'
CURRENT = ('<a href="signal-map.html" aria-current="page"><b>SIGNAL MAP</b>'
           '<i>ผังการเดินสัญญาณ</i></a>')

targets = [
    ("index.html", PLAIN),
    ("system-manager.html", PLAIN),
    ("system-monitor.html", PLAIN),
    ("modbus.html", PLAIN),
    ("signal-map.html", CURRENT),
]

for name, anchor in targets:
    path = WEB / name
    s = io.open(path, encoding="utf8").read()
    if LINK in s:
        print("  --  %-22s already has it" % name)
        continue
    if s.count(anchor) != 1:
        sys.exit("ABORT: %s -- nav anchor found %d times, expected 1"
                 % (name, s.count(anchor)))
    s = s.replace(anchor, anchor + "\n    " + LINK, 1)
    io.open(path, "w", encoding="utf8", newline="").write(s)
    print("  ok  %-22s LOGIC VIEW added after SIGNAL MAP" % name)

print("done")
