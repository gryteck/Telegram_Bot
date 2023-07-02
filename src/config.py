from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

bot = Bot(token="6282772673:AAEKOVAnNRO80FFezj3G82odvWT1gvDIZ3Q")
storage = RedisStorage2(host='localhost', port=6379, db=1, password="",)
dp = Dispatcher(bot, storage=storage)
db_url = 'postgresql://HETdQSqYXMoTjDWbzmuxmJqlvEfKHfpO:lZETgqCIlOzwyvfPCUCgTOPiPDGsUrqw' \
         '@db.thin.dev/5759e2bc-5590-44c2-bea6-f1d3724fd8a5'

db_url_docker = 'postgresql://postgres:test@postgres:5432/postgres'

db_url_local = 'postgresql://postgres:test@localhost:5432/postgres'
admins = [680359970, 1926119360, 5818978734]
supp_id = 5818978734

# ------ Limits:
daily_views = 50
liked_buffer = 21
time = '18 hours'
