from aiogram import types
from aiogram.utils import exceptions

import decor.keyboard as kb
import decor.text as t
from config import dp, bot
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait
from db.models import User


@dp.callback_query_handler(lambda c: c.data.startswith(('enable:', 'disable:')), state='*')
async def admin_callback(callback_query: types.CallbackQuery):
    action, id = callback_query.data.split(':')

    f = await db.get_user(int(id))

    f = await db.update_user(f.id, banned=False) if f.banned else await db.update_user(f.id, banned=True)

    await callback_query.message.edit_caption(caption=t.adm_cap(f), reply_markup=kb.admin(f))
    await bot.answer_callback_query(callback_query.id, f"User is {action}d")


@dp.callback_query_handler(lambda c: c.data.startswith('refresh:'), state='*')
async def admin_refresh(callback_query: types.CallbackQuery):
    action, id = callback_query.data.split(':')

    f = await db.get_user(int(id))

    try:
        return await callback_query.message.edit_caption(caption=t.adm_cap(f), reply_markup=kb.admin(f))
    except Exception:
        await bot.answer_callback_query(callback_query.id, "User is up to date!")
