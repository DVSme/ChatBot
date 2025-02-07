import os
import logging
import openai
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Update
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверяем, загружены ли API-ключи
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в переменных окружения!")

# Настраиваем OpenAI API
openai.api_key = OPENAI_API_KEY

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
    return {"message": "Bot is running!"}

# Основной маршрут вебхука
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    telegram_update = Update.model_validate(update)  # Валидация данных
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

# Устанавливаем вебхук при старте приложения
@app.on_event("startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    logging.info("Webhook удалён")

# Обработчик всех сообщений через ChatGPT
@router.message()
async def chatgpt_handler(message: types.Message):
    try:
        user_input = message.text  # Получаем текст от пользователя
        logging.info(f"Пользователь отправил: {user_input}")  # Логируем входящий текст

        # Отправляем запрос в OpenAI (ChatGPT)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )

        bot_response = response["choices"][0]["message"]["content"]  # Получаем ответ
        logging.info(f"Ответ ChatGPT: {bot_response}")  # Логируем ответ

        await message.answer(bot_response)  # Отправляем ответ пользователю

    except Exception as e:
        logging.error(f"Ошибка в обработке сообщения: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")

# Запуск FastAPI
if __name__ == "__main__":
    print("Запуск FastAPI...")  # Вывод в логах
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
