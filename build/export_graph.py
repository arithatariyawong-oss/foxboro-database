# -*- coding: utf-8 -*-
"""Build the signal graph for the wiring diagram and write graph.js.

Two sources meet here:

  * data.js -- every block in the plant, and the parameter VALUES that name
    another block ("V501_N7:05FT065.PNT", ":03FV042.BCALCO"). Each such value
    is one wire: the named block's parameter drives this block's parameter.
  * block_params.json -- B0193AX's parameter tables, which say whether a
    parameter is an INPUT or an OUTPUT and whether it is connectable. That is
    what puts a pin on the left or the right edge of a box, and in what order.

A reference may or may not carry a compound. ":05FV065.BCALCO" means "in my
own compound", so an unqualified name is resolved against the same CP first
and only then anywhere -- getting that backwards silently wires loops in one
unit to identically-named blocks in another (the plant reuses tag names
across CPs, e.g. V501:05FRC065 and V501_N7:05FRC065).

Output graph.js mirrors data.js: gzip + base64, inflated by the page with
DecompressionStream.
"""
import base64, gzip, json, os, re, sys, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
DATA = os.path.join(WEB, "data.js")
PARAMS = os.path.join(WEB, "block_params.json")
# newest export in the folder, not a fixed filename -- these are dated
# (jove_20260518_2.exp) and a new one arrives whenever Jove is re-exported
import glob
_j = sorted(glob.glob(os.path.join(os.path.dirname(WEB), "00 RAW DATABASE",
                                   "Jove", "*.exp")))
JOVE = _j[-1] if _j else ""
OUT = os.path.join(WEB, "graph.js")

t0 = time.time()
raw = open(DATA, encoding="utf8").read()
b64 = raw.split('"', 1)[1].rsplit('"', 1)[0]
d = json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf8"))
N, H, C = d["n"], d["h"], d["c"]
IDX = {h: i for i, h in enumerate(H) if h}
BP = json.load(open(PARAMS, encoding="utf8"))
print("data.js %d rows, block_params %d types (%.1fs)" % (N, len(BP), time.time() - t0))


def dense(col):
    """codes per row (-1 = empty), plus the column's dictionary"""
    a = [-1] * N
    sp = C[IDX[col]]
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


cpA, cpD = dense("CP NAME")
nmA, nmD = dense("NAME")
tyA, tyD = dense("TYPE")
dsA, dsD = dense("DESCRP")
ioA, ioD = dense("IOM_ID")
pnA, pnD = dense("PNT_NO")
arA, arD = dense("AREA")

name = [nmD[c] if c >= 0 else "" for c in nmA]
typ = [tyD[c] if c >= 0 else "" for c in tyA]

# ---- resolve a reference to a row -------------------------------------
by_full = {}                       # "COMPOUND:BLOCK" -> row
by_short = defaultdict(list)       # "BLOCK"          -> rows
for i, n in enumerate(name):
    if not n:
        continue
    by_full.setdefault(n, i)
    by_short[n.split(":")[-1]].append(i)

# A reference may carry a third dot-separated token, and dropping those was
# silently costing the diagram a QUARTER of the plant's wiring -- 14,639 of
# 60,137 reference-shaped values. Two families use it, and in both the block
# and the parameter are still the first two tokens; the tail only qualifies
# the connection:
#
#   V3973:39LISA223.ALMSTA.B15   bit 15 of a packed status word. PAKCIN is
#                                11,897 of these on its own (a PAKIN block
#                                exists to fan one word out bit by bit),
#                                then ALMSTA, LO01, BLKSTA, ECBSTA, DEVSTS.
#   C305_1:03FI046.MA.1          the boolean form, where the source and the
#                                destination parameter are always the same
#                                one (MA -> MA, IN_13 -> IN_13).
#
# ICC's own Input References pane prints the whole string (see 11.png), so
# the tail is kept as a fifth field on the edge and the map prints it too.
REF = re.compile(r"^([A-Za-z0-9_]{0,32}):?([A-Za-z0-9_]{1,32})"
                 r"\.([A-Za-z0-9_]{1,16})(?:\.([A-Za-z0-9_]{1,6}))?$")
SKIP_COLS = {"Source.Name", "VERNUM"}

edges = []          # (src_row, src_param, dst_row, dst_param, qualifier)
seen = set()
for ci, sp in enumerate(C):
    if not isinstance(sp, dict) or H[ci] in SKIP_COLS:
        continue
    col = H[ci]
    ok = {}
    for k, v in enumerate(sp["d"]):
        if "." not in v or len(v) > 72:
            continue
        try:
            float(v)                      # 1.0 / 0.5 are constants, not refs
            continue
        except ValueError:
            pass
        m = REF.match(v)
        if m:
            ok[k] = m.groups()
    if not ok:
        continue
    v, rr = sp["v"], sp.get("r")
    row = 0
    for k, code in enumerate(v):
        row = row + rr[k] if rr else k
        g = ok.get(code)
        if not g:
            continue
        comp, blk, par, qual = g
        src = by_full.get("%s:%s" % (comp, blk)) if comp else None
        if src is None:
            cands = by_short.get(blk)
            if not cands:
                continue
            same = [r for r in cands if cpA[r] == cpA[row]]   # own CP wins
            src = (same or cands)[0]
        # A block referencing its own parameter is a real wire, not noise:
        # H101:01PIC130 has RSP = H101:01PIC130.SPT, and the ICC detail draws
        # exactly that loop from the block's own SPT back into its RSP.
        key = (src, par, row, col, qual or "")
        if key in seen:
            continue
        seen.add(key)
        edges.append(key)

n_qual = sum(1 for e in edges if e[4])
print("parameter edges: %d  (%d carry a bit/boolean qualifier)  (%.1fs)"
      % (len(edges), n_qual, time.time() - t0))

# ---- the field ends: ECB <-> the I/O blocks bound to it -----------------
# An AIN does not *reference* its FBM through a parameter — it names it by
# IOM_ID, and the ECB carrying that DEV_ID is the block that stands for the
# hardware. Wiring those in is what makes an ECB the source of every input
# chain and the sink of every output chain, instead of the first AIN and the
# last AOUT. IOMIDR is the redundant partner module and is wired too.
irA, irD = dense("IOMIDR")
dvA, dvD = dense("DEV_ID")

dev_index = defaultdict(list)
for i in range(N):
    if typ[i].startswith("ECB") and dvA[i] >= 0:
        dev_index[dvD[dvA[i]]].append(i)


def ecb_for(dev, row):
    """the ECB in this block's own CP wins; the plant reuses device ids"""
    cands = dev_index.get(dev)
    if not cands:
        return None
    same = [r for r in cands if cpA[r] == cpA[row]]
    return (same or cands)[0]


n_hw, n_missed = 0, 0
for i in range(N):
    t = typ[i]
    if not t or t.startswith("ECB") or ioA[i] < 0 or not name[i]:
        continue
    # direction is the block's job: an *OUT block drives the field, the rest
    # read it. AO/MAO are the two output types whose names do not say so.
    is_out = "OUT" in t or t in ("AO", "MAO")
    chan = pnD[pnA[i]] if pnA[i] >= 0 else ""
    pin_ecb = ("CH " + chan) if chan else "DEV"
    for pin_blk, arr, dic in (("IOM_ID", ioA, ioD), ("IOMIDR", irA, irD)):
        if arr[i] < 0:
            continue
        e = ecb_for(dic[arr[i]], i)
        if e is None:
            n_missed += 1
            continue
        edges.append((i, pin_blk, e, pin_ecb, "") if is_out else (e, pin_ecb, i, pin_blk, ""))
        n_hw += 1

print("hardware edges: %d  (%d I/O bindings had no ECB in the export)" % (n_hw, n_missed))
print("edges total: %d  (%.1fs)" % (len(edges), time.time() - t0))

# ---- Jove: the OM/API objects, and the parameters they are bound to -----
# Section 1 of the export (Object Type 1) is the connected one. Parsed here
# rather than after the keep-set is built, because 5,445 of these
# connections are the ONLY thing touching their block -- freeze the keep-set
# first and those blocks are dropped before Jove can put them back.
import csv

JREF = re.compile(r"^([A-Za-z0-9_]+):([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)"
                  r"(?:\.([A-Za-z0-9_]+))?$")
jove = []                      # (obj, desc, host, attr, row, param, qual, is_write)
j_miss = 0
try:
    jtext = open(JOVE, encoding='utf8', errors='replace', newline='').read()
except OSError as e:
    print('Jove export not read (%s) -- graph built without it' % e)
    jtext = ''

jsecs, jhdr, jcur = [], None, None
for line in jtext.split('\r\n'):
    if line.startswith('#'):
        if jcur is not None:
            jsecs.append((jhdr, jcur))
        jhdr = next(csv.reader([line[1:]]))
        jcur = []
    elif jcur is not None and line.strip():
        jcur.append(line)
if jcur is not None:
    jsecs.append((jhdr, jcur))

for jh, jrows in jsecs:
    ji = {c: k for k, c in enumerate(jh)}
    if 'Connection' not in ji:            # type 0 and the empty OPC UA section
        continue
    for r in csv.reader(jrows):
        if len(r) != len(jh):
            continue
        m = JREF.match(r[ji['Connection']])
        if not m:
            j_miss += 1
            continue
        row = by_full.get('%s:%s' % (m.group(1), m.group(2)))
        if row is None:
            j_miss += 1
            continue
        obj = r[ji['Name']]
        wr = r[ji.get('Buffered Write', -1)] == 'true' if 'Buffered Write' in ji else False
        rd = r[ji.get('Buffered Read', -1)] == 'true' if 'Buffered Read' in ji else False
        attr = obj.split('.', 1)[1] if '.' in obj else obj
        # both flags set is two real connections, one each way; neither set
        # is still a configured link and is shown as a read
        for is_write in ([True] if wr else []) + ([False] if rd or not wr else []):
            jove.append((obj, r[ji['Description']], r[ji.get('API Host Name', 0)],
                         attr, row, m.group(3), m.group(4) or '', is_write))
print('Jove objects bound to a block: %d edges over %d objects (%d unresolved)'
      % (len(jove), len({j[0] for j in jove}), j_miss))

# ---- keep only the blocks the diagram can reach -------------------------
used = set()
for s, _, t, _, _ in edges:
    used.add(s)
    used.add(t)
for i in range(N):                      # field I/O is an endpoint worth having
    if ioA[i] >= 0 and name[i]:
        used.add(i)
for j in jove:                          # ...and so is anything Jove talks to
    used.add(j[4])
rows = sorted(used)
remap = {r: k for k, r in enumerate(rows)}

nodes = [[
    name[r],                                    # 0 compound:block
    typ[r],                                     # 1 block type
    dsD[dsA[r]] if dsA[r] >= 0 else "",         # 2 description
    cpD[cpA[r]] if cpA[r] >= 0 else "",         # 3 CP
    arD[arA[r]] if arA[r] >= 0 else "",         # 4 area
    ioD[ioA[r]] if ioA[r] >= 0 else "",         # 5 FBM id
    pnD[pnA[r]] if pnA[r] >= 0 else "",         # 6 point number
    r,                                          # 7 row in data.js — the key
] for r in rows]                                #   Properties reads values by
# the qualifier is a 5th element only where there is one -- 24% of the edges
# carry one, and padding the other 76% with "" would cost graph.js for nothing
elist = [[remap[s], sp, remap[t], tp] + ([q] if q else [])
         for s, sp, t, tp, q in edges]

# ---- the Jove objects, appended as nodes of their own -------------------
# A Jove node has no data.js row, so field 7 is -1 and signal-map.html shows
# the object's own attributes instead of trying to read a row that is not
# there. Field 3 carries the API host, which is the only 'where it lives'
# a Jove object has.
jnode = {}
n_jw = 0
for obj, desc, host, attr, row, param, qual, is_write in jove:
    if obj not in jnode:
        jnode[obj] = len(nodes)
        nodes.append([obj, 'JOVE', desc, host, '', '', attr, -1])
    j, b = jnode[obj], remap[row]
    # Jove writing INTO the DCS is a command path and is drawn as one
    e = ([j, attr, b, param] if is_write else [b, param, j, attr])
    if qual:
        e.append(qual)
    elist.append(e)
    n_jw += 1 if is_write else 0
print('Jove nodes %d, edges %d (%d of them Jove writing into the DCS)'
      % (len(jnode), len(jove), n_jw))

# ---- the pin reference, trimmed to what the diagram needs ---------------
pins = {}
for t, b in BP.items():
    ins = [p["name"] for p in b["params"] if p["section"] == "INPUTS" and p["con"]]
    outs = [p["name"] for p in b["params"] if p["section"] == "OUTPUTS" and p["con"]]
    desc = {p["name"]: p["desc"] for p in b["params"] if p["desc"]}
    sect = {p["name"]: p["section"][0] for p in b["params"]}      # I / O / D
    pins[t] = {"t": b["title"], "i": ins, "o": outs, "d": desc, "s": sect}

payload = {"nodes": nodes, "edges": elist, "pins": pins}
js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf8")
gz = gzip.compress(js, 9)
enc = base64.b64encode(gz).decode("ascii")
open(OUT, "w", encoding="utf8").write('window.FOX_GRAPH_B64="%s";\n' % enc)

print("nodes %d, edges %d, pin tables %d" % (len(nodes), len(elist), len(pins)))
print("json %.1f MB -> gzip %.1f MB -> graph.js %.1f MB  (%.1fs)"
      % (len(js) / 1e6, len(gz) / 1e6, os.path.getsize(OUT) / 1e6, time.time() - t0))
