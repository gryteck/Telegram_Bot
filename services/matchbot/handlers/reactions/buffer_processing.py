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

from .match_message import match_message
from .random_form import random_form


def buffer_is_not_empty(message: types.Message, f: SUser, l: SUser) -> bool:
    return l.id in f.liked and message.text in ("❤️", "👎")


async def buffer_reaction_processing(message: types.Message, f: SUser, l: SUser):
    f.liked.remove(l.id)

    f = await db.update_user(message.from_user.id, liked=f.liked)

    if message.text == "❤️":
        await db.create_action(message.from_user.id, l.id, 'match')
        await match_message(message, f, l)
        return

    await random_form(message, f)
