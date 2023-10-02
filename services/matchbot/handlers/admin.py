import random
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions

import decor.keyboard as kb
import decor.text as t
from config import dp, bot
from db.schema import db
from states import Wait


@dp.message_handler(state=Wait.admin_menu)
async def admin_menu(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "1":
        l = db.get_random_claim()
        await state.update_data(liked_id=l["id"])
        await bot.send_photo(photo=l["photo"], caption=t.cap(l), chat_id=id, reply_markup=kb.ban())
        await message.answer(text=l['claims'], reply_markup=kb.match(l["id"]))
        await Wait.admin_ban_list.set()
    elif message.text == "2":
        await message.answer("Ну вводи id, прижучим", reply_markup=types.ReplyKeyboardRemove())
        await Wait.admin_form_by_id.set()


@dp.message_handler(state=Wait.admin_ban_list)
async def get_ban_list(message: types.Message, state: FSMContext):
    try:
        l = db.get_form(int(message.text))
        await state.update_data(liked_id=l['id'])
        await bot.send_photo(photo=l['photo'], caption=t.adm_cap(l), chat_id=message.from_user.id, reply_markup=kb.ban())
        await Wait.admin_ban_list.set()
    except (ValueError, IndexError, TypeError):
        if message.text not in ("↩️", "✅", "❌", "⁉️"):
            return await message.answer("Ты че мудришь, норм отвечай")
        liked_id = (await state.get_data())["liked_id"]
        if message.text == "✅":
            db.patch_ban(liked_id, False)
        elif message.text == "❌":
            db.patch_ban(liked_id, True)
            await message.answer("Забанен")
        elif message.text == "⁉️":
            try:
                await bot.send_message(text=t.warning_ban, chat_id=liked_id)
                await message.answer("Предупрежден")
            except exceptions.BotBlocked:
                db.patch_visible(liked_id, False)
                await message.answer("Он решил скрыться")
        await message.answer("Жду новый id")
        await Wait.admin_ban_list.set()



@dp.message_handler(state=Wait.admin_form_by_id)
async def admin_form_by_id(message: types.Message, state: FSMContext):
    id = message.from_user.id
    try: l = db.get_form(int(message.text))
    except (ValueError, IndexError, TypeError): return await message.reply("Нет такого человечка")
    await state.update_data(liked_id=l['id'])
    await bot.send_photo(photo=l['photo'], caption=t.adm_cap(l), chat_id=id, reply_markup=kb.ban())
    await Wait.admin_ban_list.set()
