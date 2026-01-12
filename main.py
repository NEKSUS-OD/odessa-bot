import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

TOKEN = "8549411174:AAH0hzB0pZSeLwRbbP1AMPmjk2LBmNb2FCg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных
db = sqlite3.connect("books.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS library (title TEXT, file_id TEXT)")
db.commit()

def add_to_db(name, f_id):
    name = name.lower()
    cur.execute("SELECT * FROM library WHERE file_id = ?", (f_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO library VALUES (?, ?)", (name, f_id))
        db.commit()
        return True
    return False

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚓️ Бот Одесской библиотеки готов.\n\nНапиши /scan в канале с книгами или просто ищи здесь по названию.")

@dp.channel_post(Command("scan"))
async def scan_channel(message: types.Message):
    count = 0
    async for msg in bot.get_chat_history(message.chat.id, limit=200):
        if msg.document:
            if add_to_db(msg.document.file_name, msg.document.file_id):
                count += 1
    await bot.send_message(message.chat.id, f"✅ Сканирование завершено!\nДобавлено книг: {count}")

@dp.message(Command("test"))
async def test_db(message: types.Message):
    cur.execute("SELECT COUNT(*) FROM library")
    count = cur.fetchone()[0]
    await message.answer(f"📊 Книг в базе: {count}")

@dp.channel_post(F.document)
@dp.message(F.document)
async def handle_docs(message: types.Message):
    if add_to_db(message.document.file_name, message.document.file_id):
        print(f"Новый файл: {message.document.file_name}")

@dp.message()
async def search(message: types.Message):
    query = message.text.lower()
    cur.execute("SELECT title, file_id FROM library WHERE title LIKE ?", (f'%{query}%',))
    results = cur.fetchall()
    if results:
        for title, f_id in results:
            await bot.send_document(message.chat.id, f_id, caption=f"Найдено: {title}")
    else:
        await message.answer("❌ Книга не найдена.")

# Технический сервер для Render
async def handle(request):
    return web.Response(text="Бот работает")

async def main():
    # Запуск веб-сервера для Render на порту 7860
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 7860)
    await site.start()
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
