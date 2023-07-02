from src.imp import *

BotDB = BotDB()


@dp.message_handler(state=Wait.admin_menu)
async def admin_menu(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "1":
        l = BotDB.get_random_claim()
        await state.update_data(liked_id=l["id"])
        await bot.send_photo(photo=l["photo"], caption=b.cap(l), chat_id=id, reply_markup=kb.ban())
        await message.answer(text=l['claims'], reply_markup=kb.match(l["id"]))
        await Wait.admin_ban_list.set()
    elif message.text == "2":
        await message.answer("Ну вводи id, прижучим", reply_markup=types.ReplyKeyboardRemove())
        await Wait.get_form_by_id.set()
    elif message.text == "3":
        await message.answer("Давай никнейм, запалим", reply_markup=types.ReplyKeyboardRemove())
        await Wait.get_form_by_username.set()
    elif message.text == "4":
        f = BotDB.get_form(id)
        await bot.send_photo(photo=f['photo'], caption=b.cap(f), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(state=Wait.admin_ban_list)
async def admin_ban_list(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text not in ("↩️", "✅", "❌", "⁉️"):
        await message.answer("Ты че мудришь, норм отвечай")
        return
    if message.text == "↩️":
        await message.answer(t.admin_menu, reply_markup=kb.key_1234())
        await Wait.admin_menu.set()
        return
    data = await state.get_data()
    liked_id = data["banned_id"]
    if message.text == "✅":
        BotDB.patch_ban(liked_id, False)
    elif message.text == "❌":
        BotDB.patch_ban(liked_id, True)
    elif message.text == "⁉️":
        await bot.send_message(text=t.warning_ban, chat_id=liked_id)
    l = BotDB.get_random_claim()
    await state.update_data(liked_id=l['id'])
    await bot.send_photo(photo=l['id'], caption=b.cap(l), chat_id=id, reply_markup=kb.ban())
    await message.answer(text=l['claims'])
    await Wait.admin_ban_list.set()


@dp.message_handler(state=Wait.get_ban_list)
async def get_ban_list(message: types.Message, state: FSMContext):
    if message.text not in ("↩️", "✅", "❌", "⁉️"):
        await message.answer("Ты че мудришь, норм отвечай")
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    if message.text == "✅":
        BotDB.patch_ban(liked_id, False)
    elif message.text == "❌":
        BotDB.patch_ban(liked_id, True)
    elif message.text == "⁉️":
        await bot.send_message(text=t.warning_ban, chat_id=liked_id)
    await message.answer(t.admin_menu, reply_markup=kb.key_1234())
    await Wait.admin_menu.set()


@dp.message_handler(state=Wait.get_form_by_id)
async def get_form_by_id(message: types.Message, state: FSMContext):
    id = message.from_user.id
    try:
        l = BotDB.get_form(int(message.text))
    except (ValueError, IndexError):
        await message.reply("Нет такого человечка")
        return
    await state.update_data(liked_id=l['id'])
    await bot.send_photo(photo=l['photo'], caption=b.cap(l)+"\n"+l['claims'], chat_id=id, reply_markup=kb.ban())
    await Wait.get_ban_list.set()


@dp.message_handler(state=Wait.get_form_by_username)
async def get_form_by_username(message: types.Message, state: FSMContext):
    id = message.from_user.id
    try:
        l = BotDB.get_form_by_username(message.text)
    except (ValueError, IndexError, TypeError):
        await message.reply("Нет такого человечка")
        return
    await state.update_data(liked_id=l['id'])
    await bot.send_photo(photo=l['photo'], caption=b.cap(l)+"\n"+l['claims'], chat_id=id, reply_markup=kb.ban())
    await Wait.get_ban_list.set()
