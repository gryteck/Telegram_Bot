import asyncio
from config import bot
from aiogram import types


async def check_inactive():
    # while True:
    #     await asyncio.sleep(sleep_time)
    #     users = db.patch_daily_inactive_users()
    #     if users is not None:
    #         for user in users:
    #             try: await bot.send_message(user, t.daily_miss_u(), reply_markup=kb.cont())
    #             except (exceptions.BotBlocked, exceptions.ChatNotFound):
    #                 if user > 999: db.patch_visible(user, False)
    #     users = db.patch_inactive_users()
    #     if users is not None:
    #         for user in users:
    #             try: await bot.send_message(user, t.miss_u(), reply_markup=kb.cont())
    #             except (exceptions.BotBlocked, exceptions.ChatNotFound):
    #                 if user > 999: db.patch_visible(user, False)
    pass


async def typing(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await asyncio.sleep(1)

