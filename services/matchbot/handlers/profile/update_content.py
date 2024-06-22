from aiogram import types
from config import dp, bot, media_groups, settings
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import States
import utils.keyboard as kb
import utils.text as t


@dp.message_handler(state=States.change_photo,
                    content_types=[types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO])
async def change_photo(message: types.Message):
    id = message.from_user.id

    if message.media_group_id:
        if message.media_group_id in media_groups:
            return
        media_groups.append(message.media_group_id)
        await message.answer("Кидай только одну фотку)")
        return

    if message.content_type == 'photo':
        await rd.update_data(id, username=message.from_user.username, photo=message.photo[-1].file_id)
        await db.update_user(id, photo=message.photo[-1].file_id, banned=True, visible=True)

        f = await db.get_user(id)

        await bot.send_photo(photo=f.photo, caption=t.adm_cap(f, '#upd'), chat_id=settings.SUPPORT_ID,
                             reply_markup=kb.admin(f))
    elif message.text != "Оставить текущее":
        await message.answer(t.invalid_answer)
        return

    f = await db.get_user(id)

    await message.answer(t.form)
    await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())

    await rd.update_state(id, States.menu_answer)
