(() => {
  const S = window.SITE;
  const $ = (s, r = document) => r.querySelector(s);
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const md = s => esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  const isGif = u => /\.gif(\?|$)/i.test(u || "");
  const touch = matchMedia("(hover: none)").matches;

  // ---------- video helpers ----------
  function embedUrl(url) {
    if (!url) return null;
    let m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{6,})/);
    if (m) return `https://www.youtube-nocookie.com/embed/${m[1]}?autoplay=1&rel=0`;
    m = url.match(/vimeo\.com\/(\d+)/);
    if (m) return `https://player.vimeo.com/video/${m[1]}?autoplay=1&title=0&byline=0&portrait=0`;
    return null;
  }
  function videoBlock(url, poster, label = "Смотреть") {
    const src = embedUrl(url);
    if (!src) return "";
    return `<div class="embed" data-src="${esc(src)}">${poster ? `<img src="${esc(poster)}" alt="" loading="lazy">` : ""}<button type="button" aria-label="${esc(label)}"><span><i class="play-ico"></i>${esc(label)}</span></button></div>`;
  }
  document.addEventListener("click", e => {
    const b = e.target.closest(".embed button");
    if (!b) return;
    const box = b.parentElement;
    box.innerHTML = `<iframe src="${box.dataset.src}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
  });

  // ---------- lightbox ----------
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-zoom]");
    if (b) {
      const lb = document.createElement("div");
      lb.className = "lightbox";
      lb.innerHTML = `<img src="${esc(b.dataset.zoom)}" alt="">`;
      lb.onclick = () => lb.remove();
      document.body.appendChild(lb);
    }
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape") document.querySelectorAll(".lightbox").forEach(n => n.remove()); });

  // ---------- GIF covers: still first frame, play on hover / when in view on touch ----------
  function gifCover(img) {
    if (!isGif(img.src)) return;
    const canvas = document.createElement("canvas");
    const draw = () => { canvas.width = img.naturalWidth; canvas.height = img.naturalHeight; canvas.getContext("2d").drawImage(img, 0, 0); };
    if (img.complete && img.naturalWidth) draw(); else img.addEventListener("load", draw, { once: true });
    img.after(canvas);
    img.style.visibility = "hidden";
    const card = img.closest(".folder, .event") || img.parentElement;
    const play = on => { img.style.visibility = on ? "visible" : "hidden"; canvas.style.visibility = on ? "hidden" : "visible"; };
    card.addEventListener("mouseenter", () => play(true));
    card.addEventListener("mouseleave", () => play(false));
    card._play = play;
  }
  if (touch && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(es => es.forEach(en => {
      en.target.classList.toggle("open", en.isIntersecting);
      en.target._play && en.target._play(en.isIntersecting);
    }), { rootMargin: "-35% 0px -35% 0px" });
  }

  function card(href, cover, tab, title, text, cls = "folder") {
    const media = /\.mp4$/i.test(cover)
      ? `<video src="${esc(cover)}" poster="${esc(cover.replace(/\.mp4$/i, ".jpg"))}" muted loop playsinline preload="metadata"></video>`
      : `<img src="${esc(cover)}" alt="" loading="lazy">`;
    return `<a class="${cls === "folder" ? "" : cls + " "}folder" href="${href}">
      <span class="tab">${esc(tab)}</span>
      <div class="preview">${media}<div class="shade"></div><span class="ovl">Открыть →</span></div>
      <h3>${esc(title)}</h3><p>${esc(text)}</p></a>`;
  }
  // MP4 covers: poster frame at rest, play on hover / when scrolled into view on touch
  function videoCover(v, c) {
    const play = on => { if (on) v.play().catch(() => {}); else v.pause(); };
    c.addEventListener("mouseenter", () => play(true));
    c.addEventListener("mouseleave", () => play(false));
    c._play = play;
  }
  function wireCards(root) {
    root.querySelectorAll(".folder").forEach(c => {
      const img = c.querySelector(".preview img"), v = c.querySelector(".preview video");
      if (img) gifCover(img);
      if (v) videoCover(v, c);
      if (io) io.observe(c);
    });
  }

  // =========== HOME ===========
  if ($("#roles")) {
    $("#roles").innerHTML = S.roles.map((r, i) => `<span${i === 1 ? ' class="ai"' : ""}>${esc(r)}</span>`).join("");
    $("#intro").innerHTML = S.intro.map((p, i) => `<p class="${i ? "muted" : "lead"}">${esc(p)}</p>`).join("");
    $("#metrics").innerHTML = S.metrics.map(([b, t]) => `<div class="metric"><b>${esc(b)}</b><span>${esc(t)}</span></div>`).join("");

    const clients = S.clients.map(c => `<span class="client" title="${esc(c.name)}">${c.logo ? `<img src="${esc(c.logo)}" alt="${esc(c.name)}">` : esc(c.name)}</span>`).join("");
    $("#marquee").innerHTML = clients + clients;

    $("#aboutText").innerHTML = S.about.map(p => `<p>${esc(p)}</p>`).join("");
    $("#pillars").innerHTML = S.pillars.map(p => `<div class="pillar"><span class="label">${esc(p.k)}</span><h3>${esc(p.t)}</h3><p>${esc(p.d)}</p></div>`).join("");
    const leaf = `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M16 40C8 34 6 22 12 10"/><path d="M32 40c8-6 10-18 4-30"/><path d="M11 30c-4-1-6-4-6-7 3 0 6 2 7 5M9 21c-3-2-4-5-3-8 3 1 5 4 5 7M12 13c-1-3 0-6 2-8 2 2 2 5 1 8"/><path d="M37 30c4-1 6-4 6-7-3 0-6 2-7 5M39 21c3-2 4-5 3-8-3 1-5 4-5 7M36 13c1-3 0-6-2-8-2 2-2 5-1 8"/></svg>`;
    $("#laurels").innerHTML = S.awards.map(a => `<div class="laurel">${leaf}<b>${esc(a.y)}</b><span>${esc(a.t)}</span></div>`).join("");
    const pr = $("#press");
    pr.href = S.press.href;
    pr.innerHTML = `<span class="label">${esc(S.press.meta)}</span><b>${esc(S.press.title)}</b><span>${esc(S.press.note)}</span><span style="color:var(--text)">Читать →</span>`;

    // about: words light up as you scroll
    const paras = [...document.querySelectorAll("#aboutText p")];
    const onScroll = () => { const y = innerHeight * 0.7; paras.forEach(p => p.classList.toggle("on", p.getBoundingClientRect().top < y)); };
    addEventListener("scroll", onScroll, { passive: true }); onScroll();

    $("#eventList").innerHTML = S.events.map(e => card(`case.html?event=${e.slug}`, e.cover, e.full, e.name, e.desc, "event")).join("");
    $("#projectList").innerHTML = S.projects.map(p => card(`case.html?project=${p.slug}`, p.cover, p.name, p.title, p.sub, "proj")).join("");
    wireCards(document);

    const A = S.ai;
    $("#aiGrid").innerHTML = `
      <div class="ai-side"><h2>${esc(A.title)}</h2><p class="lead muted">${esc(A.text)}</p>
        <div class="ai-big"><b>${esc(A.big)}</b><span>${esc(A.bigLabel)}</span></div></div>
      <div class="ai-groups">${A.groups.map(([g, items]) => `<div class="grp"><span class="label">${esc(g)}</span><ul>${items.map(i => `<li>${esc(i)}</li>`).join("")}</ul></div>`).join("")}
        <div class="ai-result"><span class="label">Результат</span><ul>${A.result.map(r => `<li>${esc(r)}</li>`).join("")}</ul></div></div>`;

    const L = S.lead;
    $("#leadTitle").textContent = L.title;
    $("#leadGrid").innerHTML = `
      <div class="meet"><img src="${esc(L.community.img)}" alt="" loading="lazy"><div class="meet-text"><span class="label">Сообщество</span><h3>${esc(L.community.name)}</h3><p>${esc(L.community.text)}</p><div class="roles">${L.community.roles.map(r => `<span>${esc(r)}</span>`).join("")}</div></div></div>
      <div class="side"><div class="talk"><span class="label">Выступления</span><ul>${L.talks.map(([t, s]) => `<li>${esc(t)}<span>${esc(s)}</span></li>`).join("")}</ul></div>
        <div class="media">${L.media.map(m => `<a href="${esc(m.href)}" target="_blank" rel="noopener"><span>${esc(m.k)}</span><b>${esc(m.t)}</b></a>`).join("")}</div></div>`;

    $("#contacts").innerHTML = S.contacts.map(c => `<a href="${esc(c.href)}" target="_blank" rel="noopener"><span>${esc(c.k)}</span><b>${esc(c.t)}</b></a>`).join("");
  }

  // =========== CASE PAGE ===========
  const root = $("#case");
  if (root) {
    const q = new URLSearchParams(location.search);
    const rich = blocks => `<div class="rich">${blocks.map(b => b.ul ? `<ul>${b.ul.map(li => `<li>${md(li)}</li>`).join("")}</ul>` : `<p>${md(b.p)}</p>`).join("")}</div>`;
    const ev = S.events.find(e => e.slug === q.get("event"));
    const pr = S.projects.find(p => p.slug === q.get("project"));

    if (ev) {
      document.title = `${ev.name} — Вадим Кокшаров`;
      const vid = ev.sections.find(s => s.v)?.v;
      root.innerHTML = `
        <div class="case-hero"><a class="back" href="index.html#events">← Мероприятия</a><h1>${esc(ev.name)}</h1><p>${esc(ev.full)}</p></div>
        ${vid ? videoBlock(vid, ev.sections[0].img, "Смотреть интро") : `<div class="embed"><img src="${esc(ev.cover)}" alt=""></div>`}
        <div class="dive-stats"><div><b>${esc(ev.screens)}</b><span>экранов</span></div><div><b>${esc(ev.zones)}</b><span>зон</span></div><div><b>${esc(ev.visitors)}</b><span>посетителей</span></div></div>
        ${ev.about.length ? `<div class="block"><span class="label">Описание</span>${rich(ev.about)}</div>` : `<p class="muted">${esc(ev.desc)}</p>`}
        <div class="block dive-items">${ev.sections.map((s, i) => `
          <div class="ditem"><div class="preview" data-zoom="${esc(s.img)}" style="cursor:zoom-in"><img src="${esc(s.img)}" alt="" loading="lazy"></div>
            <div class="txt"><span class="idx">${String(i + 1).padStart(2, "0")}</span><h3>${esc(s.t)}</h3><p class="muted">${esc(s.d)}</p>
            ${s.n ? `<div class="n"><b>${esc(s.n)}</b><span>${esc(s.c)}</span></div>` : ""}</div></div>`).join("")}</div>
        ${ev.materials.length ? `<div class="block"><span class="label">Материалы</span><div class="shots">${ev.materials.map(m => `<figure class="shot"><button type="button" data-zoom="${esc(m.img)}"><img src="${esc(m.img)}" alt="${esc(m.c)}" loading="lazy"></button><figcaption>${esc(m.c)}</figcaption></figure>`).join("")}</div></div>` : ""}
        ${nextLinks(S.events, ev, "event")}`;
    } else if (pr) {
      document.title = `${pr.title} — Вадим Кокшаров`;
      const facts = [["Цель", pr.goal], ["Задача", pr.task], ["Сроки", pr.time], ["Результат", pr.result], ["Команда", pr.team]];
      root.innerHTML = `
        <div class="case-hero"><a class="back" href="index.html#projects">← Проекты</a><span class="label" style="display:block;color:var(--accent);margin-bottom:12px">${esc(pr.name)}</span><h1>${esc(pr.title)}</h1><p>${esc(pr.sub)}</p></div>
        ${videoBlock(pr.video, pr.poster, "Смотреть ролик")}
        <dl class="dive-facts">${facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>
        <div class="block"><span class="label">Описание</span>${rich(pr.about)}</div>
        <div class="block"><span class="label">Кадры</span><div class="shots">${pr.gallery.map(g => `<figure class="shot"><button type="button" data-zoom="${esc(g)}"><img src="${esc(g)}" alt="" loading="lazy"></button></figure>`).join("")}</div></div>
        ${nextLinks(S.projects, pr, "project")}`;
    } else {
      root.innerHTML = `<div class="case-hero"><h1>Не найдено</h1><p><a href="index.html">Вернуться на главную</a></p></div>`;
    }
  }

  function nextLinks(list, cur, key) {
    const i = list.indexOf(cur);
    const prev = list[(i - 1 + list.length) % list.length], next = list[(i + 1) % list.length];
    return `<div class="dive-next"><a class="btn" href="case.html?${key}=${prev.slug}">← ${esc(prev.name)}</a><a class="btn" href="case.html?${key}=${next.slug}">${esc(next.name)} →</a></div>`;
  }
})();
