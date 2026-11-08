#!/usr/bin/env python3
import os, re, glob, html, datetime, markdown
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "docs")
import json
_c = json.load(open(os.path.join(ROOT, "config.json"))) if os.path.exists(os.path.join(ROOT, "config.json")) else {}
CFG = {"name": "أمانكم", "tagline": "دليلك لحماية خصوصيتك وحساباتك على الإنترنت",
       "url": _c.get("site_url", "https://example.com"), "adsense": _c.get("adsense_id", "")}
CSS = """:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--ac:#0b6e4f;--card:#f6f8f7}
@media(prefers-color-scheme:dark){:root{--bg:#121614;--fg:#eee;--mut:#9aa;--ac:#4fd1a1;--card:#1c221f}}
*{box-sizing:border-box}body{margin:0;font:18px/1.9 system-ui,"Segoe UI",Tahoma,sans-serif;background:var(--bg);color:var(--fg)}
header,main,footer{max-width:760px;margin:auto;padding:16px}header{border-bottom:1px solid var(--card)}
header a{color:var(--ac);font-size:1.6em;font-weight:700;text-decoration:none}.t{color:var(--mut);margin:0}
nav a{margin-inline-end:14px;color:var(--fg)}.card{background:var(--card);border-radius:12px;padding:14px 18px;margin:14px 0}
.card h2{margin:0 0 6px;font-size:1.15em}.card a{color:var(--ac);text-decoration:none}.m{color:var(--mut);font-size:.85em}
h1{line-height:1.4}h2,h3{color:var(--ac)}footer{color:var(--mut);font-size:.85em;border-top:1px solid var(--card);margin-top:30px}"""
def page(title, body, desc="", path="/"):
    ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CFG["adsense"]}" crossorigin="anonymous"></script>' if CFG["adsense"] else ""
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | {CFG['name']}</title>
<meta name="description" content="{html.escape(desc or CFG['tagline'])}"><link rel="canonical" href="{CFG['url']}{path}">
<style>{CSS}</style>{ads}</head><body><header><a href="/">{CFG['name']}</a><p class="t">{CFG['tagline']}</p>
<nav><a href="/">الرئيسية</a><a href="/about.html">من نحن</a><a href="/contact.html">اتصل بنا</a><a href="/privacy.html">الخصوصية</a></nav></header>
<main>{body}</main><footer>© {datetime.date.today().year} {CFG['name']} — المحتوى للتوعية العامة وليس استشارة قانونية أو تقنية متخصصة.</footer></body></html>"""
def parse(fp):
    t = open(fp, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    return meta, m.group(2)
def write(rel, s):
    p = os.path.join(SITE, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)
def main():
    posts = []
    today = datetime.date.today().isoformat()
    for fp in glob.glob(os.path.join(ROOT, "content", "*.md")):
        meta, body = parse(fp)
        if meta.get("date", today) > today: continue
        slug = os.path.basename(fp)[:-3]; meta["slug"] = slug; posts.append((meta, body))
    posts.sort(key=lambda x: x[0]["date"], reverse=True)
    for meta, body in posts:
        h = markdown.markdown(body, extensions=["extra"])
        write(f"{meta['slug']}.html", page(meta["title"], f"<article><h1>{html.escape(meta['title'])}</h1><p class='m'>{meta['date']}</p>{h}</article>", meta.get("description",""), f"/{meta['slug']}.html"))
    cards = "".join(f"<div class='card'><h2><a href='/{m['slug']}.html'>{html.escape(m['title'])}</a></h2><p class='m'>{m['date']}</p><p>{html.escape(m.get('description',''))}</p></div>" for m, _ in posts)
    write("index.html", page("الرئيسية", cards or "<p>قريباً…</p>"))
    for f in ("about", "contact", "privacy"):
        fp = os.path.join(ROOT, "pages", f + ".md")
        if os.path.exists(fp):
            meta, body = parse(fp); write(f"{f}.html", page(meta["title"], markdown.markdown(body, extensions=["extra"]), "", f"/{f}.html"))
    urls = ["/"] + [f"/{m['slug']}.html" for m, _ in posts] + [f"/{f}.html" for f in ("about","contact","privacy")]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{CFG['url']}{u}</loc></url>" for u in urls) + "</urlset>")
    write(".nojekyll", "")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {CFG['url']}/sitemap.xml\n")
    pub = CFG["adsense"].replace("ca-pub-", "pub-")
    if pub: write("ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")
    print(f"built {len(posts)} posts")
if __name__ == "__main__": main()
