
import os
import openai
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import Dispatcher
import asyncio
from dotenv import load_dotenv

# Загружаем токены из переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Устанавливаем API-ключ OpenAI
openai.api_key = OPENAI_API_KEY

# Обработчик сообщений
@dp.message_handler()
async def chat_with_gpt(message: Message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message.text}]
    )
    await message.reply(response["choices"][0]["message"]["content"])

# Запуск бота
import asyncio

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())

