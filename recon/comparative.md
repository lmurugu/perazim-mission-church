# Church-Web Design Comparative — synthesis of 4 benchmark sites

**Date:** 2026-09-01 · **Method:** Prometheus scrape_intent (tier-1 HTML, real rendered output) + landing-scrape IA. Argus attempted first (returned title-only — insufficient), browser_exec unavailable (no Chromium default). Recon files: recon-vous.md, recon-passion.md, recon-mariners.md; recon-elevation.md BLOCKED (tier-5 halt, bot protection) — Elevation IA taken from its 297KB landing scrape + known URL structure.

---

## Per-pattern comparison

| Pattern | VOUS Church | Passion City | Mariners | Elevation (IA only) | **Perazim v2 adoption** |
|---|---|---|---|---|---|
| **Hero** | Video-led, h1 = current sermon title ("Don't Let The Stutter Stop You"), 10 videos on home | Statement hero + "Our Leadership" h1 on about | Mission-statement h1: "Inspiring people to follow Jesus and fearlessly change the world" | Vod/sermon-led "On Demand" hero | **Photo-led hero over warm gradient** (church_cover_real.jpg @ ~55% opacity) with mission tagline + 2 CTAs (Plan Your Visit / Watch Sermons). Keeps dynamic EAT service-window badge. |
| **Nav** | Visit VOUS · Sermons · Crews · Vision · Give (5 items) | About · Atlanta · Washington DC · Give · Locations (5-7) | Locations (10-campus mega-menu) · Watch · Join a Group · Plan a Visit · Give | About · Connect · eGroups · eKids · eTeams · Events · Giving · Locations · Outreach · Sermons (10+) | 7 items: About · Beliefs · Branches · **Gallery** · Sermons · Visit · Connect. (Fitts/Hick: ≤7.) |
| **Primary CTA** | "Give" (top-right, high-contrast) | "Give" + "Join Our Team" | "Watch" + "Plan a Visit" + "Give" | "Giving" + "Locations" | **"Plan Your Visit"** (primary, primary-dark #7a4a2e bg, white text) in hero; "Watch Sermons" secondary. Bold "Give"-link in footer (no giving flow — out of scope). |
| **Growth funnel** | Growth Track (4-step cards), VOUS Care | Join Our Team, Returning Givers | Plan a Visit page, Join a Group, Sign Up To Volunteer | eGroups (Sermon Discussion), eTeams, Outreach | **Plan-a-Visit 3-step modal** (already built) front-and-center + Branches cards (Embu/Mwea/Rombo). |
| **Sermon/Media grid** | Blog cards (54 imgs), Watch page | Events "Upcoming" list | Stories / Channels cards | /sermons with per-sermon slugs + Playlists | **Sermon Hub filter grid** (already built, 1 real video, empty-state) + **NEW photo gallery grid** (11 web-opt FB photos). |
| **Footer** | ? (below truncation) | Email signup ("Stay up to date with Passion") + links | **Campus cards: full address + service times** (Sun 10/11:30a/1p; Thu 7p) + email signup | Links + apps | **Campus cards for Embu/Mwea/Rombo** (address-level where verified, "PENDING" where not) + email-signup strip (mailto fallback) + social + verified legal-note. |
| **Color mood** | Dark-on-light, editorial, warm neutrals | Warm white + coral/red accents | Navy + white, clean | Dark theme + purple accent | **Flora palette from REAL photos**: cream bg (#fdf3e8), warm gold-brown primary (#aa6f45), dark-brown buttons (#7a4a2e), burnt-orange accent (#cf6a2e), deep-purple clergy accent (#8029a9) — all WCAG-passed. |
| **Typography** | Editorial sans + large display | Display serif/sans mix | Sans, strong 700 weights, tight tracking | Sans + serif display | **Cormorant Garamond display + Inter body** (existing pairing, kept) over token-based scale (display 56/32/24/16/13 captions). |
| **Mobile menu** | Hamburger (implied Webflow) | Hamburger | Hamburger | Hamburger + app links | **CSS-only hamburger** toggling nav (10 lines) |

---

## 3 concrete adoptions (non-negotiable for v2)

1. **Elevation-style sermon/multimedia presence** → keep Sermon Hub with the verified real video + stripe the YouTube subscribe CTA; gallery grid carries the visual weight.
2. **Mariners-style visit funnel** → "Plan a Visit" is the #1 CTA everywhere (hero, nav-adjacent, visit section button); modal is 3 steps, saves locally + mailto fallback.
3. **Mariners-style footer campus cards** → Embu HQ / Mwea / Rombo cards with the verified facts and PENDING labels where data missing (street, phone, times), plus the email-signup strip and social row.

---

## What we deliberately do NOT copy (honest)

- **VOUS/Passion/Elevation "Give" dominance** — no giving/backend in scope (out of Perazim scope for now; footer link placeholder only).
- **Multi-campus mega-menu** (10+ items) — Perazim has 3 confirmed branches; a 3-card grid beats a mega-menu.
- **Elevation's dark theme** — church photos + Kenya sunlight favor light, warm; verified palette is light-dominant (82% white in cover).
- **Any blocked content** — Elevation detail pages were bot-walled; NOT reconstructed from memory. Adoptions above lean on the 3 fully-recon'd sites + Elevation's public IA.