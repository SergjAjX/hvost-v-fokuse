# 🐾 Хвост в Фокусе | Сайт-визитка Telegram канала

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-222222?style=for-the-badge&logo=github)](https://sergjajx.github.io/hvost-v-fokuse/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

Одностраничный адаптивный сайт (Dashboard), который **автоматически** подтягивает и отображает последние посты из публичного Telegram-канала [@HVOST_V_FOKUSE](https://t.me/HVOST_V_FOKUSE). 

🔗 **Живой сайт:** [https://sergjajx.github.io/hvost-v-fokuse/](https://sergjajx.github.io/hvost-v-fokuse/)

---

## ✨ Возможности

- 🔄 **Полная автоматизация:** Сайт обновляется самостоятельно каждый час с помощью GitHub Actions.
- 📱 **Адаптивный дизайн:** Идеально выглядит на смартфонах, планшетах и ПК (используется Tailwind CSS).
- 🖼️ **Умный парсинг медиа:** Скрипт корректно извлекает текст, одиночные фото, альбомы и ссылки, игнорируя аватарки канала и системные сообщения.
- 🚀 **SEO и AI-оптимизация:** Встроены мета-теги Open Graph и структурированные данные JSON-LD для лучшей индексации поисковиками и ИИ-ассистентами.
- 📊 **Аналитика:** Готовые места для вставки кодов Яндекс.Метрики и Google Analytics 4.
- 🔒 **Безопасность:** Работает через парсинг публичной веб-версии канала (`t.me/s/`), не требует хранения чувствительных токенов для базовой функциональности.

---

## ⚙️ Как это работает (Архитектура)

Проект работает по принципу **Jamstack** (без классического бэкенда):

1. **GitHub Actions** по расписанию (cron: `0 * * * *`, каждый час) запускает Python-скрипт `fetch_posts.py`.
2. Скрипт с помощью библиотек `requests` и `BeautifulSoup4` обращается к публичной веб-версии канала.
3. Он находит последние 5 сообщений, извлекает дату, текст, прямые ссылки на изображения (из `tgme_widget_message_bubble`) и ссылки на посты.
4. Данные сохраняются в файл `posts.json` прямо в репозитории.
5. Файл `index.html` при загрузке страницы делает fetch-запрос к `posts.json` и динамически отрисовывает красивые карточки постов.

---

## 📂 Структура проекта

```text
├── .github/
│   └── workflows/
│       └── update-posts.yml      # Конфигурация автоматического запуска скрипта
├── _headers                      # Настройки CORS и отключения кэширования для GitHub Pages
├── fetch_posts.py                # Python-скрипт для парсинга Telegram
├── index.html                    # Главный файл сайта (Frontend)
├── posts.json                    # Файл с данными (генерируется автоматически, не редактировать вручную)
└── README.md                     # Этот файл
```

---

## 🚀 Как развернуть такой же сайт для своего канала

Если вы хотите использовать этот шаблон для своего Telegram-канала:

1. Нажмите кнопку **Fork** в правом верхнем углу этого репозитория.
2. В своем форке перейдите в **Settings > Secrets and variables > Actions** и добавьте:
   - `CHANNEL`: Имя вашего канала (например, `my_awesome_channel`).
3. Откройте файл `fetch_posts.py` и убедитесь, что переменная `CHANNEL_NAME` использует ваш секрет (или замените значение по умолчанию).
4. Откройте `index.html` и замените:
   - Название канала и описания.
   - Ссылки на администраторов (поиск по `@admin`).
   - ID счетчиков в блоках `<head>` (Яндекс.Метрика и Google Analytics).
5. Перейдите в **Settings > Pages** и включите GitHub Pages (Source: `GitHub Actions` или ветка `main`).
6. Вручную запустите Workflow во вкладке **Actions**, чтобы создать первый `posts.json`.

---

## 🛠 Используемые технологии

- **Backend (Automation):** Python 3.11, BeautifulSoup4, Requests, GitHub Actions
- **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS (через CDN)
- **Hosting:** GitHub Pages

---

## 👑 Контакты

По вопросам сотрудничества, рекламы и предложениям:
- Telegram: [@nkt_gert](https://t.me/nkt_gert)

---
*Сделано с ❤️ для сообщества "Хвост в Фокусе".*
<p>Сделано с ❤️ для сообщества <a href="https://sergjajx.github.io/hvost-v-fokuse/" target="_blank">«Хвост в Фокусе»</a>.</p>
