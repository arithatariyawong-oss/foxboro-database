# -*- coding: utf-8 -*-
"""Make the two rails match: same page width, same folding filter rail.

Two changes, both bringing a page into line with its sibling rather than
inventing anything new:

  1. index.html used `max-width:1760px` with 26/22px body padding while
     system-monitor.html used `max-width:1900px` with 22/20px. On a 1920px
     screen that is 1760px of content against 1865px -- 105px of dead margin
     on the tag table, measured, not guessed. index.html takes the wider
     page's numbers.

  2. system-monitor.html gets the folding rail index.html already has: the
     icon tile at the top, the chevron on the rail's edge, the 76px folded
     chip, and the tile-as-the-way-back-out. The CSS block is lifted verbatim
     out of index.html -- including the base64 tile -- so the two pages cannot
     drift apart, and so the icon is byte-identical rather than re-encoded.

The monitor keeps its own localStorage key. The two rails hold different
things (a tag filter against a list of stations) and a reader who folds the
station list away is not thereby saying they want the tag filter gone too;
only the gesture is shared, which is the part that has to be.

Every replacement asserts on a miss, and the script is idempotent.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
IDX = os.path.join(WEB, "index.html")
MON = os.path.join(WEB, "system-monitor.html")


def read(p):
    return open(p, encoding="utf8").read()


def write(p, s):
    open(p, "w", encoding="utf8", newline="\n").write(s)


def sub1(s, old, new, what):
    assert s.count(old) == 1, "%s: expected 1 match, got %d" % (what, s.count(old))
    return s.replace(old, new, 1)


# ==========================================================================
# 1. index.html takes the wider page's frame
# ==========================================================================
idx = read(IDX)
if "max-width:1900px" in idx:
    print("index.html already uses the wide frame")
else:
    idx = sub1(idx,
               "  padding:26px 22px 34px;\n",
               "  padding:22px 20px 26px;\n",
               "index body padding")
    idx = sub1(idx,
               ".app{max-width:1760px; margin:0 auto; display:flex; "
               "flex-direction:column; gap:18px}",
               ".app{max-width:1900px; margin:0 auto; display:flex; "
               "flex-direction:column; gap:18px}",
               "index .app width")
    # the rail sticks 26px down because the body padding was 26px; follow it
    idx = sub1(idx,
               ".rail-shell{position:sticky; top:16px; align-self:start}",
               ".rail-shell{position:sticky; top:22px; align-self:start}",
               "index rail sticky offset")
    idx = sub1(idx,
               "  max-height:calc(100vh - 32px); overflow:auto;",
               "  max-height:calc(100vh - 44px); overflow:auto;",
               "index rail max-height")
    write(IDX, idx)
    print("index.html -> 1900px frame, 22/20/26 padding, rail offsets follow")

# ==========================================================================
# 2. system-monitor.html gets the folding rail
# ==========================================================================
mon = read(MON)
if 'id="railToggle"' in mon:
    print("system-monitor.html already has the folding rail")
else:
    # ---- CSS: lift the whole block, tile and all, out of index -----------
    idx = read(IDX)
    a = idx.find(".rail-shell{position:sticky")
    b = idx.find(".rail{\n", a)
    assert a > 0 and b > a, "cannot find the rail block in index.html"
    block = idx[a:b].rstrip()
    # drop index's own section banner that trails the block
    block = re.sub(r"/\* =+ RAIL =+ \*/\s*$", "", block).rstrip()
    assert "railFloat" in block and "rail-collapsed" in block, "block looks truncated"

    mon = sub1(mon,
               "/* ============================================================ MAIN ===== */",
               "/* ---- folding: the same gesture as the tag table's filter rail -------- */\n"
               + block + "\n\n"
               "/* ============================================================ MAIN ===== */",
               "monitor CSS anchor")

    # the shell carries the sticky now, so the rail itself only has to be a
    # containing block for the chevron
    mon = sub1(mon,
               "  padding:18px 16px; position:sticky; top:22px;\n"
               "  max-height:calc(100vh - 44px); overflow:auto;",
               "  padding:18px 16px; position:relative;\n"
               "  max-height:calc(100vh - 44px); overflow:auto;",
               "monitor .rail positioning")

    mon = sub1(mon,
               "@media (max-width:1080px){ .layout{grid-template-columns:1fr} }",
               "@media (max-width:1080px){\n"
               "  .layout, body.rail-collapsed .layout{grid-template-columns:1fr}\n"
               "  .rail-shell{position:static !important}\n"
               "}",
               "monitor narrow-screen layout")

    # ---- markup ----------------------------------------------------------
    mon = sub1(mon,
               '    <aside class="rail">\n',
               '    <div class="rail-shell">\n'
               '      <button class="rail-toggle" id="railToggle" type="button"\n'
               '              aria-expanded="true" aria-controls="rail"\n'
               '              aria-label="ย่อแถบ filter" title="ย่อแถบ filter">&#8249;</button>\n'
               '      <aside class="rail" id="rail">\n'
               '      <div class="rail-logo" id="railLogo" role="button" tabindex="0"\n'
               '           aria-label="หยุดการเคลื่อนไหวของไอคอน"\n'
               '           title="คลิกเพื่อหยุดการเคลื่อนไหว"></div>\n',
               "monitor rail open tag")
    mon = sub1(mon,
               "    </aside>\n",
               "      </aside>\n    </div>\n",
               "monitor rail close tag")

    # ---- behaviour -------------------------------------------------------
    JS = """
/* =======================================================================
   13. FOLDING RAIL
   The same gesture as the tag table's filter rail — same edge chevron, same
   tile-as-the-way-back-out. Its own storage key, though: folding the list of
   stations away says nothing about wanting the tag filter gone too.
   ======================================================================= */
const RAIL_KEY = "fox-mon-rail-collapsed";
const railToggle = $("#railToggle"), railLogo = $("#railLogo");

function setRailCollapsed(on, remember){
  document.body.classList.toggle("rail-collapsed", on);
  railToggle.innerHTML = on ? "&#8250;" : "&#8249;";          // the glyph IS the label
  const label = on ? "เปิดแถบ filter" : "ย่อแถบ filter";
  railToggle.setAttribute("aria-label", label);
  railToggle.setAttribute("aria-expanded", String(!on));
  railToggle.title = label;
  if (remember){ try { localStorage.setItem(RAIL_KEY, on ? "1" : "0"); } catch (e) {} }
}
railToggle.addEventListener("click", () =>
  setRailCollapsed(!document.body.classList.contains("rail-collapsed"), true));

/* Folded, the tile reopens the rail; open, it pauses its own float — the
   second job is what tells a reader the first one is clickable at all. */
railLogo.addEventListener("click", () => {
  if (document.body.classList.contains("rail-collapsed")){ setRailCollapsed(false, true); return; }
  const paused = railLogo.classList.toggle("paused");
  railLogo.title = paused ? "คลิกเพื่อให้ไอคอนขยับต่อ" : "คลิกเพื่อหยุดการเคลื่อนไหว";
  railLogo.setAttribute("aria-label", railLogo.title);
});
railLogo.addEventListener("keydown", e => {
  if (e.key === "Enter" || e.key === " "){ e.preventDefault(); railLogo.click(); }
});
try { if (localStorage.getItem(RAIL_KEY) === "1") setRailCollapsed(true, false); } catch (e) {}

"""
    mon = sub1(mon,
               "/* =======================================================================\n"
               "   12. BOOT\n",
               JS.lstrip("\n")
               + "/* =======================================================================\n"
                 "   12. BOOT\n",
               "monitor JS anchor")

    write(MON, mon)
    print("system-monitor.html -> folding rail added (%.1f KB of CSS lifted)"
          % (len(block) / 1024))

print("done")
