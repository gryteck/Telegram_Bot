from src.imp import *

BotDB = BotDB()


@dp.message_handler(state=Wait.my_form_answer)
async def my_form_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "1":
        await message.answer("Для начала выберите свой пол", reply_markup=k.key_gender())
        await Wait.upd_gender.set()
    elif message.text == "2":
        await message.answer("Введите новый текст анкеты", reply_markup=k.key_empty())
        await Wait.change_text.set()
    elif message.text == "3":
        await message.answer("Отправьте новое фото", reply_markup=types.ReplyKeyboardRemove())
        await Wait.change_photo.set()
    elif message.text == "4" or message.text == "Продолжить":
        if len(BotDB.get_user_liked(id).split()) > 1:
            await message.answer(text="сперва проверь, кому понравилась твоя анкета!", reply_markup=k.cont())
            await Wait.like_list.set()
            return
        BotDB.update_date(id, daily_views)
        if BotDB.get_count(id) >= daily_views:
            await message.answer("На сегодня достаточно, приходи завтра")
            await message.answer(t.menu_main_text, reply_markup=k.key_123())
            return
        try:
            f = b.get_random_form(id)
        except ValueError:
            await message.answer(t.no_found)
            await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
            await message.answer(t.my_form_text, reply_markup=k.key_1234())
            await Wait.my_form_answer.set()
            return
        await state.update_data(liked_id=f[1])
        await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
        await Wait.form_reaction.set()
    else:
        await message.reply("Нет такого варианта ответа")
        return


@dp.message_handler(state=Wait.choosing_gender)
async def choose_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Парень", "Девушка"]:
        await message.answer("Нет такого варианта ответа")
        return
    await state.update_data(gender=message.text.lower())
    await message.answer(t.set_interest, reply_markup=k.key_interest())
    await Wait.choosing_interest.set()


@dp.message_handler(state=Wait.choosing_interest)
async def choose_interest(message: types.Message, state: FSMContext):
    if message.text == "Парни" or message.text == "Девушки":
        await state.update_data(interest=message.text.lower())
        await message.answer(t.set_name, reply_markup=types.ReplyKeyboardRemove())
        await Wait.name.set()
    else:
        await message.reply("Нет такого варианта ответа")
        return


@dp.message_handler(state=Wait.name)
async def name(message: types.Message, state: FSMContext):
    if len(message.text) > 20:
        await message.answer("Недопустимая длина имени")
        return
    await state.update_data(name=message.text)
    await message.reply(t.set_age+f"{message.text}!")
    await message.answer('Сколько тебе лет?')
    await Wait.age.set()


@dp.message_handler(state=Wait.age)
async def age(message: types.Message, state: FSMContext):
    try:
        if int(message.text) < 18 or int(message.text) > 30:
            await message.reply("Бот предназначен для пользователей от 18 до 30 лет")
            return
    except(TypeError, ValueError):
        await message.reply("Некорректный возраст")
        return
    await state.update_data(age=message.text)
    await message.answer(t.set_text, reply_markup=k.key_empty())
    await Wait.text.set()


@dp.message_handler(state=Wait.text)
async def text(message: types.Message, state: FSMContext):
    if message.text == "Оставить пустым":
        await state.update_data(text='')
    else:
        if len(message.text) > 400:
            await message.reply("Превышен лимит в 400 символов")
            return
        await state.update_data(text=message.text)
    await message.answer("Загрузите своё фото", reply_markup=types.ReplyKeyboardRemove())
    await Wait.photo.set()


@dp.message_handler(state=Wait.photo, content_types=["photo"])
async def download_photo(message: types.Message, state: FSMContext):
    id = message.from_user.id
    photo_id = message.photo[-1].file_id
    await state.update_data(liked="0", username=message.from_user.username, ph=photo_id)
    d = await state.get_data()
    print(list(d.values()))
    BotDB.add_form(d["username"], id, d["gender"], d["interest"], d["name"], d["age"], d["ph"], d["text"], d["liked"])
    await message.answer(t.form)
    await bot.send_photo(photo=b.ph(id), caption=f"#new_user {id} \n"+b.cap(id), chat_id=supp_id)
    await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()


@dp.message_handler(state=Wait.upd_gender)
async def upd_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Парень", "Девушка"]:
        await message.answer("Нет такого варианта ответа")
        return
    await state.update_data(gender=message.text.lower())
    await message.answer(t.set_interest, reply_markup=k.key_interest())
    await Wait.upd_interest.set()


@dp.message_handler(state=Wait.upd_interest)
async def upd_interest(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "Парни" or message.text == "Девушки":
        await state.update_data(interest=message.text.lower())
        await message.answer(t.set_name, reply_markup=k.custom(data["name"]))
        await Wait.upd_name.set()
    else:
        await message.reply("Нет такого варианта ответа")
        return


@dp.message_handler(state=Wait.upd_name)
async def upd_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if len(message.text) > 20:
        await message.answer("Недопустимая длина имени")
        return
    await state.update_data(name=message.text)
    await message.reply(t.set_age+f"{message.text}!")
    await message.answer('Сколько тебе лет?', reply_markup=k.custom(data["age"]))
    await Wait.upd_age.set()


@dp.message_handler(state=Wait.upd_age)
async def upd_age(message: types.Message, state: FSMContext):
    try:
        if int(message.text) < 18 or int(message.text) > 30:
            await message.reply("Бот предназначен для пользователей от 18 до 30 лет")
            return
    except(TypeError, ValueError):
        await message.reply("Некорректный возраст")
        return
    await state.update_data(age=message.text)
    await message.answer(t.set_text, reply_markup=k.custom("Оставить текущее"))
    await Wait.upd_text.set()


@dp.message_handler(state=Wait.upd_text)
async def upd_text(message: types.Message, state: FSMContext):
    if message.text != "Оставить текущее":
        if len(message.text) > 400:
            await message.reply("Превышен лимит в 400 символов")
            return
        await state.update_data(text=message.text)
    await message.answer("Загрузите своё фото", reply_markup=types.ReplyKeyboardRemove())
    await Wait.upd_photo.set()


@dp.message_handler(state=Wait.upd_photo, content_types=["photo"])
async def upd_photo(message: types.Message, state: FSMContext):
    id = message.from_user.id
    photo_id = message.photo[-1].file_id
    await state.update_data(ph=photo_id)
    d = await state.get_data()
    print(list(d.values()))
    BotDB.update_form(id, d["name"], d["gender"], d["interest"], d["age"], d["ph"], d["text"])
    await message.answer(t.form)
    await bot.send_photo(photo=b.ph(id), caption=f"#upd_user {id} \n"+b.cap(id), chat_id=supp_id)
    await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()


@dp.message_handler(state=Wait.delete_confirm)
async def delete_confirm(message: types.Message):
    if message.text not in ("Да", "Нет"):
        await message.reply("Нет такого варианта ответа")
        return
    id = message.from_user.id
    if message.text == "Да":
        BotDB.delete_form(id)
        BotDB.delete_user(id)
        await message.answer(t.del_form, reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Нет":
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()


@dp.message_handler(state=Wait.change_text)
async def change_text(message: types.Message):
    id = message.from_user.id
    if message.text == "Оставить пустым":
        BotDB.update_text(id, '')
    else:
        if len(message.text) > 400:
            await message.reply("Превышен лимит в 400 символов(")
            return
        BotDB.update_text(id, message.text)
    await bot.send_photo(photo=b.ph(id), caption=f"#upd {id}\n" + b.cap(id), chat_id=supp_id)
    await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()


@dp.message_handler(state=Wait.change_photo, content_types=["photo"])
async def change_photo(message: types.Message):
    id = message.from_user.id
    photo = message.photo[-1].file_id
    BotDB.update_photo(id, photo)
    await bot.send_photo(photo=b.ph(id), caption=f"#upd {id}\n" + b.cap(id), chat_id=supp_id)
    await message.answer(t.form)
    await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()
