from src.imp import *

logging.basicConfig(level=logging.INFO, filename='main.log', filemode='a',
                    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s')
BotDB = BotDB()


@dp.message_handler(commands="info", state="*")
async def info(message: types.Message):
    await bot.send_photo(photo=open(f"photos/info.png", "rb"), chat_id=message.from_user.id,
                         caption=t.info, reply_markup=k.back())
    await message.answer("Мы в "+'<a href="https://t.me/asiaparty">телеграм</a>', parse_mode="HTML")
    await Wait.like_list.set()


@dp.message_handler(commands="admin", state="*")
async def admin(message: types.Message):
    id = message.from_user.id
    if id in admins:
        await message.answer(t.admin_menu, reply_markup=k.key_1234())
        await Wait.admin_menu.set()
    else:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="like", state="*")
async def like(message: types.Message, state: FSMContext):
    id = message.from_user.id
    while len(BotDB.get_user_liked(id).split()) != 1:
        liked_str = str(BotDB.get_user_liked(message.from_user.id))
        liked_id = liked_str.split()[-1]
        if BotDB.form_exists(liked_id): break
        BotDB.update_liked(id, b.crop_list(liked_str))
    liked_str = str(BotDB.get_user_liked(id))
    if len(BotDB.get_user_liked(id).split()) == 1:
        await message.answer(t.like_list_end)
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        liked_id = liked_str.split()[-1]
        await state.update_data(liked_id=liked_id)
        await message.answer(t.like_list, reply_markup=k.react())
        await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
        await Wait.like_list.set()


@dp.message_handler(commands="res", state="*")
async def restart(message: types.Message):
    BotDB.drop()
    BotDB.add_ban(supp_id)
    BotDB.ban_user(supp_id)
    await message.reply("Рестартнуто")


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message):
    id = message.from_user.id
    if not BotDB.user_exists(message.from_user.id):
        await message.answer(t.hello_text)
        BotDB.add_user(message.from_user.id)
    if BotDB.form_exists(message.from_user.id):
        await bot.send_photo(photo=b.ph(id), chat_id=id, caption=b.cap(id))
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await message.answer(t.set_gender, reply_markup=k.key_gender())
        await Wait.choosing_gender.set()


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
    await message.reply(t.set_age)
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
    await state.update_data(liked="0", username=message.from_user.username, count=1, ph=photo_id)
    d = await state.get_data()
    print(list(d.values()))
    BotDB.add_form(d["username"], id, d["gender"], d["interest"], d["name"], d["age"], d["ph"], d["text"], d["liked"])
    await message.answer(t.form)
    await bot.send_photo(photo=b.ph(id), caption=f"#new_user {id} \n"+b.cap(id), chat_id=supp_id)
    await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
    await message.answer(t.menu_main_text, reply_markup=k.key_123())
    await Wait.menu_answer.set()


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "1" or message.text == "Продолжить":
        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        list_of_forms = BotDB.find_forms(id, a[7], a[3])
        try:
            b.get_random_form(list_of_forms)
        except ValueError:
            await message.answer(t.no_found)
            await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
            await message.answer(t.my_form_text, reply_markup=k.key_1234())
            await Wait.my_form_answer.set()
        f = b.get_random_form(list_of_forms)
        await state.update_data(liked_id=f[1])
        await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
        await Wait.form_reaction.set()
    elif message.text == "2":
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    elif message.text == "3":
        await message.answer(t.delete_q, reply_markup=k.key_yesno())
        await Wait.delete_confirm.set()
    else:
        await message.reply("Нет такого варианта ответа")
        return


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        await message.reply("Нет такого варианта ответа")
        return
    if message.text == "Вернуться назад":
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
        return
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim.set()
        return
    id = message.from_user.id
    data = await state.get_data()
    count = data["count"]
    await state.update_data(count=count+1)
    liked_id = data["liked_id"]
    if count % 9 == 0 and message.text != "❤️":
        await message.answer(text=t.notice, reply_markup=k.cont())
        await Wait.form_reaction.set()
        return
    if message.text == "❤️" and BotDB.form_exists(liked_id) and not BotDB.user_banned(id):
        liked_str = str(BotDB.get_user_liked(liked_id))
        if str(id) not in liked_str.split():
            liked_str += (" " + str(id))
            await bot.send_message(text=t.liked, chat_id=liked_id)
        BotDB.update_liked(liked_id, liked_str)
    a = BotDB.get_form(message.from_user.id)[0]
    try:
        b.get_random_form(BotDB.find_forms(id, a[7], a[3]))
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    f = b.get_random_form(BotDB.find_forms(id, a[7], a[3]))
    await state.update_data(liked_id=f[1])
    await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
    await Wait.form_reaction.set()


@dp.message_handler(state=Wait.like_list)
async def like_list(message: types.Message, state: FSMContext):
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        await message.reply("Нет такого варианта ответа")
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    id = message.from_user.id
    if message.text in ("❤️", "👎", "🚫"): BotDB.update_liked(id, b.crop_list(BotDB.get_user_liked(id)))
    if message.text == "❤️" and BotDB.form_exists(liked_id):
        await bot.send_message(text=t.like_match, chat_id=liked_id, reply_markup=k.cont())
        await bot.send_photo(photo=b.ph(id), chat_id=liked_id, caption=b.cap(id), reply_markup=k.match(id))
        await bot.send_message(text=t.like_match, chat_id=id, reply_markup=k.match(liked_id))
        await message.answer(text="Продолжить смотреть список лайкнувших?", reply_markup=k.cont())
        await Wait.like_list.set()
    elif message.text == "Продолжить" or message.text == "👎" or not BotDB.form_exists(liked_id):
        liked_str = str(BotDB.get_user_liked(id))
        while len(BotDB.get_user_liked(id).split()) != 1 and not BotDB.form_exists(liked_str.split()[-1]):
            liked_id = BotDB.get_user_liked(id).split()[-1]
            if BotDB.form_exists(liked_id): break
            BotDB.update_liked(id, b.crop_list(BotDB.get_user_liked(id)))
        if len(BotDB.get_user_liked(id).split()) == 1:
            await message.answer(t.like_list_end)
            await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
            await message.answer(t.menu_main_text, reply_markup=k.key_123())
            await Wait.menu_answer.set()
        else:
            liked_id = liked_str.split()[-1]
            await state.update_data(liked_id=liked_id)
            await message.answer(t.like_list, reply_markup=k.react())
            await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
            await Wait.like_list.set()
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim_liked.set()
    elif message.text == "Вернуться назад":
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


@dp.message_handler(state=Wait.my_form_answer)
async def my_form_answer(message: types.Message):
    id = message.from_user.id
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
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await message.reply("Нет такого варианта ответа")
        return


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


@dp.message_handler(state=Wait.claim)
async def claim(message: types.Message, state: FSMContext):
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        await Wait.claim.set()
        return
    id = message.from_user.id
    key = message.text
    data = await state.get_data()
    banned_id = data["liked_id"]
    a = BotDB.get_form(id)[0]
    f = b.get_random_form(BotDB.find_forms(id, a[7], a[3]))
    await state.update_data(liked_id=f[1])
    if int(key) in range(1, 4):
        if not BotDB.ban_exists(banned_id):
            BotDB.add_ban(banned_id)
        if str(id) not in BotDB.get_noticed(banned_id).split():
            noticed_str = str(BotDB.get_noticed(banned_id))
            noticed_str += (" " + str(id))
            BotDB.update_noticed(banned_id, id)
            claims_str = str(BotDB.get_user_claims(banned_id))
            claims_str += (" " + key)
            BotDB.update_claims(banned_id, claims_str)
        await message.answer(t.ban_thq)
    await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
    await Wait.form_reaction.set()


@dp.message_handler(state=Wait.claim_liked)
async def claim_liked(message: types.Message, state: FSMContext):
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        await Wait.claim_liked.set()
        return
    liked_str = str(BotDB.get_user_liked(message.from_user.id))
    id = message.from_user.id
    key = message.text
    data = await state.get_data()
    banned_id = data["liked_id"]
    if int(key) in range(1, 4):
        if not BotDB.ban_exists(banned_id):
            BotDB.add_ban(banned_id)
        if str(id) not in BotDB.get_noticed(banned_id).split():
            noticed_str = str(BotDB.get_noticed(banned_id))
            noticed_str += (" " + str(id))
            BotDB.update_noticed(banned_id, id)
            claims_str = str(BotDB.get_user_claims(banned_id))
            claims_str += (" " + key)
            BotDB.update_claims(banned_id, claims_str)
        await message.answer(t.ban_thq)
    if len(liked_str.split()) > 1:
        liked_id = liked_str.split()[-1]
        await state.update_data(liked_id=liked_id)
        await message.answer(t.like_list, reply_markup=k.react())
        await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
        BotDB.update_liked(message.from_user.id, b.crop_list(liked_str))
        await Wait.like_list.set()
    else:
        await message.answer(t.like_list_end)
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(state=Wait.admin_menu)
async def admin_menu(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "1":
        f = b.get_random_form(BotDB.find_banned())
        await state.update_data(banned_id=f[1])
        await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.ban())
        await message.answer(BotDB.get_user_claims(f[1]).split(), reply_markup=k.match(f[1]))
        await Wait.admin_ban_list.set()
    elif message.text == "2":
        await message.answer("Ну вводи id, прижучим", reply_markup=types.ReplyKeyboardRemove())
        await Wait.get_form_by_id.set()
    elif message.text == "3":
        await message.answer("Давай никнейм, запалим", reply_markup=types.ReplyKeyboardRemove())
        await Wait.get_form_by_username.set()
    elif message.text == "4":
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(state=Wait.admin_ban_list)
async def admin_ban_list(message: types.Message, state: FSMContext):
    if message.text not in ("↩️", "✅", "❌", "⁉️"):
        await message.answer("Ты че мудришь, норм отвечай")
        return
    if message.text == "↩️":
        await message.answer(t.admin_menu, reply_markup=k.key_1234())
        await Wait.admin_menu.set()
        return
    id = message.from_user.id
    data = await state.get_data()
    banned_id = data["banned_id"]
    f = b.get_random_form(BotDB.find_banned())
    await state.update_data(banned_id=f[1])
    if message.text == "✅":
        BotDB.unban_user(banned_id)
    elif message.text == "❌":
        BotDB.ban_user(banned_id)
    elif message.text == "⁉️":
        await bot.send_message(text=t.warning_ban, chat_id=banned_id)
    await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.ban())
    await message.answer(BotDB.get_user_claims(f[1]).split())
    await Wait.admin_ban_list.set()


@dp.message_handler(state=Wait.get_ban_list)
async def get_ban_list(message: types.Message, state: FSMContext):
    if message.text not in ("↩️", "✅", "❌", "⁉️"):
        await message.answer("Ты че мудришь, норм отвечай")
        return
    data = await state.get_data()
    banned_id = data["banned_id"]
    if message.text == "✅":
        BotDB.unban_user(banned_id)
    elif message.text == "❌":
        BotDB.ban_user(banned_id)
    elif message.text == "⁉️":
        await bot.send_message(text=t.warning_ban, chat_id=banned_id)
    await message.answer(t.admin_menu, reply_markup=k.key_1234())
    await Wait.admin_menu.set()


@dp.message_handler(state=Wait.get_form_by_id)
async def get_form_by_id(message: types.Message, state: FSMContext):
    id = message.from_user.id
    banned_id = message.text
    try:
        BotDB.get_form(int(banned_id))[0]
    except (ValueError, IndexError):
        await message.reply("Нет такого человечка")
        return
    await state.update_data(banned_id=banned_id)
    await bot.send_photo(photo=b.ph(banned_id), caption=b.cap(banned_id), chat_id=id, reply_markup=k.ban())
    if BotDB.ban_exists(banned_id):
        await message.answer(BotDB.get_user_claims(banned_id).split())
    await Wait.get_ban_list.set()


@dp.message_handler(state=Wait.get_form_by_username)
async def get_form_by_username(message: types.Message, state: FSMContext):
    id = message.from_user.id
    try:
        banned_id = BotDB.get_username_by_id(message.text)
    except (ValueError, IndexError, TypeError):
        await message.reply("Нет такого человечка")
        return
    await state.update_data(banned_id=banned_id)
    await bot.send_photo(photo=b.ph(banned_id), caption=b.cap(banned_id), chat_id=id, reply_markup=k.ban())
    if BotDB.ban_exists(banned_id):
        await message.answer(BotDB.get_user_claims(banned_id).split())
    await Wait.get_ban_list.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
