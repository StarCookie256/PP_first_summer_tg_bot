import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from bot.handlers import get_routers
from aiogram.client.session.aiohttp import AiohttpSession

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PROXY_URL = "http://176.111.37.216:39811"


async def main():
    if not BOT_TOKEN:
        raise ValueError("No token")

    # session = AiohttpSession(proxy=PROXY_URL)
    # bot = Bot(token=BOT_TOKEN, session=session)
    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()
    dp.include_routers(*get_routers())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # На Windows меняем цикл событий, чтобы избежать ошибки ProactorBasePipeTransport
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот выключен пользователем.")

