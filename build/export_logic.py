# -*- coding: utf-8 -*-
"""Build logic.js -- the CALC/CALCA/LOGIC/MATH step programs, for the Logic View.

4,232 blocks in the plant carry a step program in STEP01..STEP50. It is a
stack machine, and ICC renders it as a function block diagram (12.png). This
pulls out everything that page needs so it loads ONE small file instead of
the 2.4 MB data.js:

  * the program itself, split into step number / instruction / ;comment --
    the comments are hand-written by the engineers who built the interlock
    (";LEVEL H", ";AUTO STR CMD") and are the most valuable thing here;
  * the VALUE of every I/O parameter the program names, so a BI02 box can be
    labelled with the V3973:39LISA223.ALMSTA.B15 it actually reads. Only the
    parameters the program mentions are carried -- there is no point in
    shipping BI07..BI16 for a program that stops at BI06;
  * where each OUT lands, read back out of graph.js rather than rebuilt
    here: that file already resolved every reference against the right CP,
    including the bit-qualified ones, and doing it twice invites the two
    copies to disagree.

Only 48% of the programs are branch-free (no GTO/BIZ/BIF/EXIT). The other
half cannot be drawn as a pure gate diagram at all, so the page always shows
the listing and draws the diagram when it can. The `br` flag is computed
here so the page does not have to scan for it.
"""
import base64
import gzip
import json
import os
import re
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
DATA = os.path.join(WEB, "data.js")
GRAPH = os.path.join(WEB, "graph.js")
OUT = os.path.join(WEB, "logic.js")

t0 = time.time()


def load(path):
    raw = open(path, encoding="utf8").read()
    b64 = raw.split('"', 1)[1].rsplit('"', 1)[0]
    return json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf8"))


d = load(DATA)
N, H, C = d["n"], d["h"], d["c"]
IDX = {h: i for i, h in enumerate(H) if h}
print("data.js %d rows (%.1fs)" % (N, time.time() - t0))


def dense(col):
    a = [-1] * N
    sp = C[IDX[col]] if col in IDX else None
    if not isinstance(sp, dict):
        return a, []
    v = sp["v"]
    if "r" in sp:
        row = 0
        for k, dl in enumerate(sp["r"]):
            row += dl
            a[row] = v[k]
    else:
        for k, c in enumerate(v):
            a[k] = c
    return a, sp["d"]


nmA, nmD = dense("NAME")
tyA, tyD = dense("TYPE")
dsA, dsD = dense("DESCRP")
cpA, cpD = dense("CP NAME")
arA, arD = dense("AREA")
STEPS = [dense("STEP%02d" % i) for i in range(1, 51)]

# Every column that could hold an I/O parameter a step operand names. The
# operand shapes actually seen are BI##, BO##, RI##, RO##, IO##, II##, LI##,
# LO##, M## and bare numbers; M## is a memory register with no column of its
# own, and a bare number is a constant.
PARAM_COL = re.compile(r"^(?:BI|BO|RI|RO|IO|II|LI|LO)\d\d$")
pcols = {h: dense(h) for h in H if h and PARAM_COL.match(h)}
print("I/O parameter columns: %d  (%.1fs)" % (len(pcols), time.time() - t0))

# ---- where each output lands, straight out of graph.js -------------------
g = load(GRAPH)
gname = [n[0] for n in g["nodes"]]
dests = defaultdict(list)                 # block name -> [(out param, target)]
for e in g["edges"]:
    s, sp, t, tp = e[0], e[1], e[2], e[3]
    qual = e[4] if len(e) > 4 else ""
    dests[gname[s]].append((sp, gname[t] + "." + tp + ("." + qual if qual else "")))
print("graph.js %d edges (%.1fs)" % (len(g["edges"]), time.time() - t0))

# ---- walk the blocks -----------------------------------------------------
BRANCH = {"GTO", "GTI", "BIZ", "BIF", "BIN", "BIP", "BIT", "BII", "EXIT",
          "SSF", "SSI", "SSN", "SSP", "SST", "SSZ"}
OPERAND = re.compile(r"~?[A-Za-z]+\d+")

blocks = []
n_steps = 0
for i in range(N):
    prog = []
    for k, (a, dd) in enumerate(STEPS):
        if a[i] < 0:
            continue
        raw = dd[a[i]]
        if not raw.strip():
            continue
        code, _, cmt = raw.partition(";")
        code = code.strip()
        if not code:
            continue
        prog.append([k + 1, code, cmt.strip()])
    if not prog:
        continue

    name = nmD[nmA[i]] if nmA[i] >= 0 else ""
    if not name:
        continue

    # only the parameters this program actually names
    want = set()
    for _, code, _ in prog:
        for tok in OPERAND.findall(code):
            want.add(tok.lstrip("~").upper())
    refs = {}
    for p in want:
        col = pcols.get(p)
        if col and col[0][i] >= 0:
            v = col[1][col[0][i]]
            if v != "":
                refs[p] = v

    out = [(p, t) for p, t in dests.get(name, []) if p in want]
    branchy = any(c.split()[0].upper() in BRANCH for _, c, _ in prog if c.split())

    blocks.append([
        name,                                          # 0
        tyD[tyA[i]] if tyA[i] >= 0 else "",            # 1
        dsD[dsA[i]] if dsA[i] >= 0 else "",            # 2
        cpD[cpA[i]] if cpA[i] >= 0 else "",            # 3
        arD[arA[i]] if arA[i] >= 0 else "",            # 4
        i,                                             # 5 row in data.js
        prog,                                          # 6 [[step, code, comment]]
        refs,                                          # 7 {param: value}
        out,                                           # 8 [[param, target]]
        1 if branchy else 0,                           # 9 uses a branch opcode
    ])
    n_steps += len(prog)

blocks.sort(key=lambda b: b[0])
n_br = sum(b[9] for b in blocks)
print("blocks %d, steps %d, branch-free %d (%.0f%%)"
      % (len(blocks), n_steps, len(blocks) - n_br,
         100.0 * (len(blocks) - n_br) / max(len(blocks), 1)))

payload = {"blocks": blocks}
js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf8")
gz = gzip.compress(js, 9)
enc = base64.b64encode(gz).decode("ascii")
open(OUT, "w", encoding="utf8").write('window.FOX_LOGIC_B64="%s";\n' % enc)

print("json %.2f MB -> gzip %.2f MB -> logic.js %.2f MB  (%.1fs)"
      % (len(js) / 1e6, len(gz) / 1e6, os.path.getsize(OUT) / 1e6, time.time() - t0))
