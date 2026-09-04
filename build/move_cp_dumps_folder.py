# -*- coding: utf-8 -*-
"""Follow the SaveAll dumps into `00 RAW DATABASE/CP All Systems/`.

The 92 per-CP SaveAll text dumps used to sit loose in `00 RAW DATABASE/`
alongside the `S/` and `Jove/` folders; they were moved into a folder of
their own on 2026-09-04. Only `export_sequence.py` reads them --
`export_graph.py` and `add_jove_to_graph.py` reach into `Jove/` by name and
are unaffected -- so this is a one-line change plus the honesty to say which
folder it actually used.

Both layouts are accepted rather than just the new one. A hard-coded
`CP All Systems` would fail silently in the worst way available here: the
parser would find zero records, `row_of` would come up empty, EVERY sequence
reference would fail to resolve, and sequence.js would still be written --
942 blocks with no properties and no wiring, and no error anywhere. The
`--check` regression would catch it, but only if someone remembered to pass
it. So the folder is picked at run time and printed, and finding no dumps at
all is a hard exit instead of an empty export.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
SRC = WEB / "build" / "export_sequence.py"

s = io.open(SRC, encoding="utf8").read()
n_before = len(s)


def sub(old, new, what):
    global s
    if s.count(old) != 1:
        sys.exit("ABORT: %s -- anchor found %d times, expected 1" % (what, s.count(old)))
    s = s.replace(old, new, 1)
    print("  ok  %s" % what)


sub(
    'RAW = os.path.join(ROOT, "00 RAW DATABASE")\n'
    'SDIR = os.path.join(RAW, "S", "S")\n',
    'RAW = os.path.join(ROOT, "00 RAW DATABASE")\n'
    'SDIR = os.path.join(RAW, "S", "S")\n'
    '\n'
    '\n'
    'def dump_dir():\n'
    '    """Where the per-CP SaveAll .txt dumps live.\n'
    '\n'
    '    They moved into `CP All Systems/` on 2026-09-04. Both layouts are\n'
    '    accepted because guessing wrong here fails silently: no records means\n'
    '    no blocks, every reference then fails to resolve, and a sequence.js\n'
    '    still gets written with 942 empty blocks and no error raised.\n'
    '    """\n'
    '    for d in (os.path.join(RAW, "CP All Systems"), RAW):\n'
    '        if os.path.isdir(d) and any(f.lower().endswith(".txt")\n'
    '                                    for f in os.listdir(d)):\n'
    '            return d\n'
    '    sys.exit("ABORT: no SaveAll .txt dumps under %s (looked in\\n"\n'
    '             "       CP All Systems/ and the folder itself)" % RAW)\n'
    '\n'
    '\n'
    'DUMPS = dump_dir()\n',
    "dump_dir(): CP All Systems, falling back to the folder root",
)

sub(
    "n_rec = 0\n"
    "for fn in sorted(os.listdir(RAW)):\n"
    "    if not fn.lower().endswith(\".txt\"):\n"
    "        continue\n",
    "n_rec = 0\n"
    "print(\"SaveAll dumps: %s\" % DUMPS)\n"
    "for fn in sorted(os.listdir(DUMPS)):\n"
    "    if not fn.lower().endswith(\".txt\"):\n"
    "        continue\n",
    "read the dumps from DUMPS, and say which folder that was",
)

sub(
    '    with open(os.path.join(RAW, fn), encoding="utf8", errors="replace") as fh:\n',
    '    with open(os.path.join(DUMPS, fn), encoding="utf8", errors="replace") as fh:\n',
    "open each dump from DUMPS",
)

# the file header describes its own inputs; keep it true
sub(
    "  * `00 RAW DATABASE/*.txt` -- the SaveAll dumps, read instead of data.js\n"
    "    because the dump is the only place the parameters stand in their true\n",
    "  * `00 RAW DATABASE/CP All Systems/*.txt` -- the SaveAll dumps (they sat\n"
    "    loose in `00 RAW DATABASE/` until 2026-09-04; both layouts still\n"
    "    work, see dump_dir). Read instead of data.js\n"
    "    because the dump is the only place the parameters stand in their true\n",
    "header names the new folder",
)

io.open(SRC, "w", encoding="utf8", newline="").write(s)
print("export_sequence.py %d -> %d chars (%+d)" % (n_before, len(s), len(s) - n_before))
