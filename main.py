from src.imp import *
import psycopg2
from handlers import dp
# logging.basicConfig(level=logging.INFO, filename='src/main.log', \
# filemode='w', format='%(asctime)s, %(levelname)s, %(message)s, %(name)s')
logging.basicConfig(level=logging.INFO)

bot_db = BotDB()


async def main():
    try:
        # Connect to the database
        await bot_db.connect()
        if not await bot_db.table_users_exists():
            await bot_db.create_table_users()
        # Start the bot
        await dp.start_polling()

        # Disconnect from the database
        await bot_db.disconnect()
    except Exception as e:
        print(f"Error: {str(e)}")


async def on_startup(dp):
    # Creates database connection pool
    await bot_db.connect()
    if not await bot_db.table_users_exists():
        await bot_db.create_table_users()


async def on_shutdown(dp):
    # Closes database pool
    await bot_db.pool.close()


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )





