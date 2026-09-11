#!/usr/bin/env python3
"""Stage C — WCAG contrast gate battery for proposed Perazim v2 tokens."""
import subprocess, json, sys, re
from pathlib import Path

SCRIPT = "/home/murugu/.hermes/skills/design-tastemaker/scripts/check_contrast.py"

# Token candidates (from palette extraction + plan C4 rules)
pairs = [
    # (label, fg, bg, required_ratio, role)
    ("primary-dark on bg",   "#7a4a2e", "#fdf3e8", 4.5, "primary text/dark buttons on cream bg"),
    ("ink on bg",            "#1c1712", "#fdf3e8", 4.5, "body text on cream bg"),
    ("ink on surface",       "#1c1712", "#ffffff", 4.5, "body text on white cards"),
    ("white on primary",     "#ffffff", "#aa6f45", 4.5, "white text on primary button"),
    ("primary on bg",        "#aa6f45", "#fdf3e8", 3.0, "primary as LARGE text/decorative on bg (AA large)"),
    ("accent-orange on bg",  "#df7d39", "#fdf3e8", 3.0, "accent decorative on bg (AA large only)"),
    ("purple on bg",         "#8029a9", "#fdf3e8", 3.0, "purple decorative/leadership (AA large only)"),
    ("primary-dark on surface", "#7a4a2e", "#ffffff", 4.5, "primary-dark text on white surface"),
]

def run(fg, bg):
    r = subprocess.run(["python3", SCRIPT, fg, bg], capture_output=True, text=True)
    out = r.stdout
    m = re.search(r"Contrast ratio:\s*([\d.]+)", out)
    ratio = float(m.group(1)) if m else None
    return r.returncode, ratio, out

results = []
for label, fg, bg, need, role in pairs:
    rc, ratio, out = run(fg, bg)
    ok = ratio is not None and ratio >= need
    results.append({"label": label, "fg": fg, "bg": bg, "need": need, "ratio": ratio, "PASS": ok, "role": role})
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: {ratio} (need >= {need}) — {role}")

fails = [r for r in results if not r["PASS"]]
print()
print(f"TOTAL: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILURES:")
    for f in fails:
        print(f"  - {f['label']} {f['fg']} on {f['bg']} = {f['ratio']} (need {f['need']})")
else:
    print("ALL GATES PASS")

with open("/home/murugu/perazim-site/recon/contrast_gates.json", "w") as f:
    json.dump({"results": results, "all_pass": not fails}, f, indent=2)
print("WROTE /home/murugu/perazim-site/recon/contrast_gates.json")