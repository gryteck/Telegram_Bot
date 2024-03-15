import decor.keyboard as kb
import decor.text as t
from aiogram import types, exceptions

from config import dp, bot, media_groups, settings
from db.crud import Postgre as db
from db.redis_api import RedisDB as rd
from db.states import Wait
from .reactions import random_form
from .activity import typing


@dp.message_handler(state=Wait.my_form_answer)
async def my_form_answer(message: types.Message):
    if message.text == "1":
        await message.answer("Для начала давай выберем пол", reply_markup=kb.gender())
        await rd.update_state(message.from_user.id, Wait.set_gender)
    elif message.text == "2":
        try:
            await message.answer(t.set_text((await rd.get_data(message.from_user.id)).text),
                                 reply_markup=kb.custom("Оставить текущее"))
        except (AttributeError, KeyError, exceptions.BadRequest):
            await message.answer(t.set_text(), reply_markup=types.ReplyKeyboardRemove())
        await rd.update_state(message.from_user.id, Wait.change_text)
    elif message.text == "3":
        try:
            await bot.send_photo(photo=(await rd.get_data(message.from_user.id)).photo, chat_id=message.from_user.id,
                                 caption=t.current_photo)
            await message.answer(text=t.set_photo(), reply_markup=kb.custom("Оставить текущее"))
        except (AttributeError, KeyError, exceptions.BadRequest):
            await bot.send_message(text=t.set_photo(), chat_id=message.from_user.id,
                                   reply_markup=types.ReplyKeyboardRemove())
        await rd.update_state(message.from_user.id, Wait.change_photo)
    elif message.text == "4":
        await random_form(message, await db.get_user(message.from_user.id))
    else:
        await message.reply(t.invalid_answer)


@dp.message_handler(state=Wait.set_gender)
async def choose_gender(message: types.Message):
    if message.text not in ('Парень', 'Девушка'):
        return await message.answer(t.invalid_answer)
    await rd.update_data(message.from_user.id, gender=message.text)
    await message.answer(t.set_interest(), reply_markup=kb.interest())

    await rd.update_state(message.from_user.id, Wait.set_interest)


@dp.message_handler(state=Wait.set_interest)
async def choose_interest(message: types.Message):
    if message.text not in ('Парни', 'Девушки'):
        return await message.reply(t.invalid_answer)

    await rd.update_data(message.from_user.id, interest=message.text)

    data = await rd.get_data(message.from_user.id)

    if data.interest == "Парни" and data.gender == "Парень":
        await message.reply(t.q_boys())
    elif data.interest == "Девушки" and data.gender == "Девушка":
        await message.reply(t.q_girls())

    await typing(message)

    try:
        await message.answer(t.set_name(), reply_markup=kb.custom(data.name))
    except (AttributeError, KeyError, exceptions.BadRequest):
        await message.answer(t.set_name(), reply_markup=types.ReplyKeyboardRemove())

    await rd.update_state(message.from_user.id, Wait.set_name)


@dp.message_handler(state=Wait.set_name)
async def name(message: types.Message):
    if len(message.text) not in range(3, 12):
        return await message.answer("Недопустимая длина имени")

    if t.name_invalid(message.text):
        return await message.reply("Давай что-нибудь содержательней")

    await rd.update_data(message.from_user.id, name=message.text)

    await typing(message)

    await message.reply(t.reply_name(message.text))

    await typing(message)

    data = await rd.get_data(message.from_user.id)

    try:
        await message.answer('Сколько тебе лет?', reply_markup=kb.custom(str(data.age)))
    except (AttributeError, KeyError, exceptions.BadRequest):
        await message.answer('Сколько тебе лет?', reply_markup=types.ReplyKeyboardRemove())

    await rd.update_state(message.from_user.id, Wait.set_age)


@dp.message_handler(state=Wait.set_age)
async def age(message: types.Message):
    try:
        if int(message.text) not in range(18, 35):
            return await message.reply(t.age_out_of_range)
    except(TypeError, ValueError):
        return await message.reply("Некорректный возраст")

    await rd.update_data(message.from_user.id, age=int(message.text))

    try:
        if (text := (await rd.get_data(message.from_user.id)).text) is not None:
            await message.answer(t.set_text(text), reply_markup=kb.custom("Оставить текущее"))
        else:
            await message.answer(t.set_text())
    except (AttributeError, KeyError):
        await message.answer(t.set_text())

    await rd.update_state(message.from_user.id, Wait.set_text)


@dp.message_handler(state=Wait.set_text)
async def text(message: types.Message):
    if len(str(message.text)) > 400:
        return await message.reply(t.text_out_of_range)

    if t.text_invalid(str(message.text)):
        return await message.reply(t.text_not_meaningful)

    if str(message.text) not in ("Оставить текущее", "Сделано!"):
        await rd.update_data(message.from_user.id, text=str(message.text))

    # checking users privacy
    chat = await bot.get_chat(message.from_user.id)
    if (not chat.username) and chat.has_private_forwards and message.text != "Сделано!":
        return await bot.send_photo(photo=open(f"images/br.jpg", "rb"), chat_id=message.from_user.id,
                                    caption=t.has_private_forwards(), reply_markup=kb.custom("Сделано!"))

    # require user to send photo
    try:
        await bot.send_photo(photo=(await rd.get_data(message.from_user.id)).photo, chat_id=message.from_user.id,
                             caption=t.current_photo)
    except (AttributeError, KeyError):
        await bot.send_message(text=t.set_photo(), chat_id=message.from_user.id,
                               reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(text=t.set_photo(), reply_markup=kb.custom("Оставить текущее"))
    finally:
        await rd.update_state(message.from_user.id, Wait.set_photo)


@dp.message_handler(state=Wait.set_photo, content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def set_photo(message: types.Message):
    if message.media_group_id:
        if message.media_group_id in media_groups:
            return
        media_groups.append(message.media_group_id)
        return await message.answer("Кидай только одну фотку)")
    elif message.content_type == 'text' and message.text != "Оставить текущее":
        return await message.answer(t.invalid_answer)
    elif message.content_type == 'photo':
        await rd.update_data(message.from_user.id, username=message.from_user.username, photo=message.photo[-1].file_id)

    f = await rd.get_data(message.from_user.id)

    if await db.exists_user(message.from_user.id):
        f = await db.update_user(message.from_user.id, username=message.from_user.username, gender=f.gender,
                                 interest=f.interest, name=f.name, age=f.age, photo=f.photo, text=f.text, banned=True)

        await bot.send_photo(photo=f.photo, caption=t.adm_cap(f, 'upd'), chat_id=settings.SUPPORT_ID,
                             reply_markup=kb.admin(f))
    else:
        f = await db.create_user(f.username, message.from_user.id, f.gender, f.interest, f.name, f.age, f.photo, f.text)
        await bot.send_photo(photo=f.photo, caption=t.adm_cap(f, 'new'), chat_id=settings.SUPPORT_ID,
                             reply_markup=kb.admin(f))

    await message.answer(t.form)
    await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())
    await rd.update_state(message.from_user.id, Wait.menu_answer)


@dp.message_handler(state=Wait.delete_confirm)
async def delete_confirm(message: types.Message):
    id = message.from_user.id

    if message.text == "Да":
        await db.update_user(id, visible=False)
        await message.answer(t.del_form, reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Нет":
        f = await db.get_user(id)
        await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await rd.update_state(id, Wait.my_form_answer)
    else:
        await message.reply(t.invalid_answer)


@dp.message_handler(state=Wait.change_photo, content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
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
        await db.update_user(id, photo=message.photo[-1].file_id, banned=True)

        f = await db.get_user(id)

        await bot.send_photo(photo=f.photo, caption=t.adm_cap(f, 'upd'), chat_id=settings.SUPPORT_ID,
                             reply_markup=kb.admin(f))
    elif message.text != "Оставить текущее":
        await message.answer(t.invalid_answer)
        return

    f = await db.get_user(id)

    await message.answer(t.form)
    await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())

    await rd.update_state(id, Wait.menu_answer)


@dp.message_handler(state=Wait.change_text)
async def change_text(message: types.Message):
    text = str(message.text)

    if text != "Оставить текущее":
        if len(text) > 400:
            await message.reply(t.text_out_of_range)
            return

        if t.text_invalid(text):
            await message.reply(t.text_not_meaningful)
            return

        f = await db.update_user(message.from_user.id, text=text)

        await rd.update_data(message.from_user.id, text=text)

        await bot.send_photo(photo=f.photo, caption=t.adm_cap(f, 'upd'), chat_id=settings.SUPPORT_ID,
                             reply_markup=kb.admin(f))

    f = await db.get_user(message.from_user.id)

    await bot.send_photo(photo=f.photo, caption=t.cap(f), chat_id=message.from_user.id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())

    await rd.update_state(message.from_user.id, Wait.menu_answer)
