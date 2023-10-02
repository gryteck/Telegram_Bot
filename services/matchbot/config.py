from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from decor.promo import my_buckwheat_bot_promo, akira_matchbot_promo

db_url_docker = 'postgresql://admin:test@postgres:5432/akira'
db_url_akira = 'postgresql://admin:password@62.217.181.151:5432/akira'
db_url_local = 'postgresql://postgres:test@localhost:5432/postgres'

admins = [680359970, 1926119360, 5818978734]
supp_id = 5818978734

akira_matchbot = '6282772673:AAGYnc05dPdAAc5VpUb5qMyv_cUk8reiFdk'
my_buckwheat_bot = '5911241134:AAHuxXDW48E6rg8S5E_byTSWhIxQmMSDIk8'

media_groups = []
promo_link = 'https://t.me/+ZekSEEP_UpM3MjIy'

# ------ Configurations -------

test = False

redis_host = 'localhost'
sleep_time = 3600
daily_views = 105
liked_buffer = 22
last_active_time = '18 hours'
inactive_day = '36 hours'
inactive_time = '6 days'
ban_limit = 10

# -----------------------------
bot_token = (my_buckwheat_bot if test else akira_matchbot)
promo = (my_buckwheat_bot_promo if test else akira_matchbot_promo)
db_url = (db_url_local if test else db_url_akira)

bot = Bot(token=bot_token)

storage = RedisStorage2(host=('localhost' if test else '62.217.181.151'),
                        port=6379,
                        db=1,
                        password=("" if test else "Kebila55"),
                        )
dp = Dispatcher(bot, storage=storage)
