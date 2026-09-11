#!/usr/bin/env python3
"""Verify the two FAILURE fixes: white-on-primary-dark for buttons, and darkened accent orange."""
import subprocess, re, json
from pathlib import Path

SCRIPT = "/home/murugu/.hermes/skills/design-tastemaker/scripts/check_contrast.py"

def ratio(fg, bg):
    r = subprocess.run(["python3", SCRIPT, fg, bg], capture_output=True, text=True)
    m = re.search(r"Contrast ratio:\s*([\d.]+)", r.stdout)
    return float(m.group(1)) if m else None

checks = [
    # fix 1: white on the darkened primary for buttons
    ("white on #7a4a2e (button bg)", "#ffffff", "#7a4a2e", 4.5),
    # fix 2: find darkest accent-orange that passes >=3.0 on cream
    ("accent #cf6a2e on bg", "#cf6a2e", "#fdf3e8", 3.0),
    ("accent #c8642a on bg", "#c8642a", "#fdf3e8", 3.0),
    ("accent #c05c22 on bg", "#c05c22", "#fdf3e8", 3.0),
]
out = []
for label, fg, bg, need in checks:
    r = ratio(fg, bg)
    ok = r is not None and r >= need
    out.append({"label": label, "fg": fg, "bg": bg, "need": need, "ratio": r, "PASS": ok})
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {r} (need {need})")
    if ok and "button" in label:
        print("    ^ use #7a4a2e as BUTTON background")
    if ok and "accent #" in label.replace("accent #",""):
        pass

with open("/home/murugu/perazim-site/recon/contrast_fixes.json", "w") as f:
    json.dump(out, f, indent=2)
print("WROTE /home/murugu/perazim-site/recon/contrast_fixes.json")