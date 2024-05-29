from aiogram import types

from config import dp
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t
from .reaction_processing import reaction_processing, reaction_should_be_processed
from .buffer_processing import buffer_is_not_empty, buffer_reaction_processing
from .random_form import random_form


async def reaction_message_processor(message: types.Message):
    if message.text not in ("💤", "❤️", "👎", "🚫", "Продолжить"):
        await message.reply(t.invalid_answer, reply_markup=kb.react())
        await rd.update_state(message.from_user.id, States.form_reaction)
    elif message.text in ("Вернуться назад", "💤"):
        await message.answer("Подождем, пока кто-то увидит твою анкету")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(message.from_user.id, States.menu_answer)
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        await rd.update_state(message.from_user.id, States.claim)
    else:
        return True


@dp.message_handler(state=States.form_reaction)
async def form_reaction(message: types.Message):
    if not await reaction_message_processor(message):
        return

    f = await db.get_user(message.from_user.id)

    try:
        liked_id = (await rd.get_data(message.from_user.id)).liked_id
        l = await db.get_user(liked_id)
    except (AttributeError, KeyError, TypeError):
        await random_form(message, f)
        return

    if buffer_is_not_empty(message, f, l):
        await buffer_reaction_processing(message, f, l)
        return

    if await reaction_should_be_processed(message, f, l):
        await reaction_processing(message, l)

    await random_form(message, f)
