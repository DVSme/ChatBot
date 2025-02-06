import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

# Логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# Вебхук обработчик
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    telegram_update = Update(**data)
    await dp.process_update(telegram_update)

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Бот работает через Webhook.")

# Устанавливаем вебхук при запуске
@app.on_event("startup")
async def on_startup():
    webhook_url = "https://chatbot-crf8.onrender.com/webhook"
    await bot.set_webhook(webhook_url)
