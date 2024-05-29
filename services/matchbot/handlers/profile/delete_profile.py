from aiogram import types

from config import dp, bot
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t


@dp.message_handler(state=States.delete_confirm)
async def delete_confirm(message: types.Message):
    if message.text == "Да":
        await db.update_user(message.from_user.id, visible=False)
        await message.answer(t.del_form, reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Нет":
        f = await db.get_user(message.from_user.id)
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await rd.update_state(message.from_user.id, States.my_form_answer)
    else:
        await message.reply(t.invalid_answer)
