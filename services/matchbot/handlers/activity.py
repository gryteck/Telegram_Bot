import asyncio

from aiogram import types

import utils.keyboard as kb
import utils.text as t
from config import bot
from db.redis_api import RedisDB as rd
from db.states import States


async def typing(message: types.Message):
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await asyncio.sleep(1)


async def has_private_messages(message: types.Message, id: int):
    if (await bot.get_chat(id)).has_private_forwards and (not message.from_user.username):
        await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=message.from_user.id,
                             caption=t.has_private_forwards(), reply_markup=kb.custom("Сделано!"))
        await rd.update_state(f.id, States.cont)
        return
