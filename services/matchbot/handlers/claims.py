import decor.keyboard as kb
import decor.text as t
from aiogram import types
from config import dp, bot, supp_id

from db.crud import db
from db.redis_api import rd, Wait

from .reactions import random_form


@dp.message_handler(state=Wait.claim)
async def claim(message: types.Message):
    id = message.from_user.id
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        return await Wait.claim.set()
    data = rd.get_data(id)
    f = db.get_user(id)
    liked_id = data.liked_id
    l = db.get_user(liked_id)
    if message.text in ["1", "2"]:
        if str(id) not in l.noticed:
            db.patch_claims(liked_id, l.noticed + [id], l.claims+message.text)
        if liked_id in f.liked:
            f.liked = db.patch_liked(id, f.liked[:-1])
        await message.answer(t.ban_thq)
    if message.text == "3":
        await message.answer(t.claim_text, reply_markup=kb.back())
        rd.update_state(id, Wait.claim_text)
        return
    # вывод анкеты
    await random_form(message, id, f)


@dp.message_handler(state=Wait.claim_text)
async def claim_text(message: types.Message):
    id = message.from_user.id
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        return rd.update_state(id, Wait.claim)
    data = rd.get_data(id)
    liked_id = data.liked_id
    l = db.get_form(liked_id)
    f = db.get_form(id)
    if id not in l.noticed:
        db.patch_claims(liked_id, l.noticed.append(id), l.claims+"3")
        db.update_user(liked_id, noticed=l.noticed+id, claims=l.claims+"3")
    await bot.send_photo(photo=l.photo, chat_id=supp_id,
                         caption=f"#claim {liked_id}\n{t.cap(l)}\n\nFrom {id}:\n{message.text}")
    await message.answer(t.ban_thq)
    # вывод анкеты
    await random_form(message, id, f)
