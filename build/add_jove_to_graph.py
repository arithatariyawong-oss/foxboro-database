# -*- coding: utf-8 -*-
"""Teach export_graph.py about Jove, so the signal map shows the third way a
block is wired to something.

`00 RAW DATABASE/Jove/jove_20260518_2.exp` is a Jove OBJECTS export (v1.13),
three sections separated by `#`-prefixed header rows:

  Object Type 0  14,375 objects  Jove-internal, derived from other Jove
                                 objects (`.MAS-MISMATCH`, `.PUMP-WORD`);
                                 no Connection column, nothing to join, and
                                 14,338 of them have an empty Jove Link too.
  Object Type 1  18,871 objects  the OM/API connected ones. THIS is the
                                 section that matters.
  OPC UA         0 objects       the section exists, nothing in it.

Every one of the 18,871 rows in section 1 carries a `Connection` holding a
full `COMPOUND:BLOCK.PARAM` -- `PS1MCR_MOV05:39MOV229.MA`,
`13000F203DI1:130GBS165C.CIN` -- and all 18,871 parse. 13,057 land on a block
the graph already had, 5,445 on a block that had no wiring at all so was not
in the graph, and 369 on a name that is in neither (`T116_T:LEVEL` and
friends, 98% coverage). That second group is the point: those blocks exist
only to be read by Jove, and until now the map drew nothing for them.

DIRECTION IS IN THE FILE and it is not decoration -- `Buffered Read` /
`Buffered Write` say which way each connection runs, and Jove WRITES 6,150 of
them into the DCS (4,146 write-only plus 2,004 both ways). A command path
from a historian/API host into a control block is exactly the kind of thing
a signal map exists to make visible. 10,378 are read-only. The 2,343 with
neither flag set are drawn as reads -- the connection is configured either
way, and calling an unflagged one a write would be inventing a command path.

One node per Jove OBJECT rather than per equipment prefix: `39MOV229` has 8
objects hanging off one block, which reads the way a PAKCIN fan-out already
does, whereas grouping by prefix would put 291 pins on a single `MOGAS` box.
The Jove pin is the attribute (`CLOSE_SWITCH`), the Foxboro pin is the
parameter -- same grammar as the ECB edges, where the pin is the channel.

Run this once, then re-run `python build/export_graph.py`.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
SRC = WEB / "build" / "export_graph.py"

s = io.open(SRC, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


sub(
    'PARAMS = os.path.join(WEB, "block_params.json")\n',
    'PARAMS = os.path.join(WEB, "block_params.json")\n'
    '# newest export in the folder, not a fixed filename -- these are dated\n'
    '# (jove_20260518_2.exp) and a new one arrives whenever Jove is re-exported\n'
    'import glob\n'
    '_j = sorted(glob.glob(os.path.join(os.path.dirname(WEB), "00 RAW DATABASE",\n'
    '                                   "Jove", "*.exp")))\n'
    'JOVE = _j[-1] if _j else ""\n',
    "the Jove export's path, newest first",
)

# ---- parse + mark the blocks it reaches, BEFORE the keep-set is frozen ----
sub(
    "# ---- keep only the blocks the diagram can reach -------------------------\n"
    "used = set()\n",
    "# ---- Jove: the OM/API objects, and the parameters they are bound to -----\n"
    "# Section 1 of the export (Object Type 1) is the connected one. Parsed here\n"
    "# rather than after the keep-set is built, because 5,445 of these\n"
    "# connections are the ONLY thing touching their block -- freeze the keep-set\n"
    "# first and those blocks are dropped before Jove can put them back.\n"
    "import csv\n"
    "\n"
    "JREF = re.compile(r\"^([A-Za-z0-9_]+):([A-Za-z0-9_]+)\\.([A-Za-z0-9_]+)\"\n"
    "                  r\"(?:\\.([A-Za-z0-9_]+))?$\")\n"
    "jove = []                      # (obj, desc, host, attr, row, param, qual, is_write)\n"
    "j_miss = 0\n"
    "try:\n"
    "    jtext = open(JOVE, encoding='utf8', errors='replace', newline='').read()\n"
    "except OSError as e:\n"
    "    print('Jove export not read (%s) -- graph built without it' % e)\n"
    "    jtext = ''\n"
    "\n"
    "jsecs, jhdr, jcur = [], None, None\n"
    "for line in jtext.split('\\r\\n'):\n"
    "    if line.startswith('#'):\n"
    "        if jcur is not None:\n"
    "            jsecs.append((jhdr, jcur))\n"
    "        jhdr = next(csv.reader([line[1:]]))\n"
    "        jcur = []\n"
    "    elif jcur is not None and line.strip():\n"
    "        jcur.append(line)\n"
    "if jcur is not None:\n"
    "    jsecs.append((jhdr, jcur))\n"
    "\n"
    "for jh, jrows in jsecs:\n"
    "    ji = {c: k for k, c in enumerate(jh)}\n"
    "    if 'Connection' not in ji:            # type 0 and the empty OPC UA section\n"
    "        continue\n"
    "    for r in csv.reader(jrows):\n"
    "        if len(r) != len(jh):\n"
    "            continue\n"
    "        m = JREF.match(r[ji['Connection']])\n"
    "        if not m:\n"
    "            j_miss += 1\n"
    "            continue\n"
    "        row = by_full.get('%s:%s' % (m.group(1), m.group(2)))\n"
    "        if row is None:\n"
    "            j_miss += 1\n"
    "            continue\n"
    "        obj = r[ji['Name']]\n"
    "        wr = r[ji.get('Buffered Write', -1)] == 'true' if 'Buffered Write' in ji else False\n"
    "        rd = r[ji.get('Buffered Read', -1)] == 'true' if 'Buffered Read' in ji else False\n"
    "        attr = obj.split('.', 1)[1] if '.' in obj else obj\n"
    "        # both flags set is two real connections, one each way; neither set\n"
    "        # is still a configured link and is shown as a read\n"
    "        for is_write in ([True] if wr else []) + ([False] if rd or not wr else []):\n"
    "            jove.append((obj, r[ji['Description']], r[ji.get('API Host Name', 0)],\n"
    "                         attr, row, m.group(3), m.group(4) or '', is_write))\n"
    "print('Jove objects bound to a block: %d edges over %d objects (%d unresolved)'\n"
    "      % (len(jove), len({j[0] for j in jove}), j_miss))\n"
    "\n"
    "# ---- keep only the blocks the diagram can reach -------------------------\n"
    "used = set()\n",
    "parse the Jove export and resolve every Connection",
)

sub(
    "for i in range(N):                      # field I/O is an endpoint worth having\n"
    "    if ioA[i] >= 0 and name[i]:\n"
    "        used.add(i)\n",
    "for i in range(N):                      # field I/O is an endpoint worth having\n"
    "    if ioA[i] >= 0 and name[i]:\n"
    "        used.add(i)\n"
    "for j in jove:                          # ...and so is anything Jove talks to\n"
    "    used.add(j[4])\n",
    "a block Jove talks to is worth keeping even with no other wiring",
)

# ---- emit the Jove nodes and edges after the remap ----------------------
sub(
    "# the qualifier is a 5th element only where there is one -- 24% of the edges\n"
    "# carry one, and padding the other 76% with \"\" would cost graph.js for nothing\n"
    "elist = [[remap[s], sp, remap[t], tp] + ([q] if q else [])\n"
    "         for s, sp, t, tp, q in edges]\n",
    "# the qualifier is a 5th element only where there is one -- 24% of the edges\n"
    "# carry one, and padding the other 76% with \"\" would cost graph.js for nothing\n"
    "elist = [[remap[s], sp, remap[t], tp] + ([q] if q else [])\n"
    "         for s, sp, t, tp, q in edges]\n"
    "\n"
    "# ---- the Jove objects, appended as nodes of their own -------------------\n"
    "# A Jove node has no data.js row, so field 7 is -1 and signal-map.html shows\n"
    "# the object's own attributes instead of trying to read a row that is not\n"
    "# there. Field 3 carries the API host, which is the only 'where it lives'\n"
    "# a Jove object has.\n"
    "jnode = {}\n"
    "n_jw = 0\n"
    "for obj, desc, host, attr, row, param, qual, is_write in jove:\n"
    "    if obj not in jnode:\n"
    "        jnode[obj] = len(nodes)\n"
    "        nodes.append([obj, 'JOVE', desc, host, '', '', attr, -1])\n"
    "    j, b = jnode[obj], remap[row]\n"
    "    # Jove writing INTO the DCS is a command path and is drawn as one\n"
    "    e = ([j, attr, b, param] if is_write else [b, param, j, attr])\n"
    "    if qual:\n"
    "        e.append(qual)\n"
    "    elist.append(e)\n"
    "    n_jw += 1 if is_write else 0\n"
    "print('Jove nodes %d, edges %d (%d of them Jove writing into the DCS)'\n"
    "      % (len(jnode), len(jove), n_jw))\n",
    "append the Jove nodes and their edges",
)

io.open(SRC, "w", encoding="utf8", newline="").write(s)
print("export_graph.py %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
