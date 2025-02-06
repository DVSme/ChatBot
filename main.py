import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from fastapi import FastAPI
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.webhook import WebhookRequestHandler

# Загружаем токены из переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # Добавлен storage для Dispatcher

# Создание FastAPI приложения
app = FastAPI()

# Указываем URL вебхука (замени на свой домен Render)
WEBHOOK_URL = "https://your-app-name.onrender.com/webhook"

@app.post("/webhook")
async def telegram_webhook(update: dict):
    """Обработчик вебхука для Telegram"""
    telegram_update = Update(**update)
    await dp._process_update(telegram_update)

@app.get("/")
async def root():
    return {"message": "Webhook is working!"}

# Обработчик команд
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Вы сказали: {message.text}")

async def on_startup():
    """Запуск вебхука при старте"""
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    """Удаление вебхука при завершении работы"""
    await bot.delete_webhook()

# Подключение вебхука к FastAPI
@app.on_event("startup")
async def startup():
    await on_startup()

@app.on_event("shutdown")
async def shutdown():
    await on_shutdown()
