import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём экземпляры бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаём FastAPI приложение
app = FastAPI()

# Указываем URL вебхука (замени на свой)
WEBHOOK_URL = "https://chatbot-crf8.onrender.com/webhook"

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update(**update)
    await dp.process_update(telegram_update)
    return {"status": "ok"}

# Обработчик команд
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я работаю через вебхук.")

async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    await bot.delete_webhook()

# Запуск настроек FastAPI
@app.on_event("startup")
async def startup():
    await on_startup()

@app.on_event("shutdown")
async def shutdown():
    await on_shutdown()
