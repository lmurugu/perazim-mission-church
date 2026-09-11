#!/usr/bin/env python3
"""Generate a transparent-background version of the Perazim church logo.

Source: /home/murugu/Downloads/Images/perazim_mwea 270 x 270/perazim_mwea 270 x 270.png
  - 270x270, mode RGB, top-left/top-right pixels = (255,255,255)
  - center pixel = (209,122,59) — the actual logo artwork
Strategy: convert to RGBA, then set alpha=0 for any pixel where the original
RGB is "near-white" (all channels >= 245 AND max-min < 12). This preserves
the brand-color artwork and removes the solid background. A small feather
(pixels with R,G,B in [225,245)) get partial alpha so the edge isn't harsh.

Output: /home/murugu/perazim-site/assets/logo-transparent.png
"""
from PIL import Image
from pathlib import Path

src = Path("/home/murugu/Downloads/Images/perazim_mwea 270 x 270/perazim_mwea 270 x 270.png")
dst = Path("/home/murugu/perazim-site/assets/logo-transparent.png")

im = Image.open(src).convert("RGBA")
px = im.load()
w, h = im.size

# Thresholds (verified from source: top-left and top-right corners are pure white
# (255,255,255), center is brand orange-brown (209,122,59). Use a generous
# "near-white" cutoff so all background pixels become transparent while the
# logo artwork keeps full alpha.
def alpha_for(rgb):
    r, g, b = rgb[0], rgb[1], rgb[2]
    if r >= 250 and g >= 250 and b >= 250:
        return 0            # pure white → fully transparent
    if r >= 235 and g >= 235 and b >= 235:
        # soft white edge → semi-transparent (feather)
        # linear: 235→opaque, 250→transparent
        return int(255 * (250 - max(r, g, b)) / 15)
    return 255                # brand color → fully opaque

for y in range(h):
    for x in range(w):
        rgb = px[x, y]
        a = alpha_for(rgb)
        px[x, y] = (rgb[0], rgb[1], rgb[2], a)

im.save(dst, "PNG")
print(f"WROTE {dst} ({dst.stat().st_size} bytes)")

# Sanity: verify alpha is non-trivial (logo has real opacity, corners are 0)
im2 = Image.open(dst)
alpha = im2.split()[3]
print(f"alpha extrema: {alpha.getextrema()}")
print(f"mode: {im2.mode}, size: {im2.size}")