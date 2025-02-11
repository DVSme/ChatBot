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
PORT = int(os.getenv("PORT", 8000))  # Используем PORT от Render

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

# \u2705 Принудительно устанавливаем вебхук
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"\u2705 Webhook установлен: {WEBHOOK_URL}")

# \u2705 Keep-Alive (Исправленный)
async def keep_awake():
    await asyncio.sleep(5)  # \u0414\u0410\u0415\u041c \u0412\u0420\u0415\u041c\u042f \u041d\u0410 \u0421\u0422\u0410\u0420\u0422!
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(PING_URL)
                logging.info(f"\ud83d\udd04 Keep-alive ping sent: {response.status_code}")
        except Exception as e:
            logging.error(f"\u274c Keep-alive error: {e}")

        await asyncio.sleep(30)  # 30 \u0441\u0435\u043a\u0443\u043d\u0434

# Главное меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="\u2139\ufe0f Информация о боте")],
        [KeyboardButton(text="\ud83d\udee0 Выбрать модель"), KeyboardButton(text="\ud83d\udcc0 Запоминание истории")],
        [KeyboardButton(text="\u274c Остановка сохранения"), KeyboardButton(text="\ud83d\udd04 Сброс истории и настроек")]
    ],
    resize_keyboard=True
)

# \ud83d\ude80 Запускаем сервер
@app.on_event("startup")
async def startup():
    await set_webhook()
    asyncio.create_task(keep_awake())  # Keep-Alive

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    logging.info("\u2705 Webhook удалён")

# \ud83d\udccc Маршрут вебхука
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update.model_validate(update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# Обработчик команды /start
@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "\ud83d\udc4b Привет! Это бот на базе ChatGPT. Выберите действие из меню ниже:",
        reply_markup=menu_keyboard
    )

@router.message(lambda message: message.text == "\u2139\ufe0f Информация о боте")
async def info_handler(message: types.Message):
    info_text = (
        "\ud83e\udd16 **Этот бот работает на основе ChatGPT**.\n\n"
        "\ud83d\udcc0 **Возможности бота:**\n"
        "\ud83d\udd39 Отвечает на вопросы с использованием искусственного интеллекта.\n"
        "\ud83d\udd39 Позволяет выбирать модель ChatGPT.\n"
        "\ud83d\udd39 Может запоминать историю диалога.\n"
        "\ud83d\udd39 Позволяет сбрасывать историю и настройки.\n"
        "\ud83d\udd39 Работает в Telegram через вебхук."
    )
    await message.answer(info_text, parse_mode="Markdown")

# Запуск FastAPI
if __name__ == "__main__":
    print("\ud83d\ude80 Запуск FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
