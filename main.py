import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Создаем роутер для хэндлеров
router = Router()
dp.include_router(router)

# FastAPI приложение
app = FastAPI()

# Вебхук обработчик
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    telegram_update = Update(**data)
    await dp._process_update(telegram_update)

# Команда /start
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Бот работает через Webhook.")

# Устанавливаем вебхук при запуске
@app.on_event("startup")
async def on_startup():
    webhook_url = "https://chatbot-crf8.onrender.com/webhook"
    await bot.set_webhook(webhook_url)
