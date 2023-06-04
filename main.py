from src.imp import *
import asyncio
import sys
import psycopg2

# logging.basicConfig(level=logging.INFO, filename='src/main.log', \
# filemode='w', format='%(asctime)s, %(levelname)s, %(message)s, %(name)s')
logging.basicConfig(level=logging.INFO)
BotDB = BotDB()


async def main():
    from handlers import dp
    try:
        await dp.start_polling(dp)
    except (IndexError, psycopg2.ProgrammingError) as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
    # executor.start_polling(dp, skip_updates=True)
