import asyncio, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

TOKEN = "8549411174:AAH0hzB0pZSeLwRbbP1AMPmjk2LBmNb2FCg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных
db = sqlite3.connect("books.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS library (title TEXT, file_id TEXT)")
db.commit()

@dp.channel_post(F.document)
async def handle_docs(message: types.Message):
    try:
        name = message.document.file_name
        f_id = message.document.file_id
        # Добавляем в базу, только если такого file_id еще нет (защита от дублей)
        cur.execute("INSERT INTO library VALUES (?, ?)", (name.lower(), f_id))
        db.commit()
    except:
        pass

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    query = message.text.lower()
    cur.execute("SELECT DISTINCT title, file_id FROM library WHERE title LIKE ? LIMIT 10", (f'%{query}%',))
    results = cur.fetchall()
    
    if results:
        for title, f_id in results:
            try:
                await bot.send_document(message.chat.id, f_id, caption=f"📚 {title}")
            except:
                continue
    else:
        await message.answer("❌ В моем архиве это не найдено.")

async def handle(request): return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 7860).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
