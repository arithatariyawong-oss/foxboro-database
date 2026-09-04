# HLBL — the independent sequence (IND) blocks

942 IND blocks run in this plant, from **779 `.s` files** in
`00 RAW DATABASE/S/S/` (4.5 MB, all `INDEPENDENT_SEQUENCE`). A different language
from the step programs entirely — Pascal-like, not a stack machine.

## Why they were a hole in the signal map

A sequence does not *pull* values through configured input references the way a
PID does — **it PUSHES, in code**:

```hlbl
ID := :39FCP003_SQ:39BATCH3.II0005;      { a read  -> an input reference }
:39FCP003_SQ:39ACP302.ACTIVE := TRUE;    { a write -> an output reference }
```

So its parameter record is **all zeros** (look at `39FCP003_SQ:39ACP301` in
`39CP05.txt`) and `export_graph.py`, which only ever sees parameter values,
cannot know any of it. Everything a sequence is wired to lives in the `.s` files
and nowhere else.

## The rule that reproduces ICC exactly

A write `X.P := …` from block B's program is an edge `(B.SEQ → X.P)`; a read of
`X.P` is `(X.P → B.SEQ)`. Then **Input References** = every edge whose
destination is this block; **Output References** = every edge whose source is it.

**A neighbour legitimately appears in BOTH panes and that is not a bug.** A main
sequence writes `39ACP301.ACTIVE := TRUE` to start it, then reads the same bit
in a `WAIT UNTIL … = FALSE` to know it finished. `03 WEB/13.png` — ICC's own
screenshot — shows exactly that, three times over.

`export_sequence.py --check` asserts all 4 input and 5 output rows of 13.png plus
the property order. **If it fails, fix the parser, not the assertion.**

## Reference syntax — all four forms are in use

| form | means | count |
|---|---|---|
| `:C101:01HS111.TOGGLE` | fully qualified | 4,265 |
| `::01HC111.RBIAS` | my own compound | 281 |
| `:01RTOTIM1.TIMR2` | my own compound, one colon | 81 |
| `:39FC00'X'_AS:39ACP'Y'.IIN` | a name built at run time | 1,267 |

The quoted pieces are variables spliced into the name. **ICC cannot resolve those
either** — show them as unresolved rather than guessing. Plus 256 that name a
block absent from the dumps.

## Traps

- **A `#define` names a reference but does not USE it.** 173 files use `#define`,
  and the scan *must* expand macros — `01LY065.s` writes `CBPSPT := Lprevspt;`
  and means `V101:01LRCA065.SPT`, invisible otherwise. But scoring the directive
  line itself as a read invented **685 phantom input references** (3 on
  `V101:01LY065` alone, every one a parameter the sequence only ever writes).
  Keep those refs for the source listing; make no edge from them.
- **HLBL comments `{...}` do NOT nest.** The first `}` closes. `39ACP301.s` has a
  commented-out subroutine left unbalanced; a nesting scanner swallows the rest
  of the file.
- **Strings are `"…"` with a doubled quote for a literal one.** The character
  table in `39ACP*.s` tests for a quote by writing four in a row — a naive
  scanner reads that as an empty string followed by an unterminated one.
- **One `.s` serves many instances.** The file is named for the BLOCK, and the
  same program is deployed into several compounds (the 24 `NR_*` programs run in
  BOSS_1, BOSS_1A, BOSS_1O, BOSS_1S). So `::BLK.PARAM` resolves **per instance**,
  not per file. 942 blocks from 779 sources; 4 orphan sources.
- **Precedence for an unqualified name** is the same as `export_graph.py`'s and
  for the same reason: own compound first, then a block in the same CP, then
  anything. Getting it backwards silently wires one unit's loop to another's.

## Structure of a `.s` file

`INDEPENDENT_SEQUENCE` · `CONSTANTS` · `VARIABLES` · `USER_LABELS`
(`SN1 : SN0001;` — maps a readable name onto a block parameter) · `SUBROUTINE` ·
`BLOCK_EXCEPTION` · `STATEMENTS` · `ENDSEQUENCE`. Statements are
`IF/THEN/ELSEIF/ENDIF`, `FOR/DO/ENDFOR`, `REPEAT/UNTIL`, `WAIT n`,
`WAIT UNTIL cond`, `CALL sub`, `EXIT`.

About 20 files are `#include "$HLBL_Library\..."` stubs whose library is not in
the folder — unresolvable, and they should say so rather than appear empty.

## Regression case

`39FCP003_SQ:39ACP301` — 4 input rows, 5 output rows, 125 properties, 350 source
lines, against `03 WEB/13.png`.
