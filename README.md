# Telegram Bot — Gubkin Schedule

## Описание проекта

Telegram-бот для получения расписания занятий через API университета.
Бот реализован на базе aiogram и использует:

* Python 3.14.3
* `aiohttp` — для webhook-сервера
* PostgreSQL — для хранения данных
* Redis — для кэширования, FSM и вспомогательных задач
* Docker + Docker Compose — для запуска окружения

Проект распространяется как open-source.
# ВНИМАНИЕ!

Бот не является официальным и не претендует на право называть себя официальным. Он лишь получает расписание с сайта и передаёт его пользователям.

---

# Технологический стек

* Python 3.14.3
* aiogram
* aiohttp
* PostgreSQL
* Redis
* Docker Compose

---

# Конфигурация

Все параметры настраиваются через `.env`.

Рекомендуется создать файл `.env` на основе `.env.example`.

Пример ключевых переменных:

```env
# Bot
TG_BOT_TOKEN=your_telegram_bot_token
TG_BOT_DROP_PENDING_UPDATES=True
TG_BOT_USE_WEBHOOK=True|False  # polling if False

# WebApp (use default as in .env.example if using polling-mode)
WEBAPP_HOST="0.0.0.0"
WEBAPP_PORT=8081

# Webhook (use default as in .env.example if using polling-mode)
WEBHOOK_BASE_URL="https://abcd"
WEBHOOK_PATH="/bots/webhook"

# Postgres
POSTGRES_DB=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_DATABASE=1
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=default
```

## Режимы работы

Переключение между режимами осуществляется через:

```env
TG_BOT_USE_WEBHOOK=True
```

или

```env
TG_BOT_USE_WEBHOOK=False
```

Выбор compose-файла не влияет на режим работы бота.

---

# Запуск проекта

## 1. Разработка

```bash
docker compose -f docker-compose.dev.yml up --build
```

Предназначено для локальной разработки.
Обычно используется режим polling.

---

## 2. Разработка с watch-files

```bash
docker compose -f docker-compose.dev.yml watch
```

Используется механизм отслеживания изменений файлов Docker Compose v2.
Позволяет автоматически пересобирать контейнер при изменении исходного кода (необходимо перезапускать контейнер после изменений в коде. При изменении зависимостей в pyproject.toml образ автоматически будет создан заново).

---

## 3. Production

```bash
docker compose up -d
```

Используется для развертывания на сервере.

---

# Webhook: требования и рекомендации

Для режима `webhook` обязательно:

* наличие публичного домена
* действующий SSL-сертификат
* доступность сервера из интернета

Рекомендуемая конфигурация:

* Nginx — как reverse proxy
* Certbot — для получения и автоматического продления TLS-сертификата

Сертификаты должны быть установлены на хосте, а не внутри контейнера.

Общая схема:

```
Internet
   ↓
Nginx (TLS termination)
   ↓
Docker container (aiohttp webhook server)
```

---

# Сервисы

## PostgreSQL

Используется для постоянного хранения данных.

Данные сохраняются через Docker volume, что обеспечивает их сохранность при перезапуске контейнеров.

## Redis

Используется для aiogram FSM, кэширования и ускорения работы с API.

Также подключён через volume для сохранения данных при перезапуске.

---

# Volumes

В `docker-compose` используются именованные volumes:

* для хранения данных PostgreSQL
* для хранения данных Redis

Это гарантирует:

* сохранность данных при пересборке контейнеров
* изоляцию состояния от жизненного цикла контейнера

Удаление контейнеров не удаляет данные.
Для полного сброса требуется удаление volumes вручную.

---

# Точка входа

Основной способ запуска — через Docker Compose.

Альтернативно возможно прямое выполнение:

```bash
python main.py
```

В этом случае требуется:

* локально запущенный PostgreSQL
* локально запущенный Redis
* корректно настроенный `.env`

---

# Безопасность

Рекомендуется:

* не коммитить `.env` в репозиторий
* использовать `.env.example`
* хранить `BOT_TOKEN` вне системы контроля версий
* ограничивать доступ к базе данных извне
* использовать TLS при работе webhook

---

# Лицензия

Проект распространяется под лицензией MIT License (если иное не указано в файле LICENSE).

---

# Поддержка и развитие

Проект допускает расширение функциональности:

* добавление новых источников расписания
* улучшение кэширования
* оптимизация работы с API

При внесении изменений рекомендуется придерживаться семантического версионирования и поддерживать обратную совместимость публичных интерфейсов.
