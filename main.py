import asyncio, os, socket
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web, TCPConnector

# Пробуем вручную узнать IP телеграма, если DNS сбоит
def get_telegram_ip():
    try:
        return socket.gethostbyname('api.telegram.org')
    except:
        return None

TOKEN = "8549411174:AAH0hzB0pZSeLwRbbP1AMPmjk2LBmNb2FCg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_kb():
    kb = [[types.KeyboardButton(text="🔍 Поиск"), types.KeyboardButton(text="📜 Помощь")]]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚓️ Библиотека Одессы ожила!", reply_markup=get_main_kb())

async def handle(r): return web.Response(text="OK")

async def main():
    # Проверка связи перед стартом
    ip = get_telegram_ip()
    print(f"DEBUG: IP Telegram = {ip}")
    
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 7860).start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
