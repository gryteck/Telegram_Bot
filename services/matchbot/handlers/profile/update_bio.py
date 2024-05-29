from aiogram import types
from config import dp, bot, settings
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t


@dp.message_handler(state=States.change_text)
async def change_text(message: types.Message):
    text = str(message.text)

    if text != "Оставить текущее":
        if len(text) > 400:
            await message.reply(t.text_out_of_range)
            return

        if t.text_invalid(text):
            await message.reply(t.text_not_meaningful)
            return

        f = await db.update_user(message.from_user.id, text=text, banned=True, visible=True)

        await rd.update_data(message.from_user.id, text=text)

        await bot.send_photo(photo=f.photo, caption=t.adm_cap(f, '#upd'), chat_id=settings.SUPPORT_ID,
                             reply_markup=kb.admin(f))

    f = await db.get_user(message.from_user.id)

    await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())

    await rd.update_state(message.from_user.id, States.menu_answer)
