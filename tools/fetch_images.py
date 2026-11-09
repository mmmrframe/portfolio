"""Download every image the site uses from the Framer CDN into assets/img
and point assets/data.js at the local copies. Also saves any other image
found on the live Framer pages into assets/img/ for safekeeping."""
import re, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "data.js"
OUT = ROOT / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)
CDN = "https://framerusercontent.com/images/"
SITE = "https://mrframe.framer.website"
PAGES = ["/", "/events/soc-forum", "/events/cipr", "/events/spief", "/events/eef",
         "/projects/b2c", "/projects/clips", "/projects/editing", "/projects/ngfw", "/projects/rebrand"]
UA = {"User-Agent": "Mozilla/5.0 (portfolio mirror)"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

src = DATA.read_text(encoding="utf-8")
names = set(re.findall(r'"([A-Za-z0-9_-]+\.(?:png|jpe?g|gif|webp|svg))"', src))
names |= set(re.findall(r'IMG \+ "([^"]+)"', src))

for path in PAGES:
    try:
        html = get(SITE + path).decode("utf-8", "ignore")
        names |= set(re.findall(r'framerusercontent\.com/images/([A-Za-z0-9_-]+\.(?:png|jpe?g|gif|webp|svg))', html))
    except Exception as e:
        print("skip page", path, e)

ok = 0
for n in sorted(names):
    f = OUT / n
    if f.exists() and f.stat().st_size:
        ok += 1; continue
    try:
        f.write_bytes(get(CDN + n)); ok += 1; print("saved", n)
    except Exception as e:
        print("FAILED", n, e)
print(f"{ok}/{len(names)} images in assets/img")

new = src.replace('const IMG = "https://framerusercontent.com/images/";', 'const IMG = "assets/img/";')
if new != src:
    DATA.write_text(new, encoding="utf-8"); print("data.js now uses local images")
