# -*- coding: utf-8 -*-
"""Three fixes on top of the branching flowchart, found by driving it.

1. THE BACKFILL COULD SPIN FOREVER. `AND 3` with only two things on the stack
   has to invent the third (it came from the predecessor block). The first
   cut wrote `while (stack.length < n) pop(), stack.unshift(...)`, which is
   correct only while the stack is EMPTY: pop() on a non-empty short stack
   takes the top off and unshift puts it straight back at the bottom, so the
   length never changes and the tab hangs. Rewritten to always create the
   carry chip and slide it underneath, which grows the stack every pass.

2. THE TRUE/FALSE EDGES LEFT FROM THE MIDDLE OF THE CONTAINER, nowhere near
   the test that decides them — on a wide sheet the decision box is at the
   far right and the two arrows came out under the input boxes. They now
   leave from under the decision box itself.

3. fit() RAN TOO EARLY on the first draw. Called straight after renderCFG it
   settled on k=0.77 for a 2,257px-tall chart that needed 0.32; calling it
   again by hand gave the right answer, so the geometry was fine and only the
   timing was wrong. A second fit on the next frame, the same trick the fold
   button already used.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "logic-view.html"

s = io.open(PAGE, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


# ---- 1. the backfill --------------------------------------------------
sub(
    "        while (stack.length < n) pop(), stack.unshift(nodes.length - 1);\n",
    "        /* the missing operands came from the predecessor block, so they\n"
    "           belong UNDER what this block pushed, not on top of it. push()\n"
    "           always lands on top, hence the pop/unshift shuffle -- and it is\n"
    "           what makes the loop terminate, since every pass adds one. */\n"
    "        while (stack.length < n){\n"
    "          const c = push({ kind: 'carry', label: '↑ ค่าค้างจาก step ก่อน',\n"
    "                           inv: false, ref: '', ins: [], cmt: '' });\n"
    "          stack.pop();\n"
    "          stack.unshift(c);\n"
    "        }\n",
    "polyadic backfill can no longer spin",
)

# ---- 1b. a store with nothing on the stack is storing the predecessor's --
# B6 of 130MOV059VPL is `STM M01; LAC M01; OUT RO01`: the STM writes whatever
# B5 left in the accumulator. OUT/STM copy rather than pop, so the old code
# read `stack[top]` and quietly wrote src=null when the stack was empty --
# an output box fed by nothing at all. It gets the same carry chip every
# other underflow gets.
sub(
    "      const src = stack.length ? stack[stack.length - 1] : null;\n"
    "      outs.push({ param: arg, src, cmt: cmt || '', op, no });\n",
    "      /* pop() hands back the carry it invented but takes it off the\n"
    "         stack; a store COPIES, so it has to go straight back on */\n"
    "      if (!stack.length) stack.push(pop());\n"
    "      const src = stack[stack.length - 1];\n"
    "      outs.push({ param: arg, src, cmt: cmt || '', op, no });\n",
    "a store off an empty stack shows the carry it is really storing",
)


# ---- 2. anchor the branch edges under the decision box ----------------
sub(
    "  const G = blocks.map(blk => {\n"
    "    const g = document.createElementNS(SVGNS, 'g');\n"
    "    g.setAttribute('class', 'cfg-sheet');\n"
    "    g.innerHTML = renderSheet(layout(blk.sheet));\n"
    "    world.appendChild(g);\n"
    "    return g;\n"
    "  });\n",
    "  const testAt = [];\n"
    "  const G = blocks.map((blk, k) => {\n"
    "    const g = document.createElementNS(SVGNS, 'g');\n"
    "    g.setAttribute('class', 'cfg-sheet');\n"
    "    const L = layout(blk.sheet);\n"
    "    g.innerHTML = renderSheet(L);\n"
    "    /* where the decision box landed inside the sheet, so the two control\n"
    "       edges can leave from under the test that picks them rather than\n"
    "       from the middle of a container that may be 700px wide */\n"
    "    const ti = blk.outs.findIndex(o => o.test);\n"
    "    if (ti >= 0 && L.box.has('o' + ti)){\n"
    "      const tb = L.box.get('o' + ti);\n"
    "      testAt[k] = tb.x + tb.w / 2;\n"
    "    }\n"
    "    world.appendChild(g);\n"
    "    return g;\n"
    "  });\n",
    "remember where each block's decision box landed",
)

sub(
    "      const sx = n > 1 ? b.x + b.w * (i + 1) / (n + 1) : b.x + b.w / 2;\n",
    "      /* sheetX is where this block's sheet starts inside its container */\n"
    "      const sheetX = b.x + CFG_PAD - bb[k].x;\n"
    "      const anchor = testAt[k] != null ? sheetX + testAt[k] : b.x + b.w / 2;\n"
    "      const sx = n > 1\n"
    "        ? Math.min(Math.max(anchor + (i === 0 ? -22 : 22), b.x + 14), b.x + b.w - 14)\n"
    "        : anchor;\n",
    "branch edges leave from under the decision box",
)

# ---- 3. the container header says what the test is --------------------
sub(
    "    g += `<text class=\"cfg-sub\" x=\"${b.x + 10 + 22}\" y=\"${b.y + 15}\">step ${blk.from}`\n"
    "       + `${blk.to !== blk.from ? '–' + blk.to : ''}${blk.term ? ' · ' + blk.term : ''}</text>`;\n",
    "    g += `<text class=\"cfg-sub\" x=\"${b.x + 10 + 22}\" y=\"${b.y + 15}\">step ${blk.from}`\n"
    "       + `${blk.to !== blk.from ? '–' + blk.to : ''}`\n"
    "       + `${blk.cond ? ' · ' + esc(blk.op) + ' ' + esc(blk.cond) : ''}`\n"
    "       + `${blk.term ? ' · ' + esc(blk.term) : ''}</text>`;\n",
    "container header names the test",
)

# ---- 4. fit on the next frame too -------------------------------------
sub(
    "  if (one) render(layout(cfg.blocks[0].sheet));\n"
    "  else renderCFG(cfg);\n"
    "  fit();\n"
    "}\n",
    "  if (one) render(layout(cfg.blocks[0].sheet));\n"
    "  else renderCFG(cfg);\n"
    "  fit();\n"
    "  /* the first draw of a session can measure the stage before the flex\n"
    "     layout has settled and land on far too tight a zoom; a second pass on\n"
    "     the next frame costs nothing and is always right */\n"
    "  requestAnimationFrame(fit);\n"
    "}\n",
    "fit() again on the next frame",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("logic-view.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
