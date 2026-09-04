# -*- coding: utf-8 -*-
"""Point `FOXBORO/.claude/skills/foxboro` at the copy in this repo.

The `foxboro` skill needs to be in two places at once and must not be two
copies:

  * Claude Code discovers project skills under the directory it was opened in,
    and the work happens in `FOXBORO/` -- the raw dumps, the manuals and the
    `.s` sources all live there, so that is where a session gets started.
  * `FOXBORO/` is not a git repo. `03 WEB/` is. A skill kept only in
    `FOXBORO/.claude/` is one deleted folder away from gone.

So the real files live in `03 WEB/.claude/skills/foxboro/` where git tracks
them, and `FOXBORO/.claude/skills/foxboro` is an NTFS **directory junction**
pointing at them. Editing through either path edits the same file; git only
ever sees the repo side, because the junction sits outside the repo.

Junctions need no administrator rights (unlike symlinks), which is why this is
a junction and not `mklink /D`.

Run after a fresh clone, or any time the link is missing. Safe to re-run: it
checks where the link already points and leaves a correct one alone. It will
NOT delete a real directory that happens to sit at the link path -- that would
be someone's files.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)                       # ...\FOXBORO\03 WEB
ROOT = os.path.dirname(WEB)                       # ...\FOXBORO

TARGET = os.path.join(WEB, ".claude", "skills", "foxboro")
LINK = os.path.join(ROOT, ".claude", "skills", "foxboro")

if os.name != "nt":
    sys.exit("This is a Windows NTFS junction; nothing to do on %s." % os.name)

if not os.path.isdir(TARGET):
    sys.exit("ABORT: no skill to link to at\n       %s" % TARGET)

if os.path.exists(LINK):
    # islink() is False for a junction on Python/Windows in some versions, so
    # ask the filesystem what it actually is rather than trusting one call.
    real = os.path.realpath(LINK)
    if os.path.normcase(real) == os.path.normcase(os.path.realpath(TARGET)):
        print("already linked:\n  %s\n  -> %s" % (LINK, real))
        sys.exit(0)
    if not (os.path.islink(LINK) or os.path.ismount(LINK)
            or os.path.normcase(real) != os.path.normcase(LINK)):
        sys.exit("ABORT: %s is a real directory, not a link.\n"
                 "       Move or delete it yourself first -- refusing to "
                 "remove files that may not be a copy." % LINK)
    os.rmdir(LINK)                                # a junction: removes the link only
    print("removed a link that pointed elsewhere (%s)" % real)

os.makedirs(os.path.dirname(LINK), exist_ok=True)
r = subprocess.run(["cmd", "/c", "mklink", "/J", LINK, TARGET],
                   capture_output=True, text=True)
if r.returncode != 0:
    sys.exit("ABORT: mklink failed\n%s%s" % (r.stdout, r.stderr))

print(r.stdout.strip())
probe = os.path.join(LINK, "SKILL.md")
print("verified: %s -> %s" % (probe, "readable" if os.path.isfile(probe) else "MISSING"))
