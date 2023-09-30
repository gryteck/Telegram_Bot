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
    elif message.text == "3":
        await message.answer("Кидай промокод", reply_markup=types.ReplyKeyboardRemove())
        await Wait.admin_promo_check.set()
    elif message.text == "4":
        await message.answer("Кидай имя промоутера", reply_markup=types.ReplyKeyboardRemove())
        await Wait.admin_promo_new.set()


@dp.message_handler(state=Wait.admin_ban_list)
async def get_ban_list(message: types.Message, state: FSMContext):
    if message.text not in ("↩️", "✅", "❌", "⁉️"): return await message.answer("Ты че мудришь, норм отвечай")
    data = await state.get_data()
    liked_id = data["liked_id"]
    if message.text == "✅": db.patch_ban(liked_id, False)
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
    await Wait.admin_form_by_id.set()


@dp.message_handler(state=Wait.admin_form_by_id)
async def admin_form_by_id(message: types.Message, state: FSMContext):
    id = message.from_user.id
    try: l = db.get_form(int(message.text))
    except (ValueError, IndexError, TypeError): return await message.reply("Нет такого человечка")
    await state.update_data(liked_id=l['id'])
    await bot.send_photo(photo=l['photo'], caption=t.adm_cap(l), chat_id=id, reply_markup=kb.ban())
    await Wait.admin_ban_list.set()


@dp.message_handler(state=Wait.admin_promo_check)
async def admin_promo_check(message: types.Message):
    await message.answer(t.adm_promo(db.get_promocode(message.text)))
    await message.answer(t.admin_menu, reply_markup=kb.key_1234())
    await Wait.admin_menu.set()

@dp.message_handler(state=Wait.admin_promo_new)
async def admin_promo_new(message: types.Message, state: FSMContext):
    while True:
        promocode = str(hex(random.randint(0x10000, 0xFFFFF))[2:].upper())
        if promocode not in db.get_promocodes(): break
    db.post_promocode(message.text, promocode)
    await message.answer(t.adm_promo(db.get_promocode(promocode)))
    await message.answer(t.admin_menu, reply_markup=kb.key_1234())
    await Wait.admin_menu.set()
