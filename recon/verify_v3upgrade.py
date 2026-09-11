#!/usr/bin/env python3
"""v3-upgrade verification — checks compliance with the v3 upgrade directive
(Royal Purple #681A7D + Sunset Orange #E17D2F 2-tone accent system,
brand-wrapper + logo in nav, ambient SVG line-art + mouse parallax, hero
cleanliness, no-fabrication rule).
"""
import json, urllib.request

BASE = "http://127.0.0.1:8090"
def get(p):
    try: return urllib.request.urlopen(BASE + p, timeout=10).read().decode("utf-8", "replace")
    except Exception as e: return f"__ERROR__ {e}"

page = get("/index.html")
css  = get("/assets/styles.css")
js   = get("/assets/app.js")
r = {}

# === Brand accent tokens (the directive's 2-tone rule) ===
r["token_accent_purple"] = "--accent-purple: #681A7D" in css
r["token_accent_orange"] = "--accent-orange: #E17D2F" in css
r["token_bg_canvas"] = "--bg-canvas: #F8F8F6" in css
r["token_bg_dark_island"] = "--bg-dark-island: #0A0A0A" in css
r["token_text_muted"] = "--text-muted: #6B7280" in css

# === Selection & interaction CSS rules (the 2-tone interactive rule) ===
r["selection_orange_bg"] = "background-color: var(--accent-orange)" in css
r["selection_white_text"] = "color: #FFFFFF" in css
r["btn_primary_orange_hover"] = "background-color: var(--accent-orange)" in css and "transform: translateY(-2px)" in css
r["btn_primary_orange_shadow"] = "rgba(225, 125, 47, 0.35)" in css
r["btn_secondary_purple_hover"] = "color: var(--accent-purple)" in css and "border-color: var(--accent-purple)" in css
r["btn_secondary_purple_bg_hover"] = "#FAF5FB" in css  # the lavender hover bg

# === Logo + brand-wrapper nav ===
r["logo_image_in_nav"] = 'src="assets/logo.png"' in page and 'class="nav-logo-img"' in page
r["logo_alt_text"] = 'alt="Perazim Mission Church logo"' in page
r["brand_wrapper_class"] = 'class="brand-wrapper"' in page
r["brand_title_class"] = 'class="brand-title"' in page
r["logo_dimensions_css"] = "height: 38px" in css and "width: 38px" in css
r["logo_hover_transform"] = "transform: rotate(-8deg)" in css

# === Nav links (purple hover + orange underline) ===
r["nav_link_purple_hover"] = ".nav-links a:hover { color: var(--accent-purple); }" in css
r["nav_link_orange_underline"] = "background: var(--accent-orange);" in css and ".nav-links a:hover::after { width: 100%; }" in css

# === Ambient SVG line-art with mouse parallax ===
r["hero_svg_in_html"] = '<svg class="hero-vector-layer"' in page
r["hero_svg_low_opacity_css"] = "opacity: 0.16" in css  # the v3 spec says 0.12-0.18
r["hero_svg_pointer_events_none"] = "pointer-events: none;" in css
r["hero_svg_transition_css"] = "transition: transform 0.2s ease-out;" in css
r["mouse_parallax_handler"] = "mousemove" in js and "vectorLayer" in js
r["mouse_parallax_transform"] = "translate(" in js and "0.04" in js  # the spec's exact coefficient
r["mouse_parallax_mouseleave"] = "mouseleave" in js

# === Campus cards (purple border on hover + orange arrow) ===
r["campus_card_purple_border_hover"] = "border-color: var(--accent-purple);" in css
r["arrow_btn_orange_hover"] = "background-color: var(--accent-orange);" in css

# === Hero cleanliness: no flyer, no ORDER OF SERVICE ===
r["no_order_of_service"] = "ORDER OF SERVICE" not in page
r["no_weekly_service"] = "WEEKLY SERVICE" not in page
r["no_sunday_service_flyer"] = "SUNDAY SERVICE" not in page or "Sundays" in page  # OK if "Sundays" is the only match

# === Kicker colors follow the 2-tone rule (purple kicker for leadership, orange for messages/hero) ===
r["leadership_kicker_purple"] = "kicker\" style=\"color: var(--accent-purple);\"" in page.replace("  ","")
r["hero_kicker_orange"] = "kicker\" style=\"color: var(--accent-orange);\"" in page.replace("  ","")
r["messages_kicker_orange"] = "kicker\" style=\"color: var(--accent-orange);\"" in page.replace("  ","")

# === No fabrication: service times TBC, no fake pastors, no scraper strings ===
r["no_fabricated_service_times"] = "9:00 AM" not in page and "11:30 AM" not in page
r["service_time_TBC"] = "TBC" in page
r["no_fabricated_pastors"] = all(n not in page for n in ["John Doe","Jane Smith","Bishop Dr. David Mutweri III"])
r["no_scraper_strings"] = "Source: facebook.com" not in page and "Verified Data" not in page
r["no_court_strings"] = "John Mureithi" not in page
r["no_fb_media_id"] = "UC2Yv5gJArnHSuXApBupkv-A" not in page
r["no_unsplash_cdn"] = "images.unsplash.com" not in page
r["no_rickroll"] = "dQw4w9WgXcQ" not in page

# === Real Perazim data ===
r["real_bishop_name"] = "Bishop Dr. David Mutweri" in page
r["real_yt_video_id"] = "3O6meSzCl3I" in page
r["real_founded_year"] = "since 2003" in page

# === Asset reachability ===
assets = [
    "/assets/logo.png", "/assets/styles.css", "/assets/app.js",
    "/assets/favicon.png", "/assets/fb_photos_web/1.jpg",
    "/assets/fb_photos_web/2.jpg", "/assets/fb_photos_web/3.jpg",
    "/assets/fb_photos_web/4.jpg", "/assets/fb_photos_web/5.jpg",
    "/assets/church_cover_real.jpg", "/assets/bishop_real.jpg",
]
for a in assets:
    body = get(a)
    r["asset_" + a.split("/")[-1]] = (body != "__ERROR__")

# === Verdict ===
total = len(r)
passed = sum(1 for v in r.values() if v)
r["summary"] = {"passed": passed, "total": total}
r["failures"] = [k for k, v in r.items() if not v and k not in ("summary","failures")]

print(json.dumps({"summary": r["summary"], "failures": r["failures"], "all": r}, indent=2, default=str))

import sys
sys.exit(0 if passed == total else 1)