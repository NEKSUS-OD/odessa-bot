import asyncio, os, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = "8549411174:AAH0hzB0pZSeLwRbbP1AMPmjk2LBmNb2FCg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем базу
db = sqlite3.connect("books.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS library (title TEXT, file_id TEXT)")
db.commit()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚓️ Бот готов. Пришли книгу в канал, а потом напиши её название здесь.")

# Команда для проверки базы
@dp.message(Command("test"))
async def test_db(message: types.Message):
    cur.execute("SELECT COUNT(*) FROM library")
    count = cur.fetchone()[0]
    await message.answer(f"📊 Сейчас в базе книг: {count}")

# Слушаем файлы везде
@dp.channel_post(F.document)
@dp.message(F.document)
async def save_book(message: types.Message):
    file_name = message.document.file_name.lower()
    file_id = message.document.file_id
    cur.execute("INSERT INTO library VALUES (?, ?)", (file_name, file_id))
    db.commit()
    # Бот ответит в личку админу (тебе), если файл прошел
    print(f"DEBUG: Сохранил {file_name}")

@dp.message()
async def search(message: types.Message):
    query = message.text.lower()
    cur.execute("SELECT file_id FROM library WHERE title LIKE ?", (f'%{query}%',))
    results = cur.fetchall()
    if results:
        for f_id in results:
            await bot.send_document(message.chat.id, f_id)
    else:
        await message.answer("❌ Книга не найдена. Сначала загрузи её в канал!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
