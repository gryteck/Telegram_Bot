import random
from aiogram import types
from aiogram.utils import exceptions
from datetime import datetime, timezone, timedelta

from config import dp, bot, settings

import decor.keyboard as kb
import decor.text as t

from .activity import typing
from db.schemas import SUser
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message):
    if not await reaction_message_processor(message):
        return

    f = await db.get_user(message.from_user.id)

    try:
        liked_id = (await rd.get_data(message.from_user.id)).liked_id
        l = await db.get_user(liked_id)
    except (AttributeError, KeyError, TypeError):
        await random_form(message, f)
        return

    if buffer_is_not_empty(message, f, l):
        await buffer_reaction_processing(message, f, l)
        return

    if await reaction_should_be_processed(message, f, l):
        await reaction_processing(message, l)

    await random_form(message, f)


def buffer_is_not_empty(message: types.Message, f: SUser, l: SUser) -> bool:
    return l.id in f.liked and message.text in ("❤️", "👎")


async def reaction_should_be_processed(message: types.Message, f: SUser, l: SUser) -> bool:
    return message.text == "❤️" and (l.id > 999) and l.visible and not f.banned and (
                l.id not in await db.get_likes(message.from_user.id))


async def reaction_message_processor(message: types.Message):
    if message.text not in ("💤", "❤️", "👎", "🚫"):
        await message.reply(t.invalid_answer, reply_markup=kb.react())
        await rd.update_state(message.from_user.id, Wait.form_reaction)
    elif message.text in ("Вернуться назад", "💤"):
        await message.answer("Подождем, пока кто-то увидит твою анкету")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(message.from_user.id, Wait.menu_answer)
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        await rd.update_state(message.from_user.id, Wait.claim)
    else:
        return True


async def buffer_reaction_processing(message: types.Message, f: SUser, l: SUser):
    f.liked.remove(l.id)

    f = await db.update_user(message.from_user.id, liked=f.liked)

    if message.text == "❤️":
        await db.create_action(message.from_user.id, l.id, 'match')
        await match_message(message, f, l)
        return

    await random_form(message.from_user.id, f)


async def reaction_processing(message: types.Message, l: SUser):
    """Обработка реакции"""
    if message.from_user.id not in l.liked:
        if len(l.liked) >= settings.LIKED_BUFFER:
            await db.update_user(l.id, visible=False)

        l = await db.update_user(l.id, liked=await db.filter_liked(l.liked + [message.from_user.id]))
        if len(l.liked) in [1, 5, 10, 15]:
            try:
                await bot.send_message(text=t.liked(l), chat_id=l.id, reply_markup=kb.cont())
                await rd.update_state(l.id, Wait.cont)
                await db.create_action(message.from_user.id, l.id, 'like')
            except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
                await db.update_user(l.id, visible=False)


async def get_user_from_buffer(message: types.Message, f: SUser):
    """Выводит людей из буфера"""
    await db.update_user(id=message.from_user.id, view_count=f.view_count + 1)

    l = await db.get_user(f.liked[0])

    await rd.update_data(message.from_user.id, liked_id=l.id)
    await bot.send_photo(photo=l.photo, chat_id=message.from_user.id, caption=t.like_list(f) + t.cap(l),
                         reply_markup=kb.react())
    await rd.update_state(message.from_user.id, Wait.form_reaction)
    return


async def update_view_count(message: types.Message, f: SUser) -> SUser:
    """Обновляет количество просмотров"""
    if datetime.now(tz=timezone(timedelta(hours=3))) - f.active_date < timedelta(hours=18):
        return await db.update_user(message.from_user.id, view_count=f.view_count + 1)

    return await db.update_user(message.from_user.id, active_date=datetime.now(), view_count=1)


async def random_form(message: types.Message, f: SUser):
    """Выводит рандомную анкету"""
    f = await db.update_user(message.from_user.id, liked=await db.filter_liked(f.liked))

    if f.liked:
        await get_user_from_buffer(message, f)
        return

    f = await update_view_count(message, f)

    if f.view_count > settings.DAILY_VIEWS:
        await message.answer(t.enough() + "\n\n" + t.menu_main_text, reply_markup=kb.key_123())
        await rd.update_state(message.from_user.id, Wait.menu_answer)
        return

    if f.view_count % 15 == 0:
        if (await bot.get_chat(message.from_user.id)).has_private_forwards and (
                not (await bot.get_chat(message.from_user.id)).username):
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=message.from_user.id,
                                 caption=t.has_private_forwards(), reply_markup=kb.custom("Сделано!"))
            await rd.update_state(f.id, Wait.cont)
            return
        await random_message(message, await db.get_user(message.from_user.id))
        return

    r = await db.get_random_user(message.from_user.id)

    await rd.update_state(message.from_user.id, Wait.form_reaction)

    if r is None:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())

    await rd.update_data(message.from_user.id, liked_id=r.id)

    await bot.send_photo(photo=r.photo, caption=t.cap(r), chat_id=message.from_user.id, reply_markup=kb.react())
    await rd.update_state(message.from_user.id, Wait.form_reaction)


async def random_message(message: types.Message, f: SUser):
    await typing(message)

    if f.view_count % 60 == 0:
        await message.answer(t.day_fact(), reply_markup=kb.cont())
    elif f.view_count % 45 == 0:
        await message.answer(t.notice, reply_markup=kb.cont())
    elif f.view_count % 15 == 0:
        await bot.send_photo(photo=open(f"images/promo/{random.randint(1, 15)}.jpg", "rb"), caption=t.ad(),
                             chat_id=message.from_user.id, reply_markup=kb.cont(), parse_mode="HTML")

    await rd.update_state(message.from_user.id, Wait.cont)


async def match_message(message: types.Message, f: SUser, l: SUser):
    # sending msg to l
    try:
        if (username := (await bot.get_chat(message.from_user.id)).username) is not None:
            await bot.send_photo(photo=f.photo, chat_id=l.id, caption=t.cap(f), reply_markup=kb.match(username))
            await bot.send_message(text=t.like_match(), chat_id=l.id, reply_markup=kb.cont())
        elif not (await bot.get_chat(message.from_user.id)).has_private_forwards:
            await bot.send_photo(photo=f.photo, chat_id=l.id, caption=t.cap(f),
                                 reply_markup=kb.match(message.from_user.id))
            await bot.send_message(text=t.like_match(), chat_id=l.id, reply_markup=kb.cont())
        else:
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=message.from_user.id,
                                 caption=t.bad_request(), reply_markup=kb.cont())
            await rd.update_state(message.from_user.id, Wait.cont)
            return
    except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
        await db.update_user(l.id, visible=False)
        await message.answer('Упс, у пользователя ограничения', reply_markup=kb.cont())
        await rd.update_state(message.from_user.id, Wait.cont)
        return

    # sending message to f
    if (username := (await bot.get_chat(l.id)).username) is not None:
        await bot.send_message(text=t.like_match(), chat_id=message.from_user.id, reply_markup=kb.match(username))
    elif not (await bot.get_chat(l.id)).has_private_forwards:
        await bot.send_message(text=t.like_match(), chat_id=message.from_user.id, reply_markup=kb.match(l.id))
    else:
        try:
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=l.id, caption=t.bad_request(),
                                 reply_markup=kb.cont())
            await rd.update_state(l.id, Wait.cont)
            await message.answer('Упс, у пользователя ограничения', reply_markup=kb.cont())
            await rd.update_state(message.from_user.id, Wait.cont)
        except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
            await db.update_user(l.id, visible=False)
