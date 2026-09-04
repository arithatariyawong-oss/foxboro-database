# Raw data sources — formats, dialects, and the joins that work

Everything downstream is derived from these. Each has at least one trap that cost
real time.

## 1. SaveAll dumps — `00 RAW DATABASE/CP All Systems/*.txt`

92 files, ~54 MB, one per CP. The origin of the whole tag database, and the only
place a block's parameters stand in their **true record order** — which is what
ICC's Block Properties pane prints. `data.js`'s column list is a merge across all
1,202 columns of every block type and is ordered differently (`13.png` lists
MA/RSTMA/ACTIVE where `data.js` has HSCO1/LSCO1/DELTO1). If record order matters,
read the dump, not `data.js`.

**There are two dialects and both are in that one folder.**

```
# 87 CP files                      # CPTCI1.txt, CPTCI2.txt, CPTCI3.txt
CP=39CP05                          NAME   = CPTCI2_STA
NAME=39FCP003_SQ:39ACP301            TYPE   = COMPND
    TYPE=IND                         DESCRP =
    DESCRP=ACTUAL PRODUCT CHAR 1-4   PERIOD = 1
END                                (no CP line - the filename is the CP)
                                   (no END - a record runs to the next NAME)
```

Parsing only the first loses **93 sequence blocks** — every RTO and AMADAS one.
Match `^CP\s*=`, `^NAME\s*=`, `^[ \t]+(\w+)\s*=\s?(.*)$`, and close a record on
`END` **or** the next `NAME`.

The dumps moved out of `00 RAW DATABASE/` into `CP All Systems/` on 2026-09-04.
`export_sequence.py`'s `dump_dir()` accepts either and prints which it used, and
exits hard on finding none — because pointing a parser at an empty folder here
does not raise: it finds no records, every reference then fails to resolve, and a
`sequence.js` is still written with 942 empty blocks and no error at all.

## 2. HLBL sequence sources — `00 RAW DATABASE/S/S/*.s`

779 files, 4.5 MB, all `INDEPENDENT_SEQUENCE`. See `sequence-language.md`.

## 3. Jove export — `00 RAW DATABASE/Jove/*.exp`

Jove OBJECTS export v1.13. CRLF. A `JOVE OBJECTS,1.13` banner, then **three
sections** each introduced by a `#`-prefixed header row.

| section | Object Type | rows | usable |
|---|---|---|---|
| 0 | 0 | 14,375 | **no** — Jove-internal derived objects (`.MAS-MISMATCH`, `.PUMP-WORD`); no `Connection` column, and 14,338 of 14,375 have an empty `Jove Link` too |
| 1 | 1 | 18,871 | **yes — this is the whole value** |
| 2 | OPC UA | 0 | header only |

**`Connection` in section 1 is the join and it is clean.** Full
`COMPOUND:BLOCK.PARAM` (`PS1MCR_MOV05:39MOV229.MA`). All 18,871 parse; 18,502
resolve to a real block, 369 do not — 98%. Do **not** join on the object `Name`
prefix: it is only sometimes an equipment tag (`MOGAS` has 291 objects).

**`Buffered Read` / `Buffered Write` give the direction and it matters.** Jove
writes into the DCS **5,985 times** (4,146 write-only + 2,004 both). 10,378 are
read-only. 2,343 have neither flag — treat those as reads; the link is configured
either way, and calling an unflagged one a command path invents one.
`39MOV229.FIELDCLOSE → PS1MCR_MOV05:39MOV229.AUTCLS` is a valve close command
arriving from an API host.

Hosts: `AIMSERVER` (16,306), `AIMSERVER2` (2,565). `Historian Name`,
`Historian Point` and `OPC Server Item` are empty or junk (`OPC Server Item` is
the literal string `false` on every row) — ignore them.

`export_graph.py` picks the **newest `*.exp` in the folder**, not a fixed name.

## 4. Block parameter tables — `03 WEB/block_params.json`

Extracted from B0193AX (see §6). 78 types, 5,736 parameters, each with `desc`,
`type`, `con` (connectable), `set`, and `section` (INPUTS / OUTPUTS / DATA
STORES). `section` is what puts a pin on the left or right of a wiring diagram —
the tag database only knows which pins are *wired*. `params.js` is the slim
shipping copy.

Two known extraction artefacts: **`RIN.OUTPUTS` and `RINR.OUTPUTS` are section
headings the PDF parse caught as parameter names.** Exclude them or you get one
bogus row per RIN block.

Coverage: 46 of the 69 types in use, but only **1.4% of graph edges** touch an
uncovered type. The 4,607 blocks with no pin table at all are LONG 3,207,
UNIVFF 893, AI 379, AO 69, STA 41, PIDFF 14, MAO 2, COMPND 2 — FOUNDATION
Fieldbus blocks (documented in B0400FD / B0700BA) and ECB variants (B0400FA,
B0193RB). Absent is not the same as clean; say so in any report.

## 5. Hardware register — `TOP-Foxboro-Hardware-2025_RevA-1.xlsx`

Sheet `FBMnameAndType` has AI/AO/DI/DO/PI/IT/FF counts per letterbug,
`DATAFBMlist` firmware revs, `FBMandCP` product numbers and lifecycle.

**How a block reaches hardware:** a module is an ECB block whose TYPE is
ECB1/2/4/5/7/12/16/110/200/202 — `DEV_ID` is the letterbug, `HWTYPE` the model
code. An I/O block reaches it by `IOM_ID`; for a channel-addressed FBM that is
the module and `PNT_NO` is the channel, but for HART/FF/serial `IOM_ID` is a
*child* ECB (ECB201, or ECB18 on an FBM43) and the channel is on the child, in
`DVNAME` as `CH3` or `CHAN` as `3`.

**A block reaches redundant hardware by TWO letterbugs**: `IOM_ID` names one
module and `IOMIDR` its partner. Indexing only `IOM_ID` silently reports ~130
modules as carrying no blocks while their channel map shows tags. That was a real
bug in `system-manager.html` before it shipped.

FBM230/231/232/233 address Modbus registers and FBM228 addresses FF devices, so
neither gets a spare count — a number there would be fiction. FBM07/09/41 can
carry an expander (FBM12/FBM42) doubling the points on the same letterbug, which
is why observed channels may exceed the register.

## 6. The manuals — `04 MANUAL/k0173wt_g/`

141 files, 503 MB. **`scripts/b0.xml` is the catalogue** — 111 books with number,
revision, title, path — far faster to search than opening PDFs.

**B0193AX, Integrated Control Block Descriptions**, is the volume for anything
about block behaviour, in three parts under `V83/b0193/`:

| file | covers | pages |
|---|---|---|
| `b0193ax1_u.pdf` | ACCUM–DTIME (incl. **CALC ch.14, CALCA ch.15**) | 768 |
| `b0193ax2_u.pdf` | ECB–MOVLV (incl. LOGIC, MATH) | 802 |
| `b0193ax3_u.pdf` | MSG–VLV | 700 |

`pymupdf` is installed and works. `build/extract_block_params.py` does the
extraction.

Useful page anchors in `b0193ax1_u.pdf` (PDF page, not printed page):
§14.5 stack-effect tables 14-3..14-11 ≈ 352-359 · §14.5.6 program control
table 14-8 ≈ 357 · §14.8.1 execution sequence ≈ 416 · per-opcode pages ≈ 368-415.

## 7. `data.js` differs from the old Power BI report on purpose

Three corrections, so the numbers will not match it and that is intended:
1,070 STRING-block rows Power Query stranded in `Column1..Column5`
(75,940 → 77,010), 2,654 device ids Excel stripped a leading zero from, and
13,781 rows with a blank AREA because `02 AREA/CP AREA.xlsx` maps only 65 of 87
CPs. Filling that workbook and re-exporting is the fix for the third.
