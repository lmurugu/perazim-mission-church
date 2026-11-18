# Perazim Mission Church: official website

The website of **Perazim Mission Church (PMC)**, Embu, Kenya, under the leadership of
Bishop Dr. David Mutweri. Plain HTML, CSS and a little JavaScript, hosted on GitHub Pages.
No framework, no build step for visitors.

Live address: `https://lmurugu.github.io/perazim-mission-church/`

## Pages

| Route | Page |
|---|---|
| `/` | Home |
| `/visit/` | Plan a visit: times, place, map, first-visit questions |
| `/sermons/` | Messages (from the shared feed, linked to YouTube) |
| `/ministries/` | Fellowships, Sunday school, prayer times, ways to serve |
| `/give/` | Giving by M-Pesa and on Sunday |
| `/about/` | Our name, mission, leadership, values, beliefs |
| `/contact/` | Phone, WhatsApp, email, Facebook, YouTube, directions |
| `/next-steps/` | What to do after your first visit |
| `/news/` | Announcements and events (shared feed) |
| `/hymns/`, `/riddles/`, `/jokes/` | Family resources (shared feed) |
| `/privacy/` | What the site does and does not collect |
| `404.html` | Friendly "page not found", not indexed |

## Design

Frosted-glass look on the church's brand colours: deep purple `#2A0F33`, royal purple
`#681A7D` and orange `#E17D2F`. Light mode is the default; dark and automatic modes are
available from the sun/moon button. Every page has a painted full-width hero with a
frosted card, a call to action and a verse. The menu is a burger menu at every screen width.

- Type: Plus Jakarta Sans (headings), Inter (text), Fraunces (home title only)
- Colour and spacing tokens live at the top of `assets/styles.css`
- Motion: scroll reveals and glowing cards, all switched off for `prefers-reduced-motion`
- Everything important works without JavaScript

## SEO and sharing

Each page has a unique title and description, a canonical URL, Open Graph and Twitter
tags with an image, light and dark `theme-color`, icons and a web manifest. Structured data
(JSON-LD) describes the church, the website, breadcrumbs and each page, plus the
first-visit FAQ. `sitemap.xml` and `robots.txt` are generated.

## Working on the site

The shared head, header, hero and footer of every page are generated so they cannot drift apart:

```bash
python3 scripts/sync_site.py          # rewrite shared parts, sitemap.xml, manifest
python3 scripts/sync_site.py --check  # fail if anything is out of date
```

Edit page text in each page's own `<main>`. To change the title, description, hero text,
buttons or verse of a page, or the menu, edit `PAGES` / `MENU` in `scripts/sync_site.py`,
then run it. Sermons, hymns, riddles, jokes, news and contact details come from the
shared feed: edit `data/csv/*.csv` and run `python3 scripts/build_data.py` (see
[data/README.md](data/README.md)).

## Testing

```bash
python3 scripts/sync_site.py --check
python3 scripts/build_data.py --check
python3 scripts/check_site.py          # links, anchors, images, headings, SEO, sitemap

python3 -m http.server 8123 &          # then, with Playwright installed:
node scripts/e2e_site.js               # every page on phone, tablet, laptop, desktop
```

`check_site.py` and the two `--check` commands also run on every pull request
(`.github/workflows/`). `e2e_site.js` checks, for 14 pages at five screen sizes: no sideways
scrolling, fonts and images load, no console errors, burger menu (button, Escape, outside
click, every link), tap-target size, plus theme toggle, copy button, FAQ, scroll reveal,
reduced motion, no-JavaScript, keyboard skip link and the 404 page.

## Deploying

GitHub Pages, branch `main`, folder `/ (root)`. If the site moves to its own domain, change
`SITE` in `scripts/sync_site.py` (and the 404 base path), run it, and update `robots.txt`.

## Facts the church must confirm

Search the pages for `CHURCH TO CONFIRM` (HTML comments): group leaders' names, children's
ages for Sunday school, how Sunday school and Bible hour overlap, parking and matatu
directions. Do not invent these.

## Licence

MIT, see [LICENSE](LICENSE).
