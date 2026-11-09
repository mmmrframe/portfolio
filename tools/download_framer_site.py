"""Download the published Framer site (all pages + images + fonts) into ./framer-site
so it can be opened locally or hosted elsewhere."""
import re, pathlib, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

SITE = "https://mrframe.framer.website"
OUT = pathlib.Path("framer-site")
HOST = urllib.parse.urlparse(SITE).netloc
IMG_RE = re.compile(r'https://framerusercontent\.com/(images|assets)/([\w.-]+?\.(?:png|jpe?g|gif|webp|svg|avif|woff2?|ttf|otf|mp4|webm))(?:\?[^"\'\s,)]*)?')
UA = {"User-Agent": "Mozilla/5.0 (site backup)"}

def page_file(path):
    path = path.strip("/")
    return OUT / (path + "/index.html" if path else "index.html")

files = {}
def localize(html, depth):
    up = "../" * depth
    def sub(m):
        kind, name = m.group(1), m.group(2)
        files[(kind, name)] = f"https://framerusercontent.com/{kind}/{name}"
        return f"{up}_media/{kind}/{name}"
    html = IMG_RE.sub(sub, html)
    # internal links -> local folders
    html = re.sub(r'href="(?:' + re.escape(SITE) + r')?/([^"#?]*)"', lambda m: f'href="{up}{m.group(1).strip("/") + "/" if m.group(1).strip("/") else ""}index.html"', html)
    return html

seen, queue = set(), ["/"]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    while queue:
        path = queue.pop(0)
        if path in seen: continue
        seen.add(path)
        print("page", path)
        pg.goto(SITE + path, wait_until="networkidle", timeout=90000)
        for _ in range(40):  # scroll so lazy content loads
            pg.mouse.wheel(0, 900); pg.wait_for_timeout(120)
        pg.wait_for_timeout(1500)
        for h in pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)"):
            u = urllib.parse.urlparse(h)
            if u.netloc == HOST and u.path not in seen:
                queue.append(u.path or "/")
        html = pg.content()
        depth = len([s for s in path.strip("/").split("/") if s])
        f = page_file(path); f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(localize(html, depth), encoding="utf-8")
    b.close()

for (kind, name), url in sorted(files.items()):
    f = OUT / "_media" / kind / name
    f.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            f.write_bytes(r.read())
    except Exception as e:
        print("FAILED", url, e)
print(f"{len(seen)} pages, {len(files)} media files")
