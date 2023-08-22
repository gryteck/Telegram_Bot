from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions

from src.config import dp, bot, supp_id, br_photo, media_groups
from src.wait import Wait

import decor.text as t
import decor.keyboard as kb

from handlers.personal.reactions import random_form

from db.schema import db

@dp.message_handler(state=Wait.my_form_answer)
async def my_form_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "1":
        await message.answer("Для начала давай выберем пол", reply_markup=kb.key_gender())
        await Wait.set_gender.set()
    elif message.text == "2":
        try:
            await message.answer(t.set_text((await state.get_data())['text']), reply_markup=kb.custom("Оставить текущее"))
        except KeyError:
            await message.answer(t.set_text())
        await Wait.change_text.set()
    elif message.text == "3":
        try:
            await bot.send_photo(photo=(await state.get_data())['photo'], chat_id=id, caption=t.current_photo)
            await message.answer(text=t.set_photo(), reply_markup=kb.custom("Оставить текущее"))
        except KeyError:
            await bot.send_message(text=t.set_photo(), chat_id=id, reply_markup=types.ReplyKeyboardRemove())
        await Wait.change_photo.set()
    elif message.text in ["4", "Продолжить"]: await random_form(message, state, id, db.get_form(id))
    else: return await message.reply(t.invalid_answer)

@dp.message_handler(state=Wait.set_gender)
async def choose_gender(message: types.Message, state: FSMContext):
    if message.text == "Продолжить":
        return await random_form(message, state, message.from_user.id, db.get_form(message.from_user.id))
    elif message.text not in ['Парень', 'Девушка']: return await message.answer(t.invalid_answer)
    await state.update_data(gender=message.text)
    await message.answer(t.set_interest(), reply_markup=kb.key_interest())
    await Wait.set_interest.set()

@dp.message_handler(state=Wait.set_interest)
async def choose_interest(message: types.Message, state: FSMContext):
    if message.text == "Продолжить":
        return await random_form(message, state, message.from_user.id, db.get_form(message.from_user.id))
    elif message.text not in ['Парни', 'Девушки']: return await message.reply(t.invalid_answer)
    await state.update_data(interest=message.text)
    data = await state.get_data()
    if data['interest'] == "Парни" and data['gender'] == "Парень": await message.reply(t.q_boys())
    elif data['interest'] == "Девушки" and data['gender'] == "Девушка": await message.reply(t.q_girls())
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    try: await message.answer(t.set_name(), reply_markup=kb.custom(data['name']))
    except KeyError: await message.answer(t.set_name(), reply_markup=types.ReplyKeyboardRemove())
    await Wait.set_name.set()

@dp.message_handler(state=Wait.set_name)
async def name(message: types.Message, state: FSMContext):
    if message.text == "Продолжить":
        return await random_form(message, state, message.from_user.id, db.get_form(message.from_user.id))
    elif len(message.text) not in range(3, 12): return await message.answer("Недопустимая длина имени")
    await state.update_data(name=message.text)
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    await message.reply(t.set_age()+f"{message.text}!")
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    data = await state.get_data()
    try: await message.answer('Сколько тебе лет?', reply_markup=kb.custom(data['age']))
    except KeyError: await message.answer('Сколько тебе лет?', reply_markup=types.ReplyKeyboardRemove())
    await Wait.set_age.set()

@dp.message_handler(state=Wait.set_age)
async def age(message: types.Message, state: FSMContext):
    if message.text == "Продолжить":
        return await random_form(message, state, message.from_user.id, db.get_form(message.from_user.id))
    try:
        if int(message.text) not in range(18, 35): return await message.reply(t.age_out_of_range)
    except(TypeError, ValueError):
        return await message.reply("Некорректный возраст")
    await state.update_data(age=message.text)
    try:
        await message.answer(t.set_text((await state.get_data())['text']), reply_markup=kb.custom("Оставить текущее"))
    except KeyError: await message.answer(t.set_text())
    await Wait.set_text.set()


@dp.message_handler(state=Wait.set_text)
async def text(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "Продолжить":
        return await random_form(message, state, id, db.get_form(id))
    elif len(str(message.text)) > 400:
        return await message.reply(t.text_out_of_range)
    elif t.text_invalid(str(message.text)):
        return await message.reply(t.text_not_meaningful)
    elif str(message.text) not in ("Оставить текущее", "Сделано!"):
        await state.update_data(text=str(message.text))
    # checking users privacy
    chat = await bot.get_chat(id)
    if (not chat.username) and chat.has_private_forwards and message.text != "Сделано!":
        return await bot.send_photo(photo=br_photo, chat_id=id, caption=t.has_private_forwards(),
                                    reply_markup=kb.custom("Сделано!"))
    # require user to send photo
    try:
        await bot.send_photo(photo=(await state.get_data())['photo'], chat_id=id, caption=t.current_photo)
        await message.answer(text=t.set_photo(), reply_markup=kb.custom("Оставить текущее"))
    except KeyError: await bot.send_message(text=t.set_photo(), chat_id=id, reply_markup=types.ReplyKeyboardRemove())
    await Wait.set_photo.set()

@dp.message_handler(state=Wait.set_photo, content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def set_photo(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.media_group_id:
        if message.media_group_id in media_groups: return
        media_groups.append(message.media_group_id)
        return await message.answer("Кидай только одну фотку)")
    elif message.content_type == 'text' and message.text != "Оставить текущее":
        return await message.answer(t.invalid_answer)
    elif message.content_type == 'photo':
        await state.update_data(username=message.from_user.username, photo=message.photo[-1].file_id)

    f = await state.get_data()
    if db.user_exists(id):
        db.patch_user(f['username'], id, f['gender'], f['interest'], f['name'], f['age'], f['photo'], f['text'])
        await bot.send_photo(photo=f['photo'], caption=f"#upd {id} \n" + t.cap(f), chat_id=supp_id)
    else:
        db.post_user(f['username'], id, f['gender'], f['interest'], f['name'], f['age'], f['photo'], f['text'])
        await bot.send_photo(photo=f['photo'], caption=f"#new {id} \n" + t.cap(f), chat_id=supp_id)
    f = db.get_form(id)
    await message.answer(t.form)
    await bot.send_photo(photo=f["photo"], caption=t.cap(f), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())
    await Wait.menu_answer.set()

@dp.message_handler(state=Wait.delete_confirm)
async def delete_confirm(message: types.Message, state: FSMContext):
    if message.text == "Продолжить":
        return await random_form(message, state, message.from_user.id, db.get_form(message.from_user.id))
    elif message.text not in ("Да", "Нет"): return await message.reply(t.invalid_answer)
    id = message.from_user.id
    if message.text == "Да":
        db.patch_visible(id, False)
        await message.answer(t.del_form, reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Нет":
        f = db.get_form(id)
        await bot.send_photo(photo=f['photo'], caption=t.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()

@dp.message_handler(state=Wait.change_photo, content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def change_photo(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.media_group_id:
        if message.media_group_id in media_groups: return
        media_groups.append(message.media_group_id)
        return await message.answer("Кидай только одну фотку)")
    elif message.content_type == 'text' and message.text != "Оставить текущее":
        return await message.answer(t.invalid_answer)
    elif message.content_type == 'photo':
        await state.update_data(username=message.from_user.username, photo=message.photo[-1].file_id)
        db.patch_photo(id, message.photo[-1].file_id)
        f = db.get_form(id)
        if not f['banned']: await bot.send_photo(photo=f['photo'], caption=f"#upd {id} \n" + t.cap(f), chat_id=supp_id)
    f = db.get_form(id)
    await message.answer(t.form)
    await bot.send_photo(photo=f["photo"], caption=t.cap(f), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())
    await Wait.menu_answer.set()

@dp.message_handler(state=Wait.change_text)
async def change_text(message: types.Message, state: FSMContext):
    id, text = message.from_user.id, str(message.text)
    if text != "Оставить текущее":
        if len(text) > 400:
            return await message.reply(t.text_out_of_range)
        elif t.text_invalid(text):
            return await message.reply(t.text_not_meaningful)
        await state.update_data(text=db.patch_text(id, text))
        f = db.get_form(id)
        if not f['banned']: await bot.send_photo(photo=f['photo'], caption=f"#upd {id}\n" + t.cap(f), chat_id=supp_id)
    f = db.get_form(id)
    await bot.send_photo(photo=f['photo'], caption=t.cap(f), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=kb.key_123())
    await Wait.menu_answer.set()
