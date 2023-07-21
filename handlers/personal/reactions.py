import logging
from asyncio import sleep
from aiogram import types
from aiogram.dispatcher import FSMContext

from random import choice

from src.config import dp, bot, daily_views, liked_buffer, promo
from src.wait import Wait

import decor.text as t
import decor.keyboard as kb

from db.schema import db


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        return await message.reply(t.invalid_answer)
    if message.text == "Вернуться назад":
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        return await Wait.menu_answer.set()
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        return await Wait.claim.set()
    f = db.get_form(id)
    data = await state.get_data()
    try: liked_id = data["liked_id"]
    except KeyError: return await random_form(message, state, id, f)
    l = db.get_form(liked_id)
    # обработка реакции
    if f['liked'] and liked_id == f['liked'][-1] and message.text in ("❤️", "👎"):
        f['liked'] = db.patch_liked(id, f['liked'][:-1:])
        if message.text == "❤️":
            await bot.send_message(text=t.like_match(), chat_id=liked_id, reply_markup=kb.cont())
            await bot.send_photo(photo=f['photo'], chat_id=liked_id, caption=t.cap(f), reply_markup=kb.match(id))
            await bot.send_message(text=t.like_match(), chat_id=id, reply_markup=kb.match(liked_id))
    elif message.text == "❤️" and l['visible'] and not f['banned']:
        if len(l['liked']) >= liked_buffer: db.patch_visible(liked_id, False)
        if id not in l['liked']:
            l['liked'].append(id)
            if len(l['liked']) in [1, 5, 10, 15]: await bot.send_message(text=t.liked(l), chat_id=liked_id,
                                                                         reply_markup=kb.cont())
            db.patch_liked(liked_id, l['liked'])
    # вывод рандомной анкеты
    await random_form(message, state, id, f)

async def random_form(message: types.Message, state: FSMContext, id: int, f: dict):
    if f['view_count'] >= daily_views:
        await message.answer(t.enough()+"\n\n"+t.menu_main_text, reply_markup=kb.key_123())
        return await Wait.menu_answer.set()
    if f['view_count'] % 3 == 0: return await random_message(message, state, id, f)
    if not f['visible'] and len(f['liked']) < liked_buffer: db.patch_visible(id, True)
    if f['liked']:
        while f['liked'] and not db.user_exists(f['liked'][-1]): f['liked'].pop()
        db.patch_liked(id, f['liked'])
        if f['liked']:
            l = db.get_form(f['liked'][-1])
            await state.update_data(liked_id=l['id'])
            await bot.send_photo(photo=l['photo'], chat_id=id, caption=t.like_list(f)+t.cap(l), reply_markup=kb.react())
            return await Wait.form_reaction.set()
    try: r = db.get_random_user(id, f['age'], f['interest'])
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f['photo'], caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        return await Wait.my_form_answer.set()
    await state.update_data(liked_id=r['id'])
    await bot.send_photo(photo=r['photo'], caption=t.cap(r), chat_id=id, reply_markup=kb.react())
    db.patch_count(id)
    await Wait.form_reaction.set()

async def random_message(message: types.Message, state: FSMContext, id: int, f: dict):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    if f['view_count'] % 120 == 0:
        await message.answer(t.day_fact(), reply_markup=kb.cont())
        await Wait.form_reaction.set()
    elif f['view_count'] % 90 == 0:
        await message.answer(t.notice, reply_markup=kb.cont())
        await Wait.form_reaction.set()
    elif f['view_count'] % 30 == 0:
        await bot.send_photo(photo=choice(promo), caption=t.ad(), chat_id=id, reply_markup=kb.cont(), parse_mode="HTML")
        await Wait.form_reaction.set()
    return db.patch_count(id)
