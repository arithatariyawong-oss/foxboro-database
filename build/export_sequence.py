# -*- coding: utf-8 -*-
"""Build sequence.js -- the HLBL sequence sources and the wiring hidden inside
them, for the Sequence View popup.

934 IND (independent sequence) blocks run in this plant, and every one of them
is a hole in the signal map. A sequence block's parameter record is all zeros
(see 39FCP003_SQ:39ACP301 in 39CP05.txt) because a sequence does not *pull*
values through configured input references the way a PID does -- it PUSHES,
in code:

    ID := :39FCP003_SQ:39BATCH3.II0005;      { a read  -> an input reference }
    :39FCP003_SQ:39ACP302.ACTIVE := TRUE;    { a write -> an output reference }

so `export_graph.py`, which only ever sees parameter values, cannot know any
of it. Everything a sequence is wired to lives in `00 RAW DATABASE/S/S/*.s`
and nowhere else. This reads those 779 sources and rebuilds the two panes ICC
shows beside the block's properties (03 WEB/13.png).

Three inputs meet here:

  * `00 RAW DATABASE/S/S/*.s` -- the HLBL source. One file per sequence, named
    for the BLOCK, so a source deployed into several compounds (BOSS_1/BOSS_1A/
    ... reuse the same 24 NR_* programs) is one file serving many instances.
  * `00 RAW DATABASE/*.txt` -- the SaveAll dumps, read instead of data.js
    because the dump is the only place the parameters stand in their true
    record order. That order is what ICC's Block Properties pane prints, and
    data.js's column list is a merge across all 1,202 columns of every block
    type, which is a different order (13.png lists MA/RSTMA/ACTIVE where
    data.js has HSCO1/LSCO1/DELTO1).
  * `graph.js` -- so a sequence block that is ALSO referenced the ordinary way
    (59 of them have a BI0007 holding a real reference) shows those rows in
    the same two panes, already resolved against the right CP.

Direction, and why both panes can hold the same neighbour: a write from my
SEQ is an edge (me.SEQ -> them.PARAM); a read is (them.PARAM -> me.SEQ). A
main sequence typically does

    :C:39ACP301.ACTIVE := TRUE;                        { writes my ACTIVE }
    WAIT UNTIL ( :C:39ACP301.ACTIVE = FALSE ) AND ...  { then reads it back }

which is a genuine edge each way, and is exactly why 39MAINA/39MAINB/
39FC009TO211 appear in BOTH panes of 13.png. Do not "fix" that.

`--check` re-derives 39FCP003_SQ:39ACP301 and asserts the 4 input and 5 output
rows of 13.png, which is the regression case for the whole file.
"""
import base64
import gzip
import json
import os
import re
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
ROOT = os.path.dirname(WEB)
RAW = os.path.join(ROOT, "00 RAW DATABASE")
SDIR = os.path.join(RAW, "S", "S")
GRAPH = os.path.join(WEB, "graph.js")
OUT = os.path.join(WEB, "sequence.js")

t0 = time.time()


# ======================================================================= #
# 1. THE HLBL LEXER                                                       #
# ======================================================================= #
# Comments are { ... } and do NOT nest -- the first } closes, so the stray
# open brace in 39ACP301.s (a subroutine someone commented out and left
# unbalanced) ends at the next } and does not swallow the rest of the file.
# Strings are "..." with "" for a literal quote, which the character table in
# 39ACP*.s leans on: `ELSEIF str_x = """" THEN` is testing for one quote mark.
#
# Blanking rather than deleting: comment and string bodies become spaces of
# the SAME length, so every line number and column in the masked text still
# points at the same place in the file the user is reading on screen.

def mask(text):
    """-> code-only copy of `text`, comments and string bodies spaced out."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "{":
            j = text.find("}", i + 1)
            j = n if j < 0 else j + 1
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif c == '"':
            j = i + 1
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    j += 1
                    break
                if text[j] == "\n":
                    break            # an unterminated string dies at the line
                j += 1
            for k in range(i, min(j, n)):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        else:
            i += 1
    return "".join(out)


# A reference is [:[COMPOUND]:]BLOCK.PARAM. The plant writes all four forms:
#   :C101:01HS111.TOGGLE   fully qualified                         4,265
#   ::01HC111.RBIAS        my own compound                           281
#   :01RTOTIM1.TIMR2       my own compound, one colon                 81
#   :39FC00'X'_AS:39ACP'Y'.IIN   a name built at run time          1,267
# The quoted pieces are variables spliced into the name; ICC cannot resolve
# those either, so they are collected separately and shown as-is.
REF = re.compile(r"""
    (?<![A-Za-z0-9_.])
    : (?: (?P<comp>[A-Za-z0-9_']*) : )?
      (?P<blk>[A-Za-z0-9_']+)
    \. (?P<par>[A-Za-z0-9_']+)
""", re.X)

# what may sit between a reference and the := that makes it a write
LHS_TAIL = re.compile(r"\s*(?:\([^()]*\)\s*)?:=")

DEFINE = re.compile(r"^\s*#define\s+(\S+)\s+(.*?)\s*$", re.M)
INCLUDE = re.compile(r"^\s*#include\s+(.*?)\s*$", re.M)
LABEL = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
                   r"((?:BI|BO|BA|RI|RO|RA|II|IO|IA|SN)\d{2,4})\s*;", re.M)
SECTION = re.compile(r"^[ \t]*(INDEPENDENT_SEQUENCE|SEQUENCE|CONSTANTS|VARIABLES|"
                     r"USER_LABELS|STATEMENTS|SUBROUTINE|ENDSUBROUTINE|"
                     r"BLOCK_EXCEPTION|ENDEXCEPTION|ENDSEQUENCE)\b", re.M)


def parse_source(text):
    """-> (refs, labels, defines, includes, sections)

    refs is [(line, is_write, comp, blk, par, literal)] with `comp` '' when the
    source said "my own compound" and None never; a name carrying a ' is left
    for the caller to mark unresolvable.
    """
    code = mask(text)
    defines = dict(DEFINE.findall(code))
    includes = INCLUDE.findall(code)
    labels = {p: lab for lab, p in LABEL.findall(code)}
    sections = sorted({m.group(1) for m in SECTION.finditer(code)})

    # A macro stands in for a reference far more often than not (173 files use
    # #define, and CBPHL := x is a write to ::01LRCA065.MEASHL), so the scan
    # runs over a macro-expanded copy of each LINE -- per line, because the
    # line number has to survive to the source listing on screen.
    macro = None
    if defines:
        macro = re.compile(r"(?<![A-Za-z0-9_])(%s)(?![A-Za-z0-9_])"
                           % "|".join(re.escape(k) for k in
                                      sorted(defines, key=len, reverse=True)))

    refs = []
    for ln, line in enumerate(code.split("\n"), 1):
        if ":" not in line and not (macro and macro.search(line)):
            continue
        # `#define CBPHL ::01LRCA065.MEASHL` names a reference but does not
        # USE it -- the uses are the CBPHL:= lines further down. Scoring the
        # directive itself as a read invented three input references on
        # V101:01LY065 alone, one per macro, every one of them a parameter
        # the sequence only ever writes. Flagged rather than dropped, so the
        # source listing can still link the name where it is declared.
        decl = line.lstrip().startswith("#")
        if macro and not decl:
            for _ in range(4):                    # macros of macros do occur
                new = macro.sub(lambda m: defines[m.group(1)], line)
                if new == line:
                    break
                line = new
        for m in REF.finditer(line):
            comp = m.group("comp") or ""
            blk, par = m.group("blk"), m.group("par")
            # 0 read, 1 write, 2 named by a #define and used nowhere here
            kind = 2 if decl else (1 if LHS_TAIL.match(line, m.end()) else 0)
            refs.append((ln, kind, comp, blk, par, m.group(0)))
    return refs, labels, defines, includes, sections


# ======================================================================= #
# 2. THE SOURCES                                                          #
# ======================================================================= #
srcs = []                     # [filename, text, sections, includes]
src_of = {}                   # BLOCK (upper) -> index into srcs
parsed = {}                   # index -> (refs, labels, defines)

for fn in sorted(os.listdir(SDIR)):
    path = os.path.join(SDIR, fn)
    if not os.path.isfile(path):
        continue
    text = open(path, encoding="utf8", errors="replace").read().replace("\r\n", "\n")
    refs, labels, defines, includes, sections = parse_source(text)
    stem = fn.split(".")[0].upper()
    idx = len(srcs)
    srcs.append([fn, text, sections, includes])
    parsed[idx] = (refs, labels, defines)
    src_of.setdefault(stem, idx)

n_refs = sum(len(parsed[i][0]) for i in parsed)
print("sources %d, %.2f MB, references found %d  (%.1fs)"
      % (len(srcs), sum(len(s[1]) for s in srcs) / 1e6, n_refs, time.time() - t0))


# ======================================================================= #
# 3. THE BLOCK RECORDS, IN THEIR TRUE ORDER                               #
# ======================================================================= #
# One pass over the SaveAll dumps. Only IND records are kept in full; every
# other NAME= line is kept as a bare (compound:block -> cp) so an unqualified
# reference can be resolved against the CP it was written in.
blocks = []                   # [name, cp, descrp, props]
row_of = {}                   # "COMP:BLK" -> index into blocks
cp_of = {}                    # "COMP:BLK" -> cp   (every block in the plant)
short = defaultdict(list)     # "BLK"      -> ["COMP:BLK", ...]

# The dumps come in two dialects and both are in this folder. The 87 CP files
# write `CP=39CP05` / `NAME=COMP:BLK` / four-space `    TYPE=IND` / `END`; the
# three CPTCI files write `NAME   = COMP:BLK` / two-space `  TYPE   = IND`
# with no CP line and no END, a record simply running to the next NAME. Parsing
# only the first dialect silently loses 93 sequence blocks -- every one on
# CPTCI1/2/3, which is where the RTO and AMADAS sequences live.
CP_LINE = re.compile(r"^CP\s*=\s*(.*)$")
NAME_LINE = re.compile(r"^NAME\s*=\s*(.*)$")
PROP_LINE = re.compile(r"^[ \t]+([A-Za-z_][A-Za-z0-9_]*)\s*=\s?(.*)$")

n_rec = 0
for fn in sorted(os.listdir(RAW)):
    if not fn.lower().endswith(".txt"):
        continue
    cp = os.path.splitext(fn)[0]          # the CPTCI dialect names it nowhere else
    name, props, typ = None, [], ""

    def close():
        global name
        if name and typ == "IND" and name not in row_of:
            row_of[name] = len(blocks)
            blocks.append([name, cp, "", props])
        name = None

    with open(os.path.join(RAW, fn), encoding="utf8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            m = CP_LINE.match(line)
            if m:
                cp = m.group(1).strip() or cp
                continue
            m = NAME_LINE.match(line)
            if m:
                close()
                name, props, typ = m.group(1).strip(), [], ""
                n_rec += 1
                if ":" in name:
                    cp_of[name] = cp
                    short[name.split(":", 1)[1].upper()].append(name)
                continue
            if line.startswith("END"):
                close()
                continue
            m = PROP_LINE.match(line) if name is not None else None
            if m:
                props.append([m.group(1), m.group(2).strip()])
                if m.group(1) == "TYPE":
                    typ = m.group(2).strip()
    close()

for b in blocks:
    for k, v in b[3]:
        if k == "DESCRP":
            b[2] = v
            break

print("dump records %d, IND blocks %d  (%.1fs)"
      % (n_rec, len(blocks), time.time() - t0))


def resolve(comp, blk, home_comp, home_cp):
    """A reference to a full name, or None if nothing in the plant matches.

    Precedence is the same as export_graph.py's and for the same reason: the
    plant reuses tag names across CPs (V501:05FRC065 and V501_N7:05FRC065),
    so an unqualified name resolves to its own compound first, then to a
    block in its own CP, and only then to anything at all.
    """
    if comp:
        full = "%s:%s" % (comp, blk)
        return full if full in cp_of else None
    mine = "%s:%s" % (home_comp, blk)
    if mine in cp_of:
        return mine
    cands = short.get(blk.upper())
    if not cands:
        return None
    same = [c for c in cands if cp_of.get(c) == home_cp]
    return (same or cands)[0]


# ======================================================================= #
# 4. THE EDGES                                                            #
# ======================================================================= #
# ins[name]  = [(src_name, src_param, my_param, origin)]
# outs[name] = [(my_param, dst_name, dst_param, origin)]
# origin 0 = read out of the sequence source, 1 = an ordinary parameter
# reference already resolved by export_graph.py.
ins = defaultdict(list)
outs = defaultdict(list)
seen = set()


def wire(sname, sparam, dname, dparam, origin):
    key = (sname, sparam, dname, dparam)
    if key in seen:
        return
    seen.add(key)
    ins[dname].append([sname, sparam, dparam, origin])
    outs[sname].append([sparam, dname, dparam, origin])


# Every reference the source names, resolved AGAINST THIS INSTANCE and kept
# with the line it sits on -- that is what lets the source listing on screen
# turn each one into a link, and it is also where the two panes' rows come
# from. Resolution is per instance and not per file: one .s can be deployed
# into several compounds (the 24 NR_* programs run in BOSS_1, BOSS_1A,
# BOSS_1O and BOSS_1S), and "::SOMEBLOCK.PARAM" means a different block in
# each of them.
site_refs = {}                # block name -> [[line, write, literal, full, param]]
n_dyn = n_lost = 0

for name, cp, descrp, props in blocks:
    comp, blk = name.split(":", 1)
    si = src_of.get(blk.upper())
    rows = []
    for ln, kind, rcomp, rblk, rpar, lit in (parsed[si][0] if si is not None else []):
        full = "" if "'" in lit else (resolve(rcomp, rblk, comp, cp) or "")
        rows.append([ln, kind, lit, full, rpar])
        if not full:
            if "'" in lit:
                n_dyn += 1          # a name spliced together at run time
            else:
                n_lost += 1         # no block of that name anywhere in the dumps
            continue
        if full == name or kind == 2:
            # A sequence reading or writing its OWN parameter is not a wire;
            # it is just the block's own I/O, and ICC does not list it. Nor is
            # a #define that only gives the reference a shorter name.
            continue
        if kind == 1:
            wire(name, "SEQ", full, rpar, 0)
        else:
            wire(full, rpar, name, "SEQ", 0)
    site_refs[name] = rows

print("sequence edges %d  (dynamic names %d, unresolved %d)  (%.1fs)"
      % (len(seen), n_dyn, n_lost, time.time() - t0))


# ---- the ordinary parameter references, straight out of graph.js ---------
def load(path):
    raw = open(path, encoding="utf8").read()
    b64 = raw.split('"', 1)[1].rsplit('"', 1)[0]
    return json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf8"))


g = load(GRAPH)
gname = [n[0] for n in g["nodes"]]
n_param = 0
for e in g["edges"]:
    s, sp, t, tp = gname[e[0]], e[1], gname[e[2]], e[3]
    qual = e[4] if len(e) > 4 else ""
    if s not in row_of and t not in row_of:
        continue                     # neither end is a sequence block
    wire(s, sp + ("." + qual if qual else ""), t, tp, 1)
    n_param += 1
print("parameter edges touching a sequence: %d  (%.1fs)" % (n_param, time.time() - t0))


# ======================================================================= #
# 5. SHIP IT                                                              #
# ======================================================================= #
def sort_in(r):
    return (r[2], r[0], r[1])          # by my parameter, then by the neighbour


def sort_out(r):
    return (r[0], r[1], r[2])


out_blocks = []
for name, cp, descrp, props in blocks:
    comp, blk = name.split(":", 1)
    si = src_of.get(blk.upper())
    labels = parsed[si][1] if si is not None else {}
    out_blocks.append([
        name,                                       # 0 COMPOUND:BLOCK
        cp,                                         # 1 CP
        descrp,                                     # 2 DESCRP
        props,                                      # 3 [[param, value]] dump order
        si if si is not None else -1,               # 4 index into srcs
        sorted(ins[name], key=sort_in),             # 5 input references
        sorted(outs[name], key=sort_out),           # 6 output references
        labels,                                     # 7 {param: user label}
        site_refs.get(name, []),                    # 8 [[line, kind, literal, full, param]]
    ])

# sources with no block of that name -- 10 library/backup files. Kept so the
# page can still show them rather than pretending the folder holds 769 files.
have = {src_of.get(b[0].split(":", 1)[1].upper()) for b in blocks}
orphans = [i for i in range(len(srcs)) if i not in have]

payload = {
    "blocks": out_blocks,
    "srcs": [[s[0], s[1], s[2], s[3]] for s in srcs],
    "orphans": orphans,
}
js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf8")
gz = gzip.compress(js, 9)
open(OUT, "w", encoding="utf8").write(
    'window.FOX_SEQ_B64="%s";\n' % base64.b64encode(gz).decode("ascii"))

with_src = sum(1 for b in out_blocks if b[4] >= 0)
print("blocks %d (%d with source, %d orphan sources)"
      % (len(out_blocks), with_src, len(orphans)))
print("json %.2f MB -> gzip %.2f MB -> sequence.js %.2f MB  (%.1fs)"
      % (len(js) / 1e6, len(gz) / 1e6, os.path.getsize(OUT) / 1e6, time.time() - t0))


# ======================================================================= #
# 6. THE REGRESSION CASE                                                  #
# ======================================================================= #
# 03 WEB/13.png is ICC's own view of this block. If the two panes below stop
# matching it, the parser has drifted -- fix the parser, not the assertion.
if "--check" in sys.argv:
    NAME = "39FCP003_SQ:39ACP301"
    b = out_blocks[row_of[NAME]]
    got_in = {("%s.%s" % (r[0].split(":", 1)[1], r[1]), r[2]) for r in b[5]}
    got_out = {(r[0], "%s.%s" % (r[1].split(":", 1)[1], r[2])) for r in b[6]}
    want_in = {("39FC009TO211.SEQ", "ACTIVE"), ("39MAINB.SEQ", "ACTIVE"),
               ("39MAINA.SEQ", "ACTIVE"), ("39BATCH3.II0005", "SEQ")}
    want_out = {("ACTIVE", "39FC009TO211.SEQ"), ("ACTIVE", "39MAINB.SEQ"),
                ("ACTIVE", "39MAINA.SEQ"), ("SEQ", "39ACP303.ACTIVE"),
                ("SEQ", "39ACP302.ACTIVE")}
    bad = 0
    for what, got, want in (("input", got_in, want_in), ("output", got_out, want_out)):
        if got != want:
            bad = 1
            print("  FAIL %s refs\n    missing %s\n    extra   %s"
                  % (what, sorted(want - got), sorted(got - want)))
        else:
            print("  ok  %s references match 13.png (%d rows)" % (what, len(got)))
    p = dict(b[3])
    for k, v in (("TYPE", "IND"), ("DESCRP", "ACTUAL PRODUCT CHAR 1-4"),
                 ("LOOPID", "ASCII_SQ_2"), ("BPCSTM", "100")):
        if p.get(k) != v:
            bad = 1
            print("  FAIL property %s = %r, expected %r" % (k, p.get(k), v))
    if [k for k, _ in b[3][:8]] != ["TYPE", "DESCRP", "PERIOD", "PHASE",
                                    "LOOPID", "MA", "RSTMA", "ACTIVE"]:
        bad = 1
        print("  FAIL property order: %s" % [k for k, _ in b[3][:8]])
    else:
        print("  ok  properties are in 13.png's order")
    sys.exit(bad)
