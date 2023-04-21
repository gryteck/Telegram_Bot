from src.imp import *

logging.basicConfig(level=logging.INFO)
BotDB = BotDB('database.db')


def cap(user_id):
    a = BotDB.get_form(user_id)[0]
    return b.show_form(a[2], a[3], a[4], a[5])


def get_random_form(list_of_forms):
    form = list_of_forms[random.randint(0, len(list_of_forms) - 1)]
    a = form
    return [b.show_form(a[2], a[3], a[4], a[5]), BotDB.get_photo_id(a[1])]


@dp.message_handler(commands="res", state="*")
async def restart():
    BotDB.drop()


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message, state: FSMContext):
    global id
    id = message.from_user.id
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)
    if BotDB.form_exists(message.from_user.id):
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), chat_id=id, caption=cap(id))
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await message.answer("Давайте заполним анкету!\nДля начала выберите свой пол", reply_markup=k.key_gender())
        await Wait.choosing_gender.set()


@dp.message_handler(state=Wait.choosing_gender)
async def choose_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Парень", "Девушка"]:
        await message.answer("Выберите вариант из кнопок ниже")
        return
    await state.update_data(gender=message.text.lower())
    await message.answer("Кто вас интересует?", reply_markup=k.key_interest())
    await Wait.choosing_interest.set()


@dp.message_handler(state=Wait.choosing_interest)
async def choose_interest(message: types.Message, state: FSMContext):
    if message.text == "Парни" or message.text == "Девушки":
        await state.update_data(interest=message.text.lower())
        await message.answer("Введите своё имя", reply_markup=types.ReplyKeyboardRemove())
        await Wait.name.set()
    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.name)
async def name(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer("Слишком длинное имя")
        return
    await state.update_data(name=message.text)
    await message.answer("Сколько вам лет?")
    await Wait.age.set()


@dp.message_handler(state=Wait.age)
async def age(message: types.Message, state: FSMContext):
    try:
        if 10 > int(message.text) or int(message.text) > 100:
            await message.answer("Некорректный возраст")
            return
    except(TypeError, ValueError):
        await message.answer("Некорректный возраст")
        return
    await state.update_data(age=message.text)
    await message.answer("Напишите свой город")
    await Wait.city.set()


@dp.message_handler(state=Wait.city)
async def city(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer("Слишком длинный город")
        return
    await state.update_data(city=message.text)
    await message.answer("Введите описание анкеты (вы можете оставить его пустым)", reply_markup=k.key_empty())
    await Wait.text.set()


@dp.message_handler(state=Wait.text)
async def text(message: types.Message, state: FSMContext):
    if message.text == "Оставить пустым":
        await state.update_data(text='')
    else:
        if len(message.text) > 200:
            await message.answer("Описание может быть длиной не более 200 символов")
            return
        await state.update_data(text=message.text)
    await message.answer("Загрузите своё фото", reply_markup=types.ReplyKeyboardRemove())
    await Wait.photo.set()


@dp.message_handler(state=Wait.photo, content_types=["photo"])
async def download_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download(destination_file=f"photos/{message.from_user.id}.jpg")
    await state.update_data(liked="0", username=message.from_user.username, count=1)
    data = await state.get_data()
    d = list(data.values())
    print(d)

    BotDB.add_form(message.from_user.id, d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7])
    await message.answer("Вот ваша анкета: ")
    await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)

    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    if message.text == "1":
        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        list_of_forms = BotDB.find_forms(id, a[7], a[4], a[3])
        try:
            get_random_form(list_of_forms)
        except ValueError:
            await message.answer("Мне не удалось подобрать вам никого")
            await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
            await message.answer(t.my_form_text, reply_markup=k.key_1234())
            await Wait.my_form_answer.set()
        form = get_random_form(list_of_forms)
        await state.update_data(liked_id=form[1])
        await bot.send_photo(photo=open(f"photos/{form[1]}.jpg", "rb"), caption=form[0], chat_id=id, reply_markup=k.key_reactions())
        await Wait.form_reaction.set()
    elif message.text == "2":
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    elif message.text == "3":
        await message.answer("Вы уверены, что хотите удалить свою анкету?", reply_markup=k.key_yesno())
        await Wait.delete_confirm.set()
    elif message.text == "/like":
        await Wait.like.set()
    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    data = await state.get_data()
    list_of_forms = BotDB.find_forms(message.from_user.id, data["interest"], data["city"], data["age"])
    form = get_random_form(list_of_forms)
    count = data["count"]
    if count % 7 == 0:
        await message.answer(text="хера ты баклажан")
    await state.update_data(count=count+1)

    if message.text == "❤️":
        liked_id = data["liked_id"]
        liked_str = str(BotDB.get_user_liked(liked_id))
        if str(id) not in liked_str.split():
            liked_str += (" " + str(id))
        BotDB.update_liked(liked_id, liked_str)
        await bot.send_message(text="Вы понравились кому-то. жми /like ", chat_id=liked_id)
        await bot.send_photo(photo=open(f"photos/{form[1]}.jpg", "rb"), caption=form[0], chat_id=id)
        await Wait.form_reaction.set()
    elif message.text == "👎":
        await bot.send_photo(photo=open(f"photos/{form[1]}.jpg", "rb"), caption=form[0], chat_id=id)
        await Wait.form_reaction.set()
    elif message.text == "Вернуться назад":
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await message.answer("Выберите вариант из кнопок")
        return


@dp.message_handler(state=Wait.like)
async def like(message: types.Message, state: FSMContext):
    liked_str = str(BotDB.get_user_liked(message.from_user.id))
    if len(liked_str.split()) > 1:
        liked_id = liked_str.split()[-1]
        await state.update_data(liked_id=liked_id)
        await message.answer("Вы понравились данному пользователю:", reply_markup=k.key_reactions())
        await bot.send_photo(photo=open(f"photos/{liked_id}.jpg", "rb"), chat_id=id, caption=cap(liked_id))
        await state.update_data(liked_id=liked_id)
        BotDB.update_liked(id, b.crop_list(liked_str))
        await Wait.like_reaction.set()
    else:
        await message.answer("Вы никому не понравились:(", reply_markup=k.key_123())
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()


@dp.message_handler(state=Wait.like_reaction)
async def like_reaction(message: types.Message, state: FSMContext):
    if message.text == "❤️":
        data = await state.get_data()
        liked_id = data["liked_id"]
        await bot.send_message(text=f"Пиши - @{BotDB.get_username(liked_id)}", chat_id=id)
        await bot.send_message(text="У вас произошел мэтч!: ", chat_id=liked_id)
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), chat_id=liked_id, caption=cap(id))
        await bot.send_message(text=f"Пиши, если понравился(лась) - @{message.from_user.username}", chat_id=liked_id)
        await Wait.like.set()
    elif message.text == "":
        await Wait.like.set()


@dp.message_handler(state=Wait.delete_confirm)
async def delete_confirm(message: types.Message, state: FSMContext):
    if message.text == "Да":
        BotDB.delete_form(message.from_user.id)
        BotDB.delete_user(message.from_user.id)
        await message.answer(t.del_form, reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Нет":
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.my_form_answer)
async def my_form_answer(message: types.Message, state: FSMContext):
    if message.text == "1":
        BotDB.delete_form(message.from_user.id)
        await message.answer("Для начала выберите свой пол", reply_markup=k.key_gender())
        await Wait.choosing_gender.set()
    elif message.text == "2":
        await message.answer("Введите новый текст анкеты", reply_markup=k.key_empty())
        await Wait.change_text.set()
    elif message.text == "3":
        await message.answer("Отправьте новое фото", reply_markup=types.ReplyKeyboardRemove())
        await Wait.change_photo.set()
    elif message.text == "4":
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.change_text)
async def change_text(message: types.Message, state: FSMContext):
    if message.text == "Оставить пустым":
        BotDB.update_text(message.from_user.id, '')
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    else:
        if len(message.text) > 200:
            await message.answer("Описание должно быть длиной до 200 символов")
            return
        BotDB.update_text(message.from_user.id, message.text)
        await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(state=Wait.change_photo, content_types=["photo"])
async def change_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download(destination_file=f"photos/{message.from_user.id}.jpg")
    await message.answer("Вот ваша анкета: ")
    await bot.send_photo(photo=open(f"photos/{id}.jpg", "rb"), caption=cap(id), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
