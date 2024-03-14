from aiogram import types

import decor.keyboard as kb
import decor.text as t
from config import dp, bot
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.message_handler(state=Wait.admin)
async def get_ban_list(message: types.Message):
    try:
        l = await db.get_user(int(message.text))
    except (ValueError, IndexError, TypeError):
        await message.answer("Ты че мудришь, норм отвечай")
        return
    else:
        await rd.update_data(message.from_user.id, liked_id=l.id)
        await bot.send_photo(photo=l.photo, caption=t.adm_cap(l), chat_id=message.from_user.id,
                             reply_markup=kb.admin(l))
    finally:
        await rd.update_state(message.from_user.id, Wait.admin)
