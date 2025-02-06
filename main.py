import os
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Update
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))  # Render использует этот порт

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём экземпляры бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Создаём FastAPI приложение
app = FastAPI()

# URL вебхука
WEBHOOK_URL = f"https://chatbot-crf8.onrender.com/webhook"

# Тестовый маршрут (проверка работы сервера)
@app.get("/")
async def root():
    return {"message": "Bot is running!"}

# Основной маршрут вебхука
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        telegram_update = Update(**update)
        await dp.feed_update(bot, telegram_update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Ошибка в обработке вебхука: {e}")
        return {"status": "error", "message": str(e)}

# Устанавливаем вебхук при старте приложения
@app.on_event("startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()

# Обработчик команды /start
@router.message()
async def start_handler(message: types.Message):
    if message.text == "/start":
        await message.answer("Привет! Я работаю через вебхук.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

