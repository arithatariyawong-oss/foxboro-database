# -*- coding: utf-8 -*-
"""Draw the branching step programs instead of refusing them.

Until now logic-view.html gave up the moment it met GTO/BIF/BIN/BIZ/BIT/BII/
EXIT/SSx -- 2,280 of the plant's 4,232 programs, including every MOV valve
interlock (PS1F203MOV1:130MOV059VPL and its ~750 siblings). The page said so
honestly, but "sequential, not combinational, read the listing" is not an
answer when the listing is 49 steps long.

WHAT THE MANUAL MAKES POSSIBLE (B0193AX Rev U, ch.14 CALC / ch.15 CALCA)

  Sec 14.8.1: "Unconditional transfer of control is supported only in a
  forward direction; looping backwards is not allowed."
  Per-opcode (GTO/GTI/BIF/BII/...): branching "to a step number less than or
  equal to the current step number or greater than the step number containing
  the END statement ... writes a '-4' (invalid goto syntax error) to the
  PERROR parameter."

So the control-flow graph of a legal program is a DAG whose edges only ever
run FORWARD in step order -- there is no loop to unroll and no fixed point to
chase. Checked against the plant before building any of this: 0 backward
jumps and 0 GTI in all 4,232 programs. Two more facts that the drawing leans
on, both from the per-opcode pages:

  * every branch is `sptr(after) = sptr(before)` -- a branch reads the
    accumulator, it does not pop it;
  * SET/SETB/CLR/CLRB are "Unconditional Set/Clear": they write a literal to
    a parameter and touch no stack at all. (Reading them as a pop is what
    made a first pass believe 7,156 blocks needed a value from their
    predecessor. The true figure is 239.)

THE DRAWING

Cut each program at its branches into basic blocks -- a leader is step 1, any
branch target, and anything falling out of a control instruction. Every one of
the 26,215 basic blocks in the plant compiles cleanly under the straight-line
rules the page already had, so each block gets a REAL gate sheet, drawn by the
existing layout()/render() unchanged. The blocks are then laid out as a
flowchart: one rank per level of the DAG, true/false edges between the
containers, so the sheet reads "these gates, then this test, then those
gates". 20 blocks is the worst case in the plant.

A conditional block ends in a test box fed by whatever the accumulator holds
there, carrying the manual's own condition (BIZ/BIF "= 0", BIT "<> 0", BIN
"< 0", BIP ">= 0", BII "INIT"). That box is where the two edges leave from,
so the condition that picks the path is drawn, not just named.

Each block's sheet is self-contained on purpose: the 239 blocks that consume a
value their predecessor left on the stack get an off-sheet carry chip naming
it, rather than a wire crossing container walls. Same reasoning as
signal-map.html's routing rules -- a wire that leaves the region it was laid
out in has nothing stopping it crossing whatever it likes.

Straight-line programs (1,952 of them) go down exactly the old path and look
exactly as before; only the multi-block case is new.
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


# ======================================================================= #
# 1. CSS for the flowchart containers                                     #
# ======================================================================= #
sub(
    ".nodraw{position:absolute; inset:0; display:flex; align-items:center;\n",
    "/* ---- basic-block flowchart ---- */\n"
    ".cfg-box{fill:var(--canvas); stroke:var(--blk-edge); stroke-width:1.2; rx:10}\n"
    ".cfg-head{fill:var(--blk-head); stroke:var(--blk-head-edge); stroke-width:1}\n"
    ".cfg-term .cfg-head{fill:var(--blk-root); stroke:var(--blk-root-edge)}\n"
    ".cfg-title{font-size:10.5px; font-weight:800; letter-spacing:.05em;\n"
    "  fill:var(--blk-head-ink)}\n"
    ".cfg-sub{font-size:9.5px; fill:var(--blk-head-ink); opacity:.8}\n"
    ".cfg-term .cfg-title,.cfg-term .cfg-sub{fill:var(--blk-root-ink)}\n"
    ".cfg-wire{fill:none; stroke:var(--wire); stroke-width:1.6}\n"
    ".cfg-wire.t{stroke:var(--mint-deep)}\n"
    ".cfg-wire.f{stroke:var(--wire)}\n"
    ".cfg-arrow{fill:var(--wire)}\n"
    ".cfg-arrow.t{fill:var(--mint-deep)}\n"
    ".cfg-lbl{font-size:9.5px; font-weight:800; letter-spacing:.06em;\n"
    "  fill:var(--text-dim); paint-order:stroke; stroke:var(--canvas);\n"
    "  stroke-width:3; stroke-linejoin:round}\n"
    ".cfg-lbl.t{fill:var(--mint-deep)}\n"
    "/* the test that picks the path — an ICC decision, drawn where the\n"
    "   accumulator it reads actually lands */\n"
    ".lg-test{fill:var(--ecb-head); stroke:var(--ecb-edge); stroke-width:1.2}\n"
    ".lg-testop{font-size:10.5px; font-weight:800; fill:var(--ecb-ink)}\n"
    ".lg-testc{font-size:11px; font-weight:800; fill:var(--ecb-ink)}\n"
    "/* a value the previous block left on the stack (239 blocks in the plant) */\n"
    ".lg-carry{fill:var(--surface-3); stroke:var(--blk-edge); stroke-width:1;\n"
    "  stroke-dasharray:3 2}\n"
    "\n"
    ".nodraw{position:absolute; inset:0; display:flex; align-items:center;\n",
    "CSS: flowchart containers, test box, carry chip",
)

# ======================================================================= #
# 2. compile(): take a step list + a shared node pool, not a whole block   #
# ======================================================================= #
sub(
    "/* Build the expression DAG. Returns {nodes, outs, error} — error is set when\n"
    "   the program does something the diagram cannot honestly show. */\n"
    "function compile(b){\n"
    "  const steps = b[6], refs = b[7];\n"
    "  const nodes = [], stack = [], outs = [];\n",
    "/* Build the expression DAG for ONE straight-line run of steps.\n"
    "   `nodes` is the program's shared pool and `stack` the run's own stack;\n"
    "   both are handed in so a basic block can be compiled the same way a\n"
    "   whole program used to be. Returns {outs, err}. */\n"
    "function compileSteps(steps, refs, nodes, stack){\n"
    "  const outs = [];\n",
    "compile(b) -> compileSteps(steps, refs, nodes, stack)",
)

sub(
    "  for (const [no, code, cmt] of steps){\n"
    "    const { op, arg } = parseStep(code);\n"
    "    if (!op || op === 'NOP' || op === 'END') continue;\n"
    "    if (BRANCH.has(op)){ err = { op, no }; break; }\n",
    "  /* A block that pops past its own pushes is reading what its predecessor\n"
    "     left behind — legal, and 239 blocks in the plant do it. It becomes an\n"
    "     off-sheet carry chip rather than a wire out through the container. */\n"
    "  const pop = () => {\n"
    "    if (stack.length) return stack.pop();\n"
    "    return push({ kind: 'carry', label: '↑ ค่าค้างจาก step ก่อน', inv: false,\n"
    "                  ref: '', ins: [], cmt: '' }), stack.pop();\n"
    "  };\n"
    "\n"
    "  for (const [no, code, cmt] of steps){\n"
    "    const { op, arg } = parseStep(code);\n"
    "    if (!op || op === 'NOP' || op === 'END') continue;\n"
    "    /* control instructions are the block's edges, not its contents, and\n"
    "       every one of them is sptr(after) = sptr(before) */\n"
    "    if (BRANCH.has(op)) continue;\n",
    "branches no longer abort the compile; add the carry-chip pop()",
)

# every stack.pop() that could underflow now goes through pop()
for old, new, what in [
    ("    if (op === 'POP'){ stack.pop(); continue; }\n",
     "    if (op === 'POP'){ pop(); continue; }\n",
     "POP uses pop()"),
    ("    if (TIMER.has(op)){\n"
     "      const src = stack.pop();\n"
     "      if (src === undefined){ err = { op, no, why: 'stack' }; break; }\n",
     "    if (TIMER.has(op)){\n"
     "      const src = pop();\n",
     "TIMER uses pop()"),
    ("    if (FLIP.has(op)){\n"
     "      const b2 = stack.pop(), a2 = stack.pop();\n"
     "      if (a2 === undefined || b2 === undefined){ err = { op, no, why: 'stack' }; break; }\n",
     "    if (FLIP.has(op)){\n"
     "      const b2 = pop(), a2 = pop();\n",
     "FLIP uses pop()"),
    ("    if (UNARY.has(op)){\n"
     "      const src = stack.pop();\n"
     "      if (src === undefined){ err = { op, no, why: 'stack' }; break; }\n",
     "    if (UNARY.has(op)){\n"
     "      const src = pop();\n",
     "UNARY uses pop()"),
    ("        const n = Math.max(1, parseInt(toks[0], 10) || 2);\n"
     "        if (stack.length < n){ err = { op, no, why: 'stack' }; break; }\n"
     "        ins = stack.splice(stack.length - n, n);\n",
     "        const n = Math.max(1, parseInt(toks[0], 10) || 2);\n"
     "        while (stack.length < n) pop(), stack.unshift(nodes.length - 1);\n"
     "        ins = stack.splice(stack.length - n, n);\n",
     "polyadic count uses pop() to backfill"),
    ("      } else if (toks.length === 1){\n"
     "        const a2 = stack.pop();\n"
     "        if (a2 === undefined){ err = { op, no, why: 'stack' }; break; }\n"
     "        ins = [a2, named(toks[0])];\n",
     "      } else if (toks.length === 1){\n"
     "        const a2 = pop();\n"
     "        ins = [a2, named(toks[0])];\n",
     "diadic-with-one-operand uses pop()"),
    ("      } else {\n"
     "        const b2 = stack.pop(), a2 = stack.pop();\n"
     "        if (a2 === undefined || b2 === undefined){ err = { op, no, why: 'stack' }; break; }\n"
     "        ins = [a2, b2];\n"
     "      }\n",
     "      } else {\n"
     "        const b2 = pop(), a2 = pop();\n"
     "        ins = [a2, b2];\n"
     "      }\n",
     "bare diadic uses pop()"),
    ("      const lit = push({ kind: 'const', label: LITERAL[op], inv: false, ref: '',\n"
     "                         ins: [], cmt: cmt || '' });\n"
     "      stack.pop();                           // it feeds the output, not the stack\n",
     "      /* B0193AX table 14-9 files these under \"Unconditional Set/Clear\":\n"
     "         the literal goes to the parameter and the stack is untouched. */\n"
     "      const lit = push({ kind: 'const', label: LITERAL[op], inv: false, ref: '',\n"
     "                         ins: [], cmt: cmt || '' });\n"
     "      stack.pop();\n",
     "note why SET/CLR leaves the stack alone"),
    ("  return { nodes, outs, err };\n}\n",
     "  return { outs, err };\n}\n",
     "compileSteps returns {outs, err}"),
]:
    sub(old, new, what)

# ======================================================================= #
# 3. cutBlocks() + compileCFG()                                           #
# ======================================================================= #
sub(
    "/* =======================================================================\n"
    "   3. LAYOUT + RENDER\n",
    "/* =======================================================================\n"
    "   2b. THE CONTROL-FLOW GRAPH\n"
    "   A leader starts a basic block: step 1, any branch target, and whatever\n"
    "   falls out of a control instruction. Because the manual forbids a\n"
    "   backward branch outright (B0193AX 14.8.1, and PERROR -4 for any target\n"
    "   at or before the current step), the blocks come out already in\n"
    "   topological order — block k's predecessors all have an index below k —\n"
    "   so one forward pass is enough and there is no fixed point to iterate.\n"
    "\n"
    "   The tests, straight from the per-opcode pages:\n"
    "     BIF s / BIZ s  branch if the accumulator is 0.0   (\"BIF is identical\n"
    "                    to BIZ\", both spelled out in ch.14)\n"
    "     BIT s          branch if it is non-zero\n"
    "     BIN s          branch if it is < 0.0\n"
    "     BIP s          branch if it is >= 0.0  (positive OR zero)\n"
    "     BII s          branch if the block is initializing this cycle\n"
    "     SSx o          set o and SKIP THE NEXT STEP on the same condition\n"
    "   ======================================================================= */\n"
    "const COND = { BIF: '= 0', BIZ: '= 0', BIT: '≠ 0', BIN: '< 0', BIP: '≥ 0',\n"
    "               BII: 'INIT' };\n"
    "const SKIPC = { SSF: '= 0', SSZ: '= 0', SST: '≠ 0', SSN: '< 0', SSP: '≥ 0',\n"
    "                SSI: 'INIT' };\n"
    "const TERM = new Set(['END', 'EXIT']);\n"
    "\n"
    "function cutBlocks(steps){\n"
    "  const order = steps.map(s => s[0]);\n"
    "  const at = new Map(order.map((no, i) => [no, i]));\n"
    "  const leaders = new Set(order.length ? [order[0]] : []);\n"
    "  steps.forEach(([no, code], i) => {\n"
    "    const { op, arg } = parseStep(code);\n"
    "    if (!BRANCH.has(op) && !TERM.has(op)) return;\n"
    "    if (i + 1 < order.length) leaders.add(order[i + 1]);        // fall-through\n"
    "    if (COND[op] || op === 'GTO'){\n"
    "      const t = parseInt(arg, 10);\n"
    "      if (at.has(t)) leaders.add(t);\n"
    "    }\n"
    "    if (SKIPC[op] && i + 2 < order.length) leaders.add(order[i + 2]);\n"
    "  });\n"
    "  const blocks = [];\n"
    "  for (const st of steps){\n"
    "    if (!blocks.length || leaders.has(st[0])) blocks.push({ steps: [] });\n"
    "    blocks[blocks.length - 1].steps.push(st);\n"
    "  }\n"
    "  blocks.forEach((b, k) => {\n"
    "    b.id = k;\n"
    "    b.from = b.steps[0][0];\n"
    "    b.to = b.steps[b.steps.length - 1][0];\n"
    "  });\n"
    "  /* the edges */\n"
    "  const idOf = new Map(blocks.map(b => [b.from, b.id]));\n"
    "  blocks.forEach(b => {\n"
    "    const last = b.steps[b.steps.length - 1];\n"
    "    const { op, arg } = parseStep(last[1]);\n"
    "    const i = at.get(last[0]);\n"
    "    const fall = i + 1 < order.length ? idOf.get(order[i + 1]) : undefined;\n"
    "    b.op = op;\n"
    "    b.out = [];\n"
    "    if (TERM.has(op)){ b.term = op; return; }\n"
    "    if (op === 'GTO'){\n"
    "      const t = idOf.get(parseInt(arg, 10));\n"
    "      if (t !== undefined) b.out.push({ to: t, kind: 'goto' });\n"
    "      else b.term = 'GTO';                       // off the end of the program\n"
    "      return;\n"
    "    }\n"
    "    if (COND[op]){\n"
    "      const t = idOf.get(parseInt(arg, 10));\n"
    "      if (t !== undefined) b.out.push({ to: t, kind: 'true' });\n"
    "      if (fall !== undefined) b.out.push({ to: fall, kind: 'false' });\n"
    "      b.cond = COND[op];\n"
    "      return;\n"
    "    }\n"
    "    if (SKIPC[op]){\n"
    "      const t = i + 2 < order.length ? idOf.get(order[i + 2]) : undefined;\n"
    "      if (t !== undefined) b.out.push({ to: t, kind: 'true' });\n"
    "      if (fall !== undefined) b.out.push({ to: fall, kind: 'false' });\n"
    "      b.cond = SKIPC[op];\n"
    "      return;\n"
    "    }\n"
    "    if (fall !== undefined) b.out.push({ to: fall, kind: 'next' });\n"
    "    else b.term = 'END';\n"
    "  });\n"
    "  return blocks;\n"
    "}\n"
    "\n"
    "/* Compile every basic block over one shared node pool. Each block's stack\n"
    "   starts empty on purpose: the alternative is a wire leaving its\n"
    "   container, which is the one thing signal-map.html's routing work says\n"
    "   never to allow. The 239 blocks that read past their own pushes get a\n"
    "   dashed carry chip from compileSteps() instead. */\n"
    "function compileCFG(b){\n"
    "  const refs = b[7];\n"
    "  const blocks = cutBlocks(b[6]);\n"
    "  const nodes = [];\n"
    "  let err = null;\n"
    "  for (const blk of blocks){\n"
    "    const stack = [];\n"
    "    const r = compileSteps(blk.steps, refs, nodes, stack);\n"
    "    blk.outs = r.outs;\n"
    "    if (r.err && !err) err = r.err;\n"
    "    /* the test that picks this block's exit, fed by the accumulator as it\n"
    "       stands at the branch — a branch does not pop, so this is simply the\n"
    "       top of the stack */\n"
    "    if (blk.cond)\n"
    "      blk.outs.push({ param: blk.cond, src: stack.length ? stack[stack.length - 1] : null,\n"
    "                      test: blk.op, cmt: '' });\n"
    "    blk.sheet = { nodes, outs: blk.outs };\n"
    "  }\n"
    "  return { blocks, nodes, err };\n"
    "}\n"
    "\n"
    "/* =======================================================================\n"
    "   3. LAYOUT + RENDER\n",
    "cutBlocks() + compileCFG()",
)

# ======================================================================= #
# 4. render() returns markup instead of writing the canvas                #
# ======================================================================= #
sub(
    "function render(L){\n"
    "  const { nodes, outs, box } = L;\n",
    "function renderSheet(L){\n"
    "  const { nodes, outs, box } = L;\n",
    "render(L) -> renderSheet(L)",
)

sub(
    "  world.innerHTML = parts.join('');\n"
    "}\n"
    "const clip = (s, n) =>",
    "  return parts.join('');\n"
    "}\n"
    "function render(L){ world.innerHTML = renderSheet(L); }\n"
    "const clip = (s, n) =>",
    "renderSheet returns the markup; render() keeps its old job",
)

# the test box and the carry chip need their own shapes
sub(
    "  /* output boxes */\n"
    "  outs.forEach((o, k) => {\n"
    "    const b = box.get('o' + k);\n"
    "    const dst = (CUR.dests || []).filter(([p]) => p === o.param).map(([, t]) => t);\n"
    "    let g = `<g class=\"lg-node lg-out\" transform=\"translate(${b.x},${b.y})\">`;\n"
    "    g += `<rect class=\"lg-io\" x=\"0\" y=\"0\" width=\"${b.w}\" height=\"${b.h}\" rx=\"3\"></rect>`;\n"
    "    g += `<text class=\"lg-name\" x=\"${b.w / 2}\" y=\"${dst.length ? 14 : 21}\" text-anchor=\"middle\">${esc(o.param)}</text>`;\n"
    "    if (dst.length)\n"
    "      g += `<text class=\"lg-ref\" x=\"${b.w / 2}\" y=\"26\" text-anchor=\"middle\">(${esc(clip(dst.join(', '), 34))})</text>`;\n"
    "    g += `</g>`;\n"
    "    parts.push(g);\n"
    "  });\n",
    "  /* output boxes — and the decision box, which is an \"out\" only in the\n"
    "     layout's sense: it is the last thing in the block and the two control\n"
    "     edges leave from it. */\n"
    "  outs.forEach((o, k) => {\n"
    "    const b = box.get('o' + k);\n"
    "    if (o.test){\n"
    "      let g = `<g class=\"lg-node lg-decide\" data-out=\"${k}\" transform=\"translate(${b.x},${b.y})\">`;\n"
    "      const w = b.w, h = b.h, c = 13;\n"
    "      g += `<path class=\"lg-test\" d=\"M0 ${h / 2} L${c} 0 H${w - c} L${w} ${h / 2} `\n"
    "         + `L${w - c} ${h} H${c} Z\"></path>`;\n"
    "      g += `<text class=\"lg-testop\" x=\"${c + 4}\" y=\"${h / 2 + 4}\">${esc(o.test)}</text>`;\n"
    "      g += `<text class=\"lg-testc\" x=\"${w - c - 4}\" y=\"${h / 2 + 4}\" text-anchor=\"end\">${esc(o.param)}</text>`;\n"
    "      g += `</g>`;\n"
    "      parts.push(g);\n"
    "      return;\n"
    "    }\n"
    "    const dst = (CUR.dests || []).filter(([p]) => p === o.param).map(([, t]) => t);\n"
    "    let g = `<g class=\"lg-node lg-out\" transform=\"translate(${b.x},${b.y})\">`;\n"
    "    g += `<rect class=\"lg-io\" x=\"0\" y=\"0\" width=\"${b.w}\" height=\"${b.h}\" rx=\"3\"></rect>`;\n"
    "    g += `<text class=\"lg-name\" x=\"${b.w / 2}\" y=\"${dst.length ? 14 : 21}\" text-anchor=\"middle\">${esc(o.param)}</text>`;\n"
    "    if (dst.length)\n"
    "      g += `<text class=\"lg-ref\" x=\"${b.w / 2}\" y=\"26\" text-anchor=\"middle\">(${esc(clip(dst.join(', '), 34))})</text>`;\n"
    "    g += `</g>`;\n"
    "    parts.push(g);\n"
    "  });\n",
    "render the decision box as a flowchart diamond",
)

sub(
    "    } else {\n"
    "      g += `<rect class=\"lg-io\" x=\"0\" y=\"0\" width=\"${b.w}\" height=\"${b.h}\" rx=\"3\"></rect>`;\n",
    "    } else {\n"
    "      g += `<rect class=\"${n.kind === 'carry' ? 'lg-carry' : 'lg-io'}\" x=\"0\" y=\"0\"`\n"
    "         + ` width=\"${b.w}\" height=\"${b.h}\" rx=\"3\"></rect>`;\n",
    "carry chip gets its own dashed shape",
)

# layout() must not treat a whole shared node pool as this block's own
sub(
    "function layout(c){\n"
    "  const { nodes, outs } = c;\n"
    "  const used = new Set();\n",
    "/* `nodes` is the whole program's pool once a CFG is in play, so `used` —\n"
    "   which is seeded only from this sheet's outs — is what keeps a block's\n"
    "   drawing to its own nodes. */\n"
    "function layout(c){\n"
    "  const { nodes, outs } = c;\n"
    "  const used = new Set();\n",
    "layout(): note that `used` scopes a sheet to its own nodes",
)

io.open(PAGE, "w", encoding="utf8", newline="").write(s)
print("logic-view.html %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
