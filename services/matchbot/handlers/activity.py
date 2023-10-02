import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext

import decor.keyboard as kb
import decor.text as t
from aiogram.utils import exceptions

from config import bot, sleep_time
from db.schema import db
from states import Wait


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


async def matchbot(message: types.Message, state: FSMContext) -> None:
    id = message.from_user.id
    if db.user_exists(id):
        f = db.get_form(id)
        await message.answer("Вот твоя анкета")
        await bot.send_photo(photo=f['photo'], chat_id=id, caption=t.cap(f))
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()
    else:
        await state.update_data(liked_id=id)
        await message.answer(t.instruction)
        await bot.send_chat_action(chat_id=id, action='typing')
        await asyncio.sleep(1)
        await message.answer(t.set_gender, reply_markup=kb.gender())
        await Wait.set_gender.set()
