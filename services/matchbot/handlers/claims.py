import decor.keyboard as kb
import decor.text as t
from aiogram import types
from config import dp, bot, supp_id

from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait

from .reactions import random_form


@dp.message_handler(state=Wait.claim)
async def claim(message: types.Message):
    id = message.from_user.id
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        return await Wait.claim.set()
    f, l = await db.get_user(id), await db.get_user(await rd.get_data(id).liked_id)
    if message.text in ["1", "2"]:
        if id not in l.noticed:
            f = await db.update_user(l.id, noticed=l.noticed+[id], claims=l.claims+[message.text])
            await db.create_action(id, l.id, 'claim')
        if l.id in f.liked:
            f = await db.update_user(id, liked=f.liked[:-1])
        await message.answer(t.ban_thq)
    if message.text == "3":
        await message.answer(t.claim_text, reply_markup=kb.back())
        await rd.update_state(id, Wait.claim_text)
        return
    # вывод анкеты
    await random_form(message, id, f)


@dp.message_handler(state=Wait.claim_text)
async def claim_text(message: types.Message):
    id = message.from_user.id
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        return await rd.update_state(id, Wait.claim)
    data = await rd.get_data(id)
    liked_id = data.liked_id
    l = await db.get_user(liked_id)
    f = await db.get_user(id)
    if id not in l.noticed:
        await db.update_user(liked_id, noticed=l.noticed+[id], claims=l.claims+["3"])
        await db.create_action(id, l.id, 'claim')
    await bot.send_photo(photo=l.photo, chat_id=supp_id,
                         caption=f"#claim {liked_id}\n{t.cap(l)}\n\nFrom {id}:\n{message.text}")
    await message.answer(t.ban_thq)
    # вывод анкеты
    await random_form(message, id, f)
