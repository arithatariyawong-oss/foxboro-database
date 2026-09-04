---
name: foxboro
description: Working with the Foxboro I/A Series DCS database in Desktop/FOXBORO - the tag database, the offline web tool in 03 WEB (tag table, signal map, system manager, FBM modules, Modbus, Logic View, Sequence View), the raw SaveAll dumps, HLBL sequence sources, Jove OPC exports, and the B0193AX manuals. Use for any question or change about Foxboro blocks, pins, CPs, compounds, FBM modules, step programs, sequences, signal wiring, or rebuilding this tool's data files.
---

# Foxboro I/A Series — plant database and its web tool

`Desktop/FOXBORO/` holds a plant's whole Foxboro DCS configuration and an offline
web tool built over it. **77,010 blocks · 87 control processors · 69 block types ·
1,436 FBM modules.**

## Before anything else

1. **Measure, do not reason.** Every trap in `references/` was found by
   instrumenting something. The two times a guess came first (a browser cache, a
   mis-aimed test click) the guess was wrong and cost hours.
2. **Never resolve a qualified name by its bare name.** The plant reuses block
   names across CPs. Showing a different unit's block is worse than showing none.
3. **Every edit to a page is a one-shot script in `03 WEB/build/`** that does exact
   string replacement and `sys.exit`s if an anchor is not found exactly once. Read
   those scripts to see what changed or to reverse it. Do not hand-edit the HTML.
4. **The regression cases are real and named.** Check them after touching the
   thing they cover — they are listed in each reference file.

## Where things are

| path | what |
|---|---|
| `00 RAW DATABASE/CP All Systems/*.txt` | 92 per-CP SaveAll dumps — the origin of everything |
| `00 RAW DATABASE/S/S/*.s` | 779 HLBL sequence sources |
| `00 RAW DATABASE/Jove/*.exp` | Jove OPC/historian object exports |
| `02 AREA/CP AREA.xlsx` | CP → AREA map (incomplete: 65 of 87) |
| `03 WEB/` | the web tool — **this folder is the git repo**, not `FOXBORO` |
| `04 MANUAL/k0173wt_g/` | the I/A Series doc CD; `scripts/b0.xml` is its catalogue |

`03 WEB` pushes to `github.com/arithatariyawong-oss/foxboro-database` (public — a
settled decision, do not re-raise). `git` must run from `03 WEB`. No `gh` CLI.

## Read the reference file before working on its area

| file | when |
|---|---|
| `references/data-sources.md` | raw formats, file dialects, join keys, what each exporter reads |
| `references/block-language.md` | CALC/CALCA/LOGIC/MATH `STEP01–50`, stack effects, control flow |
| `references/sequence-language.md` | HLBL, IND blocks, `.s` files, reference syntax |
| `references/web-tool.md` | the seven pages, the data files, how to rebuild each |
| `references/house-style.md` | the UI system, and the traps in offline single-file pages |

## The one fact that explains most of this project

**A block's wiring lives in three separate places and no single file has all of it.**

- **parameter references** — a value like `V501:05FT065.PNT` sitting in another
  block's parameter. `export_graph.py` reads these. 58,129 edges.
- **HLBL code** — a sequence block pushes (`X.P := ...`), it does not pull, so its
  parameter record is *all zeros* and the graph exporter cannot see any of it.
  `export_sequence.py` reads the `.s` files. 4,075 edges.
- **Jove `Connection`** — 18,502 OPC objects bound to a parameter, and 5,985 of
  them *write into* the DCS. `add_jove_to_graph.py` reads the `.exp`.

Missing any one of them makes whole classes of block look unconnected: 942 IND
blocks and 4,027 Jove-only blocks each drew an empty signal map until their
source was wired in. When something "has no connections", check which of the
three you are actually looking at.

## Regenerating data (run from `03 WEB`)

```
python build/export_data.py        # data.js     from FOX DATABASE.xlsx
python build/export_graph.py       # graph.js    from data.js + block_params.json + Jove
python build/export_systems.py     # systems.js  from data.js + the hardware register
python build/export_modbus.py      # modbus.js   from data.js
python build/export_logic.py       # logic.js    from data.js + graph.js
python build/export_sequence.py --check   # sequence.js from the .s files + dumps + graph.js
```

`--check` on `export_sequence.py` rebuilds `39FCP003_SQ:39ACP301` and asserts it
against `03 WEB/13.png`, ICC's own screenshot of that block. **If it fails, fix
the parser, not the assertion.**

Order matters: `export_data.py` first, then everything that reads `data.js`;
`export_logic.py` and `export_sequence.py` read `graph.js`, so run them after it.
