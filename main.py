import logging
import asyncio

from handlers import dp
from handlers.personal.activity import check_inactive
from db.schema import db

# logging.basicConfig(level=logging.INFO, filename='src/main.log', \
# filemode='w', format='%(asctime)s, %(levelname)s, %(message)s, %(name)s')
logging.basicConfig(level=logging.DEBUG)


async def on_startup(dp):
    # Creates database connection pool
    pass


async def on_shutdown(dp):
    # Closes database pool
    db.close()

if __name__ == "__main__":
    from aiogram import executor

    loop = asyncio.get_event_loop()
    loop.create_task(check_inactive())

    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
