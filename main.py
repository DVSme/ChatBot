
import os
import openai
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv

# ��������� ������ �� ���������� ���������
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ������������� ����
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ������������� API-���� OpenAI
openai.api_key = OPENAI_API_KEY

# ���������� ���������
@dp.message_handler()
async def chat_with_gpt(message: Message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message.text}]
    )
    await message.reply(response["choices"][0]["message"]["content"])

# ������ ����
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
