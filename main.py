import os
import logging
from aiogram import Bot, Dispatcher, types, Router
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

# Добавляем Router (в aiogram 3.x обработчики вешаются на него)
router = Router()
dp.include_router(router)

# Создаём FastAPI приложение
app = FastAPI()

# Указываем URL вебхука
WEBHOOK_URL = "https://chatbot-crf8.onrender.com/webhook"

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# Обработчик команды /start
@router.message()
async def start_handler(message: types.Message):
    if message.text == "/start":
        await message.answer("Привет! Я работаю через вебхук.")

# Настройка FastAPI при старте
@app.on_event("startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()