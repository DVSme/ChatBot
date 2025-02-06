import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI
from dotenv import load_dotenv

# Загружаем токены из переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем FastAPI приложение
app = FastAPI()

# Указываем URL вебхука (замени на свой домен Render)
WEBHOOK_URL = "https://chatbot-crf8.onrender.com/webhook"

# Обработчик входящих обновлений от Telegram
@app.post("/webhook")
async def telegram_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)

# Простейший обработчик сообщений
@dp.message()
async def echo(message: Update):
    await message.answer(f"Вы сказали: {message.text}")

# Запуск бота при старте сервера
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
