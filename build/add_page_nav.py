# -*- coding: utf-8 -*-
"""Give all three pages one shared nav bar, and rename SYSTEM MONITOR.

Until now each page carried its own ad-hoc set of cross links in the topbar
actions -- index had one button, signal-map and system-monitor each had a back
link plus one sideways link -- so which pages existed depended on where you
were standing. This puts the same three-item bar under the title card on every
page, with the current page marked `aria-current="page"`, and strips the links
back out of the action groups so a page name appears exactly once.

The third page is relabelled **FBM MODULE MANAGEMENT**. Only the visible name
changes: the file stays `system-monitor.html` so existing links, bookmarks and
the notes that reference it keep working.

Every replacement asserts on a miss, and the script is idempotent -- it skips a
page that already carries the bar -- so it can be re-run after an edit.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)

IDX = os.path.join(WEB, "index.html")
MAP = os.path.join(WEB, "signal-map.html")
MON = os.path.join(WEB, "system-monitor.html")

PAGES = [
    ("index.html",          "FOXBORO DATABASE",       "ตาราง tag ทั้งหมด"),
    ("signal-map.html",     "SIGNAL MAP",             "ผังการเดินสัญญาณ"),
    ("system-monitor.html", "FBM MODULE MANAGEMENT",  "โมดูล &amp; spare point"),
]

CSS = """
/* ============================================================ PAGE NAV = */
/* one bar, same three items on every page; the current page is the mint pill */
.pagenav{
  --nav-on:#12402d;
  display:flex; gap:6px; flex-wrap:wrap; align-self:flex-start; flex:none;
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--r-pill); box-shadow:var(--lift-sm), var(--inset-hi);
  padding:5px;
}
:root[data-theme="dark"] .pagenav{--nav-on:#d8f3e5}
.pagenav a{
  display:flex; flex-direction:column; gap:1px; text-decoration:none;
  border:1px solid transparent; border-radius:var(--r-pill);
  padding:8px 22px 9px; color:var(--text-dim);
  transition:background .14s ease, color .14s ease;
}
.pagenav a b{font-size:13px; font-weight:800; letter-spacing:.05em; line-height:1.25}
.pagenav a i{font-style:normal; font-size:11px; line-height:1.3; color:var(--text-faint)}
.pagenav a:hover{background:var(--surface-2); color:var(--text)}
.pagenav a:focus-visible{outline:3px solid var(--mint-ring); outline-offset:2px}
.pagenav a[aria-current="page"]{
  background:var(--mint); border-color:var(--mint-ring); color:var(--nav-on);
  box-shadow:var(--lift-sm), var(--inset-hi); cursor:default;
}
.pagenav a[aria-current="page"] i{color:var(--nav-on); opacity:.72}
@media (max-width:700px){
  .pagenav{align-self:stretch}
  .pagenav a{flex:1 1 auto; align-items:center; padding-left:14px; padding-right:14px}
}

"""


def nav(current):
    out = ['  <nav class="pagenav" aria-label="หน้าในชุดเครื่องมือ">']
    for href, name, sub in PAGES:
        on = ' aria-current="page"' if href == current else ""
        out.append('    <a href="%s"%s><b>%s</b><i>%s</i></a>' % (href, on, name, sub))
    out.append("  </nav>")
    return "\n".join(out)


def read(p):
    return open(p, encoding="utf8").read()


def write(p, s):
    open(p, "w", encoding="utf8", newline="\n").write(s)


def strip(s, frag, path):
    """drop a cross-page link that the nav bar now owns"""
    assert s.count(frag) == 1, "link fragment not found once in %s" % path
    return s.replace(frag, "", 1)


# ---- the links each page has to give up -----------------------------------
DROP = {
    IDX: ['      <a class="btn" href="system-monitor.html" '
          'title="อุปกรณ์และ spare point ของแต่ละ system">SYSTEM MONITOR</a>\n'],
    MAP: ['      <a class="btn app-back" href="index.html" '
          'title="กลับไปหน้าตาราง FOXBORO DATABASE">\n'
          '        <span aria-hidden="true">↩</span> FOXBORO DATABASE</a>\n',
          '      <a class="btn" href="system-monitor.html" '
          'title="อุปกรณ์และ spare point ของแต่ละ system">SYSTEM MONITOR</a>\n'],
    MON: ['      <a class="btn app-back" href="index.html" '
          'title="กลับไปหน้าตาราง FOXBORO DATABASE">\n'
          '        <span aria-hidden="true">↩</span> FOXBORO DATABASE</a>\n',
          '      <a class="btn" href="signal-map.html" title="ผังสัญญาณ">SIGNAL MAP</a>\n'],
}

for path, current in ((IDX, "index.html"), (MAP, "signal-map.html"),
                      (MON, "system-monitor.html")):
    s = read(path)
    name = os.path.basename(path)
    if 'class="pagenav"' in s:
        print("%s already has the nav bar" % name)
        continue

    for frag in DROP[path]:
        s = strip(s, frag, name)

    # the stylesheet: in front of the topbar block, which every page has once
    assert s.count("\n.topbar{") == 1, "no unique .topbar rule in %s" % name
    s = s.replace("\n.topbar{", CSS + ".topbar{", 1)

    # the markup: directly under the title card
    assert s.count("</header>\n") == 1, "no unique </header> in %s" % name
    s = s.replace("</header>\n", "</header>\n\n" + nav(current) + "\n", 1)

    write(path, s)
    print("%s -> nav bar added, %d old link(s) removed" % (name, len(DROP[path])))

# ---- the rename, visible only --------------------------------------------
s = read(MON)
for old, new in (("<title>FOXBORO SYSTEM MONITOR</title>",
                  "<title>FOXBORO FBM MODULE MANAGEMENT</title>"),
                 ("<h1>SYSTEM MONITOR</h1>",
                  "<h1>FBM MODULE MANAGEMENT</h1>")):
    if new in s:
        continue
    assert s.count(old) == 1, "cannot rename: %r not found once" % old
    s = s.replace(old, new, 1)
    print("renamed: %s" % new)
write(MON, s)

print("done")
