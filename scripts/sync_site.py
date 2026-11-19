#!/usr/bin/env python3
"""Regenerate the shared parts of every page: head and SEO tags, header and
menu, painted hero, footer and script tags.

The site has no template engine, so this script is the single source for
everything that repeats. Page content (everything inside <main> after the
hero) is left alone, and so are the feed blocks that build_data.py fills.

Usage:
    python3 scripts/sync_site.py            # rewrite pages, sitemap, manifest
    python3 scripts/sync_site.py --check    # exit 1 if any page is out of date

To change a page title, description, hero text, hero painting or verse,
edit PAGES below and run the script. Details: CONTRIBUTING.md.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lmurugu.github.io/perazim-mission-church/"
SITE_PATH = "/perazim-mission-church/"  # used by 404.html, which can be served from any path
NAME = "Perazim Mission Church"
LASTMOD = "2026-11-19"
PHONE = "+254710772227"
WA = "https://wa.me/254710772227"
FB = "https://web.facebook.com/perazim.missioncentre"
YT = "https://www.youtube.com/@perazimchurchembu"
MAP = "https://www.google.com/maps/search/?api=1&query=Manyatta%2C+Embu%2C+Kenya"


def wa(text):
    from urllib.parse import quote
    return f"{WA}?text={quote(text)}"


# slug -> (alt text). Files live in assets/heroes/<slug>.webp and .jpg (1280x720).
ART = {
    "prodigal-son": "Watercolor painting of a father running to welcome his returning son",
    "sermon-on-the-mount": "Watercolor painting of Jesus teaching a crowd on a hillside above the Sea of Galilee",
    "good-samaritan": "Watercolor painting of the Good Samaritan caring for an injured traveler",
    "five-loaves-two-fish": "Watercolor painting of a boy offering loaves and fish to Jesus",
    "calling-the-disciples": "Watercolor painting of Jesus calling fishermen at the Sea of Galilee",
    "jesus-at-the-door": "Watercolor painting of Jesus knocking at a glowing wooden door",
}

# key '' is the home page. href values are relative to the site root.
PAGES = {
    "": dict(
        title="Perazim Mission Church, Embu | Sunday worship in Manyatta",
        desc="Perazim Mission Church is a Pentecostal and Evangelical church family in Manyatta, Embu, Kenya. Plan a visit, watch sermons and connect with us.",
        nav="Home", art="prodigal-son",
    ),
    "visit": dict(
        title="Plan a Visit | Perazim Mission Church, Embu",
        desc="Plan your first visit to Perazim Mission Church in Manyatta, Embu. Sundays: Bible hour 9:00 AM, main service 10:00 AM. Directions and what to expect.",
        nav="Visit", art="prodigal-son",
        kicker="Plan a visit", h1="We'd love to <em>meet you</em>",
        lead="Whether it's your first Sunday or you're coming back after a while, here's what you need to know.",
        ctas=[("primary", "I'm coming this Sunday", wa("Hello, I'm planning to visit Perazim this Sunday. Please send me directions."), True),
              ("secondary", "Get directions", MAP, True)],
        verse=("The Prodigal Son · Luke 15", "Come to me, all who labor and are heavy laden, and I will give you rest.", "Matthew 11:28 (ESV)"),
    ),
    "sermons": dict(
        title="Sermons | Perazim Mission Church, Embu",
        desc="Watch sermons, seminars and teaching from Perazim Mission Church in Embu, Kenya.",
        nav="Sermons", art="sermon-on-the-mount",
        kicker="Sermons", h1="Messages from <em>the pulpit</em>",
        lead="Teaching and seminars from Perazim Mission Church. Our services stream live on Facebook and YouTube, and our media team uploads each message to our YouTube channel.",
        ctas=[("primary", "Watch live on Facebook", FB, True), ("secondary", "Open YouTube", YT, True)],
        verse=("The Sermon on the Mount · Matthew 5", "Your word is a lamp to my feet and a light to my path.", "Psalm 119:105 (ESV)"),
    ),
    "ministries": dict(
        title="Ministries and Fellowships | Perazim Mission Church, Embu",
        desc="Fellowships for gents, ladies and youth, Sunday school, home fellowship, prayer meetings and outreach at Perazim Mission Church in Embu.",
        nav="Ministries", art="good-samaritan",
        kicker="Ministries", h1="Find your place <em>to serve</em>",
        lead="Fellowships, Sunday school, prayer and outreach. Wherever you are in your walk with God, there is a place for you to belong and to serve.",
        ctas=[("primary", "Find a group", wa("Hello, please tell me which groups meet at Perazim and when."), True),
              ("secondary", "Next steps", "next-steps/", False)],
        verse=("The Good Samaritan · Luke 10", "As each has received a gift, use it to serve one another, as good stewards of God's varied grace.", "1 Peter 4:10 (ESV)"),
    ),
    "give": dict(
        title="Give | Perazim Mission Church, Embu",
        desc="Give to Perazim Mission Church in Embu by M-Pesa (Paybill 4069983) or in person on Sunday.",
        nav="Give", art="five-loaves-two-fish",
        kicker="Give", h1="Generosity <em>in action</em>",
        lead="Your tithes and offerings support worship, outreach and care for families in Embu and beyond.",
        ctas=[("primary", "Give with M-Pesa", "#ways", False), ("secondary", "Ask about giving", wa("Hello, I have a question about giving at Perazim."), True)],
        verse=("The boy with five loaves and two fish · John 6", "Each one must give as he has decided in his heart, not reluctantly or under compulsion, for God loves a cheerful giver.", "2 Corinthians 9:7 (ESV)"),
    ),
    "about": dict(
        title="About Us | Perazim Mission Church, Embu",
        desc="Perazim Mission Church is a Pentecostal and Evangelical church in Embu, Kenya, led by Bishop Dr David Mutweri. Our name, our values and our leadership.",
        nav="About", art="calling-the-disciples",
        kicker="About us", h1="The place of <em>great breakthrough</em>",
        lead="Perazim Mission Church is a Pentecostal and Evangelical family of faith in Manyatta, Embu, on the slopes of Mount Kenya.",
        ctas=[("primary", "Plan my visit", "visit/", False), ("secondary", "What we believe", "#beliefs", False)],
        verse=("Jesus calls the first disciples · Matthew 4", "Follow me, and I will make you fishers of men.", "Matthew 4:19 (ESV)"),
    ),
    "contact": dict(
        title="Contact Us | Perazim Mission Church, Embu",
        desc="Contact Perazim Mission Church in Embu, Kenya: call or WhatsApp 0710 772 227, email info@perazimchurch.org, or visit us in Manyatta.",
        nav="Contact", art="jesus-at-the-door",
        kicker="Contact", h1="Get in <em>touch</em>",
        lead="Have a question, a prayer request, or want to visit? We'd love to hear from you.",
        ctas=[("primary", "Chat on WhatsApp", WA, True), ("secondary", "Call 0710 772 227", "tel:" + PHONE, False)],
        verse=("Behold, I stand at the door and knock", "If anyone hears my voice and opens the door, I will come in to him and eat with him, and he with me.", "Revelation 3:20 (ESV)"),
    ),
    "next-steps": dict(
        title="Next steps | Perazim Mission Church, Embu",
        desc="Next steps at Perazim Mission Church, Embu: plan a visit, follow Jesus, be baptised, become a member or request prayer.",
        nav="Next steps", art="prodigal-son", art_pos="30% 50%",
        kicker="Next steps", h1="Where do you go <em>from here?</em>",
        lead="Whether you're visiting for the first time or you've been coming for years, there's a clear next step for you. Pick the one that fits.",
        ctas=[("primary", "Choose your step", "#steps", False), ("secondary", "Plan a visit", "visit/", False)],
        verse=("Come home", "Ask, and it will be given to you; seek, and you will find; knock, and it will be opened to you.", "Matthew 7:7 (ESV)"),
    ),
    "news": dict(
        title="News & Events | Perazim Mission Church, Embu",
        desc="Announcements and upcoming events at Perazim Mission Church in Embu, Kenya.",
        nav="News & events", art="calling-the-disciples", art_pos="70% 50%",
        kicker="News & events", h1="What's <em>happening</em>",
        lead="Church announcements and upcoming gatherings. For day-to-day updates, follow us on Facebook.",
        ctas=[("primary", "Follow us on Facebook", FB, True), ("secondary", "Plan a visit", "visit/", False)],
        verse=("Good news to share", "Tell of his salvation from day to day.", "Psalm 96:2 (ESV)"),
    ),
    "hymns": dict(
        title="Hymns | Perazim Mission Church, Embu",
        desc="Lyrics and chord charts for the hymns sung at Perazim Mission Church in Embu.",
        nav="Hymns", art="sermon-on-the-mount", art_pos="50% 30%",
        kicker="Hymns", h1="Songs of <em>praise</em>",
        lead="Hymns and chord charts used by our worship team. Tap a hymn to see its lyrics and chords.",
        ctas=[("primary", "Browse the hymns", "#list", False), ("secondary", "Hear us on Sunday", "visit/", False)],
        verse=("Come with singing", "Make a joyful noise to the Lord, all the earth! Serve the Lord with gladness! Come into his presence with singing!", "Psalm 100:1–2 (ESV)"),
    ),
    "riddles": dict(
        title="Bible Riddles | Perazim Mission Church, Embu",
        desc="Bible riddles for families, youth groups and Sunday school from Perazim Mission Church in Embu.",
        nav="Bible riddles", art="good-samaritan", art_pos="60% 50%",
        kicker="Bible riddles", h1="Riddles from <em>Scripture</em>",
        lead="Riddles from Scripture for families and youth. Tap a riddle to reveal the answer.",
        ctas=[("primary", "Try a riddle", "#list", False), ("secondary", "More for the family", "./#family", False)],
        verse=("Jesus taught in stories", "It is the glory of God to conceal things, but the glory of kings is to search things out.", "Proverbs 25:2 (ESV)"),
    ),
    "jokes": dict(
        title="Christian Jokes | Perazim Mission Church, Embu",
        desc="Clean, light-hearted Christian jokes to share with the family, from Perazim Mission Church in Embu.",
        nav="Christian jokes", art="five-loaves-two-fish", art_pos="40% 50%",
        kicker="Christian jokes", h1="A little <em>joy</em>",
        lead="Clean, light-hearted humour to share with the family.",
        ctas=[("primary", "Read the jokes", "#list", False), ("secondary", "More for the family", "./#family", False)],
        verse=("A joyful table", "A joyful heart is good medicine, but a crushed spirit dries up the bones.", "Proverbs 17:22 (ESV)"),
    ),
    "privacy": dict(
        title="Privacy | Perazim Mission Church, Embu",
        desc="How the Perazim Mission Church website handles your information: no accounts, no tracking, and the few third-party services it uses.",
        nav="Privacy", art="jesus-at-the-door", art_pos="50% 40%", in_menu=False,
        kicker="Privacy", h1="Your privacy <em>on this site</em>",
        lead="This website does not ask you to sign in, does not run advertising and does not track you. Here is what it does use.",
        ctas=[("primary", "Contact us", "contact/", False)],
        verse=("An open door", "Behold, I stand at the door and knock.", "Revelation 3:20 (ESV)"),
    ),
    "404.html": dict(
        title="Page not found | Perazim Mission Church",
        desc="This page could not be found.",
        nav="", art="jesus-at-the-door", noindex=True, absolute=True,
        kicker="Page not found", h1="We couldn't find <em>that page</em>",
        lead="It may have moved. These links will get you where you need to go.",
        ctas=[("primary", "Go home", "./", False), ("secondary", "Plan a visit", "visit/", False)],
        verse=("Keep knocking", "Seek, and you will find.", "Matthew 7:7 (ESV)"),
    ),
}

MENU = [  # (key, label) in menu order; None = group heading
    ("", "Home"), ("visit", "Visit"), ("sermons", "Sermons"), ("ministries", "Ministries"), ("give", "Give"),
    ("about", "About"), ("contact", "Contact"),
    ("#", "More"), ("next-steps", "Next steps"), ("news", "News & events"),
    ("#", "For the family"), ("hymns", "Hymns"), ("riddles", "Bible riddles"), ("jokes", "Christian jokes"),
]

AMBIENT = [("Grace", "5%", "620px", "0s"), ("Hope", "78%", "1500px", "-3s"), ("Faith", "12%", "2600px", "-5s"),
           ("Psalm 23", "70%", "3400px", "-2s"), ("Love", "20%", "4300px", "-6s"), ("Light", "82%", "5000px", "-4s")]


def page_file(key):
    if key == "404.html":
        return ROOT / "404.html"
    return ROOT / key / "index.html" if key else ROOT / "index.html"


def page_url(key):
    if key == "404.html":
        return SITE + "404.html"
    return SITE + (key + "/" if key else "")


def prefix(key, cfg):
    if cfg.get("absolute"):
        return SITE_PATH
    return "../" if key else ""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&")


def link(href, p):
    """Resolve a page-relative href from PAGES config."""
    if href.startswith(("http", "tel:", "mailto:", "#")):
        return href
    if href.startswith("./"):
        return p + href[2:] if p != "" else href
    return p + href


# ----------------------------------------------------------------- head
def jsonld(key, cfg, main_html):
    url = page_url(key)
    blocks = []
    org = {
        "@context": "https://schema.org", "@type": "Church", "@id": SITE + "#church",
        "name": NAME, "alternateName": "PMC Embu", "slogan": "The Place of Great Breakthrough",
        "description": PAGES[""]["desc"], "url": SITE,
        "logo": SITE + "assets/logo-transparent.png", "image": SITE + "assets/og-default.jpg",
        "address": {"@type": "PostalAddress", "addressLocality": "Manyatta", "addressRegion": "Embu County", "addressCountry": "KE"},
        "telephone": PHONE, "email": "info@perazimchurch.org", "knowsLanguage": ["en", "sw"],
        "founder": {"@type": "Person", "name": "Bishop Dr David Mutweri"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "08:00", "closes": "13:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Monday", "opens": "17:30", "closes": "18:30"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Thursday", "opens": "18:00", "closes": "19:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "19:00", "closes": "20:00"},
        ],
        "sameAs": [FB, YT],
    }
    if key == "":
        blocks.append(org)
        blocks.append({"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "#website", "url": SITE,
                       "name": NAME, "inLanguage": "en", "publisher": {"@id": SITE + "#church"}})
    elif not cfg.get("noindex"):
        crumbs = [("Home", SITE), (cfg["nav"] or cfg["kicker"], url)]
        blocks.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
        wp = {"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#webpage", "url": url,
              "name": cfg["title"], "description": cfg["desc"], "inLanguage": "en",
              "isPartOf": {"@id": SITE + "#website"}, "about": {"@id": SITE + "#church"}}
        if key == "about":
            wp["@type"] = "AboutPage"
        if key == "contact":
            wp["@type"] = "ContactPage"
        blocks.append(wp)
        if key == "visit":
            qa = []
            for m in re.finditer(r"<details class=\"faq-item\"[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>", main_html, re.S):
                q, a = strip_tags(m.group(1)).strip(), strip_tags(m.group(2)).strip()
                a = a.replace("&ldquo;", "“").replace("&rdquo;", "”").replace("&rsquo;", "’")
                qa.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
            if qa:
                blocks.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qa})
    return "\n".join('<script type="application/ld+json">\n' + json.dumps(b, indent=2, ensure_ascii=False) + "\n</script>" for b in blocks)


def render_head(key, cfg, main_html):
    p = prefix(key, cfg)
    url = page_url(key)
    img = SITE + "assets/og-default.jpg"
    fam = "Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800"
    if key == "":
        fam = "Fraunces:wght@600;700&family=" + fam
    robots = "noindex" if cfg.get("noindex") else "index, follow, max-image-preview:large"
    t, d = esc(cfg["title"]), esc(cfg["desc"])
    hero_img = f"{p}assets/life/life-1.webp" if key == "" else f"{p}assets/heroes/{cfg['art']}.webp"
    lines = [
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{t}</title>",
        f'<meta name="description" content="{d}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{url}">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#07040A" media="(prefers-color-scheme: dark)">',
        f'<link rel="manifest" href="{p}manifest.webmanifest">',
        f'<link rel="icon" href="{p}assets/favicon.ico" sizes="any">',
        f'<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/favicon-32.png">',
        f'<link rel="apple-touch-icon" href="{p}assets/icons/apple-touch-icon.png">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{NAME}">',
        '<meta property="og:locale" content="en_GB">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{d}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{NAME}, Embu: the place of great breakthrough">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{t}">',
        f'<meta name="twitter:description" content="{d}">',
        f'<meta name="twitter:image" content="{img}">',
        f'<link rel="preload" as="image" href="{hero_img}" type="image/webp" fetchpriority="high">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={fam}&display=swap">',
        f'<link rel="stylesheet" href="{p}assets/styles.css">',
        "<script>",
        "  // Apply the saved theme before first paint so the page never flashes. Default: light.",
        "  (function () {",
        "    var t = 'light';",
        "    try { var s = localStorage.getItem('perazim-theme'); if (s === 'dark' || s === 'auto') t = s; } catch (e) {}",
        "    document.documentElement.setAttribute('data-theme', t);",
        "  })();",
        "</script>",
        jsonld(key, cfg, main_html),
    ]
    return "\n".join("  " + l if not l.startswith("<script type") else l for l in lines)


# ----------------------------------------------------------------- header / hero / footer
BURGER_DEFS = ('<svg class="burger-defs" width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">'
               '<defs><linearGradient id="burger-grad" gradientUnits="userSpaceOnUse" x1="4" y1="0" x2="20" y2="0">'
               '<stop offset="0" stop-color="#E17D2F"/><stop offset=".5" stop-color="#C0398F"/><stop offset="1" stop-color="#681A7D"/>'
               '</linearGradient></defs></svg>')


def render_header(key, cfg):
    p = prefix(key, cfg)
    items = []
    for k, label in MENU:
        if k == "#":
            items.append(f'<li class="nav-group" aria-hidden="true">{label}</li>')
            continue
        href = p + (k + "/" if k else "")
        if k == "" and p == "":
            href = "./"
        cur = ' aria-current="page"' if k == key else ""
        items.append(f'<li><a href="{href}"{cur}>{esc(label)}</a></li>')
    ambient = "".join(f'<span style="--x:{x};--y:{y};--d:{d}">{w}</span>' for w, x, y, d in AMBIENT)
    sun = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
    moon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
    auto = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><circle cx="12" cy="12" r="9"/><path d="M12 3v18"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>'
    home = "./" if p == "" else p
    defs = BURGER_DEFS if key == "" else ""
    return f'''<a class="skip-link" href="#main-content">Skip to content</a>
  <div class="ambient" aria-hidden="true">{ambient}</div>
  <header>
  {defs}<nav class="nav-container" aria-label="Main">
    <a href="{home}" class="brand-wrapper" aria-label="{NAME} home">
      <img src="{p}assets/logo-transparent.png" alt="" class="nav-logo-img" width="38" height="38">
      <span class="brand-title">PERAZIM</span>
    </a>
    <div class="nav-actions">
      <a href="{p}visit/" class="btn btn-primary nav-cta">Plan a Visit</a>
      <button id="theme-toggle" class="theme-toggle" type="button" aria-label="Change colour theme" title="Change colour theme">
        <span class="theme-icon theme-icon-sun" aria-hidden="true">{sun}</span>
        <span class="theme-icon theme-icon-moon" aria-hidden="true">{moon}</span>
        <span class="theme-icon theme-icon-auto" aria-hidden="true">{auto}</span>
      </button>
      <button class="nav-toggle" type="button" aria-controls="site-menu" aria-expanded="false" aria-label="Open menu">
        <svg class="icon-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        <svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
    </div>
    <ul class="nav-links" id="site-menu">{"".join(items)}</ul>
  </nav>
  </header>'''


def picture(p, slug, alt, eager=True, pos=None):
    style = f' style="object-position:{pos}"' if pos else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture class="hero-art"><source srcset="{p}assets/heroes/{slug}.webp" type="image/webp">'
            f'<img src="{p}assets/heroes/{slug}.jpg" alt="{esc(alt)}" width="1280" height="720" {load}{style}></picture>')


def render_hero(key, cfg):
    p = prefix(key, cfg)
    ctas = []
    for kind, label, href, ext in cfg["ctas"]:
        cls = "btn btn-primary" if kind == "primary" else "btn btn-secondary"
        rel = ' target="_blank" rel="noopener"' if ext else ""
        ctas.append(f'<a class="{cls}" href="{esc(link(href, p))}"{rel}>{esc(label)}</a>')
    tag, text, ref = cfg["verse"]
    return f'''<section class="page-hero" aria-labelledby="page-title">
      {picture(p, cfg["art"], ART[cfg["art"]], True, cfg.get("art_pos"))}
      <div class="hero-glaze"></div>
      <div class="page-hero-inner">
        <div class="hero-card">
          <span class="kicker">{cfg["kicker"].replace("&", "&amp;")}</span>
          <h1 id="page-title" class="editorial-title">{cfg["h1"]}</h1>
          <p class="page-lead">{esc(cfg["lead"])}</p>
          <div class="hero-actions">{"".join(ctas)}</div>
        </div>
        <figure class="hero-verse"><figcaption>{esc(tag)}</figcaption><blockquote>&ldquo;{esc(text)}&rdquo;</blockquote><cite>{esc(ref)}</cite></figure>
      </div>
    </section>'''


def render_footer(key, cfg):
    p = prefix(key, cfg)
    home = "./" if p == "" else p
    ex = [("visit", "Visit"), ("sermons", "Sermons"), ("ministries", "Ministries"), ("give", "Give"), ("about", "About us"),
          ("next-steps", "Next steps"), ("news", "News &amp; events"), ("contact", "Contact")]
    fam = [("hymns", "Hymns"), ("riddles", "Bible riddles"), ("jokes", "Christian jokes")]
    li = lambda items: "".join(f'<li><a href="{p}{k}/">{l}</a></li>' for k, l in items)
    return f'''<footer class="site-footer">
    <div class="footer-grid">
      <div>
        <a class="footer-brand" href="{home}"><img src="{p}assets/logo-transparent.png" alt="" width="36" height="36">{NAME}</a>
        <p class="footer-tagline">The Place of Great Breakthrough. A Pentecostal and Evangelical church family in Embu, Kenya.</p>
      </div>
      <div>
        <h2>Visit</h2>
        <ul>
          <li>Embu Central Campus</li>
          <li>Manyatta, Embu County</li>
          <li>Sundays: Bible hour 9:00 AM, main service 10:00 AM</li>
          <li><a href="{MAP.replace("&", "&amp;")}" target="_blank" rel="noopener">Get directions</a></li>
        </ul>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>{li(ex)}{li(fam)}</ul>
      </div>
      <div>
        <h2>Connect</h2>
        <ul>
          <li><a href="tel:{PHONE}">0710 772 227</a></li>
          <li><a href="{esc(wa("Hello, I would like to ask about Perazim."))}" target="_blank" rel="noopener">WhatsApp</a></li>
          <li><a href="{esc(wa("Hello, I would like to request prayer."))}" target="_blank" rel="noopener">Need prayer?</a></li>
          <li><a href="mailto:info@perazimchurch.org">info@perazimchurch.org</a></li>
          <li><a href="{FB}" target="_blank" rel="noopener">Facebook</a></li>
          <li><a href="{YT}" target="_blank" rel="noopener">YouTube</a></li>
        </ul>
      </div>
    </div>
    <p class="footer-bottom">&copy; <span data-year>2026</span> {NAME}, Embu, Kenya. <a href="{p}privacy/">Privacy</a></p>
  </footer>'''


# ----------------------------------------------------------------- home hero
def render_home_hero(cfg):
    return f'''<section class="home-hero" aria-labelledby="page-title">
      <div class="home-hero-inner">
        <img class="home-logo" src="assets/logo-transparent.png" alt="Perazim Mission Church logo" width="300" height="300" fetchpriority="high">
        <p class="home-kicker">Sundays in Manyatta, Embu</p>
        <h1 id="page-title" class="home-title">For God. For People. <em>For the City.</em></h1>
        <p class="home-lead">A Christ-centred church family worshipping together in Manyatta, Embu. Come as you are. You belong here.</p>
        <div class="hero-actions">
          <a class="btn btn-primary cta-pulse" href="visit/">Plan my visit</a>
          <a class="btn btn-secondary" href="{FB}" target="_blank" rel="noopener">Watch live on Facebook</a>
        </div>
      </div>
    </section>'''


# ----------------------------------------------------------------- assemble
MAIN_OPEN = '<main class="main-wrapper" id="main-content">'
HERO_RE = re.compile(r'<!-- chrome:hero -->.*?<!-- /chrome:hero -->', re.S)
OLD_HERO_RE = re.compile(r'\s*<section class="(?:page-hero|hero-island|home-hero)"[^>]*>.*?</section>', re.S)


def split_main(text):
    m = re.search(r'<main class="main-wrapper" id="main-content">(.*?)</main>', text, re.S)
    if not m:
        raise SystemExit("no <main> found")
    inner = m.group(1)
    if "<!-- /chrome:hero -->" in inner:
        rest = inner.split("<!-- /chrome:hero -->", 1)[1]
    else:
        rest = OLD_HERO_RE.sub("", inner, count=1)
    return rest.rstrip() + "\n  "


def build_page(key, cfg):
    f = page_file(key)
    old = f.read_text()
    rest = split_main(old)
    p = prefix(key, cfg)
    hero = render_home_hero(cfg) if key == "" else render_hero(key, cfg)
    page_class = "home" if key == "" else "inner"
    html = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{render_head(key, cfg, rest)}
</head>
<body class="page-{key.replace(".html", "") or "home"}">
  <!-- Generated by scripts/sync_site.py: head, header, hero and footer. Edit scripts/sync_site.py, not these regions. -->
  {render_header(key, cfg)}
  {MAIN_OPEN}
    <!-- chrome:hero -->
    {hero}
    <!-- /chrome:hero -->{rest}</main>
  {render_footer(key, cfg)}
  <script src="{p}assets/app.js"></script>
</body>
</html>
'''
    return f, html


def sitemap():
    rows = []
    for key, cfg in PAGES.items():
        if cfg.get("noindex"):
            continue
        pri = "1.0" if key == "" else "0.8" if key in ("visit", "sermons", "give", "about", "contact", "ministries") else "0.6"
        rows.append(f"  <url><loc>{page_url(key)}</loc><lastmod>{LASTMOD}</lastmod><priority>{pri}</priority></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"


def manifest():
    return json.dumps({
        "name": NAME + ", Embu", "short_name": "Perazim", "description": PAGES[""]["desc"],
        "start_url": "./", "scope": "./", "display": "standalone", "lang": "en",
        "background_color": "#FFFFFF", "theme_color": "#681A7D",
        "icons": [
            {"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "assets/icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }, indent=2) + "\n"


def main():
    check = "--check" in sys.argv
    outputs = {}
    for key, cfg in PAGES.items():
        f = page_file(key)
        if not f.exists():
            print(f"skip {key or 'home'}: {f.relative_to(ROOT)} does not exist yet")
            continue
        path, html = build_page(key, cfg)
        outputs[path] = html
    outputs[ROOT / "sitemap.xml"] = sitemap()
    outputs[ROOT / "manifest.webmanifest"] = manifest()
    outputs[ROOT / "robots.txt"] = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n"
    stale = []
    for path, text in outputs.items():
        if not path.exists() or path.read_text() != text:
            stale.append(path.relative_to(ROOT))
            if not check:
                path.write_text(text)
    if check:
        if stale:
            print("Out of date (run python3 scripts/sync_site.py):", ", ".join(map(str, stale)))
            sys.exit(1)
        print("Shared page parts are up to date.")
    else:
        print(f"Wrote {len(stale)} file(s): " + ", ".join(map(str, stale)))


if __name__ == "__main__":
    main()
