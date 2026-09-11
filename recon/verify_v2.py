#!/usr/bin/env python3
"""Stage D3 verification bundle against the local v2 build."""
import json, re, urllib.request, sys

BASE = "http://127.0.0.1:8090"
results = {}

def get(path):
    try:
        return urllib.request.urlopen(BASE + path, timeout=10).read().decode("utf-8", "replace")
    except Exception as e:
        return f"__ERROR__ {e}"

page = get("/index.html")

results["title_ok"] = "Perazim Mission Church" in page
results["gallery_images"] = len(re.findall(r"assets/gallery/gallery-\d{2}\.jpg", page))
results["gallery_11"] = results["gallery_images"] >= 11
results["favicon"] = "favicon.png" in page and "favicon.ico" in page
results["favicon_asset"] = get("/assets/favicon.png") != "__ERROR__"
results["bishop_mentions"] = len(re.findall(r"Bishop Dr David Mutweri", page))
results["pending_tags"] = len(re.findall(r"PENDING|pending", page))
results["rickroll"] = len(re.findall(r"dQw4w9WgXcQ", page))
results["real_video"] = "3O6meSzCl3I" in page
results["mutweri_facts"] = results["bishop_mentions"] >= 8
results["pending_kept"] = results["pending_tags"] >= 5
results["no_rickroll"] = results["rickroll"] == 0
# All required app.js ids present
required_ids = ["hero-badge","hero-title","hero-subtitle","hero-actions","visit-modal",
    "modal-step-1","modal-step-2","modal-step-3","sermon-grid","filter-topic","filter-search",
    "visit-form","visit-form-error","visit-mailto","confirmation-code","modal-close-btn",
    "btn-step-1-next","btn-step-2-back","guest-first-name","guest-last-name","guest-email",
    "guest-phone","guest-adults","visit-date","visit-service","btn-modal-done","hamburger","nav-menu"]
missing_ids = [i for i in required_ids if f'id="{i}"' not in page and f"id={i}" not in page and f'id=\'{i}\'' not in page]
results["all_ids"] = len(missing_ids) == 0
results["missing_ids"] = missing_ids
# assets reachable
for a in ["/assets/styles.css","/assets/app.js","/assets/sermons.json",
          "/assets/gallery/gallery-01.jpg","/assets/gallery/gallery-11.jpg",
          "/assets/church_cover_real.jpg","/assets/bishop_real.jpg","/assets/favicon.png"]:
    results["asset_" + a.split("/")[-1]] = get(a) != "__ERROR__"
# new palette tokens present
for tok in ["#fdf3e8","#aa6f45","#7a4a2e","#cf6a2e","#1c1712"]:
    results["palette_" + tok.replace("#","")] = tok in page or tok in get("/assets/styles.css")
# footer campus cards
results["campus_cards"] = page.count('class="campus"') >= 3
# legal note + honesty note preserved
results["legal_case"] = "John Mureithi Githinji v Thomas Ireri Ngai" in page
results["honesty_note"] = "david.murogo.1" in page and "not independently corroborated" in page
# Mwea/Rombo/Embu branches
results["branches"] = all(x in page for x in ["Embu HQ", "Mwea", "Rombo"])
# map
results["map"] = "openstreetmap.org/export/embed" in page

# verdict
checks = [
    ("title_ok", results["title_ok"]),
    ("gallery_11_photos", results["gallery_11"]),
    ("favicon", results["favicon"] and results["favicon_asset"]),
    ("mutweri_8plus", results["mutweri_facts"]),
    ("pending_kept", results["pending_kept"]),
    ("no_rickroll", results["no_rickroll"]),
    ("real_video", results["real_video"]),
    ("all_js_ids", results["all_ids"]),
    ("all_assets_200", all(results[k] for k in results if k.startswith("asset_"))),
    ("palette_tokens", all(results[k] for k in results if k.startswith("palette_"))),
    ("campus_cards", results["campus_cards"]),
    ("legal_case", results["legal_case"]),
    ("honesty_note", results["honesty_note"]),
    ("branches", results["branches"]),
    ("map", results["map"]),
]
results["ALL_OK"] = all(v for _, v in checks)
results["checks_passed"] = sum(1 for _, v in checks if v)
results["checks_total"] = len(checks)
results["check_breakdown"] = checks

print(json.dumps(results, indent=2, default=str))
sys.exit(0 if results["ALL_OK"] else 1)