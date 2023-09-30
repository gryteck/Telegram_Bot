from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions
from asyncio import sleep

import cv2
from PIL import Image
import numpy as np

from config import dp, bot
from states import Wait

import decor.text as t
import decor.keyboard as kb

from .reactions import random_form
from .activity import send_qr

from db.schema import db


@dp.message_handler(state=Wait.qrcode)
async def qr_menu(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "Продолжить":
        return await random_form(message, state, id, db.get_form(id))
    elif message.text == "Начать знакомства":
        f = await state.get_data()
        if db.user_exists(id):
            return await random_form(message, state, id, db.get_form(id))
        else:
            try:
                if f['gender']: await message.answer(t.set_interest(), reply_markup=kb.gender())
                await Wait.set_interest.set()
            except KeyError:
                await message.answer(t.set_gender, reply_markup=kb.gender())
                await Wait.set_gender.set()
    elif message.text == "Изменить данные":
        await message.answer(t.set_gender, reply_markup=kb.gender())
        await Wait.qr_gender.set()
    else: return await message.answer(t.invalid_answer, reply_markup=kb.qr_menu())


@dp.message_handler(state=Wait.qr_gender)
async def qr_gender(message: types.Message, state: FSMContext):
    if message.text not in ("Парень", "Девушка"):
        return await message.answer(t.invalid_answer)
    await state.update_data(gender=message.text)
    try:
        await message.answer(t.set_name(), reply_markup=kb.custom((await state.get_data())['name']))
    except KeyError:
        await message.answer(t.set_name(), reply_markup=types.ReplyKeyboardRemove())
    await Wait.qr_name.set()


@dp.message_handler(state=Wait.qr_name)
async def qr_name(message: types.Message, state: FSMContext):
    if len(message.text) not in range(3, 12):
        return await message.answer('Недопустимая длина имени')
    elif t.name_invalid(message.text):
        return await message.answer('Давай что-нибудь посодержательней')
    await state.update_data(name=message.text)

    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)
    await message.reply(t.reply_name(message.text))
    await bot.send_chat_action(chat_id=message.from_user.id, action='typing')
    await sleep(1)

    try:
        print((await state.get_data())['age'])
        await message.answer('Сколько тебе лет?', reply_markup=kb.custom(str((await state.get_data())['age'])))
    except (KeyError, exceptions.BadRequest):
        await message.answer('Сколько тебе лет?', reply_markup=types.ReplyKeyboardRemove())
    await Wait.qr_age.set()


@dp.message_handler(state=Wait.qr_age)
async def qr_age(message: types.Message, state: FSMContext):
    if int(message.text) < 18:
        return await message.answer("Наши мероприятия предназначены для гостей старше 18 лет")
    await state.update_data(age=int(message.text))
    id, f = message.from_user.id, await state.get_data()
    if db.qr_exists(id):
        db.patch_qr(id, f['name'], f['age'], f['gender'], message.from_user.username)
    else:
        db.post_qr(id, f['name'], f['age'], f['gender'], message.from_user.username, f['promocode'])
    await send_qr(id, f)
    await Wait.qrcode.set()

@dp.message_handler(state=Wait.qr_admin, content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def qr_admin(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    # получаем информацию об изображении
    file_info = await message.bot.get_file(photo_id)
    # скачиваем изображение
    photo = await message.bot.download_file(file_info.file_path)
    # открываем скаченное изображение
    image = Image.open(photo)
    # читаем qr код
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    id, bbox, straight_qrcode = detector.detectAndDecode(img)
    await message.delete()
    if db.qr_exists(id):
        l = db.get_qr(id)
        db.post_visit(id, l)  # добавляем гостя в историю посещений и обновляем дату последнего посещения и счетчик +1
        if db.user_exists(id):
            await message.answer_photo(photo=db.get_form(id)['photo'], caption=t.form_by_qr(l))
        else:
            await message.answer(t.form_by_qr(l))

        await bot.send_message(chat_id=id, text=t.welcome(), reply_markup=kb.rules())
    else:
        await message.answer("QR код не найден")
    await Wait.qr_admin.set()
