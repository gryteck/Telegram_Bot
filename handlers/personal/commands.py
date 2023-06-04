from src.imp import *

BotDB = BotDB()


@dp.message_handler(commands="try", state="*")
async def tr(message: types.Message):
    await message.answer("Слушаю")
    await Wait.instructions.set()


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


@dp.message_handler(commands="restart", state="*")
async def restart(message: types.Message):
    if message.from_user.id not in admins:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
        return
    BotDB.drop()
    BotDB.add_ban(supp_id)
    BotDB.ban_user(supp_id)
    await message.reply("Рестартнуто")


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not BotDB.user_exists(id):
        await message.answer(t.hello_text)
        BotDB.add_user(id)
        if not BotDB.ban_exists(id): BotDB.add_ban(id)
    if BotDB.form_exists(id):
        await bot.send_photo(photo=b.ph(id), chat_id=id, caption=b.cap(id))
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await state.update_data(count=1, liked_id=id)
        await message.answer(t.set_gender, reply_markup=k.key_gender())
        await Wait.choosing_gender.set()


@dp.message_handler(commands="my_profile", state="*")
async def form_start(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not BotDB.user_exists(id):
        await message.answer(t.hello_text)
        BotDB.add_user(id)
        if not BotDB.ban_exists(id): BotDB.add_ban(id)
    if BotDB.form_exists(id):
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    else:
        await state.update_data(count=1, liked_id=id)
        await message.answer(t.set_gender, reply_markup=k.key_gender())
        await Wait.choosing_gender.set()
