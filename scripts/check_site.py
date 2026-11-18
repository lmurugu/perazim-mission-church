#!/usr/bin/env python3
"""Static checks for the whole site (standard library only, safe for CI).

Checks every page for: one h1 and sensible heading order, unique ids, image alt
text, unique titles and descriptions of a good length, canonical, social and
structured-data tags, working internal links, images and anchors, safe external
links, the sitemap, robots.txt and the web manifest.

Usage: python3 scripts/check_site.py
Exit status 1 if anything fails. Warnings do not fail the run.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lmurugu.github.io/perazim-mission-church/"
errors, warnings = [], []


def err(page, msg):
    errors.append(f"{page}: {msg}")


def warn(page, msg):
    warnings.append(f"{page}: {msg}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.meta = {}      # name or property -> content
        self.links = []     # (rel, href)
        self.refs = []      # (tag, attr, url, attrs)
        self.ids = []
        self.headings = []  # (level, text)
        self._h = None
        self.imgs = []
        self.jsonld = []
        self._in_ld = False
        self.lang = None
        self.attrs_all = []
        self.has_main = False
        self.has_skip = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.attrs_all.append((tag, a))
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta.setdefault(key, a.get("content", ""))
        if tag == "link":
            self.links.append((a.get("rel"), a.get("href"), a))
            if a.get("href"):
                self.refs.append((tag, "href", a["href"], a))
        if tag == "a" and a.get("href") is not None:
            self.refs.append((tag, "href", a["href"], a))
            if a.get("class") and "skip-link" in a["class"]:
                self.has_skip = True
        if tag in ("img", "source", "script", "iframe"):
            for k in ("src", "srcset"):
                if a.get(k):
                    if k == "srcset":
                        for part in a[k].split(","):
                            self.refs.append((tag, k, part.strip().split()[0], a))
                    else:
                        self.refs.append((tag, k, a[k], a))
        if tag == "img":
            self.imgs.append(a)
        if tag == "main":
            self.has_main = True
        if a.get("id"):
            self.ids.append(a["id"])
        if re.fullmatch(r"h[1-6]", tag):
            self._h = [int(tag[1]), ""]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if re.fullmatch(r"h[1-6]", tag) and self._h:
            self.headings.append((self._h[0], re.sub(r"\s+", " ", self._h[1]).strip()))
            self._h = None
        if tag == "script":
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._h is not None:
            self._h[1] += data
        if self._in_ld:
            self.jsonld[-1] += data


def page_files():
    files = [ROOT / "index.html", ROOT / "404.html"]
    files += sorted(p / "index.html" for p in ROOT.iterdir() if p.is_dir() and (p / "index.html").exists()
                    and p.name not in ("design", "recon", "scripts", "data", "assets", ".git", ".github", "node_modules"))
    return files


def url_for(f):
    rel = f.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return SITE
    if rel == "404.html":
        return SITE + "404.html"
    return SITE + rel[: -len("index.html")]


def resolve(src_file, url):
    """Return the local Path a relative or site-absolute URL points to, or None if external."""
    u = urlparse(url)
    if u.scheme in ("http", "https"):
        if url.startswith(SITE):
            path = unquote(url[len(SITE):].split("#")[0].split("?")[0])
        else:
            return None
    elif u.scheme in ("mailto", "tel", "data", "javascript"):
        return None
    else:
        path = unquote(u.path)
        if path.startswith("/perazim-mission-church/"):
            path = path[len("/perazim-mission-church/"):]
        elif path.startswith("/"):
            return ROOT / path.lstrip("/")
        elif path == "":
            return src_file
        else:
            base = src_file.parent
            target = (base / path).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                return target
            return target if not path.endswith("/") and target.suffix else (target / "index.html" if target.is_dir() or path.endswith("/") else target)
    p = ROOT / path
    if path == "" or path.endswith("/"):
        p = p / "index.html"
    return p


def main():
    files = page_files()
    pages = {}
    titles, descs = {}, {}
    for f in files:
        name = f.relative_to(ROOT).as_posix()
        pp = Page()
        pp.feed(f.read_text())
        pages[f] = pp

    for f, pp in pages.items():
        name = f.relative_to(ROOT).as_posix()
        # --- document basics
        if pp.lang != "en":
            err(name, f"html lang is {pp.lang!r}, expected 'en'")
        if "viewport" not in pp.meta:
            err(name, "missing viewport meta")
        title = pp.title.strip()
        if not title:
            err(name, "missing <title>")
        elif len(title) > 70:
            warn(name, f"title is {len(title)} characters (aim for 60 or fewer)")
        if title in titles:
            err(name, f"duplicate title, also on {titles[title]}")
        titles[title] = name
        d = pp.meta.get("description", "")
        if not d:
            err(name, "missing meta description")
        else:
            if name != "404.html" and not 50 <= len(d) <= 170:
                warn(name, f"description is {len(d)} characters (aim for 70 to 160)")
            if d in descs:
                err(name, f"duplicate description, also on {descs[d]}")
            descs[d] = name
        canon = [h for r, h, a in pp.links if r == "canonical"]
        if canon != [url_for(f)]:
            err(name, f"canonical is {canon}, expected {url_for(f)}")
        for key in ("og:title", "og:description", "og:url", "og:image", "og:type", "og:site_name",
                    "twitter:card", "twitter:title", "twitter:description", "twitter:image", "theme-color", "robots"):
            if not pp.meta.get(key):
                err(name, f"missing {key}")
        if pp.meta.get("og:url") != url_for(f):
            err(name, "og:url does not match the canonical URL")
        if pp.meta.get("og:title") != title:
            warn(name, "og:title differs from <title>")
        if not any(r and "icon" in r for r, h, a in pp.links):
            err(name, "missing favicon link")
        if not pp.has_main:
            err(name, "missing <main>")
        if not pp.has_skip:
            err(name, "missing skip link")
        noindex = "noindex" in pp.meta.get("robots", "")
        if name == "404.html" and not noindex:
            err(name, "404 page should be noindex")
        if name != "404.html" and noindex:
            err(name, "page is noindex")
        # --- structured data
        if not pp.jsonld and name != "404.html":
            err(name, "no JSON-LD structured data")
        for raw in pp.jsonld:
            try:
                json.loads(raw)
            except ValueError as e:
                err(name, f"invalid JSON-LD: {e}")
        # --- headings
        h1s = [h for h in pp.headings if h[0] == 1]
        if len(h1s) != 1:
            err(name, f"{len(h1s)} h1 elements, expected exactly 1")
        prev = 0
        for lvl, text in pp.headings:
            if prev and lvl > prev + 1:
                err(name, f"heading level jumps from h{prev} to h{lvl} at {text[:40]!r}")
            if not text:
                err(name, f"empty h{lvl}")
            prev = lvl
        # --- ids
        seen = set()
        for i in pp.ids:
            if i in seen:
                err(name, f"duplicate id {i!r}")
            seen.add(i)
        for tag, a in pp.attrs_all:
            for k in ("aria-labelledby", "aria-controls"):
                for ref in (a.get(k) or "").split():
                    if ref not in pp.ids:
                        err(name, f"{k} points to missing id {ref!r}")
            if tag == "label" and a.get("for") and a["for"] not in pp.ids:
                err(name, f"label for={a['for']!r} has no matching id")
        # --- images
        for a in pp.imgs:
            if "alt" not in a:
                err(name, f"<img src={a.get('src')!r}> has no alt attribute")
            if not (a.get("width") and a.get("height")):
                warn(name, f"<img src={a.get('src')!r}> has no width/height (layout shift)")
        # --- links and resources
        for tag, attr, url, a in pp.refs:
            if not url or url.startswith(("tel:", "mailto:", "data:", "javascript:")):
                if url and url.startswith("tel:") and not re.fullmatch(r"tel:\+\d{9,15}", url):
                    err(name, f"bad tel link {url}")
                if url and url.startswith("mailto:") and not re.fullmatch(r"mailto:[^@\s]+@[^@\s]+\.[a-z]+", url):
                    err(name, f"bad mailto link {url}")
                continue
            base, frag = urldefrag(url)
            if url.startswith("http") and not url.startswith(SITE):
                if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
                    err(name, f"external link without rel=noopener: {url[:70]}")
                if url.startswith("http://"):
                    warn(name, f"insecure http link: {url[:70]}")
                continue
            target = resolve(f, url)
            if target is None:
                continue
            if not target.exists():
                err(name, f"broken {tag} {attr}: {url} -> {target.relative_to(ROOT) if str(target).startswith(str(ROOT)) else target}")
                continue
            if frag and tag == "a" and target.suffix == ".html":
                tp = pages.get(target)
                if tp is None:
                    tp = Page()
                    tp.feed(target.read_text())
                if frag not in tp.ids:
                    err(name, f"broken anchor: {url} (no id {frag!r} in {target.relative_to(ROOT)})")
        # --- target=_blank
        for tag, a in pp.attrs_all:
            if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
                err(name, f"target=_blank without noopener: {a.get('href', '')[:70]}")

    # --- menu links the same on every page
    menus = {}
    for f in pages:
        html = f.read_text()
        m = re.search(r'<ul class="nav-links" id="site-menu">(.*?)</ul>', html, re.S)
        hrefs = re.findall(r'<a href="([^"]*)"', m.group(1)) if m else []
        menus[f] = [(resolve(f, h).relative_to(ROOT).as_posix() if resolve(f, h) else None) for h in hrefs]
    ref = menus[ROOT / "index.html"]
    for f, m in menus.items():
        if m[: len(ref)] != ref:
            err(f.relative_to(ROOT).as_posix(), "menu links differ from the home page menu")
    # every real page is reachable from the menu
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        if rel in ("404.html", "privacy/index.html"):
            continue
        if rel not in ref:
            err(rel, "page is not linked from the menu")

    # --- sitemap, robots, manifest
    sm = (ROOT / "sitemap.xml").read_text()
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    expected = {url_for(f) for f in files if f.name != "404.html"}
    for u in sorted(expected - set(locs)):
        err("sitemap.xml", f"missing {u}")
    for u in sorted(set(locs) - expected):
        err("sitemap.xml", f"lists unknown page {u}")
    robots = (ROOT / "robots.txt").read_text()
    if f"Sitemap: {SITE}sitemap.xml" not in robots:
        err("robots.txt", "does not point to the sitemap")
    try:
        man = json.loads((ROOT / "manifest.webmanifest").read_text())
        for ic in man.get("icons", []):
            if not (ROOT / ic["src"]).exists():
                err("manifest.webmanifest", f"icon missing: {ic['src']}")
    except (OSError, ValueError) as e:
        err("manifest.webmanifest", str(e))
    if not (ROOT / "assets/og-default.jpg").exists():
        err("assets", "og-default.jpg is missing")

    for w in warnings:
        print("warn ", w)
    for e in errors:
        print("FAIL ", e)
    print(f"\n{len(files)} pages checked: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
