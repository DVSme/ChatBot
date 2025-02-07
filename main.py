import os
import logging
from openai import OpenAI
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Update
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

# ✅ Проверяем и устанавливаем вебхук
async def set_webhook():
    webhook_info = await bot.get_webhook_info()
    if not webhook_info.url or webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
    else:
        logging.info("✅ Webhook уже установлен")

# 🚀 Запускаем сервер
@app.on_event("startup")
async def startup():
    await set_webhook()
    
    # ✅ Keep-Alive
    async def keep_awake():
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(WEBHOOK_URL.replace("/webhook", "/ping"))
                    logging.info(f"🔄 Keep-alive ping sent: {response.status_code}")
            except Exception as e:
                logging.error(f"❌ Keep-alive error: {e}")

            await asyncio.sleep(600)  # 10 минут

    asyncio.create_task(keep_awake())  # Запускаем Keep-alive

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    logging.info("✅ Webhook удалён")

# 📌 Тестовый маршрут
@app.get("/")
async def root():
    return {"message": "✅ Bot is running!"}

# 📌 Keep-alive (пинг)
@app.get("/ping")
async def ping():
    return {"status": "I'm awake!"}

# 📌 Основной вебхук
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update.model_validate(update)  # Валидация данных
    await dp.feed_update(bot, telegram_update)  # ✅ Исправлено
    return {"status": "ok"}

# 🔥 Обработчик сообщений с ChatGPT
client = OpenAI(api_key=OPENAI_API_KEY)

@router.message()
async def chatgpt_handler(message: types.Message):
    try:
        user_input = message.text
        logging.info(f"📩 Пользователь отправил: {user_input}")

        # API вызов OpenAI
        response = client.chat.completions.create(
           model="gpt-4o-mini",
           messages=[{"role": "user", "content": user_input}]
        )  

        bot_response = response.choices[0].message.content
        logging.info(f"🤖 Ответ ChatGPT: {bot_response}")

        await message.answer(bot_response)

    except Exception as e:
        logging.error(f"❌ Ошибка в обработке сообщения: {e}")
        await message.answer(f"⚠️ Ошибка: {str(e)}")

# Запуск FastAPI
if __name__ == "__main__":
    print("🚀 Запуск FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
