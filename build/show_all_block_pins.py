# -*- coding: utf-8 -*-
"""Draw every pin a block HAS on the signal map, not only the wired ones.

The map used to draw a box with just the pins that carried a wire. That
answers "where does this signal go", but not "what else could this block
do" -- and on a plant floor the free pin matters as much as the used one.
An ICC block detail lists the whole set, so the box now does too:

  * the pins are the union of the wires actually found in the export and
    every connectable INPUT / OUTPUT B0193AX gives the block's TYPE
    (block_params.json -> graph.js `pins`, already shipped: it was being
    used only to ORDER the wired pins);
  * a wired pin keeps its arrow head and full-strength label; a free pin
    gets a short stub off the edge and a dimmed label, so the two are
    still told apart at a glance;
  * types B0193AX does not cover -- the FOUNDATION Fieldbus blocks (AI, AO,
    MAO, PIDFF, UNIVFF) and the ECB variants, documented in B0400FD /
    B0400FA instead -- have no reference list, so there the wired pins are
    still all there is to draw. Same for an ECB's synthetic `CH 3` / `DEV`
    pins, which are hardware channels, not type parameters.

The tall types are real: PIDE carries 47 connectable inputs, PLB 89
outputs, so those boxes go from ~150px to ~850px. The median type has 13.
That is a deliberate trade and the ☰ button in the toolbar toggles back to
wired-only, remembered per browser under `fox-map-allpins`.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "signal-map.html"

s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


# ---- 1. CSS: the dimmed label and the stub for a free pin ---------------
sub(
    ".pin{font-size:10.5px; fill:var(--pin-ink)}\n",
    ".pin{font-size:10.5px; fill:var(--pin-ink)}\n"
    "/* a pin the export found no wire on: still a pin the block has */\n"
    ".pin.off{opacity:.4}\n"
    ".stub{stroke:var(--pin-ink); stroke-width:1; opacity:.32; fill:none}\n",
    "CSS .pin.off / .stub",
)

sub(
    ".btn.icon{padding:10px 14px}\n",
    ".btn.icon{padding:10px 14px}\n"
    ".btn.on{background:var(--mint); border-color:var(--mint-deep)}\n",
    "CSS .btn.on",
)

# ---- 2. the toolbar toggle ----------------------------------------------
sub(
    '      <button class="btn icon" id="fit" title="พอดีจอ">⤢</button>\n',
    '      <button class="btn icon" id="pinsBtn">☰</button>\n'
    '      <button class="btn icon" id="fit" title="พอดีจอ">⤢</button>\n',
    "toolbar button #pinsBtn",
)

# ---- 3. the legend gets a word about the dim pins ------------------------
sub(
    '<i style="background:var(--mint-deep);border-color:var(--mint-deep);'
    'width:4px;border-radius:2px"></i>ต้นทาง / ปลายทางของโซ่</span>\n',
    '<i style="background:var(--mint-deep);border-color:var(--mint-deep);'
    'width:4px;border-radius:2px"></i>ต้นทาง / ปลายทางของโซ่</span>\n'
    '      <span style="opacity:.62">ชื่อขาสีจาง = ขาที่บล็อกมีแต่ยังไม่ได้ต่อสาย</span>\n',
    "legend note",
)

# ---- 4. blockPins: union the wired set with the type's own pin table -----
sub(
    """function blockPins(n, edges){
  /* Only WIRED pins are drawn — an ICC detail shows the connections this
     block actually has, not the hundred parameters its type could carry.
     B0193AX decides which side each one belongs on. */
  const ins = new Set(), outs = new Set();
  for (const e of edges){
    if (e[2] === n) ins.add(e[3]);
    if (e[0] === n) outs.add(e[1]);
  }
  const ref = PINS[TYPE(n)];
""",
    """let ALL_PINS = true;

function blockPins(n, edges){
  /* Every pin the block HAS, the way an ICC block detail lists them: the
     wires the export actually found, plus every other connectable pin
     B0193AX gives this TYPE. A free pin is a fact about the block just as
     much as a used one, so it is drawn — dimmed, with a stub instead of an
     arrow head, which is what `wired` below is for.

     B0193AX still decides which side each pin belongs on. The types it does
     not cover (the FF blocks, the ECB variants) have no reference list, and
     an ECB's `CH 3` / `DEV` pins are hardware channels rather than type
     parameters — for both, the wired pins remain all there is to draw. */
  const ins = new Set(), outs = new Set();
  for (const e of edges){
    if (e[2] === n) ins.add(e[3]);
    if (e[0] === n) outs.add(e[1]);
  }
  const wired = new Set([...ins].map(p => 'i' + p));
  for (const p of outs) wired.add('o' + p);
  const ref = PINS[TYPE(n)];
  if (ALL_PINS && ref){
    for (const p of ref.i) ins.add(p);
    for (const p of ref.o) outs.add(p);
  }
""",
    "blockPins union",
)

sub(
    "  return { ins: order(ins, ref && ref.i), outs: order(outs, ref && ref.o) };\n",
    "  return { ins: order(ins, ref && ref.i), outs: order(outs, ref && ref.o), wired };\n",
    "blockPins returns `wired`",
)

# ---- 5. render: arrow + solid label when wired, stub + dim when not ------
sub(
    """    p.ins.forEach((param, k) => {
      const y = HEAD_H + k * PIN_H + PIN_H / 2;
      g += `<path class="arrow" d="M0 ${y} l-7 -3.6 v7.2 z"></path>`;
      g += `<text class="pin" x="7" y="${y + 3.4}">${esc(param)}</text>`;
    });
    p.outs.forEach((param, k) => {
      const y = HEAD_H + k * PIN_H + PIN_H / 2;
      g += `<text class="pin" x="${b.w - 7}" y="${y + 3.4}" text-anchor="end">${esc(param)}</text>`;
    });
""",
    """    p.ins.forEach((param, k) => {
      const y = HEAD_H + k * PIN_H + PIN_H / 2;
      const on = p.wired.has('i' + param);
      g += on ? `<path class="arrow" d="M0 ${y} l-7 -3.6 v7.2 z"></path>`
              : `<path class="stub" d="M0 ${y} h-5"></path>`;
      g += `<text class="pin${on ? '' : ' off'}" x="7" y="${y + 3.4}">${esc(param)}</text>`;
    });
    p.outs.forEach((param, k) => {
      const y = HEAD_H + k * PIN_H + PIN_H / 2;
      const on = p.wired.has('o' + param);
      if (!on) g += `<path class="stub" d="M${b.w} ${y} h5"></path>`;
      g += `<text class="pin${on ? '' : ' off'}" x="${b.w - 7}" y="${y + 3.4}" text-anchor="end">${esc(param)}</text>`;
    });
""",
    "render dims the free pins",
)

# ---- 6. wire the toggle up ----------------------------------------------
sub(
    """$('#depth').addEventListener('input', () => {
  $('#depthN').textContent = $('#depth').value;
  if (root !== null) show(root, false);
});
""",
    """$('#depth').addEventListener('input', () => {
  $('#depthN').textContent = $('#depth').value;
  if (root !== null) show(root, false);
});

/* Every pin the block has, or only the wired ones. Both are worth having and
   which one you want depends on the job — tracing a signal wants the wires
   alone, checking what is still free wants the whole set — so it is a toggle,
   remembered per browser rather than reset on every visit. */
function paintPinsBtn(){
  const el = $('#pinsBtn');
  el.textContent = ALL_PINS ? '☰' : '☱';
  el.classList.toggle('on', ALL_PINS);
  el.title = ALL_PINS
    ? 'แสดงทุกขาที่บล็อกมี — คลิกเพื่อแสดงเฉพาะขาที่ต่อสาย'
    : 'แสดงเฉพาะขาที่ต่อสาย — คลิกเพื่อแสดงทุกขาที่บล็อกมี';
}
try { if (localStorage.getItem('fox-map-allpins') === '0') ALL_PINS = false; } catch (e) {}
paintPinsBtn();
$('#pinsBtn').addEventListener('click', () => {
  ALL_PINS = !ALL_PINS;
  try { localStorage.setItem('fox-map-allpins', ALL_PINS ? '1' : '0'); } catch (e) {}
  paintPinsBtn();
  if (root !== null) show(root, false);
});
""",
    "toggle handler",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (+%d)" % (n_before, len(s), len(s) - n_before))
