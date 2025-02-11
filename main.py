import os
import logging
from openai import OpenAI
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from fastapi import FastAPI, Request
import asyncio
import httpx
import uvicorn

# Загружаем переменные окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверяем API-ключи
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не найден в переменных окружения!")

# Логирование
logging.basicConfig(level=logging.INFO)

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

# Глобальные переменные
user_history = {}
selected_model = {}

# Кнопки меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ Информация о боте")],
        [KeyboardButton(text="🛠 Выбрать модель ChatGPT")],
        [KeyboardButton(text="📝 Запоминание истории")],
        [KeyboardButton(text="⛔ Остановка сохранения истории")],
        [KeyboardButton(text="🔄 Сброс истории и настроек")]
    ],
    resize_keyboard=True
)

# ✅ Проверяем и устанавливаем вебхук
async def set_webhook():
    webhook_info = await bot.get_webhook_info()
    if not webhook_info.url or webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
    else:
        logging.info("✅ Webhook уже установлен")

# ✅ Keep-Alive (Исправленный)
async def keep_awake():
    await asyncio.sleep(5)
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(PING_URL)
                logging.info(f"🔄 Keep-alive ping sent: {response.status_code}")
        except Exception as e:
            logging.error(f"❌ Keep-alive error: {e}")
        await asyncio.sleep(30)

# ✅ Запускаем бота
async def run_bot():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Ошибка при запуске бота: {e}")

@app.on_event("startup")
async def startup():
    await set_webhook()
    asyncio.create_task(keep_awake())
    asyncio.create_task(run_bot())

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    logging.info("✅ Webhook удалён")

@app.get("/")
async def root():
    return {"message": "✅ Bot is running!"}

@app.get("/ping")
async def ping():
    return {"status": "I'm awake!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update.model_validate(update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# Обработчик меню
@router.message()
async def menu_handler(message: types.Message):
    user_id = message.from_user.id
    if message.text == "ℹ Информация о боте":
        await message.answer("🤖 Этот бот использует ChatGPT для генерации ответов!", reply_markup=menu_keyboard)
    elif message.text == "🛠 Выбрать модель ChatGPT":
        selected_model[user_id] = "gpt-4o-mini"
        await message.answer("✅ Выбрана модель gpt-4o-mini", reply_markup=menu_keyboard)
    elif message.text == "📝 Запоминание истории":
        user_history[user_id] = []
        await message.answer("📌 История сообщений теперь запоминается!", reply_markup=menu_keyboard)
    elif message.text == "⛔ Остановка сохранения истории":
        user_history.pop(user_id, None)
        await message.answer("🛑 История сообщений больше не сохраняется.", reply_markup=menu_keyboard)
    elif message.text == "🔄 Сброс истории и настроек":
        user_history.pop(user_id, None)
        selected_model.pop(user_id, None)
        await message.answer("♻ История и настройки сброшены.", reply_markup=menu_keyboard)
    else:
        user_input = message.text
        logging.info(f"📩 Пользователь отправил: {user_input}")

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=selected_model.get(user_id, "gpt-4o-mini"),
            messages=[{"role": "user", "content": user_input}]
        )

        bot_response = response.choices[0].message.content
        logging.info(f"🤖 Ответ ChatGPT: {bot_response}")

        if user_id in user_history:
            user_history[user_id].append((user_input, bot_response))

        await message.answer(bot_response, reply_markup=menu_keyboard)

if __name__ == "__main__":
    print("🚀 Запуск FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))