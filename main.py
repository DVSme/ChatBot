import os
import logging
from openai import OpenAI
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from fastapi import FastAPI, Request
import asyncio
import httpx
import uvicorn

# Загружаем переменные окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 10000))  # Используем PORT от Render

# Проверяем API-ключи
if not TOKEN:
    raise ValueError("Ошибка: TELEGRAM_BOT_TOKEN не найден!")
if not OPENAI_API_KEY:
    raise ValueError("Ошибка: OPENAI_API_KEY не найден!")

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# FastAPI приложение
app = FastAPI()

# URL вебхука
WEBHOOK_URL = f"https://chatbot-cfr8.onrender.com/webhook"
PING_URL = "https://chatbot-cfr8.onrender.com/ping"

# Принудительно устанавливаем вебхук
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

# Keep-Alive (Исправленный)
async def keep_awake():
    await asyncio.sleep(5)
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(PING_URL)
                logging.info(f"Keep-alive ping sent: {response.status_code}")
        except Exception as e:
            logging.error(f"Keep-alive error: {e}")
        await asyncio.sleep(30)

# Главное меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ Информация о боте")],
        [KeyboardButton(text="⚙ Выбрать модель"), KeyboardButton(text="💾 Запоминание истории")],
        [KeyboardButton(text="⛔ Остановка сохранения"), KeyboardButton(text="🔄 Сброс истории и настроек")]
    ],
    resize_keyboard=True
)

# Запускаем сервер
@app.on_event("startup")
async def startup():
    await set_webhook()
    asyncio.create_task(keep_awake())

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    logging.info("Webhook удалён")

# Маршрут вебхука
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        telegram_update = Update.model_validate(update)
        await dp.feed_update(bot, telegram_update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
        return {"status": "error", "message": str(e)}

# Добавляем /ping для проверки
@app.get("/ping")
async def ping():
    return {"status": "I'm awake!"}

# Обработчик команды /start
@router.message(CommandStart())
async def start_handler(message: types.Message):
    try:
        await message.answer(
            "Привет! Это бот на базе ChatGPT. Выберите действие:",
            reply_markup=menu_keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка в команде /start: {e}")
        await message.answer("Ошибка при загрузке меню.")

@router.message(lambda message: message.text == "ℹ Информация о боте")
async def info_handler(message: types.Message):
    try:
        info_text = (
            "🤖 Этот бот работает на основе ChatGPT.\n\n"
            "📌 Возможности:\n"
            "🔹 Отвечает на вопросы с использованием ИИ.\n"
            "🔹 Позволяет выбирать модель ChatGPT.\n"
            "🔹 Может запоминать историю диалога.\n"
            "🔹 Позволяет сбрасывать историю и настройки.\n"
            "🔹 Работает в Telegram через вебхук."
        )
        await message.answer(info_text)
    except Exception as e:
        logging.error(f"Ошибка в обработке информации: {e}")
        await message.answer("Ошибка при загрузке информации.")

# Запуск FastAPI
if __name__ == "__main__":
    print("Запуск FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
