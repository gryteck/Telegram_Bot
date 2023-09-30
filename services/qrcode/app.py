import asyncio
import logging

from handlers import dp
from db.schema import db


async def on_startup(dp):
    # Creates database connection pool
    pass


async def on_shutdown(dp):
    # Closes database pool
    db.close()

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING,
                        # filename='main.log', filemode='w',
                        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s', force=True)
    from aiogram import executor
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
