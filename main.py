import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# Твой токен
TOKEN = "8549411174:AAH0hzB0pZSeLwRbbP1AMPmjk2LBmNb2FCg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем базу
db = sqlite3.connect("books.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS library (title TEXT, file_id TEXT)")
db.commit()

def add_to_db(name, f_id):
    if not name:
        return False
    name = name.lower()
    cur.execute("SELECT * FROM library WHERE file_id = ?", (f_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO library VALUES (?, ?)", (name, f_id))
        db.commit()
        return True
    return False

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚓️ Библиотека Одессы готова к работе!\n\nНапиши название книги для поиска.")

@dp.message(Command("test"))
async def test_db(message: types.Message):
    cur.execute("SELECT COUNT(*) FROM library")
    count = cur.fetchone()[0]
    await message.answer(f"📊 Книг в базе: {count}")

# ИСПРАВЛЕННАЯ ФУНКЦИЯ СКАНЕРА
@dp.channel_post(Command("scan"))
async def scan_channel(message: types.Message):
    count = 0
    # В aiogram 3.x get_chat_history вызывается через bot.get_chat_history
    # Но для надежности мы просто пройдемся по последним сообщениям
    try:
        async for msg in bot.get_chat_history(chat_id=message.chat.id, limit=200):
            if msg.document:
                if add_to_db(msg.document.file_name, msg.document.file_id):
                    count += 1
        await bot.send_message(chat_id=message.chat.id, text=f"✅ Сканирование завершено!\nДобавлено книг: {count}")
    except Exception as e:
        await bot.send_message(chat_id=message.chat.id, text=f"❌ Ошибка сканирования: {e}")

@dp.channel_post(F.document)
@dp.message(F.document)
async def handle_docs(message: types.Message):
    if add_to_db(message.document.file_name, message.document.file_id):
        print(f"Новая книга: {message.document.file_name}")

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    query = message.text.lower()
    cur.execute("SELECT title, file_id FROM library WHERE title LIKE ?", (f'%{query}%',))
    results = cur.fetchall()
    if results:
        for title, f_id in results:
            await bot.send_document(message.chat.id, f_id, caption=f"Найдено: {title}")
    else:
        await message.answer("❌ Ничего не нашел. Попробуй другое слово.")

# Техническая часть для Render
async def handle(request):
    return web.Response(text="Bot is running")

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 7860)
    await site.start()
    
    # Удаляем вебхуки перед запуском, чтобы не было конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
