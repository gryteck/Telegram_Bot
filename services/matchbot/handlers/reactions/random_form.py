import random
from aiogram import types
from datetime import datetime, timezone, timedelta

from config import bot, settings
from handlers.activity import typing
from db.schemas import SUser
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t


async def get_user_from_buffer(message: types.Message, f: SUser):
    """Выводит людей из буфера"""
    await db.update_user(id=message.from_user.id, view_count=f.view_count + 1)

    l = await db.get_user(f.liked[0])

    await rd.update_data(message.from_user.id, liked_id=l.id)
    await bot.send_photo(photo=l.photo, chat_id=message.from_user.id, caption=t.like_list(f) + t.cap(l),
                         reply_markup=kb.react())
    await rd.update_state(message.from_user.id, States.form_reaction)
    return


async def random_form(message: types.Message, f: SUser):
    """Выводит рандомную анкету"""
    f = await db.update_user(message.from_user.id, liked=await db.filter_liked(f.liked))

    if f.liked:
        await get_user_from_buffer(message, f)
        return

    f = await update_view_count(message, f)

    if f.view_count > settings.DAILY_VIEWS:
        await message.answer(t.enough() + "\n\n" + t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(message.from_user.id, States.menu_answer)
        return

    if f.view_count % 15 == 0:
        if (await bot.get_chat(message.from_user.id)).has_private_forwards and (not message.from_user.username):
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=message.from_user.id,
                                 caption=t.has_private_forwards(), reply_markup=kb.custom("Сделано!"))
            await rd.update_state(f.id, States.cont)
            return
        await random_message(message, await db.get_user(message.from_user.id))
        return

    r = await db.get_random_user(message.from_user.id)

    if r is None:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await rd.update_state(message.from_user.id, States.my_form_answer)
        return

    await rd.update_data(message.from_user.id, liked_id=r.id)

    await bot.send_photo(photo=r.photo, caption=t.cap(r), chat_id=message.from_user.id, reply_markup=kb.react())
    await rd.update_state(message.from_user.id, States.form_reaction)


async def random_message(message: types.Message, f: SUser):
    await typing(message)

    if f.view_count % 60 == 0:
        await message.answer(t.day_fact(), reply_markup=kb.cont())
    elif f.view_count % 45 == 0:
        await message.answer(t.notice, reply_markup=kb.cont())
    elif f.view_count % 15 == 0:
        await bot.send_photo(photo=open(f"images/promo/{random.randint(1, 15)}.jpg", "rb"), caption=t.ad(),
                             chat_id=message.from_user.id, reply_markup=kb.cont(), parse_mode="HTML")

    await rd.update_state(message.from_user.id, States.cont)


async def update_view_count(message: types.Message, f: SUser) -> SUser:
    """Обновляет количество просмотров"""
    if datetime.now(tz=timezone(timedelta(hours=3))) - f.active_date < timedelta(hours=18):
        return await db.update_user(message.from_user.id, view_count=f.view_count + 1)

    return await db.update_user(message.from_user.id, active_date=datetime.now(), view_count=1)
