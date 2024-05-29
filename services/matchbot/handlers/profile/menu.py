from aiogram import types, exceptions

from config import dp, bot
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
from handlers.reactions.random_form import random_form
import utils.keyboard as kb
import utils.text as t


@dp.message_handler(state=States.my_form_answer)
async def my_form_answer(message: types.Message):
    if message.text == "1":
        await message.answer("Для начала давай выберем пол", reply_markup=kb.gender())
        await rd.update_state(message.from_user.id, States.set_gender)
    elif message.text == "2":
        try:
            await message.answer(t.set_text((await rd.get_data(message.from_user.id)).text),
                                 reply_markup=kb.custom("Оставить текущее"))
        except (AttributeError, KeyError, exceptions.BadRequest):
            await message.answer(t.set_text(), reply_markup=types.ReplyKeyboardRemove())
        await rd.update_state(message.from_user.id, States.change_text)
    elif message.text == "3":
        try:
            await bot.send_photo(photo=(await rd.get_data(message.from_user.id)).photo, chat_id=message.from_user.id,
                                 caption=t.current_photo)
            await message.answer(text=t.set_photo(), reply_markup=kb.custom("Оставить текущее"))
        except (AttributeError, KeyError, exceptions.BadRequest):
            await bot.send_message(text=t.set_photo(), chat_id=message.from_user.id,
                                   reply_markup=types.ReplyKeyboardRemove())
        await rd.update_state(message.from_user.id, States.change_photo)
    elif message.text == "4":
        await random_form(message, await db.get_user(message.from_user.id))
    else:
        await message.reply(t.invalid_answer)
