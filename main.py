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
#load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"✅ TELEGRAM_BOT_TOKEN: {TOKEN}")
print(f"✅ OPENAI_API_KEY: {OPENAI_API_KEY[:5]}...")  # Выводит только первые 5 символов для безопасности

# Проверяем, загружены ли API-ключи
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не найден в переменных окружения!")

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
WEBHOOK_URL = f"https://chatbot-cfr8.onrender.com/webhook"

# Тестовый маршрут (проверка работы сервера)
@app.get("/")
async def root():
    return {"message": "✅ Bot is running!"}

# Пинг для подъема
@app.get("/ping")
async def ping():
    return {"status": "I'm awake!"}

# Основной маршрут вебхука
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update.model_validate(update)  # Валидация данных
    await dp.process_update(telegram_update)
    return {"status": "ok"}

# Устанавливаем вебхук при старте приложения
@app.on_event("startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    logging.info("✅ Webhook удалён")

# Обработчик сообщений с ChatGPT

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

        # Получаем ответ от ChatGPT
        bot_response = response.choices[0].message.content

        logging.info(f"🤖 Ответ ChatGPT: {bot_response}")

        await message.answer(bot_response)

    except Exception as e:
        logging.error(f"❌ Ошибка в обработке сообщения: {e}")
        await message.answer(f"⚠️ Ошибка: {str(e)}")
# Подъем бота
async def keep_awake():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(WEBHOOK_URL + "/ping")
                logging.info(f"🔄 Keep-alive ping sent: {response.status_code}")
        except Exception as e:
            logging.error(f"❌ Keep-alive error: {e}")

        await asyncio.sleep(600)  # Пинг каждые 10 минут (600 секунд)

@app.on_event("startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")

    # Запускаем фоновый процесс
    asyncio.create_task(keep_awake())  

# Запуск FastAPI
if __name__ == "__main__":
    print("🚀 Запуск FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))