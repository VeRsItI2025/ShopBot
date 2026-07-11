from aiogram import Bot, Dispatcher, Router

import asyncio
from dotenv import load_dotenv
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import remove_expired_discounts

from handlers import start, catalog, cart, admin, orders
from keyboards import main_menu

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # лучше хранить токен в переменной окружения
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

dp.include_router(start.router)
dp.include_router(main_menu.router)
dp.include_router(catalog.router)
dp.include_router(cart.router)
dp.include_router(admin.router)
dp.include_router(orders.router)

print("Бот Запущен!!!")

async def main():
    # Мой код
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_discounts, "interval", minutes=5)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    