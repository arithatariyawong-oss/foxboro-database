# -*- coding: utf-8 -*-
"""Extract the block-parameter tables from B0193AX (Integrated Control Block
Descriptions, Vol 1-3) into one JSON.

That manual is what says whether a parameter is an INPUT or an OUTPUT and
whether it is connectable at all -- which is what decides whether a pin
belongs on the left or the right edge of a block in a wiring diagram, and in
what order. The tag database knows which pins are *wired*; only the manual
knows what a pin IS.

Each table row is laid out down the page as
    NAME / description / type / accessibility / default / units-range
so the accessibility token (con|no-con)/(set|no-set) is the anchor: it is the
one field with a fixed vocabulary. Walk back from it for the type, then the
description, then the NAME; walk forward for default and range. Rows wrap and
the name+description sometimes share a line, so anchoring beats slicing.

Two things the layout does that are easy to get wrong:

  * A table runs over many pages and every continuation page repeats the
    header as "Table 93-1. PID Block Parameters (Continued)". The
    INPUTS/OUTPUTS/DATA STORES headings appear ONLY on the first page, so the
    section has to survive those repeats -- resetting it on each header match
    silently drops every row after page one (PID came out with 1 connectable
    input instead of 27).
  * Ranges are written as one row: "HSCI1-HSCI2", "RI01-RI16". Those are
    expanded so the pin list is complete.

Writes block_params.json:
  { "PID": {"title": ..., "params": [
      {name, desc, type, acc, con, set, section, default, range} ]}, ... }
"""
import json, re, sys
from pathlib import Path

import pymupdf

MANUAL = Path(r"C:\Users\SESA407984\Desktop\FOXBORO\04 MANUAL\k0173wt_g\V83\b0193")
VOLS = ["b0193ax1_u.pdf", "b0193ax2_u.pdf", "b0193ax3_u.pdf"]
OUT = Path(__file__).resolve().parent.parent / "block_params.json"

ACC = re.compile(r"^(no-con|con)/(no-set|set)$")
TABLE = re.compile(r"^Table\s+[\d.]+-\d+\.\s+(.+?)\s+Block Parameters", re.I)
HEADING = re.compile(r"^\d+\.\s+([A-Z][A-Z0-9_]{1,11})\s+[\u2013\u2014-]\s+(.+?)\s*$")
SECTIONS = {"INPUTS": "INPUTS", "INPUT": "INPUTS",
            "OUTPUTS": "OUTPUTS", "OUTPUT": "OUTPUTS",
            "DATA STORES": "DATA STORES", "DATA STORE": "DATA STORES"}
NAME_OK = re.compile(r"^[A-Z][A-Z0-9_]*(-[A-Z0-9_]+)?$")
HYPHEN = re.compile(r"^([A-Z_]+?)(\d+)-([A-Z_]+?)(\d+)$")
# the manual writes most ranges in words: "RI01 to RI08", "BI01 to BI16"
TO = re.compile(r"^to\s+([A-Z][A-Z0-9_]*)\b")
SPLIT = re.compile(r"^([A-Z_]+?)(\d+)$")


def _span(p1, a, p2, b):
    if p1 != p2:
        return None
    a_i, b_i = int(a), int(b)
    if not (0 <= b_i - a_i <= 64):
        return None
    return ["%s%0*d" % (p1, len(a), k) for k in range(a_i, b_i + 1)]


def expand(name):
    """"HSCI1-HSCI2" -> [HSCI1, HSCI2];  "RI01-RI16" -> [RI01 .. RI16]."""
    m = HYPHEN.match(name)
    if not m:
        return [name]
    return _span(*m.groups()) or [name]


def expand_to(first, second):
    """The "RI01 to RI08" form -- how B0193AX actually writes its ranges."""
    m1, m2 = SPLIT.match(first), SPLIT.match(second)
    if not (m1 and m2):
        return [first, second]
    return _span(m1.group(1), m1.group(2), m2.group(1), m2.group(2)) or [first, second]


blocks, titles = {}, {}

for vol in VOLS:
    path = MANUAL / vol
    if not path.exists():
        sys.exit("missing manual: %s" % path)
    doc = pymupdf.open(path)
    cur, section = None, None
    for pno in range(doc.page_count):
        lines = [l.strip() for l in doc[pno].get_text().split("\n")]
        for i, ln in enumerate(lines):
            if not ln:
                continue
            m = HEADING.match(ln)
            if m:
                titles[m.group(1)] = m.group(2)
                continue
            m = TABLE.match(ln)
            if m:
                t = m.group(1).strip().upper()
                if t != cur:           # a repeated "(Continued)" header must
                    cur, section = t, None   # not clear the current section
                    blocks.setdefault(cur, {"title": "", "params": []})
                continue
            sec = SECTIONS.get(ln.upper())
            if sec:
                section = sec
                continue
            m = ACC.match(ln)
            if not m or cur is None or section is None:
                continue
            con, st = m.group(1) == "con", m.group(2) == "set"
            typ = lines[i - 1] if i >= 1 else ""
            name, desc, names = "", "", []
            for j in range(i - 2, max(-1, i - 8), -1):
                cand = lines[j]
                if not cand:
                    continue
                first = cand.split()[0]
                if NAME_OK.match(first) and not ACC.match(cand):
                    rest = cand[len(first):].strip()
                    mt = TO.match(rest)
                    if mt:
                        names = expand_to(first, mt.group(1))
                        rest = rest[mt.end():].strip()
                    else:
                        names = expand(first)
                    name = first
                    desc = " ".join([rest] + lines[j + 1:i - 1]).strip()
                    break
            if not name:
                continue
            nxt = [x for x in lines[i + 1:i + 3] if x]
            for nm in names:
                blocks[cur]["params"].append({
                    "name": nm, "desc": desc, "type": typ, "acc": ln,
                    "con": con, "set": st, "section": section,
                    "default": nxt[0] if nxt else "",
                    "range": nxt[1] if len(nxt) > 1 else "",
                })
    doc.close()
    print("%-16s -> %d block types so far" % (vol, len(blocks)))

for t, b in blocks.items():
    seen, keep = set(), []
    for p in b["params"]:
        if p["name"] in seen:          # the header repeats; first win
            continue
        seen.add(p["name"])
        keep.append(p)
    b["params"] = keep
    b["title"] = titles.get(t, "")

blocks = {t: b for t, b in blocks.items() if b["params"]}
OUT.write_text(json.dumps(blocks, separators=(",", ":"), ensure_ascii=False), encoding="utf8")

# ---- the slim reference the pages actually read -------------------------
# A page opened over file:// cannot fetch() a .json, so the lookup ships as
# a script that assigns a global -- the same gzip+base64 trick data.js and
# graph.js use. Only the title, each parameter's description and its section
# are kept; that is everything a Properties panel needs, at a fifth of the
# size of the full table.
import base64, gzip
slim = {t: {"t": b["title"],
            "d": {p["name"]: p["desc"] for p in b["params"] if p["desc"]},
            "s": {p["name"]: p["section"][0] for p in b["params"]}}
        for t, b in blocks.items()}
raw = json.dumps(slim, separators=(",", ":"), ensure_ascii=False).encode("utf8")
enc = base64.b64encode(gzip.compress(raw, 9)).decode("ascii")
js = OUT.parent / "params.js"
js.write_text('window.FOX_PARAMS_B64="%s";' % enc + chr(10), encoding="utf8")
print("params.js: %.0f KB json -> %.0f KB" % (len(raw) / 1024, js.stat().st_size / 1024))

n_par = sum(len(b["params"]) for b in blocks.values())
n_con = sum(1 for b in blocks.values() for p in b["params"] if p["con"])
print("\n%d block types, %d parameters (%d connectable) -> %s (%.0f KB)"
      % (len(blocks), n_par, n_con, OUT.name, OUT.stat().st_size / 1024))
