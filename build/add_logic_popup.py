# -*- coding: utf-8 -*-
"""Add a "Logic View" item to signal-map.html's block menu, offered only on
the 4,232 blocks logic.js actually holds a step program for, and opened as
a popup (an iframe in a modal) rather than a navigation -- so picking it
never loses the signal map you had open.

logic.js (0.43 MB) is fetched and decompressed once in the background,
right after the graph itself boots, purely to build the name index the
menu checks. That is well before anyone has had time to click a block, so
in practice the item is simply there or not from the first click, the same
way data.js is fetched lazily the first time Properties is opened -- except
this one starts early, because the menu needs the answer *before* it draws
itself, not after someone has already asked.
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


# ---- CSS: modal + backdrop, styled like .props ---------------------------
sub(
    '.props-note{padding:16px; font-size:13px; color:var(--text-dim); text-align:center}\n',
    '.props-note{padding:16px; font-size:13px; color:var(--text-dim); text-align:center}\n'
    "\n"
    "/* ---- logic view popup ---- */\n"
    ".logic-backdrop{\n"
    "  position:fixed; inset:0; z-index:150; display:flex; align-items:center; justify-content:center;\n"
    "  background:rgba(0,0,0,.5); padding:26px;\n"
    "}\n"
    ".logic-modal{\n"
    "  width:min(1400px,96vw); height:min(880px,92vh); display:flex; flex-direction:column;\n"
    "  background:var(--surface); border:1px solid var(--border);\n"
    "  border-radius:var(--r-md); box-shadow:var(--lift), var(--inset-hi); overflow:hidden;\n"
    "}\n"
    ".logic-modal-head{\n"
    "  display:flex; align-items:center; gap:12px; padding:13px 18px;\n"
    "  border-bottom:1px solid var(--border-soft); flex:none;\n"
    "}\n"
    ".logic-modal-head b{font-size:15px; font-weight:800}\n"
    ".logic-modal-head span{font-size:12px; color:var(--text-dim)}\n"
    ".logic-modal-head .props-close{margin-left:auto}\n"
    ".logic-modal iframe{flex:1; border:0; width:100%}\n",
    "CSS: .logic-backdrop / .logic-modal",
)

# ---- JS: name index, loaded in the background ----------------------------
sub(
    "let menuEl = null;\n",
    "let LOGIC_NAMES = null, logicPromise = null;\n"
    "function loadLogicNames(){\n"
    "  /* Kicked off once at boot, not on first click -- see file header. */\n"
    "  if (LOGIC_NAMES) return Promise.resolve(LOGIC_NAMES);\n"
    "  if (!logicPromise) logicPromise = new Promise((res, rej) => {\n"
    "    if (window.FOX_LOGIC_B64) return res();\n"
    "    const s = document.createElement('script');\n"
    "    s.src = 'logic.js';\n"
    "    s.onload = () => res();\n"
    "    s.onerror = () => rej(new Error('เปิด logic.js ไม่ได้'));\n"
    "    document.head.appendChild(s);\n"
    "  }).then(async () => {\n"
    "    const g = await inflate(window.FOX_LOGIC_B64);\n"
    "    LOGIC_NAMES = new Set(g.blocks.map(b => b[0]));\n"
    "    return LOGIC_NAMES;\n"
    "  }).catch(err => { console.error(err); return null; });\n"
    "  return logicPromise;\n"
    "}\n"
    "\n"
    "let menuEl = null;\n",
    "JS: LOGIC_NAMES + loadLogicNames()",
)

sub(
    "addEventListener('keydown', e => { if (e.key === 'Escape'){ closeMenu(); closeProps(); } });\n",
    "addEventListener('keydown', e => {\n"
    "  if (e.key === 'Escape'){ closeMenu(); closeProps(); closeLogicPopup(); }\n"
    "});\n",
    "Escape also closes the logic popup",
)

sub(
    '    `<button data-a="props">Properties…<i>ค่าภายใน</i></button>` +\n'
    '    `<button data-a="copy">คัดลอกชื่อ tag</button>`;\n',
    '    `<button data-a="props">Properties…<i>ค่าภายใน</i></button>` +\n'
    "    (LOGIC_NAMES && LOGIC_NAMES.has(NAME(n))\n"
    '      ? `<button data-a="logic">Logic View…<i>step program</i></button>` : \'\') +\n'
    '    `<button data-a="copy">คัดลอกชื่อ tag</button>`;\n',
    "menu: Logic View item, only when the block has one",
)

sub(
    "    if (a.dataset.a === 'root') show(n, true);\n"
    "    else if (a.dataset.a === 'props') openProps(n);\n"
    "    else if (a.dataset.a === 'copy') navigator.clipboard?.writeText(NAME(n));\n",
    "    if (a.dataset.a === 'root') show(n, true);\n"
    "    else if (a.dataset.a === 'props') openProps(n);\n"
    "    else if (a.dataset.a === 'logic') openLogicPopup(n);\n"
    "    else if (a.dataset.a === 'copy') navigator.clipboard?.writeText(NAME(n));\n",
    "menu click: logic -> openLogicPopup",
)

# ---- JS: the popup itself, and starting the background load at boot -----
sub(
    "/* =======================================================================\n"
    "   5c. PROPERTIES\n",
    "/* =======================================================================\n"
    "   5c. LOGIC VIEW POPUP — offered from the menu only on a block logic.js\n"
    "   actually carries a step program for (CALC / CALCA / LOGIC / MATH with\n"
    "   STEP01..STEP50 written); logic-view.html itself still explains why\n"
    "   nothing else has one, this just keeps the option off blocks that never\n"
    "   could. An iframe in a modal, not a navigation — picking Logic View does\n"
    "   not cost you the map you had open, the same reason Properties is a\n"
    "   panel and not its own page.\n"
    "   ======================================================================= */\n"
    "let logicEl = null;\n"
    "function closeLogicPopup(){ if (logicEl){ logicEl.remove(); logicEl = null; } }\n"
    "function openLogicPopup(n){\n"
    "  closeLogicPopup();\n"
    "  const el = document.createElement('div');\n"
    "  el.className = 'logic-backdrop';\n"
    "  el.innerHTML =\n"
    '    `<div class="logic-modal">` +\n'
    '      `<div class="logic-modal-head"><b>${esc(NAME(n))}</b>` +\n'
    "        `<span>${esc(TYPE(n))}${DESC(n) ? ' · ' + esc(DESC(n)) : ''}</span>` +\n"
    '        `<button class="props-close" title="ปิด">✕</button></div>` +\n'
    '      `<iframe src="logic-view.html?tag=${encodeURIComponent(NAME(n))}&embed=1"></iframe>` +\n'
    "    `</div>`;\n"
    "  document.body.appendChild(el);\n"
    "  logicEl = el;\n"
    "  /* click the dim backdrop (not the modal itself) to dismiss */\n"
    "  el.addEventListener('pointerdown', ev => { if (ev.target === el) closeLogicPopup(); });\n"
    "  el.querySelector('.props-close').addEventListener('click', closeLogicPopup);\n"
    "}\n"
    "loadLogicNames();\n"
    "\n"
    "/* =======================================================================\n"
    "   5d. PROPERTIES\n",
    "insert the popup section ahead of PROPERTIES, bumped to 5d",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("signal-map.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
