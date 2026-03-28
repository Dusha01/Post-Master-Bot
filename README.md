<div align="center">

# Post Master Bot

**Почта → Telegram.** Асинхронный бот на [aiogram](https://github.com/aiogram/aiogram) слушает почтовые ящики по **IMAP IDLE** (Gmail и Яндекс) и доставляет уведомления о новых письмах в выбранный чат.

![Python](https://img.shields.io/badge/python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=flat&logo=docker&logoColor=white)

<br/>

</div>

---

## Возможности

| | |
|---|---|
| **IMAP IDLE** | Ожидание новых писем без постоянного опроса всего ящика |
| **Gmail и Яндекс** | Два независимых подключения при наличии учётных данных |
| **Формат в Telegram** | Тема, отправитель, текст, подпись отдельно, отметка о вложениях |
| **Управление** | Команды `/pause` и `/resume` для приостановки пересылки |
| **Безопасность** | Команды доступны только пользователю с `ALLOW_USER_ID` |

---

## Быстрый старт

### 1. Telegram

1. Создайте бота у [@BotFather](https://t.me/BotFather), получите токен.
2. Узнайте свой числовой `user_id` (например, через [@userinfobot](https://t.me/userinfobot)).
3. Укажите `CHAT_ID` — куда слать уведомления (личный чат или группа).

### 2. Почта

- **Gmail:** включите двухфакторную аутентификацию и создайте [пароль приложения](https://support.google.com/accounts/answer/185833).
- **Яндекс:** [пароль для внешних приложений](https://yandex.ru/support/id/authorization/app-passwords.html).

Скопируйте `.env.example` в `.env` и заполните переменные (см. таблицу ниже).

### 3. Запуск

**Локально** (Python 3.12+):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Docker** (из корня репозитория):

```bash
cp .env.example .env
# отредактируйте .env
docker compose -f Docker/docker-compose.yml up -d --build
```

---

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от BotFather |
| `CHAT_ID` | ID чата для уведомлений |
| `ALLOW_USER_ID` | ID пользователя, которому разрешены команды бота |
| `TG_PROXY_URL` | Опционально: прокси для Telegram (`socks5://…`, `http://…`) |
| `IMAP_*_GMAIL` / `IMAP_*_YANDEX` | Сервер, порт, логин, пароль, SSL для каждого провайдера |
| `IMAP_IDLE_TIMEOUT_SEC` | Таймаут IMAP IDLE (секунды) |

Пустые логин/пароль для провайдера — этот ящик не подключается.

---

## Команды бота

Команды отвечают только пользователю с `ALLOW_USER_ID`.

| Команда | Действие |
|---------|----------|
| `/start` | Справка |
| `/status` | Текущий статус пересылки |
| `/pause` | Пауза уведомлений о почте |
| `/resume` | Возобновить пересылку |

---


## Стек

- **Python 3.12** · **aiogram 3** · **Pydantic Settings**
- **Docker** · образы в **GHCR**

---

## Лицензия

MIT © 2026 Dusha_01 — см. файл [LICENSE](LICENSE).
