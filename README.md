# Портфолио Вадима Кокшарова

Копия сайта [mrframe.framer.website](https://mrframe.framer.website) в виде статичного HTML — без Framer и без сборки.

- `index.html` — главная: обо мне, награды, мероприятия, AI Production, проекты, лидерство, контакты
- `case.html?event=<slug>` / `case.html?project=<slug>` — страницы мероприятий и проектов
- `assets/data.js` — весь контент (тексты, ссылки, картинки, видео). Правки делаются здесь
- `assets/app.js` — рендер, видео-плеер Vimeo/YouTube, лайтбокс, GIF-обложки по наведению
- `assets/styles.css` — стили

Картинки пока подгружаются с CDN Framer (`framerusercontent.com`). Если Framer-проект удалить, их нужно будет сохранить в `assets/` и поменять ссылки в `data.js`.

Чтобы опубликовать: Settings → Pages → Deploy from branch → `main` / root.
