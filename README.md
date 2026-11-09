# Портфолио Вадима Кокшарова

Копия сайта [mrframe.framer.website](https://mrframe.framer.website) в виде статичного HTML — без Framer и без сборки.

- `index.html` — главная: обо мне, награды, мероприятия, AI Production, проекты, лидерство, контакты
- `case.html?event=<slug>` / `case.html?project=<slug>` — страницы мероприятий и проектов
- `assets/data.js` — весь контент (тексты, ссылки, картинки, видео). Правки делаются здесь
- `assets/app.js` — рендер, видео-плеер Vimeo/YouTube, лайтбокс, GIF-обложки по наведению
- `assets/styles.css` — стили

Все картинки лежат в `assets/img/` (скопированы с Framer). Анимированные обложки переведены из GIF в MP4 — так они весят в 5–10 раз меньше.

Чтобы опубликовать: Settings → Pages → Deploy from branch → `main` / root.
