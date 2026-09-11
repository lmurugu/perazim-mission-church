# Perazim Mission Church — Official Website

[![Status](https://img.shields.io/badge/status-production--ready-success.svg)](https://github.com/lmurugu/perazim-mission-church)
[![Tests](https://img.shields.io/badge/verification-86%2F86%20passing-brightgreen.svg)](recon/verify_v5upgrade.py)
[![Design Standard](https://img.shields.io/badge/design-VOUS%20%7C%20Passion%20City%20Standard-blueviolet.svg)](#design-system--visual-standard)
[![Data Policy](https://img.shields.io/badge/data%20integrity-zero%20fabrication-blue.svg)](#data-integrity-policy)

The official web platform for **Perazim Mission Church (PMC)**, headquartered in Embu, Kenya under the spiritual leadership of Bishop Dr. David Mutweri. 

Built with an editorial aesthetic influenced by premier global church platforms (VOUS Church, Passion City, Mariners Church), featuring native CSS motion dynamics, a 3-state theme engine (Light / Dark / System Auto), and strict adherence to verified real church media and leadership records.

---

## Table of Contents

- [Site Architecture](#site-architecture)
- [Design System & Visual Standard](#design-system--visual-standard)
- [Trending Features & Content Strategy (September 2026)](#trending-features--content-strategy-september-2026)
- [Data Integrity Policy](#data-integrity-policy)
- [Directory Structure](#directory-structure)
- [Automated Verification & Quality Gates](#automated-verification--quality-gates)
- [Local Development & Preview](#local-development--preview)
- [Deployment Guide](#deployment-guide)
- [Contributing](#contributing)
- [License](#license)

---

## Site Architecture

The project is structured as a multi-page web application optimized for fast static delivery, zero framework overhead, and complete cross-device accessibility.

| Route | Page | Purpose | Verified Assets |
|---|---|---|---|
| `/` | **Home** | Editorial landing page, hero island, core values, campus carousel, mission statement | Real cover photo, transparent vector mark, bishop portrait |
| `/sermons/` | **Sermons Archive** | Curated catalog of messages, seminars, and teachings | Real YouTube embed (`3O6meSzCl3I`) & metadata |
| `/visit/` | **Plan a Visit** | Guest registration funnel, campus directions, service guidelines | Real Embu location coordinates, honest PENDING schedule flags |
| `/about/` | **About PMC** | History, vision, episcopal leadership, and regional assemblies | Bishop Dr. David Mutweri biography & branch directory |
| `/contact/` | **Contact Channels** | Community communication links, prayer requests, social channels | Official Facebook page, YouTube channel, direct inquiry form |
| `/hymns/` | **Hymns Library** | Public domain hymnbook with lyrics & traditional translations | Classical hymns & verified seminar recordings |
| `/riddles/` | **Faith Riddles** | Family & youth biblical trivia and engagement questions | Scripture-backed study notes |
| `/jokes/` | **Christian Humor** | Wholesome, uplifting fellowship stories and clean wit | Community-curated clean humor |
| `/news/` | **Ministry News** | Community outreach updates, regional conferences, mission digests | Embu headquarters & regional branch announcements |

---

## Design System & Visual Standard

### 1. Typography Hierarchy
- **Display Headlines**: `Plus Jakarta Sans` (Weight: 900) — Bold, high-energy modern sans-serif.
- **Editorial Sub-headings & Accents**: `Instrument Serif` (Style: Italic) — Sophisticated human warmth reminiscent of modern editorial publications.
- **Body & Interface**: Inter / System UI Sans-serif — Highly legible across high-DPI displays.

### 2. Color System & Design Tokens
```css
:root {
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-accent-purple: #7c3aed;  /* Interactive accent */
  --color-accent-orange: #ea580c;  /* Warm highlight */
  --color-border: #e2e8f0;
}

[data-theme="dark"] {
  --color-bg: #090d16;
  --color-surface: #111827;
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-border: #1e293b;
}
```

### 3. Motion & Micro-Interactions
- **Ambient Vector Float**: Floating SVG ambient orbs with subtle keyframe breathing animations.
- **Scroll Reveal**: Native `IntersectionObserver` with staggered cubic-bezier entrance transitions.
- **Perspective 3D Tilt**: Hardware-accelerated 3D hover response on campus and sermon cards.
- **Theme Switcher**: 3-state stateful toggle (`light` / `dark` / `auto`) synced via `localStorage` with zero-flash pre-hydration in `<head>`.

---

## Trending Features & Content Strategy (September 2026)

### 1. High-Impact Interactive Features
- **"Sunday Stream & Interactive Worship" Dynamic Banner**: Time-aware hero banner that shifts state on Sunday mornings (e.g., 9:00 AM – 1:00 PM EAT) to display a bold "Service is Live Now" player, falling back to recent seminar highlights during weekdays.
- **Daily Scripture & Audio Manna Widget**: Daily verse card paired with a 60-second audio devotional snippet from Bishop Dr. David Mutweri with 1-click WhatsApp/Facebook sharing.
- **Interactive Prayer Wall & Testimony Board**: Moderated community board with an encouraging "🙏 I Prayed for This" counter.
- **Fast "Plan Your Visit" WhatsApp Concierge**: Floating action pill button pre-filled for first-time guests connecting directly to church hospitality (WhatsApp is Kenya's #1 channel).
- **Offline PWA Caching**: Lightweight service worker caching hymns, prayer declarations, and audio for low-connectivity environments.

### 2. Curated License-Free Content Pillars
- **Consistent Visual Aesthetic**: Warm natural textures (wood, linen, earth tones), golden-hour sunlight, and genuine acoustic worship. Real church photography blended with CC0 royalty-free imagery.
- **Public Domain Hymns**: Classical pre-1928 hymns (*Amazing Grace*, *Great Is Thy Faithfulness*, *It Is Well With My Soul*, *Blessed Assurance*, and traditional Swahili translations like *Mwathani Mwega*).
- **Biblical Riddles & Trivia**: Clean, family-friendly questions driving organic dwell time and youth engagement.
- **Wholesome Christian Humor**: Relatable, clean church wit and fellowship moments.
- **Uplifting Ministry News**: 2-minute digests covering community outreach in Embu, regional leaders' conferences, and uplifting faith milestones.

---

## Data Integrity Policy

This project strictly enforces **Zero-Fabrication Standards**:
1. **Real Media Only**: All photography originates from verified Perazim Mission Church Facebook archives and high-resolution church event archives (`assets/fb_photos_web/`, `assets/bishop_real.jpg`). No generic Unsplash stock models or fake crowd shots.
2. **Authentic Leadership & Location**: All leadership bios represent real church leadership (Bishop Dr. David Mutweri, Embu, Kenya).
3. **Explicit PENDING State**: Any operational detail not yet officially verified (such as specific Sunday morning service slot adjustments) remains explicitly flagged as `[PENDING]` rather than inventing placeholders.

---

## Directory Structure

```text
perazim-site/
├── index.html                   # Main Landing Page
├── about/
│   └── index.html               # About & Leadership Page
├── sermons/
│   └── index.html               # Sermons Archive
├── visit/
│   └── index.html               # Plan a Visit Page
├── contact/
│   └── index.html               # Contact & Inquiries Page
├── hymns/
│   └── index.html               # Public Domain Hymnbook Archive
├── riddles/
│   └── index.html               # Bible Riddles & Faith Trivia
├── jokes/
│   └── index.html               # Wholesome Christian Humor
├── news/
│   └── index.html               # Inspiring Ministry News & Announcements
├── assets/
│   ├── styles.css               # Core CSS Design Engine & Motion Rules
│   ├── app.js                   # Navigation, Theme Engine, Parallax & Observers
│   ├── sermons.json             # Verified Sermon Catalog
│   ├── gallery_manifest.json    # Photo Gallery Metadata
│   ├── bishop_real.jpg          # Verified Portrait of Bishop Dr. David Mutweri
│   ├── church_cover_real.jpg    # Verified Church Building Cover Photo
│   ├── logo-transparent.png     # Transparent Vector Logo Mark
│   ├── favicon.png              # Site Favicon
│   └── fb_photos_web/           # Verified Church Congregation Photography
├── recon/                       # Design Benchmarking & Verification Tooling
│   ├── verify_v5upgrade.py      # Automated 86-Point DOM/CSS Test Suite
│   ├── palette_extract.py       # Reference Brand Palette Extraction Tool
│   ├── v5_comparison_report.md  # Benchmarking Against Industry Sites
│   └── prometheus_scrape_v5.json# Scraping Metadata
├── ARCHITECTURE.md              # Technical Architecture & Standards
├── CONTRIBUTING.md              # Contribution Guidelines
├── LICENSE                      # Open-Source License
├── .editorconfig                # Coding Style Configuration
└── .gitignore                   # Version Control Exclusions
```

---

## Automated Verification & Quality Gates

The codebase includes an automated audit suite verifying 86 distinct structural, CSS, script, and content integrity rules:

```bash
# Run the complete test suite
python3 recon/verify_v5upgrade.py
```

---

## Local Development & Preview

Serve the site locally with any static web server:

```bash
# Using Python
python3 -m http.server 8090

# Or using Node.js / npx
npx serve . -p 8090
```

Visit [`http://localhost:8090`](http://localhost:8090) in your browser.

---

## Deployment Guide

### GitHub Pages
1. Push this repository to GitHub.
2. In your repository settings, navigate to **Pages**.
3. Under **Source**, select **Deploy from a branch** and set `Branch: main`, `Folder: / (root)`.
4. Save. Your site will be live within seconds.

---

## Contributing

Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests. All changes must pass `python3 recon/verify_v5upgrade.py`.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
