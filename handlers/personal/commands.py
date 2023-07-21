from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext

from src.config import dp, bot, admins
from src.wait import Wait

import decor.text as t
import decor.keyboard as kb

from db.schema import db

@dp.message_handler(commands="info", state="*")
async def info(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    await bot.send_photo(photo=open(f"photos/info.png", "rb"), chat_id=message.from_user.id,
                         caption=t.info, reply_markup=kb.back())
    await message.answer("Мы в "+'<a href="https://t.me/asiaparty">телеграм</a>', parse_mode="HTML")


@dp.message_handler(commands="admin", state="*")
async def admin(message: types.Message):
    id = message.from_user.id
    if id in admins:
        await message.answer(t.admin_menu, reply_markup=kb.key_1234())
        await Wait.admin_menu.set()
    else:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="restart", state="*")
async def restart(message: types.Message):
    if message.from_user.id not in admins:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()
        return
    db.drop_table_users()
    db.create_table_users()
    await message.reply("Рестартнуто")


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not db.user_exists(id):
        await state.update_data(liked_id=id)
        await message.answer(t.instruction)
        await bot.send_chat_action(chat_id=id, action='typing')
        await sleep(1)
        await message.answer(t.set_gender, reply_markup=kb.key_gender())
        await Wait.set_gender.set()
    else:
        f = db.get_form(id)
        await bot.send_photo(photo=f['photo'], chat_id=id, caption=t.cap(f))
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="my_profile", state="*")
async def my_profile(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not db.user_exists(id):
        await state.update_data(liked_id=id)
        await message.answer(t.instruction)
        await message.answer(t.set_gender, reply_markup=kb.key_gender())
        await Wait.set_gender.set()
    else:
        f = db.get_form(id)
        await bot.send_photo(photo=f['photo'], chat_id=id, caption=f['text'])
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()

@dp.message_handler(commands="pfvvfhoto", state="*")
async def get_photo(message: types.Message, state: FSMContext):
    await message.answer("Кидай фото")
    await Wait.get_photo.set()
