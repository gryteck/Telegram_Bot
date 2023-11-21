from aiogram import types
from aiogram.utils import exceptions

import decor.keyboard as kb
import decor.text as t
from config import dp, bot
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait


@dp.message_handler(state=Wait.admin)
async def get_ban_list(message: types.Message):
    id = message.from_user.id
    try:
        l = await db.get_user(int(message.text))
        await rd.update_data(id, liked_id=l.id)
        await bot.send_photo(photo=l.photo, caption=t.adm_cap(l), chat_id=id, reply_markup=kb.ban())
        await rd.update_state(id, Wait.admin)
    except (ValueError, IndexError, TypeError):
        if message.text not in ("↩️", "✅", "❌", "⁉️"):
            return await message.answer("Ты че мудришь, норм отвечай")
        liked_id = await rd.get_data(id).liked_id
        if message.text == "✅":
            await db.update_user(liked_id, banned=False)
        elif message.text == "❌":
            await db.update_user(liked_id, banned=True)
            await message.answer("Пользователь деактивирован")
        elif message.text == "⁉️":
            try:
                await bot.send_message(text=t.warning_ban, chat_id=liked_id)
                await message.answer("Предупрежден")
            except exceptions.BotBlocked:
                await db.update_user(liked_id, visible=False)
                await message.answer("Пользователь решил скрыться")
        await message.answer("Жду новый id")
        await rd.update_state(id, Wait.admin)
