#!/usr/bin/env python3
"""Stage C — extract palette from Perazim real photos (local). Writes /home/murugu/perazim-site/recon/palette_combined.json"""
import json, subprocess, sys
from pathlib import Path

SCRIPT = "/home/murugu/.hermes/skills/design-tastemaker/scripts/extract_palette.py"
ASSETS = Path("/home/murugu/perazim-site/assets")

targets = [
    ("cover",       ASSETS / "church_cover_real.jpg", 8),
    ("gallery-01",  ASSETS / "fb_photos_web" / "real_1364x1364_e56f1701.jpg", 5),
    ("gallery-02",  ASSETS / "fb_photos_web" / "real_1365x1365_02f344e4.jpg", 5),
    ("gallery-03",  ASSETS / "fb_photos_web" / "real_2048x1886_a534b21f.jpg", 5),
    ("bishop",      ASSETS / "bishop_real.jpg", 5),
]

out = {}
for label, path, n in targets:
    if not path.exists():
        print(f"  MISSING {label}: {path}")
        continue
    r = subprocess.run(["python3", SCRIPT, str(path), "--n", str(n), "--json"],
                       capture_output=True, text=True, cwd="/home/murugu")
    try:
        data = json.loads(r.stdout.strip().split("\n")[-1])
        out[label] = data
        print(f"  {label}: " + ", ".join(f"{c['hex']}({c['pct']}%)" for c in data[:5]))
    except Exception as e:
        print(f"  FAIL {label}: {e} | {r.stderr[:150]}")

with open("/home/murugu/perazim-site/recon/palette_combined.json", "w") as f:
    json.dump(out, f, indent=2)
print("WROTE /home/murugu/perazim-site/recon/palette_combined.json")