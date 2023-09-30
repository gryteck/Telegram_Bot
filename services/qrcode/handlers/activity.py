import asyncio
import qrcode
from io import BytesIO
from aiogram import types
from aiogram.dispatcher import FSMContext

import decor.keyboard as kb
import decor.text as t
from aiogram.utils import exceptions

from config import bot, sleep_time
from db.schema import db
from states import Wait


async def check_inactive():
    while True:
        await asyncio.sleep(sleep_time)
        users = db.patch_daily_inactive_users()
        if users is not None:
            for user in users:
                try: await bot.send_message(user, t.daily_miss_u(), reply_markup=kb.cont())
                except (exceptions.BotBlocked, exceptions.ChatNotFound):
                    if user > 999: db.patch_visible(user, False)
        users = db.patch_inactive_users()
        if users is not None:
            for user in users:
                try: await bot.send_message(user, t.miss_u(), reply_markup=kb.cont())
                except (exceptions.BotBlocked, exceptions.ChatNotFound):
                    if user > 999: db.patch_visible(user, False)


async def send_qr(id: int, f: dict) -> None:
    qr_data = str(id)
    img = qrcode.make(qr_data)
    # Создаем объект BytesIO для хранения изображения в памяти
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    await bot.send_photo(photo=img_buffer, chat_id=id, caption=t.cap_qr(f), reply_markup=kb.qr_menu())
    return img_buffer.close()


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


async def get_qrcode(message: types.Message, state: FSMContext, promocode) -> None:
    id = message.from_user.id
    if db.qr_exists(id):
        await send_qr(id, db.get_qr(id))
        await Wait.qrcode.set()
    elif db.user_exists(id):
        f = db.get_form(id)
        db.post_qr(id, f['name'], f['age'], f['gender'], message.from_user.username, promocode)
        await send_qr(id, f)
        await Wait.qrcode.set()
    else:
        await state.update_data(promocode=promocode)
        try:
            f = await state.get_data()
            db.post_qr(id, f['name'], f['age'], f['gender'], message.from_user.username, promocode)
            await send_qr(id, f)
            await Wait.qrcode.set()
        except KeyError:
            await message.answer(t.set_gender, reply_markup=kb.gender())
            await Wait.qr_gender.set()
