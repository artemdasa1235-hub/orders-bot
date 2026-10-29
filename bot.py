"""
Orders Bot — Telegram-бот приёма заявок.

Логика: пользователь проходит пошаговую форму (имя → телефон → комментарий),
заявка автоматически сохраняется в Google Sheets, администратору приходит
уведомление с данными заявки.

Стек: Python, aiogram 3.x, gspread (Google Sheets API).
Запуск: python bot.py
"""

import asyncio
import os

import gspread
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from oauth2client.service_account import ServiceAccountCredentials

# ── Конфигурация ─────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
SHEET_URL = os.environ["SHEET_URL"]
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])
CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")

bot = Bot(BOT_TOKEN)

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, ["https://spreadsheets.google.com/feeds",
                           "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds).open_by_url(SHEET_URL).sheet1


# ── Состояния диалога ────────────────────────────────────────────────────
class OrderForm(StatesGroup):
    name = State()
    phone = State()
    comment = State()


def save_to_sheet(row: list[str]) -> None:
    get_sheet().append_row(row, value_input_options="USER_ENTERED")


# ── Обработчики ──────────────────────────────────────────────────────────
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Здравствуйте! Я принимаю заявки.\n\n"
        "Введите ваше имя:"
    )
    await state.set_state(OrderForm.name)


@dp.message(OrderForm.name)
async def ask_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Введите телефон:")
    await state.set_state(OrderForm.phone)


@dp.message(OrderForm.phone)
async def ask_comment(message: Message, state: FSMContext):
    digits = "".join(c for c in message.text if c.isdigit())
    if len(digits) < 10:
        await message.answer("Похоже, это не телефон. Попробуйте ещё раз:")
        return
    await state.update_data(phone=message.text)
    await message.answer("📝 Добавьте комментарий к заявке (или введите «-»):")
    await state.set_state(OrderForm.comment)


@dp.message(OrderForm.comment)
async def save_order(message: Message, state: FSMContext):
    data = await state.get_data()
    now = message.date.strftime("%d.%m.%Y %H:%M")
    row = [now, message.from_user.full_name, message.from_user.username or "—",
           data["name"], data["phone"], message.text]

    try:
        save_to_sheet(row)
        await message.answer(
            "✅ Заявка принята! Мы свяжемся с вами в ближайшее время.\n\n"
            f"Имя: {data['name']}\nТелефон: {data['phone']}"
        )
    except Exception:  # noqa: BLE001
        await message.answer("⚠️ Не удалось сохранить заявку, попробуйте позже.")
        raise

    # Уведомление администратору
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"🔔 Новая заявка!\n\n"
        f"👤 {data['name']}\n📞 {data['phone']}\n💬 {message.text}\n🕐 {now}",
    )
    await state.clear()


@dp.message()
async def fallback(message: Message):
    await message.answer("Нажмите /start, чтобы подать заявку.")


# ── Запуск ───────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    main()
