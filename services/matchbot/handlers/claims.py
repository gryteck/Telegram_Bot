import decor.keyboard as kb
import decor.text as t
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, bot, supp_id
from db.schema import db
from .reactions import random_form
from states import Wait


@dp.message_handler(state=Wait.claim)
async def claim(message: types.Message, state: FSMContext):
    if message.text not in ("1", "2", "3", "4", "Продолжить"):
        await message.reply("Нет такого варианта ответа")
        return await Wait.claim.set()
    id, key = message.from_user.id, message.text
    data = await state.get_data()
    f = db.get_form(id)
    liked_id = data['liked_id']
    l = db.get_form(liked_id)
    if message.text in ["1", "2"]:
        if str(id) not in l['noticed']: db.patch_claims(liked_id, l['noticed']+[id], l['claims']+[message.text])
        if liked_id in f['liked']: f['liked'] = db.patch_liked(id, f['liked'][:-1])
        await message.answer(t.ban_thq)
    elif message.text == "Продолжить":
        return await random_form(message, state, id, f)
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
        return await Wait.claim.set()
    elif message.text == "Продолжить": return await random_form(message, state, id, db.get_form(id))
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
