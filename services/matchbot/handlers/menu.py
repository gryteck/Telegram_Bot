from aiogram import types

from config import dp, bot

import decor.text as t
import decor.keyboard as kb

from .reactions import random_form

from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message):
    f = await db.get_user(message.from_user.id)

    if message.text == "1":
        await random_form(message, f)
    elif message.text == "2":
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await rd.update_state(message.from_user.id, Wait.my_form_answer)
    elif message.text == "3":
        await message.answer(t.delete_q(f), reply_markup=kb.yes_no())
        await rd.update_state(message.from_user.id, Wait.delete_confirm)
    else:
        await message.reply(t.invalid_answer)


@dp.message_handler(state=Wait.cont)
async def cont(message: types.Message):
    if message.text in ('Продолжить', 'Вернуться назад', 'Сделано!'):
        await random_form(message, await db.get_user(message.from_user.id))
    else:
        await message.answer(t.invalid_answer, reply_markup=kb.cont())


@dp.message_handler(state=Wait.get_photo, content_types=["photo"])
async def get_photo(message: types.Message):
    await message.answer(message.photo[-1].file_id)
    await Wait.get_photo.set()
