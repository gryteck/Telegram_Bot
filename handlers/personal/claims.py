from aiogram import types
from aiogram.dispatcher import FSMContext

from src.config import dp, bot, supp_id
from src.wait import Wait

import decor.text as t
import decor.keyboard as kb

from handlers.personal.reactions import random_form

from db.schema import db


@dp.message_handler(state=Wait.claim)
async def claim(message: types.Message, state: FSMContext):
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        await Wait.claim.set()
        return
    id, key = message.from_user.id, message.text
    data = await state.get_data()
    f = db.get_form(id)
    liked_id = data['liked_id']
    l = db.get_form(liked_id)
    if message.text in ["1", "2"]:
        if str(id) not in l['noticed']: db.patch_claims(liked_id, l['noticed']+[id], l['claims']+[message.text])
        if liked_id in f['liked']: f['liked'] = db.patch_liked(id, f['liked'][:-1])
        await message.answer(t.ban_thq)
    if message.text == "3":
        await message.answer(t.claim_text, reply_markup=kb.back())
        await Wait.claim_text.set()
        return
    # вывод анкеты
    await random_form(message, state, id, f)


@dp.message_handler(state=Wait.claim_text)
async def claim_text(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        await Wait.claim.set()
        return
    data = await state.get_data()
    liked_id = data['liked_id']
    l = db.get_form(liked_id)
    f = db.get_form(id)
    if id not in l['noticed']: db.patch_claims(liked_id, l['noticed']+[id], l['claims']+["3"])
    await bot.send_photo(photo=l['photo'], chat_id=supp_id,
                         caption=f"#claim {liked_id}\n{t.cap(l)}\n\nFrom {id}:\n{message.text}")
    await message.answer(t.ban_thq)
    # вывод анкеты
    await random_form(message, state, id, f)
