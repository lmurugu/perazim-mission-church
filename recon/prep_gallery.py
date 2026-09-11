#!/usr/bin/env python3
"""Stage D prep — copy 11 web-optimized FB photos to assets/gallery/ with clean names + provenance JSON.
Fully local (no VPS writes)."""
import json, os, shutil
from pathlib import Path

BASE = Path("/home/murugu/perazim-site")
SRC = BASE / "assets/fb_photos_web"
DST = BASE / "assets/gallery"
DST.mkdir(exist_ok=True)

# Map of real files (web-opt) → clean gallery names. Provenance: FB media_id encoded in filename where known.
# The web-opt names encode their source resolution; source = facebook.com/perazim.missioncentre public posts (2026-09-01 harvest).
files = sorted(SRC.glob("real_*.jpg"))
print(f"found {len(files)} web-opt photos")

manifest = []
for i, f in enumerate(files, 1):
    clean = f"gallery-{i:02d}.jpg"
    shutil.copy2(f, DST / clean)
    manifest.append({
        "file": clean,
        "source_file": f.name,
        "source": "facebook.com/perazim.missioncentre (public page photos, anonymous crawler harvest 2026-09-01)",
        "size_bytes": (DST / clean).stat().st_size,
        "caption_hint": "",
    })
    print(f"  {clean} <- {f.name} ({(DST / clean).stat().st_size} B)")

with open(BASE / "assets" / "gallery_manifest.json", "w") as fh:
    json.dump({"schema": "perazim-gallery-v1", "count": len(manifest), "photos": manifest}, fh, indent=2)
print(f"WROTE gallery_manifest.json ({len(manifest)} photos)")

# Favicon: build a 32x32 (and 64x64) P-monogram PNG via PIL from the palette.
try:
    from PIL import Image, ImageDraw, ImageFont
    for size in (32, 64):
        img = Image.new("RGBA", (size, size), (253, 243, 232, 255))  # cream bg
        d = ImageDraw.Draw(img)
        # rounded square primary-dark
        margin = size // 8
        d.rounded_rectangle([margin, margin, size - margin, size - margin],
                            radius=size // 5, fill=(122, 74, 46, 255))  # #7a4a2e
        # letter P in white, centered
        try:
            font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", int(size * 0.55))
        except Exception:
            font = ImageFont.load_default()
        bbox = d.textbbox((0, 0), "P", font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), "P",
               font=font, fill=(255, 255, 255, 255))
        out = BASE / "assets" / (f"favicon-{size}.png" if size < 64 else "favicon.png")
        img.save(out, "PNG")
        print(f"  favicon: {out} ({size}x{size})")
    # ico: PIL can't do ico; serve favicon.png + also copy as favicon.ico (PNG-in-ico is fine for modern browsers)
    shutil.copy2(BASE / "assets" / "favicon.png", BASE / "assets" / "favicon.ico")
    print("  favicon.ico = PNG copy (modern browsers accept)")
except ImportError as e:
    print("  PIL unavailable — favicon will be inline SVG data-URI in HTML")
except Exception as e:
    print(f"  favicon build FAILED: {e}")