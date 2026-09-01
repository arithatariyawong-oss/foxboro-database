# -*- coding: utf-8 -*-
"""Build the Modbus / serial-gateway communication list and write modbus.js.

One source: data.js -- the tag database.

  * A serial gateway is an FBM230/231/232/233. Its module ECB (ECB200 or
    ECB202) carries the letterbug in DEV_ID and 230/231/232/233 in HWTYPE.
    Every serial device on it is an ECB201 child that names the gateway
    letterbug in PARENT, the station address (RTU) or the IP pair (TCP) in
    DVNAME, the protocol options in DVOPTS ("MODBUS+@20+H+TO"), and the
    serial port in PORTNO.

  * Each Modbus point is an I/O block bound to the device (or, for a few
    diagnostics, straight to the gateway) by IOM_ID / IOMIDR:
        RIN  IIN  BIN  PAKIN  STRIN   -> the CP reads the device   (IN)
        ROUT IOUT BOUT PAKOUT         -> the CP writes the device  (OUT)
    PNT_NO is the Modbus register: "45003:U2", "400001:S4:W3", "11134",
    "00038". The leading digit is the register bank in the standard Modbus
    convention -- 0 coil (RW), 1 discrete input (RO), 3 input register (RO),
    4 holding register (RW). PAKIN/PAKOUT map a whole contact group and carry
    no register here (the mapping lives in the FBM's own config file); they
    are still real I/O and are kept with an empty register and bank -1.

  * "$"-prefixed PNT_NO ($M_OVERSCANS, $M_LAST_ERR_MSG, ...) are the gateway's
    own diagnostic pseudo-registers, not process I/O -- dropped.

Engineering range comes off the block: EI1/LSCI1/HSCI1 for an input,
EO1/LSCO1/HSCO1 for an output; blank for the boolean blocks.

Output modbus.js mirrors data.js / systems.js: gzip + base64 in a global,
inflated by the page with DecompressionStream, because a page opened from
file:// cannot fetch() a .json.
"""
import base64, gzip, json, os, re, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
DATA = os.path.join(WEB, "data.js")
OUT = os.path.join(WEB, "modbus.js")

t0 = time.time()

raw = open(DATA, encoding="utf8").read()
b64 = raw.split('"', 1)[1].rsplit('"', 1)[0]
d = json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf8"))
N, H, C = d["n"], d["h"], d["c"]
IDX = {h: i for i, h in enumerate(H) if h}


def col(name):
    a = [""] * N
    sp = C[IDX[name]]
    if not isinstance(sp, dict):
        return a
    v, dd = sp["v"], sp["d"]
    if "r" in sp:
        row = 0
        for k, dl in enumerate(sp["r"]):
            row += dl
            a[row] = dd[v[k]]
    else:
        for k, cc in enumerate(v):
            a[k] = dd[cc]
    return a


TY = col("TYPE"); CP = col("CP NAME"); NM = col("NAME"); DS = col("DESCRP")
DEV = col("DEV_ID"); HW = col("HWTYPE"); IOM = col("IOM_ID"); IOMR = col("IOMIDR")
PNT = col("PNT_NO"); PAR = col("PARENT"); DVN = col("DVNAME"); DVO = col("DVOPTS")
PRT = col("PORTNO"); AR = col("AREA")
EI1 = col("EI1"); LSCI1 = col("LSCI1"); HSCI1 = col("HSCI1")
EO1 = col("EO1"); LSCO1 = col("LSCO1"); HSCO1 = col("HSCO1")
print("data.js %d rows  (%.1fs)" % (N, time.time() - t0))

COMM = {"230": "FBM230", "231": "FBM231", "232": "FBM232", "233": "FBM233"}
IN_TY = {"RIN", "IIN", "BIN", "PAKIN", "STRIN"}
OUT_TY = {"ROUT", "IOUT", "BOUT", "PAKOUT"}

# ---- gateway modules and their serial devices --------------------------
gw_row = {}                                   # (cp, letterbug) -> row
for r in range(N):
    if TY[r] in ("ECB200", "ECB202") and HW[r] in COMM:
        gw_row.setdefault((CP[r], DEV[r]), r)

dev_row = {}                                  # (cp, dev id) -> row
for r in range(N):
    if TY[r] == "ECB201" and HW[r] in COMM:
        dev_row.setdefault((CP[r], DEV[r]), r)


def parse_dvopts(s):
    """"MODBUS+@20+H+TO" -> ("MODBUS", "@20 H TO")."""
    s = (s or "").strip()
    if not s:
        return "", ""
    parts = [p for p in s.split("+") if p]
    return parts[0], " ".join(parts[1:])


def dev_addr(s):
    """DVNAME -> (kind, shown address).  digits = RTU station, else TCP."""
    s = (s or "").strip()
    if not s:
        return "", ""
    return ("RTU", s) if s.isdigit() else ("TCP", s)


# ---- index the points by binding target -------------------------------
bound = {}                                    # (cp, target dev) -> [rows]
for r in range(N):
    if TY[r] not in IN_TY and TY[r] not in OUT_TY:
        continue
    p = PNT[r].strip()
    if not p or p.startswith("$"):
        # PAKIN/PAKOUT legitimately carry no register; keep those, drop the
        # empty non-packed blocks and every diagnostic pseudo-register
        if not (TY[r] in ("PAKIN", "PAKOUT") and not p):
            continue
    for dv in (IOM[r], IOMR[r]):
        if not dv:
            continue
        key = (CP[r], dv)
        if key in dev_row or key in gw_row:
            bound.setdefault(key, []).append(r)
            break


def bank_of(reg):
    """Leading digit -> Modbus register bank; -1 when there is no register."""
    if not reg or not reg[0].isdigit():
        return -1
    lead = reg[0]
    return int(lead) if lead in ("0", "1", "3", "4") else -1


def split_pnt(p):
    """"45003:U2" -> ("45003", "U2");  "400001:S4:W3" -> ("400001", "S4 W3")."""
    p = p.strip()
    if not p:
        return "", ""
    bits = p.split(":")
    return bits[0], " ".join(bits[1:])


def rng(r, out):
    eu = (EO1[r] if out else EI1[r]).strip()
    lo = (LSCO1[r] if out else LSCI1[r]).strip()
    hi = (HSCO1[r] if out else HSCI1[r]).strip()
    if lo or hi:
        return eu, lo, hi
    return eu, "", ""


# ---- assemble ---------------------------------------------------------
cps = sorted({c for (c, _) in dev_row} | {c for (c, _) in gw_row})
cp_ix = {c: i for i, c in enumerate(cps)}

gws = []                                      # gateway modules
gw_ix = {}
for (c, lb), r in sorted(gw_row.items()):
    gw_ix[(c, lb)] = len(gws)
    gws.append({"c": cp_ix[c], "lb": lb, "md": COMM[HW[r]],
                "ds": DS[r].strip(), "ar": AR[r].strip()})

devs = []
dev_ix = {}
for (c, dv), r in sorted(dev_row.items()):
    proto, opt = parse_dvopts(DVO[r])
    kind, addr = dev_addr(DVN[r])
    g = gw_ix.get((c, PAR[r]))
    if g is None:                             # gateway module ECB not exported
        gw_ix[(c, PAR[r])] = g = len(gws)
        gws.append({"c": cp_ix[c], "lb": PAR[r] or "?", "md": COMM.get(HW[r], ""),
                    "ds": "", "ar": AR[r].strip()})
    dev_ix[(c, dv)] = len(devs)
    devs.append({"g": g, "nm": NM[r].split(":")[-1] or dv, "dv": dv,
                 "kind": kind, "addr": addr, "proto": proto or "MODBUS",
                 "opt": opt, "port": PRT[r].strip(), "ds": DS[r].strip(),
                 "in": 0, "out": 0})

# a gateway that only ever appears as a direct binding target (diagnostic
# blocks) still needs a synthetic device row so its points have a home
for (c, tgt) in bound:
    if (c, tgt) in dev_row:
        continue
    g = gw_ix.get((c, tgt))
    if g is None:
        continue
    if (c, tgt) not in dev_ix:
        dev_ix[(c, tgt)] = len(devs)
        devs.append({"g": g, "nm": tgt, "dv": tgt, "kind": "", "addr": "",
                     "proto": "MODBUS", "opt": "", "port": "",
                     "ds": "gateway diagnostics", "in": 0, "out": 0})

pts = []
for (c, tgt), rows in bound.items():
    di = dev_ix[(c, tgt)]
    for r in rows:
        out = TY[r] in OUT_TY
        reg, fmt = split_pnt(PNT[r])
        eu, lo, hi = rng(r, out)
        pts.append([di, 1 if out else 0, reg, bank_of(reg), fmt, TY[r],
                    NM[r], DS[r].strip(), eu, lo, hi])
        devs[di]["out" if out else "in"] += 1

pts.sort(key=lambda p: (p[0], p[1], p[2].zfill(8), p[6]))

payload = {
    "gen": time.strftime("%Y-%m-%d"),
    "cps": cps,
    "gws": gws,
    "devs": devs,
    "pts": pts,
}
js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf8")
gz = gzip.compress(js, 9)
open(OUT, "w", encoding="utf8", newline="\n").write(
    'window.FOX_MB_B64="%s";\n' % base64.b64encode(gz).decode("ascii"))

nin = sum(1 for p in pts if p[1] == 0)
nout = len(pts) - nin
print("CPs %d  gateways %d  devices %d  points %d  (IN %d / OUT %d)"
      % (len(cps), len(gws), len(devs), len(pts), nin, nout))
print("banks:", dict(Counter(p[3] for p in pts)))
print("json %.2f MB -> gzip %.0f KB -> modbus.js %.0f KB  (%.1fs)"
      % (len(js) / 1e6, len(gz) / 1024, os.path.getsize(OUT) / 1024, time.time() - t0))
