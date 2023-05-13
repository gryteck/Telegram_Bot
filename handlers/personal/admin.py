from src.imp import *

BotDB = BotDB()


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
    id = message.from_user.id
    if message.text not in ("↩️", "✅", "❌", "⁉️"):
        await message.answer("Ты че мудришь, норм отвечай")
        return
    if message.text == "↩️":
        await message.answer(t.admin_menu, reply_markup=k.key_1234())
        await Wait.admin_menu.set()
        return
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