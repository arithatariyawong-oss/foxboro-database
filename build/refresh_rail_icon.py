# -*- coding: utf-8 -*-
"""Regenerate the rail's icon tile from 05.jpg and swap it into index.html.

The source is a 1024px render with a wide white margin, so painted at
background-size:cover the icon itself only occupies the middle ~60% of a
108px tile and reads far smaller than it should. Trim to the artwork's own
bounding box (its drop shadow included), pad it back out to a square, and
the icon fills the tile.

The white that remains is left alone on purpose: it becomes the tile's face,
the way the reference app treats its own square-on-white icon. Keying it to
transparent would take the drop shadow with it.

Run this again after replacing 05.jpg.
"""
import base64, io, re, sys
from pathlib import Path
from PIL import Image, ImageChops

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "index.html"
SRC = WEB / "05.jpg"
TILE = 256          # 108px tile on a 2x display, with room to spare
PAD = 0.05          # breathing room around the artwork, as a share of its box

im = Image.open(SRC).convert("RGB")
w, h = im.size

# bounding box of everything that is not the white field
bg = Image.new("RGB", im.size, (255, 255, 255))
diff = ImageChops.difference(im, bg).convert("L")
box = diff.point(lambda p: 255 if p > 6 else 0).getbbox()
if box is None:
    sys.exit("05.jpg looks blank")
x0, y0, x1, y1 = box
print("artwork bbox %s of %dx%d  (%.0f%% of the frame)"
      % (box, w, h, (x1 - x0) * (y1 - y0) / (w * h) * 100))

# square it up around the artwork's centre, then pad
side = max(x1 - x0, y1 - y0)
side = int(side * (1 + PAD * 2))
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
half = side // 2
crop = im.crop((cx - half, cy - half, cx + half, cy + half))   # PIL pads with black
# re-crop against a white canvas so any overhang stays white, not black
canvas = Image.new("RGB", (side, side), (255, 255, 255))
src_box = (max(cx - half, 0), max(cy - half, 0), min(cx + half, w), min(cy + half, h))
canvas.paste(im.crop(src_box), (max(0, half - (cx - src_box[0])), max(0, half - (cy - src_box[1]))))
canvas = canvas.resize((TILE, TILE), Image.LANCZOS)

buf = io.BytesIO()
canvas.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
b64 = base64.b64encode(buf.getvalue()).decode("ascii")
print("-> %dpx tile, %.1f KB raw, %.1f KB encoded" % (TILE, len(buf.getvalue()) / 1024, len(b64) / 1024))

s = io.open(PAGE, encoding="utf8").read()
new, k = re.subn(r"(url\(data:image/jpeg;base64,)[A-Za-z0-9+/=]+(\) center/cover)",
                 lambda m: m.group(1) + b64 + m.group(2), s, count=1)
if k != 1:
    sys.exit("could not find the rail icon's data URI in index.html")
io.open(PAGE, "w", encoding="utf8").write(new)
print("index.html now %.1f KB" % (PAGE.stat().st_size / 1024))
