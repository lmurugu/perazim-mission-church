#!/usr/bin/env python3
"""Retry elevation with higher prometheus tiers (4) for JS-rendered pages."""
import json, subprocess, re, time, sys

SITES = {
    "elevation": ["https://elevationchurch.org", "https://elevationchurch.org/sermons",
                  "https://elevationchurch.org/events", "https://elevationchurch.org/egroups"],
}

def scrape(url, max_tier=4, fs=1, timeout=90):
    req = {
        "url": url, "max_tier": max_tier, "force_tier": fs,
        "headers": {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"},
        "timeout_seconds": timeout, "min_confidence": 0.2,
        "output_schema": {"type": "object", "properties": {}},
    }
    payload = json.dumps(req).replace('"', '\\"')
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "agent@63.250.59.149",
           f"curl -s -X POST http://127.0.0.1:8000/scrape -H 'Content-Type: application/json' -d \"{payload}\""]
    try:
        out = subprocess.check_output(cmd, text=True, timeout=timeout + 25)
        d = json.loads(out)
        print(f"    [{url}] status={d.get('status')} tier={d.get('final_tier')} html={len(d.get('html') or '')}")
        return d.get("html") or ""
    except Exception as e:
        print(f"    FAIL {url}: {e}")
        return ""

def extract(html, url):
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    title = m.group(1).strip() if m else "?"
    h1s = [re.sub(r"<[^>]+>", "", h).strip()[:110] for h in re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)][:3]
    nav = re.findall(r"<nav[^>]*>(.*?)</nav>", html, re.I | re.S)
    nav_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", nav[0]))[:280] if nav else "?"
    links = re.findall(r"<a[^>]*>([^<]{2,40})</a>", html)
    ctas = [l.strip() for l in links if re.search(r"(watch|visit|give|plan|join|learn|get|start|sign|register|connect|serve|care|growth|back|sermon|event)", l, re.I)][:15]
    foot = re.findall(r"<footer[^>]*>(.*?)</footer>", html, re.I | re.S)
    foot_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", foot[0]))[:350] if foot else "?"
    fonts = re.findall(r"font-family:\s*([^;}{]+)", html)[:4]
    return {"url": url, "title": title[:100], "h1": h1s, "nav": nav_text,
            "ctas": ctas, "footer": foot_text, "fonts": fonts,
            "imgs": len(re.findall(r"<img", html)), "vids": len(re.findall(r"<video", html)),
            "forms": len(re.findall(r"<input|<textarea|<select", html))}

lines = [f"# elevation recon v2 (tier-4 retry) — {time.strftime('%Y-%m-%d %H:%M')}", ""]
for u in SITES["elevation"]:
    html = scrape(u)
    if not html:
        lines.append(f"## {u}\n\nBLOCKED\n")
        continue
    d = extract(html, u)
    lines.append(f"## {u}")
    for k, v in d.items():
        if k in ("imgs", "vids", "forms"):
            lines.append(f"- {k}={v}")
        else:
            lines.append(f"- {k}: {v}")
    lines.append("")
    time.sleep(1)

md = "\n".join(lines)
with open("/home/murugu/perazim-site/recon/recon-elevation.md", "w") as f:
    f.write(md)
print(f"\nWROTE recon-elevation.md ({len(md)} bytes)")