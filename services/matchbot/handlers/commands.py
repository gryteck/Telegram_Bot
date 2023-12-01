from asyncio import sleep

from aiogram import types

from config import dp, bot, admins

import decor.keyboard as kb
import decor.text as t

from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.message_handler(commands="info", state="*")
async def command_info(message: types.Message):
    id = message.from_user.id
    await bot.send_chat_action(chat_id=id, action='typing')
    await sleep(1)
    await bot.send_photo(photo=open(f"images/info.png", "rb"), chat_id=id, caption=t.info,
                         reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")


@dp.message_handler(commands="admin", state="*")
async def command_admin(message: types.Message):
    id = message.from_user.id
    if id in admins:
        await message.answer("Кидай id пользователя")
        await rd.update_state(id, Wait.admin)
    else:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(id, Wait.menu_answer)


@dp.message_handler(commands="restart", state="*")
async def command_restart(message: types.Message):
    id = message.from_user.id
    if id not in admins:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(id, Wait.menu_answer)
    pass


@dp.message_handler(commands=['start', 'matchbot'], state="*")
async def command_start(message: types.Message):
    id = message.from_user.id
    if f := await db.exists_user(id):
        await message.answer("Вот твоя анкета")
        await bot.send_photo(photo=f.photo, chat_id=id, caption=t.cap(f))
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(id, Wait.menu_answer)
    else:
        await rd.update_data(id, liked_id=id)
        await message.answer(t.instruction)
        await bot.send_chat_action(chat_id=id, action='typing')
        await sleep(1)
        await message.answer(t.set_gender, reply_markup=kb.gender())
        await rd.update_state(id, Wait.set_gender)


@dp.message_handler(commands="my_profile", state="*")
async def my_profile(message: types.Message):
    id = message.from_user.id
    if not (f := await db.exists_user(id)):
        await rd.update_data(id, liked_id=id)
        await message.answer(t.instruction)
        await message.answer(t.set_gender, reply_markup=kb.gender())
        await rd.update_state(id, Wait.set_gender)
    else:
        await message.answer("Вот твоя анкета")
        await bot.send_photo(photo=f.photo, chat_id=id, caption=t.cap(f))
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await rd.update_state(id, Wait.my_form_answer)


@dp.message_handler(commands="photo", state="*")
async def get_photo(message: types.Message):
    await message.answer("Кидай фото")
    await Wait.get_photo.set()
