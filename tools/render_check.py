"""Serve a checkout of the site at http://localhost:8000/portfolio/ and record console errors + screenshots."""
import sys, json, pathlib, threading, http.server, functools, socketserver
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(sys.argv[1]).resolve(); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
pages = [("" if a == "home" else a) for a in sys.argv[3:]] or [""]
serve = ROOT.parent / "_serve"; serve.mkdir(exist_ok=True)
link = serve / "portfolio"
if not link.exists(): link.symlink_to(ROOT, target_is_directory=True)
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(serve))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
report = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for path in pages:
        pg = b.new_page(viewport={"width": 1440, "height": 900}); logs = []
        pg.on("console", lambda m, logs=logs: logs.append(f"{m.type}: {m.text}"[:400]) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e, logs=logs: logs.append(f"pageerror: {e}"[:600]))
        pg.on("requestfailed", lambda r, logs=logs: logs.append(f"failed: {r.url[:160]} {r.failure}"))
        pg.goto("http://localhost:8000/portfolio/" + path, wait_until="load", timeout=60000)
        for _ in range(30): pg.mouse.wheel(0, 700); pg.wait_for_timeout(150)
        pg.wait_for_timeout(4000)
        name = (path.strip("/").replace("/", "_") or "home")
        pg.screenshot(path=str(OUT / f"{name}.jpg"), full_page=True, quality=60, type="jpeg")
        report[path or "/"] = {"logs": logs[:40], "url": pg.url, "title": pg.title()}
        pg.close()
    b.close()
(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=1)[:6000])
