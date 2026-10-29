# Orders Bot — Telegram-бот приёма заявок

Бот на Python (aiogram 3), который принимает заявки от пользователей,
автоматически записывает их в Google Sheets и отправляет уведомления ответственным.

Упрощённый аналог заявочного модуля CRM: приём данных → фиксация в базе → уведомления.

## Как работает

```
Пользователь         Бот                Google Sheets        Админ
     │                 │                     │                  │
     │── /start ──────▶│                     │                  │
     │── имя ─────────▶│                     │                  │
     │── телефон ─────▶│── строка в таблицу ▶│                  │
     │── комментарий ─▶│── уведомление ──────┼─────────────────▶│
     │◀── «Заявка принята» ─────────────────┘                  │
```

## Функции

- Пошаговый приём заявки (имя → телефон → комментарий) с валидацией
- Автоматическая запись каждой заявки в Google Sheets (таблица заявок)
- Мгновенное уведомление администратора в Telegram о новой заявке
- Подтверждение пользователю с номером заявки

## Стек

- Python 3.10+
- aiogram 3.x (Telegram Bot API)
- gspread + Google Service Account (Google Sheets API)

## Быстрый старт

1. Создай бота через [@BotFather](https://t.me/BotFather), получи токен
2. В [Google Cloud Console](https://console.cloud.google.com) создай Service Account,
   включи Google Sheets API, скачай JSON-ключ
3. Дай боту доступ к таблице (поделись ей на email сервис-аккаунта)

```bash
pip install -r requirements.txt
export BOT_TOKEN="123456:ABC..."   # токен от BotFather
export GOOGLE_CREDENTIALS_FILE="credentials.json"
export SHEET_URL="https://docs.google.com/spreadsheets/d/..."
export ADMIN_CHAT_ID="123456789"   # твой chat_id для уведомлений

python bot.py
```

## Структура заявки в таблице

| Дата | Имя | Телефон | Комментарий |
|---|---|---|---|
| 28.10.2026 14:32 | Иван | +7... | Нужен замер |

## Автор

[Artem](https://github.com/artemdasa1235-hub) — учебный проект: упрощённый
аналог заявочного модуля CRM на Python.
