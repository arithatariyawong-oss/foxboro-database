# The step language — CALC / CALCA / LOGIC / MATH

4,232 blocks carry a program in `STEP01..STEP50` (CALCA 1,954, CALC 1,329,
LOGIC 928, MATH 21). It is a **stack machine**; B0193AX calls the top of stack
the accumulator. 72 distinct opcodes are in use. Format is
`OP [operands] ;comment`, and those comments are hand-written by the engineers
who built the interlocks — the most valuable thing in the dataset.

Source: **B0193AX ch.14 (CALC) and ch.15 (CALCA)**, `b0193ax1_u.pdf`.

## Stack effects that are easy to get wrong

Each was found by a program that refused to compile, never by reading the tables.

- **`OUT` COPIES the accumulator to the parameter — it does not pop.**
  `P3973:P3973ILK` cannot tell the two readings apart (its `OR 5` takes the top
  five either way), so do not "verify" this against that block.
  `02MG07_AOUT1:TIMER` is the discriminating case: `SUB / OUT RO03 / IN M02 /
  SUB`, and the second `SUB` has one operand unless `OUT` left the first alone.
- **`TIM` PUSHES the time from midnight.** It is not a timer that consumes its
  input. The manual gives it away: the operands of the timing instructions
  "except for TIM" name a time value, because TIM takes none. `DON`/`DOFF`/`OSP`
  *are* unary timers whose operand is **seconds**, never a count.
- **`SET`/`SETB`/`CLR`/`CLRB` touch NO stack.** Table 14-9 files them under
  "Unconditional Set/Clear": a literal goes to the parameter and the stack is
  untouched. Reading them as a pop made one pass believe 7,156 basic blocks
  needed a value from their predecessor. The true figure is **239**.
- **Arity is decided by how many operands are WRITTEN**, and all four forms are
  in use: `SUB RI05 RI06` (both named, nothing popped), `AND 2` (a count —
  polyadic only), `SUB M01` (pop one, combine with M01), `AND` (pop two).
  **`AND 2` and `SUB 2` look identical and are not**: AND is polyadic so 2 is a
  count, SUB is diadic so 2 is the number two.
- **B0193AX's "Instruction Type" column is the authority on the rest.**
  *Input Value / Input Status* push (`RBD`, `RCL`, `RQL`, `INS`, `RON`, `ROO`,
  `RE`, `RCN`, `RQE`, `TIM`); *Output Value* pops (`OUT`, `SAC`, `STH`, `STL`,
  `STM`); *Output Status* touches no stack (`CBD`, `CE`, `COO`, `REL`, `SBD`,
  `SE`, `SEC`, `SOO`). Reading those as pops underflowed 528 programs. Getting
  all four right took plant-wide underflows from 530 to **3**, and those three
  are genuinely malformed.

Other syntax: `~BI01` means **inverted** (the hollow circle in ICC).
`M01..M24` are memory registers with no column of their own. `CST` clears the
stack. `FF`/`MRS` are set-reset flip-flops (2 in, Q out; MRS reset-dominant).
`NOP`, `END`, `CST`, `CLA`, `CLM`, `DUP` were never in the opcode tables the page
originally carried — `CST` alone appears in 4,146 programs.

## Control flow is a FORWARD-ONLY DAG

This is the fact everything about drawing a branching program rests on.

> **§14.8.1:** "Unconditional transfer of control is supported only in a forward
> direction; looping backwards is not allowed."

and every branch opcode's own page adds that a target at or before the current
step (or past `END`) writes **`-4`, invalid goto syntax error, to `PERROR`**.

Verified against the plant: **0 backward jumps and 0 `GTI` in all 4,232
programs.** So a legal program has no loop, no fixed point to iterate, and basic
blocks that come out already in topological order.

**Every branch is `sptr(after) = sptr(before)`** — it reads the accumulator and
never pops it. So the value feeding a decision is simply the top of stack.

| opcode | branches when |
|---|---|
| `BIF s` / `BIZ s` | accumulator `= 0.0` — the manual says outright they are identical |
| `BIT s` | `≠ 0` |
| `BIN s` | `< 0` |
| `BIP s` | **`≥ 0` — positive OR zero** |
| `BII s` | the block is initializing this cycle |
| `GTO s` | unconditional |
| `SSx o` | sets `o` and **skips exactly one step** on the same condition |
| `EXIT` | "functionally equivalent to a GTO pointing at END" |

Frequencies: GTO 6,094 · END 3,435 · BIZ 3,217 · BIF 3,052 · BIN 1,424 ·
BIT 1,394 · EXIT 877 · BIP 330 · SSZ 112 · SSP 56 · SSN 22 · SSF 3 · SST 3 ·
BII 1.

## Cutting at branches makes 100% of it drawable

A leader starts a basic block: step 1, any branch target, and whatever falls out
of a control instruction. **All 26,215 basic blocks in the plant compile cleanly**
under the straight-line rules above, with zero unsupported opcodes. Max 20 blocks
in one program; 1,952 programs have exactly one.

That is what `logic-view.html` draws: a flowchart of basic blocks, each holding
its own real gate sheet, built by
`draw_branching_logic.py` → `layout_branching_logic.py` → `fix_branching_polish.py`
(in that order; each asserts its anchors).

**4,231 of 4,232 programs draw.** The one holdout, `SMS_SYS:SYS_COM3`, reads
BI01–BI07 and writes nothing — there is genuinely no output to draw.

## Regression cases

- **`P3973:P3973ILK`** — straight-line. Must stay 1 block / 0 containers /
  15 gates. ICC's own rendering is `03 WEB/12.png`.
- **`PS1F203MOV1:130MOV059VPL`** — branching. 19 basic blocks.

## Two traps in the drawing code itself

- **A polyadic backfill can spin forever.** `AND 3` with two things on the stack
  has to invent the third. Rotating the stack (pop then unshift) leaves the
  length unchanged and hangs the tab — every pass must *add* one.
- **A column can mix a wide IO box with a narrower gate box centred in the same
  reserved width, so a box's own `x` is not a safe lane anchor.** Anchor entry
  and exit lanes to the column's shared edges (min `x` / max `x+w` across every
  box at that depth).
