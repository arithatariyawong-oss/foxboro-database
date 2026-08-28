# -*- coding: utf-8 -*-
"""Export FOX DATABASE.xlsx -> compact gzip+base64 JS payload for the web dashboard."""
import zipfile, json, gzip, base64, time, os, sys
from xml.etree.ElementTree import iterparse

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
# Resolved from this file's own location so a clone builds anywhere:
#   build/  ->  the web folder  ->  the folder holding FOX DATABASE.xlsx
# Point it elsewhere with:  python build/export_data.py "<path to .xlsx>"
HERE = os.path.dirname(os.path.abspath(__file__))
WEB  = os.path.dirname(HERE)
ROOT = os.path.dirname(WEB)
XLSX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "FOX DATABASE.xlsx")
OUT  = os.path.join(WEB, "data.js")

def col_index(ref):
    n = 0
    for ch in ref:
        if ch.isalpha():
            n = n * 26 + (ord(ch.upper()) - 64)
        else:
            break
    return n - 1

def read_shared_strings(z):
    out = []
    with z.open("xl/sharedStrings.xml") as f:
        for _, el in iterparse(f, ("end",)):
            if el.tag == NS + "si":
                out.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
    return out

def iter_sheet(z, part, ss):
    """yield (row_number, {col_index: text})"""
    with z.open(part) as f:
        for _, el in iterparse(f, ("end",)):
            if el.tag != NS + "row":
                continue
            vals = {}
            for c in el:
                v = c.find(NS + "v")
                if v is None or v.text is None:
                    continue
                txt = ss[int(v.text)] if c.get("t") == "s" else v.text
                if txt is None or txt == "":
                    continue
                vals[col_index(c.get("r"))] = txt
            yield int(el.get("r")), vals
            el.clear()

t0 = time.time()
z = zipfile.ZipFile(XLSX)
ss = read_shared_strings(z)
print("sharedStrings %d  (%.1fs)" % (len(ss), time.time() - t0))

# ---- CP -> AREA lookup (sheet44 = "AREA") -------------------------------
area_of = {}
for rn, vals in iter_sheet(z, "xl/worksheets/sheet44.xml", ss):
    if rn == 1:
        continue
    cp = (vals.get(0) or "").strip()
    ar = (vals.get(1) or "").strip()
    if cp:
        area_of[cp] = ar
print("AREA map: %d CPs" % len(area_of))

# ---- main table (sheet1 = "FOX TAG DATABASE") ---------------------------
headers = None
NC = 0
# per column: dict value -> code, list of codes, list of row ids
dicts, codes, rows_of = [], [], []
nrows = 0
area_col = None
# Power Query left the STRING blocks of 03CP09 / 31CP01 / 31CP02 in generic
# "Column1..Column5" instead of the named columns, which is why the Power BI
# report only ever counted 75,940 of the 77,013 rows. Fold them back into the
# real columns rather than dropping them.
STRAY = {}       # generic column index -> real column index
stray_val = None # "Column5" -> its own VALUE column
n_realigned = 0
n_dropped = 0
# Excel stored the FBM/device ids as numbers, so "010404" came back as
# "10404". Same fix as CONVERT 5 TO 6 DIGID.txt, applied to every column
# that holds a device id.
PAD6_NAMES = ("IOM_ID", "IOMIDR", "DEV_ID", "PARENT")
PAD6 = set()
n_padded = 0

for rn, vals in iter_sheet(z, "xl/worksheets/sheet1.xml", ss):
    if headers is None:
        NC = max(vals) + 1
        headers = [(vals.get(i) or "").strip() for i in range(NC)]
        by_name = {h: i for i, h in enumerate(headers)}
        for gen, real in (("Column1", "CP NAME"), ("Column2", "NAME"),
                          ("Column3", "TYPE"), ("Column4", "DESCRP")):
            if gen in by_name and real in by_name:
                STRAY[by_name[gen]] = by_name[real]
        stray_val = by_name.get("Column5")
        if stray_val is not None:
            headers[stray_val] = "VALUE"       # the STRING blocks' payload
        PAD6 = {i for i, h in enumerate(headers) if h in PAD6_NAMES}
        dicts   = [dict() for _ in range(NC + 1)]
        codes   = [[] for _ in range(NC + 1)]
        rows_of = [[] for _ in range(NC + 1)]
        area_col = NC            # synthetic AREA column appended at the end
        headers.append("AREA")
        continue
    if not vals:
        continue
    # realign the stray rows; drop the header rows repeated inside the data
    if not vals.get(by_name["TYPE"]) and STRAY:
        moved = {}
        for gen, real in STRAY.items():
            if gen in vals:
                moved[real] = vals.pop(gen)
        if moved:
            if moved.get(by_name["CP NAME"]) == "CP NAME":
                n_dropped += 1
                continue
            vals.update(moved)
            n_realigned += 1
    r = nrows
    nrows += 1
    for ci, txt in vals.items():
        if ci >= NC:
            continue
        if ci in PAD6 and len(txt) < 6 and txt.isdigit():
            txt = txt.zfill(6)
            n_padded += 1
        d = dicts[ci]
        c = d.get(txt)
        if c is None:
            c = len(d)
            d[txt] = c
        codes[ci].append(c)
        rows_of[ci].append(r)
    # synthetic AREA
    cp = vals.get(1)
    ar = area_of.get((cp or "").strip(), "") if cp else ""
    if ar:
        d = dicts[area_col]
        c = d.get(ar)
        if c is None:
            c = len(d)
            d[ar] = c
        codes[area_col].append(c)
        rows_of[area_col].append(r)

print("rows %d  cols %d  | realigned %d stray, dropped %d headers, padded %d device ids  (%.1fs)"
      % (nrows, NC + 1, n_realigned, n_dropped, n_padded, time.time() - t0))

# ---- build payload ------------------------------------------------------
cols_out = []
for i in range(NC + 1):
    rws = rows_of[i]
    if not rws:
        cols_out.append(0)              # empty column marker
        continue
    vocab = [None] * len(dicts[i])
    for k, v in dicts[i].items():
        vocab[v] = k
    if len(rws) == nrows:               # dense: row ids are implicit
        cols_out.append({"d": vocab, "v": codes[i]})
    else:                              # sparse: delta-encoded row ids
        delta, prev = [], 0
        for r in rws:
            delta.append(r - prev)
            prev = r
        cols_out.append({"d": vocab, "v": codes[i], "r": delta})

payload = {"n": nrows, "h": headers, "c": cols_out}
raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf8")
gz  = gzip.compress(raw, 9)
b64 = base64.b64encode(gz).decode("ascii")

with open(OUT, "w", encoding="utf8") as f:
    f.write("window.FOX_DATA_B64=\"%s\";\n" % b64)

print("json %.1f MB -> gzip %.1f MB -> data.js %.1f MB   (%.1fs)"
      % (len(raw)/1e6, len(gz)/1e6, os.path.getsize(OUT)/1e6, time.time() - t0))
