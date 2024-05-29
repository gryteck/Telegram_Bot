import random
from aiogram import types
from aiogram.utils import exceptions
from datetime import datetime, timezone, timedelta

from config import dp, bot, settings
from handlers.activity import typing
from db.schemas import SUser
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t


async def reaction_should_be_processed(message: types.Message, f: SUser, l: SUser) -> bool:
    return message.text == "❤️" and (l.id > 999) and l.visible and not f.banned and (
            l.id not in await db.get_likes(message.from_user.id))


async def reaction_processing(message: types.Message, l: SUser):
    """Обработка реакции"""
    if message.from_user.id not in l.liked:
        if len(l.liked) >= settings.LIKED_BUFFER:
            await db.update_user(l.id, visible=False)

        l = await db.update_user(l.id, liked=await db.filter_liked(l.liked + [message.from_user.id]))
        if len(l.liked) in [1, 5, 10, 15]:
            try:
                await bot.send_message(text=t.liked(l), chat_id=l.id, reply_markup=kb.cont())
                await rd.update_state(l.id, States.cont)
                await db.create_action(message.from_user.id, l.id, 'like')
            except (exceptions.BotBlocked, exceptions.ChatNotFound, exceptions.UserDeactivated):
                await db.update_user(l.id, visible=False)
