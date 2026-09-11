#!/usr/bin/env python3
"""Stage A recon via Prometheus scrape — extract design details from reference church sites.
Runs on VPS where prometheus serves :8000. Writes per-site markdown to /tmp/church_recon/<site>.md
"""
import json, re, subprocess, sys, time

SITES = {
    "vous":     ["https://vouschurch.com", "https://vouschurch.com/blog", "https://vouschurch.com/give", "https://vouschurch.com/growth-track"],
    "passion":  ["https://passioncitychurch.com", "https://passioncitychurch.com/events", "https://passioncitychurch.com/beliefs", "https://passioncitychurch.com/give"],
    "mariners": ["https://marinerschurch.org", "https://marinerschurch.org/visit", "https://marinerschurch.org/anaheim", "https://marinerschurch.org/baptism", "https://marinerschurch.org/hb"],
    "elevation":["https://elevationchurch.org", "https://elevationchurch.org/sermons", "https://elevationchurch.org/events", "https://elevationchurch.org/egroups", "https://elevationchurch.org/ekidz"],
}

def scrape(url, max_tier=3, timeout=60):
    """POST /scrape on prometheus (VPS side). Returns html string."""
    req = {
        "url": url,
        "max_tier": max_tier,
        "force_tier": 1,
        "headers": {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"},
        "timeout_seconds": timeout,
        "min_confidence": 0.2,
        "output_schema": {"type": "object", "properties": {}},
    }
    payload = json.dumps(req).replace('"', '\\"')
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "agent@63.250.59.149",
           f"curl -s -X POST http://127.0.0.1:8000/scrape -H 'Content-Type: application/json' -d \"{payload}\""]
    try:
        out = subprocess.check_output(cmd, text=True, timeout=timeout+20)
        d = json.loads(out)
        return d.get("html") or ""
    except Exception as e:
        print(f"  SCRAPE FAIL {url}: {e}")
        return ""

def extract(html, url):
    """Pull the design-relevant bits from HTML."""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    # title + h1
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    title = m.group(1).strip() if m else "?"
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    h1s = [re.sub(r"<[^>]+>", "", h).strip()[:120] for h in h1s]
    # nav anchors
    nav = re.findall(r"<nav[^>]*>(.*?)</nav>", html, re.I | re.S)
    nav_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", nav[0]))[:300] if nav else "?"
    # CTA-ish links (visible text)
    links = re.findall(r"<a[^>]*>([^<]{2,40})</a>", html)
    ctas = [l.strip() for l in links if re.search(r"(watch|visit|give|plan|join|learn|get|start|sign|register|connect|serve|care|growth|back)", l, re.I)][:15]
    # footer
    foot = re.findall(r"<footer[^>]*>(.*?)</footer>", html, re.I | re.S)
    foot_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", foot[0]))[:400] if foot else "?"
    # font-family from inline style/head (best-effort)
    fonts = re.findall(r"font-family:\s*([^;}{]+)", html)[:5]
    # count images, videos, form inputs
    imgs = len(re.findall(r"<img", html))
    vids = len(re.findall(r"<video", html))
    forms = len(re.findall(r"<input|<textarea|<select", html))
    # distinctive card patterns (list items with img + h3 in one li)
    cards = len(re.findall(r"<li[^>]*>.*?<img.*?<h[234]", html, re.I | re.S))
    return {
        "url": url, "title": title[:100], "h1": h1s[:3], "nav": nav_text[:280],
        "ctas": ctas, "footer": foot_text[:380], "fonts": fonts[:3],
        "img_count": imgs, "video_count": vids, "form_count": forms, "card_patterns_li_img_h": cards,
    }

def main():
    sites_to_run = sys.argv[1] if len(sys.argv) > 1 else None
    for site, urls in SITES.items():
        if sites_to_run and site != sites_to_run:
            continue
        print(f"=== {site} ===")
        out_path = f"/tmp/church_recon/{site}.md"
        lines = [f"# {site} recon — {time.strftime('%Y-%m-%d %H:%M')}", ""]
        for u in urls:
            print(f"  scrape {u}")
            html = scrape(u)
            if not html:
                lines.append(f"## {u}\n\nBLOCKED (no html returned)\n")
                continue
            d = extract(html, u)
            lines.append(f"## {u}")
            lines.append(f"- title: {d['title']}")
            lines.append(f"- h1: {d['h1']}")
            lines.append(f"- nav: {d['nav']}")
            lines.append(f"- ctas: {d['ctas']}")
            lines.append(f"- footer: {d['footer']}")
            lines.append(f"- fonts: {d['fonts']}")
            lines.append(f"- imgs={d['img_count']} videos={d['video_count']} forms={d['form_count']} li_img_h_cards={d['card_patterns_li_img_h']}")
            lines.append("")
            time.sleep(1)
        md = "\n".join(lines)
        # ship md to VPS recon dir
        with open("/tmp/_recon_tmp.md", "w") as f:
            f.write(md)
        subprocess.run(["scp", "-o", "BatchMode=yes", "/tmp/_recon_tmp.md",
                        f"agent@63.250.59.149:{out_path}"], check=False)
        print(f"  wrote {out_path} ({len(md)} bytes)")

if __name__ == "__main__":
    main()