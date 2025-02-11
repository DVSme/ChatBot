from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

import logging
import os

app = FastAPI()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@app.get("https://chatbot-cfr8.onrender.com/ping")
def ping():
    return {"status": "ok"}

@app.post("https://chatbot-cfr8.onrender.com/webhook")
async def telegram_webhook(update: dict):
    try:
        logging.info(f"Incoming update: {update}")
        telegram_update = types.Update(**update)
        await dp.feed_update(bot, telegram_update)
    except Exception as e:
        logging.error(f"Webhook processing error: {e}")
    return {"ok": True}

@dp.message(Command("start"))

async def start_handler(message: Message):
    try:
        text = "\U0001F916 Этот бот работает на основе ChatGPT.\n\n📌 Возможности:\n" \
               "\U0001F539 Отвечает на вопросы с использованием ИИ.\n" \
               "\U0001F539 Позволяет выбирать модель ChatGPT.\n" \
               "\U0001F539 Может запоминать историю диалога.\n" \
               "\U0001F539 Позволяет сбрасывать историю и настройки.\n" \
               "\U0001F539 Работает в Telegram через вебхук."
        text = text.encode("utf-8", "ignore").decode("utf-8")
        await message.answer(text)
    except Exception as e:
        logging.error(f"Error in /start command: {e}")
