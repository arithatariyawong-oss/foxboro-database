# -*- coding: utf-8 -*-
"""Regenerate the rail's icon tile from 05.jpg and swap it into index.html.

Three things happen to the source before it becomes a 108px tile.

1. DE-SKEW. 05.jpg is an oblique 3D render: the plate's top and bottom edges
   run downhill to the right by about 12.5 degrees, so the icon reads as
   crooked. It is NOT rotated, though — the slider stems are vertical to
   within 0.01 degrees, which is the signature of an oblique projection.
   Rotating to level the plate would therefore tilt the stems and make it
   worse. A vertical SHEAR is the correct correction: it maps (x, y) to
   (x, y + s*x), which levels the sloping edges while leaving every vertical
   line exactly vertical. The slope is measured from the artwork itself, so
   this still works if 05.jpg is replaced.

   The top and bottom edges differ by ~2 degrees (11.4 vs 13.6) because the
   plate really is in perspective; a single shear cannot remove that, so the
   average is used and about a degree of trapezoid remains. Undoing it fully
   would need a four-corner perspective warp of a rounded shape, which costs
   sharpness for something no one can see at 108px.

2. TRIM, on the ink rather than the drop shadow. The shadow falls down and
   right, so trimming to every non-white pixel pushes the icon up and left
   inside the tile and it looks off-centre. A high threshold finds the
   artwork; the shadow is then kept as padding rather than as content.

3. SCALE to 256px and inline as a data: URI, because Chrome will not load a
   relative background-image from a page opened over file://.

Run again after replacing 05.jpg.
"""
import base64, io, math, re, sys
from pathlib import Path

from PIL import Image, ImageChops

WEB = Path(__file__).resolve().parent.parent
PAGE = WEB / "index.html"
SRC = WEB / "05.jpg"
TILE = 256          # a 108px tile on a 2x display, with room to spare
PAD = 0.05          # breathing room around the artwork
INK = 40            # "this is the icon", not its soft shadow


def ink_mask(im, thr=INK):
    diff = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255)))
    return diff.convert("L").point(lambda p: 255 if p > thr else 0)


def edge_slope(mask):
    """slope of the plate's top and bottom edges, over their straight middle"""
    px = mask.load()
    bb = mask.getbbox()
    if not bb:
        return None
    x0, y0, x1, y1 = bb
    lo, hi = x0 + int((x1 - x0) * 0.22), x0 + int((x1 - x0) * 0.78)
    out = []
    for rng in (range(y0, y1), range(y1 - 1, y0, -1)):
        pts = []
        for x in range(lo, hi):
            for y in rng:
                if px[x, y]:
                    pts.append((x, y))
                    break
        if len(pts) < 40:
            return None
        n = len(pts)
        mx = sum(p[0] for p in pts) / n
        my = sum(p[1] for p in pts) / n
        den = sum((p[0] - mx) ** 2 for p in pts)
        if not den:
            return None
        s = sum((p[0] - mx) * (p[1] - my) for p in pts) / den
        resid = sum(abs(p[1] - (my + s * (p[0] - mx))) for p in pts) / n
        if resid > 4:                      # not a straight edge; do not guess
            return None
        out.append(s)
    return sum(out) / len(out)


im = Image.open(SRC).convert("RGB")
w, h = im.size
slope = edge_slope(ink_mask(im))

if slope is None:
    print("could not measure the plate edges - leaving the artwork as it is")
else:
    print("plate edges slope %+.4f (%.2f deg) - shearing vertically to level them"
          % (slope, math.degrees(math.atan(slope))))
    grow = int(abs(slope) * w) + 8
    canvas = Image.new("RGB", (w, h + grow * 2), (255, 255, 255))
    canvas.paste(im, (0, grow))
    # output(x, y) samples input(x, y + slope*x): verticals stay vertical
    im = canvas.transform(canvas.size, Image.AFFINE,
                          (1, 0, 0, slope, 1, -slope * w / 2),
                          resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    left = edge_slope(ink_mask(im))
    if left is not None:
        print("  after shear: %+.4f (%.2f deg)" % (left, math.degrees(math.atan(left))))

# ---- keep the whole frame, centred on the artwork ------------------------
# The square is the SOURCE frame's own size, not a tight crop of the ink, so
# the icon keeps the margin it was drawn with and nothing of it is lost to
# the tile's 24px corner rounding. Centring on the artwork's own bounding box
# rather than on the frame makes the margin even on all four sides — the
# render sits low and left of centre in 05.jpg, and the shear moves it again.
box = ink_mask(im).getbbox()
if box is None:
    sys.exit("05.jpg looks blank")
x0, y0, x1, y1 = box
print("artwork bbox %s of %s" % (box, im.size))

side = max(w, int(max(x1 - x0, y1 - y0) * (1 + PAD * 2)))
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
print("square %dpx centred on the artwork at (%d,%d) -> margins L/R %d, T/B %d"
      % (side, cx, cy, (side - (x1 - x0)) // 2, (side - (y1 - y0)) // 2))
half = side // 2
canvas = Image.new("RGB", (side, side), (255, 255, 255))
src = (max(cx - half, 0), max(cy - half, 0), min(cx + half, im.width), min(cy + half, im.height))
canvas.paste(im.crop(src), (max(0, half - (cx - src[0])), max(0, half - (cy - src[1]))))
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
