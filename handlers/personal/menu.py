from aiogram import types
from aiogram.dispatcher import FSMContext

from src.config import dp, bot
from src.wait import Wait

import decor.text as t
import decor.keyboard as kb

from handlers.personal.reactions import random_form

from db.schema import db


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    f = db.get_form(id)
    if message.text == ("1" or "Продолжить"):
        await random_form(message, state, id, f)
    elif message.text == "2":
        await bot.send_photo(photo=f["photo"], caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()
    elif message.text == "3":
        await message.answer(t.delete_q, reply_markup=kb.key_yesno())
        await Wait.delete_confirm.set()
    else:
        return await message.reply(t.invalid_answer)


@dp.message_handler(state=Wait.get_photo, content_types=["photo"])
async def get_photo(message: types.Message, state: FSMContext):
    await message.answer(message.photo[-1].file_id)
    await Wait.get_photo.set()
