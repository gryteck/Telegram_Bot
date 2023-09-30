from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext

from config import dp, bot, admins
from states import Wait

import decor.keyboard as kb
import decor.text as t

from db.schema import db

from .activity import get_qrcode, matchbot


@dp.message_handler(commands="info", state="*")
async def command_info(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    await bot.send_photo(photo=open(f"images/info.jpg", "rb"), chat_id=message.from_user.id,
                         caption=t.info, reply_markup=types.ReplyKeyboardRemove, parse_mode="HTML")


@dp.message_handler(commands="admin", state="*")
async def command_admin(message: types.Message):
    id = message.from_user.id
    if id in admins:
        await message.answer(t.admin_menu, reply_markup=kb.key_1234())
        await Wait.admin_menu.set()
    else:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="restart", state="*")
async def command_restart(message: types.Message):
    if message.from_user.id not in admins:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        return await Wait.menu_answer.set()
    pass


@dp.message_handler(commands=['start'], state="*")
async def command_start(message: types.Message, state: FSMContext):
    if ref := message.get_args():
        if ref == "matchbot": await matchbot(message, state)
        elif ref == "qrcode": await get_qrcode(message, state, "qrcode")
        elif ref in db.get_promocodes(): await get_qrcode(message, state, ref)
    else:
        await message.answer(t.start, reply_markup=kb.start())
        await Wait.start.set()


@dp.message_handler(commands="my_profile", state="*")
async def my_profile(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not db.user_exists(id):
        await state.update_data(liked_id=id)
        await message.answer(t.instruction)
        await message.answer(t.set_gender, reply_markup=kb.gender())
        await Wait.set_gender.set()
    else:
        f = db.get_form(id)
        await message.answer("Вот твоя анкета")
        await bot.send_photo(photo=f['photo'], chat_id=id, caption=t.cap(f))
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()


@dp.message_handler(commands="qrcode", state="*")
async def command_qrcode(message: types.Message, state: FSMContext):
    await get_qrcode(message, state, "qrcode")


@dp.message_handler(commands='matchbot', state="*")
async def command_matchbot(message: types.Message, state: FSMContext):
    await matchbot(message, state)


@dp.message_handler(commands="photo", state="*")
async def get_photo(message: types.Message):
    await message.answer("Кидай фото")
    await Wait.get_photo.set()


@dp.message_handler(commands="qr_admin", state="*")
async def qr_admin(message: types.Message):
    await message.answer("кидай фотку")
    await Wait.qr_admin.set()
