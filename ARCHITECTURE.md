# Architecture

## Principles

- Static HTML, CSS and vanilla JavaScript. No framework, no bundler, no template engine.
- Content first: every page reads fully without JavaScript. JavaScript only adds the menu,
  theme choice, scroll reveal and copy buttons (`assets/app.js`).
- Animations use `transform`, `opacity` and `filter` and respect `prefers-reduced-motion`.
- One stylesheet (`assets/styles.css`), one script (`assets/app.js`).

## How a page is built

```
<head>            generated  (title, description, canonical, Open Graph, Twitter, icons,
                             theme-color, JSON-LD, fonts, stylesheet)
<body>
  skip link, floating scripture words, header + burger menu     generated
  <main id="main-content">
    <!-- chrome:hero --> ... <!-- /chrome:hero -->              generated
    page sections                                               written by hand
  </main>
  footer                                                        generated
  <script src="assets/app.js">
```

`scripts/sync_site.py` owns everything marked generated. Its `PAGES` table holds each page's
SEO text, hero painting, headline, buttons and verse; `MENU` holds the navigation. It also writes
`sitemap.xml` and `manifest.webmanifest`. Run it after any change to those tables; `--check` is
used in CI. The shared content feed (`data/`, `scripts/build_data.py`) fills the
`<!-- feed:NAME -->` blocks in the same pages. The two generators work on different markers and
do not touch each other's output.

## Theme

`<html data-theme="light|dark|auto">`. Light is the default. The button cycles
light, dark, auto and saves a non-default choice in `localStorage` (`perazim-theme`). A small
script in `<head>` applies it before first paint to avoid a flash. `auto` follows the system.
All colours come from CSS custom properties in section 1 of `styles.css`.

## Colour rules

- Dark purple text on light glass; white text only on deep purple or pink cards.
- Dark text on orange. Small orange text uses `--orange-ink` for contrast.
- Cards cycle purple, pink, orange (`.card-purple`, `.card-pink`, `.card-orange`).

## Stylesheet map

1 tokens, 2 base and ambient words, 3 buttons, 4 header and burger, 5 page hero,
6 sections and cards, 7 footer, 8 scroll reveal, 8b home, 9 responsive, reduced motion, print.

## Quality gates

`scripts/sync_site.py --check`, `scripts/build_data.py --check`, `scripts/check_site.py`
(static) and `scripts/e2e_site.js` (browser, five screen sizes). The older `recon/` scripts
belong to the earlier design and are kept only as history.
