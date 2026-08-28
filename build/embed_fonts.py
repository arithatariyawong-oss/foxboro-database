# -*- coding: utf-8 -*-
"""Inline the SF Compact subsets into index.html as data: URIs.

The page has to work when index.html is opened straight off the disk, and
Chrome will not load an @font-face from a relative file:// URL there. Base64
in the stylesheet is the only thing that survives that, so the two weights
(~31 KB each -> ~42 KB encoded) ride inside the HTML.

The .woff2 files come from SF-Compact.dmg via the subsetting build in
"PT2 Analysis/scripts/build_sf_compact_subset.py"; they carry Latin plus the
typographic marks only. SF Compact has no Thai glyphs at all, which is why
--font-ui keeps Noto Sans Thai / Leelawadee UI behind it -- the browser falls
back per glyph, so Thai labels stay correct.

Re-run only if the fonts are replaced. Safe to run twice: it rewrites the
block between the FONTS markers rather than appending.
"""
import base64, io, re, sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
FONTS = WEB / "assets" / "fonts"
PAGE = WEB / "index.html"
FACES = [(400, "sf-compact-400.woff2"), (700, "sf-compact-700.woff2")]

START = "/* ============================================================ FONTS ==== */"
END = "/* ============================================================ TOKENS ==== */"

blocks = []
for weight, name in FACES:
    f = FONTS / name
    if not f.exists():
        sys.exit("missing font: %s" % f)
    b64 = base64.b64encode(f.read_bytes()).decode("ascii")
    blocks.append(
        '@font-face{font-family:"SF Compact";font-style:normal;font-weight:%d;'
        'font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % (weight, b64)
    )
    print("%-22s %6.1f KB -> %6.1f KB encoded" % (name, f.stat().st_size / 1024, len(b64) / 1024))

html = io.open(PAGE, encoding="utf8").read()
new = START + "\n" + "\n".join(blocks) + "\n\n" + END

if START in html:
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: new, html, flags=re.S)
else:
    if END not in html:
        sys.exit("could not find the TOKENS marker in index.html")
    html = html.replace(END, new, 1)

io.open(PAGE, "w", encoding="utf8").write(html)
print("index.html now %.1f KB" % (PAGE.stat().st_size / 1024))
