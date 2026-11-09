# Правила для этого репозитория

Это сайт-портфолио Вадима Кокшарова на GitHub Pages: https://mmmrframe.github.io/portfolio/
Вторая копия сайта — во Framer: https://mrframe.framer.website (проект M071zMEHGpaIfIomRmCO).

## Порядок публикации (правило пользователя от 09.11.2026)

1. **Сначала GitHub.** Любую правку вносим в этот репозиторий, коммитим, пушим в `main`
   и ждём успешного деплоя `pages-build-deployment`.
2. **Потом спросить про Framer.** После публикации на GitHub обязательно задать вопрос:
   «Обновить это же во Framer?» — и только после «да» вносить правку во Framer и публиковать там.

GitHub — основная версия. Не перезаписывать `main` снимком из Framer без прямой просьбы:
так пропадут правки, сделанные только на GitHub.

## Устройство

- `index.html`, `events/*/`, `projects/*/` — снимок страниц Framer (скрипты Framer грузятся с framerusercontent.com).
- `_media/` — картинки (WebP) и шрифты. Анимированные обложки — animated WebP со ссылкой `...webp?a.gif`:
  суффикс `.gif` нужен, чтобы ховер-оверрайд Framer показывал первый кадр до наведения.
- Правки поверх снимка (все применяет `tools/postprocess.py`, скрипт идемпотентный):
  убраны скрипты редактора и аналитики Framer, скрыта плашка «Made in Framer»,
  шоурил Vimeo 330892454 открывается во всплывающем плеере (`tools/inject/showreel.html`),
  медиа оптимизированы.
- Новые картинки добавлять сразу в WebP: статичные до 2400 px, q≈82; анимации — animated WebP 800 px, q≈72.

## Если нужно подтянуть изменения из Framer

Только по просьбе пользователя: Actions → «Download Framer site» → Run workflow → снимок появится в ветке
`framer-export` → `python tools/postprocess.py <папка снимка>` → перенести нужные страницы в `main`,
не потеряв правки, сделанные только на GitHub.

## Коммиты

Сообщения коммитов заканчивать строками:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01176ad6wuwrd5pvsTkjeVQs
