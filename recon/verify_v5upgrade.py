#!/usr/bin/env python3
"""v5-upgrade verification — Dynamics & Motion Engine compliance.

Checks:
  1. CSS: keyframes, reveal-on-scroll, .scrolled nav, card hover, image zoom,
     shimmer ::after, button physics, watermark-text, ambient-float / -pulse
  2. JS: IntersectionObserver, scroll-nav handler, attachParallax helper,
     3D tilt, slider scrollBy, prefers-reduced-motion guard, theme toggle
     preserved (3-state cycle)
  3. HTML: watermark-text div in hero, ambient-float class on hero SVG,
     ambient-pulse class on values SVG
  4. v3/v4 preservation: brand tokens, theme tokens, logo-transparent, no fabrication
"""
import json, re, urllib.request
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
# 1. CSS — keyframes + motion utilities
# ============================================================
r["css_keyframes_ambientFloat"]  = "@keyframes ambientFloat" in css
r["css_keyframes_pulseGlow"]    = "@keyframes pulseGlow" in css
r["css_ambient_float_class"]    = ".ambient-float" in css and "animation: ambientFloat 9s ease-in-out infinite" in css
r["css_ambient_pulse_class"]    = ".ambient-pulse" in css and "animation: pulseGlow 6s ease-in-out infinite" in css
r["css_reveal_on_scroll_rule"]   = ".reveal-on-scroll {" in css and "opacity: 0" in css and "translateY(28px)" in css
r["css_reveal_is_revealed_rule"] = ".reveal-on-scroll.is-revealed" in css
r["css_stagger_1"]              = ".stagger-1" in css and "transition-delay: 0.1s" in css
r["css_stagger_2"]              = ".stagger-2" in css and "transition-delay: 0.2s" in css
r["css_stagger_3"]              = ".stagger-3" in css
r["css_stagger_4"]              = ".stagger-4" in css

# ============================================================
# 2. CSS — sticky navbar morph on scroll
# ============================================================
r["css_nav_scrolled_class"]   = ".nav-container.scrolled" in css
r["css_nav_scrolled_padding"] = "padding: 0.45rem 1.25rem" in css
r["css_nav_scrolled_blur20"]  = "backdrop-filter: blur(20px)" in css
r["css_nav_scrolled_boxshdw"] = "0 12px 30px -10px rgba(0, 0, 0, 0.08)" in css
r["css_dark_nav_scrolled"]    = '[data-theme="dark"] .nav-container.scrolled' in css

# ============================================================
# 3. CSS — card hover (campus + tilt + poster) + image zoom + shimmer
# ============================================================
r["css_card_hover_translate"]  = "transform: translateY(-6px)" in css
r["css_card_hover_boxshadow"] = "0 22px 45px -12px rgba(104, 26, 125, 0.15)" in css
r["css_card_hover_purple"]    = "border-color: var(--accent-purple)" in css
r["css_img_zoom_transition"]   = "transform: scale(1.08)" in css
r["css_shimmer_after_block"]  = ".campus-card::after, .values-section::after" in css
r["css_shimmer_hover_left"]   = ".campus-card:hover::after" in css and "left: 150%" in css

# ============================================================
# 4. CSS — button micro-physics
# ============================================================
r["css_btn_position_relative"] = ".btn {" in css and "position: relative" in css and "will-change: transform" in css
r["css_btn_hover_transform"]   = ".btn:hover" in css and "translateY(-2px) scale(1.02)" in css
r["css_btn_active_press"]      = ".btn:active" in css and "scale(0.98)" in css

# ============================================================
# 5. CSS — watermark text
# ============================================================
r["css_watermark_class"]      = ".watermark-text" in css
r["css_watermark_size"]       = "clamp(6rem, 18vw, 15rem)" in css
r["css_watermark_dark_stroke"] = "-webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.05)" in css
r["css_watermark_light_dark"]  = '[data-theme="light"] .watermark-text-dark' in css

# ============================================================
# 6. JS — IntersectionObserver scroll-reveal
# ============================================================
r["js_intersection_observer"]      = "IntersectionObserver" in js
r["js_intersection_observer_check"] = "'IntersectionObserver' in window" in js
r["js_reveal_targets_query"]       = ".hero-content, .section-header" in js
r["js_reveal_targets_value_item"]  = ".value-item" in js
r["js_reveal_classlist_add"]       = "classList.add('reveal-on-scroll')" in js
r["js_stagger_assignment"]         = "stagger-" in js
r["js_reveal_observer_unobserve"]  = "obs.unobserve(entry.target)" in js
r["js_is_revealed_class_add"]      = "classList.add('is-revealed')" in js
r["js_rootMargin_minus60"]         = "'0px 0px -60px 0px'" in js
r["js_threshold_012"]              = "threshold: 0.12" in js

# ============================================================
# 7. JS — sticky navbar morph
# ============================================================
r["js_scroll_y_40"]            = "scrollY > 40" in js
r["js_nav_scrolled_classlist"] = "classList.toggle('scrolled'" in js
r["js_scroll_passive_listener"] = "addEventListener('scroll'" in js and "passive: true" in js

# ============================================================
# 8. JS — attachParallax helper (hero + values)
# ============================================================
r["js_attach_parallax_fn"]    = "function attachParallax" in js
r["js_parallax_0045"]         = "0.045" in js  # hero intensity
r["js_parallax_0035"]         = "0.035" in js  # values intensity
r["js_parallax_translate3d"]  = "translate3d" in js
r["js_parallax_raf_throttle"]  = "requestAnimationFrame" in js

# ============================================================
# 9. JS — 3D tilt on tilt-card / campus-card
# ============================================================
r["js_tilt_query"]         = ".tilt-card, .campus-card" in js
r["js_tilt_perspective"]   = "perspective(1000px)" in js
r["js_tilt_rotateX_neg5"]  = "rotateX(" in js and "-5" in js
r["js_tilt_translate_y6"]  = "translateY(-6px)" in js
# The transform string is split across two lines — match the prefix.
r["js_tilt_mouseleave_reset"] = "card.style.transform =" in js and "rotateX(0deg)" in js and "translateY(0)" in js

# ============================================================
# 10. JS — slider prev/next
# ============================================================
r["js_slider_query"]   = "querySelector('.campus-grid')" in js
r["js_slider_scrollBy"] = "scrollBy" in js
r["js_slider_360"]     = "360" in js and ("-360" in js or "360" in js)

# ============================================================
# 11. JS — prefers-reduced-motion guard
# ============================================================
r["js_prefers_reduced_motion"] = "prefers-reduced-motion: reduce" in js or "prefersReduce" in js
r["js_reduced_motion_default"] = "prefersReduce" in js  # variable used as guard

# ============================================================
# 12. HTML — watermark + ambient-float + ambient-pulse injected
# ============================================================
r["html_watermark_text_in_hero"] = 'class="watermark-text"' in page and ">PERAZIM</div>" in page
r["html_ambient_float_on_hero_svg"] = 'class="hero-vector-layer ambient-float"' in page
r["html_ambient_pulse_on_values_svg"] = 'class="ambient-vector-bg ambient-pulse"' in page

# ============================================================
# 13. v3/v4 PRESERVATION (must not regress)
# ============================================================
r["v3_purple_token_kept"]      = "--accent-purple: #681A7D" in css
r["v3_orange_token_kept"]      = "--accent-orange: #E17D2F" in css
r["v4_dark_purple_lifted"]     = "--accent-purple: #9D4EDD" in css
r["v4_dark_orange_lifted"]     = "--accent-orange: #F09054" in css
r["v4_data_theme_auto_default"]= '<html lang="en" data-theme="auto">' in page
r["v4_no_flash_init_in_head"]  = "perazim-theme" in page and "localStorage.getItem" in page
r["v4_theme_toggle_3state"]    = "['light', 'dark', 'auto']" in js
r["v4_storage_event_sync"]     = "addEventListener('storage'" in js
r["logo_transparent_in_nav"]   = 'src="assets/logo-transparent.png"' in page
r["real_bishop_mutweri"]       = "Bishop Dr. David Mutweri" in page
r["real_youtube_video"]        = "3O6meSzCl3I" in page
r["no_rickroll"]               = "dQw4w9WgXcQ" not in page
r["no_fabricated_service_times"] = "9:00 AM" not in page and "11:30 AM" not in page
r["no_scraper_strings"]        = "Source: facebook.com" not in page and "Verified Data" not in page
r["no_court_strings"]          = "John Mureithi" not in page
r["no_unsplash_cdn"]           = "images.unsplash.com" not in page

# ============================================================
# 14. Asset reachability
# ============================================================
assets = ["/", "/assets/styles.css", "/assets/app.js",
          "/assets/logo-transparent.png", "/assets/favicon.png",
          "/assets/fb_photos_web/1.jpg", "/assets/fb_photos_web/2.jpg",
          "/assets/fb_photos_web/3.jpg", "/assets/fb_photos_web/4.jpg",
          "/assets/fb_photos_web/5.jpg", "/assets/church_cover_real.jpg"]
for a in assets:
    body = get(a)
    r["asset_" + a.split("/")[-1].replace(".", "_") or "root"] = (body != "__ERROR__")

# ============================================================
# Verdict (strict True check; numeric info fields excluded)
# ============================================================
total = len(r)
passed = sum(1 for k, v in r.items() if v is True)
r["__summary__"] = {"passed": passed, "total": total, "pct": round(100*passed/total, 1)}
_INFO_KEYS = {"logo_alpha_min", "logo_alpha_max"}
r["__failures__"] = [k for k, v in r.items() if v is not True and k not in _INFO_KEYS and not k.startswith("__")]

print(json.dumps(r, indent=2, default=str))

import sys
sys.exit(0 if passed == total else 1)