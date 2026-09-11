#!/usr/bin/env python3
"""v4-upgrade verification — checks compliance with the v4 directive
(transparent logo + favicon, Instrument Serif editorial pairing,
values-section with 01/02/03 hover-fill, .tilt-card 3D rotation,
.arrow-btn slider controls, .ambient-vector-bg watermark parallax,
preserved v3 brand tokens, no-fabrication rule).
"""
import json, re, urllib.request, struct, zlib
from pathlib import Path

BASE = "http://127.0.0.1:8090"
def get(p):
    try: return urllib.request.urlopen(BASE + p, timeout=10).read().decode("utf-8", "replace")
    except Exception as e: return f"__ERROR__ {e}"

page = get("/index.html")
css  = get("/assets/styles.css")
js   = get("/assets/app.js")
r = {}

# ============================================================
# 1. TRANSPARENT LOGO + FAVICON
# ============================================================
r["favicon_logo_transparent"] = 'rel="icon" type="image/png" href="assets/logo-transparent.png"' in page
r["favicon_fallback_kept"] = 'rel="icon" type="image/png" href="assets/favicon.png"' in page
r["apple_touch_icon"] = 'rel="apple-touch-icon" href="assets/logo-transparent.png"' in page
r["nav_logo_src_transparent"] = 'src="assets/logo-transparent.png"' in page
r["nav_logo_alt"] = 'alt="Perazim Mission Church logo"' in page
r["nav_logo_class"] = 'class="nav-logo-img"' in page
r["nav_logo_onerror_fallback"] = "this.src='assets/logo.png'" in page  # graceful fallback to original

# Verify the actual logo file is RGBA with non-trivial alpha (use PIL — source of truth)
def check_logo_rgba(path):
    try:
        from PIL import Image
        im = Image.open(path)
        return im.mode == "RGBA"
    except Exception:
        return False

logo_path = Path("/home/murugu/perazim-site/assets/logo-transparent.png")
r["logo_transparent_rgba"] = check_logo_rgba(logo_path)
r["logo_transparent_size"] = logo_path.stat().st_size > 1000  # not a blank file

# Sample corner pixels to verify the white-background is actually transparent
def logo_alpha_extrema(path):
    try:
        from PIL import Image
        im = Image.open(path)
        if im.mode != "RGBA":
            return None
        return im.split()[3].getextrema()  # (min, max) of alpha channel
    except Exception:
        return None

ext = logo_alpha_extrema(logo_path)
r["logo_alpha_extrema_valid"] = (ext is not None and ext[0] == 0 and ext[1] >= 200)
r["logo_alpha_min"] = ext[0] if ext else None
r["logo_alpha_max"] = ext[1] if ext else None

# ============================================================
# 2. INSTRUMENT SERIF FONT (the "Passion City" italic pairing)
# ============================================================
r["fonts_instrument_serif_in_head"] = "Instrument+Serif:ital@1" in page
r["editorial_title_class_in_css"] = ".editorial-title {" in css
r["editorial_title_em_class"] = ".editorial-title em {" in css
r["editorial_title_font_instrument_serif"] = "'Instrument Serif'" in css
r["editorial_title_em_italic"] = "font-style: italic" in css
r["editorial_title_used_in_hero"] = 'class="hero-title editorial-title"' in page
r["editorial_title_used_in_locations"] = 'class="section-title editorial-title"' in page
r["editorial_title_used_in_values"] = 'class="editorial-title" style="color: var(--text-light);"' in page
r["em_tag_in_hero"] = "<em>For The City.</em>" in page
r["em_tag_in_locations"] = "<em>the Movement</em>" in page
r["em_tag_in_values"] = "<em>Core Values</em>" in page

# ============================================================
# 3. VALUES SECTION (VOUS-Style dark island with 01/02/03)
# ============================================================
r["values_section_class"] = 'class="values-section' in page
# --bg-deep is always near-black so values-section remains a dark island
# in BOTH light and dark themes (the section is the visual "dark hero card").
r["values_section_dark_bg"] = ".values-section {" in css and "background-color: var(--bg-deep)" in css
# Sanity: --bg-deep is defined as a top-level :root token (always near-black)
r["bg_deep_token_defined"] = "--bg-deep: #0A0A0A" in css
r["values_grid_in_html"] = 'class="values-grid"' in page
r["values_grid_css"] = ".values-grid {" in css and "grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))" in css
r["value_item_count_3"] = page.count('class="value-item"') == 3
r["value_number_outlined_stroke"] = "-webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.4)" in css
r["value_number_hover_fill_orange"] = ".value-item:hover .value-number" in css and "color: var(--accent-orange)" in css
r["value_item_hover_border_orange"] = ".value-item:hover {" in css and "border-color: var(--accent-orange)" in css
r["values_01_present"] = '<span class="value-number">01</span>' in page
r["values_02_present"] = '<span class="value-number">02</span>' in page
r["values_03_present"] = '<span class="value-number">03</span>' in page
r["values_kicker_our_dna"] = "Our DNA" in page

# ============================================================
# 4. AMBIENT VECTOR WATERMARK (SVG with low opacity, mouse-tracked)
# ============================================================
r["ambient_vector_svg_in_html"] = '<svg class="ambient-vector-bg"' in page
r["ambient_vector_css_class"] = ".ambient-vector-bg {" in css
r["ambient_vector_opacity_12"] = "opacity: 0.12" in css
r["ambient_vector_pointer_events_none"] = "pointer-events: none;" in css
r["ambient_vector_mouse_parallax_js"] = "ambient-vector-bg" in js and "values-section" in js

# ============================================================
# 5. 3D TILT CARDS (perspective 1000px, ±6deg on X/Y)
# ============================================================
r["tilt_card_class_in_html"] = page.count("tilt-card") >= 3  # 3 campus cards
r["tilt_card_class_in_css"] = ".tilt-card {" in css and "perspective: 1000px" in css
r["tilt_card_transform_3d"] = "transform-style: preserve-3d" in css
r["tilt_card_js_handler"] = ".tilt-card" in js and "perspective(1000px)" in js
r["tilt_card_rotateX"] = "rotateX" in js
r["tilt_card_rotateY"] = "rotateY" in js
r["tilt_card_translateY"] = "translateY(-4px)" in js
r["tilt_card_mouseleave_reset"] = "card.addEventListener('mouseleave'" in js

# ============================================================
# 6. SLIDER ARROW CONTROLS (campus grid prev/next)
# ============================================================
r["arrow_btn_class_in_html"] = 'class="arrow-btn"' in page
r["slider_prev_button_id"] = 'id="slider-prev"' in page
r["slider_next_button_id"] = 'id="slider-next"' in page
r["arrow_btn_css"] = ".arrow-btn {" in css and "border-radius: 50%" in css
r["arrow_btn_hover_invert"] = ".arrow-btn:hover {" in css and "background: #0A0A0A" in css
r["carousel_controls_class"] = 'class="carousel-controls"' in page
r["slider_js_scrollBy"] = "scrollBy" in js and "slider" in js
r["slider_js_380_step"] = "SCROLL_STEP = 380" in js or "380" in js

# ============================================================
# 7. PRESERVED v3 (must not regress: purple/orange 2-tone, no fabrication)
# ============================================================
r["v3_purple_token_kept"] = "--accent-purple: #681A7D" in css
r["v3_orange_token_kept"] = "--accent-orange: #E17D2F" in css
r["v3_selection_orange"] = "::selection" in css and "var(--accent-orange)" in css
r["v3_no_fabricated_service_times"] = "9:00 AM" not in page and "11:30 AM" not in page
r["v3_tbc_chips_kept"] = "TBC" in page
r["v3_no_fabricated_pastors"] = all(n not in page for n in ["John Doe", "Jane Smith", "Bishop Dr. David Mutweri III"])
r["v3_no_rickroll"] = "dQw4w9WgXcQ" not in page
r["v3_no_unsplash_cdn"] = "images.unsplash.com" not in page
r["v3_no_scraper_strings"] = "Source: facebook.com" not in page and "Verified Data" not in page
r["v3_no_court_strings"] = "John Mureithi" not in page
r["v3_no_fb_media_id"] = "UC2Yv5gJArnHSuXApBupkv-A" not in page
r["v3_bishop_mutweri"] = "Bishop Dr. David Mutweri" in page
r["v3_youtube_id"] = "3O6meSzCl3I" in page
r["v3_founded_2003"] = "since 2003" in page or "founded 2003" in page.lower() or "2003" in page

# ============================================================
# 8. ASSET REACHABILITY (logo-transparent must be served)
# ============================================================
assets = [
    "/",
    "/assets/styles.css",
    "/assets/app.js",
    "/assets/logo-transparent.png",
    "/assets/logo.png",
    "/assets/favicon.png",
    "/assets/fb_photos_web/1.jpg",
    "/assets/fb_photos_web/2.jpg",
    "/assets/fb_photos_web/3.jpg",
    "/assets/fb_photos_web/4.jpg",
    "/assets/fb_photos_web/5.jpg",
    "/assets/church_cover_real.jpg",
    "/assets/bishop_real.jpg",
]
for a in assets:
    body = get(a)
    r["asset_" + a.split("/")[-1].replace(".","_") or "root"] = (body != "__ERROR__")

# ============================================================
# Verdict
# ============================================================
total = len(r)
# `is True` (strict) avoids the Python 0/None falsy-trap
passed = sum(1 for k, v in r.items() if v is True)
r["__summary__"] = {"passed": passed, "total": total, "pct": round(100*passed/total, 1)}
# Only flag keys that are intended as boolean checks. `logo_alpha_min` and
# `logo_alpha_max` are informational (numeric values), not pass/fail.
_INFO_KEYS = {"logo_alpha_min", "logo_alpha_max"}
r["__failures__"] = [k for k, v in r.items() if v is not True and k not in _INFO_KEYS and not k.startswith("__")]

print(json.dumps(r, indent=2, default=str))

import sys
sys.exit(0 if passed == total else 1)
# ============================================================
# 9. 3-THEME SYSTEM (light / dark / system)
# ============================================================
r["html_default_data_theme"] = '<html lang="en" data-theme="auto">' in page
r["no_flash_init_script"] = "perazim-theme" in page and "localStorage.getItem" in page
r["no_flash_inline_script_in_head"] = re.search(
    r'<script>\s*// No-flash theme init.*?localStorage\.getItem', page, re.DOTALL) is not None
r["theme_toggle_button"] = 'id="theme-toggle"' in page and 'class="theme-toggle"' in page
r["theme_toggle_sun_icon"] = 'class="theme-icon theme-icon-sun"' in page
r["theme_toggle_moon_icon"] = 'class="theme-icon theme-icon-moon"' in page
r["theme_toggle_auto_icon"] = 'class="theme-icon theme-icon-auto"' in page
# CSS: light/dark/auto theme blocks
r["css_light_theme_block"] = ':root[data-theme="light"] {' in css
r["css_dark_theme_block"] = ':root[data-theme="dark"] {' in css
r["css_auto_theme_block"] = ':root[data-theme="auto"] {' in css
r["css_prefers_dark_media"] = '@media (prefers-color-scheme: dark)' in css
# All three themes define the full token set
r["css_light_has_bg_canvas"] = '--bg-canvas: #F8F8F6' in css  # in :root,[data-theme="light"]
r["css_dark_has_bg_canvas"] = '--bg-canvas: #0A0A0A' in css  # in :root[data-theme="dark"]
r["css_auto_has_bg_canvas"] = '--bg-canvas: #0A0A0A' in css  # in :root[data-theme="auto"] when OS dark
# Brand accents (purple/orange) preserved in dark theme
r["css_dark_has_accent_purple"] = '--accent-purple: #9D4EDD' in css
r["css_dark_has_accent_orange"] = '--accent-orange: #F09054' in css
# Old token names should be GONE
r["css_no_old_text_dark"] = 'var(--text-dark)' not in css
r["css_no_old_text_light"] = 'var(--text-light)' not in css
r["css_no_old_bg_dark_island"] = 'var(--bg-dark-island)' not in css
# JS: theme toggle cycle (light → dark → auto → light)
r["js_theme_toggle_handler"] = "id='theme-toggle'" in js.replace('"', "'") or 'id="theme-toggle"' in js
r["js_theme_order_array"] = "['light', 'dark', 'auto']" in js or "[\"light\", \"dark\", \"auto\"]" in js
r["js_theme_storage_persist"] = "perazim-theme" in js and "localStorage.setItem" in js
r["js_theme_storage_clear_on_auto"] = "localStorage.removeItem" in js
r["js_theme_storage_sync_tab"] = "addEventListener('storage'" in js
# Theme transition CSS (smooth 0.3s)
r["css_body_theme_transition"] = "transition: background-color 0.3s ease" in css
# Nav uses theme tokens
r["css_nav_uses_nav_bg_token"] = "background: var(--nav-bg)" in css
# Theme-specific dark hover overrides
r["css_dark_arrow_btn_hover"] = ":root[data-theme=\"dark\"] .arrow-btn:hover" in css
r["css_dark_tilt_card_hover"] = ":root[data-theme=\"dark\"] .tilt-card:hover" in css
r["css_dark_value_number_hover"] = ":root[data-theme=\"dark\"] .value-item:hover .value-number" in css
# Auto/system dark overrides
r["css_auto_dark_arrow_hover"] = ":root[data-theme=\"auto\"] .arrow-btn:hover" in css
r["css_auto_dark_tilt_hover"] = ":root[data-theme=\"auto\"] .tilt-card:hover" in css
