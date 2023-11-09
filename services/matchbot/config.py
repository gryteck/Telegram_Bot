from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from pydantic_settings import BaseSettings
from dotenv import dotenv_values

env = dotenv_values()

admins = eval(env['ADMINS'])
supp_id = int(env['SUPPORT_ID'])

media_groups = []
promo_link = 'https://t.me/+ZekSEEP_UpM3MjIy'

# ------ Configurations -------

sleep_time = 3600
daily_views = 105
liked_buffer = 22
last_active_time = '18 hours'
inactive_day = '36 hours'
inactive_time = '6 days'
ban_limit = 10

# -----------------------------

pg_url = env['POSTGRES_URL']

bot = Bot(token=env["TOKEN"])
dp = Dispatcher(bot, storage=RedisStorage2(host=env['REDIS_HOST'], db=1, password=env['REDIS_PASSWORD']))
