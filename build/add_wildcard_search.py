# -*- coding: utf-8 -*-
r"""Let every search box take `*` (and `?`) as a wildcard.

The plant's names are positional -- 05FRC065 is unit 05, loop FRC, number
065 -- so the question people actually have is "every FRC on unit 05" or
"everything numbered 065", and a substring search cannot ask either. `*`
can: `05F*065`, `05*RC*`, `39PK1*`.

Design, and why:

  * a query with NO wildcard behaves exactly as it did -- a case-insensitive
    substring. Nothing that works today changes.
  * the pattern is left UNANCHORED. Anchoring is the obvious choice and it
    is wrong here: every NAME carries its compound (`V501:05FRC065`), so
    `05FRC*` anchored would match nothing at all, which is precisely the
    query someone would try first.
  * `?` matches exactly one character, the standard companion to `*`. No
    Foxboro name contains a literal `?` or `*`, so nothing is shadowed.
  * the RegExp is compiled once per query, never per row. 77,010 rows on
    every keystroke is exactly how localeCompare froze this page before.

One helper, `foxMatch`, goes into all five pages -- they are standalone
files served off file:// with no shared script, so it is copied, not
imported. It returns null for an empty query so every caller keeps its
existing "no filter" branch.

Rewired here: NAME / DESCRP / TYPE / CP / column / parameter filters on the
tag table, tag search + parameter filter on the signal map, tree search +
Block Properties filter on System Manager, the system rail on the FBM page,
and both point and device filters on the Modbus page.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent

HELPER = r"""
/* ---- wildcard search --------------------------------------------------
   A query stays a plain case-insensitive substring, exactly as it always
   was, UNLESS it carries a wildcard: `*` is any run of characters and `?`
   is exactly one. The pattern is left UNANCHORED either way, so `05F*065`
   finds V501:05FRC065 without having to spell the compound out — anchoring
   would make the obvious `05FRC*` match nothing, because every name here
   begins with its compound.
   Returns null for an empty query (meaning "no filter"), else a predicate.
   The RegExp is compiled once per query and never per row: 77,010 rows
   would otherwise pay for the compile on every keystroke, which is the
   trap Intl.Collator set on this page before. */
function foxMatch(q){
  const s = (q == null ? '' : String(q)).trim();
  if (!s) return null;
  const str = v => String(v == null ? '' : v);
  if (s.indexOf('*') === -1 && s.indexOf('?') === -1){
    const needle = s.toUpperCase();
    return v => str(v).toUpperCase().indexOf(needle) !== -1;
  }
  const re = new RegExp(s.replace(/[.+^${}()|[\]\\]/g, '\\$&')
                         .replace(/\*/g, '.*').replace(/\?/g, '.'), 'i');
  return v => re.test(str(v));
}
"""

ANCHOR = "const $ = s => document.querySelector(s);\n"


class Page:
    def __init__(self, name):
        self.path = WEB / name
        self.name = name
        self.s = io.open(self.path, encoding="utf8").read()
        self.n0 = len(self.s)

    def sub(self, old, new, what, count=1):
        if self.s.count(old) != count:
            sys.exit("ABORT: %s / %s -- anchor found %d times, expected %d"
                     % (self.name, what, self.s.count(old), count))
        self.s = self.s.replace(old, new, count)
        print("    ok  %s" % what)

    def install_helper(self):
        self.sub(ANCHOR, ANCHOR + HELPER, "foxMatch helper")

    def save(self):
        io.open(self.path, "w", encoding="utf8", newline="").write(self.s)
        print("  %-22s %d -> %d chars (%+d)"
              % (self.name, self.n0, len(self.s), len(self.s) - self.n0))


# ======================================================================
print("index.html")
p = Page("index.html")
p.install_helper()

p.sub(
    """function textMask(ci, q){
  if (!q) return null;
  const d = dictOf(ci), m = new Uint8Array(d.length + 1), needle = q.toLowerCase();
  for (let k = 0; k < d.length; k++) if (d[k].toLowerCase().indexOf(needle) !== -1) m[k + 1] = 1;
  return m;                                     // blank never matches a query
}""",
    """function textMask(ci, q){
  /* over the column's DICTIONARY, not its 77,010 rows -- 33,387 distinct
     DESCRP values is what a wildcard actually has to be tested against */
  const hit = foxMatch(q);
  if (!hit) return null;
  const d = dictOf(ci), m = new Uint8Array(d.length + 1);
  for (let k = 0; k < d.length; k++) if (hit(d[k])) m[k + 1] = 1;
  return m;                                     // blank never matches a query
}""",
    "NAME / DESCRP filter",
)

p.sub(
    """  const q = src.filterInput ? src.filterInput.value.trim().toLowerCase() : '';
  const items = q ? src.items.filter(it => it.label.toLowerCase().indexOf(q) !== -1) : src.items;""",
    """  const hit = foxMatch(src.filterInput ? src.filterInput.value : '');
  const items = hit ? src.items.filter(it => hit(it.label)) : src.items;""",
    "TYPE / CP chip filter",
)

p.sub(
    """  const q = $('#qCol').value.trim().toLowerCase();
  const list = (q ? colCandidates.filter(c => c.h.toLowerCase().indexOf(q) !== -1) : colCandidates).slice(0, 400);""",
    """  const hit = foxMatch($('#qCol').value);
  const list = (hit ? colCandidates.filter(c => hit(c.h)) : colCandidates).slice(0, 400);""",
    "column picker filter",
)

p.sub(
    "  const q = propsEl.querySelector('#pq').value.trim().toUpperCase();\n",
    "  const hit = foxMatch(propsEl.querySelector('#pq').value);\n",
    "Properties filter (query)",
)
p.sub(
    "    if (q && k.toUpperCase().indexOf(q) === -1 && v.toUpperCase().indexOf(q) === -1) continue;\n",
    "    if (hit && !hit(k) && !hit(v)) continue;\n",
    "Properties filter (test)",
)

p.sub(
    'id="qName" placeholder="ค้นหา NAME…"',
    'id="qName" placeholder="ค้นหา NAME… ใช้ * ได้"',
    "qName placeholder",
)
p.sub(
    'id="qDesc" placeholder="ค้นหา DESCRP…"',
    'id="qDesc" placeholder="ค้นหา DESCRP… ใช้ * ได้"',
    "qDesc placeholder",
)
p.save()

# ======================================================================
print("signal-map.html")
p = Page("signal-map.html")
p.install_helper()

p.sub(
    """  const q = $('#q').value.trim().toUpperCase();
  if (q.length < 2){ $('#results').innerHTML = ''; hits = []; return; }
  hits = [];
  for (let i = 0; i < NODES.length && hits.length < 60; i++){
    const n = NODES[i][0];
    if (n.toUpperCase().indexOf(q) !== -1) hits.push(i);
  }
  if (!hits.length){
    for (let i = 0; i < NODES.length && hits.length < 60; i++)
      if ((NODES[i][2] || '').toUpperCase().indexOf(q) !== -1) hits.push(i);
  }""",
    """  const raw = $('#q').value.trim(), hit = foxMatch(raw);
  if (raw.length < 2 || !hit){ $('#results').innerHTML = ''; hits = []; return; }
  hits = [];
  for (let i = 0; i < NODES.length && hits.length < 60; i++)
    if (hit(NODES[i][0])) hits.push(i);
  if (!hits.length){                            // fall back to the description
    for (let i = 0; i < NODES.length && hits.length < 60; i++)
      if (hit(NODES[i][2] || '')) hits.push(i);
  }""",
    "tag search",
)

p.sub(
    "  const q = propsEl.querySelector('#pq').value.trim().toUpperCase();\n",
    "  const hit = foxMatch(propsEl.querySelector('#pq').value);\n",
    "Properties filter (query)",
)
p.sub(
    "    if (q && k.toUpperCase().indexOf(q) === -1 && v.toUpperCase().indexOf(q) === -1) continue;\n",
    "    if (hit && !hit(k) && !hit(v)) continue;\n",
    "Properties filter (test)",
)

p.sub(
    'placeholder="ค้นหา tag เช่น 05FRC065, 01PIC130…"',
    'placeholder="ค้นหา tag เช่น 05FRC065, 05F*065…"',
    "search placeholder",
)
p.save()

# ======================================================================
print("system-manager.html")
p = Page("system-manager.html")
p.install_helper()

p.sub(
    """  const q = (filter || '').trim().toUpperCase();
  const keep = rows.filter(([k, v]) =>
    k !== 'Source.Name' &&
    (!q || k.toUpperCase().indexOf(q) >= 0 || v.toUpperCase().indexOf(q) >= 0));""",
    """  const hit = foxMatch(filter);
  const keep = rows.filter(([k, v]) =>
    k !== 'Source.Name' && (!hit || hit(k) || hit(v)));""",
    "Block Properties filter",
)

p.sub(
    """  const up = raw.toUpperCase(), out = [];
  for (const s of CPS){
    if (s.n.toUpperCase().indexOf(up) >= 0)""",
    """  const hit = foxMatch(raw), out = [];
  if (!hit){ box.innerHTML = ''; box.classList.add('hide'); return; }
  for (const s of CPS){
    if (hit(s.n))""",
    "tree search (stations)",
)
p.sub(
    "    if (d[c].toUpperCase().indexOf(up) >= 0)\n",
    "    if (hit(d[c]))\n",
    "tree search (blocks)",
)

p.sub(
    'id="q" placeholder="ค้นหา tag / compound / station…"',
    'id="q" placeholder="ค้นหา tag / compound / station… ใช้ * ได้"',
    "search placeholder",
)
p.save()

# ======================================================================
print("system-monitor.html")
p = Page("system-monitor.html")
p.install_helper()

p.sub(
    """  const q = qSys.trim().toLowerCase();
  let list = SYS.map((s,i) => ({s,i})).filter(({s}) => {
    if (areaSel && s.area !== areaSel) return false;
    if (!q) return true;
    return s.n.toLowerCase().includes(q) || (s.sta||"").toLowerCase().includes(q)
        || s._lb.toLowerCase().includes(q);
  });""",
    """  const hit = foxMatch(qSys);
  let list = SYS.map((s,i) => ({s,i})).filter(({s}) => {
    if (areaSel && s.area !== areaSel) return false;
    if (!hit) return true;
    return hit(s.n) || hit(s.sta || "") || hit(s._lb);
  });""",
    "system rail filter",
)

p.sub(
    'id="qSys" placeholder="ค้นหา system / letterbug…"',
    'id="qSys" placeholder="ค้นหา system / letterbug… ใช้ * ได้"',
    "search placeholder",
)
p.save()

# ======================================================================
print("modbus.html")
p = Page("modbus.html")
p.install_helper()

# both filteredPts() and filteredDevs() carry the identical two lines
p.sub(
    '  const needle = q.trim().toLowerCase();\n',
    '  const hit = foxMatch(q);\n',
    "point + device filter (query)",
    count=2,
)
p.sub(
    "    if (needle){\n",
    "    if (hit){\n",
    "point + device filter (branch)",
    count=2,
)
p.sub(
    "      if (!hay.includes(needle)) return false;\n",
    "      if (!hit(hay)) return false;\n",
    "point + device filter (test)",
    count=2,
)

p.sub(
    'id="q" placeholder="tag / register / คำอธิบาย / letterbug…"',
    'id="q" placeholder="tag / register / คำอธิบาย / letterbug… ใช้ * ได้"',
    "search placeholder",
)
p.save()

print("done")
