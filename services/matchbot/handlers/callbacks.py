import aiogram
from aiogram import types
from aiogram.utils import exceptions

import decor.keyboard as kb
import decor.text as t
from config import dp, bot
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.callback_query_handler(lambda c: c.data.startswith(('enable', 'disable')), state='*')
async def admin_callback(callback_query: types.CallbackQuery):
    action, id = callback_query.data.split(':')

    f = await db.get_user(int(id))

    f = await db.update_user(f.id, banned=False) if f.banned else await db.update_user(f.id, banned=True)

    await callback_query.message.edit_caption(caption=t.adm_cap(f, 'adm'), reply_markup=kb.admin(f))
    await bot.answer_callback_query(callback_query.id, f"User is {action}d")


@dp.callback_query_handler(lambda c: c.data.startswith('refresh'), state='*')
async def admin_refresh(callback_query: types.CallbackQuery):
    action, id = callback_query.data.split(':')

    f = await db.get_user(int(id))

    try:
        return await callback_query.message.edit_caption(caption=t.adm_cap(f, 'adm'), reply_markup=kb.admin(f))
    except aiogram.utils.exceptions.MessageNotModified:
        await bot.answer_callback_query(callback_query.id, "User is up to date!")


@dp.callback_query_handler(lambda c: c.data.startswith('warn'), state='*')
async def admin_warn(callback_query: types.CallbackQuery):
    action, id = callback_query.data.split(':')

    f = await db.get_user(int(id))

    await callback_query.message.edit_caption(caption=t.adm_cap(f, 'adm'), reply_markup=kb.admin_warn(f))


@dp.callback_query_handler(lambda c: c.data.startswith(('image', 'bio', 'back')), state='*')
async def admin_warn(callback_query: types.CallbackQuery):
    action, id = callback_query.data.split(':')

    f = await db.get_user(int(id))
    if action != 'back':
        try:
            await bot.send_message(chat_id=id, text=t.warning(action, f), reply_markup=kb.cont())
            await bot.answer_callback_query(callback_query.id, "Warned!")
            await rd.update_state(f.id, Wait.cont)
        except exceptions.BotBlocked:
            await db.update_user(f.id, visible=False)
            await bot.answer_callback_query(callback_query.id, "User left(")

    await callback_query.message.edit_caption(caption=t.adm_cap(f, 'adm'), reply_markup=kb.admin(f))
