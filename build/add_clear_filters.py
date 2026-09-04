# -*- coding: utf-8 -*-
"""One "Clear all filters" button, in the same place, on every page that filters.

TAG SEARCH already had one (amber, top right, next to Export CSV). The other
filtering pages had nothing: you got out of a filter by remembering which of
five selects, three chip rails and two search boxes you had touched. Now all
of them carry the same amber button in the same corner, and it puts the page
back exactly where it opens.

What each page counts as a filter -- the rule is "anything that hides rows",
not "anything you can click":

  index.html          NAME / DESCRP search, the AREA·TYPE·CP chip sets, AND
                      the three little search boxes that filter the chip
                      LISTS themselves (qType/qCp/qCol). clearAll() already
                      existed but left those three full, so after clicking it
                      the TYPE rail could still be showing 4 of 69 types with
                      no filter active to explain why.
  system-monitor.html the system scope, AREA, the system search, the sort
                      order, and the spare-point class chips.
  modbus.html         all five selects (CP · gateway · device · direction ·
                      register bank) and the search.
  system-manager.html the equipment scope, the Blocks Types filter, the
                      Block Properties filter and the search box. Scope IS
                      the dominant filter here, so clearing goes back to
                      nothing-picked -- which since build/quiet_default_views.py
                      is also how the page opens, and was otherwise a state
                      with no way back to it.
  sequence-view.html  the parameter filter and the find-in-source box.

The tab/view a page is on is NOT a filter and is left alone: Modbus stays on
Register points or สรุปอุปกรณ์, the FBM page stays on the tab you were reading.
Clearing filters should not also throw away where you were looking.

signal-map.html and logic-view.html are deliberately skipped -- their only
control is a search box you navigate WITH (typing a tag jumps to it, it hides
nothing), plus view state like chain length and the all-pins toggle. A button
labelled "clear all filters" would have nothing to clear.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent

BTN = '<button class="btn amber" id="clearBtn">Clear all filters</button>'
CSS = (".btn.amber{background:var(--amber); color:var(--amber-ink); border-color:transparent}\n"
       ".btn.amber:hover{filter:brightness(1.06)}\n")


def edit(path, jobs):
    s = io.open(path, encoding="utf8").read()
    n0 = len(s)
    for old, new, what in jobs:
        if s.count(old) != 1:
            sys.exit("ABORT: %s in %s -- anchor found %d times, expected 1"
                     % (what, path.name, s.count(old)))
        s = s.replace(old, new, 1)
        print("  ok  %-22s %s" % (path.name, what))
    io.open(path, "w", encoding="utf8", newline="").write(s)
    print("      %s %d -> %d chars (%+d)" % (path.name, n0, len(s), len(s) - n0))


def tools_bar(page, extra_css_anchor):
    """the shared header button, plus the .btn.amber rule the page lacks"""
    return [
        (extra_css_anchor, CSS + extra_css_anchor, "CSS: .btn.amber"),
        ('    <div class="tools">\n'
         '      <button class="btn" id="csvBtn">Export CSV</button>\n',
         '    <div class="tools">\n'
         '      ' + BTN + '\n'
         '      <button class="btn" id="csvBtn">Export CSV</button>\n',
         "header button"),
    ]


# ---- 1. TAG SEARCH: the existing clearAll missed the chip-list searches ---
edit(WEB / "index.html", [
    (
        "function clearAll(){\n"
        "  Object.values(state.sets).forEach(s => s.clear());\n"
        "  state.q.name = state.q.desc = '';\n"
        "  state.sort.ci = null;\n"
        "  $('#qName').value = $('#qDesc').value = '';\n"
        "  ['area','type','cp'].forEach(paintChips);\n"
        "  refresh();\n"
        "}\n",
        "function clearAll(){\n"
        "  Object.values(state.sets).forEach(s => s.clear());\n"
        "  state.q.name = state.q.desc = '';\n"
        "  state.sort.ci = null;\n"
        "  $('#qName').value = $('#qDesc').value = '';\n"
        "  /* The chip rails have search boxes of their own, and leaving them\n"
        "     full after a clear shows TYPE cut down to 4 of 69 with nothing\n"
        "     on screen to say why. They are filters too. */\n"
        "  $('#qType').value = $('#qCp').value = $('#qCol').value = '';\n"
        "  ['area','type','cp'].forEach(paintChips);\n"
        "  paintColList();\n"
        "  refresh();\n"
        "}\n",
        "clearAll() also empties the chip-list searches",
    ),
])

# ---- 2. FBM (I/O) MODULE MANAGEMENT -------------------------------------
edit(WEB / "system-monitor.html", tools_bar(
    "system-monitor.html", ".btn:hover{background:var(--btn-hover)}\n") + [
    (
        'let qSys = "";\n',
        'let qSys = "";\n'
        "\n"
        "/* Everything that hides a row, back to how the page opens. The TAB is\n"
        "   not one of them -- clearing a filter should not also throw away\n"
        "   whether you were reading Modules or Spare points. */\n"
        "function clearAll(){\n"
        '  cur = -1; sortBy = "name"; areaSel = ""; qSys = ""; spareCls = "";\n'
        '  const q = document.querySelector("#qSys"); if (q) q.value = "";\n'
        "  drawRail(); drawView(); drawKpis();\n"
        "}\n",
        "clearAll()",
    ),
])

# ---- 3. MODBUS COMMUNICATION -------------------------------------------
edit(WEB / "modbus.html", tools_bar(
    "modbus.html", ".btn:hover{background:var(--btn-hover)}\n") + [
    (
        'let fCP = "", fGW = "", fDev = "", fDir = "", fBank = "", q = "";\n',
        'let fCP = "", fGW = "", fDev = "", fDir = "", fBank = "", q = "";\n'
        "\n"
        "/* All five selects and the search. The tab is left where it was. */\n"
        "function clearAll(){\n"
        '  fCP = fGW = fDev = fDir = fBank = q = "";\n'
        "  shown = 800;\n"
        '  const s = document.querySelector("#q"); if (s) s.value = "";\n'
        "  rebuildSelects();\n"
        '  for (const id of ["#fDir", "#fBank"]){\n'
        '    const el = document.querySelector(id); if (el) el.value = "";\n'
        "  }\n"
        "  draw();\n"
        "}\n",
        "clearAll()",
    ),
])

# ---- 4. SYSTEM MANAGER --------------------------------------------------
edit(WEB / "system-manager.html", tools_bar(
    "system-manager.html", ".btn:hover{background:var(--btn-hover)}\n") + [
    (
        "const PICK_ME = ",
        "/* Scope is the dominant filter on this page, so clearing goes all the\n"
        "   way back to nothing-picked -- which is also how the page opens, and\n"
        "   was otherwise a state with no way to return to it. */\n"
        "function clearAll(){\n"
        "  picked = false;\n"
        "  selCp = -1; selComp = -1; selType = ''; selBlk = -1;\n"
        "  selMod = -1; MODROWS = null;\n"
        "  blkCap = cmpCap = 300; pFilter = '';\n"
        "  expanded = new Set(['net']);\n"
        "  for (const id of ['#q', '#pq']){\n"
        "    const el = $(id); if (el) el.value = '';\n"
        "  }\n"
        "  const ns = $('#netSel'); if (ns) ns.value = '-1';\n"
        "  render();\n"
        "}\n"
        "\n"
        "const PICK_ME = ",
        "clearAll()",
    ),
])

# ---- 5. SEQUENCE VIEW ---------------------------------------------------
edit(WEB / "sequence-view.html", [
    (
        ".btn:hover{background:var(--btn-hover)}\n",
        CSS + ".btn:hover{background:var(--btn-hover)}\n",
        "CSS: .btn.amber",
    ),
    (
        '    <button class="btn icon" id="themeBtn" title="สลับธีม">◐</button>\n',
        '    ' + BTN + '\n'
        '    <button class="btn icon" id="themeBtn" title="สลับธีม">◐</button>\n',
        "header button",
    ),
    (
        "$('#fProps').addEventListener('input', () => { if (CUR) paintProps(CUR, $('#fProps').value); });\n",
        "$('#fProps').addEventListener('input', () => { if (CUR) paintProps(CUR, $('#fProps').value); });\n"
        "\n"
        "/* the parameter filter and the find-in-source box; the block you are\n"
        "   looking at is not a filter and stays put */\n"
        "function clearAll(){\n"
        "  $('#fProps').value = '';\n"
        "  $('#fSrc').value = '';\n"
        "  srcHits = []; srcAt = -1; srcQ = '';\n"
        "  $('#srcBody').querySelectorAll('.lrow.marked').forEach(el => el.classList.remove('marked'));\n"
        "  if (CUR) paintProps(CUR, '');\n"
        "}\n"
        "$('#clearBtn').addEventListener('click', clearAll);\n",
        "clearAll()",
    ),
])

# ---- the three .tools pages need the click wired up ---------------------
for page, anchor in (
    ("system-monitor.html", '$("#csvBtn").addEventListener("click"'),
    ("modbus.html", '$("#csvBtn").addEventListener("click"'),
    ("system-manager.html", "$('#csvBtn').addEventListener('click'"),
):
    p = WEB / page
    s = io.open(p, encoding="utf8").read()
    if s.count(anchor) != 1:
        sys.exit("ABORT: %s -- csvBtn handler found %d times" % (page, s.count(anchor)))
    q = "\"" if anchor.startswith('$("') else "'"
    wire = "$(%s#clearBtn%s).addEventListener(%sclick%s, clearAll);\n" % (q, q, q, q)
    s = s.replace(anchor, wire + anchor, 1)
    io.open(p, "w", encoding="utf8", newline="").write(s)
    print("  ok  %-22s clearBtn wired" % page)
