from aiogram import types
from aiogram.utils import exceptions

from config import bot
from db.schemas import SUser
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t


async def match_message(message: types.Message, f: SUser, l: SUser):
    # sending msg to l
    try:
        if (username := message.from_user.username) is not None:
            await bot.send_photo(photo=f.photo, chat_id=l.id, caption=t.cap(f), reply_markup=kb.match(username))
            await bot.send_message(text=t.like_match(), chat_id=l.id, reply_markup=kb.cont())
        elif not (await bot.get_chat(message.from_user.id)).has_private_forwards:
            await bot.send_photo(photo=f.photo, chat_id=l.id, caption=t.cap(f),
                                 reply_markup=kb.match(message.from_user.id))
            await bot.send_message(text=t.like_match(), chat_id=l.id, reply_markup=kb.cont())
        else:
            await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=message.from_user.id,
                                 caption=t.bad_request(), reply_markup=kb.cont())
            await rd.update_state(message.from_user.id, States.cont)
            return
    except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
        await db.update_user(l.id, visible=False)
        await message.answer('Упс, у пользователя ограничения', reply_markup=kb.cont())
        await rd.update_state(message.from_user.id, States.cont)
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
            await rd.update_state(l.id, States.cont)
            await message.answer('Упс, у пользователя ограничения', reply_markup=kb.cont())
            await rd.update_state(message.from_user.id, States.cont)
        except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
            await db.update_user(l.id, visible=False)