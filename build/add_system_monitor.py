# -*- coding: utf-8 -*-
"""Embed the SF Compact faces into system-monitor.html and link the three pages.

Two jobs, both idempotent so the script can be re-run after an edit:

  1. system-monitor.html ships with a /*FONTS*/ marker instead of 180 KB of
     base64. A page opened from file:// will not load an @font-face from a
     relative path in Chrome, so the two woff2 subsets have to be inlined --
     they are lifted verbatim out of index.html rather than re-encoded, so all
     three pages carry byte-identical faces.
  2. index.html and signal-map.html get a SYSTEM MONITOR button in their
     topbar, next to the buttons that are already there.

SUPERSEDED on 2026-08-31 by build/add_page_nav.py, which took those cross-page
links out of the topbars and put all three pages in one shared nav bar under
the title card -- and relabelled the third page FBM MODULE MANAGEMENT. Step 2
here is a no-op now (it sees the page already links to the monitor and skips);
step 1, the font embedding, is still the live path.

Every replacement asserts on a miss; a silent no-op here would ship a page
with no font or no way to reach it.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
IDX = os.path.join(WEB, "index.html")
MAP = os.path.join(WEB, "signal-map.html")
MON = os.path.join(WEB, "system-monitor.html")

FACE = re.compile(r'@font-face\{font-family:"SF Compact".*?\}', re.S)


def read(p):
    return open(p, encoding="utf8").read()


def write(p, s):
    open(p, "w", encoding="utf8", newline="\n").write(s)


# ---- 1. fonts ------------------------------------------------------------
faces = FACE.findall(read(IDX))
assert len(faces) == 2, "expected 2 @font-face rules in index.html, got %d" % len(faces)

mon = read(MON)
if "/*FONTS*/" in mon:
    mon = mon.replace("/*FONTS*/", "\n".join(faces), 1)
    print("fonts embedded (%.0f KB)" % (sum(len(f) for f in faces) / 1024))
else:
    # already embedded: refresh in place so a font change propagates
    have = FACE.findall(mon)
    assert len(have) == 2, "system-monitor.html has neither the marker nor 2 faces"
    for old, new in zip(have, faces):
        mon = mon.replace(old, new, 1)
    print("fonts refreshed")
write(MON, mon)

# ---- 2. the link into the new page --------------------------------------
BTN = ('<a class="btn" href="system-monitor.html" '
       'title="อุปกรณ์และ spare point '
       'ของแต่ละ system">SYSTEM MONITOR</a>')

for path, anchor in (
    (IDX, '<button class="btn" id="csvBtn">Export CSV</button>'),
    (MAP, '<label class="search">'),
):
    s = read(path)
    if "system-monitor.html" in s:
        print("%s already links to the monitor" % os.path.basename(path))
        continue
    assert s.count(anchor) >= 1, "anchor not found in %s" % path
    s = s.replace(anchor, BTN + "\n      " + anchor, 1)
    write(path, s)
    print("%s -> SYSTEM MONITOR button added" % os.path.basename(path))

print("done")
