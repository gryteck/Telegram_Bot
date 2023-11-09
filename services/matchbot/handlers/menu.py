from aiogram import types

from config import dp, bot

import decor.text as t
import decor.keyboard as kb

from .reactions import random_form

from db.crud import db
from db.redis_api import rd, Wait


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message):
    id = message.from_user.id
    f = db.get_user(id)
    if message.text == "1":
        await random_form(message, id, f)
    elif message.text == "2":
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        rd.update_state(id, Wait.my_form_answer)
    elif message.text == "3":
        await message.answer(t.delete_q(f), reply_markup=kb.yes_no())
        rd.update_state(id, Wait.delete_confirm)
    else:
        return await message.reply(t.invalid_answer)


@dp.message_handler(state=Wait.get_photo, content_types=["photo"])
async def get_photo(message: types.Message):
    await message.answer(message.photo[-1].file_id)
    await Wait.get_photo.set()
