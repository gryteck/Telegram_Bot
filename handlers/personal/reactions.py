from asyncio import sleep
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions

from random import choice

from src.config import dp, bot, daily_views, liked_buffer, promo, br_photo
from src.wait import Wait

import decor.text as t
import decor.keyboard as kb

from db.schema import db

@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text not in ("Продолжить", "Вернуться назад", "💤", "❤️", "👎", "🚫", "Сделано!"):
        return await message.reply(t.invalid_answer)
    if message.text in ("Вернуться назад", "💤"):
        await message.answer("Подождем, пока кто-то увидит твою анкету")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        return await Wait.menu_answer.set()
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        return await Wait.claim.set()
    elif message.text in ("Продолжить", "Сделано!"): return await random_form(message, state, id, db.get_form(id))
    f = db.get_form(id)
    try: liked_id = (await state.get_data())["liked_id"]
    except KeyError: return await random_form(message, state, id, f)
    l = db.get_form(liked_id)
    # обработка реакции
    if f['liked'] and liked_id == f['liked'][-1] and message.text in ("❤️", "👎"):
        f['liked'] = db.patch_liked(id, f['liked'][:-1:])
        if message.text == "❤️":
            await match_message(message, state, id, f, l)
    elif message.text == "❤️" and (liked_id > 999) and l['visible'] and not f['banned']:
        db.patch_count(id)
        if len(l['liked']) >= liked_buffer: db.patch_visible(liked_id, False)
        if id not in l['liked']:
            l['liked'].append(id)
            if len(l['liked']) in [1, 5, 10, 15]:
                try:
                    await bot.send_message(text=t.liked(l), chat_id=liked_id, reply_markup=kb.cont())
                except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
                    db.patch_visible(liked_id, False)
            db.patch_liked(liked_id, l['liked'])
    # вывод рандомной анкеты
    await random_form(message, state, id, f)

async def random_form(message: types.Message, state: FSMContext, id: int, f: dict):
    # выводим людей из буффера f['liked']
    if not f['visible'] and len(f['liked']) < liked_buffer:
        db.patch_visible(id, True)
    if f['liked']:
        while f['liked'] and not db.user_exists(f['liked'][-1]):
            f['liked'].pop()
        db.patch_liked(id, f['liked'])
        if f['liked']:
            db.patch_count(id)
            l = db.get_form(f['liked'][-1])
            await state.update_data(liked_id=l['id'])
            await bot.send_photo(photo=l['photo'], chat_id=id, caption=t.like_list(f)+t.cap(l), reply_markup=kb.react())
            return await Wait.form_reaction.set()
    # проверяем количество просмотров
    view_count = db.patch_count(id)
    if view_count > daily_views:
        await message.answer(t.enough()+"\n\n"+t.menu_main_text, reply_markup=kb.key_123())
        return await Wait.menu_answer.set()
    elif view_count % 20 == 0:
        if (await bot.get_chat(id)).has_private_forwards and (not (await bot.get_chat(id)).username):
            await bot.send_photo(photo=br_photo, chat_id=id, caption=t.has_private_forwards(), reply_markup=kb.custom("Сделано!"))
            return
        return await random_message(message, state, id, db.get_form(id))
    # если не достигнут лимит выводим рандомные анкеты
    try: r = db.get_random_user(id, f['age'], f['interest'])
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f['photo'], caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        return await Wait.my_form_answer.set()
    await state.update_data(liked_id=r['id'])
    await bot.send_photo(photo=r['photo'], caption=t.cap(r), chat_id=id, reply_markup=kb.react())
    await Wait.form_reaction.set()

async def random_message(message: types.Message, state: FSMContext, id: int, f: dict):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    if f['view_count'] % 80 == 0:
        await message.answer(t.day_fact(), reply_markup=kb.cont())
    elif f['view_count'] % 60 == 0:
        await message.answer(t.notice, reply_markup=kb.cont())
    elif f['view_count'] % 20 == 0:
        await bot.send_photo(photo=choice(promo), caption=t.ad(), chat_id=id, reply_markup=kb.cont(), parse_mode="HTML")
    return await Wait.form_reaction.set()

async def match_message(message: types.Message, state: FSMContext, id: int, f: dict, l: dict):
    # sending msg to l
    try:
        if (username := (await bot.get_chat(id)).username) is not None:
            await bot.send_photo(photo=f['photo'], chat_id=l['id'], caption=t.cap(f), reply_markup=kb.match(username))
            await bot.send_message(text=t.like_match(), chat_id=l['id'], reply_markup=kb.cont())
        elif not (await bot.get_chat(id)).has_private_forwards:
            await bot.send_photo(photo=f['photo'], chat_id=l['id'], caption=t.cap(f), reply_markup=kb.match(id))
            await bot.send_message(text=t.like_match(), chat_id=l['id'], reply_markup=kb.cont())
        else:
            await bot.send_photo(photo=br_photo, chat_id=id, caption=t.bad_request(), reply_markup=kb.cont())
    except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
        db.patch_visible(l['id'], False)
    # sending message to f
    if (username := (await bot.get_chat(l['id'])).username) is not None:
        await bot.send_message(text=t.like_match(), chat_id=id, reply_markup=kb.match(username))
    elif not (await bot.get_chat(l['id'])).has_private_forwards:
        await bot.send_message(text=t.like_match(), chat_id=id, reply_markup=kb.match(l['id']))
    else:
        try:
            await bot.send_photo(photo=br_photo, chat_id=l['id'], caption=t.bad_request(), reply_markup=kb.cont())
        except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
            db.patch_visible(l['id'], False)
