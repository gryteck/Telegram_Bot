import logging

from handlers import dp

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING,
                        # filename='main.log', filemode='w',
                        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s', force=True)
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
