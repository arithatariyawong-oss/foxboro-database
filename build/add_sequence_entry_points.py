# -*- coding: utf-8 -*-
"""Make Sequence View reachable for the blocks that need it most.

add_sequence_popup.py hung the popup off signal-map.html's block menu, which
is fine until you notice what a sequence block's map looks like: EMPTY. A
sequence's parameter record holds no references, so graph.js has no node for
it, so signal-map draws nothing and there is no box to right-click. 39ACP301
-- the block in 13.png, with nine references between its two panes -- is
exactly such a block. The one entry point missed the whole point.

Three additions, all of them popup-or-link, none of them a page in the nav:

  * index.html -- the tag table's NAME menu gains "เปิด Sequence View" beside
    the signal-map link it already has, shown when TYPE is IND. This is the
    reliable route: the table has a row for every block in the plant and
    knows its type, whether or not it is wired to anything.
  * signal-map.html, isolated block -- the block IS in the graph but has no
    neighbours; TYPE is known, so the empty state offers the popup outright.
  * signal-map.html, block not in the graph at all -- nothing is known but
    the name, so the empty state says what Sequence View is for and lets the
    reader decide. sequence-view.html says so itself if the name is not one.
"""
import io
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent


def edit(path, jobs):
    s = io.open(path, encoding="utf8").read()
    n0 = len(s)
    for old, new, what in jobs:
        if s.count(old) != 1:
            sys.exit("ABORT: %s -- anchor found %d times, expected 1"
                     % (what, s.count(old)))
        s = s.replace(old, new, 1)
        print("  ok  %s" % what)
    io.open(path, "w", encoding="utf8", newline="").write(s)
    print("%s %d -> %d chars (%+d)" % (path.name, n0, len(s), len(s) - n0))


# ---- index.html: the tag table's NAME menu -------------------------------
edit(WEB / "index.html", [(
    "    `<a href=\"signal-map.html?tag=${encodeURIComponent(tag)}\">"
    "เปิด signal map<i>ผังสัญญาณ</i></a>` +\n",
    "    `<a href=\"signal-map.html?tag=${encodeURIComponent(tag)}\">"
    "เปิด signal map<i>ผังสัญญาณ</i></a>` +\n"
    "    /* Only IND blocks have an HLBL program, and every one of them does.\n"
    "       This is the dependable way in: a sequence block is usually absent\n"
    "       from the signal map entirely (its parameter record references\n"
    "       nothing), so the map's own menu cannot offer it. */\n"
    "    (ty === 'IND'\n"
    "      ? `<a href=\"sequence-view.html?tag=${encodeURIComponent(tag)}\">"
    "เปิด Sequence View<i>โปรแกรม + reference</i></a>` : '') +\n",
    "index.html: Sequence View in the tag menu, on IND rows",
)])

# ---- signal-map.html: both empty states ----------------------------------
edit(WEB / "signal-map.html", [
    (
        "    $('#empty').innerHTML = `<div><b>${esc(NAME(n))}</b> "
        "ไม่มีการเชื่อมต่อกับบล็อกอื่นในฐานข้อมูล<br>` +\n"
        "      `<span style=\"font-size:13px\">${esc(TYPE(n))}"
        "${IOM(n) ? ' · FBM ' + esc(IOM(n)) : ''}</span></div>`;\n",
        "    $('#empty').innerHTML = `<div><b>${esc(NAME(n))}</b> "
        "ไม่มีการเชื่อมต่อกับบล็อกอื่นในฐานข้อมูล<br>` +\n"
        "      `<span style=\"font-size:13px\">${esc(TYPE(n))}"
        "${IOM(n) ? ' · FBM ' + esc(IOM(n)) : ''}</span>` +\n"
        "      /* An IND block wires itself up in code, not in its parameter\n"
        "         record, so \"no connections\" here means \"not in this graph\" —\n"
        "         not that there are none. Say where they are. */\n"
        "      (TYPE(n) === 'IND'\n"
        "        ? `<br><br><span style=\"font-size:13px\">บล็อก sequence "
        "เชื่อมต่อผ่านโค้ด ไม่ใช่ผ่านค่าพารามิเตอร์ จึงไม่ปรากฏในผังนี้ — `+\n"
        "          `<b class=\"seq-open\" style=\"cursor:pointer;color:var(--wire-hot);"
        "text-decoration:underline\">เปิด Sequence View</b></span>` : '') +\n"
        "      `</div>`;\n"
        "  if (laid.keep.size <= 1 && TYPE(n) === 'IND')\n"
        "    $('#empty').querySelector('.seq-open')\n"
        "      .addEventListener('click', () => openSeqPopup(n));\n",
        "signal-map.html: isolated IND block points at the popup",
    ),
    (
        "        `<div><b>${esc(want)}</b> ไม่มีการเชื่อมต่อกับบล็อกอื่น จึงไม่มี signal map<br>` +\n"
        "        `<span style=\"font-size:13px\">บล็อกที่ไม่อ้างถึงบล็อกอื่น ไม่ถูกบล็อกอื่นอ้างถึง ` +\n"
        "        `และไม่ผูกกับ FBM จะไม่อยู่ในกราฟ — ลองค้นหา tag อื่นด้านบน</span></div>`;\n",
        "        `<div><b>${esc(want)}</b> ไม่มีการเชื่อมต่อกับบล็อกอื่น จึงไม่มี signal map<br>` +\n"
        "        `<span style=\"font-size:13px\">บล็อกที่ไม่อ้างถึงบล็อกอื่น ไม่ถูกบล็อกอื่นอ้างถึง ` +\n"
        "        `และไม่ผูกกับ FBM จะไม่อยู่ในกราฟ — ลองค้นหา tag อื่นด้านบน</span><br><br>` +\n"
        "        /* Nothing is known here but the name — the block is not in\n"
        "           graph.js at all, which is the normal state of a sequence.\n"
        "           sequence-view.html says so itself if the name is not IND. */\n"
        "        `<span style=\"font-size:13px\">ถ้าเป็นบล็อก sequence (IND) reference ทั้งหมด ` +\n"
        "        `อยู่ในโค้ด ไม่ใช่ในค่าพารามิเตอร์ — ` +\n"
        "        `<a href=\"sequence-view.html?tag=${encodeURIComponent(want)}\" ` +\n"
        "        `style=\"color:var(--wire-hot)\">เปิด Sequence View</a></span></div>`;\n",
        "signal-map.html: a name not in the graph points at Sequence View",
    ),
])
