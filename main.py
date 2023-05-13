from src.imp import *

logging.basicConfig(level=logging.INFO, filename='test/main.log', filemode='w',
                    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s')

BotDB = BotDB()

if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)
