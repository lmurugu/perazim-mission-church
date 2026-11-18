#!/usr/bin/env python3
"""Build the shared content feed.

The CSV files in data/csv/ are the source of truth. They use the same tab
names and column headers as the Android app's Google Sheet feed
(perazim-android docs/CONTENT_GUIDE.md), so the Android app can read the
published CSV URLs without code changes.

This script validates every CSV, writes a matching JSON file to data/
for the web app (plus data/manifest.json), and renders the website's
content blocks. Any HTML page can hold a block like

    <!-- feed:hymns -->  ...generated...  <!-- /feed:hymns -->

and the script fills it from the feed, so the site stays plain static HTML.

    python3 scripts/build_data.py           # rebuild data/*.json
    python3 scripts/build_data.py --check   # fail if data/*.json is stale
"""
import csv
import html
import re
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "data" / "csv"
OUT_DIR = ROOT / "data"
SCHEMA_VERSION = 1

# Required columns per tab. Extra columns are allowed and passed through.
TABS = {
    "announcements": ["id", "title", "body", "date", "priority", "campus", "active"],
    "events": ["id", "title", "start", "end", "venue", "campus", "description", "active"],
    "hymns": ["id", "title", "writer", "year", "key", "bpm", "tags", "lyrics", "chords", "active"],
    "riddles": ["id", "category", "question", "answer", "xp", "active"],
    "jokes": ["id", "text", "active"],
    "sermons": ["id", "title", "speaker", "date", "series", "scripture", "youtube_url", "audio_url", "active"],
    "verses": ["date", "reference", "text"],
    "campuses": ["id", "name", "area", "service_times", "photo", "active"],
    "config": ["key", "value"],
}
INT_FIELDS = {"bpm", "xp", "year"}


def coerce(key, value):
    value = value.strip()
    if key == "active":
        return value.upper() != "FALSE"
    if key in INT_FIELDS and value.lstrip("-").isdigit():
        return int(value)
    return value


def load_tab(name, required):
    path = CSV_DIR / f"{name}.csv"
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        missing = [c for c in required if c not in header]
        if missing:
            raise SystemExit(f"{path.name}: missing columns {missing}")
        rows = [{k: coerce(k, v or "") for k, v in row.items()} for row in reader]
    key = "key" if name == "config" else "date" if name == "verses" else "id"
    seen = set()
    for row in rows:
        if not row.get(key):
            raise SystemExit(f"{path.name}: a row has an empty '{key}'")
        if row[key] in seen:
            raise SystemExit(f"{path.name}: duplicate {key} '{row[key]}'")
        seen.add(row[key])
    if name == "config":
        return {r["key"]: r["value"] for r in rows}
    # Inactive rows stay in the CSV (so editors can switch them back on)
    # but are left out of the JSON that apps render.
    return [r for r in rows if r.get("active", True) is not False]


def esc(value):
    return html.escape(str(value), quote=True)


def youtube_id(url):
    m = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def html_sermons(items):
    out = []
    for s in items:
        vid = youtube_id(s["youtube_url"])
        href = s["youtube_url"] or s["audio_url"] or "#"
        poster = (
            f'<div class="card-poster-img-wrap"><img src="https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" '
            f'alt="Sermon thumbnail: {esc(s["title"])}" loading="lazy" class="card-poster-img" />'
            '<div class="card-poster-overlay"></div></div>'
            if vid else ""
        )
        series = f' — {esc(s["series"])}' if s["series"] else ""
        scripture = f'<p class="message-sub">{esc(s["scripture"])}</p>' if s["scripture"] else ""
        out.append(
            f'<article class="tilt-card message-card" data-tilt><a href="{esc(href)}" target="_blank" rel="noopener" '
            f'aria-label="Watch {esc(s["title"])}" class="sermon-link">{poster}<div class="message-card-body">'
            f'<h3 class="message-title">{esc(s["title"])}</h3>'
            f'<p class="message-sub"><strong>{esc(s["speaker"])}</strong>{series}</p>{scripture}'
            f'<span class="message-date">{esc(s["date"])}</span></div></a></article>'
        )
    return out


def html_hymns(items):
    out = []
    for h in items:
        meta = " · ".join(esc(x) for x in (h["writer"], h["year"], h["key"]) if x)
        chords = f'<p class="feed-chords">Chords: {esc(h["chords"])}</p>' if h["chords"] else ""
        out.append(
            f'<details class="feed-card" id="{esc(h["id"])}"><summary><span class="feed-title">{esc(h["title"])}</span>'
            f'<span class="feed-meta">{meta}</span></summary>{chords}<pre class="feed-lyrics">{esc(h["lyrics"])}</pre></details>'
        )
    return out


def html_riddles(items):
    return [
        f'<details class="feed-card" id="{esc(r["id"])}"><summary><span class="feed-meta">{esc(str(r["category"]).lower())}</span>'
        f'<span class="feed-title">{esc(r["question"])}</span></summary><p class="feed-answer">{esc(r["answer"])}</p></details>'
        for r in items
    ]


def html_jokes(items):
    return [f'<blockquote class="feed-card feed-joke">{esc(j["text"])}</blockquote>' for j in items]


def html_events(items):
    return [
        f'<article class="feed-card"><span class="feed-meta">{" · ".join(esc(x) for x in (e["start"], e["venue"]) if x)}</span>'
        f'<h3 class="feed-title">{esc(e["title"])}</h3><p class="message-sub">{esc(e["description"])}</p></article>'
        for e in items
    ]


def html_announcements(items):
    return [
        f'<article class="feed-card"><span class="feed-meta">{esc(n["date"])}</span>'
        f'<h3 class="feed-title">{esc(n["title"])}</h3><p class="message-sub">{esc(n["body"])}</p></article>'
        for n in items
    ]


HTML_RENDERERS = {
    "sermons": html_sermons,
    "hymns": html_hymns,
    "riddles": html_riddles,
    "jokes": html_jokes,
    "events": html_events,
    "announcements": html_announcements,
}
EMPTY_TEXT = '<p class="message-sub feed-empty">Nothing here yet. Check back soon.</p>'
BLOCK = re.compile(r"(<!-- feed:(\w+) -->)(.*?)(<!-- /feed:\2 -->)", re.S)


def fill_page(text, feeds):
    def sub(m):
        tab = m.group(2)
        if tab not in HTML_RENDERERS:
            raise SystemExit(f"unknown feed block '{tab}'")
        parts = HTML_RENDERERS[tab](feeds[tab]) or [EMPTY_TEXT]
        return m.group(1) + "\n" + "\n".join(parts) + "\n" + m.group(4)
    return BLOCK.sub(sub, text)


def render(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main():
    check = "--check" in sys.argv
    outputs = {}
    feeds = {}
    manifest = {"schema_version": SCHEMA_VERSION, "tabs": {}}
    for name, required in TABS.items():
        data = load_tab(name, required)
        feeds[name] = data
        outputs[OUT_DIR / f"{name}.json"] = render({"schema_version": SCHEMA_VERSION, name: data})
        manifest["tabs"][name] = {
            "json": f"data/{name}.json",
            "csv": f"data/csv/{name}.csv",
            "count": len(data),
        }
    outputs[OUT_DIR / "manifest.json"] = render(manifest)

    for page in sorted(ROOT.glob("**/*.html")):
        if ".git" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        if "<!-- feed:" in text:
            outputs[page] = fill_page(text, feeds)

    stale = []
    for path, text in outputs.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            stale.append(path.relative_to(ROOT))
            if not check:
                path.write_text(text, encoding="utf-8")
    if check and stale:
        print("Out of date, run: python3 scripts/build_data.py")
        for p in stale:
            print("  ", p)
        sys.exit(1)
    print(("checked " if check else "built ") + f"{len(outputs)} files" + (f", updated {len(stale)}" if stale and not check else ""))


if __name__ == "__main__":
    main()
