# -*- coding: utf-8 -*-
"""One-off: enlarge the type scale of index.html and put SF Compact in front
of the font stack. Kept in build/ so the edit is reproducible; every rule is
an exact string swap and a miss is reported rather than silently skipped."""
import io, sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"
s = io.open(PAGE, encoding="utf8").read()

SUBS = [
    # ---- font stack: SF Compact first, Thai fallback behind it -----------
    ('--font-ui:-apple-system,BlinkMacSystemFont,"Segoe UI","Helvetica Neue",Arial,\n'
     '            "Noto Sans Thai","Leelawadee UI",Tahoma,sans-serif;',
     '--font-ui:"SF Compact",-apple-system,BlinkMacSystemFont,"Segoe UI",\n'
     '            "Noto Sans Thai","Leelawadee UI",Tahoma,sans-serif;'),

    # ---- base -----------------------------------------------------------
    ('font-family:var(--font-ui); font-size:14px; line-height:1.55;',
     'font-family:var(--font-ui); font-size:15.5px; line-height:1.55;'),

    # ---- topbar ---------------------------------------------------------
    ('.eyebrow{margin:0 0 6px; font-size:10.5px;', '.eyebrow{margin:0 0 7px; font-size:12px;'),
    ('h1{font-size:clamp(30px,4.4vw,46px);', 'h1{font-size:clamp(34px,5vw,54px);'),
    ('.lede{margin:9px 0 0; color:var(--text-dim); font-size:13px}',
     '.lede{margin:10px 0 0; color:var(--text-dim); font-size:15px}'),
    ('  border-radius:var(--r-pill); padding:9px 18px; cursor:pointer;\n'
     '  font-size:12.5px; font-weight:700; letter-spacing:.02em;',
     '  border-radius:var(--r-pill); padding:11px 22px; cursor:pointer;\n'
     '  font-size:14px; font-weight:700; letter-spacing:.02em;'),

    # ---- tabs -----------------------------------------------------------
    ('  padding:9px 26px; border-radius:var(--r-pill); cursor:pointer;\n'
     '  font-size:12px; font-weight:800; letter-spacing:.1em;',
     '  padding:11px 30px; border-radius:var(--r-pill); cursor:pointer;\n'
     '  font-size:13.5px; font-weight:800; letter-spacing:.09em;'),

    # ---- rail -----------------------------------------------------------
    ('.layout{display:grid; grid-template-columns:300px minmax(0,1fr);',
     '.layout{display:grid; grid-template-columns:335px minmax(0,1fr);'),
    ('.rail-head span{font-size:13px;', '.rail-head span{font-size:15px;'),
    ('  font-size:10px; font-weight:800; letter-spacing:.11em; text-transform:uppercase;\n'
     '  color:var(--accent); padding:0 4px;',
     '  font-size:11.5px; font-weight:800; letter-spacing:.1em; text-transform:uppercase;\n'
     '  color:var(--accent); padding:0 4px;'),
    ('  margin-left:auto; font-size:9.5px; font-weight:700;',
     '  margin-left:auto; font-size:11px; font-weight:700;'),
    ('  border-radius:var(--r-pill); padding:10px 34px 10px 15px; font-size:13px;',
     '  border-radius:var(--r-pill); padding:11px 36px 11px 16px; font-size:14.5px;'),
    ('.search .mag{position:absolute; right:13px; color:var(--text-faint); font-size:12px;',
     '.search .mag{position:absolute; right:14px; color:var(--text-faint); font-size:14px;'),

    # ---- chips ----------------------------------------------------------
    ('.chips{display:flex; flex-wrap:wrap; gap:6px; max-height:190px;',
     '.chips{display:flex; flex-wrap:wrap; gap:7px; max-height:215px;'),
    ('  border-radius:var(--r-pill); padding:5px 12px; cursor:pointer;\n'
     '  font-size:11.5px; font-weight:700; white-space:nowrap;',
     '  border-radius:var(--r-pill); padding:6px 14px; cursor:pointer;\n'
     '  font-size:13px; font-weight:700; white-space:nowrap;'),
    ('.chip .c{opacity:.62; font-weight:600; margin-left:5px; font-size:10.5px}',
     '.chip .c{opacity:.62; font-weight:600; margin-left:6px; font-size:11.5px}'),

    # ---- column picker --------------------------------------------------
    ('.colrow .nm{font-size:12px;', '.colrow .nm{font-size:13.5px;'),
    ('.colrow .ct{margin-left:auto; font-size:10px;', '.colrow .ct{margin-left:auto; font-size:11.5px;'),
    ('.collist{\n  max-height:340px;', '.collist{\n  max-height:380px;'),
    ('  border-radius:var(--r-pill); padding:4px 11px; font-size:10.5px; font-weight:700; cursor:pointer;',
     '  border-radius:var(--r-pill); padding:5px 13px; font-size:12px; font-weight:700; cursor:pointer;'),

    # ---- section headings ----------------------------------------------
    ('h2{font-size:11px; font-weight:800; letter-spacing:.11em;',
     'h2{font-size:12.5px; font-weight:800; letter-spacing:.1em;'),
    ('h2 .n{font-size:10.5px;', 'h2 .n{font-size:12px;'),

    # ---- KPI tiles ------------------------------------------------------
    ('.kpis{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px}',
     '.kpis{display:grid; grid-template-columns:repeat(auto-fit,minmax(175px,1fr)); gap:14px}'),
    ('.kpi b{font-size:27px;', '.kpi b{font-size:34px;'),
    ('.kpi span{font-size:9.5px;', '.kpi span{font-size:11px;'),
    ('.kpi em{font-style:normal; font-size:11px;', '.kpi em{font-style:normal; font-size:12.5px;'),

    # ---- charts ---------------------------------------------------------
    ('figcaption{font-size:11px; font-weight:800; letter-spacing:.09em;',
     'figcaption{font-size:12.5px; font-weight:800; letter-spacing:.08em;'),
    ('.chart .lbl{font-size:11px; fill:var(--text-dim)}',
     '.chart .lbl{font-size:12.5px; fill:var(--text-dim)}'),
    ('.chart .val{font-size:11px; fill:var(--text); font-weight:700}',
     '.chart .val{font-size:13px; fill:var(--text); font-weight:700}'),
    ('  box-shadow:var(--lift); padding:8px 12px; font-size:12px;',
     '  box-shadow:var(--lift); padding:10px 14px; font-size:13.5px;'),
    ('.tip b{display:block; font-size:12.5px;', '.tip b{display:block; font-size:14px;'),
    ('  const LW = 116, VW = 78, RH = 24, GAP = 6, PAD = 2;',
     '  const LW = 134, VW = 90, RH = 29, GAP = 7, PAD = 3;'),
    ('    const y = PAD + k * (RH + GAP), bh = 14, by = y + (RH - bh) / 2;',
     '    const y = PAD + k * (RH + GAP), bh = 17, by = y + (RH - bh) / 2;'),

    # ---- tables ---------------------------------------------------------
    ('  padding:10px 12px; font-size:10px; font-weight:800; letter-spacing:.08em;',
     '  padding:12px 13px; font-size:11.5px; font-weight:800; letter-spacing:.07em;'),
    ('  padding:0 12px; height:34px; line-height:34px; font-size:12.5px;',
     '  padding:0 13px; height:39px; line-height:39px; font-size:14px;'),
    ('const ROWH = 34, OVER = 8;', 'const ROWH = 39, OVER = 8;'),
    ('  overflow:auto; max-height:560px; position:relative;',
     '  overflow:auto; max-height:620px; position:relative;'),
    ('.tbl-scroll.short{max-height:330px}', '.tbl-scroll.short{max-height:370px}'),
    ('.sbar{display:block; height:9px;', '.sbar{display:block; height:11px;'),
    ("const WIDTH = { 'AREA':110, 'CP NAME':105, 'TYPE':95, 'NAME':250, 'DESCRP':300, 'Source.Name':120 };",
     "const WIDTH = { 'AREA':125, 'CP NAME':125, 'TYPE':110, 'NAME':290, 'DESCRP':340, 'Source.Name':145 };"),
    ('const widthOf = ci => WIDTH[HEAD[ci]] || 140;', 'const widthOf = ci => WIDTH[HEAD[ci]] || 155;'),
    ("  const tp = '120px 115px 105px 95px minmax(120px,1fr)';",
     "  const tp = '135px 135px 120px 110px minmax(130px,1fr)';"),

    # ---- misc -----------------------------------------------------------
    ('.note{font-size:11.5px;', '.note{font-size:13px;'),
    ('  padding:44px 20px; text-align:center; color:var(--text-dim); font-size:13px;',
     '  padding:48px 20px; text-align:center; color:var(--text-dim); font-size:15px;'),
    ('#boot p{margin:0; color:var(--text-dim); font-size:13px}',
     '#boot p{margin:0; color:var(--text-dim); font-size:15px}'),
]

missing = []
for old, new in SUBS:
    if old not in s:
        missing.append(old.strip().splitlines()[0][:76])
    else:
        s = s.replace(old, new, 1)

if missing:
    print("NOT FOUND (%d):" % len(missing))
    for m in missing:
        print("   -", m)
    sys.exit(1)

io.open(PAGE, "w", encoding="utf8").write(s)
print("applied %d edits -> %.1f KB" % (len(SUBS), PAGE.stat().st_size / 1024))
