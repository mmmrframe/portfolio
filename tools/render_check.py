"""Serve a checkout of the site at http://localhost:8000/portfolio/ and record console errors + screenshots.
Each page is opened twice: as published, and with our injected scripts removed, to tell which part breaks it."""
import re, sys, json, pathlib, threading, http.server, functools, multiprocessing as mp

def serve(root):
    srvdir = root.parent / "_serve"; srvdir.mkdir(exist_ok=True)
    link = srvdir / "portfolio"
    if not link.exists(): link.symlink_to(root, target_is_directory=True)
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(srvdir))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), H); threading.Thread(target=s.serve_forever, daemon=True).start()

INJ = ["talks-js", "text-overrides", "reel-js"]

def run_one(path, variant, out, q):
    from playwright.sync_api import sync_playwright
    logs = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.set_default_timeout(20000)
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"[:300]) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"[:500]))
        if variant == "stripped":
            def strip(route):
                r = route.fetch(); body = r.text()
                for i in INJ: body = re.sub(r'<script id="' + i + r'">.*?</script>', "", body, flags=re.S)
                route.fulfill(response=r, body=body)
            pg.route(re.compile(r"localhost:8000/portfolio/.*(/|\.html)$"), strip)
        pg.goto(path if path.startswith("http") else "http://localhost:8000/portfolio/" + path, wait_until="load", timeout=45000)
        pg.wait_for_timeout(3000)
        for y in range(0, 12000, 900): pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(120)
        pg.wait_for_timeout(2500)
        stat = pg.evaluate("""() => { const im=[...document.images]; return { stills: im.filter(i=>i.src.startsWith('blob:')).length, animSrc: im.filter(i=>/\\.(gif|webp)(\\?|$)/i.test(i.src)).map(i=>i.src.split('/').pop().slice(0,40)).slice(0,10) } }""")
        logs.append("covers: " + json.dumps(stat))
        name = (re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "home") + "_" + variant
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
        pg.screenshot(path=str(out / f"{name}.jpg"), full_page=True, quality=55, type="jpeg", timeout=30000)
        b.close()
    q.put(logs)

if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1]).resolve(); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    pages = [("" if a == "home" else a) for a in sys.argv[3:]] or [""]
    serve(root); report = {}
    for path in pages:
        for variant in ("as-is", "stripped"):
            q = mp.Queue(); pr = mp.Process(target=run_one, args=(path, variant, out, q)); pr.start(); pr.join(100)
            if pr.is_alive(): pr.kill(); report[f"{path or '/'} [{variant}]"] = "HUNG (page did not respond in 150s)"
            else: report[f"{path or '/'} [{variant}]"] = q.get() if not q.empty() else f"exit {pr.exitcode}"
            print(f"{path or '/'} [{variant}]:", json.dumps(report[f'{path or "/"} [{variant}]'], ensure_ascii=False)[:1500], flush=True)
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
