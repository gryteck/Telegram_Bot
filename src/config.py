from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from telebot import TeleBot as TeleBot

import decor.promo

db_url_docker = 'postgresql://admin:test@postgres:5432/akira'
db_url_akira = 'postgresql://admin:password@62.217.181.151:5432/akira'
db_url_local = 'postgresql://postgres:test@localhost:5432/postgres'
admins = [680359970, 1926119360, 5818978734]
supp_id = 5818978734
akira_matchbot = '6282772673:AAGYnc05dPdAAc5VpUb5qMyv_cUk8reiFdk'
my_buckwheat_bot = '5911241134:AAHuxXDW48E6rg8S5E_byTSWhIxQmMSDIk8'
# br_photo = 'AgACAgIAAxkBAALlrmTBZmmVBAeczagvyGAPg0r62bGxAAIMyTEbkBARSpvSJbl_bwfMAQADAgADeQADLwQ'
br_photo = 'AgACAgIAAxkBAAJT12TDxjHUQyXZdCzqPaHW0NLhrgWhAAIMyTEbkBARShl6o1Zard0RAQADAgADeQADLwQ'
media_groups = []
promo_link = 'https://t.me/+ZekSEEP_UpM3MjIy'
# ------ Configurations -------
bot_token = my_buckwheat_bot
promo = decor.promo.my_buckwheat_bot_promo
redis_host = 'localhost'

sleep_time = 3600
daily_views = 125
liked_buffer = 22
last_active_time = '18 hours'
inactive_day = '36 hours'
inactive_time = '6 days'
ban_limit = 10
db_url = db_url_local

# -----------------------------
telebot = TeleBot(token=bot_token)
bot = Bot(token=bot_token)

storage = RedisStorage2(host='localhost', port=6379, db=1, password="",)
dp = Dispatcher(bot, storage=storage)
