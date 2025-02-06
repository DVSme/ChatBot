import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.utils.webhook import configure_app
from fastapi import FastAPI
from dotenv import load_dotenv

# Загружаем токены из переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создание FastAPI приложения
app = FastAPI()

# Указываем URL вебхука (замени на свой домен Render)
WEBHOOK_URL = "https://your-app-name.onrender.com/webhook"

@app.post("/webhook")
async def telegram_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.process_update(telegram_update)

# Обработчик команд
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Вы сказали: {message.text}")

async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    await bot.delete_webhook()

# Настроим приложение с aiogram
configure_app(dp, app, on_startup=on_startup, on_shutdown=on_shutdown)
