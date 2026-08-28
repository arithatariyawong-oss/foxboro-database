# -*- coding: utf-8 -*-
"""Give the filter rail the icon tile and the fold-away control from the user's
own PT2 Online Monitor, so both apps fold a panel by the same gesture:

  * a 108px icon tile at the head of the rail, floating on a 3.8s bob,
    click to pause -- and, once folded, click to come back out;
  * a 28px round chevron pinned to the panel's edge (top 30px, right -14px)
    that straddles the border, flipping between the two angle glyphs;
  * folded, the rail becomes a 76px chip carrying only the tile.

05.jpg is a square icon on a WHITE field, so the tile paints it with
background-size:cover -- inset, that field would read as a white square
pasted onto the cream rather than as the tile's own face.

The rail scrolls, and an overflow container clips anything hanging outside
it (there is no per-axis escape -- overflow-x:visible computes to auto once
the other axis scrolls), so a .rail-shell wrapper becomes the sticky,
unclipped element and the button is its child, not the rail's.

The column-width change is deliberately instant, matching the reference: a
width transition relayouts the table on every frame for no real gain.
"""
import base64, io, sys
from pathlib import Path
from PIL import Image

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "index.html"
SRC = WEB / "05.jpg"

# ---- 1. the icon, downscaled: the tile is 108px, the source is 1024px ----
im = Image.open(SRC).convert("RGB").resize((256, 256), Image.LANCZOS)
buf = io.BytesIO()
im.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
b64 = base64.b64encode(buf.getvalue()).decode("ascii")
print("05.jpg %.0f KB -> 256px %.1f KB -> %.1f KB encoded"
      % (SRC.stat().st_size / 1024, len(buf.getvalue()) / 1024, len(b64) / 1024))

s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)

CSS = """
/* ---- rail shell -------------------------------------------------------
   The rail scrolls, so it clips; the shell is the sticky, unclipped
   element the edge handle can hang off. */
.rail-shell{position:sticky; top:16px; align-self:start}
.rail-toggle{
  position:absolute; top:30px; right:-14px; z-index:30;
  width:28px; height:28px; padding:0; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  background:color-mix(in srgb, var(--accent) 12%, var(--surface));
  color:var(--accent); border:1px solid var(--accent);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.45), 0 3px 8px -2px rgba(44,51,47,.4);
  font-size:16px; line-height:1; font-weight:700; cursor:pointer;
  transition:background .15s ease, color .15s ease, transform .15s ease;
}
.rail-toggle:hover{background:var(--accent); color:var(--surface); transform:translateY(-1px)}
.rail-toggle:active{transform:translateY(1px)}
.rail-toggle:focus-visible{outline:2px solid var(--accent); outline-offset:2px}

/* ---- the icon tile: the filter's mark, and the way back out of the rail */
.rail-logo{
  display:block; width:108px; height:108px; margin:2px auto 4px; flex:none;
  border-radius:24px; border:1px solid var(--border);
  background:var(--surface) url(data:image/jpeg;base64,__ICON__) center/cover no-repeat;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.55),
             inset 0 -2px 5px -2px rgba(44,51,47,.25), var(--lift-sm);
  cursor:pointer; user-select:none;
  animation:railFloat 3.8s ease-in-out infinite;
  transition:border-radius .28s ease, box-shadow .2s ease,
             width .28s ease, height .28s ease;
}
.rail-logo:hover{box-shadow:inset 0 1px 0 rgba(255,255,255,.55),
             inset 0 -2px 5px -2px rgba(44,51,47,.25), var(--lift)}
.rail-logo:focus-visible{outline:2px solid var(--accent); outline-offset:3px}
.rail-logo.paused{animation-play-state:paused}
@keyframes railFloat{0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)}}
@media (prefers-reduced-motion:reduce){.rail-logo{animation:none}}

/* ---- folded: a chip carrying just the tile ---------------------------- */
body.rail-collapsed .layout{grid-template-columns:76px minmax(0,1fr)}
body.rail-collapsed .rail{padding:12px 8px; overflow:hidden; height:auto; max-height:none}
body.rail-collapsed .rail > *:not(.rail-logo){display:none}
body.rail-collapsed .rail-logo{width:42px; height:42px; border-radius:12px; margin:0 auto}

/* ============================================================== RAIL ==== */"""

SUBS = [
    # ---- CSS -----------------------------------------------------------
    ("\n/* ============================================================== RAIL ==== */",
     CSS.replace("__ICON__", b64)),

    # the rail itself is no longer the sticky element
    (""".rail{
  position:sticky; top:16px;""",
     """.rail{
  position:relative;"""),

    # the single-column breakpoint has to beat the collapsed grid rule,
    # which outranks a bare `.layout` on specificity
    ("""@media (max-width:1080px){ .layout{grid-template-columns:1fr} .rail{position:static !important} }""",
     """@media (max-width:1080px){
  .layout, body.rail-collapsed .layout{grid-template-columns:1fr}
  .rail-shell{position:static !important}
}"""),

    # ---- markup --------------------------------------------------------
    ("""    <aside class="rail">
      <div class="rail-head">""",
     """    <div class="rail-shell">
      <button class="rail-toggle" id="railToggle" type="button"
              aria-expanded="true" aria-controls="rail"
              aria-label="ย่อแถบ filter" title="ย่อแถบ filter">&#8249;</button>
      <aside class="rail" id="rail">
      <div class="rail-logo" id="railLogo" role="button" tabindex="0"
           aria-label="หยุดการเคลื่อนไหวของไอคอน" title="คลิกเพื่อหยุดการเคลื่อนไหว"></div>
      <div class="rail-head">"""),

    ("""        <div class="collist" id="colList"></div>
      </section>
    </aside>""",
     """        <div class="collist" id="colList"></div>
      </section>
      </aside>
    </div>"""),

    # ---- behaviour -----------------------------------------------------
    ("""$('#themeBtn').addEventListener('click', () => {""",
     """/* The fold gesture is deliberately the one the user's PT2 Online Monitor
   uses: same edge chevron, same tile-as-the-way-back-out. Two apps the same
   person uses should not fold a panel two different ways. */
const RAIL_KEY = 'fox-rail-collapsed';
const railToggle = $('#railToggle'), railLogo = $('#railLogo');

function setRailCollapsed(on, remember){
  document.body.classList.toggle('rail-collapsed', on);
  railToggle.innerHTML = on ? '&#8250;' : '&#8249;';          // the glyph IS the label
  const label = on ? 'เปิดแถบ filter' : 'ย่อแถบ filter';
  railToggle.setAttribute('aria-label', label);
  railToggle.setAttribute('aria-expanded', String(!on));
  railToggle.title = label;
  if (remember){ try { localStorage.setItem(RAIL_KEY, on ? '1' : '0'); } catch (e) {} }
  if (N) paintRows();                       // the table just changed width
}
railToggle.addEventListener('click', () =>
  setRailCollapsed(!document.body.classList.contains('rail-collapsed'), true));

/* Folded, the tile reopens the rail; open, it pauses its own float — the
   second job is what tells a reader the first one is clickable at all. */
railLogo.addEventListener('click', () => {
  if (document.body.classList.contains('rail-collapsed')){ setRailCollapsed(false, true); return; }
  const paused = railLogo.classList.toggle('paused');
  railLogo.title = paused ? 'คลิกเพื่อให้ไอคอนขยับต่อ' : 'คลิกเพื่อหยุดการเคลื่อนไหว';
  railLogo.setAttribute('aria-label', railLogo.title);
});
railLogo.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); railLogo.click(); }
});
try { if (localStorage.getItem(RAIL_KEY) === '1') setRailCollapsed(true, false); } catch (e) {}

$('#themeBtn').addEventListener('click', () => {"""),
]

missing = []
for old, new in SUBS:
    if old not in s:
        missing.append(old.strip().splitlines()[0][:76])
    else:
        s = s.replace(old, new, 1)
if missing:
    print("NOT FOUND (%d):" % len(missing))
    for m in missing:
        print("   -", m)
    sys.exit(1)

io.open(PAGE, "w", encoding="utf8").write(s)
print("rail fold added: %.1f KB -> %.1f KB" % (n_before / 1024, len(s) / 1024))
