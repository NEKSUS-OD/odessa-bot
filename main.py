import asyncio, os, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Твой токен
TOKEN = "8549411174:AAH0hzB0pZSeLwRbbP1AMPmjk2LBmNb2FCg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем базу данных
db = sqlite3.connect("books.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS library (title TEXT, file_id TEXT)")
db.commit()

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🔍 Поиск")],
        [types.KeyboardButton(text="📜 Инструкция")]
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("⚓️ Одесская библиотека на связи! \n\nКидайте книги в канал-хранилище, а я их проиндексирую.", reply_markup=markup)

# ЭТА ЧАСТЬ ТЕПЕРЬ СЛУШАЕТ И КАНАЛЫ
@dp.channel_post(F.document)
@dp.message(F.document)
async def save_book(message: types.Message):
    # Берем имя файла, например "Lagun_Kapitan-Sorvi-golova.fb2"
    file_name = message.document.file_name
    file_id = message.document.file_id
    
    # Сохраняем в базу (в нижнем регистре для удобства поиска)
    cur.execute("INSERT INTO library VALUES (?, ?)", (file_name.lower(), file_id))
    db.commit()
    
    # Отправляем подтверждение (в личку или лог)
    print(f"Книга добавлена: {file_name}")

# Поиск книги по названию
@dp.message()
async def search(message: types.Message):
    if message.text in ["🔍 Поиск", "📜 Инструкция"]:
        await message.answer("Просто напиши название книги или автора:")
        return

    query = message.text.lower()
    cur.execute("SELECT title, file_id FROM library WHERE title LIKE ?", (f'%{query}%',))
    results = cur.fetchall()

    if results:
        for title, f_id in results:
            await bot.send_document(message.chat.id, f_id, caption=f"Найдено: {title} 📖")
    else:
        await message.answer("К сожалению, такой книги пока нет в базе. Попробуйте другое название.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
