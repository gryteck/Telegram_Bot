import utils.keyboard as kb
import utils.text as t
from aiogram import types
from config import dp, bot, settings

from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States

from .reactions import random_form


@dp.message_handler(state=States.claim)
async def claim(message: types.Message):
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        return await rd.update_state(message.from_user.id, States.claim)
    f, l = await db.get_user(message.from_user.id), await db.get_user(
        (await rd.get_data(message.from_user.id)).liked_id)
    if message.text in ["1", "2"]:
        if message.from_user.id not in l.noticed and l.id < 999:
            f = await db.update_user(l.id, noticed=l.noticed + [message.from_user.id],
                                     claims=l.claims + [int(message.text)])
            await db.create_action(message.from_user.id, l.id, 'claim')
        if l.id in f.liked:
            f = await db.update_user(message.from_user.id, liked=f.liked[:-1])
        await message.answer(t.ban_thq)
    if message.text == "3":
        await message.answer(t.claim_text, reply_markup=kb.back())
        await rd.update_state(message.from_user.id, States.claim_text)
        return
    # вывод анкеты
    await random_form(message, f)


@dp.message_handler(state=States.claim_text)
async def claim_text(message: types.Message):
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        await rd.update_state(message.from_user.id, States.claim)
        return

    liked_id = (await rd.get_data(message.from_user.id)).liked_id

    l, f = await db.get_user(liked_id), await db.get_user(message.from_user.id)

    if message.from_user.id not in l.noticed and l.id < 999:
        await db.update_user(liked_id, noticed=l.noticed + [message.from_user.id], claims=l.claims + [3])
        await db.create_action(message.from_user.id, l.id, 'claim')

    await bot.send_photo(photo=l.photo, chat_id=settings.SUPPORT_ID,
                         caption=f"#claim {liked_id}\n{t.cap(l)}\n\nFrom {message.from_user.id}:\n{message.text}")
    await message.answer(t.ban_thq)
    # вывод анкеты
    await random_form(message, f)
