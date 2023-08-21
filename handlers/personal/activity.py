import asyncio

from aiogram.utils import exceptions
from src.config import bot, sleep_time
from db.schema import db
import decor.keyboard as kb
import decor.text as t

async def check_inactive():
    while True:
        await asyncio.sleep(sleep_time)
        users = db.patch_daily_inactive_users()
        if users is not None:
            for user in users:
                try: await bot.send_message(user, t.daily_miss_u(), reply_markup=kb.cont())
                except (exceptions.BotBlocked, exceptions.ChatNotFound):
                    if user > 999: db.patch_visible(user, False)
        users = db.patch_inactive_users()
        if users is not None:
            for user in users:
                try: await bot.send_message(user, t.miss_u(), reply_markup=kb.cont())
                except (exceptions.BotBlocked, exceptions.ChatNotFound):
                    if user > 999: db.patch_visible(user, False)
