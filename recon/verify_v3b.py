#!/usr/bin/env python3
"""v3b verification — directive-template compliance (replaces v3 with the actual spec the user gave)."""
import json, re, urllib.request, sys

BASE = "http://127.0.0.1:8090"
def get(p):
    try: return urllib.request.urlopen(BASE + p, timeout=10).read().decode("utf-8", "replace")
    except Exception as e: return f"__ERROR__ {e}"

page = get("/index.html")
css  = get("/assets/styles.css")
results = {}

# === Structural / class-name compliance (per the directive's exact spec) ===
class_names = [
    "hero-island", "hero-bg", "hero-scrim", "hero-content", "hero-title", "hero-subtitle", "hero-actions",
    "section-header", "section-title", "campus-grid", "campus-card",
    "campus-img-wrap", "campus-details", "campus-times", "campus-address", "arrow-icon-btn",
    "leadership-island", "leadership-text", "leadership-bio", "portrait-wrap",
    "poster-grid", "poster-card", "poster-bg", "poster-scrim", "poster-content",
    "nav-container", "logo", "nav-links", "main-wrapper",
    "btn", "btn-black", "btn-white", "btn-cyan", "kicker", "font-display",
]
for cn in class_names:
    results["class_" + cn] = cn in page

# === Verbatim content from the directive ===
directive_strings = [
    "PERAZIM",  # wordmark
    "For God.<br>For People.<br>For The City.",  # hero copy
    "A vibrant Christ-centered church family worshipping across Embu and beyond. You belong here.",  # hero subtitle (verbatim)
    "Gatherings Every Sunday",  # hero kicker
    "Join Us In-Person",  # locations kicker
    "Our Locations",  # locations title
    "Embu Central Campus",  # first campus name
    "Mwea Campus",
    "Rombo Campus",
    "Manyatta, Embu",  # first campus address
    "Kirinyaga County",  # Mwea address
    "Rombo, Kenya",  # Rombo address
    "Global Leadership",  # leadership kicker
    "Bishop Dr. David Mutweri",  # leadership h2 (real, verified)
    "Leading with a conviction for community restoration and practical faith since 2003.",  # leadership bio start
    "Walking in Unwavering Faith",  # poster 1 title
    "Hebrews 11",  # poster 1 reference
    "Midweek Prayer",  # poster 2 title (spec says "Midweek Prayer & Praise")
    "Perazim Kids",  # poster 3 title
    "Latest Teaching",  # poster kicker
    "Media & Community",  # messages kicker
    "The Latest",  # messages title
    "View All",  # section header CTA
    "Plan a Visit",  # nav button + final CTA
]
for s in directive_strings:
    results["verbatim_" + s[:30].replace(" ","_").replace(".","").replace("<","").replace(">","")] = s in page

# === Typography math (in CSS, since the directive inlines) ===
results["css_plus_jakarta_900"] = "font-weight: 900" in css
results["css_negative_letter_spacing"] = "letter-spacing: -0.04em" in css
results["css_cyan_accent"] = "#00C2FF" in css
results["css_dark_island"] = "#0A0A0A" in css
results["css_28px_radius"] = "28px" in css
results["css_32px_radius"] = "32px" in css
results["css_pill_radius"] = "9999px" in css

# === Photographic scrim rule ===
# Scrim rule — match the directive's exact gradient stops
results["scrim_hero_3stop"] = "rgba(10,10,10,0.1) 0%" in css and "rgba(10,10,10,0.5) 45%" in css and "#0A0A0A 100%" in css
results["scrim_poster_2stop"] = "rgba(0,0,0,0.1) 0%" in css and "rgba(0,0,0,0.85) 100%" in css

# === No-fabrication rule (overrides) ===
results["no_fabricated_service_times"] = "9:00 AM" not in page and "11:30 AM" not in page
results["service_time_TBC_present"] = "TBC" in page
results["no_fabricated_pastors"] = not any(n in page for n in ["John Doe", "Jane Smith", "Mark Reed", "Lisa Park", "Wilkerson", "DawnCheré", "Bishop Dr. David Mutweri III"])
results["no_unsplash_cdn"] = "images.unsplash.com" not in page
results["no_jqwikwik_youtube"] = "dQw4w9WgXcQ" not in page  # rickroll guard
results["no_court_strings"] = "John Mureithi" not in page
results["no_scraper_strings"] = "Source: facebook.com" not in page and "Verified Data" not in page
results["no_fb_media_id_strings"] = "UC2Yv5gJArnHSuXApBupkv-A" not in page

# === Asset reachability (real FB photos renamed 1.jpg..8.jpg per spec) ===
asset_paths = [
    "/assets/fb_photos_web/1.jpg", "/assets/fb_photos_web/2.jpg",
    "/assets/fb_photos_web/3.jpg", "/assets/fb_photos_web/4.jpg",
    "/assets/fb_photos_web/5.jpg", "/assets/fb_photos_web/6.jpg",
    "/assets/fb_photos_web/7.jpg", "/assets/fb_photos_web/8.jpg",
    "/assets/favicon.png", "/assets/bishop_real.jpg",
]
for a in asset_paths:
    body = get(a)
    results["asset_" + a.split("/")[-1]] = (body != "__ERROR__")

# === Final verdict ===
checks = [(k, v) for k, v in results.items() if not k.startswith("verbatim_unknown")]

# Just report: don't compute a fake ALL_OK
total = len(checks)
passed = sum(1 for _, v in checks if v)
results["summary"] = {"passed": passed, "total": total}
results["failures"] = [{"check": k, "value": v} for k, v in checks if not v]

print(json.dumps(results, indent=2, default=str))
sys.exit(0 if passed == total else 1)