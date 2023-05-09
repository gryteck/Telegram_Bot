from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

bot = Bot(token="5911241134:AAHuxXDW48E6rg8S5E_byTSWhIxQmMSDIk8")
storage = RedisStorage2(host='127.0.0.1', port=6379, db=1, password="",)
dp = Dispatcher(bot, storage=storage)
db_url = 'postgresql://HETdQSqYXMoTjDWbzmuxmJqlvEfKHfpO:lZETgqCIlOzwyvfPCUCgTOPiPDGsUrqw' \
         '@db.thin.dev/5759e2bc-5590-44c2-bea6-f1d3724fd8a5'

db_url_local = 'postgresql://postgres:test@localhost:5432/postgres'
admins = [680359970, 1926119360, 5818978734]
supp_id = 5818978734

# ------ Limits:
daily_views = 50
liked_buffer = 21

