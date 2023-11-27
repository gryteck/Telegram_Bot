import random
from asyncio import sleep
from aiogram import types
from aiogram.utils import exceptions
from datetime import datetime, timezone, timedelta

from config import dp, bot, daily_views, liked_buffer

import decor.keyboard as kb
import decor.text as t

from db.crud import User
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.message_handler(state=Wait.cont)
async def cont(message: types.Message):
    if message.text in ('Продолжить', 'Вернуться назад', 'Сделано!'):
        await random_form(message, id := message.from_user.id, await db.get_user(id))
    else:
        await message.answer(t.invalid_answer, reply_markup=kb.cont())


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message):
    id = message.from_user.id
    if message.text not in ("💤", "❤️", "👎", "🚫"):
        return await message.reply(t.invalid_answer, reply_markup=kb.react())
    if message.text in ("Вернуться назад", "💤"):
        await message.answer("Подождем, пока кто-то увидит твою анкету")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        return await rd.update_state(id, Wait.menu_answer)
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        return await rd.update_state(id, Wait.claim)
    f = await db.get_user(id)
    try:
        l = await db.get_user((await rd.get_data(id)).liked_id)
    except (AttributeError, KeyError, TypeError):
        return await random_form(message, id, f)

    # обработка реакции
    if f.liked and l.id == f.liked[-1] and message.text in ("❤️", "👎"):
        f = await db.update_user(id, liked=f.liked[:-1:])
        if message.text == "❤️":
            await db.create_action(id, l.id, 'match')
            await match_message(message, id, f, l)
    elif message.text == "❤️" and (l.id > 999) and l.visible and not f.banned and (l.id not in await db.get_liked(id)):
        if len(l.liked) >= liked_buffer:
            await db.update_user(l.id, visible=False)
        if id not in l.liked:
            l.liked = l.liked+[id]
            await db.update_user(l.id, liked=l.liked)
            if len(l.liked) in [1, 5, 10, 15]:
                try:
                    await bot.send_message(text=t.liked(l), chat_id=l.id, reply_markup=kb.cont())
                    await rd.update_state(l.id, Wait.cont)
                    await db.create_action(id, l.id, 'like')
                except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
                    await db.update_user(l.id, visible=False)
    # вывод случайной анкеты
    await random_form(message, id, f)


async def random_form(message: types.Message, id: int, f: User):
    # выводим людей из буфера f['liked']
    if not f.visible and len(f.liked) < liked_buffer:
        await db.update_user(id, visible=True)
    f.liked = await db.filter_liked(f.liked)
    if f.liked:
        await db.update_user(id, count=f.view_count+1)
        l = await db.get_user(f.liked[-1])
        await rd.update_data(id, liked_id=l.id)
        await bot.send_photo(photo=l.photo, chat_id=id, caption=t.like_list(f)+t.cap(l), reply_markup=kb.react())
        return await rd.update_state(id, Wait.form_reaction)
    # проверяем количество просмотров
    if datetime.now(tz=timezone(timedelta(hours=3))) - f.active_date < timedelta(hours=18):
        f = await db.update_user(id, view_count=f.view_count+1)
    else:
        f = await db.update_user(id, active_date=datetime.now(), view_count=1)

    if f.view_count > daily_views:
        await message.answer(t.enough()+"\n\n"+t.menu_main_text, reply_markup=kb.key_123())
        return await rd.update_state(id, Wait.menu_answer)
    elif f.view_count % 20 == 0:
        if (await bot.get_chat(id)).has_private_forwards and (not (await bot.get_chat(id)).username):
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=id, caption=t.has_private_forwards(),
                                 reply_markup=kb.custom("Сделано!"))
            await rd.update_state(f.id, Wait.cont)
            return
        return await random_message(message, id, await db.get_user(id))
    # если не достигнут лимит выводим рандомные анкеты
    if r := await db.get_random_user(id):
        await rd.update_data(id, liked_id=r.id)
        await bot.send_photo(photo=r.photo, caption=t.cap(r), chat_id=id, reply_markup=kb.react())
        return await rd.update_state(id, Wait.form_reaction)
    else:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        return await rd.update_state(id, Wait.my_form_answer)


async def random_message(message: types.Message, id: int, f: User):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    if f.view_count % 80 == 0:
        await message.answer(t.day_fact(), reply_markup=kb.cont())
    elif f.view_count % 60 == 0:
        await message.answer(t.notice, reply_markup=kb.cont())
    elif f.view_count % 20 == 0:
        await bot.send_photo(photo=open(f"images/promo/{random.randint(1, 15)}.jpg", "rb"), caption=t.ad(), chat_id=id,
                             reply_markup=kb.cont(), parse_mode="HTML")
    return await rd.update_state(id, Wait.cont)


async def match_message(message: types.Message, id: int, f: User, l: User):
    # sending msg to l
    try:
        if (username := (await bot.get_chat(id)).username) is not None:
            await bot.send_photo(photo=f.photo, chat_id=l.id, caption=t.cap(f), reply_markup=kb.match(username))
            await bot.send_message(text=t.like_match(), chat_id=l.id, reply_markup=kb.cont())
        elif not (await bot.get_chat(id)).has_private_forwards:
            await bot.send_photo(photo=f.photo, chat_id=l.id, caption=t.cap(f), reply_markup=kb.match(id))
            await bot.send_message(text=t.like_match(), chat_id=l.id, reply_markup=kb.cont())
        else:
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=id, caption=t.bad_request(),
                                 reply_markup=kb.cont())
            await rd.update_state(id, Wait.cont)
            await bot.send_message(text='Упс, у пользователя ограничения', chat_id=l.id, reply_markup=kb.cont())
            await rd.update_state(l.id, Wait.cont)
            return
    except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
        await db.update_user(l.id, visible=False)

    # sending message to f
    if (username := (await bot.get_chat(l.id)).username) is not None:
        await bot.send_message(text=t.like_match(), chat_id=id, reply_markup=kb.match(username))
    elif not (await bot.get_chat(l.id)).has_private_forwards:
        await bot.send_message(text=t.like_match(), chat_id=id, reply_markup=kb.match(l.id))
    else:
        try:
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=l.id, caption=t.bad_request(),
                                 reply_markup=kb.cont())
            await rd.update_state(l.id, Wait.cont)
            await message.answer('Упс, у пользователя ограничения', reply_markup=kb.cont())
            await rd.update_state(f.id, Wait.cont)
        except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
            await db.update_user(l.id, visible=False)
