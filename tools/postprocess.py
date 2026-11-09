"""Apply the GitHub-copy tweaks to a fresh Framer snapshot (idempotent).

Usage: python tools/postprocess.py <site_dir>
  1. removes Framer editor bar + analytics scripts
  2. hides the "Made in Framer" badge
  3. sets page titles and descriptions (tools/inject/titles.json), replaces the Framer favicon with the MeetMotion logo (tools/inject/favicon.html)
  4. puts the MeetMotion logo into the Meet Motion card via CSS (survives Framer re-render)
  5. applies text edits made on GitHub (tools/inject/text-overrides.html: HTML + a guard against Framer re-render)
  6. adds the on-page showreel player (tools/inject/showreel.html)
  7. optimizes media: GIF -> animated WebP (800px, q72), PNG/JPG -> WebP (q82, max 2400px);
     animated covers keep a "?a.gif" suffix so the Framer hover override still treats them as GIFs
"""
import re, sys, json, html, pathlib, subprocess
from PIL import Image

SITE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
INJ = pathlib.Path(__file__).parent / "inject"
BADGE = (INJ / "hide-badge.html").read_text(encoding="utf-8").strip()
FAV = (INJ / "favicon.html").read_text(encoding="utf-8").strip()
TITLES = json.loads((INJ / "titles.json").read_text(encoding="utf-8"))
MEET = (INJ / "meetmotion.html").read_text(encoding="utf-8").strip()
TXT = (INJ / "text-overrides.html").read_text(encoding="utf-8").strip()
REEL = (INJ / "showreel.html").read_text(encoding="utf-8").strip()
IMG = SITE / "_media" / "images"

ren = {}
if IMG.exists():
    for f in sorted(IMG.iterdir()):
        ext, before = f.suffix.lower(), f.stat().st_size
        if ext == ".gif":
            out = f.with_suffix(".webp"); w = Image.open(f).size[0]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", f"scale={min(w, 800)}:-1:flags=lanczos",
                            "-c:v", "libwebp_anim", "-lossless", "0", "-q:v", "72", "-compression_level", "6", "-loop", "0", str(out)], check=True)
            ren[f.name] = out.name + "?a.gif"
        elif ext in (".png", ".jpg", ".jpeg"):
            im = Image.open(f); im.load()
            if im.size[0] > 2400: im = im.resize((2400, round(im.size[1] * 2400 / im.size[0])), Image.LANCZOS)
            if im.mode not in ("RGB", "RGBA"): im = im.convert("RGBA" if im.mode in ("LA", "P") or "transparency" in im.info else "RGB")
            out = f.with_suffix(".webp"); im.save(out, "WEBP", quality=82, method=6)
            if out.stat().st_size >= before: out.unlink(); continue
            ren[f.name] = out.name
        else:
            continue
        print(f"{before/1e3:9.0f}KB -> {out.stat().st_size/1e3:8.0f}KB  {f.name}")
        f.unlink()

for h in SITE.rglob("*.html"):
    s = h.read_text(encoding="utf-8")
    s = s.replace("https://vimeo.com/76979871", "https://vimeo.com/330892454")
    s = re.sub(r'<script[^>]*src="https://(?:events\.framer\.com|framer\.com/edit)[^"]*"[^>]*>\s*</script>', "", s)
    s = re.sub(r'_media/images/([A-Za-z0-9_-]+\.(?:gif|png|jpe?g))', lambda m: "_media/images/" + ren.get(m.group(1), m.group(1)), s)
    key = str(h.parent.relative_to(SITE)).replace("\\", "/").strip(".")
    if key in TITLES:
        t = TITLES[key] if key == "" else TITLES[key] + TITLES["_suffix"]
        t, d = html.escape(t, quote=True), html.escape(TITLES["_description"], quote=True)
        s = re.sub(r"<title>[^<]*</title>", f"<title>{t}</title>", s, count=1)
        s = re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*"', lambda m: m.group(1) + t + '"', s)
        s = re.sub(r'(<meta (?:property|name)="(?:description|og:description|twitter:description)" content=")[^"]*"', lambda m: m.group(1) + d + '"', s)
    s = re.sub(r'<link[^>]*href="https://framerusercontent\.com/sites/icons/[^"]*"[^>]*>', "", s)
    if "_media/favicon.png" not in s: s = s.replace("</head>", FAV + "</head>", 1)
    if 'id="meetmotion-card"' not in s and 'data-framer-name="Meet Motion"' in s: s = s.replace("</head>", MEET + "</head>", 1)
    if 'id="hide-framer-badge"' not in s: s = s.replace("</head>", BADGE + "</head>", 1)
    m = re.search(r'var MAP=(\{.*?\});', TXT)
    for old, new in json.loads(m.group(1)).items(): s = s.replace(old, new)
    if 'id="text-overrides"' not in s: s = s.replace("</body>", TXT + "</body>", 1)
    if 'id="reel-js"' not in s: s = s.replace("</body>", REEL + "</body>", 1)
    h.write_text(s, encoding="utf-8")
print("postprocess done:", len(ren), "media files converted")
